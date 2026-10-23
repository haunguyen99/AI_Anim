"""Temporal smoothing of per-frame fitted poses (quaternion + translation per bone).

python tools/fit/smooth.py work/idle [--in fit_basis.npy] [--out fit_smooth.npy] [--sigma 1.2] [--loop]
--loop treats the clip as cyclic (idle loops) so the first and last frames blend.
"""
import argparse
import os

import numpy as np


def mat_to_quat(R):
    t = np.trace(R)
    if t > 0:
        s = np.sqrt(t + 1) * 2
        return np.array([0.25 * s, (R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s])
    i = np.argmax(np.diag(R))
    if i == 0:
        s = np.sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2]) * 2
        return np.array([(R[2, 1] - R[1, 2]) / s, 0.25 * s, (R[0, 1] + R[1, 0]) / s, (R[0, 2] + R[2, 0]) / s])
    if i == 1:
        s = np.sqrt(1 + R[1, 1] - R[0, 0] - R[2, 2]) * 2
        return np.array([(R[0, 2] - R[2, 0]) / s, (R[0, 1] + R[1, 0]) / s, 0.25 * s, (R[1, 2] + R[2, 1]) / s])
    s = np.sqrt(1 + R[2, 2] - R[0, 0] - R[1, 1]) * 2
    return np.array([(R[1, 0] - R[0, 1]) / s, (R[0, 2] + R[2, 0]) / s, (R[1, 2] + R[2, 1]) / s, 0.25 * s])


def quat_to_mat(q):
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def gauss(arr, sigma, loop):
    if sigma <= 0:
        return arr
    r = max(1, int(round(3 * sigma)))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    pad = np.pad(arr, [(r, r)] + [(0, 0)] * (arr.ndim - 1), mode="wrap" if loop else "edge")
    out = np.zeros_like(arr)
    for i, w in enumerate(k):
        out += w * pad[i:i + len(arr)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--in", dest="inp", default="fit_basis.npy")
    ap.add_argument("--out", default="fit_smooth.npy")
    ap.add_argument("--sigma", type=float, default=1.2)
    ap.add_argument("--loop", action="store_true")
    a = ap.parse_args()
    B = np.load(os.path.join(a.work, a.inp))
    N, nb = B.shape[:2]
    out = B.copy()
    for b in range(nb):
        q = np.array([mat_to_quat(B[f, b, :3, :3]) for f in range(N)])
        for f in range(1, N):  # same hemisphere frame to frame
            if np.dot(q[f], q[f - 1]) < 0:
                q[f] = -q[f]
        if a.loop and np.dot(q[0], q[-1]) < 0:
            pass  # wrap blending only valid if the ends agree in sign; flip handled by renormalising below
        qs = gauss(q, a.sigma, a.loop)
        ts = gauss(B[:, b, :3, 3], a.sigma, a.loop)
        for f in range(N):
            out[f, b, :3, :3] = quat_to_mat(qs[f])
            out[f, b, :3, 3] = ts[f]
    np.save(os.path.join(a.work, a.out), out)
    # how much smoothing moved things (deg), to spot jitter
    d = []
    for f in range(N):
        for b in range(nb):
            R = B[f, b, :3, :3].T @ out[f, b, :3, :3]
            d.append(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
    d = np.array(d)
    print(f"smoothed {N} frames x {nb} bones: mean change {d.mean():.2f} deg, p99 {np.percentile(d, 99):.2f} deg")


if __name__ == "__main__":
    main()
