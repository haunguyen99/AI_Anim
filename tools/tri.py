"""Triangulate reference pixels from two (or more) orthographic views into a 3D point,
and print where the model's joints currently project — the animator's "match the
front and side views" step, done with numbers.

  python tools/tri.py WORK front=1215,440 left=962,462        -> world xyz (Blender, metres)
  python tools/tri.py WORK --joints Shoulder_L,Elbow_L,Wrist_L --frame 1   (needs key_pose dump)
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fit"))


def cams(work):
    return json.load(open(os.path.join(work, "rig_np.json")))["cameras"]


def triangulate(work, obs):
    """obs: {view: (u, v)} -> least-squares world point. Each ortho view constrains two axes."""
    C = cams(work)
    A, b = [], []
    for v, (u, w) in obs.items():
        c = C[v]
        pos, r, up, k = np.array(c["pos"]), np.array(c["right"]), np.array(c["up"]), c["k"]
        # (p - pos).r = (u - W/2) k ;  (p - pos).up = (H/2 - w) k
        A += [r, up]
        b += [pos @ r + (u - c["W"] / 2) * k, pos @ up + (c["H"] / 2 - w) * k]
    p, res, *_ = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)
    return p, (np.sqrt(res[0] / len(b)) if len(res) else 0.0)


def main():
    work = sys.argv[1]
    args = sys.argv[2:]
    if "--joints" in args:
        from silmodel import SilModel
        m = SilModel(work)
        f = int(args[args.index("--frame") + 1]) if "--frame" in args else 1
        names = args[args.index("--joints") + 1].split(",")
        _, M = m.skin(m.basis0[f - 1])
        for n in names:
            pw = m.to_world(M[m.idx[n], :3, 3][None])[0]
            s = "  ".join(f"{v}=({m.project(pw[None], v)[0][0][0]:.0f},{m.project(pw[None], v)[0][0][1]:.0f})" for v in m.cams)
            print(f"{n:12s} world {np.round(pw, 3)}  {s}")
        return
    obs = {a.split("=")[0]: tuple(float(x) for x in a.split("=")[1].split(",")) for a in args}
    p, err = triangulate(work, obs)
    print(f"world {np.round(p, 4).tolist()}  (fit error {err * 100:.1f} cm)")


if __name__ == "__main__":
    main()
