"""REF | ANIM side by side for every view, same crop, plus the ANIM outline drawn on the REF (green) and per-view IoU.

python tools/eye_side.py WORK FRAME TAG [TAG2 ...] [--dir work/attack/look_v4] [--out file.png] [--h 420]
Renders come from tools/blender/eye_views.py (<dir>/<TAG>_<view>.png, RGBA). WORK/refs.json lists the reference videos.
Rows = views; columns = REF+outline, then each TAG. The IoU uses the filled reference mask (shading lines closed).
"""
import argparse
import json
import os

import cv2
import numpy as np


def ref_frame(path, n):
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, n - 1)
    ok, f = cap.read()
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("frame", type=int)
    ap.add_argument("tags", nargs="+")
    ap.add_argument("--dir")
    ap.add_argument("--out")
    ap.add_argument("--h", type=int, default=420)
    ap.add_argument("--views", default="front,back,left,right,top")
    ap.add_argument("--band", help="y0,y1 rows (full frame) to crop to, e.g. 600,915 for legs (top view keeps all)")
    a = ap.parse_args()
    d = a.dir or os.path.join(a.work, "look_v4")
    views = json.load(open(os.path.join(a.work, "refs.json")))["views"]
    rows, rep = [], {}
    for v in a.views.split(","):
        ref = ref_frame(views[v]["path"], a.frame)
        rm = cv2.morphologyEx((ref.max(2) > 110).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)) > 0
        anims = []
        for t in a.tags:
            im = cv2.imread(os.path.join(d, f"{t}_{v}.png"), cv2.IMREAD_UNCHANGED)
            am = im[:, :, 3] > 127
            bg = np.zeros_like(im[:, :, :3])
            rgb = np.where(am[..., None], im[:, :, :3], bg)
            anims.append((t, am, rgb))
            rep[f"{t}_{v}"] = round(float((am & rm).sum() / max((am | rm).sum(), 1)), 3)
        m = rm.copy()
        for _, am, _ in anims:
            m |= am
        if a.band and v != "top":
            b0, b1 = map(int, a.band.split(","))
            m[:b0] = False
            m[b1:] = False
        ys, xs = np.nonzero(m)
        y0, y1 = max(ys.min() - 30, 0), min(ys.max() + 30, m.shape[0])
        x0, x1 = max(xs.min() - 30, 0), min(xs.max() + 30, m.shape[1])
        r = ref.copy()
        cnt, _ = cv2.findContours(anims[0][1].astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(r, cnt, -1, (0, 255, 0), 2)
        tiles = [("REF " + v, r)] + [(f"{t} IoU {rep[f'{t}_{v}']:.2f}", rgb) for t, _, rgb in anims]
        row = []
        for label, im in tiles:
            c = im[y0:y1, x0:x1]
            c = cv2.resize(c, (int(c.shape[1] * a.h / c.shape[0]), a.h))
            cv2.putText(c, label, (6, 24), 0, 0.7, (0, 0, 255), 2)
            row.append(c)
        rows.append(np.hstack(row))
    w = max(r.shape[1] for r in rows)
    out = a.out or os.path.join(d, f"cmp_f{a.frame}_{'_'.join(a.tags)}.png")
    cv2.imwrite(out, np.vstack([np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0))) for r in rows]))
    print(out)
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
