#!/usr/bin/env python3
"""Verify the exact author ATM9 payload plus its separately pinned additions.

Preparation checks are static composition checks. Pass --require-loaded-inventory
for publication with a recorded Forge ModList or a guarded exact-removal projection.
A projection is reported separately and never becomes a fresh native observation.
Neither mode establishes a successful client/world/AI/Steam runtime by itself.
"""
from __future__ import annotations

import argparse
import base64
from collections import defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import unquote, urlsplit
import zipfile

import pack_library
import atm9_base_jar_overrides
import carpets_recipe_policy
import waypoint_source_policy

CONTENT_ROOTS = {"mods", "config", "kubejs", "scripts", "defaultconfigs", "data",
                 "resourcepacks", "shaderpacks", "configureddefaults", "packmenu",
                 "datapacks", "resources", "launcher"}
HASH_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
MOD_PATTERN = re.compile(r"[a-z][a-z0-9_]{1,63}\Z")
RESERVED = {"con", "prn", "aux", "nul", *[f"com{x}" for x in range(1, 10)],
            *[f"lpt{x}" for x in range(1, 10)]}
# This narrow exception is the user's explicit approval to localize Verity.
# It does not permit altering another author's JAR or introducing a helper mod.
APPROVED_VERITY_SOURCE = {
    "sha256": "f76f641f17ea3e3b2e8486596790ae65c27c2b016fae6ed8557c67887816b7d0",
    "sizeBytes": 256881551,
    "sourceUrl": "https://mediafilez.forgecdn.net/files/9300/987/verity-6.0.0.jar",
    "fileName": "verity-6.0.0.jar",
    "fileId": 9300987,
}
APPROVED_GROTESQUE_QUIET = {
    "originalPath": "tools/GrotesqueSteve/source/grotesque_steve-1.4.2-forge-1.20.1.jar",
    "originalSha256": "7edde5b1506a69a725412769525ba16122b1dd4c38e35f3edc5c015eef3a6f63",
    "originalSizeBytes": 22223025,
    "patchTool": "tools/grotesque_steve_quiet.py",
    "patchToolSha256": "7ffd540ddefa641f5bb897760002ed45de15a194c6def473865e27e9de3688a0",
    "path": "mods/grotesque_steve-1.4.2-quiet.1-forge-1.20.1.jar",
    "fileName": "grotesque_steve-1.4.2-quiet.1-forge-1.20.1.jar",
    "sha256": "ffa7df6fb07e54217757436b566fa0073b460c5fa4b695cfd2d4d40692208052",
    "sizeBytes": 26240866, "version": "1.4.2-quiet.1",
}
QUEST_MANIFEST_PATH = "tools/atm9_ru_quests/manifest.json"
QUEST_PATCH_TOOL = "tools/atm9_ru_quests.py"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_relative(value: str) -> str:
    require(isinstance(value, str) and value and "\\" not in value and ":" not in value
            and "\x00" not in value, "Unsafe managed path: " + repr(value))
    parts = value.split("/")
    require(not PurePosixPath(value).is_absolute() and all(
        x not in {"", ".", ".."} and x.rstrip(" .") == x and
        x.split(".", 1)[0].casefold() not in RESERVED and not any(ord(c) < 32 or c in '<>"|?*' for c in x)
        for x in parts), "Unsafe managed path: " + repr(value))
    return value


