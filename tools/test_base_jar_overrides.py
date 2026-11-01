"""Behavioral restore/persistence guards; no game, personal files or real network."""
from pathlib import Path
import copy, hashlib, io, json, tempfile, unittest, zipfile
from unittest.mock import patch
import atm9_base_jar_overrides as policy
import restore_modified as restore
import verify_modified as verify
import update_atm9_quests as owner
import atm9_ru_future as locale
import test_modified_tools as legacy_tests
import test_update_atm9_quests as owner_tests
from test_modified_quest_schema2 import ModifiedFixture
from test_atm9_quest_profile import js


def jar(version, mod='alltheleaks'):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as z:
        z.writestr('META-INF/mods.toml',f'modLoader="javafml"\nloaderVersion="[47,)"\nlicense="MIT"\n[[mods]]\nmodId="{mod}"\nversion="{version}"\n')
    return stream.getvalue()


class BaseOverrideTests(unittest.TestCase):
    def setUp(self):
        self.fixture=legacy_tests.ModifiedCompositionTests('test_exact_composition_passes_without_claiming_runtime')
        self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        f=self.fixture;self.pack=f.pack;self.cache=f.cache
        self.new=jar('1.1.4+1.20.1-forge')
        approved={**policy.APPROVED,'sizeBytes':len(self.new),'sha256':hashlib.sha256(self.new).hexdigest()}
        self.pin=patch.object(policy,'APPROVED',approved);self.pin.start();self.addCleanup(self.pin.stop)
        f.base.write_bytes(jar('1.0.7+1.20.1-forge'));self.old=f.base.read_bytes()
        self.upstream=verify.read_json(self.pack/'tools/upstream-lock.json')
        row={**f.record(f.base),'fileName':f.base.name,'projectId':1091339,'fileId':7065024,
             'sourceUrl':'https://edge.forgecdn.net/files/7065/024/'+f.base.name}
        self.upstream['files']=[row];f.write('tools/upstream-lock.json',self.upstream)
        f.write('tools/base-mod-ids.json',{'modIds':['alltheleaks']})
        f.lock.update(upstreamLockSha256=verify.sha256(self.pack/'tools/upstream-lock.json'),baseModIdsSha256=verify.sha256(self.pack/'tools/base-mod-ids.json'))
        self.entry={'modId':'alltheleaks','original':{**{k:row[k] for k in ['path','sha256','sizeBytes']},'version':'1.0.7+1.20.1-forge'},
                    'replacement':copy.deepcopy(approved),'reason':'Explicit compatible user pin','updatePolicy':policy.POLICY}
        f.lock['baseJarOverrides']=[self.entry];f.save_lock()
        new_cache=self.cache/'additional'/approved['sha256'];new_cache.parent.mkdir(parents=True);new_cache.write_bytes(self.new)

    def restore(self):
        with patch.object(restore,'urlopen',side_effect=AssertionError('No unpinned network expected')):
            return restore.restore(self.pack,self.cache)

    def reject_before_write(self):
        before={p.relative_to(self.pack):p.read_bytes() for p in self.pack.rglob('*') if p.is_file()}
        with patch.object(restore,'run_quest_localization') as normalize,patch.object(restore,'urlopen') as network:
            with self.assertRaises(ValueError):restore.restore(self.pack,self.cache)
        normalize.assert_not_called();network.assert_not_called()
        self.assertEqual(before,{p.relative_to(self.pack):p.read_bytes() for p in self.pack.rglob('*') if p.is_file()})

    def test_legacy_actual_author_restore_twice_keeps_pin_and_base_count(self):
        a=self.restore();b=self.restore()
        self.assertFalse(self.fixture.base.exists())
        self.assertEqual((self.pack/self.entry['replacement']['path']).read_bytes(),self.new)
        self.assertEqual(a['jarFiles'],2);self.assertEqual(b['jarFiles'],2)
        self.assertEqual(len(a['baseJarOverrides']),1)
        self.assertFalse(a['runtimeAcceptanceClaimed'])
        self.assertEqual((self.cache/'upstream/locked'/self.entry['original']['sha256']).read_bytes(),self.old)

    def test_missing_replacement_is_recovered_on_next_restore(self):
        self.restore();(self.pack/self.entry['replacement']['path']).unlink();self.restore()
        self.assertEqual((self.pack/self.entry['replacement']['path']).read_bytes(),self.new)
        self.assertFalse(self.fixture.base.exists())

    def test_identity_override_never_deletes_its_own_target(self):
        original={k:self.entry['replacement'][k] for k in ['path','sha256','sizeBytes','version']}
        self.fixture.base.unlink();path=self.pack/original['path'];path.write_bytes(self.new)
        self.upstream['files']=[{**self.entry['replacement']}]
        self.fixture.write('tools/upstream-lock.json',self.upstream)
        self.entry['original']=original;self.fixture.lock['upstreamLockSha256']=verify.sha256(self.pack/'tools/upstream-lock.json');self.fixture.save_lock()
        self.restore();self.restore();self.assertEqual(path.read_bytes(),self.new)

    def test_unknown_original_fails_before_cache_or_source_normalization(self):
        self.fixture.base.write_bytes(b'unknown author bytes');self.reject_before_write()

    def test_unknown_replacement_target_fails_before_normalization(self):
        (self.pack/self.entry['replacement']['path']).write_bytes(b'unknown replacement bytes');self.reject_before_write()

    def test_unrelated_corrupt_base_config_fails_before_normalization(self):
        (self.pack/'config/base.toml').write_bytes(b'unknown');self.reject_before_write()

    def test_missing_persistent_entry_cannot_restore_older_author_jar(self):
        del self.fixture.lock['baseJarOverrides'];self.fixture.save_lock();self.reject_before_write()

    def test_other_mod_override_and_changed_replacement_pin_refused(self):
        for field,value in [('modId','base_mod'),('updatePolicy','follow-upstream')]:
            with self.subTest(field=field):
                original=self.entry[field];self.entry[field]=value;self.fixture.save_lock();self.reject_before_write();self.entry[field]=original
        self.entry['replacement']['sha256']='0'*64;self.fixture.save_lock();self.reject_before_write()

    def test_wrong_author_project_or_original_hash_refused(self):
        self.upstream['files'][0]['projectId']=123456;self.fixture.write('tools/upstream-lock.json',self.upstream)
        self.fixture.lock['upstreamLockSha256']=verify.sha256(self.pack/'tools/upstream-lock.json');self.fixture.save_lock();self.reject_before_write()

    def test_quest_profile_cannot_authorize_base_jar_replacement(self):
        self.fixture.lock['baseReplacements']=[{'path':self.fixture.base.relative_to(self.pack).as_posix()}]
        self.fixture.save_lock();self.reject_before_write()

    def test_bad_official_replacement_download_precedes_no_source_write(self):
        (self.cache/'additional'/policy.APPROVED['sha256']).unlink()
        before=self.fixture.base.read_bytes()
        with patch.object(restore,'urlopen',return_value=io.BytesIO(b'bad')),patch.object(restore,'run_quest_localization') as normalize:
            with self.assertRaises(ValueError):restore.restore(self.pack,self.cache)
        normalize.assert_not_called();self.assertEqual(self.fixture.base.read_bytes(),before)

    def test_original_native_metadata_version_must_match_record(self):
        self.entry['original']['version']='wrong';self.fixture.save_lock()
        with patch.object(restore,'run_quest_localization') as normalize:
            with self.assertRaisesRegex(ValueError,'native mod ID/version'):restore.restore(self.pack,self.cache)
        normalize.assert_not_called();self.assertEqual(self.fixture.base.read_bytes(),self.old)


class FutureOverrideTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='atm9-base-pin-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.pack=self.root/'pack';self.pack.mkdir();self.cache=self.root/'cache'
        self.new=jar('1.1.4+1.20.1-forge')
        self.approved={**policy.APPROVED,'sha256':hashlib.sha256(self.new).hexdigest(),'sizeBytes':len(self.new)}
        patcher=patch.object(policy,'APPROVED',self.approved);patcher.start();self.addCleanup(patcher.stop)

    def fixture(self,version):
        f=ModifiedFixture(self.pack)
        relative='mods/future-author-'+version+'.jar';raw=jar(version)
        f.f.old[relative]=raw;f.f.new[relative]=raw;f.f.write(relative,raw);f.rebuild_native_rows()
        row=next(r for r in f.f.upstream['files'] if r['path']==relative);row.update(projectId=1091339,fileId=9191919,sourceUrl='https://mediafilez.forgecdn.net/files/9191/919/'+Path(relative).name)
        f.f.raw=js(f.f.upstream);f.f.write('tools/upstream-lock.json',f.f.raw);f.f.descriptor['upstreamLockSha256']=locale.sha(f.f.raw)
        f.f.write('tools/base-mod-ids.json',js({'modIds':['base_mod','alltheleaks']}))
        entry={'modId':'alltheleaks','original':{**{k:row[k] for k in ['path','sha256','sizeBytes']},'version':version},'replacement':copy.deepcopy(self.approved),'reason':'Persistent user-compatible pin','updatePolicy':policy.POLICY}
        f.lock.update(baseJarOverrides=[entry],upstreamLockSha256=locale.sha(f.f.raw),questLocalization=f.f.descriptor,baseModIdsSha256=verify.sha256(self.pack/'tools/base-mod-ids.json'));f.save_lock()
        path=self.cache/'additional'/self.approved['sha256'];path.parent.mkdir(parents=True);path.write_bytes(self.new)
        return f,entry

    def test_future_schema2_changed_author_path_hash_version_actual_restore_twice(self):
        f,entry=self.fixture('0.9.0-future-author')
        rebound=policy.rebind([entry],self.pack,f.f.upstream,locale)
        self.assertEqual(rebound[0]['replacement'],self.approved)
        self.assertEqual(rebound[0]['original']['version'],'0.9.0-future-author')
        a,b=f.run_twice(self.cache)
        self.assertEqual(a['jarFiles'],2);self.assertEqual(b['jarFiles'],2)
        self.assertFalse((self.pack/entry['original']['path']).exists())
        self.assertEqual((self.pack/entry['replacement']['path']).read_bytes(),self.new)
        self.assertEqual(a['dynamicAuthorRestore']['clientFileId'],9876543)

    def test_newer_author_version_still_retains_exact_user_pin(self):
        f,entry=self.fixture('9.9.9-future-author')
        rebound=policy.rebind([entry],self.pack,f.f.upstream,locale)
        self.assertEqual(rebound[0]['replacement'],self.approved)
        self.assertEqual(rebound[0]['original']['version'],'9.9.9-future-author')
        f.run_twice(self.cache);self.assertEqual((self.pack/entry['replacement']['path']).read_bytes(),self.new)

    def test_future_author_project_with_wrong_actual_mod_id_is_not_base_binding(self):
        f,entry=self.fixture('0.9.0-future-author');path=self.pack/entry['original']['path'];path.write_bytes(jar('0.9.0-future-author','unrelated'))
        with self.assertRaisesRegex(ValueError,'actual AllTheLeaks'):policy.rebind([entry],self.pack,f.f.upstream,locale)

    def test_explicit_offline_cache_reconstructs_exact_author_for_stage_author(self):
        f,entry=self.fixture('0.9.0-future-author');raw=(self.pack/entry['original']['path']).read_bytes();f.run_twice(self.cache)
        with self.assertRaisesRegex(ValueError,'--base-cache'):policy.author_payload(self.pack,entry['original'],None,locale)
        self.assertEqual(policy.author_payload(self.pack,entry['original'],self.cache/'upstream',locale),raw)
        (self.cache/'upstream/locked'/entry['original']['sha256']).write_bytes(b'unknown')
        with self.assertRaisesRegex(ValueError,'differs/missing'):policy.author_payload(self.pack,entry['original'],self.cache/'upstream',locale)


