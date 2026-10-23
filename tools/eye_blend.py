"""Edge / ghost check: reference vs each trial render (edges: ref green, model magenta; ghost: 50% blend) (tools/blender/eye_pose.py renders).

python tools/eye_blend.py --frame 1 --trials o,L6 [--views left,back,front] [--out work/idle/analysis/blend.png]
Rows = trials, columns = views. Misplaced parts show as double images.
"""
import argparse
import os

import cv2
import numpy as np

from eye_compare import REGIONS, ROOT, ref_frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=int, default=1)
    ap.add_argument("--trials", required=True)
    ap.add_argument("--views", default="left,back,front")
    ap.add_argument("--region", default="body")
    ap.add_argument("--height", type=int, default=300)
    ap.add_argument("--mode", default="edges", help="edges | ghost")
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "idle", "analysis", "blend.png"))
    a = ap.parse_args()
    refs = {v: ref_frame(v, a.frame) for v in a.views.split(",")}
    rows = []
    for t in a.trials.split(","):
        tiles = []
        for v, ref in refs.items():
            r = cv2.resize(cv2.imread(os.path.join(ROOT, "work", "blender", "look", f"eye_{t}_{v}.png"), cv2.IMREAD_UNCHANGED),
                           (ref.shape[1], ref.shape[0]))
            am = r[:, :, 3:] / 255.0
            m = (ref * (1 - am) + r[:, :, :3] * am).astype(np.uint8)
            if a.mode == "edges":      # ref edges green, model edges magenta, on a dark copy of the ref
                er = cv2.Canny(cv2.GaussianBlur(cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY), (3, 3), 0), 40, 110)
                em = cv2.Canny(cv2.GaussianBlur(cv2.cvtColor(m, cv2.COLOR_BGR2GRAY), (3, 3), 0), 40, 110)
                em[r[:, :, 3] < 30] = 0
                b = (ref * 0.25).astype(np.uint8)
                b[er > 0] = (0, 255, 0)
                b[em > 0] = (255, 0, 255)
                b[(er > 0) & (em > 0)] = (255, 255, 255)
            else:
                b = cv2.addWeighted(ref, 0.5, m, 0.5, 0)
            x0, y0, x1, y1 = REGIONS[a.region][v]
            c = b[y0:y1, x0:x1].copy()
            c = cv2.resize(c, (int(c.shape[1] * a.height / c.shape[0]), a.height), interpolation=cv2.INTER_AREA)
            cv2.putText(c, f"{t} {v}", (5, 18), 0, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            tiles.append(c)
        rows.append(np.hstack(tiles))
    w = max(r.shape[1] for r in rows)
    cv2.imwrite(a.out, np.vstack([np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0))) for r in rows]))
    print(a.out)


if __name__ == "__main__":
    main()
