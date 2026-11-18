import math
M="Pet_Pinchy_Balboa"
def pts(md): Q=md['positions']; return [Q[i*3:i*3+3] for i in range(len(Q)//3)]
mdb=api.mesh_data(M); B=pts(mdb); idx=list(mdb['vertices']); pos={v:i for i,v in enumerate(idx)}
E=set(); c=0
for s in mdb['face_sizes']:
    cs=[pos.get(q,q) for q in mdb['face_corners'][c:c+s]]; c+=s
    for k in range(s): a,b=cs[k],cs[(k+1)%s]; E.add((min(a,b),max(a,b)))
E=list(E); d=math.dist
L0=[d(B[a],B[b]) for a,b in E]
ctls=[c for c in api.ls("Curve") if c.startswith("CTL_") and c!="CTL_Main"]
api.set_frame(1); api.set_frame(0)
for c in api.ls("Curve"):
    if c.startswith("CTL_"): api.rotate(c,0,0,0); api.move(c,0,0,0)
out=[]
for c in ctls:
    for ax in "xyz":
        AMP=lambda c: 15 if 'Head' in c else 10 if 'Root' in c else 30 if 'Arm' in c else 15 if 'Glove' in c else 25 if 'Tip' in c else 20 if 'Leg' in c else 30
        for v in (AMP(c),-AMP(c)):
            r=[0,0,0]; r["xyz".index(ax)]=v; api.rotate(c,*r)
            Pp=pts(api.mesh_data(M, posed=True))
            worst=max(((d(Pp[a],Pp[b])/max(l,1e-6)),i) for i,((a,b),l) in enumerate(zip(E,L0)) if l>0.004)
            lo=min(((d(Pp[a],Pp[b])/max(l,1e-6)),i) for i,((a,b),l) in enumerate(zip(E,L0)) if l>0.004)
            api.rotate(c,0,0,0)
            out.append((worst[0],lo[0],c,ax,v,B[E[worst[1]][0]]))
out.sort(reverse=True)
for o in [o for o in out if o[0]>1.4 or o[1]<0.7][:30]: print("stretch %.2f squash %.2f %s r%s %+d at (%.2f %.2f %.2f)"%(o[0],o[1],o[2],o[3],o[4],*o[5]))
print("worst squash:", sorted(out,key=lambda o:o[1])[:3])
# weights sanity
bad=0
for i in range(len(idx)):
    w=api.vertex_weights(idx[i]) 
    s=sum(x[1] for x in w) if w and isinstance(w[0],(list,tuple)) else None
    if s is None or abs(s-1)>0.01 or len(w)>4: bad+=1
print("verts bad weights:", bad, "of", len(idx))
