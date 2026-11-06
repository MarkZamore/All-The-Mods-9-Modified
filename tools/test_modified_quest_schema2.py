"""Actual Modified load/restore/verify against opt-in future data fixtures."""
from pathlib import Path
import base64,copy,hashlib,io,json,os,shutil,subprocess,tempfile,unittest,zipfile
from unittest.mock import patch
import import_upstream
import verify_modified as v
import restore_modified as restore
import atm9_quest_profile as q
import atm9_ru_future as producer
from test_atm9_quest_profile import Fixture as DisplayFixture,js,pin,CHAPTER,ALIAS

HERE=Path(__file__).resolve().parent


def jar():
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as z:
        z.writestr('META-INF/mods.toml','modLoader="javafml"\nloaderVersion="[47,)"\nlicense="MIT"\n[[mods]]\nmodId="base_mod"\nversion="1.0.0"\n')
    return stream.getvalue()


class ModifiedFixture:
    def __init__(self,root,role='support',empty=False):
        self.root=root;self.f=DisplayFixture(root,role=role,empty=empty)
        native=jar();self.f.old['mods/native.jar']=native;self.f.new['mods/native.jar']=native;self.f.write('mods/native.jar',native)
        client=b'Mojang client fixture, not executed'
        self.f.old['minecraft-client.jar']=client;self.f.new['minecraft-client.jar']=client;self.f.write('minecraft-client.jar',client)
        self.f.upstream['pack'].update(minecraftVersion='1.20.1',loader={'type':'forge','version':'47.5-fixture'})
        self.rebuild_native_rows()
        self.f.write('tools/base-mod-ids.json',js({'modIds':['base_mod']}))
        self.f.write('portable-pack.json',js({'schemaVersion':1,'minecraftVersion':'1.20.1','loader':self.f.upstream['pack']['loader'],'clientJar':''}))
        self.f.write('launcher/pack-owned.txt',b'mods\nconfig\nkubejs\n')
        for name in ['import_upstream.py','verify_modified.py','restore_modified.py','pack_library.py','atm9_quest_profile.py','atm9_quest_restore.py','atm9_base_jar_overrides.py']:
            self.f.write('tools/'+name,(HERE/name).read_bytes())
        self.lock={'schemaVersion':1,'upstreamLockSha256':q.digest(self.f.raw),'baseModIdsSha256':v.sha256(root/'tools/base-mod-ids.json'),
            'baseReplacements':self.f.replacements,'questLocalization':self.f.descriptor,'files':[],
            'supportFiles':[{**r,'kind':'resource','reason':'Synthetic reviewed native Russian locale'} for r in self.f.support]}
        self.save_lock()

    def rebuild_native_rows(self):
        self.f.rows=[pin(p,raw) for p,raw in self.f.old.items()]
        files=[{**r,'fileName':r['path'].split('/')[-1],'projectId':123456,'fileId':1000001,
            'sourceUrl':'https://edge.forgecdn.net/files/1000/001/'+r['path'].split('/')[-1]} for r in self.f.rows if r['path'].startswith('mods/')]
        client=next(r for r in self.f.rows if r['path']=='minecraft-client.jar');client={**client,'sha1':hashlib.sha1(self.f.old[client['path']]).hexdigest()};client['sourceUrl']='https://piston-data.mojang.com/v1/objects/'+client['sha1']+'/client.jar'
        self.f.upstream.update(files=files,overrides=[r for r in self.f.rows if not r['path'].startswith('mods/') and r['path']!='minecraft-client.jar'],client=client)
        self.f.raw=js(self.f.upstream);self.f.write('tools/upstream-lock.json',self.f.raw);self.f.descriptor['upstreamLockSha256']=q.digest(self.f.raw)

    def save_lock(self):
        self.f.write('tools/modified-lock.json',js(self.lock))

    def run_twice(self,cache):
        with patch.object(import_upstream,'restore_locked_files',side_effect=AssertionError('Old archive identity importer must not run for schema2')),patch.object(import_upstream,'urlopen') as network:
            a=restore.restore(self.root,cache);b=restore.restore(self.root,cache)
        network.assert_not_called()
        return a,b

    def compile_locale(self,role):
        # A fresh changed author chapter and new strings are data, not a code
        # exception. Unknown inline text stays native; stale manual is omitted.
        self.f.old[q.EN]=producer.json_bytes({'manual.stale':'Changed English','community.override':'Same English','fill.manual':'Fill English'})
        self.f.old[CHAPTER]=b'{title:"Entirely changed author chapter",quests:[{id:"ABC",tasks:[{type:"item",count:37}]}]}\n'
        if role=='base':self.f.old[q.RU]=producer.json_bytes({'community.override':'Свежий перевод авторской сборки'})
        else:self.f.old.pop(q.RU,None)
        for path,raw in self.f.old.items():self.f.write(path,raw)
        self.rebuild_native_rows()
        with tempfile.TemporaryDirectory(prefix='atm9-fresh-author-') as temp:
            source=Path(temp)
            for path,raw in self.f.old.items():
                target=source/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            manual={'schemaVersion':1,'kind':producer.KIND,'entries':{
                'manual.stale':{'englishFingerprint':producer.fp('Old English'),'text':'Устаревшая ручная строка','decision':'translated'},
                'community.override':{'englishFingerprint':producer.fp('Same English'),'text':'Наш ручной запасной','decision':'translated'},
                'fill.manual':{'englishFingerprint':producer.fp('Fill English'),'text':'Проверенный запасной перевод','decision':'translated'}}}
            english=producer.load(source/q.EN);community=producer.community_capture({'community.override':'Новая внешняя строка'},{'providerId':'fixture-author'},english,provider_english=english)
            overlay,profile,ownership,report=producer.prepare(source,self.f.upstream,manual,community,{'files':[]},{},quest_snapshot=[])
        for path,raw in overlay.items():self.f.write(path,raw)
        self.f.files=profile['files'];self.f.refresh();self.f.descriptor['russianRole']=role
        self.lock.update(upstreamLockSha256=q.digest(self.f.raw),questLocalization=self.f.descriptor,baseReplacements=self.f.replacements,
            supportFiles=[] if role=='base' else [{**pin(q.RU,overlay[q.RU]),'kind':'resource','reason':'Fresh reviewed community/manual fallback'}])
        self.save_lock();return report,overlay


