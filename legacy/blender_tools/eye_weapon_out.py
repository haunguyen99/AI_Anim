"""Weapon-only renders (part_<tag>_<view>.png) vs reference mask: % of weapon pixels outside the reference silhouette.
python legacy/blender_tools/eye_weapon_out.py --trials a,b"""
import argparse, json, os
import cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ap = argparse.ArgumentParser(); ap.add_argument("--trials", required=True); ap.add_argument("--frame", type=int, default=1); a = ap.parse_args()
z = np.load(os.path.join(ROOT, "work", "idle", "refmasks.npz")); meta = json.load(open(os.path.join(ROOT, "work", "idle", "refmasks.json")))
R = {}
for v in ("front", "left", "back", "right"):
    b = meta["boxes"][v]; m = np.zeros((1080, 1920), np.uint8)
    m[b[1]:b[3], b[0]:b[2]] = cv2.resize(z[v][a.frame - 1], (b[2] - b[0], b[3] - b[1]), interpolation=cv2.INTER_NEAREST)
    R[v] = cv2.erode(m, np.ones((5, 5), np.uint8)) > 0       # 2 px tolerance
out = []
for t in a.trials.split(","):
    row = []
    for v in ("front", "left", "back", "right"):
        w = cv2.resize(cv2.imread(os.path.join(ROOT, "work", "blender", "look", f"part_{t}_{v}.png"), cv2.IMREAD_UNCHANGED)[:, :, 3], (1920, 1080)) > 100
        row.append(100.0 * (w & ~R[v]).sum() / max(1, w.sum()))
    out.append((float(np.mean(row)), t, row))
for m_, t, row in sorted(out):
    print(f"{t:10s} weapon outside ref: {np.round(row, 1)} %  mean {m_:.1f}%")
