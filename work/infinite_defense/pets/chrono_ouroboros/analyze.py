md = api.mesh_data("Pet_Chrono_Ouroboros"); idx=list(md['vertices']); P=md['positions']
P=[P[i*3:i*3+3] for i in range(len(idx))]
pos={v:i for i,v in enumerate(idx)}; par=list(range(len(idx)))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
c=0
for sz in md['face_sizes']:
    cs=[pos.get(q,q) for q in md['face_corners'][c:c+sz]]; c+=sz
    for k in range(1,sz): par[f(cs[k])]=f(cs[0])
from collections import defaultdict
g=defaultdict(list)
for i in range(len(idx)): g[f(i)].append(i)
print("components",len(g), "faces", len(md['face_sizes']))
for k,v in sorted(g.items(), key=lambda t:-len(t[1])):
    xs=[P[i][0] for i in v]; ys=[P[i][1] for i in v]; zs=[P[i][2] for i in v]
    print(len(v), "x %.2f %.2f y %.2f %.2f z %.2f %.2f"%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)))
