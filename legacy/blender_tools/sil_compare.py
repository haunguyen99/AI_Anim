"""IoU and overlay between rendered silhouettes (legacy/blender/sil_render.py) and the reference frames.

python legacy/blender_tools/sil_compare.py WORK RENDERDIR FRAMES OUT.png [--ref-frames F,...]
WORK/refs.json maps views to videos; camera Ref_<view> pairs with view <view> ("top" via WORK/refs.json "views" too).
Overlay colours: white = both, red = ref only (anim missing), cyan = anim only (anim extra).
--ref-frames: compare anim frame i with a different ref frame (default: same numbers).
"""
import argparse
import json
import os

import cv2
import numpy as np


def ref_frames(path, wanted):
    cap, i, out = cv2.VideoCapture(path), 0, {}
    while len(out) < len(wanted):
        ok, f = cap.read()
        if not ok:
            break
        i += 1
        if i in wanted:
            out[i] = f
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("renders")
    ap.add_argument("frames")
    ap.add_argument("out")
    ap.add_argument("--ref-frames")
    ap.add_argument("--thr", type=int, default=110)
    a = ap.parse_args()
    frames = [int(f) for f in a.frames.split(",")]
    rfr = [int(f) for f in a.ref_frames.split(",")] if a.ref_frames else frames
    views = json.load(open(os.path.join(a.work, "refs.json")))["views"]
    rows, report = [], {}
    for view, info in views.items():
        refs = ref_frames(info["path"], set(rfr))
        tiles = []
        for f, rf in zip(frames, rfr):
            rp = os.path.join(a.renders, f"Ref_{view}_{f:03d}.png")
            if not os.path.exists(rp) or rf not in refs:
                continue
            am = cv2.imread(rp, 0) > 127
            rm = cv2.morphologyEx((refs[rf].max(2) > a.thr).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)) > 0  # fill shading lines
            iou = (am & rm).sum() / max((am | rm).sum(), 1)
            report[f"{view}_{f}"] = round(float(iou), 3)
            ov = np.zeros(am.shape + (3,), np.uint8)
            ov[am & rm] = (255, 255, 255)
            ov[rm & ~am] = (0, 0, 255)
            ov[am & ~rm] = (255, 255, 0)
            ys, xs = np.nonzero(am | rm)
            y0, y1 = max(ys.min() - 20, 0), min(ys.max() + 20, am.shape[0])
            x0, x1 = max(xs.min() - 20, 0), min(xs.max() + 20, am.shape[1])
            t = cv2.resize(ov[y0:y1, x0:x1], (int((x1 - x0) * 360 / (y1 - y0)), 360))
            cv2.putText(t, f"{view} f{f} IoU {iou:.2f}", (5, 22), 0, 0.6, (0, 255, 0), 2)
            tiles.append(t)
        if tiles:
            rows.append(np.hstack(tiles))
    w = max(r.shape[1] for r in rows)
    cv2.imwrite(a.out, np.vstack([np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0))) for r in rows]))
    print(json.dumps(report))


if __name__ == "__main__":
    main()
