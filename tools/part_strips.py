"""Time strips of one body part in every view (step 2 of docs/pipeline_v2.md).

Crops the same box from each view at every STEP frames and lays them out as rows (one per view),
with frame numbers, so a part can be read over time from all sides at once.

python tools/part_strips.py WORK --name head --box front=1000,440,1140,620 --box left=740,440,900,620 \
       [--frames 1-133] [--step 4] [--tile 150] [--cols 17]
Writes WORK/analysis/strip_<name>[_<n>].png (split into chunks of COLS tiles per row).
"""
import argparse
import json
import os

import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--name", required=True)
    ap.add_argument("--box", action="append", required=True, help="view=x0,y0,x1,y1")
    ap.add_argument("--frames", default=None)
    ap.add_argument("--step", type=int, default=4)
    ap.add_argument("--tile", type=int, default=150, help="tile height in px")
    ap.add_argument("--cols", type=int, default=12)
    ap.add_argument("--marks", default="", help="frames to outline in red, e.g. 1,20,30")
    a = ap.parse_args()
    refs = json.load(open(os.path.join(a.work, "refs.json")))
    n = refs["frame_count"]
    s, e = [int(x) for x in a.frames.split("-")] if a.frames else (1, n)
    want = list(range(s, e + 1, a.step))
    if want[-1] != e:
        want.append(e)
    marks = {int(x) for x in a.marks.split(",") if x}
    boxes = [(b.split("=")[0], [int(v) for v in b.split("=")[1].split(",")]) for b in a.box]
    rows = {}
    for v, (x0, y0, x1, y1) in boxes:
        cap = cv2.VideoCapture(refs["views"][v]["path"])
        tiles, f = [], 0
        while True:
            ok, im = cap.read()
            if not ok:
                break
            f += 1
            if f in want:
                t = im[y0:y1, x0:x1]
                sc = a.tile / t.shape[0]
                t = cv2.resize(t, (int(t.shape[1] * sc), a.tile), interpolation=cv2.INTER_AREA)
                # light grid every 20 ref px to read small motion
                for gy in range(0, y1 - y0, 20):
                    yy = int(gy * sc)
                    cv2.line(t, (0, yy), (6, yy), (0, 255, 255), 1)
                cv2.putText(t, f"{v[0].upper()} f{f}", (3, a.tile - 5), 0, 0.42, (255, 255, 255), 2)
                cv2.putText(t, f"{v[0].upper()} f{f}", (3, a.tile - 5), 0, 0.42, (0, 0, 0), 1)
                if f in marks:
                    cv2.rectangle(t, (0, 0), (t.shape[1] - 1, a.tile - 1), (0, 0, 255), 2)
                tiles.append(t)
        cap.release()
        rows[v] = tiles
    out_dir = os.path.join(a.work, "analysis")
    os.makedirs(out_dir, exist_ok=True)
    chunks = range(0, len(want), a.cols)
    for ci, c0 in enumerate(chunks):
        lines = []
        for v, _ in boxes:
            seg = rows[v][c0:c0 + a.cols]
            line = np.hstack(seg)
            lines.append(line)
        w = max(l.shape[1] for l in lines)
        lines = [np.pad(l, ((0, 2), (0, w - l.shape[1]), (0, 0))) for l in lines]
        suffix = f"_{ci + 1}" if len(chunks) > 1 else ""
        p = os.path.join(out_dir, f"strip_{a.name}{suffix}.png")
        cv2.imwrite(p, np.vstack(lines))
        print(p)


if __name__ == "__main__":
    main()
