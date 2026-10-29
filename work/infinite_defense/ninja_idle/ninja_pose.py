"""Ninja: dựng pose qua cầu nối Studio (lớp Anim) bằng FK tính ở đây.

Rig Studio của Ninja có mọi khớp ở bind với góc 0, nên trục local của khớp = trục thế giới three.js
(Y lên, +Z trước, +X bên trái nhân vật). `anim read` trả vị trí theo trục Blender (x, -z, y).

    from ninja_pose import Bridge, arm_fk
    br = Bridge(); W = br.world(); ...
Hàm chính:
  arm_fk(br, side, elbow_dir, fore_dir, hand_dir, palm_hint, blade_dir=None)
     đặt Shoulder/Elbow/Wrist (và Weapon nếu blade_dir) theo hướng thế giới; khuỷu là bản lề thuần
     (trục gập ⊥ cánh tay và cẳng tay), cổ tay xoay theo hand_dir + palm_hint.
"""
import json, os, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import studio_cmd as SC  # noqa: E402

REST = json.load(open(os.path.join(ROOT, "work", "store", "ninja_rig_lab", "rig", "skeleton.json")))
REST = {j["name"]: (j["parent"], np.array(j["pos"], float)) for j in REST["joints"]}


# ---------------- quaternion (x, y, z, w) như three.js
def q_mul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return np.array([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz])


def q_inv(q): return np.array([-q[0], -q[1], -q[2], q[3]])


def q_rot(q, v):
    p = q_mul(q_mul(q, np.r_[v, 0.0]), q_inv(q)); return p[:3]


def q_from_euler_xyz(deg):   # three.js Euler order XYZ
    x, y, z = np.radians(deg) / 2
    c1, c2, c3, s1, s2, s3 = np.cos(x), np.cos(y), np.cos(z), np.sin(x), np.sin(y), np.sin(z)
    return np.array([s1 * c2 * c3 + c1 * s2 * s3, c1 * s2 * c3 - s1 * c2 * s3, c1 * c2 * s3 + s1 * s2 * c3, c1 * c2 * c3 - s1 * s2 * s3])


