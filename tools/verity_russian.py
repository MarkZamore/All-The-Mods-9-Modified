"""Rebuild one explicitly authorized Russian Verity fork from the exact official JAR.

This is an offline preparation tool. The game loads no patcher, agent or helper.
"""
from __future__ import annotations

import argparse
import base64
import collections
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import zlib

SUPPORT = Path(__file__).resolve().parent / "VerityRussian"
AUTHOR_SHA = "f76f641f17ea3e3b2e8486596790ae65c27c2b016fae6ed8557c67887816b7d0"
AUTHOR_SIZE = 256881551
VERSION = "6.0.0-ru.1"
LIBRARIES = {
    "asm-9.8.jar": (126113, "876eab6a83daecad5ca67eb9fcabb063c97b5aeb8cf1fca7a989ecde17522051"),
    "asm-tree-9.8.jar": (51934, "14b7880cb7c85eed101e2710432fc3ffb83275532a6a894dc4c4095d49ad59f1"),
}


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def matches(path: Path, size: int, digest: str) -> bool:
    return path.is_file() and not path.is_symlink() and path.stat().st_size == size and sha(path) == digest


def ensure_asset(spec: dict, cache: Path) -> Path:
    target = cache / (spec["sha256"] + "-" + spec["name"])
    if matches(target, spec["size"], spec["sha256"]):
        return target
    cache.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".part")
    request = urllib.request.Request(spec["url"], headers={"User-Agent": "LANMinecraft-VerityRussian/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, partial.open("wb") as output:
        shutil.copyfileobj(response, output, 1024 * 1024)
    if not matches(partial, spec["size"], spec["sha256"]):
        raise ValueError("Official speech asset failed size/SHA256: " + spec["name"])
    partial.replace(target)
    return target


def zip_bytes(entries: dict[str, bytes]) -> bytes:
    target = io.BytesIO()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, (2026, 10, 28, 0, 0, 0))
            # Match the frozen Windows artifact on every preparation platform.
            info.create_system = 0
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)
    return target.getvalue()


def key(row: dict) -> tuple:
    return tuple(row[x] for x in ("class", "method", "descriptor", "kind", "original"))


def model_replacements(inventory: list[dict]) -> list[dict]:
    rows = []
    for row in inventory:
        original = row["original"]
        target = None
        if row["class"] == "varmite/verity/entity/llm/builder/LocalTTSBuilder" and row["method"] == "init" and original == "en_US-ryan-medium.onnx":
            target = "ru_RU-denis-medium.onnx"
        if row["class"] in ("varmite/verity/entity/llm/builder/ModelExtractor", "varmite/verity/client/audio/TTSHandler"):
            if original in ("tiny.en-encoder.int8.onnx", "tiny.en-decoder.int8.onnx", "tiny.en-tokens.txt"):
                target = original.replace("tiny.en", "base")
            elif row["class"].endswith("/ModelExtractor") and original == "sherpa-model":
                target = "sherpa-model-ru-base-v1"
        if target is not None:
            rows.append({**row, "translated": target})
    if len(rows) != 8:
        raise ValueError("Unexpected native model filename/cache inventory")
    return rows


def name_replacements(inventory: list[dict]) -> list[dict]:
    rows = []
    for row in inventory:
        original = row["original"]
        if row["class"] == "varmite/verity/client/audio/TTSHandler" and row["method"] == "sanitizeTranscript" and "verdi|verdy|verde|verdie" in original:
            target = original.replace("(?i)", "(?iuU)").replace("(verdi|", "(верити|верите|веритий|verdi|")
        elif row["class"] == "varmite/verity/entity/llm/AiAPI" and row["method"] == "<clinit>" and "verdi|verdy|veriti|veritiy" in original:
            target = "(?iuU)" + original.replace("(verdi|", "(верити|верите|веритий|verdi|")
        else:
            continue
        rows.append({**row, "translated": target})
    if len(rows) != 2:
        raise ValueError("Unexpected native speech-name normalizer inventory")
    return rows


