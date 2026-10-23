"""Fit ONE prop-in-hand offset for the whole clip (a held prop doesn't slide in the hand).

Poses stay fixed; the 6 offset params (rotation deg, translation m, in prop-local axes) are
optimised over a sample of frames. Saves grip.json, which fitpose --fixed-grip then uses.

python tools/fit/fit_grip.py work/idle [--frames 1,17,33,...] [--prop Weapon --holder Wrist_L]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fitpose import Fitter  # noqa: E402
from silmodel import rotvec_to_mat  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--frames", default=None)
    ap.add_argument("--prop", default="Weapon")
    ap.add_argument("--holder", default="Wrist_L")
    ap.add_argument("--scale", type=float, default=0.3)
    a = ap.parse_args()

    F = Fitter(a.work, ["front", "back", "left", "right"], a.scale, fixed_grip=True)
    m = F.m
    N = m.basis0.shape[0]
    frames = [int(x) - 1 for x in a.frames.split(",")] if a.frames else list(range(0, N, max(1, N // 10)))
    refs = {f: {v: F.ref(v, f) for v in F.views} for f in frames}
    base = F.fixed_off[a.prop]
    pi, hi = m.idx[a.prop], m.idx[a.holder]

    def offset(d):
        D = np.eye(4)
        D[:3, :3] = rotvec_to_mat(np.radians(d[:3]))
        D[:3, 3] = d[3:] / F.unit
        return base @ D

    def loss(d):
        off = offset(d)
        tot = 0
        for f in frames:
            F.attach_for = lambda b0, x, off=off: {pi: (hi, off)}
            tot += F.loss(m.basis0[f], np.zeros(len(F.params)), refs[f])[0]
        return tot / len(frames)

    d = np.zeros(6)
    best = loss(d)
    print(f"start loss {best:.4f}")
    for st_r, st_t in ((10, 0.05), (4, 0.02), (1.5, 0.008), (0.5, 0.003)):
        improved = True
        while improved:
            improved = False
            for i in range(6):
                for sgn in (1, -1):
                    e = d.copy()
                    e[i] += sgn * (st_r if i < 3 else st_t)
                    l = loss(e)
                    if l < best - 1e-5:
                        d, best, improved = e, l, True
                        break
        print(f"step {st_r} deg: loss {best:.4f}  delta rot {np.round(d[:3], 1)} deg, trans {np.round(d[3:], 3)} m")
    json.dump({a.prop: {"holder": a.holder, "offset": offset(d).tolist()}},
              open(os.path.join(a.work, "grip.json"), "w"), indent=1)
    print("saved grip.json")


if __name__ == "__main__":
    main()
