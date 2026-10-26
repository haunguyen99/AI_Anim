"""Side-by-side eye check: reference frame vs trial renders from tools/blender/eye_pose.py, five views.

python tools/eye_compare.py --frame 1 --trials a,b [--region weapon|body] [--out work/idle/analysis/eye.png]
Rows = views, columns = REF then each trial.
"""
import argparse
import glob
import os

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFDIR = os.path.join(ROOT, "Assets", "Boss_Gaygor", "Ref", "Boss_Gaygor_idle")
# file name suffix per view (the left/right files are swapped: see work/idle/refs.json)
FILES = {"front": "front", "back": "back", "left": "right", "right": "left", "top": "top"}
REGIONS = {
    "weapon": {"front": (1000, 300, 1340, 640), "left": (700, 260, 1120, 660), "back": (560, 260, 980, 660),
               "right": (720, 220, 1140, 640), "top": (860, 330, 1300, 720)},
    "hand": {"front": (1080, 340, 1340, 600), "left": (760, 330, 1080, 600), "back": (560, 340, 840, 620),
             "right": (760, 300, 1060, 560), "top": (1080, 400, 1340, 660)},
    "body": {"front": (820, 220, 1300, 840), "left": (680, 220, 1180, 840), "back": (540, 220, 1020, 840),
             "right": (720, 220, 1220, 840), "top": (800, 300, 1320, 780)},
}


def ref_frame(view, f):
    p = glob.glob(os.path.join(REFDIR, f"*_{FILES[view]}_*.mov"))[0]
    cap = cv2.VideoCapture(p)
    for _ in range(f):
        ok, im = cap.read()
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=int, default=1)
    ap.add_argument("--trials", required=True)
    ap.add_argument("--region", default="weapon")
    ap.add_argument("--views", default="front,left,back,right,top")
    ap.add_argument("--height", type=int, default=230)
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "idle", "analysis", "eye.png"))
    a = ap.parse_args()
    rows = []
    for v in a.views.split(","):
        ref = ref_frame(v, a.frame)
        x0, y0, x1, y1 = REGIONS[a.region][v]
        tiles = [("REF", ref)]
        for t in a.trials.split(","):
            r = cv2.resize(cv2.imread(os.path.join(ROOT, "work", "blender", "look", f"eye_{t}_{v}.png"), cv2.IMREAD_UNCHANGED),
                           (ref.shape[1], ref.shape[0]))
            am = r[:, :, 3:] / 255.0
            tiles.append((t, (np.full_like(ref, 90) * (1 - am) + r[:, :, :3] * am).astype(np.uint8)))
        out = []
        for name, im in tiles:
            c = im[y0:y1, x0:x1].copy()
            c = cv2.resize(c, (int(c.shape[1] * a.height / c.shape[0]), a.height), interpolation=cv2.INTER_AREA)
            cv2.putText(c, f"{name} {v}", (5, 18), 0, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            out.append(c)
        rows.append(np.hstack(out))
    w = max(r.shape[1] for r in rows)
    cv2.imwrite(a.out, np.vstack([np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0))) for r in rows]))
    print(a.out)


if __name__ == "__main__":
    main()
