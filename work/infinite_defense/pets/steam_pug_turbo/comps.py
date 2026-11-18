import json,os,numpy as np
from PIL import Image,ImageDraw
md=json.load(open(os.path.join(os.environ["TEMP"],"pug_md.json")))
P=np.array(md['positions']).reshape(-1,3); idx=list(md['vertices']); fs=md['face_sizes']; fc=md['face_corners']
print(len(P),len(idx),len(fs),len(fc),idx[:5],fc[:6])
pos={v:i for i,v in enumerate(idx)}
par=list(range(len(P)))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
i=0
for s in fs:
    c=[pos.get(q,q) for q in fc[i:i+s]]; i+=s
    for k in c[1:]: par[f(k)]=f(c[0])
roots={}
for v in range(len(P)): roots.setdefault(f(v),[]).append(v)
comps=sorted(roots.values(),key=lambda c:-len(c))
print(len(comps),"components")
for k,c in enumerate(comps):
    q=P[c]; print(k,len(c),np.round(q.min(0),2),np.round(q.max(0),2))
json.dump(comps,open(os.path.join(os.environ["TEMP"],"pug_comps.json"),"w"))
S=420; sc=S/1.15
img=Image.new("RGB",(S*3,S),"white"); d=ImageDraw.Draw(img)
cols=[(230,25,75),(60,180,75),(0,130,200),(245,130,48),(145,30,180),(70,240,240),(240,50,230),(128,128,0),(0,128,128),(170,110,40)]
def pt(a,b,o): return (o+S/2+a*sc, S-20-b*sc)
for k,c in enumerate(comps):
    col=cols[k%10]
    for v in c:
        x,y,z=P[v]
        for o,(a,b) in ((0,(z,y)),(S,(x,y)),(2*S,(x,-z+0.5))):
            X,Y=pt(a,b,o); d.ellipse((X-1.5,Y-1.5,X+1.5,Y+1.5),fill=col)
    x,y,z=P[c].mean(0); d.text(pt(z,y,0),str(k),fill=(0,0,0))
img.save("work/infinite_defense/pets/steam_pug_turbo/shots/comps.png")
