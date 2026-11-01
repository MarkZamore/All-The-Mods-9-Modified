"""Standalone native checks with explicit pinned inputs; never launches a game."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

JAR_PINS = {
    'forge-1.20.1-47.4.0-client.jar': '010adc332f19b05fb24383954ec7a88694666216e480a6824ff0cbc4740c3c66',
    'client-1.20.1-20230612.114412-srg.jar': 'e2e940fe7ca0a9fba5a5c11ad2cf3e2f7df91bbf51d12af22cdde7af18adc344',
    'forge-1.20.1-47.4.0-universal.jar': '2b0e97b22fd4d043dbbcc8e0a44ef0d58915689ed9224e4cd28d5c4976a16bcc',
}
PROVIDERS = {
    'net/minecraft/server/packs/metadata/pack/PackMetadataSectionSerializer.class': 'forge-1.20.1-47.4.0-client.jar',
    'net/minecraft/commands/CommandFunction.class': 'client-1.20.1-20230612.114412-srg.jar',
    'net/minecraftforge/event/entity/player/PlayerEvent$PlayerLoggedInEvent.class': 'forge-1.20.1-47.4.0-universal.jar',
}
AUTHOR = (22223025, '7edde5b1506a69a725412769525ba16122b1dd4c38e35f3edc5c015eef3a6f63')
QUIET = (26240866, 'ffa7df6fb07e54217757436b566fa0073b460c5fa4b695cfd2d4d40692208052')
EXPECTED = {
    'quiet-native-parsers': ['NATIVE_PACK_METADATA_FORMAT 15', 'NATIVE_FUNCTION_LINE_ACCEPTED give @p grotesque_steve:manualbook'],
    'author-native-parsers': ['NATIVE_PACK_METADATA_FORMAT 15', 'NATIVE_AUTHOR_LEADING_SLASH_REJECTED'],
    'quiet-native-callbacks': ['QUIET_CALLBACK_RETURNED GrotesqueMessageProcedure', 'QUIET_CALLBACK_RETURNED AdvancementtriggerProcedure'],
    'author-native-callbacks': ['AUTHOR_NULL_EVENT_DEREFERENCE GrotesqueMessageProcedure', 'AUTHOR_NULL_EVENT_DEREFERENCE AdvancementtriggerProcedure'],
}

def sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def require_jar(path: Path, pin: tuple[int, str]) -> None:
    if not path.is_file() or path.stat().st_size != pin[0] or sha(path) != pin[1]:
        raise ValueError('Wrong author/quiet edition or bytes: ' + path.name)

def read_classpath(path: Path) -> list[Path]:
    text = path.read_text(encoding='utf-8-sig').strip()
    values = json.loads(text) if text.startswith('[') else text.split(os.pathsep)
    if not isinstance(values, list) or not values or not all(isinstance(s, str) and s for s in values):
        raise ValueError('Classpath must be a JSON string array or one host-separated classpath line')
    paths = list(dict.fromkeys(Path(s).resolve() for s in values))
    if not all(p.is_file() and p.suffix.lower() == '.jar' for p in paths):
        raise ValueError('Classpath requires existing JAR files, with no automatic discovery')
    by_name = {p.name: p for p in paths}
    for name, expected in JAR_PINS.items():
        if name not in by_name or sha(by_name[name]) != expected:
            raise ValueError('Native Forge/SRG source SHA mismatch: ' + name)
    # Verify the actual first providers, so an earlier stub/other version cannot
    # silently shadow the pinned native classes. Grotesque is added per case.
    providers = {}
    for jar_path in paths:
        with zipfile.ZipFile(jar_path) as jar:
            names = set(jar.namelist())
            if 'net/mde/grotesquesteve/procedures/GrotesqueMessageProcedure.class' in names:
                raise ValueError('Do not include either Grotesque edition in the dependency classpath')
            for entry in PROVIDERS:
                if entry in names and entry not in providers:
                    expected_name = PROVIDERS[entry]
                    if jar_path.name != expected_name or sha(jar_path) != JAR_PINS[expected_name]:
                        raise ValueError('Native class provider shadowed: '+entry)
                    providers[entry] = jar_path.name
    if providers != PROVIDERS:
        raise ValueError('Native class provider shadowed or missing')
    return paths

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ['java', 'javac', 'classpath-file', 'author', 'quiet', 'out']:
        parser.add_argument('--'+option, type=Path, required=True)
    args = parser.parse_args()
    support = Path(__file__).resolve().parent
    probe = support/'NativeQuietProbe.java'
    paths = read_classpath(args.classpath_file)
    require_jar(args.author, AUTHOR)
    require_jar(args.quiet, QUIET)
    for executable in [args.java, args.javac]:
        if not executable.is_file():
            raise ValueError('Explicit Java/Javac executable missing')
    inputs = paths + [args.java, args.javac, args.classpath_file, args.author, args.quiet, probe, Path(__file__)]
    out = args.out.resolve()
    if any(p.resolve().is_relative_to(out) for p in inputs):
        raise ValueError('Output directory must not contain any immutable input')
    out.mkdir(parents=True, exist_ok=True)
    classes = Path(tempfile.mkdtemp(prefix='native-classes-', dir=out))
    classpath = os.pathsep.join(map(str, paths))
    results = {}

    def run(command: list[str], label: str) -> str:
        completed = subprocess.run(command, capture_output=True, timeout=60)
        (out/(label+'.stdout.private.txt')).write_bytes(completed.stdout)
        (out/(label+'.stderr.private.txt')).write_bytes(completed.stderr)
        text = (completed.stdout+completed.stderr).decode('utf-8', errors='replace')
        if completed.returncode:
            raise RuntimeError('Standalone check failed: '+label+'; private diagnostics are under --out')
        for expected in EXPECTED.get(label, []):
            if expected not in text:
                raise RuntimeError('Missing native observation: '+label)
        results[label] = {'exitCode':0, 'expectedObservations':EXPECTED.get(label, [])}
        return text

    java_version = run([str(args.java), '-version'], 'java-version')
    javac_version = run([str(args.javac), '-version'], 'javac-version')
    if not re.search(r'version\s+"17(?:\.|\")', java_version):
        raise ValueError('The native check requires the actual Java17 runtime')
    match = re.search(r'javac\s+(\d+)', javac_version)
    if not match or int(match.group(1)) < 17:
        raise ValueError('Javac17+ is required for --release17')
    run([str(args.javac), '--release', '17', '-encoding', 'UTF-8', '-cp', classpath, '-d', str(classes), str(probe)], 'compile-native')
    if sorted(p.relative_to(classes).as_posix() for p in classes.rglob('*.class')) != ['NativeQuietProbe.class']:
        raise RuntimeError('Unexpected native probe classes; no game/test stubs are allowed')
    for mode, jar in [('quiet', args.quiet), ('author', args.author)]:
        common = [str(args.java), '-Xverify:all', '-Dfile.encoding=UTF-8', '-cp']
        run(common+[str(classes)+os.pathsep+classpath, 'NativeQuietProbe', mode, str(jar)], mode+'-native-parsers')
        run(common+[str(classes)+os.pathsep+str(jar)+os.pathsep+classpath, 'NativeQuietProbe', 'callbacks', mode], mode+'-native-callbacks')
    report = {
        'status':'PASS', 'gameStarted':False, 'testStubClasses':0,
        'javaVersion':java_version.splitlines()[0], 'javacVersion':javac_version.splitlines()[0],
        'nativePackFormat':15, 'realForgeAndMinecraftClasses':True,
        'sourceJarsSha256':JAR_PINS,
        'author':{'sizeBytes':AUTHOR[0], 'sha256':AUTHOR[1]},
        'quiet':{'version':'1.4.2-quiet.1', 'sizeBytes':QUIET[0], 'sha256':QUIET[1]},
        'checks':results,
        'commandCheckScope':'Real Minecraft CommandFunction leading-slash validation with minimal Brigadier give/greedy-string registration; no full item-registry resolution claimed.',
        'callbackScope':'Real full author/quiet classes, exact Forge callback descriptor, null event negative control, Java17 -Xverify:all; no actual login/world/UI/audio test.',
        'advancementScope':'Static author JSON/bytecode proof: changed_dimension and impossible are AND criteria; no remaining native automatic completion after login callback RETURN. A full fresh-world check is separate.',
        'privateDiagnosticsNotForPublication':True,
    }
    (out/'native-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('PASS: native pack format, function parser and both edition callback controls; no game launched.')

if __name__ == '__main__':
    main()
