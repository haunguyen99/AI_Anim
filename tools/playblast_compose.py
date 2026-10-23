"""Compose a review video: reference | Blender render for every view, every frame (docs/pipeline_v2.md step 4/6).

Blender side first: FRAMES = list(range(1, N+1)); VIEWS = [...]; exec(live_render.py)  -> work/blender/look/r_<view>_<frame>.png
python tools/playblast_compose.py --out work/idle/review_blocking.mp4 [--label "BLOCKING (stepped)"] [--keys 1,9,17]
"""
import argparse
import json
import os

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--refs", default=os.path.join(ROOT, "work", "idle"))
    ap.add_argument("--cams", default=os.path.join(ROOT, "work", "idle_breath", "cameras.json"))
    ap.add_argument("--views", default="front,left,back,right")
    ap.add_argument("--height", type=int, default=300)
    ap.add_argument("--label", default="")
    ap.add_argument("--keys", default="")
    a = ap.parse_args()
    refs = json.load(open(os.path.join(a.refs, "refs.json")))
    cams = json.load(open(a.cams))
    keys = {int(k) for k in a.keys.split(",") if k}
    look = os.path.join(ROOT, "work", "blender", "look")
    views = a.views.split(",")
    caps = {v: cv2.VideoCapture(refs["views"][v]["path"]) for v in views}
    n = refs["frame_count"]
    writer = None
    for f in range(1, n + 1):
        tiles = []
        for v in views:
            ok, ref = caps[v].read()
            ren = cv2.imread(os.path.join(look, f"r_{v}_{f:04d}.png"), cv2.IMREAD_UNCHANGED)
            ren = cv2.resize(ren, (ref.shape[1], ref.shape[0]))
            am = (ren[:, :, 3] / 255.0)[:, :, None]
            solid = (np.full_like(ref, 90) * (1 - am) + ren[:, :, :3] * am).astype(np.uint8)
            c = cams[v]; h = c["ground_px"] - c["top_px"]
            x0, x1 = int(c["center_px"] - 0.9 * h), int(c["center_px"] + 0.9 * h)
            y0, y1 = int(c["top_px"] - 0.55 * h), int(c["ground_px"] + 0.08 * h)
            x0, y0 = max(0, x0), max(0, y0)
            pair = []
            for img, tag in ((ref, "REF"), (solid, "ANIM")):
                crop = img[y0:y1, x0:x1]
                s = a.height / crop.shape[0]
                crop = cv2.resize(crop, (int(crop.shape[1] * s), a.height), interpolation=cv2.INTER_AREA)
                cv2.putText(crop, f"{tag} {v}", (6, 18), 0, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                pair.append(crop)
            tiles.append(np.hstack(pair))
        w = max(t.shape[1] for t in tiles)
        tiles = [np.pad(t, ((0, 0), (0, w - t.shape[1]), (0, 0))) for t in tiles]
        rows = [np.hstack(tiles[i:i + 2]) for i in range(0, len(tiles), 2)]
        frame = np.vstack(rows)
        bar = np.full((28, frame.shape[1], 3), 25, np.uint8)
        txt = f"f{f:3d}/{n}  {a.label}" + ("   [KEY]" if f in keys else "")
        cv2.putText(bar, txt, (8, 20), 0, 0.6, (0, 220, 255) if f in keys else (230, 230, 230), 1, cv2.LINE_AA)
        frame = np.vstack([bar, frame])
        if writer is None:
            writer = cv2.VideoWriter(a.out, cv2.VideoWriter_fourcc(*"mp4v"), refs["fps"], (frame.shape[1], frame.shape[0]))
        writer.write(frame)
    writer.release()
    print(a.out)


if __name__ == "__main__":
    main()
