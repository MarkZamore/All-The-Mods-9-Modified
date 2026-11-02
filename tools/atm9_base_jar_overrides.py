"""Exact approved AllTheLeaks and ModernFix BASE exceptions; not locale rules.

Changing the replacement is a separately reviewed source/data change. A newer
author version never silently replaces this pack-owned compatible pin.
"""
from __future__ import annotations
import copy, hashlib, re
from pathlib import Path
import pack_library

POLICY = "retain-pinned-compatible-jar"
APPROVED = {
    "path": "mods/alltheleaks-1.1.4+1.20.1-forge.jar",
    "fileName": "alltheleaks-1.1.4+1.20.1-forge.jar",
    "sha256": "fb72063a7d17df97740d24355444ef2f95eab97728e1256c639bb432c61b7716",
    "sizeBytes": 1274164,
    "sourceUrl": "https://mediafilez.forgecdn.net/files/9188/826/alltheleaks-1.1.4%2B1.20.1-forge.jar",
    "projectId": 1091339, "fileId": 9188826,
    "version": "1.1.4+1.20.1-forge", "modIds": ["alltheleaks"],
    "websiteUrl": "https://www.curseforge.com/minecraft/mc-mods/alltheleaks",
}
APPROVED_MODERNFIX = {
    "path": "mods/modernfix-forge-5.25.0+mc1.20.1.jar",
    "fileName": "modernfix-forge-5.25.0+mc1.20.1.jar",
    "sha256": "8c0156eec349bb115621e7c3bbf99a5cebf01eea6d9b5a4512fd8cd74b267a91",
    "sizeBytes": 897884,
    "sourceUrl": "https://mediafilez.forgecdn.net/files/7190/629/modernfix-forge-5.25.0%2Bmc1.20.1.jar",
    "projectId": 790626, "fileId": 7190629,
    "version": "5.25.0+mc1.20.1", "modIds": ["modernfix"],
    "websiteUrl": "https://www.curseforge.com/minecraft/mc-mods/modernfix",
}


def approved():
    # Resolve live constants per call: fixtures replace the exact approved
    # payloads, while production remains pinned to these two records only.
    return {"alltheleaks": APPROVED, "modernfix": APPROVED_MODERNFIX}


def title(mod_id):
    return {"alltheleaks": "AllTheLeaks", "modernfix": "ModernFix"}[mod_id]


def require(ok, message):
    if not ok: raise ValueError(message)


def validate(pack, entries, upstream, rows, base_ids, api):
    """Pure lock/path validation, before any normalize/network/write operation."""
    pins = approved()
    require(isinstance(entries, list) and len(entries) <= len(pins), "Only the two exact approved BASE JAR overrides are supported")
    require(all(isinstance(entry, dict) and set(entry) == {"modId", "original", "replacement", "reason", "updatePolicy"} for entry in entries),
            "Invalid BASE JAR override fields")
    ids = [entry["modId"] for entry in entries]
    require(all(isinstance(mod_id, str) and mod_id in pins for mod_id in ids) and len(ids) == len(set(ids)),
            "Duplicate or unapproved BASE JAR override")
    required = {mod_id for mod_id, pin in pins.items() if mod_id in base_ids
                or any(row.get("projectId") == pin["projectId"] for row in upstream["files"])}
    require(set(ids) == required,
            "Persistent user-owned BASE pins are missing or not in author BASE; author import must retain every approved pin")
    effective = list(rows)
    for entry in entries:
        mod_id = entry["modId"]; pin = pins[mod_id]
        require(mod_id in base_ids and entry["updatePolicy"] == POLICY, "Only persistent approved BASE pins are allowed")
        require(isinstance(entry["reason"], str) and entry["reason"].strip(), "BASE JAR override needs its explicit reason")
        original, replacement = entry["original"], entry["replacement"]
        require(isinstance(original, dict) and set(original) == {"path", "sha256", "sizeBytes", "version"}, "Invalid BASE JAR original binding")
        api.validate_hash_record(original)
        require(isinstance(original["version"], str) and bool(original["version"]), "Missing original BASE JAR version")
        require(replacement == pin, "BASE JAR replacement is not the exact user-approved official " + title(mod_id) + " pin")
        api.source_url(replacement)
        author = [row for row in upstream["files"] if row.get("projectId") == pin["projectId"]]
        require(len(author) == 1, "Author BASE must contain exactly one " + title(mod_id) + " project row")
        source = author[0]
        require(all(original[key] == source[key] for key in ["path", "sha256", "sizeBytes"]), "BASE JAR original differs from the exact new author row")
        api.source_url(source)
        require(original["path"].startswith("mods/") and original["path"].count("/") == 1 and original["path"].endswith(".jar"), "BASE override original must be a top-level JAR")
        require(sum(row["path"] == original["path"] for row in effective) == 1, "BASE override original row is missing/duplicated")
        require(not any(row["path"].casefold() == replacement["path"].casefold() and row["path"] != original["path"] for row in effective), "BASE replacement collides with another author resource")
        for row in [original, replacement]: api.target_path(pack, row["path"])
        replacement_row = {**replacement, "metadataUrl": f"https://www.curseforge.com/api/v1/mods/{replacement['projectId']}/files/{replacement['fileId']}"}
        effective = [replacement_row if row["path"] == original["path"] else row for row in effective]
    return copy.deepcopy(entries), effective


