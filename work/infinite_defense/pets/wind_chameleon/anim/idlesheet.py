import subprocess,sys,os,tempfile
from PIL import Image
W="work/infinite_defense/pets/wind_chameleon/"
ims=[]; tmp=tempfile.gettempdir()
for f in (0,12,24,36):
    code=open(W+"anim/test_idle.py").read().replace("FRAME", str(f))
    code="api.set_frame(1)\n"+code+"\napi.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\napi.look_through('side'); api.set_camera_ortho('side', True); api.set_attr('side.ow', 1.7); api.move('side', 100, 0.45, 0.05)\n"
    open(W+"anim/_ti.py","w").write(code)
    subprocess.run([sys.executable,"-I","tools/frolvy_port.py","9884",W+"anim/_ti.py"],capture_output=True)
    subprocess.run([sys.executable,"-I","tools/frolvy_shot.py","9884",tmp+"/ii.png"],capture_output=True)
    ims.append(Image.open(tmp+"/ii.png").convert("RGB"))
w,h=ims[0].size; s=Image.new("RGB",(w*2,h*2))
for i,im in enumerate(ims): s.paste(im,((i%2)*w,(i//2)*h))
s.save(W+"shots/idle.png")
