"""Per-body-part motion measured on the REFERENCE videos (step 2 of docs/pipeline_v2.md).

Each region (box in reference pixels, per view) is tracked frame to frame with Lucas-Kanade
feature points (forward-backward checked, re-seeded when too few survive). Per frame we fit a
similarity transform to the surviving points and accumulate:
  dx, dy  (cm, image right / image up)   rot (deg, in image plane, + = counter-clockwise on screen)
  scale   (%, growth = part coming toward camera or turning its wide side to it)
Extremes (local peaks) of each curve are listed so the analysis can quote frames and amplitudes.

python tools/ref_timing.py WORK --regions REGIONS.json --cams CAMERAS.json [--height-m 2.0065]
Writes WORK/analysis/motion.json and WORK/analysis/motion_<view>.png.
"""
import argparse
import json
import os

import cv2
import numpy as np


def read_all(path):
    cap = cv2.VideoCapture(path)
    out = []
    while True:
        ok, im = cap.read()
        if not ok:
            break
        out.append(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY))
    cap.release()
    return out


def seed(img, box):
    x0, y0, x1, y1 = box
    m = np.zeros_like(img)
    m[y0:y1, x0:x1] = 255
    p = cv2.goodFeaturesToTrack(img, 80, 0.01, 4, mask=m, blockSize=5)
    return p if p is not None else np.zeros((0, 1, 2), np.float32)


