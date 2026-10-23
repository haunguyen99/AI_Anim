"""Body-part motion: reference (optical flow) vs model (exact mesh vertices), per region.

For the model, the mesh vertices that project into a region at the first frame (front-most
third by depth, i.e. the visible surface) are followed through the animation; their median
projected displacement is the model's motion for that region. Needs `key_pose.py dump`.

python tools/motion_compare2.py WORK --regions regions.json [--views front,left] [--frames 1-31]
"""
import argparse, json, os, sys
import cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "fit"))
from keyanim import load, read_frame  # noqa: E402
from silmodel import SilModel  # noqa: E402


def ref_flow(imgs, box, px_cm):
    x0, y0, x1, y1 = box
    g0 = imgs[0][y0 - 40:y1 + 40, x0 - 40:x1 + 40]
    out = []
    for im in imgs:
        fl = cv2.calcOpticalFlowFarneback(g0, im[y0 - 40:y1 + 40, x0 - 40:x1 + 40], None, 0.5, 3, 21, 3, 5, 1.1, 0)[40:-40, 40:-40]
        out.append((np.median(fl[..., 0]) / px_cm, np.median(fl[..., 1]) / px_cm))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work"); ap.add_argument("--regions", required=True)
    ap.add_argument("--views", default=None); ap.add_argument("--frames", default=None)
    a = ap.parse_args()
    m = SilModel(a.work)
    n = m.basis0.shape[0]
    s, e = [int(x) for x in a.frames.split("-")] if a.frames else (1, n)
    frames = list(range(s, e + 1))
    regions = load(a.regions); views = a.views.split(",") if a.views else list(regions)
    refs = load(os.path.join(a.work, "refs.json"))
    Pw = [m.to_world(m.skin(m.basis0[f - 1])[0]) for f in frames]
    rows = []
    for v in views:
        c = m.cams[v]; px_cm = 1 / (c["k"] * 100)
        ref = [cv2.cvtColor(read_frame(refs["views"][v]["path"], f - 1), cv2.COLOR_BGR2GRAY) for f in frames]
        uv0, d0 = m.project(Pw[0], v)
        for name, (x0, y0, x1, y1) in regions[v].items():
            inside = (uv0[:, 0] > x0) & (uv0[:, 0] < x1) & (uv0[:, 1] > y0) & (uv0[:, 1] < y1)
            idx = np.flatnonzero(inside)
            if len(idx) < 3:
                print(f"{v} {name}: no model vertices in region"); continue
            idx = idx[d0[idx] <= np.percentile(d0[idx], 33)]          # visible surface
            mod = np.array([np.median(m.project(P, v)[0][idx] - uv0[idx], axis=0) / px_cm for P in Pw])
            rf = ref_flow(ref, (x0, y0, x1, y1), px_cm)
            rows.append((v, name, rf, mod))
            def pk(arr):
                i = int(np.argmax(np.abs(arr))); return f"{arr[i]:+5.1f}cm@f{frames[i]}"
            print(f"{v:5s} {name:8s} up: ref {pk(-rf[:, 1])} model {pk(-mod[:, 1])} | side: ref {pk(rf[:, 0])} model {pk(mod[:, 0])}"
                  f" | rms {np.sqrt(np.mean(np.sum((rf - mod) ** 2, 1))):.1f}cm")
    W, H = 300, 90; tiles = []
    for v, name, rf, mod in rows:
        img = np.full((H, W, 3), 30, np.uint8)
        sc = H / 2 / max(2.0, np.abs(np.r_[rf[:, 1], mod[:, 1]]).max())
        for arr, col in ((rf[:, 1], (255, 255, 255)), (mod[:, 1], (0, 160, 255))):
            pts = [(int(i * (W - 1) / (len(arr) - 1)), int(H / 2 + arr[i] * sc)) for i in range(len(arr))]
            cv2.polylines(img, [np.array(pts)], False, col, 2)
        cv2.putText(img, f"{v} {name}: up/down (white ref, orange model)", (4, 12), 0, 0.35, (200, 200, 200), 1)
        tiles.append(img)
    while len(tiles) % 2: tiles.append(np.zeros_like(tiles[0]))
    cv2.imwrite(os.path.join(a.work, "look", "motion_compare.png"), np.vstack([np.hstack(tiles[i:i + 2]) for i in range(0, len(tiles), 2)]))


if __name__ == "__main__":
    main()
