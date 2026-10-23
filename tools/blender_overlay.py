"""Overlay renders of the LIVE Blender scene (made through the Ref_* cameras) on the reference frames.

Blender side (run via MCP execute_blender_code):  exec(open(r"E:/AI Animation/tools/blender/live_render.py").read())
then:  python tools/blender_overlay.py --frames 1,17 [--views front,left] [--refs work/idle]
Writes work/blender/look/overlay_<frame>.png  (per view: reference+model outline | model).
"""
import argparse
import json
import os

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--views", default="front,left,back,right")
    ap.add_argument("--refs", default=os.path.join(ROOT, "work", "idle"))
    ap.add_argument("--cams", default=os.path.join(ROOT, "work", "idle_breath", "cameras.json"))
    ap.add_argument("--height", type=int, default=420)
    a = ap.parse_args()
    refs = json.load(open(os.path.join(a.refs, "refs.json")))
    cams = json.load(open(a.cams))
    out_dir = os.path.join(ROOT, "work", "blender", "look")
    for fr in [int(x) for x in a.frames.split(",")]:
        tiles = []
        for v in a.views.split(","):
            info = refs["views"][v]
            cap = cv2.VideoCapture(info["path"])    # read sequentially: seeking in the .mov files is not frame-exact
            for _ in range(fr):
                ok, ref = cap.read()
            cap.release()
            ren = cv2.imread(os.path.join(out_dir, f"r_{v}_{fr:04d}.png"), cv2.IMREAD_UNCHANGED)
            ren = cv2.resize(ren, (info["width"], info["height"]))
            alpha = ren[:, :, 3]
            over = ref.copy()
            cnts, _ = cv2.findContours((alpha > 100).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(over, cnts, -1, (255, 255, 0), 2)
            am = (alpha / 255.0)[:, :, None]
            solid = (np.full_like(ref, 70) * (1 - am) + ren[:, :, :3] * am).astype(np.uint8)
            c = cams[v]; h = c["ground_px"] - c["top_px"]
            x0, x1 = int(c["center_px"] - 0.9 * h), int(c["center_px"] + 0.9 * h)
            y0, y1 = int(c["top_px"] - 0.5 * h), int(c["ground_px"] + 0.1 * h)
            x0, y0 = max(0, x0), max(0, y0)
            pair = []
            for img in (over, solid):
                crop = img[y0:y1, x0:x1]
                s = a.height / crop.shape[0]
                crop = cv2.resize(crop, (int(crop.shape[1] * s), a.height))
                cv2.putText(crop, f"{v} f{fr}", (6, a.height - 8), 0, 0.55, (255, 255, 255), 2)
                pair.append(crop)
            tiles.append(np.hstack(pair))
        w = max(t.shape[1] for t in tiles)
        tiles = [np.pad(t, ((0, 0), (0, w - t.shape[1]), (0, 0))) for t in tiles]
        rows = [np.hstack(tiles[i:i + 2]) if i + 1 < len(tiles) else np.hstack([tiles[i], np.zeros_like(tiles[i])])
                for i in range(0, len(tiles), 2)]
        p = os.path.join(out_dir, f"overlay_{fr:04d}.png")
        cv2.imwrite(p, np.vstack(rows))
        print(p)


if __name__ == "__main__":
    main()
