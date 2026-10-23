"""Refine each view's 2D camera offset (du, dv in reference pixels) so the model
silhouette lines up with the reference over several frames.

Updates cameras.json (center_px += du, ground/top += dv) and rig_np.json (camera pos)
in place, so later fits and Blender renders use the corrected cameras.

python tools/fit/refine_cams.py work/idle fit_basis.npy --frames 1,52,95 --range 30
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refmask  # noqa: E402
from silmodel import SilModel  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("basis", nargs="?")
    ap.add_argument("--frames", default="1,52,95")
    ap.add_argument("--range", type=int, default=30, help="search +- this many ref pixels")
    ap.add_argument("--scale", type=float, default=0.4)
    ap.add_argument("--zoom", default="1.0", help="camera scale factors to try, e.g. 0.96,0.98,1,1.02,1.04")
    a = ap.parse_args()

    m = SilModel(a.work)
    masks, meta = refmask.load(a.work)
    B = np.load(os.path.join(a.work, a.basis)) if a.basis else m.basis0
    frames = [int(x) - 1 for x in a.frames.split(",")]
    s = meta["scale"]
    shifts = {}
    Ps = []
    for f in frames:
        P, _ = m.skin(B[f])
        Ps.append(m.to_world(P))
    for v in masks:
        box = meta["boxes"][v]
        refs = [masks[v][f] > 0 for f in frames]
        k0 = m.cams[v]["k"]
        best = (-1, 0, 0, 1.0)
        R = int(a.range * s)
        for z in [float(t) for t in a.zoom.split(",")]:
            m.cams[v]["k"] = k0 * z
            mods = [m.raster(Pw, v, box, s) > 0 for Pw in Ps]
            for dy in range(-R, R + 1):
                for dx in range(-R, R + 1):
                    M = np.float32([[1, 0, dx], [0, 1, dy]])
                    tot = 0
                    for mm, r in zip(mods, refs):
                        sh = cv2.warpAffine(mm.astype(np.uint8), M, (mm.shape[1], mm.shape[0])) > 0
                        hh, ww = min(r.shape[0], sh.shape[0]), min(r.shape[1], sh.shape[1])
                        rr, ss = r[:hh, :ww], sh[:hh, :ww]
                        tot += (rr & ss).sum() / max(1, (rr | ss).sum())
                    if tot > best[0]:
                        best = (tot, dx, dy, z)
        m.cams[v]["k"] = k0
        mods = [m.raster(Pw, v, box, s) > 0 for Pw in Ps]
        du, dv = best[1] / s, best[2] / s
        base = sum(((r[:mm.shape[0], :mm.shape[1]] & mm[:r.shape[0], :r.shape[1]]).sum()
                    / max(1, (r[:mm.shape[0], :mm.shape[1]] | mm[:r.shape[0], :r.shape[1]]).sum()))
                   for mm, r in zip(mods, refs)) / len(frames)
        shifts[v] = (du, dv, best[3])
        print(f"{v}: shift du={du:+.1f}px dv={dv:+.1f}px zoom {best[3]:.3f}  IoU {base:.3f} -> {best[0] / len(frames):.3f}")

    cam_path = os.path.join(a.work, "cameras.json")
    cams = json.load(open(cam_path))
    meta_np = json.load(open(os.path.join(a.work, "rig_np.json")))
    for v, (du, dv, z) in shifts.items():
        c = meta_np["cameras"][v]
        if abs(z - 1) > 1e-9:
            # a zoom about the image centre: the ref pixel of any point moves away from the centre by 1/z.
            # Expressed in calibration terms: rescale the head-top/ground span and the offsets from the centre.
            W, H = c["W"], c["H"]
            cams[v]["center_px"] = W / 2 + (cams[v]["center_px"] - W / 2) / z
            cams[v]["ground_px"] = H / 2 + (cams[v]["ground_px"] - H / 2) / z
            cams[v]["top_px"] = H / 2 + (cams[v]["top_px"] - H / 2) / z
            c["k"] *= z
        cams[v]["center_px"] += du
        cams[v]["ground_px"] += dv
        cams[v]["top_px"] += dv
        c["pos"] = list(np.array(c["pos"]) - du * c["k"] * np.array(c["right"]) + dv * c["k"] * np.array(c["up"]))
    json.dump(cams, open(cam_path, "w"), indent=1)
    json.dump(meta_np, open(os.path.join(a.work, "rig_np.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
