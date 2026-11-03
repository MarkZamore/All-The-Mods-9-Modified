"""Retired diagnostic executables cannot regain the support-resource exception."""
from pathlib import Path
import tempfile
import unittest

import verify_modified as verify


class RetiredDiagnosticProtectionTests(unittest.TestCase):
    @staticmethod
    def row(path, kind="resource"):
        return {"path": path, "sha256": "0" * 64, "sizeBytes": 0,
                "kind": kind, "reason": "Reviewed data fixture"}

    def test_former_exact_bundle_cannot_reactivate_as_temporary_kind_or_resource(self):
        # Historical pins are fixtures, never an executable allowlist.
        former = [
            ("launcher/diagnostics/recipe-exception-observer.jar", 44663,
             "71b7167dd4e9d34dfc16581e2b9eb3472c5b13f7f728980aab37332f978e71e0"),
            ("launcher/diagnostics/Start-RecipeDiagnostics.ps1", 2327,
             "081a885fc387d0f55e2ba899b2db4ee841109c53d74b28c9a0820d700afc7b44"),
            ("launcher/diagnostics/Start-RecipeDiagnostics.cmd", 174,
             "ce29b986dea9d50d2109a3a06db727b5d955a29378693f726aa4fd562ac1745a"),
        ]
        for path, size, digest in former:
            for kind in ("temporary-diagnostic-tool", "temporary-diagnostic-launcher", "resource", "configuration"):
                row = {**self.row(path, kind), "sizeBytes": size, "sha256": digest}
                with self.subTest(path=path, kind=kind), self.assertRaises(ValueError):
                    verify.validate_support_resource(row)
        # Renaming an old executable kind to look like a harmless text file
        # also does not bring its former privilege back.
        for kind in ("temporary-diagnostic-tool", "temporary-diagnostic-launcher"):
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "kind/root"):
                verify.validate_support_resource(self.row("launcher/note.txt", kind))

    def test_executables_are_rejected_in_every_support_root_and_case(self):
        for root in verify.CONTENT_ROOTS - {"mods"}:
            for extension in ("jar", "class", "java", "dll", "exe", "cmd", "bat", "ps1"):
                for suffix in (extension, extension.upper()):
                    with self.subTest(root=root, suffix=suffix), self.assertRaisesRegex(ValueError, "Executable/helper"):
                        verify.validate_support_resource(self.row(f"{root}/unreviewed.{suffix}"))
        for path in ("mods/helper.jar", "tools/helper.txt", "../launcher/helper.txt"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                verify.validate_support_resource(self.row(path))

    def test_regular_pack_configuration_and_data_remain_valid(self):
        for path, kind in (
            ("config/log4j2.xml", "configuration"),
            ("launcher/jvm-args.txt", "configuration"),
            ("kubejs/server_scripts/pack_recipe_policy.js", "resource"),
            ("resources/pack.mcmeta", "resource"),
            ("resourcepacks/localization.zip", "resource"),
            ("data/pack/recipes/carpets.json", "resource"),
        ):
            with self.subTest(path=path):
                verify.validate_support_resource(self.row(path, kind))

    def test_retired_source_contract_preserves_logging_and_content_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            pack = Path(directory)
            def write(relative, data):
                path = pack / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                return path
            def snapshot():
                return {path.relative_to(pack).as_posix(): path.read_bytes()
                        for path in pack.rglob("*") if path.is_file()}
            selector = b"-Dlog4j.configurationFile=config/log4j2.xml\n"
            ownership = b"config/**\nkubejs/**\n"
            jvm = write("launcher/jvm-args.txt", selector)
            owned = write("launcher/pack-owned.txt", ownership)
            write("config/log4j2.xml", b"Permanent bounded caught-throwable logging fixture")
            write("mods/author-content.jar", b"Author bytes that this verifier must never change")
            write("kubejs/data/alchemistry/recipes/dissolver/carpets.json", b'{"ingredient":{"tag":"minecraft:wool_carpets"}}')
            clean = snapshot()
            verify.verify_retired_diagnostics(pack)
            self.assertEqual(clean, snapshot())
            for relative in ("launcher/diagnostics/recipe-exception-observer.jar",
                             "launcher/diagnostics/Start-RecipeDiagnostics.ps1",
                             "launcher/diagnostics/Start-RecipeDiagnostics.cmd",
                             "kubejs/startup_scripts/atm9_modified_recipe_diagnostics.js"):
                path = write(relative, b"Retired executable fixture")
                before = snapshot()
                # Exercise the actual restore preflight before it can read a
                # lock or write/recover an author payload.
                with self.subTest(path=relative), self.assertRaisesRegex(ValueError, "Retired temporary diagnostic"):
                    verify.load_plan(pack)
                self.assertEqual(before, snapshot())
                path.unlink()
            for flag in ("-agentlib:jdwp=transport=dt_socket,address=127.0.0.1:0,server=y,suspend=n",
                         "-agentlib:jdwp=transport=dt_socket,address=0.0.0.0:1234,server=y,suspend=y",
                         "-Xrunjdwp:transport=dt_socket,server=y",
                         "-Dlanminecraft.diagnostics.recipeIds=true",
                         "-Dlanminecraft.diagnostics.recipeIds=false"):
                jvm.write_bytes(selector + flag.encode() + b"\n")
                before = snapshot()
                with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, "JVM flag"):
                    verify.load_plan(pack)
                self.assertEqual(before, snapshot())
            jvm.write_bytes(selector)
            for line in ("launcher/diagnostics/**", "launcher/diagnostics/Start-RecipeDiagnostics.cmd", "launcher/diagnostics/"):
                owned.write_bytes(ownership + line.encode() + b"\n")
                before = snapshot()
                with self.subTest(ownership=line), self.assertRaisesRegex(ValueError, "ownership"):
                    verify.load_plan(pack)
                self.assertEqual(before, snapshot())
            owned.write_bytes(ownership)
            verify.verify_retired_diagnostics(pack)
            self.assertEqual(clean, snapshot())


if __name__ == "__main__": unittest.main()
