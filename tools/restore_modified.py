#!/usr/bin/env python3
"""Restore the locked author base, then exact pinned official additional JARs.

Run only in a checkout/staging copy with Minecraft stopped. This preparation
tool never cleans a player's installation or migrates personal data; production
launcher sync owns that operation. Unknown active files fail verification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen

import import_upstream
import verify_modified as verifier
import atm9_base_jar_overrides as base_jars

CHUNK = 1024 * 1024
USER_AGENT = "LANMinecraft-ATM9-ModifiedLockedRestore/1"


def matches(path: Path, row: dict) -> bool:
    return path.is_file() and not verifier.is_link(path) and path.stat().st_size == row["sizeBytes"] and verifier.sha256(path) == row["sha256"]


def download(row: dict, target: Path) -> bool:
    url = verifier.source_url(row)
    verifier.require(not verifier.is_link(target), "Refusing linked download target: " + str(target))
    if matches(target, row):
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".download-", suffix=".part", dir=target.parent, delete=False) as output:
            temporary = Path(output.name)
            with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=120) as response:
                # urllib follows redirects; an official host must also own the final response.
                final_url = response.geturl() if hasattr(response, "geturl") else url
                verifier.source_url(row, url=final_url)
                h, size = hashlib.sha256(), 0
                while chunk := response.read(CHUNK):
                    size += len(chunk)
                    verifier.require(size <= row["sizeBytes"], "Download exceeds pinned size: " + row["path"])
                    h.update(chunk)
                    output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        verifier.require(size == row["sizeBytes"] and h.hexdigest() == row["sha256"],
                         "Download size/SHA256 mismatch: " + row["path"])
        os.replace(temporary, target)
        return True
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def install(source: Path, pack: Path, row: dict) -> bool:
    target = verifier.target_path(pack, row["path"])
    if matches(target, row):
        return False
    verifier.require(matches(source, row), "Unverified cached addition: " + row["path"])
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".install-", suffix=".part", dir=target.parent, delete=False) as output:
            temporary = Path(output.name)
            with source.open("rb") as input_stream:
                shutil.copyfileobj(input_stream, output, CHUNK)
            output.flush()
            os.fsync(output.fileno())
        verifier.require(matches(temporary, row), "Staged addition changed: " + row["path"])
        os.replace(temporary, target)
        return True
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def prepare_payload(pack: Path, cache: Path, row: dict) -> tuple[Path, int]:
    if row.get("sourceKind") == "bundled-user-provided" and row.get("transformation"):
        transformation = verifier.validate_grotesque_quiet(pack, row)
        payload = verifier.target_path(cache, "additional/" + row["sha256"])
        if matches(payload, row):
            return payload, 0
        payload.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".grotesque-quiet-", dir=payload.parent) as folder:
            output = Path(folder) / row["fileName"]
            original = verifier.target_path(pack, transformation["originalPath"])
            tool = verifier.target_path(pack, transformation["patchTool"])
            subprocess.run([sys.executable, str(tool), "--input", str(original), "--output", str(output)], cwd=pack, check=True)
            verifier.validate_grotesque_quiet(pack, row)
            verifier.require(matches(output, row), "Grotesque quiet output does not reproduce the reviewed derivative")
            os.replace(output, payload)
        return payload, 0
    verifier.require(row.get("sourceKind") != "bundled-user-provided",
                     "Bundled user-provided original has no download source; restore its exact Git-tracked bytes")
    payload = verifier.target_path(cache, "additional/" + row["sha256"])
    if matches(payload, row):
        return payload, 0
    original = verifier.download_record(pack, row)
    if not row.get("transformation"):
        return payload, int(download(row, payload))
    original_payload = verifier.target_path(cache, "official/" + original["sha256"])
    downloaded = int(download(original, original_payload))
    payload.parent.mkdir(parents=True, exist_ok=True)
    # The author JAR remains unchanged in its own cache. A fresh temporary
    # derivative must reproduce the final locked bytes before atomic promotion.
    with tempfile.TemporaryDirectory(prefix=".verity-localize-", dir=payload.parent) as folder:
        output = Path(folder) / row["fileName"]
        patch_tool = verifier.target_path(pack, row["transformation"]["patchTool"])
        subprocess.run([sys.executable, str(patch_tool), "--input", str(original_payload),
                        "--output", str(output)], cwd=pack, check=True)
        verifier.require(matches(original_payload, original), "The Verity patcher changed its official source input")
        verifier.require(matches(output, row), "Verity localization output does not reproduce the locked final bytes")
        os.replace(output, payload)
    return payload, downloaded


def prevalidate_base_inputs(pack: Path, plan: dict):
    """Refuse every unknown BASE byte before a localization can write anything."""
    effective = {row["path"]: row for row in plan["questBaseRows"]}
    overrides = {row["original"]["path"]: row for row in plan["baseJarOverrides"]}
    committed_overrides = {row["path"] for row in plan["upstream"]["overrides"]}
    for original in plan["originalBaseRows"]:
        path = verifier.target_path(pack, original["path"])
        if not path.exists():
            verifier.require(original["path"] not in committed_overrides,
                             "Missing upstream override: " + original["path"] + "; restore the checkout or run a full import")
            continue  # The unmodified author importer restores absent originals.
        override = overrides.get(original["path"])
        if (matches(path, original) or plan["questLocalization"] and matches(path, effective[original["path"]]) or
                override and override["replacement"]["path"] == original["path"] and matches(path, override["replacement"])):
            continue
        raise ValueError("Existing file differs from frozen BASE or reviewed quest localization: " + original["path"])
    for entry in plan["baseJarOverrides"]:
        row = entry["replacement"]
        path = verifier.target_path(pack, row["path"])
        if path.exists():
            verifier.require(matches(path, row) or row["path"] == entry["original"]["path"] and matches(path, entry["original"]),
                             "Unknown existing BASE override target: " + row["path"])


def prepare_base_jar_overrides(pack: Path, cache: Path, plan: dict):
    """Verify both directions before any source normalization or installation."""
    prepared = []
    for entry in plan["baseJarOverrides"]:
        original, replacement = entry["original"], entry["replacement"]
        source = next(r for r in plan["originalBaseRows"] if r["path"] == original["path"])
        old_cache = verifier.target_path(cache, "upstream/locked/" + original["sha256"])
        current = verifier.target_path(pack, original["path"])
        if matches(current, original):
            install(current, cache, {**original, "path": "upstream/locked/" + original["sha256"]})
        else:
            download(source, old_cache)
        verifier.require(matches(old_cache, original), "Unverified original BASE override cache")
        base_jars.metadata(old_cache.read_bytes(), Path(original["path"]).name, original["version"])
        new_cache = verifier.target_path(cache, "additional/" + replacement["sha256"])
        current = verifier.target_path(pack, replacement["path"])
        if matches(current, replacement):
            install(current, cache, {**replacement, "path": "additional/" + replacement["sha256"]})
        else:
            download(replacement, new_cache)
        verifier.require(matches(new_cache, replacement), "Unverified replacement BASE override cache")
        base_jars.metadata(new_cache.read_bytes(), replacement["fileName"], replacement["version"])
        prepared.append((entry, old_cache, new_cache))
    return prepared


def normalize_base_jars(pack: Path, prepared):
    for entry, old_cache, new_cache in prepared:
        original, replacement = entry["original"], entry["replacement"]
        target = verifier.target_path(pack, replacement["path"])
        if original["path"] != replacement["path"] and target.exists():
            verifier.check_file(pack, replacement, "Known BASE replacement before normalization")
        install(old_cache, pack, original)
        if original["path"] != replacement["path"] and target.exists():
            verifier.check_file(pack, replacement, "Known BASE replacement before removal")
            target.unlink()


def apply_base_jars(pack: Path, prepared):
    for entry, old_cache, new_cache in prepared:
        original, replacement = entry["original"], entry["replacement"]
        verifier.check_file(pack, original, "Exact original BASE JAR before replacement")
        install(new_cache, pack, replacement)
        if original["path"] != replacement["path"]:
            verifier.check_file(pack, original, "Exact retired BASE JAR before removal")
            verifier.target_path(pack, original["path"]).unlink()


def run_quest_localization(pack: Path, plan: dict, mode: str):
    profile = plan["questLocalization"]
    if profile is None:
        return
    verifier.require(mode in {"normalize", "apply"}, "Unsupported quest localization staging operation")
    # Recheck both physical pins immediately before each execution; a prior
    # successful load_plan must not authorize a replaced tool or manifest.
    for path_key, hash_key in [("manifestPath", "manifestSha256"), ("patchTool", "patchToolSha256")]:
        path = verifier.target_path(pack, profile[path_key])
        verifier.require(path.is_file() and verifier.sha256(path) == profile[hash_key],
                         "Pinned quest localization file differs before execution: " + profile[path_key])
    subprocess.run([sys.executable, str(verifier.target_path(pack, profile["patchTool"])), mode,
                    "--root", str(pack), "--manifest", str(verifier.target_path(pack, profile["manifestPath"]))],
                   cwd=pack, check=True)


def restore(pack: Path, cache: Path) -> dict:
    plan = verifier.load_plan(pack)
    # A user-provided original may be a different edition from a free public
    # project. It is already part of the Git checkout, never a mutable paid URL.
    # Fail before base restoration or network access if those exact bytes are absent.
    for row in plan["files"]:
        if row.get("sourceKind") == "bundled-user-provided":
            if row.get("transformation"):
                verifier.validate_grotesque_quiet(pack, row)
                target = verifier.target_path(pack, row["path"])
                verifier.require(not target.exists() or matches(target, row), "Unknown existing bundled derivative target: " + row["path"])
            else:
                verifier.check_bundled_file(pack, row)
    for row in plan["supportFiles"]:
        verifier.check_file(pack, row, "Committed Modified support file")
    known_originals = {e["original"]["path"] for e in plan["baseJarOverrides"]}
    extra = verifier.content_paths(pack) - verifier.expected_content(plan) - known_originals
    verifier.require(not extra, "Unknown active content must be reviewed before restore: " + repr(sorted(extra)[:30]))
    prevalidate_base_inputs(pack, plan)
    prepared_base_jars = prepare_base_jar_overrides(pack, cache, plan)
    downloaded = 0
    payloads = []
    for row in plan["files"]:
        target = verifier.target_path(pack, row["path"])
        if matches(target, row):
            payloads.append((target, row))
            continue
        payload, received = prepare_payload(pack, cache, row)
        downloaded += received
        payloads.append((payload, row))
    # All downloads/derivations have passed before the first source write.
    normalize_base_jars(pack, prepared_base_jars)
    run_quest_localization(pack, plan, "normalize")
    # This validates every existing baseline byte first and refuses modified
    # author configs/scripts/JARs. Extra Modified files are intentionally not
    # deleted by the original importer; the combined verifier accounts for them.
    dynamic_author_restore = None
    if plan["questLocalization"] and plan["questLocalization"].get("schemaVersion") == 2:
        import atm9_quest_restore
        dynamic_author_restore = atm9_quest_restore.restore_profiled_author(
            pack, cache / "upstream", plan["questLocalization"],
            verifier.target_path(pack, "tools/upstream-lock.json").read_bytes(), plan["originalBaseRows"])
    else:
        import_upstream.restore_locked_files(pack, cache / "upstream")
    for row in plan["originalBaseRows"]:
        verifier.check_file(pack, row, "Author baseline file")
    # Finish verifying all network payloads before installing the first addition.
    installed = sum(install(source, pack, row) for source, row in payloads)
    apply_base_jars(pack, prepared_base_jars)
    run_quest_localization(pack, plan, "apply")
    result = verifier.verify(pack)
    result.update({"restoredAdditionalJars": installed, "downloadedAdditionalJars": downloaded,
                   "baseRestore": "import_upstream --restore-locked-files", "personalInstallationsTouched": False,
                   "questLocalizationWorkflow": "normalize, author import, verify originals, apply, verify effective BASE"
                   if plan["questLocalization"] else None})
    if dynamic_author_restore is not None:
        result.update({"baseRestore": "explicit schema2 data-pinned author lock",
                       "dynamicAuthorRestore": dynamic_author_restore,
                       "questLocalizationWorkflow": "normalize, exact new author restore, verify originals, apply, verify effective BASE"})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--cache", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    pack = args.pack.absolute()
    cache = (args.cache or pack / "artifacts/modified-restore").absolute()
    verifier.require(not verifier.is_link(cache), "Cache must not be linked")
    report = restore(pack, cache)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
