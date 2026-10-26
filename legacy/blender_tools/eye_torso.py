"""Torso/head check: model outline on the reference (grid cameras), region from the hips up, with 0.1 m ticks.
python legacy/blender_tools/eye_torso.py --trials a,b [--lo 0.6 --hi 1.9] [--views front,left,back,right]"""
import argparse, json, os
import cv2, numpy as np
from eye_compare import ROOT, ref_frame
ap = argparse.ArgumentParser(); ap.add_argument("--trials", required=True); ap.add_argument("--frame", type=int, default=1)
ap.add_argument("--lo", type=float, default=0.6); ap.add_argument("--hi", type=float, default=1.95)
ap.add_argument("--views", default="front,left,back,right"); ap.add_argument("--half", type=float, default=0.75)
ap.add_argument("--out", default=os.path.join(ROOT, "work", "idle", "analysis", "torso.png")); a = ap.parse_args()
cams = json.load(open(os.path.join(ROOT, "work", "idle_breath", "cameras.json")))
rows = []
for t in a.trials.split(","):
    tiles = []
    for v in a.views.split(","):
        ref = ref_frame(v, a.frame).copy(); c = cams[v]; gx, gy, ppm = int(c["center_px"]), int(c["ground_px"]), c["px_per_m"]
        if t != "REF":
            r = cv2.imread(os.path.join(ROOT, "work", "blender", "look", f"eye_{t}_{v}.png"), cv2.IMREAD_UNCHANGED)
            m = cv2.resize((r[:, :, 3] > 100).astype(np.uint8), (1920, 1080), interpolation=cv2.INTER_NEAREST)
            cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); cv2.drawContours(ref, cs, -1, (255, 255, 0), 2)
        for k in range(int(a.lo * 10), int(a.hi * 10) + 1):
            y = int(round(gy - k * ppm / 10)); cv2.line(ref, (gx - int(a.half * ppm), y), (gx - int(a.half * ppm) + (14 if k % 5 == 0 else 6), y), (0, 255, 255), 1)
        crop = ref[int(gy - a.hi * ppm):int(gy - a.lo * ppm), gx - int(a.half * ppm):gx + int(a.half * ppm)]
        cv2.putText(crop, f"{t} {v}", (5, 18), 0, 0.55, (255, 255, 255), 2); tiles.append(crop)
    rows.append(np.hstack(tiles))
cv2.imwrite(a.out, np.vstack(rows)); print(a.out)
