import subprocess,sys,tempfile
from PIL import Image
tmp=tempfile.gettempdir(); ims=[]
vals=[tuple(float(y) for y in x.split(":")) for x in sys.argv[2].split(",")]
for v in vals:
    for cam in ("front","side"):
        code="api.set_frame(1)\nfor c in api.ls('Curve'):\n    if c.startswith('CTL_'):\n        for a in ('rx','ry','rz','tx','ty','tz'): api.set_attr(c+'.'+a,0.0)\napi.set_attr('CTL_Tongue1_M.tz',-0.26); api.set_attr('CTL_Jaw_M.rx',%f); api.set_attr('CTL_Mouth_M.sy',%f)\napi.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\napi.look_through('%s'); api.set_camera_ortho('%s', True); api.set_attr('%s.ow', 0.5)\napi.move('%s', %s)\n"%(v[0],v[1],cam,cam,cam,cam,"100, 0.36, 0.3" if cam=="side" else "0, 0.36, 100")
        open(tmp+"/_jj.py","w").write(code)
        subprocess.run([sys.executable,"-I","tools/frolvy_port.py","9884",tmp+"/_jj.py"],capture_output=True)
        subprocess.run([sys.executable,"-I","tools/frolvy_shot.py","9884",tmp+"/jj.png"],capture_output=True)
        ims.append(Image.open(tmp+"/jj.png").convert("RGB").resize((560,360)))
w,h=ims[0].size; s=Image.new("RGB",(w*2,h*len(vals)))
for i,im in enumerate(ims): s.paste(im,((i%2)*w,(i//2)*h))
s.save(sys.argv[1])
