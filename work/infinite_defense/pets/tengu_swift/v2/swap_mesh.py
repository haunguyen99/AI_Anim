import math, json
from collections import defaultdict
FBX='/home/ngocvb/Projects/endless-kicker/Assets/Kho/Skin/mesh/Pet_new/mesh/Pet_tengu_swift.fbx'
OLD='Pet_tengu_swift'
D=json.load(open('/tmp/tg/oldw.json')); P0=D['P']; ow=D['W']
op=[P0[i*3:i*3+3] for i in range(len(ow))]
used_j=sorted({j for w in ow for j,_ in w}); print('used',len(used_j))
for _c in api.ls("Curve"):
    if _c.startswith("CTL_") and _c!="CTL_Main": api.rotate(_c,0,0,0); api.move(_c,0,0,0)
api.set_frame(3); api.set_frame(0)
cell=0.02; grid=defaultdict(list)
for i,p in enumerate(op): grid[(int(p[0]//cell),int(p[1]//cell),int(p[2]//cell))].append(i)
def nn(q):
    c=(int(q[0]//cell),int(q[1]//cell),int(q[2]//cell)); best=(9,None)
    for r in (1,2,4):
        for dx in range(-r,r+1):
            for dy in range(-r,r+1):
                for dz in range(-r,r+1):
                    for i in grid.get((c[0]+dx,c[1]+dy,c[2]+dz),[]):
                        d=math.dist(q,op[i])
                        if d<best[0]: best=(d,i)
        if best[1] is not None and best[0]<r*cell: break
    return best
before=set(api.ls())
api.import_file(FBX,'add')
new=[x for x in api.ls() if x not in before and api.node_type(x)=='Object']
body=[n for n in new if 'Vu_khi' not in n][0]
for n in new:
    if n!=body: api.delete_node(n)
print('delete old',api.delete_node(OLD)); print('rename',api.rename(body,OLD))
api.select([OLD]); print('bind',api.bind_skin(used_j))
nm=api.mesh_data(OLD); NV=list(nm['vertices']); NP=nm['positions']
ds=[nn(NP[i*3:i*3+3]) for i in range(len(NV))]
far=[i for i,(d,_) in enumerate(ds) if d>1e-4]
print('verts',len(NV),'moi/khong trung',len(far),'max d',round(max(d for d,_ in ds),4))
rows=[]
for k in range(len(NV)):
    w=[(j,v) for j,v in ow[ds[k][1]] if v>1e-6]; s=sum(v for _,v in w); rows.append([(j,v/s) for j,v in w])
api.select([OLD]); print('weights',api.set_skin_weights(NV,rows))
api.set_frame(1); api.set_frame(0)
print(api.ls('Object'))
print(api.vertex_weights(NV[0]))
