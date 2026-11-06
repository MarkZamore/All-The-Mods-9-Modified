import hashlib
import io
import json
import base64
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import import_upstream
import restore_modified
import verify_modified


class ModifiedCompositionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.pack, self.cache = self.root / "pack", self.root / "cache"
        (self.pack / "tools").mkdir(parents=True)
        self.base = self.jar("mods/base.jar", "base_mod")
        self.addon = self.jar("mods/addon.jar", "addon")
        config = self.pack / "config/base.toml"
        config.parent.mkdir()
        config.write_bytes(b"author=true\n")
        client = self.pack / "minecraft-1.20.1-client.jar"
        client.write_bytes(b"mojang-client-fixture")
        self.author_config = self.record(config)
        upstream = {"schemaVersion": 1, "pack": {
            "projectId": import_upstream.PROJECT_ID, "clientFileId": import_upstream.CLIENT_FILE_ID,
            "clientArchiveSha256": import_upstream.CLIENT_SHA256, "version": "1.1.1",
            "minecraftVersion": "1.20.1", "loader": {"type": "forge", "version": "47.4.0"}},
            "files": [{**self.record(self.base), "fileName": self.base.name}],
            "overrides": [self.author_config], "client": self.record(client)}
        self.write("tools/upstream-lock.json", upstream)
        self.write("tools/base-mod-ids.json", {"modIds": ["base_mod"]})
        self.write("portable-pack.json", {"schemaVersion": 1, "minecraftVersion": "1.20.1",
                   "loader": {"type": "forge", "version": "47.4.0"}, "clientJar": ""})
        ownership = self.pack / "launcher/pack-owned.txt"
        ownership.parent.mkdir()
        ownership.write_text("config/**\n", encoding="utf-8")
        self.lock = {"schemaVersion": 1,
                     "upstreamLockSha256": verify_modified.sha256(self.pack / "tools/upstream-lock.json"),
                     "baseModIdsSha256": verify_modified.sha256(self.pack / "tools/base-mod-ids.json"),
                     "files": [self.addition(self.addon)], "supportFiles": [], "baseReplacements": []}
        self.save_lock()
        self.original_base = self.base.read_bytes()
        self.original_config = config.read_bytes()

    def write(self, relative, value):
        path = self.pack / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def jar(self, relative, mod_id):
        path = self.pack / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "w") as jar:
            jar.writestr("META-INF/mods.toml", f'modLoader="javafml"\nloaderVersion="[47,)"\nlicense="MIT"\n[[mods]]\nmodId="{mod_id}"\nversion="1.0.0"\n')
        return path

    def record(self, path):
        return {"path": path.relative_to(self.pack).as_posix(), "sizeBytes": path.stat().st_size,
                "sha256": verify_modified.sha256(path)}

    def addition(self, path, file_id=1000002, mod_id="addon"):
        return {**self.record(path), "fileName": path.name, "projectId": 1000001, "fileId": file_id,
                "sourceUrl": f"https://edge.forgecdn.net/files/{file_id // 1000}/{file_id % 1000:03d}/{path.name}",
                "websiteUrl": "https://www.curseforge.com/minecraft/mc-mods/example-author-project",
                "modIds": [mod_id], "version": "1.0.0", "kind": "requested"}

    def save_lock(self):
        self.write("tools/modified-lock.json", self.lock)

    def assert_base_unchanged(self):
        self.assertEqual(self.base.read_bytes(), self.original_base)
        self.assertEqual((self.pack / "config/base.toml").read_bytes(), self.original_config)

    def test_exact_composition_passes_without_claiming_runtime(self):
        report = verify_modified.verify(self.pack)
        self.assertEqual(report["jarFiles"], 2)
        self.assertFalse(report["runtimeInventoryVerified"])
        self.assertFalse(report["runtimeAcceptanceClaimed"])

    def test_same_size_author_config_corruption_is_not_overwritten(self):
        config = self.pack / "config/base.toml"
        corruption = b"x" * len(self.original_config)
        config.write_bytes(corruption)
        with patch.object(restore_modified, "urlopen") as network:
            with self.assertRaisesRegex(ValueError, "Existing file differs"):
                restore_modified.restore(self.pack, self.cache)
        network.assert_not_called()
        self.assertEqual(config.read_bytes(), corruption)
        self.assertEqual(self.base.read_bytes(), self.original_base)

    def test_unknown_custom_jar_and_stale_script_are_rejected(self):
        for relative in ["mods/custom-helper.jar", "kubejs/server_scripts/retired.js"]:
            with self.subTest(relative=relative):
                path = self.pack / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"unknown fixture")
                with self.assertRaisesRegex(ValueError, "Unexpected/missing active content"):
                    verify_modified.verify(self.pack)
                with patch.object(restore_modified, "urlopen") as network:
                    with self.assertRaisesRegex(ValueError, "Unknown active content"):
                        restore_modified.restore(self.pack, self.cache)
                network.assert_not_called()
                self.assertEqual(path.read_bytes(), b"unknown fixture")
                path.unlink()
        self.assert_base_unchanged()

    def test_duplicate_actual_top_level_id_is_rejected(self):
        duplicate = self.jar("mods/duplicate.jar", "addon")
        self.lock["files"].append(self.addition(duplicate, file_id=1000003, mod_id="claimed_other"))
        self.save_lock()
        with self.assertRaisesRegex(ValueError, "Duplicate top-level Forge mod IDs"):
            verify_modified.verify(self.pack)

    def test_frozen_upstream_lock_change_fails_before_network(self):
        with (self.pack / "tools/upstream-lock.json").open("a", encoding="utf-8") as stream:
            stream.write("\n")
        with patch.object(restore_modified, "urlopen") as network:
            with self.assertRaisesRegex(ValueError, "Frozen baseline file differs"):
                restore_modified.restore(self.pack, self.cache)
        network.assert_not_called()
        self.assert_base_unchanged()

    def test_base_replacement_is_not_implicitly_authorized(self):
        self.lock["baseReplacements"] = [{"path": "mods/base.jar", "reason": "fixture"}]
        self.save_lock()
        with self.assertRaisesRegex(ValueError, "Base replacements are not authorized"):
            verify_modified.verify(self.pack)

    def test_path_traversal_and_wrong_cdn_file_id_are_rejected(self):
        for changes in [{"path": "mods/../outside.jar"}, {"path": "mods/NUL.jar"},
                        {"sourceUrl": "https://edge.forgecdn.net/files/1000/999/addon.jar"},
                        {"sourceUrl": "https://mirror.invalid/addon.jar"}]:
            with self.subTest(changes=changes):
                self.lock["files"][0] = {**self.addition(self.addon), **changes}
                self.save_lock()
                with patch.object(restore_modified, "urlopen") as network:
                    with self.assertRaises(ValueError):
                        restore_modified.restore(self.pack, self.cache)
                network.assert_not_called()
        self.assert_base_unchanged()

    def test_correct_existing_files_are_reused_and_second_restore_is_idempotent(self):
        with patch.object(restore_modified, "urlopen") as network:
            for _ in range(2):
                report = restore_modified.restore(self.pack, self.cache)
                self.assertEqual(report["downloadedAdditionalJars"], 0)
                self.assertEqual(report["restoredAdditionalJars"], 0)
        network.assert_not_called()
        self.assert_base_unchanged()

    def test_same_size_corrupt_addition_is_replaced_from_verified_download(self):
        expected = self.addon.read_bytes()
        self.addon.write_bytes(b"x" * len(expected))
        with patch.object(restore_modified, "urlopen", return_value=io.BytesIO(expected)) as network:
            result = restore_modified.restore(self.pack, self.cache)
        network.assert_called_once()
        self.assertEqual(result["downloadedAdditionalJars"], 1)
        self.assertEqual(self.addon.read_bytes(), expected)
        self.assert_base_unchanged()

    def test_failed_download_does_not_replace_cache_or_install_partial_batch(self):
        second = self.jar("mods/second.jar", "second")
        first_bytes, second_bytes = self.addon.read_bytes(), second.read_bytes()
        self.lock["files"].append(self.addition(second, file_id=1000003, mod_id="second"))
        self.save_lock()
        self.addon.unlink()
        second.unlink()
        with patch.object(restore_modified, "urlopen", side_effect=[io.BytesIO(first_bytes), io.BytesIO(b"bad")]):
            with self.assertRaisesRegex(ValueError, "Download size/SHA256 mismatch"):
                restore_modified.restore(self.pack, self.cache)
        self.assertFalse(self.addon.exists())
        self.assertFalse(second.exists())
        self.assertFalse(list(self.cache.rglob("*.part")))
        self.assert_base_unchanged()
        # A retry reuses the first verified cache and fetches only the missing second payload.
        with patch.object(restore_modified, "urlopen", return_value=io.BytesIO(second_bytes)) as network:
            result = restore_modified.restore(self.pack, self.cache)
        network.assert_called_once()
        self.assertEqual(result["downloadedAdditionalJars"], 1)
        self.assertEqual(result["restoredAdditionalJars"], 2)

    def test_invalid_or_interrupted_download_preserves_previous_cache(self):
        target = self.cache / "test-cache"
        target.parent.mkdir()
        target.write_bytes(b"previous verified revision")
        with patch.object(restore_modified, "urlopen", return_value=io.BytesIO(b"x" * self.lock["files"][0]["sizeBytes"])):
            with self.assertRaisesRegex(ValueError, "Download size/SHA256 mismatch"):
                restore_modified.download(self.lock["files"][0], target)
        self.assertEqual(target.read_bytes(), b"previous verified revision")
        self.assertFalse(list(self.cache.glob("*.part")))
        class Interrupted(io.BytesIO):
            def read(self, size=-1):
                raise OSError("fixture connection interrupted")
        with patch.object(restore_modified, "urlopen", return_value=Interrupted(b"partial")):
            with self.assertRaisesRegex(OSError, "interrupted"):
                restore_modified.download(self.lock["files"][0], target)
        self.assertEqual(target.read_bytes(), b"previous verified revision")
        self.assertFalse(list(self.cache.glob("*.part")))

    def test_new_rat_config_is_pinned_without_changing_author_config(self):
        rat = self.pack / "config/rats-common.toml"
        rat.write_bytes(b"fixture_ratlantis=true\n")
        self.lock["supportFiles"] = [{**self.record(rat), "kind": "configuration", "reason": "New author Rats config fixture"}]
        self.save_lock()
        self.assertEqual(verify_modified.verify(self.pack)["supportFiles"], 1)
        self.assert_base_unchanged()

    def test_final_verification_requires_real_current_source_jar_inventory(self):
        with self.assertRaisesRegex(ValueError, "Current exact-hash Forge loaded inventory"):
            verify_modified.verify(self.pack, require_loaded_inventory=True)
        self.write("library/loaded-mods.json", {"schemaVersion": 1, "minecraftVersion": "1.20.1",
            "loader": {"type": "forge", "version": "47.4.0"},
            "sourceJars": {x.relative_to(self.pack).as_posix(): verify_modified.sha256(x) for x in [self.base, self.addon]},
            "mods": [{"id": "base_mod", "name": "Base", "version": "1.0.0"},
                     {"id": "addon", "name": "Addon", "version": "1.0.0"}]})
        result = verify_modified.verify(self.pack, require_loaded_inventory=True)
        self.assertTrue(result["runtimeInventoryVerified"])
        self.assertEqual(result["actualLoadedPackModCount"], 2)

    def verity_fixture(self):
        derivative = self.jar("mods/verity-6.0.0-ru.1.jar", "verity")
        official_bytes = b"official source fixture, not a shipped JAR"
        approved = {**verify_modified.APPROVED_VERITY_SOURCE,
                    "sha256": hashlib.sha256(official_bytes).hexdigest(), "sizeBytes": len(official_bytes)}
        row = {**self.addition(derivative, file_id=approved["fileId"], mod_id="verity"),
               "sourceUrl": approved["sourceUrl"], "transformation": {
                   "kind": "russian-localization", "originalSha256": approved["sha256"],
                   "originalSizeBytes": approved["sizeBytes"], "originalSourceUrl": approved["sourceUrl"],
                   "patchTool": "tools/verity_russian.py", "reason": "Explicitly approved Verity localization test fixture"}}
        self.lock["files"] = [row]
        self.save_lock()
        self.addon.unlink()
        final_bytes = derivative.read_bytes()
        derivative.unlink()
        tool = self.pack / "tools/verity_russian.py"
        tool.write_text('import argparse,base64,pathlib\np=argparse.ArgumentParser()\np.add_argument("--input")\np.add_argument("--output")\na=p.parse_args()\npathlib.Path(a.output).write_bytes(base64.b64decode(' + repr(base64.b64encode(final_bytes).decode()) + '))\n', encoding="utf-8")
        return row, approved, official_bytes, final_bytes

    def test_only_approved_verity_transformation_is_allowed(self):
        row, approved, _, _ = self.verity_fixture()
        for changes in [{"modIds": ["another_mod"]}, {"kind": "dependency"},
                        {"transformation": {**row["transformation"], "originalSha256": "0" * 64}},
                        {"transformation": {**row["transformation"], "patchTool": "tools/arbitrary.py"}}]:
            with self.subTest(changes=changes):
                self.lock["files"] = [{**row, **changes}]
                self.save_lock()
                with patch.object(verify_modified, "APPROVED_VERITY_SOURCE", approved), \
                        patch.object(restore_modified, "urlopen") as network:
                    with self.assertRaisesRegex(ValueError, "Verity|approved"):
                        restore_modified.restore(self.pack, self.cache)
                network.assert_not_called()
        self.assert_base_unchanged()

    def test_approved_verity_derivative_is_reproduced_and_source_is_preserved(self):
        row, approved, official, final = self.verity_fixture()
        with patch.object(verify_modified, "APPROVED_VERITY_SOURCE", approved), \
                patch.object(restore_modified, "urlopen", return_value=io.BytesIO(official)) as network:
            result = restore_modified.restore(self.pack, self.cache)
        network.assert_called_once()
        self.assertEqual(result["restoredAdditionalJars"], 1)
        self.assertEqual((self.pack / row["path"]).read_bytes(), final)
        self.assertEqual((self.cache / "official" / approved["sha256"]).read_bytes(), official)
        self.assert_base_unchanged()
        with patch.object(verify_modified, "APPROVED_VERITY_SOURCE", approved), \
                patch.object(restore_modified, "urlopen") as network, \
                patch.object(restore_modified.subprocess, "run") as patcher:
            self.assertEqual(restore_modified.restore(self.pack, self.cache)["restoredAdditionalJars"], 0)
        network.assert_not_called()
        patcher.assert_not_called()

    def test_incorrect_verity_derivative_is_not_installed_or_promoted(self):
        row, approved, official, _ = self.verity_fixture()
        cached_final = self.cache / "additional" / row["sha256"]
        cached_final.parent.mkdir(parents=True)
        cached_final.write_bytes(b"previous cache bytes")
        def bad_patch(args, **kwargs):
            Path(args[args.index("--output") + 1]).write_bytes(b"bad output")
        with patch.object(verify_modified, "APPROVED_VERITY_SOURCE", approved), \
                patch.object(restore_modified, "urlopen", return_value=io.BytesIO(official)), \
                patch.object(restore_modified.subprocess, "run", side_effect=bad_patch):
            with self.assertRaisesRegex(ValueError, "does not reproduce the locked final bytes"):
                restore_modified.restore(self.pack, self.cache)
        self.assertFalse((self.pack / row["path"]).exists())
        self.assertEqual(cached_final.read_bytes(), b"previous cache bytes")
        self.assert_base_unchanged()

    def bundled_row(self):
        row = {key: value for key, value in self.addition(self.addon).items()
               if key not in {"sourceUrl", "projectId", "fileId"}}
        row.update({"sourceKind": "bundled-user-provided",
                    "officialProjectUrl": "https://author.gumroad.com/l/original-edition",
                    "websiteUrl": "https://author.gumroad.com/l/original-edition",
                    "provenance": {"suppliedBy": "user", "edition": "Gumroad original",
                                   "sourceFileName": "original-edition.jar"}})
        return row

    def test_exact_bundled_original_is_verified_and_never_downloaded(self):
        self.lock["files"] = [self.bundled_row()]
        self.save_lock()
        expected = self.addon.read_bytes()
        with patch.object(restore_modified, "urlopen") as network:
            report = restore_modified.restore(self.pack, self.cache)
        network.assert_not_called()
        self.assertEqual(report["bundledUserProvidedJars"], 1)
        self.assertEqual(report["restoredAdditionalJars"], 0)
        self.assertEqual(self.addon.read_bytes(), expected)
        self.assert_base_unchanged()

    def test_missing_or_corrupt_bundled_original_fails_before_base_or_network(self):
        original = self.addon.read_bytes()
        self.lock["files"] = [self.bundled_row()]
        self.save_lock()
        for contents in [None, b"x" * len(original)]:
            with self.subTest(missing=contents is None):
                if contents is None:
                    self.addon.unlink(missing_ok=True)
                else:
                    self.addon.write_bytes(contents)
                with patch.object(restore_modified, "urlopen") as network, \
                        patch.object(import_upstream, "restore_locked_files") as base_restore:
                    with self.assertRaisesRegex(ValueError, "exact Git-tracked original JAR.*No download URL, alternate edition"):
                        restore_modified.restore(self.pack, self.cache)
                network.assert_not_called()
                base_restore.assert_not_called()
                self.assertEqual(self.addon.read_bytes() if self.addon.exists() else None, contents)
        self.assert_base_unchanged()

    def test_bundled_provenance_rejects_signed_urls_other_edition_and_private_paths(self):
        row = self.bundled_row()
        for changes in [{"sourceUrl": "https://paid.invalid/download?token=private"},
                        {"officialProjectUrl": "https://author.gumroad.com/l/original-edition?token=private"},
                        {"projectId": 123}, {"fileId": 456},
                        {"websiteUrl": "https://www.curseforge.com/minecraft/mc-mods/different-safety-edition"},
                        {"provenance": {**row["provenance"], "sourceFileName": "C:/Personal/original.jar"}},
                        {"provenance": {**row["provenance"], "downloadUrl": "https://paid.invalid/secret"}}]:
            with self.subTest(changes=changes):
                self.lock["files"] = [{**row, **changes}]
                self.save_lock()
                with patch.object(restore_modified, "urlopen") as network:
                    with self.assertRaises(ValueError):
                        restore_modified.restore(self.pack, self.cache)
                network.assert_not_called()
        self.assert_base_unchanged()

    def quest_fixture(self):
        """107 tiny resources exercise the real reviewed reversible CLI, never author data."""
        tool = Path(os.environ.get("ATM9_QUEST_LOCALIZATION_TOOL", Path(__file__).with_name("atm9_ru_quests.py")))
        self.assertTrue(tool.is_file(), "Install the reviewed quest tool or set ATM9_QUEST_LOCALIZATION_TOOL for a candidate test")
        shutil.copyfile(tool, self.pack / verify_modified.QUEST_PATCH_TOOL)
        files, originals, localized = [], {}, {}
        for index in range(107):
            english = index == 106
            relative = "kubejs/assets/kubejs/lang/en_us.json" if english else f"config/ftbquests/quests/chapters/fixture_{index:03d}.snbt"
            before = b'{"old":"author"}\n' if english else b'{title:"Author",id:"unchanged"}\n'
            a = before.index(b'}') if english else before.index(b'"Author"')
            old = b'' if english else b'"Author"'
            new = b',"new":"fixture"' if english else b'"Localized"'
            after = before[:a] + new + before[a + len(old):]
            path = self.pack / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(before)
            files.append({"path": relative, "originalSha256": hashlib.sha256(before).hexdigest(), "originalSizeBytes": len(before),
                "localizedSha256": hashlib.sha256(after).hexdigest(), "localizedSizeBytes": len(after),
                "edits": [{"originalOffset": a, "localizedOffset": a, "originalBase64": base64.b64encode(old).decode(),
                           "localizedBase64": base64.b64encode(new).decode(), "displayPath": ["title"]}]})
            originals[relative], localized[relative] = before, after
        upstream = verify_modified.read_json(self.pack / "tools/upstream-lock.json")
        upstream["overrides"].extend({"path": row["path"], "sha256": row["originalSha256"], "sizeBytes": row["originalSizeBytes"]} for row in files)
        self.write("tools/upstream-lock.json", upstream)
        self.lock["upstreamLockSha256"] = verify_modified.sha256(self.pack / "tools/upstream-lock.json")
        self.quest_manifest = {"schemaVersion": 1, "kind": "ftbquests-russian-display-localization", "sourceVersion": "1.1.1",
            "sourceLangSha256": files[-1]["originalSha256"], "files": files}
        self.lock["questLocalization"] = {"manifestPath": verify_modified.QUEST_MANIFEST_PATH,
            "manifestSha256": "", "patchTool": verify_modified.QUEST_PATCH_TOOL,
            "patchToolSha256": verify_modified.sha256(self.pack / verify_modified.QUEST_PATCH_TOOL)}
        self.lock["baseReplacements"] = [{"path": row["path"], "originalSha256": row["originalSha256"],
            "originalSizeBytes": row["originalSizeBytes"], "sha256": row["localizedSha256"], "sizeBytes": row["localizedSizeBytes"],
            "kind": "quest-localization", "reason": "Explicit display-only localization fixture"} for row in files]
        self.save_quest_manifest()
        return originals, localized

    def save_quest_manifest(self):
        self.write(verify_modified.QUEST_MANIFEST_PATH, self.quest_manifest)
        self.lock["questLocalization"]["manifestSha256"] = verify_modified.sha256(self.pack / verify_modified.QUEST_MANIFEST_PATH)
        self.save_lock()

    def assert_resources(self, expected):
        for relative, content in expected.items():
            self.assertEqual((self.pack / relative).read_bytes(), content, relative)

    def test_reviewed_quest_profile_reports_every_replacement_and_keeps_original_base_rows(self):
        originals, localized = self.quest_fixture()
        frozen = (self.pack / "tools/upstream-lock.json").read_bytes()
        plan = verify_modified.load_plan(self.pack)
        original_rows = {row["path"]: row for row in plan["originalBaseRows"]}
        effective_rows = {row["path"]: row for row in plan["baseRows"]}
        for relative in originals:
            self.assertEqual(original_rows[relative]["sha256"], hashlib.sha256(originals[relative]).hexdigest())
            self.assertEqual(effective_rows[relative]["sha256"], hashlib.sha256(localized[relative]).hexdigest())
        self.assert_resources(originals)
        with self.assertRaisesRegex(ValueError, "Author baseline file.*mismatch"):
            verify_modified.verify(self.pack)
        restore_modified.run_quest_localization(self.pack, plan, "apply")
        report = verify_modified.verify(self.pack)
        self.assertEqual(len(report["baseReplacements"]), 107)
        self.assertEqual(report["questLocalization"], self.lock["questLocalization"])
        self.assertFalse(report["runtimeAcceptanceClaimed"])
        self.assertEqual((self.pack / "tools/upstream-lock.json").read_bytes(), frozen)
        self.assert_base_unchanged()

    def test_restore_normalizes_before_unmodified_importer_then_reapplies_idempotently(self):
        originals, localized = self.quest_fixture()
        restore_modified.run_quest_localization(self.pack, verify_modified.load_plan(self.pack), "apply")
        importer = import_upstream.restore_locked_files
        seen = []
        def check_originals(pack, cache):
            self.assert_resources(originals); self.assert_base_unchanged(); seen.append("native importer")
            return importer(pack, cache)
        frozen = (self.pack / "tools/upstream-lock.json").read_bytes()
        with patch.object(import_upstream, "restore_locked_files", side_effect=check_originals), \
                patch.object(restore_modified, "urlopen") as network, patch.object(import_upstream, "urlopen") as base_network:
            for _ in range(2):
                report = restore_modified.restore(self.pack, self.cache)
                self.assertEqual(len(report["baseReplacements"]), 107)
                self.assertEqual(report["downloadedAdditionalJars"], 0)
                self.assertEqual(report["restoredAdditionalJars"], 0)
                self.assert_resources(localized)
        self.assertEqual(len(seen), 2); network.assert_not_called(); base_network.assert_not_called()
        self.assertEqual((self.pack / "tools/upstream-lock.json").read_bytes(), frozen)
        self.assert_base_unchanged()

    def test_unknown_late_quest_hash_or_unrelated_author_change_fails_before_any_write(self):
        originals, localized = self.quest_fixture()
        restore_modified.run_quest_localization(self.pack, verify_modified.load_plan(self.pack), "apply")
        for relative in [list(localized)[-2], "config/base.toml"]:
            with self.subTest(relative=relative):
                path = self.pack / relative; previous = path.read_bytes(); path.write_bytes(b'x' * len(previous))
                snapshot = {name: (self.pack / name).read_bytes() for name in localized}
                with patch.object(restore_modified.subprocess, "run") as patcher, \
                        patch.object(import_upstream, "restore_locked_files") as importer, patch.object(restore_modified, "urlopen") as network:
                    with self.assertRaisesRegex(ValueError, "Existing file differs"):
                        restore_modified.restore(self.pack, self.cache)
                patcher.assert_not_called(); importer.assert_not_called(); network.assert_not_called()
                self.assert_resources(snapshot); path.write_bytes(previous)
        self.assert_resources(localized); self.assert_base_unchanged()

    def test_missing_tracked_quest_override_keeps_existing_importer_boundary_before_writes(self):
        _, localized = self.quest_fixture()
        restore_modified.run_quest_localization(self.pack, verify_modified.load_plan(self.pack), "apply")
        missing = list(localized)[-2]; (self.pack / missing).unlink()
        with patch.object(restore_modified.subprocess, "run") as patcher, \
                patch.object(import_upstream, "restore_locked_files") as importer, patch.object(restore_modified, "urlopen") as network:
            with self.assertRaisesRegex(ValueError, "Missing upstream override.*restore the checkout"):
                restore_modified.restore(self.pack, self.cache)
        patcher.assert_not_called(); importer.assert_not_called(); network.assert_not_called()
        self.assert_resources({key: value for key, value in localized.items() if key != missing})
        self.assertFalse((self.pack / missing).exists()); self.assert_base_unchanged()

    def test_quest_profile_cannot_authorize_jars_other_configs_or_scripts(self):
        self.quest_fixture()
        original_manifest = json.loads(json.dumps(self.quest_manifest))
        for relative in ["mods/base.jar", "config/base.toml", "kubejs/server_scripts/fix.js",
                         "config/ftbquests/quests/../../base.toml", "config/ftbquests/quests/NUL.snbt"]:
            with self.subTest(relative=relative):
                self.quest_manifest = json.loads(json.dumps(original_manifest)); self.quest_manifest["files"][0]["path"] = relative
                self.save_quest_manifest()
                with patch.object(restore_modified.subprocess, "run") as patcher, patch.object(restore_modified, "urlopen") as network:
                    with self.assertRaises(ValueError): restore_modified.restore(self.pack, self.cache)
                patcher.assert_not_called(); network.assert_not_called(); self.assert_base_unchanged()

    def test_quest_profile_requires_exact_manifest_set_original_pins_and_lock_records(self):
        originals, _ = self.quest_fixture()
        initial_manifest = json.loads(json.dumps(self.quest_manifest)); initial_lock = json.loads(json.dumps(self.lock))
        for changed in ["row-count", "duplicate", "original-sha", "original-size", "source-version", "schema-type", "kind", "language-source", "display-path", "english-overwrite", "offset", "base64"]:
            with self.subTest(changed=changed):
                self.quest_manifest = json.loads(json.dumps(initial_manifest)); self.lock = json.loads(json.dumps(initial_lock))
                row = self.quest_manifest["files"][0]
                if changed == "row-count": self.quest_manifest["files"].pop()
                elif changed == "duplicate": self.quest_manifest["files"][-2] = row
                elif changed == "original-sha": row["originalSha256"] = '0' * 64
                elif changed == "original-size": row["originalSizeBytes"] += 1
                elif changed == "source-version": self.quest_manifest["sourceVersion"] = "1.1.0"
                elif changed == "schema-type": self.quest_manifest["schemaVersion"] = True
                elif changed == "kind": self.quest_manifest["kind"] = "arbitrary-base-rewrite"
                elif changed == "language-source": self.quest_manifest["sourceLangSha256"] = '0' * 64
                elif changed == "display-path": row["edits"][0]["displayPath"] = ["reward", "count"]
                elif changed == "english-overwrite": self.quest_manifest["files"][-1]["edits"][0]["originalBase64"] = base64.b64encode(b'o').decode()
                elif changed == "offset": row["edits"][0]["localizedOffset"] += 1
                else: row["edits"][0]["originalBase64"] = "not!base64"
                self.save_quest_manifest()
                with patch.object(restore_modified.subprocess, "run") as patcher, patch.object(restore_modified, "urlopen") as network:
                    with self.assertRaises(ValueError): restore_modified.restore(self.pack, self.cache)
                patcher.assert_not_called(); network.assert_not_called(); self.assert_resources(originals)
        for changed in ["localized-sha", "original-sha", "localized-size", "extra-field", "reason", "duplicate", "missing"]:
            with self.subTest(changed=changed):
                self.quest_manifest = json.loads(json.dumps(initial_manifest)); self.lock = json.loads(json.dumps(initial_lock))
                row = self.lock["baseReplacements"][0]
                if changed == "localized-sha": row["sha256"] = '0' * 64
                elif changed == "original-sha": row["originalSha256"] = '0' * 64
                elif changed == "localized-size": row["sizeBytes"] += 1
                elif changed == "extra-field": row["allowJar"] = True
                elif changed == "reason": row["reason"] = ""
                elif changed == "duplicate": self.lock["baseReplacements"][-1] = row
                else: self.lock["baseReplacements"].pop()
                self.save_quest_manifest()
                with self.assertRaises(ValueError): verify_modified.load_plan(self.pack)
                self.assert_resources(originals)
        for changed in ["manifest-path", "tool-path", "manifest-hash", "tool-hash", "extra-profile-field", "null-profile"]:
            with self.subTest(changed=changed):
                self.lock = json.loads(json.dumps(initial_lock)); profile = self.lock["questLocalization"]
                if changed == "manifest-path": profile["manifestPath"] = "tools/unreviewed/manifest.json"
                elif changed == "tool-path": profile["patchTool"] = "tools/unreviewed.py"
                elif changed == "manifest-hash": profile["manifestSha256"] = '0' * 64
                elif changed == "tool-hash": profile["patchToolSha256"] = '0' * 64
                elif changed == "extra-profile-field": profile["allowOtherBaseReplacements"] = True
                else: self.lock["questLocalization"] = None
                self.save_lock()
                with patch.object(restore_modified.subprocess, "run") as patcher, patch.object(restore_modified, "urlopen") as network:
                    with self.assertRaises(ValueError): restore_modified.restore(self.pack, self.cache)
                patcher.assert_not_called(); network.assert_not_called(); self.assert_resources(originals)

    def test_quest_manifest_and_tool_physical_pins_are_rechecked_before_execution(self):
        originals, _ = self.quest_fixture()
        plan = verify_modified.load_plan(self.pack)
        for key in ["manifestPath", "patchTool"]:
            with self.subTest(key=key):
                path = self.pack / self.lock["questLocalization"][key]; original = path.read_bytes(); path.write_bytes(original + b'\n')
                with self.assertRaisesRegex(ValueError, "Pinned quest localization file differs"):
                    verify_modified.load_plan(self.pack)
                with patch.object(restore_modified.subprocess, "run") as patcher:
                    with self.assertRaisesRegex(ValueError, "Pinned quest localization file differs"):
                        restore_modified.run_quest_localization(self.pack, plan, "apply")
                patcher.assert_not_called(); self.assert_resources(originals); path.write_bytes(original)
        self.assert_base_unchanged()

    def test_wrong_reversible_span_is_globally_rejected_before_normalization_writes(self):
        _, localized = self.quest_fixture()
        restore_modified.run_quest_localization(self.pack, verify_modified.load_plan(self.pack), "apply")
        self.quest_manifest["files"][-2]["edits"][0]["originalBase64"] = base64.b64encode(b'"Wrong!"').decode()
        self.save_quest_manifest()
        with patch.object(import_upstream, "restore_locked_files") as importer, patch.object(restore_modified, "urlopen") as network:
            with self.assertRaises(restore_modified.subprocess.CalledProcessError): restore_modified.restore(self.pack, self.cache)
        importer.assert_not_called(); network.assert_not_called(); self.assert_resources(localized); self.assert_base_unchanged()


if __name__ == "__main__":
    unittest.main()
