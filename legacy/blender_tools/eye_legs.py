"""Leg-region check: reference vs trial renders, model outline drawn on the reference, metric ticks (grid cameras).

Blender side: legacy/blender/eye_pose.py or work/blender/p0_grid.py renders eye_<tag>_<view>.png
python legacy/blender_tools/eye_legs.py --trials a,b [--frame 1] [--out work/idle/analysis/legs.png]
"""
import argparse
import json
import os

import cv2
import numpy as np

from eye_compare import ROOT, ref_frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", required=True)
    ap.add_argument("--frame", type=int, default=1)
    ap.add_argument("--up", type=float, default=0.75, help="metres above the floor to show")
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "idle", "analysis", "legs.png"))
    a = ap.parse_args()
    cams = json.load(open(os.path.join(ROOT, "work", "idle_breath", "cameras.json")))
    rows = []
    for t in a.trials.split(","):
        tiles = []
        for v in ("front", "left", "back", "right"):
            ref = ref_frame(v, a.frame).copy()
            r = cv2.imread(os.path.join(ROOT, "work", "blender", "look", f"eye_{t}_{v}.png"), cv2.IMREAD_UNCHANGED)
            m = cv2.resize((r[:, :, 3] > 100).astype(np.uint8), (1920, 1080), interpolation=cv2.INTER_NEAREST)
            cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(ref, cs, -1, (255, 255, 0), 2)
            c = cams[v]; gx, gy, ppm = int(c["center_px"]), int(c["ground_px"]), c["px_per_m"]
            for k in range(-8, 9):
                x = int(round(gx + k * ppm / 10))
                cv2.line(ref, (x, gy), (x, gy + (14 if k % 5 == 0 else 6)), (0, 255, 255), 1)
            y0 = int(gy - a.up * ppm)
            crop = ref[y0:gy + 20, gx - int(0.9 * ppm):gx + int(0.9 * ppm)]
            crop = cv2.resize(crop, None, fx=1.2, fy=1.2)
            cv2.putText(crop, f"{t} {v}", (5, 18), 0, 0.55, (255, 255, 255), 2)
            tiles.append(crop)
        rows.append(np.hstack(tiles))
    cv2.imwrite(a.out, np.vstack(rows))
    print(a.out)


if __name__ == "__main__":
    main()
