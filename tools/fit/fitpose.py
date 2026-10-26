"""Per-frame pose fitting by silhouette matching (analysis-by-synthesis).

For every frame: start from the current animation (eye-keyed, interpolated) plus the
previous frame's corrections, then adjust bone rotations (and root/prop translation)
so the rasterised model silhouette matches the reference silhouettes (IoU), group by
group with a pattern search. Writes fit_basis.npy (frames, bones, 4, 4) of local
pose matrices, which `key_pose.py bake` turns into one key per frame.

python tools/fit/fitpose.py work/idle [--frames 1-133] [--views front,left] [--scale 0.25]
"""
import argparse
import json
import os
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refmask  # noqa: E402
from silmodel import SilModel, rotvec_to_mat  # noqa: E402

# (group name, [(bone, kind)]) kind: "r" rotation (deg), "t" translation (armature units)
DEFAULT_GROUPS = [
    ("torso", [("Root_M", "t"), ("Root_M", "r"), ("Spine1_M", "r"), ("Chest_M", "r")]),
    ("head", [("Neck_M", "r"), ("Head_M", "r")]),
    ("arm_L", [("Scapula_L", "r"), ("Shoulder_L", "r"), ("Elbow_L", "r"), ("Wrist_L", "r")]),
    ("weapon", [("Weapon", "r"), ("Weapon", "t")]),
    ("arm_R", [("Scapula_R", "r"), ("Shoulder_R", "r"), ("Elbow_R", "r"), ("Wrist_R", "r")]),
    ("legs", [("Hip_L", "r"), ("Knee_L", "r"), ("Ankle_L", "r"), ("Hip_R", "r"), ("Knee_R", "r"), ("Ankle_R", "r")]),
]


