"""Silhouette IoU of eye-trial renders (tools/blender/eye_pose.py) against the reference masks - a check, not a target.

python tools/eye_iou.py --trials a,b [--frame 1]
"""
import argparse
import json
import os

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", required=True)
    ap.add_argument("--frame", type=int, default=1)
    ap.add_argument("--prefix", default="eye")
    a = ap.parse_args()
    z = np.load(os.path.join(ROOT, "work", "idle", "refmasks.npz"))
    meta = json.load(open(os.path.join(ROOT, "work", "idle", "refmasks.json")))
    for t in a.trials.split(","):
        row = []
        for v in ("front", "left", "back", "right"):
            b = meta["boxes"][v]; m = z[v][a.frame - 1] > 0
            r = cv2.imread(os.path.join(ROOT, "work", "blender", "look", f"{a.prefix}_{t}_{v}.png"), cv2.IMREAD_UNCHANGED)[:, :, 3]
            r = cv2.resize(r, (1920, 1080))[b[1]:b[3], b[0]:b[2]]
            r = cv2.resize(r, (m.shape[1], m.shape[0])) > 100
            row.append((r & m).sum() / (r | m).sum())
        print(f"{t:8s} IoU front {row[0]:.3f} left {row[1]:.3f} back {row[2]:.3f} right {row[3]:.3f}  mean {np.mean(row):.3f}")


if __name__ == "__main__":
    main()
