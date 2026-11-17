import math
from collections import defaultdict
OB="Pet_Chrono_Ouroboros"
JI={r['name']:r for r in api.joint_info()}
md=api.mesh_data(OB); idx=list(md['vertices']); P=md['positions']; P=[P[i*3:i*3+3] for i in range(len(idx))]
def adj(a,b):
    return JI[a]['parent']==b or JI[b]['parent']==a or a==b
dom=defaultdict(list); bad=[]; far=[]; nn=0
for k,v in enumerate(idx):
    w=api.vertex_weights(v); w=sorted(w,key=lambda t:-t[1]); nn=max(nn,len(w))
    dom[w[0][0]].append(k)
    for i in range(len(w)):
        for j in range(i+1,len(w)):
            if not adj(w[i][0],w[j][0]) and w[i][1]>.1 and w[j][1]>.1: bad.append((k,w[i][0],w[j][0]))
    d=math.dist(P[k],JI[w[0][0]]['world'])
    if d>0.45: far.append((k,w[0][0],round(d,2)))
print("max influences",nn)
for j in JI:
    if j=="DEF_Muzzle_M": continue
    v=dom.get(j,[])
    if not v: print("%-16s 0 dinh (KHONG ANH HUONG GI)"%j); continue
    xs=[P[k][0] for k in v]; ys=[P[k][1] for k in v]; zs=[P[k][2] for k in v]
    print("%-16s %3d dinh  x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f"%(j,len(v),min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)))
print("cap xuong khong ke nhau dung chung dinh:",len(bad)); 
c=defaultdict(int)
for k,a,b in bad: c[(a,b)]+=1
for (a,b),n in sorted(c.items(),key=lambda t:-t[1])[:12]: print("  ",a,b,n)
print("dinh xa xuong chinh >0.45:",len(far),far[:8])
