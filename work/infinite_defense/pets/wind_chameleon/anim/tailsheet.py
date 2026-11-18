import subprocess,sys,tempfile
from PIL import Image
W="work/infinite_defense/pets/wind_chameleon/"; tmp=tempfile.gettempdir(); ims=[]
for f in [int(x) for x in sys.argv[2].split(",")]:
    code=open(W+"anim/test_idle.py").read().replace("FRAME", str(f))
    code="api.set_frame(1)\n"+code+"\napi.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\napi.look_through('side'); api.set_camera_ortho('side', True); api.set_attr('side.ow', 0.9); api.move('side', 100, 0.5, -0.22)\n"
    open(tmp+"/_tt.py","w").write(code)
    subprocess.run([sys.executable,"-I","tools/frolvy_port.py","9884",tmp+"/_tt.py"],capture_output=True)
    subprocess.run([sys.executable,"-I","tools/frolvy_shot.py","9884",tmp+"/tt.png"],capture_output=True)
    ims.append(Image.open(tmp+"/tt.png").convert("RGB"))
w,h=ims[0].size; s=Image.new("RGB",(w*2,h*((len(ims)+1)//2)))
for i,im in enumerate(ims): s.paste(im,((i%2)*w,(i//2)*h))
s.save(sys.argv[1])
