"""Opaque Cascadeur renders (<tag>_<view>_raw.png from casc_views.py) -> RGBA <tag>_<view>.png for tools/eye_side.py.

python tools/cascadeur/casc_mask.py DIR TAG [--views front,back,left,right,top]
Background is flat grey (~89) with thin grid lines (<=127); the model is lit grey above that.
Mask = brighter than the flat background, opened to drop the 1-3 px grid lines, holes filled.
The HUD text in the bottom-left corner is cleared.
"""
import argparse
import os

import cv2
import numpy as np


def mask(img, thr=96, open_px=5):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    m = (g > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((open_px, open_px), np.uint8))
    m[980:, :420] = 0                                  # "Frame: N / Cascadeur version" HUD
    ff = m.copy()
    cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 1)
    return (m | (1 - ff)) > 0                          # fill enclosed holes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("tag")
    ap.add_argument("--views", default="front,back,left,right,top")
    a = ap.parse_args()
    for v in a.views.split(","):
        src = os.path.join(a.dir, f"{a.tag}_{v}_raw.png")
        img = cv2.imread(src)
        m = mask(img)
        rgba = np.dstack([img, (m * 255).astype(np.uint8)])
        cv2.imwrite(os.path.join(a.dir, f"{a.tag}_{v}.png"), rgba)
        print(v, int(m.sum()))


if __name__ == "__main__":
    main()
