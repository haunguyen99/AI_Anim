import sys, json, os, numpy as np
sys.argv = [sys.argv[0]] + sys.argv[1:]
out = sys.argv[1]; frames = [int(x) for x in sys.argv[2].split(",")]; view = sys.argv[3] if len(sys.argv) > 3 else "side"
sys.path.insert(0, "work/infinite_defense/pets/steam_pug_turbo")
import render as R
A = json.load(open(os.environ["TEMP"] + "/pug_anim.json"))
from PIL import Image, ImageDraw
ims = []
for f in frames:
    R.P = np.array(A[str(f)]).reshape(-1, 3)
    im = R.render(R.views[view], S=420, sc=300); ImageDraw.Draw(im).text((8, 8), "f%d" % f, fill=(255, 255, 255)); ims.append(im)
S = ims[0].size[0]; sh = Image.new("RGB", (S * len(ims), S)); [sh.paste(im, (i * S, 0)) for i, im in enumerate(ims)]; sh.save(out)
