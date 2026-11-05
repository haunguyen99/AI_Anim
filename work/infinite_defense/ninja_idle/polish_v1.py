"""Ninja Idle polish_v1: key mọi frame F1–F40 (F41 = F1) trên Studio, từ blocking b50_v1 đã duyệt.

Giữ đường cong thở + overlap + sóng khăn của blocking (`blocking_b50.py`), thêm:
- tay phải (tay không) lùi ra sau khi hít, trễ 4F (blocking: tay trôi ra ngoài 2 cm ở F17) — xoay vai quanh trục X thế giới;
- khuỷu trái gập thêm khi hít (trễ 5F) và cổ tay trái vẩy nhẹ (overlap 4→7F) cho kunai "sống";
- ngón tay phải nắm thêm khi hít (trễ 6–7F);
- đầu lệch hướng rất nhẹ (0,8°) theo chu kỳ 40F.
Mọi góc tính sẵn ở đây (không đọc lại từng khớp), mỗi frame chỉ đọc độ cao hông.
Chạy khi Studio đang mở anim ninja_idle bản polish_v1:  .venv/Scripts/python.exe -I -X utf8 work/infinite_defense/ninja_idle/polish_v1.py
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ninja_pose as N
from blocking_b50 import DELAY, WIND_X, WIND_Y, WIND_PERIOD, WIND_STEP, LR_PHASE, breath

FRAMES = list(range(1, 41))
CHAIN_R = ["Root_M", "Spine1_M", "Chest_M", "Scapula_R"]          # cha của Shoulder_R
EXTRA = ["Shoulder_R", "Shoulder_L", "Elbow_L", "Wrist_L", "MiddleFinger1_R", "MiddleFinger2_R", "Head_M"]


def qe(e): return N.q_from_euler_xyz(e)
def ax(axis, deg):
    a = math.radians(deg) / 2; v = np.asarray(axis, float) * math.sin(a); return np.array([v[0], v[1], v[2], math.cos(a)])


def main(dry=False):
    br = N.Bridge()
    names = sorted(set(DELAY) | set(EXTRA))
    # pose gốc lấy từ k10_v1 đã duyệt (F1/F17 của bản này đã có trễ + sóng khăn của blocking)
    import time
    def open_v(v):
        br.anim(do="version", v=v)
        for _ in range(50):
            try:
                if br.anim(do="info")["version"] == v: br.read(["Root_M"]); return
            except RuntimeError: pass
            time.sleep(0.2)
        raise RuntimeError("không mở được " + v)
    open_v("k10_v1")
    br.anim(do="frame", f=1); P1 = br.read(names)
    br.anim(do="frame", f=17); P2 = br.read(names)
    open_v("polish_v1")
    z1, z2 = P1["Root_M"]["pos"][2], P2["Root_M"]["pos"][2]
    for f in FRAMES:
        t = f - 1
        L = {}
        for n in names:
            w = breath(t - DELAY.get(n, 0))
            L[n] = [a + (b - a) * w for a, b in zip(P1[n]["rot"], P2[n]["rot"])]
            if n.startswith("Scarf"):
                i, side = int(n[5]), n[-1]
                ph = 2 * math.pi * (t - WIND_STEP * i - (LR_PHASE if side == "R" else 0)) / WIND_PERIOD
                L[n][0] += WIND_X[i] * math.sin(ph)
                L[n][1] += WIND_Y[i] * math.sin(ph / 2 + (0.0 if side == "L" else math.pi)) * (1 if side == "L" else -1)
        Q = {n: qe(L[n]) for n in names}
        # tay phải lùi ra sau khi hít: xoay vai quanh X thế giới (+ = tay đang buông xuống đi về sau)
        qp = np.array([0, 0, 0, 1.0])
        for c in CHAIN_R: qp = N.q_mul(qp, Q[c])
        qw = N.q_mul(N.q_mul(ax([1, 0, 0], 2.5 * breath(t - 4)), qp), Q["Shoulder_R"])
        Q["Shoulder_R"] = N.q_mul(N.q_inv(qp), qw)
        # khuỷu trái gập thêm (bản lề quanh Y local, trái = góc âm), cổ tay trái vẩy nhẹ
        Q["Elbow_L"] = N.q_mul(Q["Elbow_L"], ax([0, 1, 0], -1.5 * breath(t - 5)))
        Q["Wrist_L"] = N.q_mul(Q["Wrist_L"], ax([0, 0, 1], 2.0 * (breath(t - 7) - breath(t - 4))))
        # ngón tay phải nắm thêm khi hít (Z+ = cuộn về lòng bàn tay với tay phải)
        Q["MiddleFinger1_R"] = N.q_mul(Q["MiddleFinger1_R"], ax([0, 0, 1], 4.0 * breath(t - 6)))
        Q["MiddleFinger2_R"] = N.q_mul(Q["MiddleFinger2_R"], ax([0, 0, 1], 3.0 * breath(t - 7)))
        Q["Head_M"] = N.q_mul(Q["Head_M"], ax([0, 1, 0], 0.8 * math.sin(2 * math.pi * t / 40 + 1.0)))
        if dry:
            continue
        br.anim(do="frame", f=f)
        for n in names:
            if n == "Root_M":
                continue
            br.anim(do="rot", name=n, r=[round(float(v), 3) for v in N.euler_xyz_from_q(Q[n])], abs=True)
        z = z1 + (z2 - z1) * breath(t)
        cur = br.read(["Root_M"])["Root_M"]["pos"][2]
        if abs(z - cur) > 0.005:
            br.anim(do="pos", name="Root_M", t=[0, 0, round(z - cur, 3)])
        br.anim(do="key")
        print("F%d" % f, flush=True)
    print(br.anim(do="info")["keys"])


if __name__ == "__main__":
    main(dry="--dry" in sys.argv)
