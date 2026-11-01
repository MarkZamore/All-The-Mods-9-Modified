"""The one user-approved persistent AllTheLeaks BASE exception; not a locale rule.

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


def require(ok, message):
    if not ok: raise ValueError(message)


def validate(pack, entries, upstream, rows, base_ids, api):
    """Pure lock/path validation, before any normalize/network/write operation."""
    require(isinstance(entries, list) and len(entries) <= 1, "Only one explicitly approved BASE JAR override is supported")
    effective = list(rows)
    if not entries:
        require("alltheleaks" not in base_ids and not any(r.get("projectId") == APPROVED["projectId"] for r in upstream["files"]),
                "Persistent user-owned AllTheLeaks BASE pin is missing; author import must not restore an older JAR")
        return [], effective
    entry = entries[0]
    require(isinstance(entry, dict) and set(entry) == {"modId", "original", "replacement", "reason", "updatePolicy"}, "Invalid BASE JAR override fields")
    require(entry["modId"] == "alltheleaks" and entry["modId"] in base_ids and entry["updatePolicy"] == POLICY, "Only the persistent AllTheLeaks BASE pin is approved")
    require(isinstance(entry["reason"], str) and entry["reason"].strip(), "BASE JAR override needs its explicit reason")
    original, replacement = entry["original"], entry["replacement"]
    require(isinstance(original, dict) and set(original) == {"path", "sha256", "sizeBytes", "version"}, "Invalid BASE JAR original binding")
    api.validate_hash_record(original)
    require(isinstance(original["version"], str) and bool(original["version"]), "Missing original BASE JAR version")
    require(replacement == APPROVED, "BASE JAR replacement is not the exact user-approved official AllTheLeaks pin")
    api.source_url(replacement)
    author = [r for r in upstream["files"] if r.get("projectId") == APPROVED["projectId"]]
    require(len(author) == 1, "Author BASE must contain exactly one AllTheLeaks project row")
    source = author[0]
    require(all(original[k] == source[k] for k in ["path", "sha256", "sizeBytes"]), "BASE JAR original differs from the exact new author row")
    api.source_url(source)
    require(original["path"].startswith("mods/") and original["path"].count("/") == 1 and original["path"].endswith(".jar"), "BASE override original must be a top-level JAR")
    require(sum(r["path"] == original["path"] for r in rows) == 1, "BASE override original row is missing/duplicated")
    require(not any(r["path"].casefold() == replacement["path"].casefold() and r["path"] != original["path"] for r in rows), "BASE replacement collides with another author resource")
    for row in [original, replacement]: api.target_path(pack, row["path"])
    # Do not inherit the old author's metadataUrl/title/file identity into the
    # replacement. Original provenance remains separately in originalBaseRows.
    replacement_row = {**replacement, "metadataUrl": f"https://www.curseforge.com/api/v1/mods/{replacement['projectId']}/files/{replacement['fileId']}"}
    effective = [replacement_row if r["path"] == original["path"] else r for r in rows]
    return copy.deepcopy(entries), effective


def metadata(raw, filename, version):
    top = [m for m in pack_library.read_mods(raw, filename, loader="forge") if m["isLoadedMod"] and m["_depth"] == 0]
    require(len(top) == 1 and top[0]["id"] == "alltheleaks" and top[0]["version"] == version,
            "AllTheLeaks BASE override differs from actual native mod ID/version metadata")


def matches(path, row):
    return path.is_file() and path.stat().st_size == row["sizeBytes"] and hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]


def rebind(entries, fresh, upstream, api):
    """Owner review: find the actual author mod ID, retain our approved pin.

    Fresh BASE membership is independently verified by the caller. Project ID
    alone never promotes a new dependency or a same-name unrelated JAR to BASE.
    """
    if not entries: return []
    require(len(entries) == 1 and entries[0]["replacement"] == APPROVED and entries[0]["modId"] == "alltheleaks" and entries[0]["updatePolicy"] == POLICY,
            "Cannot carry an unapproved BASE pin into a future author release")
    found = []
    for row in upstream["files"]:
        if not row["path"].startswith("mods/") or not row["path"].endswith(".jar"): continue
        path = api.safe(fresh, row["path"])
        top = [m for m in pack_library.read_mods(path.read_bytes(), path.name, loader="forge") if m["isLoadedMod"] and m["_depth"] == 0]
        if any(m["id"] == "alltheleaks" for m in top):
            require(len(top) == 1 and row.get("projectId") == APPROVED["projectId"], "Fresh AllTheLeaks author row has wrong project/multiple mod identity")
            found.append((row, top[0]["version"]))
    require(len(found) == 1, "Fresh author BASE needs exactly one actual AllTheLeaks; preserving its pin needs owner review if absent")
    row, version = found[0]
    result = copy.deepcopy(entries)
    result[0]["original"] = {**{k: row[k] for k in ["path", "sha256", "sizeBytes"]}, "version": version}
    return result


def author_payload(pack, original, cache, api):
    """Owner stage-author only: verified offline cache, never hidden network."""
    path = api.safe(pack, original["path"])
    if matches(path, original):
        metadata(path.read_bytes(), Path(original["path"]).name, original["version"])
        return path.read_bytes()
    require(cache is not None, "Pinned BASE original is absent; pass explicit offline --base-cache with locked/<original SHA256>")
    path = api.safe(cache, "locked/" + original["sha256"])
    require(matches(path, original), "Explicit offline BASE original cache differs/missing")
    metadata(path.read_bytes(), Path(original["path"]).name, original["version"])
    return path.read_bytes()
