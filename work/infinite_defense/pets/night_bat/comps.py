M="Pet_Night_Bat"
md = api.mesh_data(M); P = md['positions']; P=[P[i*3:i*3+3] for i in range(len(P)//3)]
idx=list(md['vertices']); par=list(range(len(idx)))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
pos={v:i for i,v in enumerate(idx)}; c=0
for s in md['face_sizes']:
    cs=md['face_corners'][c:c+s]; c+=s
    for q in cs[1:]: par[f(pos.get(q,q))]=f(pos.get(cs[0],cs[0]))
comp={}
for i in range(len(idx)): comp.setdefault(f(i),[]).append(i)
print(len(idx), len(comp))
for vs in sorted(comp.values(), key=len, reverse=True):
    xs=[P[i][0] for i in vs]; ys=[P[i][1] for i in vs]; zs=[P[i][2] for i in vs]
    print(len(vs), "x %.3f %.3f y %.3f %.3f z %.3f %.3f"%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)))
