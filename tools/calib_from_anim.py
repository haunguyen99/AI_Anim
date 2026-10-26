"""Re-calibrate the reference cameras from a known animation of the same model (e.g. the original FBX).

Input: work/idle/original/orig_verts.json (world mesh points of the known animation at a few frames + current Ref_*
cameras, written from Blender) and work/idle/analysis/silref.npz (reference silhouettes: distance maps + contours).
For each view an orthographic camera is refined - orbit (yaw about world Z through the character), elevation (pitch),
roll, scale and image offset - by minimising the two-sided silhouette distance over all frames (pattern search).
Optionally a perspective camera (--persp) with a focal length.

python tools/calib_from_anim.py [--views front,left,back,right] [--persp]
Writes work/idle/original/calib.json and prints IoU-like scores before/after.
"""
import argparse
import json
import os

import numpy as np
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rot(axis, ang):
    c, s = np.cos(ang), np.sin(ang)
    x, y, z = axis
    return np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                     [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                     [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])


def make_cam(base, p, pivot):
    """base: 4x4 camera world matrix. p = [yaw, pitch, roll (deg), log_scale, du, dv (px), (focal_mm)]"""
    M = np.array(base["matrix_world"]); R0 = M[:3, :3]; C0 = M[:3, 3]
    Ry = rot((0, 0, 1), np.radians(p[0]))                 # orbit around the character (world up)
    C = pivot + Ry @ (C0 - pivot); R = Ry @ R0
    Rp = rot(R[:, 0], np.radians(p[1]))                   # orbit up/down about the camera's side axis
    C = pivot + Rp @ (C - pivot); R = Rp @ R
    R = R @ rot((0, 0, 1), np.radians(p[2]))              # roll about the view axis
    return R, C, base["ortho_scale"] * np.exp(-p[3]), p[4], p[5], (p[6] if len(p) > 6 else None)


def project(P, cam):
    R, C, osc, du, dv, foc = cam
    q = (P - C) @ R                      # camera coords: x right, y up, -z forward
    if foc is None:
        s = 1920 / osc
        return np.c_[960 + q[:, 0] * s + du, 540 - q[:, 1] * s + dv]
    f = foc / 36.0 * 1920                # px focal (36 mm sensor width)
    z = -q[:, 2]
    return np.c_[960 + f * q[:, 0] / z + du, 540 - f * q[:, 1] / z + dv]


def cost(Ps, frames, view, cam, sil):
    sc_ = float(sil["scale"]); box = sil[view + "_box"]; tot = []
    for f, P in zip(frames, Ps):
        uv = project(P, cam)
        dt = sil[view + "_dt"][f - 1].astype(np.float32)
        iu = np.clip(((uv[:, 0] - box[0]) * sc_).astype(int), 0, dt.shape[1] - 1)
        iv = np.clip(((uv[:, 1] - box[1]) * sc_).astype(int), 0, dt.shape[0] - 1)
        out = np.minimum(dt[iv, iu], 40.0).mean()
        # reference contour points -> distance to the nearest projected model point (distance transform of the points)
        img = np.full(dt.shape, 255, np.uint8)
        img[iv, iu] = 0
        dm = cv2.distanceTransform(img, cv2.DIST_L2, 3) / sc_
        ct = sil[view + "_ct"][f - 1]
        cu = np.clip(((ct[:, 0] - box[0]) * sc_).astype(int), 0, dt.shape[1] - 1)
        cv_ = np.clip(((ct[:, 1] - box[1]) * sc_).astype(int), 0, dt.shape[0] - 1)
        tot.append(out + np.minimum(dm[cv_, cu], 40.0).mean())
    return float(np.mean(tot))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--views", default="front,left,back,right")
    ap.add_argument("--persp", action="store_true")
    a = ap.parse_args()
    d = json.load(open(os.path.join(ROOT, "work", "idle", "original", "orig_verts.json")))
    sil = np.load(os.path.join(ROOT, "work", "idle", "analysis", "silref.npz"))
    frames = [int(k) for k in d["verts"]]
    Ps = [np.array(d["verts"][str(f)]) for f in frames]
    pivot = np.array([0.0, 0.0, 1.0])
    res = {}
    for v in a.views.split(","):
        base = d["cams"][v]
        p = np.array([0, 0, 0, 0, 0, 0] + ([50.0] if a.persp else []), float)
        steps = np.array([8, 4, 2, 0.04, 8, 8] + ([20.0] if a.persp else []), float)
        best = cost(Ps, frames, v, make_cam(base, p, pivot), sil)
        start = best
        for _ in range(7):
            improved = True
            while improved:
                improved = False
                for i in range(len(p)):
                    for sgn in (1, -1):
                        q = p.copy(); q[i] += sgn * steps[i]
                        if a.persp and i == 6 and q[i] < 10:
                            continue
                        c = cost(Ps, frames, v, make_cam(base, q, pivot), sil)
                        if c < best - 1e-4:
                            p, best, improved = q, c, True
            steps /= 2
        res[v] = {"params": p.round(3).tolist(), "cost_before": round(start, 2), "cost_after": round(best, 2)}
        print(f"{v:5s} cost {start:6.2f} -> {best:6.2f} px   yaw {p[0]:+6.1f}  pitch {p[1]:+6.1f}  roll {p[2]:+5.1f}"
              f"  scale x{np.exp(p[3]):.3f}  du {p[4]:+6.1f}  dv {p[5]:+6.1f}" + (f"  focal {p[6]:.0f}mm" if a.persp else ""))
    json.dump(res, open(os.path.join(ROOT, "work", "idle", "original", "calib.json" if not a.persp else "calib_persp.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