def is_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        return bool(getattr(path.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except FileNotFoundError:
        return False


def target_path(root: Path, relative: str) -> Path:
    target = root / safe_relative(relative)
    for path in [target, *target.parents]:
        require(not is_link(path), "Refusing linked managed path: " + str(path))
        if path == root:
            break
    require(target.resolve().is_relative_to(root.resolve()), "Managed path escapes pack: " + relative)
    return target


def validate_hash_record(row: dict):
    require(isinstance(row, dict), "Invalid file record")
    safe_relative(row.get("path"))
    require(isinstance(row.get("sizeBytes"), int) and not isinstance(row["sizeBytes"], bool)
            and row["sizeBytes"] >= 0, "Invalid file size: " + row["path"])
    require(isinstance(row.get("sha256"), str) and HASH_PATTERN.fullmatch(row["sha256"]),
            "Invalid SHA256: " + row["path"])


def check_file(pack: Path, row: dict, label="Locked file"):
    target = target_path(pack, row["path"])
    require(target.is_file(), label + " is missing: " + row["path"])
    require(target.stat().st_size == row["sizeBytes"], label + " size mismatch: " + row["path"])
    require(sha256(target) == row["sha256"], label + " SHA256 mismatch: " + row["path"])


def validate_support_resource(row: dict):
    """Support is configuration/data, with no standalone executable exception."""
    validate_hash_record(row)
    relative = row["path"]
    require(relative.split("/", 1)[0] in CONTENT_ROOTS - {"mods"}
            and row.get("kind") in {"configuration", "resource"},
            "Invalid support file kind/root: " + relative)
    require(not relative.lower().endswith((".jar", ".class", ".java", ".dll", ".exe", ".cmd", ".bat", ".ps1")),
            "Executable/helper files are not support resources: " + relative)
    require(isinstance(row.get("reason"), str) and row["reason"].strip(), "Support file needs a reason: " + relative)


def verify_retired_diagnostics(pack: Path):
    """Keep retired debugging out of a future source restore; never edit user files."""
    for relative in ("launcher/diagnostics/recipe-exception-observer.jar",
                     "launcher/diagnostics/Start-RecipeDiagnostics.ps1",
                     "launcher/diagnostics/Start-RecipeDiagnostics.cmd",
                     "kubejs/startup_scripts/atm9_modified_recipe_diagnostics.js"):
        require(not target_path(pack, relative).exists(), "Retired temporary diagnostic remains in source: " + relative)
    jvm = target_path(pack, "launcher/jvm-args.txt")
    if jvm.is_file():
        flags = [line.strip() for line in jvm.read_text(encoding="utf-8-sig").splitlines()
                 if line.strip() and not line.strip().startswith("#")]
        require(not any(value.startswith(("-agentlib:jdwp", "-Xrunjdwp", "-Dlanminecraft.diagnostics.recipeIds")) for value in flags),
                "Retired temporary diagnostic JVM flag remains in source")
    owned = target_path(pack, "launcher/pack-owned.txt")
    if owned.is_file():
        lines = [line.strip().rstrip("/") for line in owned.read_text(encoding="utf-8-sig").splitlines()
                 if line.strip() and not line.strip().startswith("#")]
        require(not any(line == "launcher/diagnostics" or line.startswith("launcher/diagnostics/") for line in lines),
                "Retired temporary diagnostic ownership remains in source")


def source_url(row: dict, *, url=None, filename=None) -> str:
    """Accept exact pinned public CurseForge/Modrinth CDN paths, never a mirror."""
    url = row.get("sourceUrl") if url is None else url
    require(isinstance(url, str), "Missing official source URL: " + row["path"])
    parsed = urlsplit(url)
    require(parsed.scheme == "https" and not parsed.username and not parsed.password
            and not parsed.query and not parsed.fragment and parsed.port is None,
            "Source must be a pinned official HTTPS URL: " + row["path"])
    file_id, project_id = row.get("fileId"), row.get("projectId")
    if parsed.hostname in {"edge.forgecdn.net", "mediafilez.forgecdn.net", "media.forgecdn.net"}:
        require(isinstance(file_id, int) and not isinstance(file_id, bool) and file_id > 0
                and isinstance(project_id, int) and not isinstance(project_id, bool) and project_id > 0,
                "CurseForge files require exact numeric project/file IDs: " + row["path"])
        # Official redirects normalize e.g. /7065/024/ to /7065/24/.
        # Accept only those two spellings of this exact pinned numeric ID.
        prefixes = {f"/files/{file_id // 1000}/{file_id % 1000:03d}/",
                    f"/files/{file_id // 1000}/{file_id % 1000}/"}
        require(any(parsed.path.startswith(prefix) for prefix in prefixes),
                "CurseForge URL does not match the pinned file ID: " + row["path"])
    elif parsed.hostname == "cdn.modrinth.com":
        require(isinstance(project_id, str) and re.fullmatch(r"[A-Za-z0-9]+", project_id)
                and isinstance(file_id, str) and re.fullmatch(r"[A-Za-z0-9]+", file_id),
                "Modrinth files require exact project/version IDs: " + row["path"])
        require(parsed.path.startswith(f"/data/{project_id}/versions/{file_id}/"),
                "Modrinth URL does not match the pinned project/version IDs: " + row["path"])
    else:
        raise ValueError("Unsupported/nonofficial locked source host: " + str(parsed.hostname))
    expected = filename or row["fileName"]
    require(unquote(parsed.path.rsplit("/", 1)[-1]) == expected,
            "Source filename differs from the lock: " + row["path"])
    return url


def download_record(pack: Path, row: dict) -> dict:
    """Resolve the one explicitly authorized reproducible Verity derivative."""
    require(row.get("sourceKind", "official-download") == "official-download",
            "Bundled user-provided files have no download source; restore the exact Git-tracked original JAR")
    transformation = row.get("transformation")
    if not transformation:
        source_url(row)
        return row
    require(isinstance(transformation, dict) and row["modIds"] == ["verity"] and
            row["kind"] == "requested" and transformation.get("kind") == "russian-localization" and
            transformation.get("patchTool") == "tools/verity_russian.py",
            "Only the explicitly approved Verity Russian localization transformation is allowed")
    require(transformation.get("originalSha256") == APPROVED_VERITY_SOURCE["sha256"] and
            transformation.get("originalSizeBytes") == APPROVED_VERITY_SOURCE["sizeBytes"] and
            transformation.get("originalSourceUrl") == APPROVED_VERITY_SOURCE["sourceUrl"] and
            row.get("fileId") == APPROVED_VERITY_SOURCE["fileId"] and
            row.get("sourceUrl") == APPROVED_VERITY_SOURCE["sourceUrl"],
            "Verity transformation must use the exact approved official author source")
    require(isinstance(transformation.get("reason"), str) and transformation["reason"].strip(),
            "Verity localization transformation needs an explicit reason")
    patch_tool = target_path(pack, transformation["patchTool"])
    require(patch_tool.is_file(), "Missing reproducible Verity patch tool")
    original = {**row, **APPROVED_VERITY_SOURCE}
    original.pop("transformation", None)
    source_url(original)
    return original


def validate_grotesque_quiet(pack: Path, row: dict):
    transformation = row.get("transformation")
    require(isinstance(transformation, dict) and set(transformation) == {
        "kind", "patchTool", "patchToolSha256", "originalPath", "originalSha256", "originalSizeBytes", "reason"},
        "Invalid bundled Grotesque quiet transformation fields")
    require(transformation["kind"] == "grotesque-steve-quiet" and row.get("modIds") == ["grotesque_steve"] and
            row.get("kind") == "requested" and row.get("sourceKind") == "bundled-user-provided",
            "Only the specifically approved user-provided Grotesque quiet transformation is permitted")
    require(all(transformation[k] == APPROVED_GROTESQUE_QUIET[k] for k in [
        "patchTool", "patchToolSha256", "originalPath", "originalSha256", "originalSizeBytes"]),
        "Grotesque quiet must use the exact approved original and reproducible tool")
    require(all(row.get(k) == APPROVED_GROTESQUE_QUIET[k] for k in ["path", "fileName", "sha256", "sizeBytes", "version"]),
            "Grotesque quiet output must be the exact reviewed derivative")
    require(isinstance(transformation["reason"], str) and transformation["reason"].strip(), "Grotesque quiet needs an explicit reason")
    check_file(pack, {"path": transformation["originalPath"], "sha256": transformation["originalSha256"],
                      "sizeBytes": transformation["originalSizeBytes"]}, "Git-tracked user-provided Grotesque original source")
    tool = target_path(pack, transformation["patchTool"])
    require(tool.is_file() and sha256(tool) == transformation["patchToolSha256"], "Pinned Grotesque quiet tool differs/missing")
    return transformation


def validate_bundled_source(row: dict, pack: Path | None = None):
    require(row["kind"] == "requested", "A bundled user-provided JAR must be a requested original or its one approved derivative")
    if row.get("transformation"):
        require(pack is not None, "Bundled derivative needs its exact source tree")
        validate_grotesque_quiet(pack, row)
    forbidden = {"sourceUrl", "downloadUrl", "signedUrl", "token", "password", "localPath", "sourcePath"}
    require(not forbidden & set(row), "Private/download fields are forbidden for bundled user-provided sources")
    require("projectId" not in row and "fileId" not in row,
            "Bundled originals must not borrow another edition's project/file IDs")
    official = row.get("officialProjectUrl")
    require(isinstance(official, str), "Bundled original needs its public official project URL")
    parsed = urlsplit(official)
    require(parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password
            and not parsed.query and not parsed.fragment and parsed.port is None,
            "Bundled original project URL must be public HTTPS without credentials or signed query")
    require(row.get("websiteUrl") == official, "Bundled original websiteUrl must identify its actual official edition")
    provenance = row.get("provenance")
    require(isinstance(provenance, dict) and set(provenance) == {"suppliedBy", "edition", "sourceFileName"}
            and provenance.get("suppliedBy") == "user" and isinstance(provenance.get("edition"), str)
            and provenance["edition"].strip(), "Bundled original needs explicit public user-provided edition provenance")
    supplied_name = safe_relative(provenance["sourceFileName"])
    require("/" not in supplied_name and supplied_name.lower().endswith(".jar"),
            "Bundled provenance records a JAR basename, never a personal path")


def check_bundled_file(pack: Path, row: dict):
    try:
        check_file(pack, row, "Bundled user-provided original")
    except ValueError as error:
        raise ValueError(str(error) + "; restore this exact Git-tracked original JAR. "
                         "No download URL, alternate edition or automated replacement is available.") from error


def validate_quest_localization(pack: Path, lock: dict, upstream: dict, original_rows: list[dict]):
    """Only the explicitly reviewed ATM9 1.1.1 display-resource profile."""
    replacements = lock.get("baseReplacements", [])
    profile = lock.get("questLocalization")
    if "questLocalization" not in lock:
        require(not replacements,
                "Base replacements are not authorized by this restore profile; use an explicitly reviewed replacement workflow")
        return None, [], original_rows
    if isinstance(profile, dict) and profile.get("schemaVersion") == 2:
        # Explicit future recipe only. The legacy four-field107/1.1.1 reader
        # below remains unchanged; reviewed new data cannot authorize JAR or
        # arbitrary config replacements through this locale/display route.
        import atm9_quest_profile
        import atm9_quest_restore
        upstream_bytes = target_path(pack, "tools/upstream-lock.json").read_bytes()
        atm9_quest_restore.validate_author_downloads(upstream_bytes, original_rows)
        checked = atm9_quest_profile.validate(
            pack, profile, upstream_bytes,
            original_rows, replacements, lock.get("supportFiles", []))
        return profile, checked["replacements"], checked["effectiveBaseRows"]
    require(isinstance(profile, dict) and set(profile) == {
        "manifestPath", "manifestSha256", "patchTool", "patchToolSha256"}, "Invalid questLocalization profile")
    require(profile["manifestPath"] == QUEST_MANIFEST_PATH and profile["patchTool"] == QUEST_PATCH_TOOL,
            "Quest localization must use the explicitly reviewed manifest and tool paths")
    for path_key, hash_key in [("manifestPath", "manifestSha256"), ("patchTool", "patchToolSha256")]:
        require(isinstance(profile[hash_key], str) and HASH_PATTERN.fullmatch(profile[hash_key]),
                "Invalid quest localization SHA256: " + hash_key)
        path = target_path(pack, profile[path_key])
        require(path.is_file() and sha256(path) == profile[hash_key], "Pinned quest localization file differs: " + profile[path_key])
    manifest_path = target_path(pack, profile["manifestPath"])
    require(manifest_path.stat().st_size <= 8 * 1024 * 1024, "Quest localization manifest exceeds its byte limit")
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate quest localization JSON field: " + key)
            result[key] = value
        return result
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    require(isinstance(manifest, dict) and type(manifest.get("schemaVersion")) is int and manifest["schemaVersion"] == 1 and
            manifest.get("kind") == "ftbquests-russian-display-localization" and
            manifest.get("sourceVersion") == upstream["pack"].get("version") == "1.1.1",
            "Unsupported quest localization profile kind/source version")
    files = manifest.get("files")
    require(isinstance(files, list) and len(files) == 107 and isinstance(replacements, list) and len(replacements) == 107,
            "Quest localization must declare the exact reviewed 107 replacement files")
    original = {row["path"]: row for row in original_rows}
    localized, expected = {}, {}
    for row in files:
        require(isinstance(row, dict), "Invalid quest localization manifest row")
        relative = safe_relative(row.get("path"))
        require(relative == "kubejs/assets/kubejs/lang/en_us.json" or
                relative.startswith("config/ftbquests/quests/") and relative.endswith(".snbt"),
                "Quest localization cannot replace JARs or other author resources: " + relative)
        require(relative not in localized and relative in original, "Duplicate/non-BASE quest localization path: " + relative)
        before = {"path": relative, "sha256": row.get("originalSha256"), "sizeBytes": row.get("originalSizeBytes")}
        after = {"path": relative, "sha256": row.get("localizedSha256"), "sizeBytes": row.get("localizedSizeBytes")}
        validate_hash_record(before); validate_hash_record(after)
        require(all(original[relative][key] == before[key] for key in ["sha256", "sizeBytes"]),
                "Quest localization original differs from frozen BASE: " + relative)
        require(before["sha256"] != after["sha256"], "Quest localization must describe an actual display replacement: " + relative)
        edits = row.get("edits")
        require(isinstance(edits, list) and edits, "Quest localization replacement needs reversible edits: " + relative)
        original_end = localized_end = delta = 0
        for edit in edits:
            require(isinstance(edit, dict), "Invalid reversible quest localization edit")
            if relative != "kubejs/assets/kubejs/lang/en_us.json":
                field_path = edit.get("displayPath")
                require(isinstance(field_path, list) and next((part for part in reversed(field_path) if isinstance(part, str)), None)
                        in {"title", "subtitle", "description", "hover"},
                        "Quest localization edit is not a declared human-display field: " + relative)
            before_offset, after_offset = edit.get("originalOffset"), edit.get("localizedOffset")
            require(type(before_offset) is int and type(after_offset) is int and
                    before_offset >= original_end and after_offset >= localized_end and
                    after_offset == before_offset + delta, "Unordered/invalid quest localization edit offsets: " + relative)
            chunks = []
            for key in ["originalBase64", "localizedBase64"]:
                value = edit.get(key)
                require(isinstance(value, str), "Invalid reversible quest localization Base64: " + relative)
                try:
                    decoded = base64.b64decode(value, validate=True)
                except (ValueError, base64.binascii.Error) as error:
                    raise ValueError("Invalid reversible quest localization Base64: " + relative) from error
                require(base64.b64encode(decoded).decode("ascii") == value, "Noncanonical quest localization Base64: " + relative)
                chunks.append(decoded)
            require(chunks[0] or chunks[1], "Empty quest localization edit: " + relative)
            if relative == "kubejs/assets/kubejs/lang/en_us.json":
                require(not chunks[0], "Quest localization EN-US compatibility edits must be append-only")
            original_end = before_offset + len(chunks[0]); localized_end = after_offset + len(chunks[1])
            require(original_end <= before["sizeBytes"] and localized_end <= after["sizeBytes"],
                    "Quest localization edit exceeds its file bounds: " + relative)
            delta += len(chunks[1]) - len(chunks[0])
        require(after["sizeBytes"] == before["sizeBytes"] + delta, "Quest localization edit sizes differ: " + relative)
        target_path(pack, relative)
        localized[relative] = {**original[relative], "sha256": after["sha256"], "sizeBytes": after["sizeBytes"]}
        expected[relative] = {"path": relative, "originalSha256": before["sha256"], "originalSizeBytes": before["sizeBytes"],
                              "sha256": after["sha256"], "sizeBytes": after["sizeBytes"], "kind": "quest-localization"}
    require("kubejs/assets/kubejs/lang/en_us.json" in localized, "Quest localization must include its reviewed EN-US compatibility resource")
    require(manifest.get("sourceLangSha256") == original["kubejs/assets/kubejs/lang/en_us.json"]["sha256"],
            "Quest localization language source differs from frozen BASE")
    seen = set()
    for row in replacements:
        require(isinstance(row, dict) and set(row) == {"path", "originalSha256", "originalSizeBytes", "sha256", "sizeBytes", "kind", "reason"},
                "Invalid quest localization replacement record")
        relative = row.get("path")
        require(relative in expected and relative not in seen, "Duplicate/unreviewed quest localization replacement path: " + str(relative))
        require({key: row[key] for key in expected[relative]} == expected[relative], "Quest localization lock/manifest record differs: " + relative)
        require(isinstance(row["reason"], str) and row["reason"].strip(), "Quest localization replacement needs an explicit reason: " + relative)
        seen.add(relative)
    require(seen == set(expected), "Quest localization lock and manifest path sets differ")
    return profile, replacements, [localized.get(row["path"], row) for row in original_rows]


def load_plan(pack: Path) -> dict:
    """Validate every lock/path/provenance before a restore can write anything."""
    pack = pack.absolute()
    require(not is_link(pack), "Pack root must not be linked")
    verify_retired_diagnostics(pack)
    lock_path = target_path(pack, "tools/modified-lock.json")
    lock = read_json(lock_path)
    require(lock.get("schemaVersion") == 1, "Unsupported Modified lock schema")
    for key, relative in [("upstreamLockSha256", "tools/upstream-lock.json"),
                          ("baseModIdsSha256", "tools/base-mod-ids.json")]:
        require(isinstance(lock.get(key), str) and HASH_PATTERN.fullmatch(lock[key]), "Missing/invalid " + key)
        require(sha256(target_path(pack, relative)) == lock[key], "Frozen baseline file differs: " + relative)
    upstream = read_json(target_path(pack, "tools/upstream-lock.json"))
    base_ids_doc = read_json(target_path(pack, "tools/base-mod-ids.json"))
    base_ids = base_ids_doc.get("modIds")
    require(isinstance(base_ids, list) and len(base_ids) == len(set(base_ids)) and all(
        isinstance(x, str) and MOD_PATTERN.fullmatch(x) for x in base_ids), "Invalid frozen BASE mod ID inventory")
    base_rows = [*upstream["files"], *upstream["overrides"], upstream["client"]]
    require(all(x.get("included", True) for x in upstream["files"]), "Historical entries cannot be active baseline files")
    seen = set()
    for row in base_rows:
        validate_hash_record(row)
        key = row["path"].casefold()
        require(key not in seen, "Duplicate baseline path: " + row["path"])
        seen.add(key)
        target_path(pack, row["path"])
    original_base_rows = base_rows
    quest_profile, replacements, base_rows = validate_quest_localization(pack, lock, upstream, original_base_rows)
    quest_base_rows = base_rows
    jar_overrides, base_rows = atm9_base_jar_overrides.validate(
        pack, lock.get("baseJarOverrides", []), upstream, base_rows, set(base_ids), __import__(__name__))
    for row in base_rows:
        seen.add(row["path"].casefold())
    files, support = lock.get("files"), lock.get("supportFiles", [])
    require(isinstance(files, list) and isinstance(support, list), "Modified files/supportFiles must be lists")
    for row in files:
        validate_hash_record(row)
        relative = row["path"]
        require(relative.startswith("mods/") and relative.count("/") == 1 and relative.lower().endswith(".jar"),
                "Added mods must be top-level mods/*.jar files: " + relative)
        require(row.get("fileName") == relative.split("/")[1], "Filename/path mismatch: " + relative)
        require(row.get("kind") in {"requested", "dependency"}, "Unclassified addition: " + relative)
        require(isinstance(row.get("version"), str) and row["version"], "Missing addition version: " + relative)
        ids = row.get("modIds")
        require(isinstance(ids, list) and len(ids) == len(set(ids)) and all(
            isinstance(x, str) and MOD_PATTERN.fullmatch(x) for x in ids), "Invalid declared mod IDs: " + relative)
        require(not set(ids) & set(base_ids), "Added JAR duplicates frozen BASE mod IDs: " + relative)
        source_kind = row.get("sourceKind", "official-download")
        require(source_kind in {"official-download", "bundled-user-provided"}, "Unknown addition sourceKind: " + relative)
        if source_kind == "bundled-user-provided":
            validate_bundled_source(row, pack)
        else:
            website = urlsplit(row.get("websiteUrl", ""))
            require(website.scheme == "https" and not website.username and not website.password and
                    website.hostname in {"www.curseforge.com", "curseforge.com", "modrinth.com"},
                    "Addition needs its official project page: " + relative)
            download_record(pack, row)
    for row in support:
        validate_support_resource(row)
    for row in [*files, *support]:
        key = row["path"].casefold()
        require(key not in seen, "Addition overwrites baseline or duplicates an active path: " + row["path"])
        seen.add(key)
        target_path(pack, row["path"])
    platform = read_json(target_path(pack, "portable-pack.json"))
    require(platform.get("minecraftVersion") == upstream["pack"]["minecraftVersion"] and
            platform.get("loader") == upstream["pack"]["loader"] and
            platform.get("clientJar") == upstream["client"]["path"], "Platform differs from the frozen author base")
    return {"pack": pack, "lock": lock, "upstream": upstream, "baseRows": base_rows,
            "originalBaseRows": original_base_rows, "questLocalization": quest_profile, "baseReplacements": replacements,
            "questBaseRows": quest_base_rows, "baseJarOverrides": jar_overrides,
            "files": files, "supportFiles": support, "baseIds": set(base_ids), "platform": platform}


def content_paths(pack: Path) -> set[str]:
    result = set()
    for root in CONTENT_ROOTS:
        folder = target_path(pack, root)
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            require(not is_link(path), "Linked content is not allowed: " + str(path))
            if path.is_file():
                result.add(path.relative_to(pack).as_posix())
    return result


def expected_content(plan: dict) -> set[str]:
    # This existing launcher ownership file is a declaration, never executable code.
    return {x["path"] for x in [*plan["baseRows"], *plan["files"], *plan["supportFiles"]]
            if x["path"].split("/", 1)[0] in CONTENT_ROOTS} | {"launcher/pack-owned.txt"}


def jar_metadata(path: Path) -> list[dict]:
    return pack_library.read_mods(path.read_bytes(), path.name, loader="forge")


def verify(pack: Path, *, require_loaded_inventory=False) -> dict:
    plan = load_plan(pack)
    rows = [*plan["baseRows"], *plan["files"], *plan["supportFiles"]]
    base_paths = {x["path"] for x in plan["baseRows"]}
    for row in rows:
        if row.get("sourceKind") == "bundled-user-provided":
            check_bundled_file(pack, row)
        else:
            check_file(pack, row, "Author baseline file" if row["path"] in base_paths else "Modified locked file")
    if any(row["path"] == carpets_recipe_policy.OVERRIDE for row in plan["supportFiles"]):
        carpets_recipe_policy.verify(pack)
    if any(row["path"] == waypoint_source_policy.SCRIPT for row in plan["supportFiles"]):
        waypoint_source_policy.verify(pack)
    expected, actual = expected_content(plan), content_paths(pack)
    require(actual == expected, "Unexpected/missing active content: " + repr(sorted(actual ^ expected)[:30]))
    require(target_path(pack, "launcher/pack-owned.txt").is_file(), "Missing launcher ownership declarations")
    jars = sorted(x["path"] for x in rows if x["path"].startswith("mods/") and x["path"].lower().endswith(".jar"))
    top_ids = defaultdict(list)
    metadata = {}
    declared_ids = set()
    for relative in jars:
        mods = jar_metadata(pack / relative)
        metadata[relative] = mods
        for mod in mods:
            if mod["isLoadedMod"]:
                declared_ids.add(mod["id"])
                if mod["_depth"] == 0:
                    top_ids[mod["id"]].append(relative)
    duplicates = {key: value for key, value in top_ids.items() if len(value) > 1}
    require(not duplicates, "Duplicate top-level Forge mod IDs: " + repr(duplicates))
    for row in plan["files"]:
        top = [m for m in metadata[row["path"]] if m["isLoadedMod"] and m["_depth"] == 0]
        require(set(row["modIds"]) == {m["id"] for m in top}, "Addition mod IDs differ from actual JAR metadata: " + row["path"])
        known_versions = {m["version"] for m in top if m["version"]}
        require(not known_versions or row["version"] in known_versions,
                "Addition version differs from actual JAR metadata: " + row["path"])
        with zipfile.ZipFile(pack / row["path"]) as jar:
            manifest = jar.read("META-INF/MANIFEST.MF").decode("utf-8-sig") if "META-INF/MANIFEST.MF" in jar.namelist() else ""
            require(not re.search(r"(?im)^(?:Premain-Class|Agent-Class):", manifest), "A Java agent cannot be an added content mod: " + row["path"])
    for entry in plan["baseJarOverrides"]:
        row = entry["replacement"]
        atm9_base_jar_overrides.metadata((pack / row["path"]).read_bytes(), row["fileName"], row["version"], entry["modId"])
    hashes = {relative: sha256(pack / relative) for relative in jars}
    inventory_path = pack / "library/loaded-mods.json"
    inventory = read_json(inventory_path) if inventory_path.is_file() else {}
    inventory_current = (inventory.get("schemaVersion") == 1 and inventory.get("sourceJars") == hashes
                         and inventory.get("minecraftVersion") == plan["platform"]["minecraftVersion"]
                         and inventory.get("loader") == plan["platform"]["loader"])
    inventory_kind = pack_library.inventory_evidence_kind(pack, inventory) if inventory_current else None
    actual_ids = []
    if inventory_current:
        for mod in inventory.get("mods", []):
            mod_id = mod.get("id")
            require(mod_id in declared_ids and mod_id not in actual_ids, "Invalid/duplicate actual loaded mod ID: " + str(mod_id))
            actual_ids.append(mod_id)
        require(plan["baseIds"] <= set(actual_ids), "Actual runtime inventory lost frozen BASE IDs")
        require(set(top_ids) <= set(actual_ids), "Actual runtime inventory omits top-level Forge mods")
    require(not require_loaded_inventory or inventory_current,
            "Current exact-hash Forge loaded inventory is required; the existing base inventory is stale")
    return {"status": "PASS", "kind": "static composition verification", "authorVersion": plan["upstream"]["pack"]["version"],
            "minecraftVersion": plan["platform"]["minecraftVersion"], "loader": plan["platform"]["loader"],
            "basePayloadFiles": len(plan["baseRows"]), "baseReplacements": plan["baseReplacements"],
            "questLocalization": plan["questLocalization"],
            "baseJarOverrides": plan["baseJarOverrides"],
            "additionJars": len(plan["files"]), "requestedJars": len([x for x in plan["files"] if x["kind"] == "requested"]),
            "dependencyJars": len([x for x in plan["files"] if x["kind"] == "dependency"]),
            "bundledUserProvidedJars": len([x for x in plan["files"] if x.get("sourceKind") == "bundled-user-provided"]),
            "supportFiles": len(plan["supportFiles"]), "jarFiles": len(jars), "topLevelForgeModIds": len(top_ids),
            "duplicateTopLevelIds": duplicates, "runtimeInventoryVerified": inventory_current and inventory_kind == "native-observation",
            "inventorySourceBindingsVerified": inventory_current, "inventoryEvidenceKind": inventory_kind,
            "actualLoadedPackModCount": len(actual_ids) if inventory_current and inventory_kind == "native-observation" else None,
            "projectedLoadedPackModCount": len(actual_ids) if inventory_current and inventory_kind == "exact-removal-projection" else None,
            "runtimeAcceptanceClaimed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--require-loaded-inventory", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = verify(args.pack.absolute(), require_loaded_inventory=args.require_loaded_inventory)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
