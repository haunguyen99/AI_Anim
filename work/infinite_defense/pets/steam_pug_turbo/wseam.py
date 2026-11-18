import json,os,numpy as np,math
T=os.environ["TEMP"]; W=json.load(open(T+"/pug_w.json")); md=json.load(open(T+"/pug_md.json"))
idx=list(md['vertices']); pos={v:i for i,v in enumerate(idx)}
wd={int(k):dict(v[1]) for k,v in W.items()}; P={int(k):v[0] for k,v in W.items()}
E=set();c=0
for s in md['face_sizes']:
    cs=[pos[q] for q in md['face_corners'][c:c+s]];c+=s
    for k in range(s): E.add(tuple(sorted((cs[k],cs[(k+1)%s]))))
res=[]
for a,b in E:
    ks=set(wd[a])|set(wd[b]); d=sum(abs(wd[a].get(j,0)-wd[b].get(j,0)) for j in ks)/2   # 0..1 = how different
    L=math.dist(P[a],P[b])
    res.append((d,L,a,b))
res.sort(reverse=True)
print("edges",len(E),"hard seams (diff>=0.9):",sum(1 for r in res if r[0]>=0.9),"; medium 0.5-0.9:",sum(1 for r in res if 0.5<=r[0]<0.9))
def tag(i): return max(wd[i],key=wd[i].get)[4:]
from collections import Counter
cnt=Counter()
for d,L,a,b in res:
    if d>=0.9:
        pair=tuple(sorted((tag(a),tag(b))))
        if pair[0]!=pair[1]: cnt[pair]+=1
for p,n in cnt.most_common(): print(p,n)
