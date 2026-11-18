import math
M="Pet_Pinchy_Balboa"
api.set_frame(1); api.set_frame(0)
def pts(md): Q=md['positions']; return [Q[i*3:i*3+3] for i in range(len(Q)//3)]
mdb=api.mesh_data(M); B=pts(mdb); Pp=pts(api.mesh_data(M, posed=True))
idx=list(mdb['vertices']); pos={v:i for i,v in enumerate(idx)}
E=set(); c=0
for s in mdb['face_sizes']:
    cs=[pos.get(q,q) for q in mdb['face_corners'][c:c+s]]; c+=s
    for k in range(s): a,b=cs[k],cs[(k+1)%s]; E.add((min(a,b),max(a,b)))
d=lambda p,q: math.dist(p,q)
res=sorted(((d(Pp[b],Pp[a])/max(d(B[b],B[a]),1e-6),a,b) for a,b in E), reverse=True)
for r,a,b in res[:12]:
    print("%.2f"%r, "bind(%.2f %.2f %.2f)"%tuple(B[a]), "len %.3f"%d(B[a],B[b]), "->", "%.3f"%d(Pp[a],Pp[b]))
print("edges >1.5:", sum(1 for r in res if r[0]>1.5), ">1.25:", sum(1 for r in res if r[0]>1.25))
# gap between stalk and glove: min distance between glove-comp verts and body arm verts posed vs bind
