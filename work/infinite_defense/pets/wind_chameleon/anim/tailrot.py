import subprocess,sys,tempfile
from PIL import Image
W="work/infinite_defense/pets/wind_chameleon/"; tmp=tempfile.gettempdir(); ims=[]
cases=[(int(a.split(":")[0]),a.split(":")[1],float(a.split(":")[2])) for a in sys.argv[2].split(",")]
for i,ch,ang in cases:
    code="api.set_frame(1)\nfor c in api.ls('Curve'):\n    for a in ('rx','ry','rz'): api.set_attr(c+'.'+a,0.0)\napi.set_attr('CTL_Tail%d_M.%s',%f)\n"%(i,ch,ang)
    code+="api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\napi.look_through('side'); api.set_camera_ortho('side', True); api.set_attr('side.ow', 1.0); api.move('side', 100, 0.38, -0.2)\n"
    open(tmp+"/_tt.py","w").write(code)
    subprocess.run([sys.executable,"-I","tools/frolvy_port.py","9884",tmp+"/_tt.py"],capture_output=True)
    subprocess.run([sys.executable,"-I","tools/frolvy_shot.py","9884",tmp+"/tt.png"],capture_output=True)
    ims.append(Image.open(tmp+"/tt.png").convert("RGB"))
w,h=ims[0].size; cols=3; s=Image.new("RGB",(w*cols,h*((len(ims)+cols-1)//cols)))
for i,im in enumerate(ims): s.paste(im,((i%cols)*w,(i//cols)*h))
s.save(sys.argv[1])