class ModifiedSchema2Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='atm9-modified-schema2-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.pack=self.root/'pack';self.pack.mkdir();self.cache=self.root/'cache'

    def test_new_archive_and_variable_profile_actual_restore_twice(self):
        f=ModifiedFixture(self.pack)
        self.assertNotEqual(f.f.upstream['pack']['clientFileId'],import_upstream.CLIENT_FILE_ID)
        a,b=f.run_twice(self.cache)
        self.assertEqual(a['dynamicAuthorRestore']['clientFileId'],9876543)
        self.assertEqual(a['dynamicAuthorRestore']['verifiedOriginalRows'],4)
        self.assertEqual(len(a['baseReplacements']),2);self.assertEqual(b['dynamicAuthorRestore']['restoredBinaryFiles'],[])
        self.assertEqual((self.pack/CHAPTER).read_bytes(),f.f.new[CHAPTER])
        self.assertFalse(a['runtimeAcceptanceClaimed'])

    def test_real_compiler_changed_chapter_fresh_community_wins_stale_manual_english(self):
        f=ModifiedFixture(self.pack);report,overlay=f.compile_locale('support');a,b=f.run_twice(self.cache)
        ru=json.loads((self.pack/q.RU).read_text(encoding='utf-8'))
        self.assertEqual(ru['community.override'],'Новая внешняя строка')
        self.assertNotIn('manual.stale',ru);self.assertIn('manual.stale',{r['key'] for r in report['refreshQueue']})
        self.assertEqual((self.pack/CHAPTER).read_bytes(),f.f.old[CHAPTER]);self.assertEqual(a['baseReplacements'],[])
        self.assertEqual((self.pack/q.EN).read_bytes(),f.f.old[q.EN])

    def test_real_compiler_new_native_ru_preserved_as_base_and_extended(self):
        f=ModifiedFixture(self.pack,role='base');report,overlay=f.compile_locale('base');a,b=f.run_twice(self.cache)
        ru=json.loads((self.pack/q.RU).read_text(encoding='utf-8'))
        self.assertEqual(ru['community.override'],'Свежий перевод авторской сборки')
        self.assertEqual(ru['fill.manual'],'Проверенный запасной перевод')
        self.assertNotIn('manual.stale',ru);self.assertEqual(len(a['baseReplacements']),1)
        self.assertEqual(a['baseReplacements'][0]['path'],q.RU)
        self.assertEqual(a['supportFiles'],0)

    def test_unsupported_future_locale_layout_empty_profile_keeps_native_data(self):
        f=ModifiedFixture(self.pack,role='absent',empty=True)
        raw=f.f.old.pop(q.EN);(self.pack/q.EN).unlink();path='kubejs/assets/new_native/lang/en_us.json';f.f.old[path]=raw;f.f.write(path,raw)
        f.rebuild_native_rows();f.lock.update(upstreamLockSha256=q.digest(f.f.raw),questLocalization=f.f.descriptor);f.save_lock()
        a,b=f.run_twice(self.cache);self.assertEqual(a['baseReplacements'],[])
        self.assertFalse((self.pack/q.RU).exists());self.assertEqual((self.pack/path).read_bytes(),raw)

    def test_exact_cached_missing_binary_restored_under_new_archive_identity(self):
        f=ModifiedFixture(self.pack);row=f.f.upstream['files'][0];payload=self.cache/'upstream/locked'/row['sha256'];payload.parent.mkdir(parents=True);payload.write_bytes((self.pack/row['path']).read_bytes());(self.pack/row['path']).unlink()
        a,b=f.run_twice(self.cache);self.assertEqual(a['dynamicAuthorRestore']['restoredBinaryFiles'],['mods/native.jar'])
        self.assertEqual(a['dynamicAuthorRestore']['downloadedBinaries'],0)

    def test_invalid_identity_and_url_rejected_before_normalize(self):
        f=ModifiedFixture(self.pack);f.run_twice(self.cache);before=(self.pack/CHAPTER).read_bytes()
        f.f.upstream['files'][0]['sourceUrl']='https://example.invalid/native.jar';f.f.raw=js(f.f.upstream);f.f.write('tools/upstream-lock.json',f.f.raw);f.f.descriptor['upstreamLockSha256']=q.digest(f.f.raw);f.lock.update(upstreamLockSha256=q.digest(f.f.raw),questLocalization=f.f.descriptor);f.save_lock()
        with self.assertRaisesRegex(ValueError,'exact CurseForge'):restore.restore(self.pack,self.cache)
        self.assertEqual((self.pack/CHAPTER).read_bytes(),before)

    def test_unknown_profile_or_base_bytes_refused_before_display_write(self):
        f=ModifiedFixture(self.pack);f.run_twice(self.cache);before=(self.pack/CHAPTER).read_bytes();(self.pack/'mods/native.jar').write_bytes(b'unknown author JAR')
        with self.assertRaises(ValueError):restore.restore(self.pack,self.cache)
        self.assertEqual((self.pack/CHAPTER).read_bytes(),before)

    def test_unknown_content_refused_without_discard_or_normalization(self):
        f=ModifiedFixture(self.pack);f.run_twice(self.cache);before=(self.pack/CHAPTER).read_bytes();path=self.pack/'config/personal.toml';path.parent.mkdir(exist_ok=True);path.write_bytes(b'private=true')
        with self.assertRaisesRegex(ValueError,'Unknown active content'):restore.restore(self.pack,self.cache)
        self.assertEqual(path.read_bytes(),b'private=true');self.assertEqual((self.pack/CHAPTER).read_bytes(),before)

    def test_wrong_profile_upstream_pin_fails_before_normalization(self):
        f=ModifiedFixture(self.pack);f.run_twice(self.cache);before=(self.pack/CHAPTER).read_bytes();f.lock['questLocalization']['upstreamLockSha256']='0'*64;f.save_lock()
        with self.assertRaisesRegex(ValueError,'exact upstream'):restore.restore(self.pack,self.cache)
        self.assertEqual((self.pack/CHAPTER).read_bytes(),before)

    def test_malformed_pinned_profile_rejected_before_normalization(self):
        f=ModifiedFixture(self.pack);f.run_twice(self.cache);before=(self.pack/CHAPTER).read_bytes();raw=b'{"schemaVersion":2,"files":'
        f.f.write(q.MANIFEST,raw);f.lock['questLocalization']['manifestSha256']=q.digest(raw);f.save_lock()
        with self.assertRaises(ValueError):restore.restore(self.pack,self.cache)
        self.assertEqual((self.pack/CHAPTER).read_bytes(),before)

    def test_claimed_gameplay_field_path_rejected_before_normalization(self):
        f=ModifiedFixture(self.pack);f.run_twice(self.cache);before=(self.pack/CHAPTER).read_bytes()
        f.f.files[0]['edits'][0]['displayPath']=['quests',0,'tasks',0,'item','tag','title'];f.f.refresh();f.lock.update(questLocalization=f.f.descriptor,baseReplacements=f.f.replacements);f.save_lock()
        with self.assertRaises(ValueError):restore.restore(self.pack,self.cache)
        self.assertEqual((self.pack/CHAPTER).read_bytes(),before)

    def test_real_linked_profile_refused_before_normalization(self):
        f=ModifiedFixture(self.pack);f.run_twice(self.cache);before=(self.pack/CHAPTER).read_bytes();manifest=self.pack/q.MANIFEST
        outside=self.root/'profile-outside.json';outside.write_bytes(manifest.read_bytes());manifest.unlink();junction=False
        try:
            try:os.symlink(outside,manifest)
            except OSError:
                if os.name!='nt':raise
                # Both targets are verified inside this exact owned fixture.
                folder=manifest.parent;backing=self.root/'profile-backing';self.assertTrue(folder.resolve().is_relative_to(self.root.resolve()));self.assertTrue(backing.parent.resolve()==self.root.resolve())
                folder.rename(backing);shutil.copyfile(outside,backing/manifest.name)
                pathtext=str(folder).replace("'","''");targettext=str(backing).replace("'","''")
                subprocess.run(['powershell','-NoProfile','-Command',f"New-Item -ItemType Junction -Path '{pathtext}' -Target '{targettext}' | Out-Null"],capture_output=True,check=True)
                junction=True
            with self.assertRaisesRegex(ValueError,'[Ll]ink|escap'):restore.restore(self.pack,self.cache)
            self.assertEqual((self.pack/CHAPTER).read_bytes(),before)
        finally:
            if junction:os.rmdir(manifest.parent)
            elif manifest.is_symlink():manifest.unlink()


if __name__=='__main__':unittest.main(verbosity=2)