def m_from_q(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def q_from_m(m):
    t = np.trace(m)
    if t > 0:
        s = 0.5 / np.sqrt(t + 1); return np.array([(m[2, 1] - m[1, 2]) * s, (m[0, 2] - m[2, 0]) * s, (m[1, 0] - m[0, 1]) * s, 0.25 / s])
    i = int(np.argmax(np.diag(m)))
    if i == 0:
        s = 2 * np.sqrt(1 + m[0, 0] - m[1, 1] - m[2, 2]); return np.array([0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s, (m[2, 1] - m[1, 2]) / s])
    if i == 1:
        s = 2 * np.sqrt(1 + m[1, 1] - m[0, 0] - m[2, 2]); return np.array([(m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s, (m[0, 2] - m[2, 0]) / s])
    s = 2 * np.sqrt(1 + m[2, 2] - m[0, 0] - m[1, 1]); return np.array([(m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s, (m[1, 0] - m[0, 1]) / s])


def euler_xyz_from_q(q):     # three.js setFromRotationMatrix, order XYZ
    m = m_from_q(q)
    y = np.arcsin(np.clip(m[0, 2], -1, 1))
    if abs(m[0, 2]) < 0.9999999:
        x = np.arctan2(-m[1, 2], m[2, 2]); z = np.arctan2(-m[0, 1], m[0, 0])
    else:
        x = np.arctan2(m[2, 1], m[1, 1]); z = 0.0
    return np.degrees([x, y, z])


def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)


def frame(x, yhint):
    """Ma trận xoay có cột 0 = x, cột 1 gần yhint (trực chuẩn)."""
    x = unit(x); y = np.asarray(yhint, float) - np.dot(yhint, x) * x; y = unit(y); z = np.cross(x, y)
    return np.c_[x, y, z]


# ---------------- cầu nối
class Bridge:
    def __init__(self, cid=None):
        SC.CID = cid

    def cmd(self, op, args, timeout=15):
        r = SC.call(op, args, timeout)
        if not r.get("ok"):
            raise RuntimeError(f"{op} {args}: {r}")
        return r["result"]

    def anim(self, **a): return self.cmd("anim", a)

    def read(self, names=None):
        return self.anim(do="read", names=names or [])

    def world_q(self, name, R=None):
        """Quaternion thế giới của khớp = tích local từ gốc (bind: mọi khớp góc 0, vị trí chỉ là tịnh tiến)."""
        chain = []
        n = name
        while n:
            chain.append(n); n = REST[n][0] if n in REST else None
        chain = [c for c in reversed(chain) if c != "root"]
        R = R or self.read(chain)
        q = np.array([0, 0, 0, 1.0])
        for c in chain:
            e = R[c]["rot"] if c in R else [0, 0, 0]
            q = q_mul(q, q_from_euler_xyz(e))
        return q

    def set_world(self, name, qw):
        """Đặt góc tuyệt đối sao cho quaternion thế giới của khớp = qw."""
        par = REST[name][0]
        qp = self.world_q(par) if par and par != "root" else np.array([0, 0, 0, 1.0])
        ql = q_mul(q_inv(qp), qw)
        e = [round(float(v), 3) for v in euler_xyz_from_q(ql)]
        return self.anim(do="rot", name=name, r=e, abs=True)


def blender_to_three(p): return np.array([p[0], p[2], -p[1]], float)


def leg_fk(br, side, hip, knee, ankle, foot_yaw_deg=0.0):
    """Chân FK theo điểm thế giới (trục three, cm): đùi hip→knee, cẳng ankle; gối là bản lề quanh trục X local
    (ở bind chân chỉ -Y, gối gập ra trước). Bàn chân đặt phẳng, mũi xoay foot_yaw_deg quanh trục đứng (+ = sang trái nhân vật)."""
    hip, knee, ankle = (np.asarray(v, float) for v in (hip, knee, ankle))
    t, s = unit(knee - hip), unit(ankle - knee)
    n = np.cross(s, t)                      # trục gập: gối ra trước → n gần +X
    n = unit(n) if np.linalg.norm(n) > 1e-6 else np.array([1.0, 0, 0])
    if n[0] < 0: n = -n
    def seg(d):
        y = -unit(d); x = unit(n - np.dot(n, y) * y); return q_from_m(np.c_[x, y, np.cross(x, y)])
    br.set_world("Hip_" + side, seg(t))
    br.set_world("Knee_" + side, seg(s))
    a = np.radians(foot_yaw_deg) / 2
    br.set_world("Ankle_" + side, np.array([0, np.sin(a), 0, np.cos(a)]))
    return {"thigh": round(float(np.linalg.norm(knee - hip)), 1), "shin": round(float(np.linalg.norm(ankle - knee)), 1),
            "knee_deg": round(float(np.degrees(np.arccos(np.clip(np.dot(t, s), -1, 1)))), 1)}


def two_bone(root, target, l1, l2, pole):
    """Điểm khớp giữa của chuỗi 2 đoạn root→mid→target, mặt phẳng gập theo hướng pole."""
    root, target, pole = (np.asarray(v, float) for v in (root, target, pole))
    d = target - root; L = min(np.linalg.norm(d), l1 + l2 - 1e-3); d = unit(d)
    a = (l1 * l1 + L * L - l2 * l2) / (2 * l1 * L)
    p = pole - np.dot(pole, d) * d; p = unit(p)
    return root + d * l1 * a + p * l1 * np.sqrt(max(0.0, 1 - a * a))


def arm_fk(br, side, elbow_dir, fore_dir, hand_dir, palm_hint=(0, 1, 0), blade_dir=None, blade_roll_hint=(0, 1, 0), grip_thumb=None):
    """Hướng (trục three): elbow_dir = vai→khuỷu, fore_dir = khuỷu→cổ tay, hand_dir = cổ tay→đầu ngón,
    palm_hint = hướng mu bàn tay xấp xỉ (trục +Y local của bàn tay ở bind là mu tay; lòng tay −Y).
    Xương tay trái ở bind chỉ +X, tay phải chỉ −X."""
    s = 1.0 if side == "L" else -1.0
    u, f, h = unit(elbow_dir), unit(fore_dir), unit(hand_dir)
    n = np.cross(u, f)
    if np.linalg.norm(n) < 1e-6: n = np.array([0, 1.0, 0])
    n = unit(n)
    # cột 0 của khung = hướng xương (+X với tay trái, -X với tay phải → nhân s)
    def bone_frame(d, yh):
        M = frame(s * d, yh)          # cột 0 = s*d: trục X local của xương trỏ theo xương (trái) / ngược (phải)
        return q_from_m(M)
    # khuỷu bản lề theo giải phẫu ở bind: tay duỗi ngang lòng úp, khuỷu gập về trước = xoay quanh trục Y local
    # (trái: góc âm, phải: góc dương) → cột Y của khung = -s·n, hai đoạn chung trục đó
    def hinge(d):
        x = unit(s * d); y = -s * n; y = unit(y - np.dot(y, x) * x); return q_from_m(np.c_[x, y, np.cross(x, y)])
    qs, qe = hinge(u), hinge(f)
    if grip_thumb is not None:   # bàn tay nắm: trục ngón cái (+Z local bàn tay ở bind) theo grip_thumb
        x = unit(s * h); z = np.asarray(grip_thumb, float); z = unit(z - np.dot(z, x) * x)
        qw = q_from_m(np.c_[x, np.cross(z, x), z])
    else:
        qw = bone_frame(h, palm_hint)
    br.set_world("Shoulder_" + side, qs)
    br.set_world("Elbow_" + side, qe)
    br.set_world("Wrist_" + side, qw)
    if blade_dir is not None and side == "L":
        # kunai: trục lưỡi = +Z local của Weapon ở bind
        d = unit(blade_dir); yh = np.asarray(blade_roll_hint, float)
        y = unit(yh - np.dot(yh, d) * d); x = np.cross(y, d)
        br.set_world("Weapon", q_from_m(np.c_[x, y, d]))
    return {"elbow_bend_deg": round(float(np.degrees(np.arccos(np.clip(np.dot(u, f), -1, 1)))), 1),
            "wrist_dev_deg": round(float(np.degrees(np.arccos(np.clip(np.dot(f, h), -1, 1)))), 1)}
