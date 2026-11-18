"""py shot.py out.png cam ow cy 'ctl:rx,ry,rz;ctl:...' ... -> 1 image per pose-string (cam persp uses current view)"""
import subprocess, sys, os, tempfile
from PIL import Image
out, cam, ow, cy = sys.argv[1:5]; poses = sys.argv[5:]
PORT = os.environ.get("KPORT", "9887"); T = tempfile.gettempdir()
pos = {"side": "100, %s, 0", "front": "0, %s, 100", "top": "0, 100, 0.001"}[cam] % cy if cam != "top" else "0,100,0.001"
ims = []
for k, ps in enumerate(poses):
    code = "CT=[c for c in api.ls('Curve') if c.startswith('CTL_') and c!='CTL_Main']\nfor c in CT: api.rotate(c,0,0,0); api.move(c,0,0,0)\n"
    for it in [x for x in ps.split(";") if x]:
        n, v = it.split(":"); code += "api.rotate('%s',%s)\n" % (n, v)
    code += "api.set_frame(3); api.set_frame(0)\napi.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\n"
    code += "api.look_through('%s'); api.set_camera_ortho('%s', True); api.set_attr('%s.ow', %s)\napi.move('%s', %s)\n" % (cam, cam, cam, ow, cam, pos)
    p = os.path.join(T, "_kp.py"); open(p, "w").write(code)
    subprocess.run([sys.executable, "-I", "tools/frolvy_port.py", PORT, p], capture_output=True)
    png = os.path.join(T, "_kp%d.png" % k); subprocess.run([sys.executable, "-I", "tools/frolvy_shot.py", PORT, png], capture_output=True)
    ims.append(Image.open(png).convert("RGB").crop((200, 0, 600, 337)))
w, h = ims[0].size; sh = Image.new("RGB", (w * len(ims), h))
for i, im in enumerate(ims): sh.paste(im, (i * w, 0))
sh.save(out); print("ok", out)
