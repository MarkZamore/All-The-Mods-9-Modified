"""Two exact BASE pins restore together and survive author imports without widening authority."""
import copy
import hashlib
import io
from pathlib import Path
import unittest
from unittest.mock import patch

import atm9_base_jar_overrides as policy
import atm9_ru_future as locale
import restore_modified as restore
import test_base_jar_overrides as single
import verify_modified as verify


class DualBaseOverrideTests(unittest.TestCase):
    def setUp(self):
        single.BaseOverrideTests.setUp(self)
        f = self.fixture
        self.modern_old = single.jar('5.24.4+mc1.20.1', 'modernfix')
        self.modern_new = single.jar('5.25.0+mc1.20.1', 'modernfix')
        self.modern_pin = {**policy.APPROVED_MODERNFIX, 'sizeBytes': len(self.modern_new),
                           'sha256': hashlib.sha256(self.modern_new).hexdigest()}
        self.modern_patch = patch.object(policy, 'APPROVED_MODERNFIX', self.modern_pin)
        self.modern_patch.start(); self.addCleanup(self.modern_patch.stop)
        self.modern_base = self.pack / 'mods/modernfix-author.jar'
        self.modern_base.write_bytes(self.modern_old)
        row = {**f.record(self.modern_base), 'fileName': self.modern_base.name,
               'projectId': 790626, 'fileId': 6837713,
               'sourceUrl': 'https://edge.forgecdn.net/files/6837/713/' + self.modern_base.name}
        self.upstream['files'].append(row)
        f.write('tools/upstream-lock.json', self.upstream)
        f.write('tools/base-mod-ids.json', {'modIds': ['alltheleaks', 'modernfix']})
        f.lock.update(upstreamLockSha256=verify.sha256(self.pack / 'tools/upstream-lock.json'),
                      baseModIdsSha256=verify.sha256(self.pack / 'tools/base-mod-ids.json'))
        self.modern_entry = {'modId': 'modernfix',
            'original': {**{key: row[key] for key in ('path', 'sha256', 'sizeBytes')}, 'version': '5.24.4+mc1.20.1'},
            'replacement': copy.deepcopy(self.modern_pin), 'reason': 'Explicit official ModernFix update',
            'updatePolicy': policy.POLICY}
        f.lock['baseJarOverrides'].append(self.modern_entry); f.save_lock()
        (self.cache / 'additional' / self.modern_pin['sha256']).write_bytes(self.modern_new)

    def restore(self):
        return single.BaseOverrideTests.restore(self)

    def reject_before_write(self):
        return single.BaseOverrideTests.reject_before_write(self)

    def test_two_pins_restore_twice_keep_base_count_and_metadata_identity(self):
        for report in (self.restore(), self.restore()):
            self.assertEqual(report['jarFiles'], 3)
            self.assertEqual({row['modId'] for row in report['baseJarOverrides']}, {'alltheleaks', 'modernfix'})
            self.assertFalse(report['runtimeAcceptanceClaimed'])
        self.assertFalse(self.fixture.base.exists()); self.assertFalse(self.modern_base.exists())
        self.assertEqual((self.pack / self.modern_pin['path']).read_bytes(), self.modern_new)
        self.assertEqual((self.pack / self.entry['replacement']['path']).read_bytes(), self.new)

    def test_either_or_both_required_pins_cannot_be_dropped(self):
        for entries in ([self.entry], [self.modern_entry], []):
            with self.subTest(mods=[row['modId'] for row in entries]):
                self.fixture.lock['baseJarOverrides'] = entries; self.fixture.save_lock()
                self.reject_before_write()

    def test_duplicate_third_or_cross_mod_pin_is_rejected_before_writes(self):
        cases = [[self.entry, self.entry], [self.entry, self.modern_entry, self.modern_entry],
                 [self.entry, {**self.modern_entry, 'replacement': self.entry['replacement']}]]
        for entries in cases:
            with self.subTest(entries=entries):
                self.fixture.lock['baseJarOverrides'] = entries; self.fixture.save_lock()
                self.reject_before_write()

    def test_unknown_second_source_bytes_are_not_replaced(self):
        self.modern_base.write_bytes(b'personal or corrupt bytes')
        self.reject_before_write()

    def test_second_wrong_metadata_version_fails_before_normalization(self):
        self.modern_entry['original']['version'] = 'wrong'
        self.fixture.save_lock()
        self.reject_before_write()

    def test_corrupt_second_download_does_not_normalize_first_or_second_source(self):
        (self.cache / 'additional' / self.modern_pin['sha256']).unlink()
        before = {path.relative_to(self.pack): path.read_bytes() for path in self.pack.rglob('*') if path.is_file()}
        with patch.object(restore, 'urlopen', return_value=io.BytesIO(b'bad')), patch.object(restore, 'run_quest_localization') as normalize:
            with self.assertRaises(ValueError): restore.restore(self.pack, self.cache)
        normalize.assert_not_called()
        self.assertEqual(before, {path.relative_to(self.pack): path.read_bytes() for path in self.pack.rglob('*') if path.is_file()})

    def test_two_identity_overrides_keep_their_targets(self):
        self.fixture.base.unlink(); self.modern_base.unlink()
        rows = []
        for entry, raw in ((self.entry, self.new), (self.modern_entry, self.modern_new)):
            row = copy.deepcopy(entry['replacement']); rows.append(row)
            (self.pack / row['path']).write_bytes(raw)
            entry['original'] = {key: row[key] for key in ('path', 'sha256', 'sizeBytes', 'version')}
        self.upstream['files'] = rows; self.fixture.write('tools/upstream-lock.json', self.upstream)
        self.fixture.lock['upstreamLockSha256'] = verify.sha256(self.pack / 'tools/upstream-lock.json')
        self.fixture.save_lock(); self.restore(); self.restore()
        self.assertEqual((self.pack / self.modern_pin['path']).read_bytes(), self.modern_new)
        self.assertEqual((self.pack / self.entry['replacement']['path']).read_bytes(), self.new)

    def fresh_rows(self):
        fresh = self.pack.parent / 'fresh-author'; (fresh / 'mods').mkdir(parents=True)
        rows = []
        for mod_id, filename, project, version in (
                ('alltheleaks', 'renamed-atl.jar', 1091339, '9.9.9-future'),
                ('modernfix', 'renamed-modern.jar', 790626, '99.0.0-future')):
            raw = single.jar(version, mod_id); relative = 'mods/' + filename
            (fresh / relative).write_bytes(raw)
            rows.append({'path': relative, 'fileName': filename, 'sizeBytes': len(raw),
                         'sha256': hashlib.sha256(raw).hexdigest(), 'projectId': project, 'fileId': 9999999,
                         'sourceUrl': 'https://edge.forgecdn.net/files/9999/999/' + filename})
        return fresh, {'files': rows}

    def test_two_newer_renamed_author_jars_rebind_independently_keep_both_pins(self):
        fresh, upstream = self.fresh_rows()
        result = policy.rebind([self.entry, self.modern_entry], fresh, upstream, locale)
        self.assertEqual(result[0]['replacement'], self.entry['replacement'])
        self.assertEqual(result[1]['replacement'], self.modern_entry['replacement'])
        self.assertEqual([row['original']['version'] for row in result], ['9.9.9-future', '99.0.0-future'])
        _, effective = policy.validate(fresh, result, upstream, upstream['files'], {'alltheleaks', 'modernfix'}, verify)
        self.assertEqual({row['path'] for row in effective}, {self.entry['replacement']['path'], self.modern_pin['path']})

    def test_second_future_author_project_or_actual_id_must_match(self):
        fresh, upstream = self.fresh_rows()
        upstream['files'][1]['projectId'] = 1
        with self.assertRaises(ValueError): policy.rebind([self.entry, self.modern_entry], fresh, upstream, locale)
        upstream['files'][1]['projectId'] = 790626
        (fresh / upstream['files'][1]['path']).write_bytes(single.jar('99.0.0-future', 'unrelated'))
        with self.assertRaisesRegex(ValueError, 'actual ModernFix'):
            policy.rebind([self.entry, self.modern_entry], fresh, upstream, locale)

    def test_offline_author_payload_preserves_modernfix_identity(self):
        self.restore()
        raw = policy.author_payload(self.pack, self.modern_entry['original'], self.cache / 'upstream', locale, 'modernfix')
        self.assertEqual(raw, self.modern_old)
        with self.assertRaises(ValueError):
            policy.author_payload(self.pack, self.modern_entry['original'], self.cache / 'upstream', locale, 'alltheleaks')


if __name__ == '__main__': unittest.main()
