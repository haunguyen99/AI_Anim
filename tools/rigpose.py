"""(tools/, chuyển từ work/shoot_die_repeat/sdr03 2026-10-28; mặc định RIG_FBX/TEX là của SDR03 map3)
FK + IK + skin + render trên khung xương FBX của team (MC_char_map3_Rig.fbx, 38 xương, cả nỏ slingshot_* và bím tóc),
không Blender, không rig Studio (rig Studio chỉ giữ 25 xương thân). Toạ độ FBX: cm, Y lên, nhân vật nhìn +Z, phải = −X.

    from rigpose import Rig
    rig = Rig()                       # nạp rig + texture
    P = rig.rest()                    # pose = {tên xương: local 4x4 kiểu FBX}
    P = rig.frame_of(anim_fbx, f)     # pose từ một frame của FBX anim cùng khung xương
    rig.rot(P, "Chest_M", [0, 30, 0]) # xoay quanh khớp theo trục world (độ, thứ tự X→Y→Z)
    rig.ik_arm(P, "L", wrist_world4x4, pole_world)   # khuỷu bản lề, trục bản lề = trục của rig
    rig.render(P, "side_r", path)     # ảnh đúng texture (tools/render_fbx_tex.py)
"""
import os, sys, json, subprocess, tempfile, shutil
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))       # tools/
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import render_fbx_tex as RT
import fbxanim

RIG_FBX = r"E:\Horus\shot-die-repeat\Assets\_Game\Animations\Map03\MC_char_map3_Rig.fbx"
TEX = r"E:\Horus\shot-die-repeat\Assets\_Game\3D\Texture\T_Color_ShotDieRepeat.tga"
CACHE = os.path.join(ROOT, "work", "_cache", "rigpose", "rig_extract")   # mesh/xương đọc từ FBX (theo file + mtime)


def Rx(a): a = np.radians(a); c, s = np.cos(a), np.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(a): a = np.radians(a); c, s = np.cos(a), np.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(a): a = np.radians(a); c, s = np.cos(a), np.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def eul(e): return Rz(e[2]) @ Ry(e[1]) @ Rx(e[0])   # X trước, rồi Y, rồi Z (trục world)
def axis_angle(ax, deg):
    ax = np.asarray(ax, float); ax = ax / np.linalg.norm(ax); a = np.radians(deg)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * K @ K