class OwnerPersistentPinTests(unittest.TestCase):
    def setUp(self):
        f=owner_tests.OwnerWorkflowTests('test_current_identical_payload_preserves_legacy_profile_and_support')
        f.setUp();self.addCleanup(f.tearDown);self.f=f
        self.old=jar('1.0.7+1.20.1-forge');self.new=jar('1.1.4+1.20.1-forge')
        approved={**policy.APPROVED,'sha256':locale.sha(self.new),'sizeBytes':len(self.new)}
        patcher=patch.object(policy,'APPROVED',approved);patcher.start();self.addCleanup(patcher.stop)
        # Exact managed publication: native original remains in author rows,
        # only the approved replacement is a published runtime file.
        f.author['mods/author.jar']=self.old
        current=f.lock_for('1.1.1');row=current['files'][0]
        row.update(projectId=1091339,fileId=7065024,fileName='author.jar',sourceUrl='https://edge.forgecdn.net/files/7065/024/author.jar')
        self.entry={'modId':'alltheleaks','original':{**{k:row[k] for k in ['path','sha256','sizeBytes']},'version':'1.0.7+1.20.1-forge'},'replacement':approved,'reason':'User-owned compatible BASE pin','updatePolicy':policy.POLICY}
        f.put(f.published,'tools/upstream-lock.json',locale.json_bytes(current))
        f.put(f.published,'tools/portable-profile.json',locale.json_bytes({'baseJarOverrides':[self.entry]}))
        (f.published/'mods/author.jar').unlink();f.put(f.published,approved['path'],self.new)
        f.snapshot.update(sourceKind='modified',baseJarOverrides=[self.entry],originalBaseRows=current['files']+current['overrides'])
        f.snapshot['upstreamLock']=owner.pin(f.published,'tools/upstream-lock.json')
        f.snapshot['publicationLock']=owner.pin(f.published,'tools/portable-profile.json')
        f.snapshot['content']=[owner.pin(f.published,p.relative_to(f.published).as_posix()) for p in f.published.rglob('*') if p.is_file() and p.relative_to(f.published).parts[0] in owner.CONTENT_ROOTS]
        f.snapshot['sourceControls']=[owner.pin(f.published,p['path']) for p in f.snapshot['sourceControls']]

    def test_real_owner_review_emits_retained_pin_rebound_by_actual_mod_id(self):
        f=self.f;newpath='mods/new-author-filename.jar'
        (f.fresh/'mods/author.jar').unlink();f.author.pop('mods/author.jar');f.author[newpath]=jar('9.9.9-author')
        f.update_author('2.0.0');row=f.lock['files'][0];row.update(projectId=1091339,fileId=9999999,fileName=Path(newpath).name,sourceUrl='https://edge.forgecdn.net/files/9999/999/'+Path(newpath).name)
        f.lock_path.write_bytes(locale.json_bytes(f.lock));f.review()
        result=locale.load(f.root/'review/required-lock-updates.json')
        retained=result['proposedBaseJarOverrides'][0]
        self.assertEqual(retained['replacement'],self.entry['replacement'])
        self.assertEqual(retained['original']['path'],newpath)
        self.assertEqual(retained['original']['version'],'9.9.9-author')
        self.assertEqual(result['retainAdditionalJarsOnlyAfterSeparateModCompatibilityReview'],[])
        self.assertEqual(result['proposedDynamicQuestLocalization']['schemaVersion'],2)

    def test_stage_author_requires_offline_original_before_creating_output(self):
        f=self.f;out=f.root/'staged'
        with self.assertRaisesRegex(ValueError,'--base-cache'):owner.stage_author(f.published,f.snapshot,out)
        self.assertFalse(out.exists())
        cache=f.root/'offline';path=cache/'locked'/self.entry['original']['sha256'];path.parent.mkdir(parents=True);path.write_bytes(self.old)
        report=owner.stage_author(f.published,f.snapshot,out,base_cache=cache)
        self.assertEqual(report['restoredPinnedBaseJarOriginals'],1)
        self.assertEqual((out/'mods/author.jar').read_bytes(),self.old)
        self.assertFalse((out/self.entry['replacement']['path']).exists())
        self.assertEqual((f.published/self.entry['replacement']['path']).read_bytes(),self.new)

    def test_snapshot_cannot_drop_persistent_ownership_to_relabel_pin_as_author(self):
        self.f.snapshot['baseJarOverrides']=[]
        with self.assertRaisesRegex(ValueError,'persistent BASE pin'):owner.stage_author(self.f.published,self.f.snapshot,self.f.root/'staged')
        self.assertFalse((self.f.root/'staged').exists())


if __name__=='__main__':unittest.main(verbosity=2)
