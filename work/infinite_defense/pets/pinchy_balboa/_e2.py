import math
M="Pet_Pinchy_Balboa"
def pts(md): Q=md['positions']; return [Q[i*3:i*3+3] for i in range(len(Q)//3)]
mdb=api.mesh_data(M); B=pts(mdb); idx=list(mdb['vertices']); pos={v:i for i,v in enumerate(idx)}
E=set(); c=0
for s in mdb['face_sizes']:
    cs=[pos.get(q,q) for q in mdb['face_corners'][c:c+s]]; c+=s
    for k in range(s): a,b=cs[k],cs[(k+1)%s]; E.add((min(a,b),max(a,b)))
api.set_frame(1); api.set_frame(6)
Pp=pts(api.mesh_data(M, posed=True))
L=[(math.dist(Pp[a],Pp[b])/math.dist(B[a],B[b]),a,b) for a,b in E if math.dist(B[a],B[b])>0.004]
api.select([M])
for r,a,b in sorted(L,reverse=True)[:3]+sorted(L)[:3]:
    print("ratio %.2f len %.3f"%(r,math.dist(B[a],B[b])))
    for v in (a,b): print("  ",[round(x,3) for x in B[v]],[(j[4:],round(x,2)) for j,x in api.vertex_weights(idx[v])])
api.set_frame(1); api.set_frame(0)
