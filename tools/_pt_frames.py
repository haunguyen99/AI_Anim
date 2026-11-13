"""Chup nhieu frame cua Frolvy theo cong thanh 1 anh: python tools/_pt_frames.py <cong> <out.png> f1,f2,... [side|front]"""
import subprocess, sys, tempfile, os
from PIL import Image
port, out, fr = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
cam = sys.argv[4] if len(sys.argv) > 4 else "side"
ims = []
for f in fr:
    code = "api.set_frame(1); api.set_frame(%d)\n" % f
    if f == fr[0]:
        code += "api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\napi.look_through('%s'); api.set_camera_ortho('%s', True); api.set_attr('%s.ow', 3.0)\napi.move('%s', %s)\n" % (cam, cam, cam, cam, "100, 0.48, 0" if cam == "side" else "0, 0.48, 100")
    p = os.path.join(tempfile.gettempdir(), "_pf.py"); open(p, "w").write(code)
    subprocess.run([sys.executable, "-I", "tools/frolvy_port.py", port, p], capture_output=True)
    png = os.path.join(tempfile.gettempdir(), "_pf_%d.png" % f)
    subprocess.run([sys.executable, "-I", "tools/frolvy_shot.py", port, png], capture_output=True)
    ims.append(Image.open(png).convert("RGB"))
w, h = ims[0].size; cols = min(len(ims), 3); rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (w * cols, h * rows))
for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(out); print("ok", out, sheet.size)
