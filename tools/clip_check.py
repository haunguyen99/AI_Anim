"""Interpenetration check between a prop and the body (per frame or one frame).
python tools/clip_check.py WORK [--prop Weapon] [--bones Shoulder_L,Elbow_L,Wrist_L] [--frames 1,16,31]
Reports how many body vertices (skinned mainly to the given bones) lie inside the prop's
convex-ish cross-section (radius profile along its bone axis)."""
import argparse, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fit"))
from silmodel import SilModel

ap = argparse.ArgumentParser(); ap.add_argument("work"); ap.add_argument("--prop", default="Weapon")
ap.add_argument("--bones", default="Shoulder_L,Elbow_L,Wrist_L,Head_M,Neck_M,Chest_M,Scapula_L")
ap.add_argument("--frames", default="1"); a = ap.parse_args()
m = SilModel(a.work)
for f in [int(x) for x in a.frames.split(",")]:
    P, M = m.skin(m.basis0[f - 1]); Pw = m.to_world(P)
    w = m.idx[a.prop]; W = m.to_world(M[w, :3, 3][None])[0]
    ax = m.arm_mw[:3, :3] @ M[w, :3, 1]; ax /= np.linalg.norm(ax)
    wv = Pw[m.part == 1]; wt = (wv - W) @ ax; wr = np.linalg.norm((wv - W) - np.outer(wt, ax), axis=1)
    bins = np.linspace(wt.min(), wt.max(), 40); prof = np.zeros(len(bins) - 1)
    for i in range(len(prof)):
        s = (wt >= bins[i]) & (wt < bins[i + 1]); prof[i] = np.percentile(wr[s], 60) if s.sum() > 3 else 0
    out = []
    for b in a.bones.split(","):
        sel = (m.wi[:, 0] == m.idx[b]) & (m.part == 0)
        bv = Pw[sel]; t = (bv - W) @ ax; r = np.linalg.norm((bv - W) - np.outer(t, ax), axis=1)
        bi = np.clip(np.searchsorted(bins, t) - 1, 0, len(prof) - 1)
        inside = (t > bins[0]) & (t < bins[-1]) & (r < prof[bi])
        depth = (prof[bi] - r)[inside]
        out.append(f"{b}: {inside.sum()}/{len(bv)}" + (f" (max {depth.max()*100:.0f}cm)" if inside.any() else ""))
    print(f"frame {f}: " + "  ".join(out))
