"""Numpy model of the rig for silhouette fitting: forward kinematics, linear blend
skinning, orthographic projection into the calibrated reference views, rasterising.

Data comes from `key_pose.py dump` (rig_np.npz / rig_np.json in the work folder).
All bone math is in ARMATURE space; arm_mw maps to world (Blender, Z up).
"""
import json
import os

import cv2
import numpy as np


def quat_to_mat(q):
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def rotvec_to_mat(r):
    a = np.linalg.norm(r)
    if a < 1e-12:
        return np.eye(3)
    k = r / a
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * K @ K


def mat_to_rotvec(R):
    c = np.clip((np.trace(R) - 1) / 2, -1, 1)
    a = np.arccos(c)
    if a < 1e-9:
        return np.zeros(3)
    if np.pi - a < 1e-4:  # ~180 deg
        w, V = np.linalg.eigh((R + np.eye(3)) / 2)
        return V[:, np.argmax(w)] * a
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (2 * np.sin(a))
    return v * a


class SilModel:
    def __init__(self, work):
        d = np.load(os.path.join(work, "rig_np.npz"))
        meta = json.load(open(os.path.join(work, "rig_np.json")))
        self.V = d["verts"]                          # rest, armature space
        self.Vh = np.c_[self.V, np.ones(len(self.V))]
        self.F = d["faces"]
        self.wi, self.ww = d["wi"], d["ww"]
        self.part = d["part"]                        # 1 = weapon/prop
        self.vcol = d["vcol"]
        self.rest = d["rest"]                        # (B,4,4) bone.matrix_local
        self.rest_inv = np.linalg.inv(self.rest)
        self.parent = d["parent"]
        self.basis0 = d["basis"]                     # (N,B,4,4) current animation
        self.arm_mw = d["arm_mw"]
        self.bones = meta["bones"]
        self.idx = {n: i for i, n in enumerate(self.bones)}
        self.cams = meta["cameras"]
        self.axes = meta["char_axes_world"]
        # colour class per face (majority of its vertices), same rules as the reference pixels
        from refmask import classify_hsv
        c = (np.clip(self.vcol, 0, 1) * 255).astype(np.uint8)[None]
        vlab = classify_hsv(cv2.cvtColor(c, cv2.COLOR_RGB2HSV))[0]
        fl = vlab[self.F]
        self.flabel = np.array([np.bincount(r, minlength=6).argmax() for r in fl], np.uint8)
        self.rel = np.array([self.rest_inv[p] @ self.rest[i] if p >= 0 else self.rest[i]
                             for i, p in enumerate(self.parent)])

    # ------------------------------------------------------------ kinematics
    def fk(self, basis, attach=None):
        """basis (B,4,4) local pose -> posed armature-space matrices (B,4,4).
        attach: {prop_idx: (holder_idx, offset 4x4)} pins a prop to a bone (prop = holder @ offset)."""
        M = np.empty_like(basis)
        for i, p in enumerate(self.parent):
            M[i] = (M[p] @ self.rel[i] if p >= 0 else self.rel[i]) @ basis[i]
        if attach:
            for w, (h, off) in attach.items():
                M[w] = M[h] @ off
                for c in np.flatnonzero(self.parent == w):  # props are leaf bones here; refresh children anyway
                    M[c] = M[w] @ self.rel[c] @ basis[c]
        return M

    def attach_offset(self, basis, prop, holder):
        M = self.fk(basis)
        return np.linalg.inv(M[self.idx[holder]]) @ M[self.idx[prop]]

    def basis_from_fk(self, basis, M):
        """Local basis matrices that reproduce posed matrices M (used to bake attached props)."""
        B = basis.copy()
        for i, p in enumerate(self.parent):
            parent_m = M[p] @ self.rel[i] if p >= 0 else self.rel[i]
            B[i] = np.linalg.inv(parent_m) @ M[i]
        return B

    def skin(self, basis, attach=None):
        M = self.fk(basis, attach)
        S = M @ self.rest_inv                        # (B,4,4)
        out = np.zeros((len(self.V), 3))
        for j in range(4):
            Sj = S[self.wi[:, j]]                    # (N,4,4)
            out += self.ww[:, j:j + 1] * np.einsum("nij,nj->ni", Sj[:, :3, :], self.Vh)
        return out, M

    def to_world(self, P):
        return P @ self.arm_mw[:3, :3].T + self.arm_mw[:3, 3]

    # ------------------------------------------------------------ cameras
    def project(self, Pw, view):
        c = self.cams[view]
        rel = Pw - np.array(c["pos"])
        u = c["W"] / 2 + rel @ np.array(c["right"]) / c["k"]
        v = c["H"] / 2 - rel @ np.array(c["up"]) / c["k"]
        depth = rel @ np.array(c["dir"])
        return np.c_[u, v], depth

    def raster_labels(self, Pw, view, box, scale):
        """Part-label image (class id per pixel) with occlusion: triangles painted far to near."""
        uv, depth = self.project(Pw, view)
        x0, y0, x1, y1 = box
        pts = ((uv - [x0, y0]) * scale * 16).astype(np.int32)
        h, w = int(round((y1 - y0) * scale)), int(round((x1 - x0) * scale))
        zf = depth[self.F].mean(1)
        order = np.argsort(-zf)                  # farthest first (depth grows away from the camera)
        tri = pts[self.F[order]]
        lab = self.flabel[order]
        m = np.zeros((h, w), np.uint8)
        for t, l in zip(tri, lab):
            cv2.fillConvexPoly(m, t, int(l), lineType=cv2.LINE_8, shift=4)
        return m

    def raster(self, Pw, view, box, scale, faces_mask=None):
        """Silhouette mask of the posed mesh inside crop `box` (x0,y0,x1,y1 ref px), resized by `scale`."""
        uv, _ = self.project(Pw, view)
        x0, y0, x1, y1 = box
        pts = ((uv - [x0, y0]) * scale * 16).astype(np.int32)   # 4 bits sub-pixel
        h, w = int(round((y1 - y0) * scale)), int(round((x1 - x0) * scale))
        F = self.F if faces_mask is None else self.F[faces_mask]
        tri = pts[F]
        # back-face cull: for a closed mesh the front faces alone cover the silhouette
        a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
        area = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
        tri = tri[area != 0]
        m = np.zeros((h, w), np.uint8)
        # fillPoly with many contours uses an even-odd rule (overlaps cancel), so fill each triangle
        for t in tri:
            cv2.fillConvexPoly(m, t, 255, lineType=cv2.LINE_8, shift=4)
        return m
