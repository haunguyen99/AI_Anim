"""Draw the outline of a part render (tools/blender/eye_part.py) on the reference frame, per view and trial.

python tools/eye_outline.py --trials a,b [--frame 1] [--views front,left,back,right] [--region weapon]
"""
import argparse
import os

import cv2
import numpy as np

from eye_compare import REGIONS, ROOT, ref_frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", required=True)
    ap.add_argument("--frame", type=int, default=1)
    ap.add_argument("--views", default="front,left,back,right")
    ap.add_argument("--region", default="weapon")
    ap.add_argument("--height", type=int, default=260)
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "idle", "analysis", "outline.png"))
    a = ap.parse_args()
    refs = {v: ref_frame(v, a.frame) for v in a.views.split(",")}
    rows = []
    for t in a.trials.split(","):
        tiles = []
        for v, ref in refs.items():
            r = cv2.imread(os.path.join(ROOT, "work", "blender", "look", f"part_{t}_{v}.png"), cv2.IMREAD_UNCHANGED)
            m = cv2.resize((r[:, :, 3] > 100).astype(np.uint8), (ref.shape[1], ref.shape[0]), interpolation=cv2.INTER_NEAREST)
            o = ref.copy()
            cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(o, cs, -1, (255, 255, 0), 2)
            x0, y0, x1, y1 = REGIONS[a.region][v]
            c = o[y0:y1, x0:x1].copy()
            c = cv2.resize(c, (int(c.shape[1] * a.height / c.shape[0]), a.height), interpolation=cv2.INTER_AREA)
            cv2.putText(c, f"{t} {v}", (5, 18), 0, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            tiles.append(c)
        rows.append(np.hstack(tiles))
    w = max(r.shape[1] for r in rows)
    cv2.imwrite(a.out, np.vstack([np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0))) for r in rows]))
    print(a.out)


if __name__ == "__main__":
    main()
