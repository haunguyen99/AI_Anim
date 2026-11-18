import json,os,sys,numpy as np
from PIL import Image,ImageDraw
T=os.environ["TEMP"]; W=json.load(open(T+"/pug_w.json")); J=json.load(open("work/infinite_defense/pets/steam_pug_turbo/joints.json"))
names=sorted({j for v in W.values() for j,_ in v[1]}); print(len(names),"joints with weight")
dom={}
for k,(p,w) in W.items():
    dom.setdefault(max(w,key=lambda t:t[1])[0],[]).append(np.array(p))
for n in names:
    q=np.array(dom.get(n,[]))
    if len(q): print("%-14s n=%3d  y %.2f..%.2f  x %.2f..%.2f  z %.2f..%.2f"%(n[4:],len(q),q[:,1].min(),q[:,1].max(),q[:,0].min(),q[:,0].max(),q[:,2].min(),q[:,2].max()))
    else: print(n,"NO dominant verts")
print("joints with no weight:",[n for n in J if "DEF_"+n not in names and n!="Muzzle_M"])
print("--- anomalies")
for k,(p,w) in W.items():
    x,y,z=p
    for j,v in w:
        s=j[-1]; 
        if s in "LR" and v>0.05 and ((s=="L")!=(x>0)) and abs(x)>0.04: print("side-cross",j,v,np.round(p,2))
        jp=np.array(J[j[4:]][0]); d=np.linalg.norm(jp-np.array(p))
        if v>0.3 and d>0.45: print("far",j,v,round(d,2),np.round(p,2))
    if len(w)>4: print(">4",k)
    if abs(sum(v for _,v in w)-1)>0.02: print("sum",k,w)
mixed=[(k,w) for k,(p,w) in W.items() if len(w)>=3]
print("verts with >=3 influences:",len(mixed),"of",len(W))
# colour render
cols={n:tuple(int(c) for c in np.array(plt)) for n,plt in []}
import colorsys
cm={n:tuple(int(255*c) for c in colorsys.hsv_to_rgb((i*0.618)%1,0.8,0.95)) for i,n in enumerate(names)}
def view(proj,S=520,sc=380):
    img=Image.new("RGB",(S,S),(30,35,40)); d=ImageDraw.Draw(img)
    pts=[]
    for k,(p,w) in W.items():
        a,b,z=proj(p); col=np.zeros(3)
        for j,v in w: col+=v*np.array(cm[j])
        pts.append((z,S/2+a*sc,S-30-b*sc,tuple(int(c) for c in col)))
    pts.sort()
    for z,X,Y,c in pts: d.ellipse((X-4,Y-4,X+4,Y+4),fill=c)
    return img
vs=[lambda p:(p[2],p[1],-p[0]),lambda p:(-p[0],p[1],-p[2]),lambda p:(-p[0],-p[2]+0.5,p[1])]
ims=[view(v) for v in vs]; sh=Image.new("RGB",(520*3,520)); [sh.paste(im,(i*520,0)) for i,im in enumerate(ims)]
d=ImageDraw.Draw(sh)
for i,n in enumerate(names): d.rectangle((6,6+i*13,16,16+i*13),fill=cm[n]); d.text((20,5+i*13),n[4:],fill=(255,255,255))
sh.save("work/infinite_defense/pets/steam_pug_turbo/shots/weights.png")
