"""Offline exact-edition preparation. No patcher/helper is loaded by Minecraft."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import tempfile
import tomllib
import zipfile

AUTHOR_SHA = '7edde5b1506a69a725412769525ba16122b1dd4c38e35f3edc5c015eef3a6f63'
AUTHOR_SIZE = 22223025
VERSION = '1.4.2-quiet.1'
DESC = '(Lnet/minecraftforge/event/entity/player/PlayerEvent$PlayerLoggedInEvent;)V'
PREFIX = 'net/mde/grotesquesteve/procedures/'
TARGETS = {
    PREFIX+'GrotesqueMessageProcedure.class': ('312ee6123303d6750fb181f851a93595494c79a3b3423c6298b9baa3f482c47e', '6b4d579daad001a6f9a960d9ee31986855266a50dee9d201d4af023ae2b34f75'),
    PREFIX+'AdvancementtriggerProcedure.class': ('458d58fe861f847c9101d418218bffb222bcb12ea15150b0269ba60e07001505', '94ae659c0f7569b80209d11414f3519aa9b1f17d97825b29b12fb1c22f5604c8'),
}
MANUAL = 'data/minecraft/functions/manualgiver.mcfunction'
META = 'META-INF/mods.toml'
CHANGED = set(TARGETS) | {MANUAL, META}
# Code attribute: max_stack=0, max_locals=1, code_length=1, RETURN,
# exception_table_length=0, attributes_count=0. No branch or StackMap is needed.
QUIET_CODE = struct.pack('>HHI', 0, 1, 1) + b'\xb1' + b'\x00\x00\x00\x00'

def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()

class ClassFile:
    def __init__(self, blob: bytes):
        self.blob = blob
        self.pos = 0
        self.utf = {}
        if self.take(4) != b'\xca\xfe\xba\xbe': raise ValueError('Not a class file')
        if self.u2() != 0 or self.u2() != 61: raise ValueError('Unexpected Java class version')
        count = self.u2()
        index = 1
        while index < count:
            tag = self.take(1)[0]
            if tag == 1:
                # Names/descriptors are ASCII. Keep arbitrary modified-UTF8 values
                # opaque unless used as an attribute/name below.
                value = self.take(self.u2())
                self.utf[index] = value
            elif tag in (3, 4, 9, 10, 11, 12, 17, 18): self.take(4)
            elif tag in (5, 6): self.take(8); index += 1
            elif tag in (7, 8, 16, 19, 20): self.take(2)
            elif tag == 15: self.take(3)
            else: raise ValueError('Unsupported constant-pool tag')
            index += 1
        self.take(6)
        self.take(self.u2() * 2)
        self.table()  # fields
        self.methods = self.table()
        self.attributes()
        if self.pos != len(blob): raise ValueError('Trailing class bytes')

    def take(self, count: int) -> bytes:
        if count < 0 or self.pos + count > len(self.blob): raise ValueError('Truncated class')
        result = self.blob[self.pos:self.pos+count]
        self.pos += count
        return result

    def u2(self) -> int: return int.from_bytes(self.take(2), 'big')
    def u4(self) -> int: return int.from_bytes(self.take(4), 'big')

    def attributes(self) -> list[dict]:
        rows = []
        for _ in range(self.u2()):
            name = self.utf[self.u2()].decode('ascii')
            length_position = self.pos
            size = self.u4()
            start = self.pos
            value = self.take(size)
            rows.append({'name':name, 'lengthPosition':length_position, 'start':start, 'end':self.pos, 'value':value})
        return rows

    def table(self) -> list[dict]:
        rows = []
        for _ in range(self.u2()):
            start = self.pos
            access = self.u2()
            name = self.utf[self.u2()].decode('ascii')
            descriptor = self.utf[self.u2()].decode('ascii')
            attributes = self.attributes()
            rows.append({'access':access, 'name':name, 'descriptor':descriptor, 'attributes':attributes, 'raw':self.blob[start:self.pos]})
        return rows

def callback(cf: ClassFile) -> dict:
    found = [m for m in cf.methods if m['name']=='onPlayerLoggedIn' and m['descriptor']==DESC]
    if len(found)!=1 or found[0]['access']!=9: raise ValueError('Callback binding changed')
    return found[0]

def code(method: dict) -> dict:
    found = [a for a in method['attributes'] if a['name']=='Code']
    if len(found)!=1: raise ValueError('Unexpected Code attribute count')
    return found[0]

def patch_class(blob: bytes, entry: str) -> bytes:
    class_sha, method_sha = TARGETS[entry]
    if digest(blob)!=class_sha: raise ValueError('Exact source class SHA mismatch')
    before = ClassFile(blob)
    method = callback(before)
    if digest(method['raw'])!=method_sha: raise ValueError('Exact source callback SHA mismatch')
    if not any(a['name']=='RuntimeVisibleAnnotations' for a in method['attributes']): raise ValueError('Forge annotation missing')
    attr = code(method)
    result = blob[:attr['lengthPosition']] + struct.pack('>I',len(QUIET_CODE)) + QUIET_CODE + blob[attr['end']:]
    after = ClassFile(result)
    changed = callback(after)
    if code(changed)['value']!=QUIET_CODE: raise ValueError('Callback is not exactly RETURN')
    if len(before.methods)!=len(after.methods): raise ValueError('Method table changed')
    for old,new in zip(before.methods,after.methods):
        if old is method:
            if [(a['name'],a['value']) for a in old['attributes'] if a['name']!='Code'] != [(a['name'],a['value']) for a in new['attributes'] if a['name']!='Code']:
                raise ValueError('Callback annotations/other attributes changed')
        elif old['raw']!=new['raw']: raise ValueError('Unrelated method bytes changed')
    # Outside exactly this original Code length+payload, every class byte is kept.
    if result[:attr['lengthPosition']]!=blob[:attr['lengthPosition']] or result[attr['lengthPosition']+4+len(QUIET_CODE):]!=blob[attr['end']:]:
        raise ValueError('Outside-Code bytes changed')
    return result

def read_author(path: Path) -> dict[str,bytes]:
    if not path.is_file() or path.is_symlink() or path.stat().st_size!=AUTHOR_SIZE: raise ValueError('Only exact user-provided Grotesque1.4.2 is supported')
    raw = path.read_bytes()
    if digest(raw)!=AUTHOR_SHA: raise ValueError('Exact user-provided JAR SHA mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as jar:
        names = jar.namelist()
        if len(names)!=len(set(names)): raise ValueError('Duplicate ZIP entries')
        if len(names)!=2499: raise ValueError('Author entry inventory changed')
        if any(n.startswith('/') or '\\' in n or '..' in Path(n).parts for n in names): raise ValueError('Unsafe ZIP entry')
        if any(n.startswith('META-INF/') and n.upper().endswith(('.SF','.RSA','.DSA','.EC')) for n in names): raise ValueError('Signed source cannot be edited')
        return {name:jar.read(name) for name in names}

def build(source: Path, output: Path) -> dict:
    if source.resolve()==output.resolve() or output.is_symlink(): raise ValueError('Separate regular derivative output required')
    before = read_author(source)
    meta = tomllib.loads(before[META].decode('utf-8'))
    if len(meta.get('mods',[]))!=1 or meta['mods'][0].get('modId')!='grotesque_steve' or meta['mods'][0].get('version')!='1.4.2': raise ValueError('Native metadata binding changed')
    if json.loads(before['pack.mcmeta'])['pack']['pack_format']!=15: raise ValueError('Native1.20.1 pack format must remain15')
    if before[MANUAL]!=b'/give @p grotesque_steve:manualbook': raise ValueError('Manual function source changed')
    if before[META].count(b'version="1.4.2"')!=1: raise ValueError('Native version field ambiguous')
    after = dict(before)
    for entry in TARGETS: after[entry] = patch_class(before[entry],entry)
    after[MANUAL] = before[MANUAL][1:]
    after[META] = before[META].replace(b'version="1.4.2"',('version="'+VERSION+'"').encode())
    changed = {name for name in before if before[name]!=after[name]}
    if changed!=CHANGED or set(after)!=set(before): raise ValueError('Changed-entry whitelist mismatch')
    # STORED avoids zlib/platform-dependent recompression and preserves all
    # non-edited entry payloads, including audio, textures, animations and libs.
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,temp_name = tempfile.mkstemp(prefix='.grotesque-quiet-',suffix='.jar.tmp',dir=output.parent)
    try:
        with os.fdopen(fd,'wb') as stream:
            with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_STORED) as jar:
                for name,value in sorted(after.items()):
                    info = zipfile.ZipInfo(name,(2026,10,30,0,0,0))
                    info.create_system = 0
                    info.compress_type = zipfile.ZIP_STORED
                    info.external_attr = 0o100644 << 16
                    jar.writestr(info,value)
        temp = Path(temp_name)
        with zipfile.ZipFile(temp) as jar:
            if jar.testzip() is not None or set(jar.namelist())!=set(before): raise ValueError('Output ZIP validation failed')
            if any(jar.read(n)!=v for n,v in after.items()): raise ValueError('Output entry payload changed')
        raw = temp.read_bytes()
        report = {'sourceSha256':AUTHOR_SHA,'sourceSizeBytes':AUTHOR_SIZE,'version':VERSION,'outputSha256':digest(raw),'outputSizeBytes':len(raw),
            'entryCount':len(after),'changedEntries':sorted(changed),'unchangedEntries':len(before)-len(changed),'onlyTwoCodeAttributesChanged':True,
            'sourceOnlyToolNotLoadedByGame':True,'newClassesOrEntries':[],'nativePackFormat':15,
            'entryPins':{n:{'beforeSha256':digest(before[n]),'afterSha256':digest(after[n])} for n in sorted(changed)}}
        temp.replace(output)
        return report
    finally:
        Path(temp_name).unlink(missing_ok=True)

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cache',type=Path,help='Accepted for shared restore interface; no download/build cache needed.')
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    if args.report:
        if args.report.is_symlink() or any(args.report.resolve()==p.resolve() or
                (args.report.exists() and p.exists() and os.path.samefile(args.report,p))
                for p in [args.input,args.output]):
            raise ValueError('Report must not alias author source or derivative output')
    result=build(args.input,args.output)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
