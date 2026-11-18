"""py shot.py out.png frames cam ow cy [hide=1]  -> contact sheet; cam front|side|top"""
import subprocess, sys, tempfile, os
from PIL import Image
out, fr = sys.argv[1], [int(x) for x in sys.argv[2].split(",")]
cam = sys.argv[3]; ow = sys.argv[4]; cy = sys.argv[5]; showrig = len(sys.argv) > 6 and sys.argv[6] == "rig"
pos = {"persp": "0,0,0", "side": "100, %s, 0", "front": "0, %s, 100", "top": "0, 100, 0.001"}[cam]
if "%s" in pos: pos = pos % cy
ims = []
for k, f in enumerate(fr):
    code = "api.set_frame(1); api.set_frame(%d)\n" % f
    if k == 0:
        code += ("api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(%s); api.select([])\n" % ("False" if showrig else "True"))
        code += "api.look_through('%s'); api.set_camera_ortho('%s', True); api.set_attr('%s.ow', %s)\napi.move('%s', %s)\n" % (cam, cam, cam, ow, cam, pos)
    p = os.path.join(tempfile.gettempdir(), "_pf.py"); open(p, "w").write(code)
    subprocess.run([sys.executable, "-I", "tools/frolvy_port.py", os.environ.get("BATPORT","9886"), p], capture_output=True)
    png = os.path.join(tempfile.gettempdir(), "_pf_%d.png" % f)
    subprocess.run([sys.executable, "-I", "tools/frolvy_shot.py", os.environ.get("BATPORT","9886"), png], capture_output=True)
    ims.append(Image.open(png).convert("RGB"))
w, h = ims[0].size; cols = min(len(ims), 3); rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (w * cols, h * rows))
for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(out); print("ok", out, sheet.size)
