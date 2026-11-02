"""A temporary standalone diagnostic must not widen support into arbitrary executables."""
from pathlib import Path
import copy
import tempfile
import unittest

import verify_modified as verify


class RecipeDiagnosticBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.pack = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1]
        self.rows = [{**pin, 'reason': 'Temporary reviewed diagnostic fixture'} for pin in
                     [verify.APPROVED_RECIPE_OBSERVER, *verify.APPROVED_RECIPE_DIAGNOSTIC_LAUNCHERS]]
        for row in self.rows:
            target = self.pack / row['path']; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((source / row['path']).read_bytes())
        (self.pack / 'launcher/jvm-args.txt').write_text(verify.RECIPE_DIAGNOSTIC_JDWP + '\n-Dlanminecraft.diagnostics.recipeIds=true\n', encoding='utf-8')
        (self.pack / 'launcher/pack-owned.txt').write_text('config/**\nlauncher/diagnostics/**\n', encoding='utf-8')

    def snapshot(self):
        return {path.relative_to(self.pack): path.read_bytes() for path in self.pack.rglob('*') if path.is_file()}

    def test_exact_three_file_bundle_is_verified_without_source_changes(self):
        before = self.snapshot()
        for row in self.rows: verify.validate_recipe_observer(self.pack, row, self.rows)
        self.assertEqual(before, self.snapshot())

    def test_changed_path_digest_size_kind_or_extra_executable_cannot_use_exception(self):
        for field, value in [('path', 'mods/recipe-exception-observer.jar'), ('sha256', '0' * 64),
                             ('sizeBytes', 1), ('kind', 'resource')]:
            row = copy.deepcopy(self.rows[0]); row[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify.validate_recipe_observer(self.pack, row, self.rows)
        row = {**self.rows[0], 'path': 'launcher/diagnostics/unreviewed.jar'}
        with self.assertRaises(ValueError): verify.validate_recipe_observer(self.pack, row, self.rows)

    def test_missing_launcher_or_obsolete_unsupported_startup_is_rejected(self):
        with self.assertRaises(ValueError): verify.validate_recipe_observer(self.pack, self.rows[0], self.rows[:-1])
        script = self.pack / verify.RECIPE_DIAGNOSTIC_SCRIPT; script.parent.mkdir(parents=True); script.write_text('// obsolete', encoding='utf-8')
        with self.assertRaises(ValueError): verify.validate_recipe_observer(self.pack, self.rows[0], self.rows)

    def test_nonloopback_suspending_or_missing_optin_is_rejected(self):
        for flags in [verify.RECIPE_DIAGNOSTIC_JDWP.replace('127.0.0.1', '0.0.0.0'),
                      verify.RECIPE_DIAGNOSTIC_JDWP.replace('suspend=n', 'suspend=y'),
                      verify.RECIPE_DIAGNOSTIC_JDWP + '\n-Dlanminecraft.diagnostics.recipeIds=false']:
            (self.pack / 'launcher/jvm-args.txt').write_text(flags + '\n', encoding='utf-8')
            with self.subTest(flags=flags), self.assertRaises(ValueError):
                verify.validate_recipe_observer(self.pack, self.rows[0], self.rows)


if __name__ == '__main__': unittest.main()
