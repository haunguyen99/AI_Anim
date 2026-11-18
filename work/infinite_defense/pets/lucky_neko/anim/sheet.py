"""py -I sheet.py out.png frames cam   (cam front|side|persp) -> contact sheet from Frolvy 9891 (rig hidden)"""
import subprocess, sys, os, math
from PIL import Image
out, fr, cam = sys.argv[1], [int(x) for x in sys.argv[2].split(",")], sys.argv[3]
PY = sys.executable; PORT = "9891"; T = os.environ["TEMP"]
setup = {"front": "api.look_through('front'); api.set_camera_ortho('front', True); api.set_attr('front.ow', 1.5); api.move('front', 0.0, 0.34, 100)\n",
         "side": "api.look_through('side'); api.set_camera_ortho('side', True); api.set_attr('side.ow', 1.3); api.move('side', 100, 0.34, 0.12)\n",
         "persp": "import math\napi.look_through('persp'); api.set_camera_ortho('persp', False); a = math.radians(25)\napi.move('persp', 0.8*math.sin(a), 0.5, 0.8*math.cos(a)); api.rotate('persp', -8, 25, 0)\n"}[cam]
open(os.path.join(T, "_sh_setup.py"), "w").write("api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\n" + setup)
subprocess.run([PY, "-I", "tools/frolvy_port.py", PORT, os.path.join(T, "_sh_setup.py")], capture_output=True)
ims = []
for f in fr:
    open(os.path.join(T, "_sh_f.py"), "w").write("api.set_frame(%d)\n" % f)
    subprocess.run([PY, "-I", "tools/frolvy_port.py", PORT, os.path.join(T, "_sh_f.py")], capture_output=True)
    png = os.path.join(T, "_sh_%d.png" % f)
    subprocess.run([PY, "-I", "tools/frolvy_shot.py", PORT, png], capture_output=True)
    im = Image.open(png).convert("RGB"); w, h = im.size
    ims.append(im.crop((int(w * 0.28), 0, int(w * 0.72), h)))
w, h = ims[0].size; cols = min(len(ims), 4); rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (w * cols, h * rows))
for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(out); print("ok", out, sheet.size)
open(os.path.join(T, "_sh_f.py"), "w").write("api.set_frame(0); api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(False); api.select([])\n")
subprocess.run([PY, "-I", "tools/frolvy_port.py", PORT, os.path.join(T, "_sh_f.py")], capture_output=True)
