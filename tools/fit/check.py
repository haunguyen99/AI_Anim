"""Visual + numeric check of model silhouettes vs reference masks.
python tools/fit/check.py WORK [basis.npy] --frames 1,52,95 --out look/sil_check.png"""
import argparse, os, sys, time
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from silmodel import SilModel
import refmask

def compare(m, masks, meta, basis, f, views):
    P, _ = m.skin(basis); Pw = m.to_world(P); tiles, ious = [], {}
    for v in views:
        r = masks[v][f] > 0; box = meta['boxes'][v]
        mm = m.raster(Pw, v, box, meta['scale']) > 0
        hh, ww = min(r.shape[0], mm.shape[0]), min(r.shape[1], mm.shape[1]); r, mm = r[:hh, :ww], mm[:hh, :ww]
        iou = (r & mm).sum() / max(1, (r | mm).sum()); ious[v] = iou
        img = np.zeros(r.shape + (3,), np.uint8); img[r & mm] = (200, 200, 200); img[r & ~mm] = (60, 60, 255); img[~r & mm] = (255, 160, 40)
        cv2.putText(img, f'{v} f{f+1} IoU {iou:.3f}', (4, 14), 0, 0.45, (255, 255, 255), 1); tiles.append(img)
    return tiles, ious

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("work"); ap.add_argument("basis", nargs="?")
    ap.add_argument("--frames", default="1,52,95"); ap.add_argument("--out", default="look/sil_check.png")
    a = ap.parse_args()
    m = SilModel(a.work); masks, meta = refmask.load(a.work)
    B = np.load(a.basis) if a.basis else m.basis0
    views = list(masks); rows = []; allv = []
    for f in [int(x) - 1 for x in a.frames.split(",")]:
        tiles, ious = compare(m, masks, meta, B[f], f, views); allv += list(ious.values())
        hmax = max(t.shape[0] for t in tiles); rows.append(np.hstack([np.pad(t, ((0, hmax - t.shape[0]), (0, 4), (0, 0))) for t in tiles]))
    wmax = max(r.shape[1] for r in rows)
    cv2.imwrite(os.path.join(a.work, a.out), np.vstack([np.pad(r, ((0, 0), (0, wmax - r.shape[1]), (0, 0))) for r in rows]))
    print(f"mean IoU {np.mean(allv):.3f}")
