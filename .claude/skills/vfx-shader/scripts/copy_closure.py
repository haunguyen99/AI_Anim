"""Copy a Unity prefab + everything it references (guid closure) from one project to another, keeping GUIDs.
usage: copy_closure.py <src Assets dir> <dst dir> <prefab rel path> [<prefab rel path> ...]
Skips .cs scripts and shader-graph/URP-only shaders (reported)."""
import sys,re,os,shutil
src,dst,*roots=sys.argv[1:]
guid2path={}
for dp,_,fs in os.walk(src):
    for f in fs:
        if f.endswith('.meta'):
            try:
                g=re.search(r'guid: (\w{32})',open(os.path.join(dp,f),encoding='utf8',errors='ignore').read())
                if g: guid2path[g.group(1)]=os.path.join(dp,f)[:-5]
            except: pass
seen=set(); todo=[os.path.join(src,r) for r in roots]; skipped=[]
TEXT=('.prefab','.mat','.shader','.cginc','.hlsl','.controller','.anim','.asset','.physicMaterial')
while todo:
    p=todo.pop()
    if p in seen or not os.path.exists(p): continue
    seen.add(p)
    if p.endswith(TEXT):
        t=open(p,encoding='utf8',errors='ignore').read()
        if p.endswith('.shader') and ('UniversalPipeline' in t or 'HLSLPROGRAM' in t and 'URP' in t): skipped.append(p)
        for g in set(re.findall(r'guid: (\w{32})',t)):
            q=guid2path.get(g)
            if q and not q.endswith('.cs'): todo.append(q)
        if p.endswith('.shader'):
            for inc in re.findall(r'#include "([^"]+\.cginc)"',t):
                c=os.path.join(os.path.dirname(p),inc)
                if os.path.exists(c): todo.append(c)
for p in sorted(seen):
    if p in skipped: print('SKIP(URP)',p); continue
    rel=os.path.relpath(p,src); o=os.path.join(dst,rel); os.makedirs(os.path.dirname(o),exist_ok=True)
    shutil.copy2(p,o)
    if os.path.exists(p+'.meta'): shutil.copy2(p+'.meta',o+'.meta')
    print(rel)
print(len(seen),'files')
