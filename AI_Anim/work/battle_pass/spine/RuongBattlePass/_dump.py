import warnings, os, sys, json
warnings.filterwarnings("ignore")
from psd_tools import PSDImage
HERE=os.path.dirname(os.path.abspath(__file__))
p=PSDImage.open(os.path.join(HERE,"src","Ruong_battle_pass_anim.psd"))
out=os.path.join(HERE,"_raw"); i=0; info=[]
def walk(g,path=""):
    global i
    for l in g:
        n=path+l.name.strip()
        if l.is_group(): walk(l,n+"/"); continue
        im=l.topil()
        extra=[]
        if l.has_mask(): extra.append("mask")
        if l.has_clip_layers(): extra.append("clipbase")
        if l.clipping_layer: extra.append("CLIP")
        if getattr(l,'effects',None) and len(list(l.effects))>0: extra.append("fx:"+",".join(e.__class__.__name__ for e in l.effects))
        fn=f"{i:02d}.png"
        if im is not None: im.convert("RGBA").save(os.path.join(out,fn))
        info.append(dict(i=i,path=n,kind=l.kind,bbox=list(l.bbox),blend=l.blend_mode.name,op=round(l.opacity/255,2),vis=l.visible,extra=extra,size=list(im.size) if im else None))
        print(fn,n,l.kind,l.bbox,l.blend_mode.name,round(l.opacity/255,2),extra)
        i+=1
walk(p)
json.dump(info,open(os.path.join(out,"info.json"),"w"),ensure_ascii=False,indent=1)
p.composite().save(os.path.join(HERE,"preview","psd_composite.png"))
