"""python work/.../anim/shotsheet.py <out.png> mode f1,f2,...   mode=pose (apply attack/idle pose in test, needs test script) -- here: keyed scene frames"""
import subprocess, sys, tempfile, os
from PIL import Image
out, fr = sys.argv[1], [int(x) for x in sys.argv[2].split(",")]
cam = sys.argv[3] if len(sys.argv) > 3 else "side"
pre = open(sys.argv[4]).read() if len(sys.argv) > 4 else ""
ims = []
for f in fr:
    code = "api.set_frame(1); api.set_frame(%d)\n" % f
    code += "api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\napi.look_through('%s'); api.set_camera_ortho('%s', True); api.set_attr('%s.ow', 1.7)\napi.move('%s', %s)\n" % (cam, cam, cam, cam, "100, 0.45, 0.05" if cam == "side" else "0, 0.4, 100")
    p = os.path.join(tempfile.gettempdir(), "_pf.py"); open(p, "w").write(code)
    subprocess.run([sys.executable, "-I", "tools/frolvy_port.py", "9884", p], capture_output=True)
    png = os.path.join(tempfile.gettempdir(), "_pf_%d.png" % f)
    subprocess.run([sys.executable, "-I", "tools/frolvy_shot.py", "9884", png], capture_output=True)
    ims.append(Image.open(png).convert("RGB"))
w, h = ims[0].size; cols = min(len(ims), 3); rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (w * cols, h * rows))
for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(out); print("ok", out, sheet.size)
