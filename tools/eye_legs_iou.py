"""IoU of trial renders vs reference masks, restricted to the leg region (below UP metres), per view.
python tools/eye_legs_iou.py --trials a,b [--up 0.75]"""
import argparse, json, os
import cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument("--trials", required=True); ap.add_argument("--up", type=float, default=0.75)
ap.add_argument("--frame", type=int, default=1); a = ap.parse_args()
z = np.load(os.path.join(ROOT, "work", "idle", "refmasks.npz")); meta = json.load(open(os.path.join(ROOT, "work", "idle", "refmasks.json")))
cams = json.load(open(os.path.join(ROOT, "work", "idle_breath", "cameras.json")))
for t in a.trials.split(","):
    row = []
    for v in ("front", "left", "back", "right"):
        b = meta["boxes"][v]; m = np.zeros((1080, 1920), bool)
        m[b[1]:b[3], b[0]:b[2]] = cv2.resize(z[v][a.frame - 1], (b[2] - b[0], b[3] - b[1]), interpolation=cv2.INTER_NEAREST) > 0
        r = cv2.resize(cv2.imread(os.path.join(ROOT, "work", "blender", "look", f"eye_{t}_{v}.png"), cv2.IMREAD_UNCHANGED)[:, :, 3], (1920, 1080)) > 100
        y0 = int(cams[v]["ground_px"] - a.up * cams[v]["px_per_m"]); m, r = m[y0:], r[y0:]
        row.append((m & r).sum() / (m | r).sum())
    print(f"{t:8s} legs IoU front {row[0]:.3f} left {row[1]:.3f} back {row[2]:.3f} right {row[3]:.3f} mean {np.mean(row):.3f}")
