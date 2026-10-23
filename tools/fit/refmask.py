"""Reference silhouettes: character pixels vs a flat neutral background (+ grid lines).

Cached per work folder as refmasks.npz: masks[view] -> (frames, h, w) uint8 at the fit scale,
plus the crop box and scale used, so model masks can be rasterised on the same grid.
"""
import json
import os

import cv2
import numpy as np


def fit_box(cal, W, H):
    """Crop around the calibrated character, with headroom for props held overhead."""
    h = cal["ground_px"] - cal["top_px"]
    x0, x1 = cal["center_px"] - 0.95 * h, cal["center_px"] + 0.95 * h
    y0, y1 = cal["top_px"] - 0.6 * h, cal["ground_px"] + 0.06 * h
    return [max(0, int(x0)), max(0, int(y0)), min(W, int(x1)), min(H, int(y1))]


def segment(img, bg_spread=7, bg_lo=35, bg_hi=120):
    """Foreground = anything that is not a neutral mid-grey (background and grid lines)."""
    f = img.astype(np.int16)
    spread = f.max(2) - f.min(2)
    val = f.mean(2)
    bg = (spread < bg_spread) & (val > bg_lo) & (val < bg_hi)
    fg = (~bg).astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    # fill interior holes (dark-grey shading inside the character)
    h, w = fg.shape
    flood = fg.copy()
    cv2.floodFill(flood, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 255)
    fg = fg | (255 - flood)
    # keep the largest blobs only (drops stray noise)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg)
    if n > 1:
        keep = st[1:, cv2.CC_STAT_AREA] >= 0.02 * st[1:, cv2.CC_STAT_AREA].max()
        fg = np.isin(lab, 1 + np.flatnonzero(keep)).astype(np.uint8) * 255
    return fg


def build(work, scale=0.4, force=False):
    out = os.path.join(work, "refmasks.npz")
    if os.path.exists(out) and not force:
        return load(work)
    refs = json.load(open(os.path.join(work, "refs.json")))
    cams = json.load(open(os.path.join(work, "cameras.json")))
    data, meta = {}, {"scale": scale, "boxes": {}}
    for v, info in refs["views"].items():
        if v not in cams:
            continue
        box = fit_box(cams[v], info["width"], info["height"])
        meta["boxes"][v] = box
        cap = cv2.VideoCapture(info["path"])
        ms = []
        for _ in range(refs["frame_count"]):
            ok, img = cap.read()
            if not ok:
                break
            crop = img[box[1]:box[3], box[0]:box[2]]
            m = segment(crop)
            ms.append(cv2.resize(m, (int(round(crop.shape[1] * scale)), int(round(crop.shape[0] * scale))),
                                 interpolation=cv2.INTER_AREA))
        cap.release()
        data[v] = (np.array(ms) > 127).astype(np.uint8)
    np.savez_compressed(out, **data)
    json.dump(meta, open(os.path.join(work, "refmasks.json"), "w"))
    return load(work)


def load(work):
    d = np.load(os.path.join(work, "refmasks.npz"))
    meta = json.load(open(os.path.join(work, "refmasks.json")))
    return {k: d[k] for k in d.files}, meta


# ---------------------------------------------------------------- part labels (colour classes)
CLASSES = ["bg", "red", "dark", "gold", "purple", "white"]
PALETTE = np.array([[0, 0, 0], [40, 40, 220], [90, 70, 70], [40, 190, 230], [190, 60, 140], [255, 255, 255]], np.uint8)


def classify_hsv(hsv):
    """hsv: (..., 3) OpenCV HSV uint8 -> class ids (1..5). Shared by reference pixels and model colours."""
    h, s, v = [hsv[..., i].astype(np.int16) for i in range(3)]
    lab = np.full(h.shape, 1, np.uint8)                       # red by default
    lab[(s < 90) & (v < 160)] = 2                             # dark (weapon metal, gauntlet)
    lab[(s >= 90) & (h >= 9) & (h < 32)] = 3                  # gold
    lab[(s >= 70) & (h >= 110) & (h < 168)] = 4               # purple
    lab[(s < 60) & (v >= 160)] = 5                            # white
    return lab


def build_labels(work, force=False):
    out = os.path.join(work, "reflabels.npz")
    if os.path.exists(out) and not force:
        d = np.load(out)
        return {k: d[k] for k in d.files}
    refs = json.load(open(os.path.join(work, "refs.json")))
    meta = json.load(open(os.path.join(work, "refmasks.json")))
    scale = meta["scale"]
    data = {}
    for v, box in meta["boxes"].items():
        cap = cv2.VideoCapture(refs["views"][v]["path"])
        ls = []
        for _ in range(refs["frame_count"]):
            ok, img = cap.read()
            if not ok:
                break
            crop = img[box[1]:box[3], box[0]:box[2]]
            fg = segment(crop) > 0
            lab = classify_hsv(cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)) * fg
            lab = cv2.medianBlur(lab.astype(np.uint8), 5)
            ls.append(cv2.resize(lab, (int(round(crop.shape[1] * scale)), int(round(crop.shape[0] * scale))),
                                 interpolation=cv2.INTER_NEAREST))
        cap.release()
        data[v] = np.array(ls)
    np.savez_compressed(out, **data)
    return data
