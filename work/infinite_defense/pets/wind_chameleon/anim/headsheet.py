import subprocess,sys,tempfile
from PIL import Image
W="work/infinite_defense/pets/wind_chameleon/"; tmp=tempfile.gettempdir(); ims=[]
for cam,f in [("side",0),("side",13),("side",16),("side",24)]:
    code="api.set_frame(1); api.set_frame(%d)\napi.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\napi.look_through('%s'); api.set_camera_ortho('%s', True); api.set_attr('%s.ow', 0.9)\napi.move('%s', %s)\n"%(f,cam,cam,cam,cam,"100, 0.5, 0.3" if cam=="side" else "0, 0.5, 100")
    open(tmp+"/_hh.py","w").write(code)
    subprocess.run([sys.executable,"-I","tools/frolvy_port.py","9884",tmp+"/_hh.py"],capture_output=True)
    subprocess.run([sys.executable,"-I","tools/frolvy_shot.py","9884",tmp+"/hh.png"],capture_output=True)
    ims.append(Image.open(tmp+"/hh.png").convert("RGB"))
w,h=ims[0].size; s=Image.new("RGB",(w*2,h*2))
for i,im in enumerate(ims): s.paste(im,((i%2)*w,(i//2)*h))
s.save(W+"shots/head.png")
