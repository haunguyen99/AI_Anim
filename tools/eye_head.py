"""Head close-up: REF | each trial (textured), crops centred on work/idle/analysis/head_px.json.
python tools/eye_head.py --trials a,b [--size 170]"""
import argparse, json, os
import cv2, numpy as np
from eye_compare import ROOT, ref_frame
ap = argparse.ArgumentParser(); ap.add_argument("--trials", required=True); ap.add_argument("--size", type=int, default=170)
ap.add_argument("--frame", type=int, default=1); ap.add_argument("--out", default=os.path.join(ROOT, "work", "idle", "analysis", "head.png")); a = ap.parse_args()
hp = json.load(open(os.path.join(ROOT, "work", "idle", "analysis", "head_px.json"))); rows = []
for v in ("front", "left", "back", "right"):
    ref = ref_frame(v, a.frame); cx, cy = map(int, hp[v]); h = a.size
    tiles = [("REF", ref)]
    for t in a.trials.split(","):
        r = cv2.resize(cv2.imread(os.path.join(ROOT, "work", "blender", "look", f"eye_{t}_{v}.png"), cv2.IMREAD_UNCHANGED), (1920, 1080))
        am = r[:, :, 3:] / 255.0; tiles.append((t, (np.full_like(ref, 90) * (1 - am) + r[:, :, :3] * am).astype(np.uint8)))
    out = []
    for n, im in tiles:
        c = cv2.resize(im[cy - h:cy + h, cx - h:cx + h], (240, 240)); cv2.line(c, (120, 0), (120, 240), (0, 255, 255), 1); cv2.line(c, (0, 120), (240, 120), (0, 255, 255), 1)
        cv2.putText(c, f"{n} {v}", (4, 16), 0, 0.45, (255, 255, 255), 1); out.append(c)
    rows.append(np.hstack(out))
cv2.imwrite(a.out, np.vstack(rows)); print(a.out)