def track(frames, box):
    lk = dict(winSize=(21, 21), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
    acc = np.eye(3)
    res = [(0.0, 0.0, 0.0, 1.0)]
    p0 = seed(frames[0], box)
    c0 = np.array([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2, 1.0])
    for i in range(1, len(frames)):
        a, b = frames[i - 1], frames[i]
        if len(p0) < 12:
            # re-seed inside the region's current position
            cx, cy = (acc @ c0)[:2]
            hw, hh = (box[2] - box[0]) / 2, (box[3] - box[1]) / 2
            p0 = seed(a, (int(cx - hw), int(cy - hh), int(cx + hw), int(cy + hh)))
        if len(p0) < 2:  # no trackable texture left in this region: hold it still for this frame
            p0 = np.zeros((0, 1, 2), np.float32)
            acc = acc
            res.append((float(acc[0, 2]), float(acc[1, 2]), 0.0, 1.0))
            continue
        p1, st, _ = cv2.calcOpticalFlowPyrLK(a, b, p0, None, **lk)
        pb, st2, _ = cv2.calcOpticalFlowPyrLK(b, a, p1, None, **lk)
        ok = (st[:, 0] == 1) & (st2[:, 0] == 1) & (np.linalg.norm(pb - p0, axis=2)[:, 0] < 0.5)
        M = None
        if ok.sum() >= 6:
            M, inl = cv2.estimateAffinePartial2D(p0[ok], p1[ok], method=cv2.RANSAC, ransacReprojThreshold=1.0)
        if M is None:
            M = np.array([[1, 0, 0], [0, 1, 0]], float)
        acc = np.vstack([M, [0, 0, 1]]) @ acc
        c = acc @ c0
        rot = np.degrees(np.arctan2(acc[1, 0], acc[0, 0]))
        sc = np.hypot(acc[0, 0], acc[1, 0])
        res.append((c[0] - c0[0], c[1] - c0[1], rot, sc))
        p0 = p1[ok].reshape(-1, 1, 2)
    return np.array(res)


def extremes(y, frames, min_amp):
    """Local maxima/minima whose prominence is at least min_amp; frames are 1-based."""
    out = []
    n = len(y)
    for i in range(n):
        lo, hi = max(0, i - 4), min(n, i + 5)
        win = y[lo:hi]
        if y[i] == win.max() or y[i] == win.min():
            kind = "max" if y[i] == win.max() else "min"
            if not out or out[-1][1] != kind:
                out.append([frames[i], kind, round(float(y[i]), 2)])
            elif (kind == "max" and y[i] > out[-1][2]) or (kind == "min" and y[i] < out[-1][2]):
                out[-1] = [frames[i], kind, round(float(y[i]), 2)]
    keep = []
    for e in out:
        if not keep or abs(e[2] - keep[-1][2]) >= min_amp:
            keep.append(e)
    return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--regions", required=True)
    ap.add_argument("--cams", required=True)
    ap.add_argument("--height-m", type=float, default=2.0065)
    ap.add_argument("--views", default=None)
    a = ap.parse_args()
    refs = json.load(open(os.path.join(a.work, "refs.json")))
    regions = json.load(open(a.regions))
    cams = json.load(open(a.cams))
    out_dir = os.path.join(a.work, "analysis")
    os.makedirs(out_dir, exist_ok=True)
    result = {}
    for v in (a.views.split(",") if a.views else list(regions)):
        frames = read_all(refs["views"][v]["path"])
        px_cm = (cams[v]["ground_px"] - cams[v]["top_px"]) / (a.height_m * 100)
        fr = list(range(1, len(frames) + 1))
        result[v] = {}
        plots = []
        for name, box in regions[v].items():
            r = track(frames, box)
            dx, dy = r[:, 0] / px_cm, -r[:, 1] / px_cm
            rot, sc = -r[:, 2], (r[:, 3] - 1) * 100       # image y is down: flip so + rot = CCW on screen
            rec = {"dx_cm": np.round(dx, 2).tolist(), "dy_cm": np.round(dy, 2).tolist(),
                   "rot_deg": np.round(rot, 2).tolist(), "scale_pct": np.round(sc, 2).tolist(),
                   "ext": {"dx": extremes(dx, fr, 0.6), "dy": extremes(dy, fr, 0.6),
                           "rot": extremes(rot, fr, 1.0), "scale": extremes(sc, fr, 1.0)}}
            result[v][name] = rec
            print(f"{v:5s} {name:12s} dy {dy.min():+5.1f}..{dy.max():+5.1f}cm  dx {dx.min():+5.1f}..{dx.max():+5.1f}cm"
                  f"  rot {rot.min():+5.1f}..{rot.max():+5.1f}  scale {sc.min():+5.1f}..{sc.max():+5.1f}%")
            W, H = 560, 110
            img = np.full((H, W, 3), 28, np.uint8)
            for gx in range(0, len(fr), 10):
                x = int(gx * (W - 1) / (len(fr) - 1))
                cv2.line(img, (x, 14), (x, H), (60, 60, 60), 1)
                cv2.putText(img, str(gx + 1), (x + 1, H - 3), 0, 0.3, (120, 120, 120), 1)
            cv2.line(img, (0, H // 2), (W, H // 2), (70, 70, 70), 1)
            curves = ((dy, (255, 255, 255), "dy"), (dx, (0, 200, 255), "dx"), (rot / 3, (120, 255, 120), "rot/3"),
                      (sc / 3, (255, 120, 200), "scale/3"))
            s = (H / 2 - 16) / max(2.0, max(np.abs(c).max() for c, _, _ in curves))
            for c, col, _ in curves:
                pts = np.array([(int(i * (W - 1) / (len(c) - 1)), int(H / 2 - c[i] * s)) for i in range(len(c))])
                cv2.polylines(img, [pts], False, col, 1, cv2.LINE_AA)
            cv2.putText(img, f"{v} {name}  [white dy  orange dx  green rot/3  pink scale/3]  1 unit={1 / s * (H / 2 - 16):.1f}",
                        (4, 11), 0, 0.33, (220, 220, 220), 1)
            plots.append(img)
        cv2.imwrite(os.path.join(out_dir, f"motion_{v}.png"), np.vstack(plots))
    json.dump(result, open(os.path.join(out_dir, "motion.json"), "w"))
    print("wrote", os.path.join(out_dir, "motion.json"))


if __name__ == "__main__":
    main()
