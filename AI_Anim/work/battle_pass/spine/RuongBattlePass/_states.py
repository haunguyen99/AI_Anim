import warnings, os
warnings.filterwarnings("ignore")
from psd_tools import PSDImage
from PIL import Image
p=PSDImage.open("src/Ruong_battle_pass_anim.psd")
top={l.name.strip():l for l in p}
print(list(top))
def show(names):
    for k,l in top.items():
        if k!="rương": l.visible = k in names
    return p.composite(force=True)
ims=[]
for nm,s in [("none",[]),("closed",["cửa đóng","Layer 24"]),("closed+ring",["cửa đóng","Layer 24","vong tron"]),("half",["cửa mở vừa"]),("open",["cửa mở hẳn"])]:
    im=show(s); im.save(f"preview/state_{nm}.png"); ims.append(im.convert("RGBA"))
W,H=ims[0].size
sheet=Image.new("RGBA",(W*3//2*1, H*2//2*1),(90,90,110,255))
sheet=Image.new("RGBA",(W*3//2,H*2//2*2//1),(90,90,110,255))
sheet=Image.new("RGBA",(int(W*0.5)*5,int(H*0.5)),(90,90,110,255))
for k,im in enumerate(ims):
    t=im.resize((W//2,H//2)); sheet.paste(t,(k*(W//2),0),t)
sheet.save("preview/states.png"); print(sheet.size)
