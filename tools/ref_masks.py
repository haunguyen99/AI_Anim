"""Filled reference silhouettes per frame and view, downscaled, for fast pose fitting in Blender.
python tools/ref_masks.py WORK OUTDIR [--pct 25] [--frames 1-68]
Writes OUTDIR/f<frame>_<view>.npy (bool, H x W at PCT % of 1920x1080). Same fill as tools/eye_side.py (closes shading lines)."""
import argparse, json, os
import cv2, numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("work"); ap.add_argument("out"); ap.add_argument("--pct", type=int, default=25)
ap.add_argument("--frames", default="1-68")
a = ap.parse_args()
f0, f1 = map(int, a.frames.split("-"))
V = json.load(open(os.path.join(a.work, "refs.json")))["views"]
os.makedirs(a.out, exist_ok=True)
W, H = 1920 * a.pct // 100, 1080 * a.pct // 100
for v, d in V.items():
    cap = cv2.VideoCapture(d["path"])
    for f in range(1, f1 + 1):
        ok, fr = cap.read()
        if f < f0:
            continue
        m = cv2.morphologyEx((fr.max(2) > 110).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        m = cv2.resize(m.astype(np.float32), (W, H), interpolation=cv2.INTER_AREA) > 0.5
        np.save(os.path.join(a.out, f"f{f}_{v}.npy"), m)
print("ok", W, H)
