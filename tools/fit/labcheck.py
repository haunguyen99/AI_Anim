"""Side-by-side part-label maps: reference | model, per view and frame.
python tools/fit/labcheck.py WORK BASIS.npy --frames 1,52 --out look/labcheck.png"""
import argparse, os, sys
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refmask
from silmodel import SilModel
ap = argparse.ArgumentParser(); ap.add_argument("work"); ap.add_argument("basis", nargs="?")
ap.add_argument("--frames", default="1"); ap.add_argument("--views", default="front,back,left,right")
ap.add_argument("--out", default="look/labcheck.png"); a = ap.parse_args()
m = SilModel(a.work); meta = refmask.load(a.work)[1]; L = refmask.build_labels(a.work)
B = np.load(a.basis) if a.basis else m.basis0
rows = []
for f in [int(x) - 1 for x in a.frames.split(",")]:
    P, _ = m.skin(B[f]); Pw = m.to_world(P); tiles = []
    for v in a.views.split(","):
        ml = m.raster_labels(Pw, v, meta["boxes"][v], meta["scale"]); rl = L[v][f]
        hh, ww = min(ml.shape[0], rl.shape[0]), min(ml.shape[1], rl.shape[1])
        t = np.hstack([refmask.PALETTE[rl[:hh, :ww]], np.full((hh, 2, 3), 90, np.uint8), refmask.PALETTE[ml[:hh, :ww]]])
        cv2.putText(t, f"{v} f{f + 1}  ref | model", (4, 14), 0, 0.4, (255, 255, 255), 1)
        tiles.append(np.pad(t, ((0, 0), (0, 6), (0, 0)), constant_values=60))
    rows.append(np.hstack(tiles))
cv2.imwrite(os.path.join(a.work, a.out), np.vstack(rows))
