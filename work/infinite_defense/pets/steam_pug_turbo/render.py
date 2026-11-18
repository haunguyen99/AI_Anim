"""render.py out.png [joints.json]  - tu ve mesh tu du lieu (view: side/front/top/3q), mau theo manh."""
import json,os,sys,numpy as np
from PIL import Image,ImageDraw
T=os.environ["TEMP"]
md=json.load(open(os.path.join(T,"pug_md.json"))); comps=json.load(open(os.path.join(T,"pug_comps.json")))
P=np.array(md['positions']).reshape(-1,3); idx=list(md['vertices']); pos={v:i for i,v in enumerate(idx)}
fs=md['face_sizes']; fc=[pos.get(q,q) for q in md['face_corners']]
cid=np.zeros(len(P),int)
for k,c in enumerate(comps): cid[c]=k
cols=[(200,200,200),(60,180,75),(0,130,200),(245,130,48),(145,30,180),(70,200,200),(240,50,230),(180,180,0),(0,128,128),(170,110,40)]
def render(proj,S=520,sc=380,extra=None):
    img=Image.new("RGB",(S,S),(40,50,60)); d=ImageDraw.Draw(img)
    polys=[];i=0
    for s in fs:
        c=fc[i:i+s];i+=s
        q=P[c]; a,b,z=proj(q); polys.append((z.mean(),[(S/2+x*sc,S-30-y*sc) for x,y in zip(a,b)],c[0]))
    polys.sort(key=lambda t:t[0])
    for z,pl,v in polys:
        col=cols[cid[v]%10]; sh=0.55+0.45*(1-(z-polys[0][0])/(polys[-1][0]-polys[0][0]+1e-9))
        d.polygon(pl,fill=tuple(int(u*sh) for u in col),outline=(30,30,30))
    if extra: extra(d,proj,S,sc)
    return img
views={"side":lambda q:(q[:,2],q[:,1],-q[:,0]),"front":lambda q:(-q[:,0],q[:,1],-q[:,2]),"top":lambda q:(-q[:,0],-q[:,2]+0.5,q[:,1]),
 "back":lambda q:(q[:,0],q[:,1],q[:,2])}
def c3q(q):
    a=0.6; x=q[:,0]*np.cos(a)+q[:,2]*np.sin(a); z=-q[:,0]*np.sin(a)+q[:,2]*np.cos(a); return (x,q[:,1],-z)
views["3q"]=c3q
if __name__=="__main__":
    out=sys.argv[1]; J=json.load(open(sys.argv[2])) if len(sys.argv)>2 else None
    def extra(d,proj,S,sc):
        if not J: return
        for n,(p,par) in J.items():
            a,b,_=proj(np.array([p]));X,Y=S/2+a[0]*sc,S-30-b[0]*sc
            d.ellipse((X-4,Y-4,X+4,Y+4),fill=(255,255,0),outline=(0,0,0)); d.text((X+5,Y-5),n,fill=(255,255,255))
            if par:
                a2,b2,_=proj(np.array([J[par][0]]));d.line((X,Y,S/2+a2[0]*sc,S-30-b2[0]*sc),fill=(255,255,0))
    vs=sys.argv[3].split(",") if len(sys.argv)>3 else ["side","front","top","3q"]
    ims=[render(views[v],extra=extra) for v in vs]; S=ims[0].size[0]
    sheet=Image.new("RGB",(S*len(ims),S)); [sheet.paste(im,(i*S,0)) for i,im in enumerate(ims)]; sheet.save(out)
