"""Bang anh tu kiem: python3 -I sheet_v2.py <out.png> <cam> <frames,..> [ow] [cx,cy,cz]  (mo san scene tren cong 9885)"""
import subprocess, sys, os
from PIL import Image, ImageDraw
out, cam, fr = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
extra = sys.argv[4:]
ims = []
here = os.path.dirname(os.path.abspath(__file__))
for f in fr:
    p = "/tmp/_sh_%d.png" % f
    subprocess.run([sys.executable, "-I", os.path.join(here, "shot_v2.py"), p, cam, str(f)] + extra, capture_output=True)
    im = Image.open(p).convert("RGB"); ImageDraw.Draw(im).text((6, 4), "f%d" % f, fill=(255, 255, 0)); ims.append(im)
w, h = ims[0].size; cols = min(4, len(ims)); rows = (len(ims) + cols - 1) // cols
sh = Image.new("RGB", (w * cols, h * rows))
for i, im in enumerate(ims): sh.paste(im, ((i % cols) * w, (i // cols) * h))
sh.save(out); print("ok", out, sh.size)
