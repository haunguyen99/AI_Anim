import math
M="Pet_Pinchy_Balboa"
def pts(md): Q=md['positions']; return [Q[i*3:i*3+3] for i in range(len(Q)//3)]
mdb=api.mesh_data(M); B=pts(mdb); idx=list(mdb['vertices']); pos={v:i for i,v in enumerate(idx)}
E=set(); c=0
for s in mdb['face_sizes']:
    cs=[pos.get(q,q) for q in mdb['face_corners'][c:c+s]]; c+=s
    for k in range(s): a,b=cs[k],cs[(k+1)%s]; E.add((min(a,b),max(a,b)))
E=[(a,b,math.dist(B[a],B[b])) for a,b in E if math.dist(B[a],B[b])>0.004]
N=NF
worst=[]
for f in range(0,N+1,2):
    api.set_frame(1); api.set_frame(f); Pp=pts(api.mesh_data(M, posed=True))
    r=max((math.dist(Pp[a],Pp[b])/l,a,b) for a,b,l in E); q=min((math.dist(Pp[a],Pp[b])/l,a,b) for a,b,l in E)
    worst.append((f,round(r[0],2),[round(x,2) for x in B[r[1]]],round(q[0],2),[round(x,2) for x in B[q[1]]]))
print("max stretch", max(w[1] for w in worst), "min squash", min(w[3] for w in worst))
for w in sorted(worst,key=lambda w:-w[1])[:4]: print(w)
api.set_frame(1); api.set_frame(0)