def build(args: argparse.Namespace) -> dict:
    if args.input.resolve() == args.output.resolve():
        raise ValueError("The immutable author source and derivative output must be separate files")
    if not matches(args.input, AUTHOR_SIZE, AUTHOR_SHA):
        raise ValueError("Only exact official Verity 6.0.0 file9300987 is supported")
    java_home = args.java_home or (Path(os.environ["JAVA_HOME"]) if os.environ.get("JAVA_HOME") else None)
    executable_suffix = ".exe" if os.name == "nt" else ""
    java = str(java_home / ("bin/java" + executable_suffix)) if java_home else shutil.which("java")
    javac = str(java_home / ("bin/javac" + executable_suffix)) if java_home else shutil.which("javac")
    if not java or not javac:
        raise ValueError("A JDK17+ is required by this offline preparation tool")
    for filename, (size, digest) in LIBRARIES.items():
        if not matches(SUPPORT / "lib" / filename, size, digest):
            raise ValueError("Offline ASM support library differs from its approved pin")
    cp = os.pathsep.join(str((SUPPORT / "lib" / name).resolve()) for name in LIBRARIES)
    build_root = args.cache.parent / "verity-russian-builds"
    build_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="build-", dir=build_root) as temp:
        work = Path(temp)
        subprocess.run([javac, "--release", "17", "-encoding", "UTF-8", "-cp", cp, "-d", str(work), str(SUPPORT / "VerityBinaryPatch.java")], check=True)
        run = [java, "-Dfile.encoding=UTF-8", "-cp", str(work) + os.pathsep + cp, "VerityBinaryPatch"]
        subprocess.run(run + ["inventory", str(args.input), str(work / "inventory.tsv")], check=True)
        counts = collections.Counter()
        inventory = []
        for line in (work / "inventory.tsv").read_text(encoding="utf-8").splitlines():
            fields = line.split("\t")
            values = [base64.b64decode(value).decode("utf-8") for value in fields[:5]]
            row = dict(zip(("class", "method", "descriptor", "kind", "original"), values), ordinal=int(fields[5]))
            inventory.append(row)
            counts[key(row)] += 1
        translation = json.loads((SUPPORT / "translations.json").read_text(encoding="utf-8"))
        if translation.get("sourceJarSha256") != AUTHOR_SHA:
            raise ValueError("Translation inventory does not pin the approved author JAR")
        replacements = translation["strings"] + model_replacements(inventory) + name_replacements(inventory)
        used = set()
        encoded = []
        for row in replacements:
            identity = key(row)
            exact = identity + (row.get("ordinal"),)
            if exact in used or identity not in counts:
                raise ValueError("Duplicate or absent exact source translation")
            used.add(exact)
            if "occurrences" in row and row["occurrences"] != counts[identity] and "ordinal" not in row:
                raise ValueError("Translation source occurrence count changed")
            if "ordinal" in row and not 0 <= row["ordinal"] < counts[identity]:
                raise ValueError("Exact translation ordinal changed")
            if row["original"].count("\x01") != row["translated"].count("\x01") or row["original"].count("\x02") != row["translated"].count("\x02"):
                raise ValueError("String-concat placeholder count changed")
            fields = [base64.b64encode(value.encode("utf-8")).decode() for value in (*identity, row["translated"])]
            if "ordinal" in row:
                fields.append(str(row["ordinal"]))
            encoded.append("\t".join(fields))
        (work / "translations.tsv").write_text("\n".join(encoded) + "\n", encoding="utf-8")
        subprocess.run(run + ["patch", str(args.input), str(work / "classes"), str(work / "translations.tsv")], check=True)
        files = json.loads((SUPPORT / "speech-pins.json").read_text(encoding="utf-8"))["files"]
        assets = {(entry["repo"].split("/")[-1], entry["name"]): ensure_asset(entry, args.cache) for entry in files}
        with zipfile.ZipFile(args.input) as author:
            updates = {path.relative_to(work / "classes").as_posix(): path.read_bytes() for path in (work / "classes").rglob("*.class")}
            with zipfile.ZipFile(io.BytesIO(author.read("assets/verity/tts/piper.zip"))) as piper:
                voice = {name: piper.read(name) for name in piper.namelist() if not name.endswith("/") and name not in ("en_US-ryan-medium.onnx", "tokens.txt")}
            voice["ru_RU-denis-medium.onnx"] = assets[("vits-piper-ru_RU-denis-medium", "ru_RU-denis-medium.onnx")].read_bytes()
            voice["tokens.txt"] = assets[("vits-piper-ru_RU-denis-medium", "tokens.txt")].read_bytes()
            voice["MODEL_CARD-ru-denis"] = assets[("vits-piper-ru_RU-denis-medium", "MODEL_CARD")].read_bytes()
            if "espeak-ng-data/lang/zle/ru" not in voice or "espeak-ng-data/ru_dict" not in voice:
                raise ValueError("Author eSpeak data does not contain Russian")
            updates["assets/verity/tts/piper.zip"] = zip_bytes(voice)
            updates["assets/verity/sherpa-model.zip"] = zip_bytes({name: assets[("sherpa-onnx-whisper-base", name)].read_bytes() for name in ("base-encoder.int8.onnx", "base-decoder.int8.onnx", "base-tokens.txt")})
            for resource in translation.get("resources", []):
                if resource["path"] != "assets/verity/lang/ru_ru.json":
                    raise ValueError("Unexpected translated data resource")
                updates[resource["path"]] = resource["content"].encode("utf-8")
            russian_lang = json.loads(updates["assets/verity/lang/ru_ru.json"])
            author_lang = json.loads(author.read("assets/verity/lang/en_us.json"))
            if set(author_lang) != set(russian_lang):
                raise ValueError("Russian language keys must match native keys exactly")
            updates["assets/verity/lang/en_us.json"] = updates["assets/verity/lang/ru_ru.json"]
            audio = json.loads((SUPPORT / "audio.json").read_text(encoding="utf-8"))
            if {row["file"] for row in audio["recordings"]} != {"box_verity_0.ogg", "box_verity_2.ogg", "intro.ogg"}:
                raise ValueError("Unexpected localized audio scope")
            for row in audio["recordings"]:
                source = SUPPORT / "audio" / row["file"]
                if not matches(source, row["size"], row["sha256"]) or not source.read_bytes().startswith(b"OggS"):
                    raise ValueError("Localized recording differs from its reviewed Ogg pin")
                updates["assets/verity/sounds/" + row["file"]] = source.read_bytes()
            # Git checkouts can use CRLF. Text resources in the frozen JAR use LF.
            prompt = (SUPPORT / "verity.xml").read_text(encoding="utf-8").encode("utf-8")
            ET.fromstring(prompt)
            old_prompt = author.read("prompts/verity.xml")
            if collections.Counter(re.findall(rb"\{[^{}]+\}", prompt)) != collections.Counter(re.findall(rb"\{[^{}]+\}", old_prompt)):
                raise ValueError("Native prompt placeholders changed")
            old_root, new_root = ET.fromstring(old_prompt), ET.fromstring(prompt)
            if [node.tag for node in old_root.iter()] != [node.tag for node in new_root.iter()]:
                raise ValueError("Native prompt structure changed")
            updates["prompts/verity.xml"] = prompt
            metadata = author.read("META-INF/mods.toml").decode("utf-8")
            if metadata.count('version="6.0.0"') != 1:
                raise ValueError("Author mod version changed")
            description = "Hello, I'm Verity! Your personal helper friend. You can ask me anything, I know everything."
            if metadata.count(description) != 1:
                raise ValueError("Author mod description changed")
            metadata = metadata.replace(description, "Привет! Я Верити, твой личный друг и помощник. Спрашивай о чём угодно. Я знаю всё.")
            updates["META-INF/mods.toml"] = metadata.replace('version="6.0.0"', 'version="' + VERSION + '"').encode("utf-8")
            manifest = author.read("META-INF/MANIFEST.MF")
            if manifest.count(b"Implementation-Version: 6.0.0") != 1:
                raise ValueError("Author implementation version changed")
            updates["META-INF/MANIFEST.MF"] = manifest.replace(b"Implementation-Version: 6.0.0", b"Implementation-Version: " + VERSION.encode())
            pack = json.loads(author.read("pack.mcmeta"))
            if pack["pack"]["pack_format"] != 15:
                raise ValueError("Wrong Minecraft1.20.1 pack format")
            # Immutable record makes the direct fork visible without adding executable code.
            provenance = {"schemaVersion": 1, "version": VERSION, "authorJarSha256": AUTHOR_SHA,
                          "transformation": "Russian localization of exact author Verity6.0.0; no helper mod or runtime agent",
                          "officialSources": files, "updatesFrozenByUser": True,
                          "nativeSpeech": {"tts": "Russian Piper Denis medium", "stt": "multilingual Whisper base int8, ru/transcribe"},
                          "microphone": "unchanged explicit native push-to-talk only",
                          "authoredRecordedAudio": audio,
                          "compatibility": "Original platform, mod ID, dependencies, tools, game mechanics, effects, music and248 intro frames retained. Four enum display labels use toString only; enum name/valueOf/config IDs preserved. Required-name gate also accepts the Russian form of Verity."}
            updates["META-INF/lanminecraft-verity-russian.json"] = (json.dumps(provenance, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            for license_path in (SUPPORT / "licenses").glob("*"):
                notice = license_path.read_text(encoding="utf-8")
                # This notice used CRLF in the frozen artifact; the other notices used LF.
                if license_path.name == "ASM-BSD3.txt":
                    notice = notice.replace("\n", "\r\n")
                updates["META-INF/verity-russian-notices/" + license_path.name] = notice.encode("utf-8")
            entries = {entry.filename: author.read(entry) for entry in author.infolist() if not entry.is_dir()}
            for name in entries:
                if re.match(r"META-INF/.*\.(SF|RSA|DSA)$", name, re.I):
                    raise ValueError("Unexpected signed author archive; a derivative must not claim its signature")
            changed = []
            for name, data in updates.items():
                before = entries.get(name)
                changed.append({"path": name, "oldSha256": hashlib.sha256(before).hexdigest() if before is not None else None,
                                "newSha256": hashlib.sha256(data).hexdigest(), "oldSize": len(before) if before is not None else None,
                                "newSize": len(data)})
            entries.update(updates)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        partial = args.output.with_name(args.output.name + ".part")
        partial.write_bytes(zip_bytes(entries))
        with zipfile.ZipFile(partial) as result:
            if result.testzip() is not None:
                raise ValueError("Generated archive has a bad CRC")
            if set(result.namelist()) != set(entries):
                raise ValueError("Generated archive entry set changed")
        partial.replace(args.output)
        report = {"schemaVersion": 1, "sourceJarSha256": AUTHOR_SHA, "sourceJarSize": AUTHOR_SIZE,
                  "outputJarSha256": sha(args.output), "outputJarSize": args.output.stat().st_size,
                  "version": VERSION, "modIds": ["verity"], "translationKeys": len(replacements),
                  "changedEntries": changed, "newExecutableClasses": [], "zlibVersion": zlib.ZLIB_VERSION,
                  "sourceProvenance": "Fresh official author JAR and official Sherpa/Piper downloads; no previous Modified source or helpers",
                  "remaining": ["Two short box lines are contextual adaptations, not asserted exact transcripts. Box1/cinematic soundtrack and all other effects/music remain original.", "Full client integration and native game lifecycle require separate acceptance."]}
        args.output.with_suffix(".patch-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache", type=Path, default=Path(__file__).resolve().parents[1] / "artifacts/atm9-modified/verity-russian-cache")
    parser.add_argument("--java-home", type=Path)
    args = parser.parse_args()
    report = build(args)
    print(json.dumps({key: report[key] for key in ("outputJarSha256", "outputJarSize", "version", "translationKeys")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
