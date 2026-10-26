"""Close-ups (REF | trials, textured) and silhouette IoU inside a body-part box (work/idle/analysis/part_<PART>.json).
python legacy/blender_tools/eye_part_box.py --part armR --trials A0,A1 [--views front,left,back,right]"""
import argparse
import json
import os

import cv2
import numpy as np

from eye_compare import ROOT, ref_frame

ap = argparse.ArgumentParser(); ap.add_argument("--part", required=True); ap.add_argument("--trials", required=True)
ap.add_argument("--views", default="front,left,back,right"); ap.add_argument("--frame", type=int, default=1)
ap.add_argument("--tile", type=int, default=230); ap.add_argument("--no-image", action="store_true")
a = ap.parse_args()
boxes = json.load(open(os.path.join(ROOT, "work", "idle", "analysis", f"part_{a.part}.json")))
z = np.load(os.path.join(ROOT, "work", "idle", "refmasks.npz")); meta = json.load(open(os.path.join(ROOT, "work", "idle", "refmasks.json")))
views = a.views.split(","); trials = a.trials.split(",")
ref_m = {}
for v in views:
    b = meta["boxes"][v]; m = np.zeros((1080, 1920), bool)
    m[b[1]:b[3], b[0]:b[2]] = cv2.resize(z[v][a.frame - 1], (b[2] - b[0], b[3] - b[1]), interpolation=cv2.INTER_NEAREST) > 0
    ref_m[v] = m
rows = []; scores = {t: [] for t in trials}
for v in views:
    x0, y0, x1, y1 = boxes[v]; ref = ref_frame(v, a.frame); tiles = [("REF", ref)]
    for t in trials:
        r = cv2.resize(cv2.imread(os.path.join(ROOT, "work", "blender", "look", f"eye_{t}_{v}.png"), cv2.IMREAD_UNCHANGED), (1920, 1080))
        mk = r[:, :, 3] > 100; sl = (slice(max(0, y0), y1), slice(max(0, x0), x1))
        scores[t].append((mk[sl] & ref_m[v][sl]).sum() / max(1, (mk[sl] | ref_m[v][sl]).sum()))
        am = r[:, :, 3:] / 255.0; tiles.append((t, (np.full_like(ref, 90) * (1 - am) + r[:, :, :3] * am).astype(np.uint8)))
    out = []
    for n, im in tiles:
        c = im[max(0, y0):y1, max(0, x0):x1]; c = cv2.resize(c, (int(c.shape[1] * a.tile / c.shape[0]), a.tile))
        cv2.putText(c, f"{n} {v}", (4, 16), 0, 0.45, (255, 255, 255), 1); out.append(c)
    rows.append(np.hstack(out))
for t in trials:
    print(f"{t:6s} {a.part} IoU", np.round(scores[t], 3), "mean", round(float(np.mean(scores[t])), 3))
if not a.no_image:
    w = max(r.shape[1] for r in rows)
    p = os.path.join(ROOT, "work", "idle", "analysis", f"part_{a.part}.png")
    cv2.imwrite(p, np.vstack([np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0))) for r in rows])); print(p)
