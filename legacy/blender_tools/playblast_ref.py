"""Review playblast with the reference: REF | ANIM for each view, views laid out in rows (--views "front,back,top/left").

Blender side first (keyed animation): attack_pose.playblast_frames(OUTDIR, range(1, N+1)) -> OUTDIR/r_<view>_<frame>.png
python legacy/blender_tools/playblast_ref.py --work work/attack --renders work/attack/playblast/blocking_v1 --frames 68
       --keys 1,13,25 --label "Attack blocking v1 (stepped)" --out work/attack/playblast/blocking_v1.webm
       [--page-webm work/review_page/clips/attack_blocking_v1.webm] [--thumb ...jpg --thumb-frame 13] [--loops 2]
Crop per view = union of reference and render silhouettes over the clip, so both halves share one scale.
Key frames get a red "KEY" tag on the ANIM half; held (stepped) frames show which key they hold.
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playblast_anim import encode  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--renders", required=True)
    ap.add_argument("--frames", type=int, required=True)
    ap.add_argument("--views", default="front,back,top/left", help="views per row, rows separated by '/'")
    ap.add_argument("--keys", default="")
    ap.add_argument("--label", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--page-webm", default="")
    ap.add_argument("--thumb", default="")
    ap.add_argument("--thumb-frame", type=int, default=1)
    ap.add_argument("--loops", type=int, default=2)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--height", type=int, default=330)
    a = ap.parse_args()
    layout = [r.split(",") for r in a.views.split("/")]
    views = [v for r in layout for v in r]
    n = a.frames
    keys = sorted(int(k) for k in a.keys.split(",") if k)
    V = json.load(open(os.path.join(a.work, "refs.json")))["views"]
    ref, anim = {}, {}
    for v in views:
        cap = cv2.VideoCapture(V[v]["path"])
        for f in range(1, n + 1):
            ok, fr = cap.read()
            ref[(v, f)] = cv2.resize(fr, (960, 540), interpolation=cv2.INTER_AREA)
            im = cv2.imread(os.path.join(a.renders, f"r_{v}_{f:04d}.png"), cv2.IMREAD_UNCHANGED)
            anim[(v, f)] = cv2.resize(im, (960, 540), interpolation=cv2.INTER_AREA)
    box = {}
    for v in views:
        m = np.zeros((540, 960), bool)
        for f in range(1, n + 1):
            m |= ref[(v, f)].max(2) > 110
            m |= anim[(v, f)][:, :, 3] > 0
        ys, xs = np.where(m)
        box[v] = (max(0, ys.min() - 15), min(540, ys.max() + 15), max(0, xs.min() - 15), min(960, xs.max() + 15))

    def held(f):
        k = [k for k in keys if k <= f]
        return k[-1] if k else None

    def cell(v, f):
        y0, y1, x0, x1 = box[v]
        r = ref[(v, f)][y0:y1, x0:x1].copy()
        im = anim[(v, f)][y0:y1, x0:x1]
        al = im[:, :, 3:] / 255.0
        an = (np.full(im.shape[:2] + (3,), 62) * (1 - al) + im[:, :, :3] * al).astype(np.uint8)
        s = a.height / r.shape[0]
        r = cv2.resize(r, (int(r.shape[1] * s), a.height), interpolation=cv2.INTER_AREA)
        an = cv2.resize(an, (int(an.shape[1] * s), a.height), interpolation=cv2.INTER_AREA)
        cv2.putText(r, f"REF {v}", (6, 20), 0, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(an, f"ANIM {v}", (6, 20), 0, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        if f in keys:
            cv2.putText(an, "KEY", (an.shape[1] - 52, 20), 0, 0.6, (60, 60, 255), 2, cv2.LINE_AA)
        elif held(f):
            cv2.putText(an, f"hold f{held(f)}", (an.shape[1] - 90, 20), 0, 0.45, (170, 170, 170), 1, cv2.LINE_AA)
        sep = np.full((a.height, 2, 3), 20, np.uint8)
        return np.hstack([r, sep, an])

    cells = {(v, f): cell(v, f) for v in views for f in range(1, n + 1)}
    roww = [sum(cells[(v, 1)].shape[1] for v in r) + 6 * (len(r) - 1) for r in layout]
    W = max(roww)
    grid = {}
    for f in range(1, n + 1):
        rows = []
        for r, rw in zip(layout, roww):
            parts = []
            for i, v in enumerate(r):
                if i:
                    parts.append(np.full((a.height, 6, 3), 30, np.uint8))
                parts.append(cells[(v, f)])
            row = np.hstack(parts)
            padl = (W - rw) // 2
            rows.append(np.pad(row, ((0, 0), (padl, W - rw - padl), (0, 0)), constant_values=30))
        g = np.vstack(rows)
        grid[f] = g[: g.shape[0] // 2 * 2, : g.shape[1] // 2 * 2]   # even size for yuv420p
    if a.page_webm:
        encode([grid[f] for f in range(1, n + 1)], a.page_webm, a.fps, gop=10)
        print(a.page_webm, f"{os.path.getsize(a.page_webm) / 1e3:.0f} kB", grid[1].shape[1], "x", grid[1].shape[0])
    if a.thumb:
        t = grid[a.thumb_frame]
        cv2.imwrite(a.thumb, cv2.resize(t, (192, int(t.shape[0] * 192 / t.shape[1]))), [cv2.IMWRITE_JPEG_QUALITY, 85])
    seq = []
    for lp in range(a.loops):
        for f in range(1, n + 1):
            bar = np.full((30, grid[f].shape[1], 3), 25, np.uint8)
            tag = "KEY" if f in keys else (f"hold f{held(f)}" if held(f) else "")
            cv2.putText(bar, f"{a.label}  f{f:3d}/{n}  {tag}", (8, 21), 0, 0.6, (230, 230, 230), 1, cv2.LINE_AA)
            seq.append(np.vstack([bar, grid[f]]))
    encode(seq, a.out, a.fps)
    print(a.out, f"{os.path.getsize(a.out) / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
