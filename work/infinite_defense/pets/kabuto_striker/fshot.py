"""py fshot.py out.png cam ow cy f1,f2,... -> contact sheet (4 cols), crops ngang giua"""
import subprocess, sys, os, tempfile
from PIL import Image
out, cam, ow, cy, frs = sys.argv[1:6]; frs = [int(x) for x in frs.split(",")]
PORT = os.environ.get("KPORT", "9887"); T = tempfile.gettempdir()
pos = {"side": "100, %s, 0" % cy, "front": "0, %s, 100" % cy, "top": "0,100,0.001"}[cam]
ims = []
for k, f in enumerate(frs):
    code = "api.set_frame(1); api.set_frame(%d)\n" % f
    if k == 0:
        code += "api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\napi.look_through('%s'); api.set_camera_ortho('%s', True); api.set_attr('%s.ow', %s)\napi.move('%s', %s)\n" % (cam, cam, cam, ow, cam, pos)
    p = os.path.join(T, "_kf.py"); open(p, "w").write(code)
    subprocess.run([sys.executable, "-I", "tools/frolvy_port.py", PORT, p], capture_output=True)
    png = os.path.join(T, "_kf%d.png" % f); subprocess.run([sys.executable, "-I", "tools/frolvy_shot.py", PORT, png], capture_output=True)
    ims.append(Image.open(png).convert("RGB").crop((250, 0, 550, 337)))
w, h = ims[0].size; cols = min(4, len(ims)); rows = (len(ims) + cols - 1) // cols
sh = Image.new("RGB", (w * cols, h * rows))
for i, im in enumerate(ims): sh.paste(im, ((i % cols) * w, (i // cols) * h))
sh.save(out); print("ok", out)