def metadata(raw, filename, version, mod_id="alltheleaks"):
    top = [m for m in pack_library.read_mods(raw, filename, loader="forge") if m["isLoadedMod"] and m["_depth"] == 0]
    require(mod_id in approved() and len(top) == 1 and top[0]["id"] == mod_id and top[0]["version"] == version,
            "BASE override differs from actual native mod ID/version metadata")


def matches(path, row):
    return path.is_file() and path.stat().st_size == row["sizeBytes"] and hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]


def rebind(entries, fresh, upstream, api):
    """Owner review: find the actual author mod ID, retain our approved pin.

    Fresh BASE membership is independently verified by the caller. Project ID
    alone never promotes a new dependency or a same-name unrelated JAR to BASE.
    """
    if not entries: return []
    pins = approved()
    require(len(entries) <= len(pins) and all(entry.get("modId") in pins for entry in entries)
            and len({entry["modId"] for entry in entries}) == len(entries)
            and all(entry["replacement"] == pins[entry["modId"]] and entry["updatePolicy"] == POLICY for entry in entries),
            "Cannot carry an unapproved BASE pin into a future author release")
    found = {entry["modId"]: [] for entry in entries}
    for row in upstream["files"]:
        if not row["path"].startswith("mods/") or not row["path"].endswith(".jar"): continue
        path = api.safe(fresh, row["path"])
        top = [m for m in pack_library.read_mods(path.read_bytes(), path.name, loader="forge") if m["isLoadedMod"] and m["_depth"] == 0]
        for mod_id in found:
            if any(mod["id"] == mod_id for mod in top):
                require(len(top) == 1 and row.get("projectId") == pins[mod_id]["projectId"], "Fresh " + title(mod_id) + " author row has wrong project/multiple mod identity")
                found[mod_id].append((row, top[0]["version"]))
    result = copy.deepcopy(entries)
    for entry in result:
        mod_id = entry["modId"]
        require(len(found[mod_id]) == 1, "Fresh author BASE needs exactly one actual " + title(mod_id) + "; preserving its pin needs owner review if absent")
        row, version = found[mod_id][0]
        entry["original"] = {**{key: row[key] for key in ["path", "sha256", "sizeBytes"]}, "version": version}
    return result


def author_payload(pack, original, cache, api, mod_id="alltheleaks"):
    """Owner stage-author only: verified offline cache, never hidden network."""
    path = api.safe(pack, original["path"])
    if matches(path, original):
        metadata(path.read_bytes(), Path(original["path"]).name, original["version"], mod_id)
        return path.read_bytes()
    require(cache is not None, "Pinned BASE original is absent; pass explicit offline --base-cache with locked/<original SHA256>")
    path = api.safe(cache, "locked/" + original["sha256"])
    require(matches(path, original), "Explicit offline BASE original cache differs/missing")
    metadata(path.read_bytes(), Path(original["path"]).name, original["version"], mod_id)
    return path.read_bytes()