class Fitter:
    def __init__(self, work, views, scale, groups=DEFAULT_GROUPS, reg=0.0005, attach=(("Weapon", "Wrist_L"),),
                 fixed_grip=False, temporal=0.0):
        self.m = SilModel(work)
        self.temporal = temporal
        self.x_prev = None
        self.masks, self.meta = refmask.load(work)
        self.labels = refmask.build_labels(work)
        self.views, self.scale, self.reg = views, scale, reg
        if fixed_grip:  # a held prop does not slide in the hand: one offset for the whole clip
            groups = [(g, items) for g, items in groups if g != "weapon"]
        self.groups = [(g, [(b, k) for b, k in items if b in self.m.idx]) for g, items in groups]
        self.params = [(b, k, ax) for _, items in self.groups for b, k in items for ax in range(3)]
        self.pidx = {p: i for i, p in enumerate(self.params)}
        self.boxes = {v: self.meta["boxes"][v] for v in views}
        self.attach_names = [(p, h) for p, h in attach if p in self.m.idx and h in self.m.idx]
        self.fixed_off = {}
        if fixed_grip:
            from smooth import mat_to_quat, quat_to_mat
            for prop, holder in self.attach_names:
                offs = np.array([self.m.attach_offset(B, prop, holder) for B in self.m.basis0])
                q = np.array([mat_to_quat(o[:3, :3]) for o in offs])
                q *= np.sign(q @ q[0])[:, None]
                O = np.eye(4)
                O[:3, :3] = quat_to_mat(q.mean(0))
                O[:3, 3] = np.median(offs[:, :3, 3], axis=0)
                self.fixed_off[prop] = O
            gp = os.path.join(work, "grip.json")  # a clip-wide fitted offset wins over the average
            if os.path.exists(gp):
                for prop, g in json.load(open(gp)).items():
                    if prop in self.fixed_off:
                        self.fixed_off[prop] = np.array(g["offset"])
        self.unit = abs(np.linalg.det(self.m.arm_mw[:3, :3])) ** (1 / 3)  # metres per armature unit

    def ref(self, v, f):
        r = self.labels[v][f]
        box = self.boxes[v]
        h, w = int(round((box[3] - box[1]) * self.scale)), int(round((box[2] - box[0]) * self.scale))
        return cv2.resize(r, (w, h), interpolation=cv2.INTER_NEAREST)

    def attach_for(self, basis0, x):
        """Props pinned to their holder with the offset of the current animation,
        adjusted by the prop's own params (rotation/translation in prop-local axes)."""
        att = {}
        for prop, holder in self.attach_names:
            off = self.fixed_off.get(prop)
            if off is None:
                off = self.m.attach_offset(basis0, prop, holder)
            r, t = np.zeros(3), np.zeros(3)
            for (b, k, ax), val in zip(self.params, x):
                if b == prop:
                    (r if k == "r" else t)[ax] = val
            D = np.eye(4)
            D[:3, :3] = rotvec_to_mat(np.radians(r))
            D[:3, 3] = t / self.unit
            att[self.m.idx[prop]] = (self.m.idx[holder], off @ D)
        return att

    def final_basis(self, basis0, x):
        """Basis with attached props baked into their own local matrices."""
        B = self.apply(basis0, x)
        att = self.attach_for(basis0, x)
        if not att:
            return B
        return self.m.basis_from_fk(B, self.m.fk(B, att))

    def apply(self, basis0, x):
        attached = {p for p, _ in self.attach_names}
        B = basis0.copy()
        # build per-bone rotation vectors / translations
        rv, tv = {}, {}
        for (b, k, ax), val in zip(self.params, x):
            if b in attached:
                continue
            (rv if k == "r" else tv).setdefault(b, np.zeros(3))[ax] = val
        for b, r in rv.items():
            i = self.m.idx[b]
            B[i, :3, :3] = B[i, :3, :3] @ rotvec_to_mat(np.radians(r))
        for b, t in tv.items():
            i = self.m.idx[b]
            B[i, :3, 3] += t / self.unit  # metres -> armature units (bone-local axes)
        return B

    def loss(self, basis0, x, refs):
        P, _ = self.m.skin(self.apply(basis0, x), self.attach_for(basis0, x))
        Pw = self.m.to_world(P)
        sils, parts = [], []
        for v in self.views:
            ml = self.m.raster_labels(Pw, v, self.boxes[v], self.scale)
            rl = refs[v]
            hh, ww = min(rl.shape[0], ml.shape[0]), min(rl.shape[1], ml.shape[1])
            rl, ml = rl[:hh, :ww], ml[:hh, :ww]
            r, mm = rl > 0, ml > 0
            sils.append((r & mm).sum() / max(1, (r | mm).sum()))
            for c in (2, 3, 4):  # dark (weapon/gauntlet), gold, purple
                rc, mc = rl == c, ml == c
                u = (rc | mc).sum()
                if u > 20:
                    parts.append((rc & mc).sum() / u)
        sil = float(np.mean(sils))
        part = float(np.mean(parts)) if parts else sil
        score = 0.5 * sil + 0.5 * part
        self.last = (sil, part)
        pen = self.reg * float(np.sum(np.square(x)))
        if self.temporal and self.x_prev is not None:
            pen += self.temporal * float(np.sum(np.square(x - self.x_prev)))
        return 1 - score + pen, sil

    def fit_frame(self, f, basis0, x0, steps=(12.0, 5.0, 2.0), tsteps=(0.05, 0.02, 0.008), passes=1):
        """x0 doubles as the temporal anchor (previous frame's solution) when temporal > 0."""
        refs = {v: self.ref(v, f) for v in self.views}
        x = x0.copy()
        best, iou = self.loss(basis0, x, refs)
        start_iou = iou
        evals = 1
        for si in range(len(steps)):
            for _ in range(passes):
                improved = False
                for g, items in self.groups:
                    for b, k in items:
                        for ax in range(3):
                            i = self.pidx[(b, k, ax)]
                            st = steps[si] if k == "r" else tsteps[si]
                            for sgn in (1, -1):
                                y = x.copy()
                                y[i] += sgn * st
                                l, io = self.loss(basis0, y, refs)
                                evals += 1
                                if l < best - 1e-5:
                                    x, best, iou, improved = y, l, io, True
                                    # keep going in the same direction while it helps
                                    while True:
                                        y = x.copy()
                                        y[i] += sgn * st
                                        l, io = self.loss(basis0, y, refs)
                                        evals += 1
                                        if l < best - 1e-5:
                                            x, best, iou = y, l, io
                                        else:
                                            break
                                    break
                if not improved:
                    break
        return x, start_iou, iou, evals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--frames", default=None, help="e.g. 1-133 or 1,52")
    ap.add_argument("--views", default="front,left")
    ap.add_argument("--scale", type=float, default=0.25)
    ap.add_argument("--reg", type=float, default=0.00001)
    ap.add_argument("--out", default="fit_basis.npy")
    ap.add_argument("--fresh", action="store_true", help="don't warm-start from the previous frame")
    ap.add_argument("--log", default="fit_log.json")
    ap.add_argument("--fixed-grip", action="store_true")
    ap.add_argument("--temporal", type=float, default=0.0, help="penalty per deg^2 of change from the previous frame")
    ap.add_argument("--warmup", type=int, default=0, help="fit this many frames before the range (not saved)")
    a = ap.parse_args()

    F = Fitter(a.work, a.views.split(","), a.scale, reg=a.reg, fixed_grip=a.fixed_grip, temporal=a.temporal)
    N = F.m.basis0.shape[0]
    if a.frames is None:
        frames = list(range(N))
    elif "-" in a.frames:
        s, e = a.frames.split("-")
        frames = list(range(int(s) - 1, int(e)))
    else:
        frames = [int(x) - 1 for x in a.frames.split(",")]
    out_path = os.path.join(a.work, a.out)
    result = np.load(out_path) if os.path.exists(out_path) else F.m.basis0.copy()
    xs_path = os.path.join(a.work, a.out.replace(".npy", "_x.npy"))
    X = np.load(xs_path) if os.path.exists(xs_path) else np.zeros((N, len(F.params)))
    log = []
    x = np.zeros(len(F.params))
    t0 = time.time()
    keep = set(frames)
    if a.warmup and frames:
        frames = [max(0, frames[0] - a.warmup) + i for i in range(frames[0] - max(0, frames[0] - a.warmup))] + frames
    for n, f in enumerate(frames):
        warm = not a.fresh and n > 0
        x0 = x if warm else np.zeros_like(x)
        F.x_prev = x0 if warm else None
        if warm:
            x, i0, i1, ev = F.fit_frame(f, F.m.basis0[f], x0, steps=(5.0, 2.0, 0.7), tsteps=(0.02, 0.008, 0.003))
        else:
            x, i0, i1, ev = F.fit_frame(f, F.m.basis0[f], x0)
        if f not in keep:
            continue
        result[f] = F.final_basis(F.m.basis0[f], x)
        X[f] = x
        log.append({"frame": f + 1, "iou_before": round(i0, 4), "iou_after": round(i1, 4), "evals": ev})
        print(f"frame {f + 1}: IoU {i0:.3f} -> {i1:.3f}  ({ev} evals, {time.time() - t0:.0f}s)", flush=True)
        if n % 10 == 0 or n == len(frames) - 1:
            np.save(out_path, result)
            np.save(xs_path, X)
    json.dump({"params": [list(p) for p in F.params], "log": log},
              open(os.path.join(a.work, a.log), "w"), indent=1)


if __name__ == "__main__":
    main()
