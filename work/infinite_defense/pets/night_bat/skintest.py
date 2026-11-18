"""py skintest.py out.png cam : poses test sheet"""
import subprocess, sys, tempfile, os
from PIL import Image
out, cam = sys.argv[1], sys.argv[2]
tests = [
 "",
 "api.rotate('CTL_Wing1_L',0,0,35); api.rotate('CTL_Wing2_L',0,0,25); api.rotate('CTL_Wing3_L',0,0,25); api.rotate('CTL_Wing4_L',0,0,25); api.rotate('CTL_Wing1_R',0,0,-35); api.rotate('CTL_Wing2_R',0,0,-25); api.rotate('CTL_Wing3_R',0,0,-25); api.rotate('CTL_Wing4_R',0,0,-25)",
 "api.rotate('CTL_Wing1_L',0,0,-35); api.rotate('CTL_Wing2_L',0,0,-25); api.rotate('CTL_Wing3_L',0,0,-25); api.rotate('CTL_Wing4_L',0,0,-25); api.rotate('CTL_Wing1_R',0,0,35); api.rotate('CTL_Wing2_R',0,0,25); api.rotate('CTL_Wing3_R',0,0,25); api.rotate('CTL_Wing4_R',0,0,25)",
 "api.rotate('CTL_Ear1_L',0,0,-25); api.rotate('CTL_Ear2_L',0,0,-25); api.rotate('CTL_Ear1_R',0,0,25); api.rotate('CTL_Ear2_R',0,0,25)",
 "api.rotate('CTL_Head_M',-25,0,0); api.rotate('CTL_Jaw_M',25,0,0)",
 "api.rotate('CTL_Root_M',-20,0,0); api.rotate('CTL_Spine1_M',-15,0,0)",
 "api.rotate('CTL_Ear1_L',-25,0,0); api.rotate('CTL_Ear1_R',-25,0,0); api.rotate('CTL_Wing1_L',0,40,0); api.rotate('CTL_Wing1_R',0,-40,0)",
 "api.rotate('CTL_Wing1_L',0,0,48); api.rotate('CTL_Wing1_R',0,0,-48)",
 "api.rotate('CTL_Wing1_L',0,0,-48); api.rotate('CTL_Wing1_R',0,0,48)",
]
ALL = ['CTL_Root_M','CTL_Spine1_M','CTL_Head_M','CTL_Jaw_M'] + ['CTL_%s_%s' % (n, s) for n in ('Ear1','Ear2','Wing1','Wing2','Wing3','Wing4') for s in 'LR']
pos = {"side": "100, 0.33, 0", "front": "0, 0.33, 100", "top": "0, 100, 0"}[cam]
ims = []
for k, t in enumerate(tests):
    code = "for c in %r: api.rotate(c,0,0,0); api.move(c,0,0,0)\n%s\napi.set_frame(3); api.set_frame(0)\n" % (ALL, t)
    if k == 0:
        code += "api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\napi.look_through('%s'); api.set_camera_ortho('%s', True); api.set_attr('%s.ow', 1.6)\napi.move('%s', %s)\n" % (cam, cam, cam, cam, pos)
    p = os.path.join(tempfile.gettempdir(), "_st.py"); open(p, "w").write(code)
    r = subprocess.run([sys.executable, "-I", "tools/frolvy_port.py", os.environ.get("BATPORT","9883"), p], capture_output=True, text=True)
    png = os.path.join(tempfile.gettempdir(), "_st_%d.png" % k)
    subprocess.run([sys.executable, "-I", "tools/frolvy_shot.py", os.environ.get("BATPORT","9883"), png], capture_output=True)
    ims.append(Image.open(png).convert("RGB"))
w, h = ims[0].size; cols = 3; rows = (len(ims) + 2) // 3
sheet = Image.new("RGB", (w * cols, h * rows))
for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(out); print("ok", sheet.size)
