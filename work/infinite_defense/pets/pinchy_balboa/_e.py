import math
M="Pet_Pinchy_Balboa"
def pts(md): Q=md['positions']; return [Q[i*3:i*3+3] for i in range(len(Q)//3)]
mdb=api.mesh_data(M); B=pts(mdb); idx=list(mdb['vertices']); pos={v:i for i,v in enumerate(idx)}
E=set(); c=0
for s in mdb['face_sizes']:
    cs=[pos.get(q,q) for q in mdb['face_corners'][c:c+s]]; c+=s
    for k in range(s): a,b=cs[k],cs[(k+1)%s]; E.add((min(a,b),max(a,b)))
for c_ in api.ls("Curve"):
    if c_.startswith("CTL_"): api.rotate(c_,0,0,0)
api.rotate("CTL_Head_M",0,0,15)
Pp=pts(api.mesh_data(M, posed=True)); api.rotate("CTL_Head_M",0,0,0)
res=sorted(((math.dist(Pp[a],Pp[b])/max(math.dist(B[a],B[b]),1e-6),a,b) for a,b in E if math.dist(B[a],B[b])>0.004),reverse=True)[:3]
api.select([M])
for r,a,b in res+sorted(((math.dist(Pp[a],Pp[b])/max(math.dist(B[a],B[b]),1e-6),a,b) for a,b in E if math.dist(B[a],B[b])>0.004))[:2]:
    print("ratio %.2f len %.3f"%(r,math.dist(B[a],B[b])))
    for v in (a,b): print("  ",[round(x,2) for x in B[v]],[(j[4:],round(x,2)) for j,x in api.vertex_weights(idx[v])])
