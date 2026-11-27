import json, numpy as np
from PIL import Image
lay=json.load(open("layers.json"))["layers"]; W,H=json.load(open("layers.json"))["canvas"]
def cv(n):
    im=np.asarray(Image.open(f"images/{n}.png").convert("RGBA"),np.float32)/255; x0,y0,x1,y1=lay[n]["bbox"]
    c=np.zeros((H,W,4),np.float32); c[y0:y1,x0:x1]=im; return c
def over(dst,src,mask=None):
    a=src[...,3:4]*(1 if mask is None else mask[...,None]); 
    out=dst.copy(); oa=a+dst[...,3:4]*(1-a)
    out[...,:3]=np.where(oa>0,(src[...,:3]*a+dst[...,:3]*dst[...,3:4]*(1-a))/np.maximum(oa,1e-6),0); out[...,3:4]=oa; return out
cavA=cv("cavity")[...,3]
order=["chest_body","cavity","in_stack5","in_stack4","in_c1","in_c2","in_c3","in_c4","in_tilt","in_stack3","fg_stack3","fg_tilt1","fg_c1","fg_c2","fg_c3","fg_tilt2","fg_tilt3"]
clipped={"in_stack5","in_stack4","in_c1","in_c2","in_c3","in_c4"}
states={"none":[],"closed":["door_c","dial"],"ring":["door_c","dial","ring"],"half":["door_h","bolt_h1","bolt_h2","bolt_h3"],"open":["door_o","bolt_o1","bolt_o2","bolt_o3"]}
for st,extra in states.items():
    c=np.zeros((H,W,4),np.float32)
    for n in order+extra: c=over(c,cv(n),cavA if n in clipped else None)
    ref=np.asarray(Image.open(f"preview/state_{st if st!='ring' else 'closed+ring'}.png").convert("RGBA"),np.float32)/255
    # so trên nền trắng
    f=lambda x:(x[...,:3]*x[...,3:4]+(1-x[...,3:4]))
    d=np.abs(f(c)-f(ref))*255
    print(st,"mean",round(float(d.mean()),3),"max",round(float(d.max()),1),"px>8:",int((d.max(2)>8).sum()))
    Image.fromarray((np.clip(f(c),0,1)*255).astype(np.uint8)).save(f"preview/static_{st}.png")