def rot_between(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = float(np.dot(a, b))
    if np.linalg.norm(v) < 1e-9:
        if c > 0: return np.eye(3)
        p = np.cross(a, [1, 0, 0] if abs(a[0]) < 0.9 else [0, 1, 0]); return axis_angle(p, 180)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K * (1 / (1 + c))
def ang(a, b): return float(np.degrees(np.arccos(np.clip(np.dot(a, b) / np.linalg.norm(a) / np.linalg.norm(b), -1, 1))))


class Rig:
    def __init__(self, rig_fbx=RIG_FBX, tex=TEX):
        import hashlib   # cache theo file + thời điểm sửa (rig gốc và rig đã sửa không lẫn nhau)
        key = hashlib.md5(("%s|%d" % (os.path.abspath(rig_fbx), os.path.getmtime(rig_fbx))).encode()).hexdigest()[:10]
        cache = CACHE + "_" + key
        if not os.path.isfile(os.path.join(cache, "ref_mesh.json")):
            os.makedirs(cache, exist_ok=True)
            subprocess.run([sys.executable, "-I", os.path.join(ROOT, "work", "rig_lab", "extract_fbx.py"), rig_fbx, cache],
                           check=True, capture_output=True)
        self.path = rig_fbx
        self.meshes = json.load(open(os.path.join(cache, "ref_mesh.json")))
        skel = json.load(open(os.path.join(cache, "ref_skeleton.json")))
        self.bind = {s["name"]: np.array(s["bind_mat"]).reshape(4, 4) for s in skel if s.get("bind_mat")}
        models, par = fbxanim.load(rig_fbx)
        self.models = {m["name"]: m for m in models.values() if m["type"] == "LimbNode"}
        id2n = {i: m["name"] for i, m in models.items()}
        self.parent = {id2n[c]: id2n[p] for c, p in par.items() if id2n.get(c) in self.models and id2n.get(p) in self.models}
        self.order = []                    # cha trước con
        def add(n):
            if n in self.order: return
            if n in self.parent: add(self.parent[n])
            self.order.append(n)
        for n in self.models: add(n)
        self.children = {n: [c for c, p in self.parent.items() if p == n] for n in self.models}
        T = np.asarray(Image.open(tex).convert("RGB"), float) / 255.0
        H, W = T.shape[:2]
        self.cols = []
        for m in self.meshes:   # màu mỗi tam giác = trung bình 3 góc UV
            uv = np.array(m["uvc"]).reshape(-1, 3, 2)
            px = np.clip((uv[..., 0] * W).astype(int), 0, W - 1); py = np.clip(((1 - uv[..., 1]) * H).astype(int), 0, H - 1)
            self.cols.append(T[py, px].mean(1))
        self.rest_pose = {n: fbxanim.local(m, 0.0) for n, m in self.models.items()}
        W0 = self.world(self.rest_pose)
        for n in self.models:      # xương không có cluster: bind = rest
            self.bind.setdefault(n, W0[n])
        self.bind_inv = {n: np.linalg.inv(M) for n, M in self.bind.items()}

    # ---------------------------------------------------------------- pose
    def rest(self): return {n: M.copy() for n, M in self.rest_pose.items()}
    def frame_of(self, anim_fbx, f, fps=30):
        models, _ = fbxanim.load(anim_fbx)
        by = {m["name"]: m for m in models.values() if m["type"] == "LimbNode"}
        return {n: (fbxanim.local(by[n], f / fps) if n in by else self.rest_pose[n].copy()) for n in self.models}
    def world(self, P):
        W = {}
        for n in self.order:
            W[n] = (W[self.parent[n]] @ P[n]) if n in self.parent else P[n].copy()
        return W
    def pos(self, P, n): return self.world(P)[n][:3, 3].copy()
    def set_world_rot(self, P, n, R3, W=None):
        """Đặt hướng world của xương n (giữ vị trí khớp), con đi theo."""
        W = W or self.world(P); M = W[n].copy(); M[:3, :3] = R3 @ np.diag(np.linalg.norm(W[n][:3, :3], axis=0))
        Wp = W[self.parent[n]] if n in self.parent else np.eye(4)
        P[n] = np.linalg.inv(Wp) @ M
    def rot(self, P, n, e, about=None):
        """Xoay xương n thêm một góc theo trục world (độ, X→Y→Z) quanh khớp của nó."""
        W = self.world(P); R = eul(e) if np.ndim(e) == 1 else np.asarray(e)
        self.set_world_rot(P, n, R @ W[n][:3, :3] / np.linalg.norm(W[n][:3, :3], axis=0), W)
    def move(self, P, n, d):
        """Dời xương n thêm d (cm, world)."""
        W = self.world(P); Wp = W[self.parent[n]] if n in self.parent else np.eye(4)
        M = W[n].copy(); M[:3, 3] += d; P[n] = np.linalg.inv(Wp) @ M
    def set_world(self, P, n, M):
        """Đặt ma trận world 4x4 của xương n (con đi theo)."""
        W = self.world(P); Wp = W[self.parent[n]] if n in self.parent else np.eye(4)
        P[n] = np.linalg.inv(Wp) @ M
    def rotmat(self, P, n):
        R = self.world(P)[n][:3, :3]; return R / np.linalg.norm(R, axis=0)

    # ---------------------------------------------------------------- IK tay: khuỷu bản lề quanh trục Z local của Elbow
    def ik_arm(self, P, side, wrist_target, pole, hinge_axis_local=(0, 0, 1)):
        """wrist_target: 4x4 world (vị trí + hướng cổ tay). pole: điểm world khuỷu nên chĩa về. Trả dict đo."""
        s, e, w = "Shoulder_" + side, "Elbow_" + side, "Wrist_" + side
        W = self.world(P); S, E0, Wr0 = W[s][:3, 3], W[e][:3, 3], W[w][:3, 3]
        a, b = np.linalg.norm(E0 - S), np.linalg.norm(Wr0 - E0)
        T = wrist_target[:3, 3]; d = T - S; L = np.linalg.norm(d); Lc = min(L, (a + b) * 0.9995)
        u = d / L
        x = (a * a - b * b + Lc * Lc) / (2 * Lc); h = np.sqrt(max(a * a - x * x, 0))
        pv = np.asarray(pole, float) - S; pv = pv - np.dot(pv, u) * u; pv /= np.linalg.norm(pv)
        E = S + u * x + pv * h
        # 1) vai: xoay cánh tay trên về phía E
        self.set_world_rot(P, s, rot_between(E0 - S, E - S) @ self.rotmat(P, s))
        # 2) xoắn vai quanh trục cánh tay trên để trục bản lề khuỷu ⟂ mặt phẳng (S, E, T)
        W = self.world(P); ax_up = (E - S) / a
        hinge = self.rotmat(P, e) @ np.asarray(hinge_axis_local, float)
        n = np.cross(E - S, T - E); n = n / np.linalg.norm(n) if np.linalg.norm(n) > 1e-6 else hinge
        h_proj = hinge - np.dot(hinge, ax_up) * ax_up; n_proj = n - np.dot(n, ax_up) * ax_up
        best = None
        for sign in (1, -1):    # trục bản lề có thể cùng hay ngược pháp tuyến: chọn cái gập đúng chiều
            t = n_proj * sign
            twist = np.degrees(np.arctan2(np.dot(np.cross(h_proj, t), ax_up), np.dot(h_proj, t)))
            Q = {k: v.copy() for k, v in P.items()}
            self.set_world_rot(Q, s, axis_angle(ax_up, twist) @ self.rotmat(Q, s))
            # 3) khuỷu: xoay quanh trục bản lề để cẳng tay chỉ tới T
            Wq = self.world(Q); Eq, Wq0 = Wq[e][:3, 3], Wq[w][:3, 3]
            hz = self.rotmat(Q, e) @ np.asarray(hinge_axis_local, float)
            v0, v1 = Wq0 - Eq, T - Eq
            v0p, v1p = v0 - np.dot(v0, hz) * hz, v1 - np.dot(v1, hz) * hz
            bend = np.degrees(np.arctan2(np.dot(np.cross(v0p, v1p), hz), np.dot(v0p, v1p)))
            self.set_world_rot(Q, e, axis_angle(hz, bend) @ self.rotmat(Q, e))
            err = np.linalg.norm(self.pos(Q, w) - T)
            if best is None or err < best[0]: best = (err, Q, twist, bend)
        err, Q, twist, bend = best
        P.update(Q)
        # 4) cổ tay: đặt hướng đích, đo độ lệch so với cẳng tay
        before = self.rotmat(P, w)
        self.set_world_rot(P, w, wrist_target[:3, :3] / np.linalg.norm(wrist_target[:3, :3], axis=0))
        Wf = self.world(P)
        return {"err_cm": round(float(np.linalg.norm(Wf[w][:3, 3] - T)), 2), "reach": round(L / (a + b), 3),
                "elbow_deg": round(180 - ang(Wf[s][:3, 3] - Wf[e][:3, 3], Wf[w][:3, 3] - Wf[e][:3, 3]), 1),
                "wrist_dev_deg": round(ang(self.rotmat(P, w)[:, 0], before[:, 0]), 1)}

    # ---------------------------------------------------------------- skin + render
    def skin(self, P):
        W = self.world(P)
        S = {n: W[n] @ self.bind_inv[n] for n in self.models}
        out = []
        for m in self.meshes:
            V = np.array(m["verts"]).reshape(-1, 3); Vh = np.c_[V, np.ones(len(V))]
            acc = np.zeros((len(V), 3)); ws = np.zeros(len(V))
            for bone, (ix, wt) in m["weights"].items():
                if bone not in S: continue
                ix = np.array(ix, int); wt = np.array(wt, float)
                acc[ix] += wt[:, None] * (Vh[ix] @ S[bone].T)[:, :3]; ws[ix] += wt
            ok = ws > 1e-6
            acc[ok] /= ws[ok, None]; acc[~ok] = V[~ok]
            out.append(acc)
        return out
    def tris(self, P, skip=()):
        V = self.skin(P); T, C = [], []
        for m, v, c in zip(self.meshes, V, self.cols):
            if m["name"] in skip: continue
            T.append(v[np.array(m["tris"]).reshape(-1, 3)]); C.append(c)
        return np.concatenate(T), np.concatenate(C)
    def render(self, P, view, path, size=900, box=None, skip=()):
        t, c = self.tris(P, skip); img = RT.render(t, c, view, size, box=box); img.save(path); return path
