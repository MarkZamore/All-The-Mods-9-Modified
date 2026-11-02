from pathlib import Path
import argparse, hashlib, struct, zipfile, json

ROOT = Path(__file__).resolve().parent


def parse(data):
    p = 8
    def u1():
        nonlocal p
        v=data[p];p+=1;return v
    def u2():
        nonlocal p
        v=struct.unpack_from('>H',data,p)[0];p+=2;return v
    def u4():
        nonlocal p
        v=struct.unpack_from('>I',data,p)[0];p+=4;return v
    n=u2(); cp=[None]*n;i=1
    while i<n:
        t=u1()
        if t==1:
            length=u2();cp[i]=(t,data[p:p+length].decode('utf-8','replace'));p+=length
        elif t in (3,4):p+=4
        elif t in (5,6):p+=8;i+=1
        elif t in (7,8,16,19,20):cp[i]=(t,u2())
        elif t in (9,10,11,12,17,18):cp[i]=(t,u2(),u2())
        elif t==15:cp[i]=(t,u1(),u2())
        else:raise ValueError(t)
        i+=1
    def utf(i): return cp[i][1]
    def cls(i): return utf(cp[i][1]) if i else None
    access=u2();this=cls(u2());sup=cls(u2());interfaces=[cls(u2()) for _ in range(u2())]
    def members():
        nonlocal p
        out={}
        for _ in range(u2()):
            flags=u2();name=utf(u2());desc=utf(u2());out[(name,desc)]=flags
            for __ in range(u2()):
                u2();length=u4();p+=length
        return out
    fields=members();methods=members();refs=[]
    for row in cp:
        if row and row[0] in (9,10,11):
            nat=cp[row[2]];refs.append((row[0],cls(row[1]),utf(nat[1]),utf(nat[2])))
    return {'name':this,'access':access,'super':sup,'interfaces':interfaces,'fields':fields,'methods':methods,'refs':refs,'classRefs':[cls(i) for i,row in enumerate(cp) if row and row[0]==7]}

def classes(path):
    with zipfile.ZipFile(path) as jar:
        return {value['name']:value for n in jar.namelist() if n.endswith('.class') for value in [parse(jar.read(n))]}

def resolve(table, owner, kind, name, desc, seen=None):
    seen=set() if seen is None else seen
    if owner in seen:return None
    seen.add(owner);value=table.get(owner)
    if value is None:return None
    if (name,desc) in value[kind]:return owner,value[kind][(name,desc)]
    for parent in [value['super'],*value['interfaces']]:
        if parent and (found:=resolve(table,parent,kind,name,desc,seen)):return found
    return None

def main():
    parser=argparse.ArgumentParser(description='Pinned mc1201 constant-pool API reference check; no game or ability execution.')
    for name in ('old-library','new-library','type95','shooting-star','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    pins={'old_library':'579a02a11efaf5d16b9704e0597e82b6c6c68c87c5c645953fe4a197fff71960',
          'new_library':'906cbd286f6c491898620eed26aea1337e21bb68b6345c211ba083e9c646c5e6',
          'type95':'8f0aca5fb5ab9772028e5839e89ba6861c2ef7eb781e517162cb6054ed07c439',
          'shooting_star':'9a547738e3971b79f0e501fb3311e4abb74e48547acab6c921db9c8c3b1dd4f5'}
    for name,digest in pins.items():
        if hashlib.sha256(getattr(args,name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Wrong pinned input: '+name)
    libraries={label:classes(path) for label,path in [('old',args.old_library),('new',args.new_library)]}
    consumers={label:classes(path) for label,path in [('type95',args.type95),('shootingStar151',args.shooting_star)]}
    result={}
    for label,table in consumers.items():
        refs={ref for name,value in table.items() if '/mc1201/' in name for ref in value['refs'] if ref[1].startswith('cyou/rimuru/rimulib/')}
        checks=[]
        for tag,owner,name,desc in sorted(refs):
            kind='fields' if tag==9 else 'methods'
            old=resolve(libraries['old'],owner,kind,name,desc);new=resolve(libraries['new'],owner,kind,name,desc)
            checks.append({'kind':kind,'owner':owner,'name':name,'descriptor':desc,'resolvedInOld':old is not None,'resolvedInNew':new is not None,'oldFlags':None if old is None else old[1],'newFlags':None if new is None else new[1]})
        types={owner for name,value in table.items() if '/mc1201/' in name for owner in value['classRefs'] if owner.startswith('cyou/rimuru/rimulib/')}
        changed=[row for row in checks if row['resolvedInOld'] and row['resolvedInNew'] and (bool(row['oldFlags']&8)!=bool(row['newFlags']&8) or (row['oldFlags']&1 and not row['newFlags']&1))]
        changed_types=[{'owner':owner,'oldFlags':libraries['old'][owner]['access'],'newFlags':libraries['new'][owner]['access']} for owner in sorted(types) if owner in libraries['old'] and owner in libraries['new'] and ((libraries['old'][owner]['access']&1 and not libraries['new'][owner]['access']&1) or bool(libraries['old'][owner]['access']&512)!=bool(libraries['new'][owner]['access']&512))]
        result[label]={'uniqueMemberRefs':len(checks),'referencedLibraryClasses':len(types),'missingClassesInNew':sorted(types-set(libraries['new'])),'changedClassKindOrReducedPublicVisibility':changed_types,'missingInNew':[row for row in checks if not row['resolvedInNew']],'changedStaticOrReducedPublicVisibility':changed,'checks':checks}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({label:{k:v for k,v in r.items() if k!='checks'} for label,r in result.items()},indent=2))

if __name__=='__main__':main()
