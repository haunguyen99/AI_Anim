"""Ninja Idle polish_v3/v4: polish_v2 + anim hai tay (v4: biên độ tay giảm, overlap thân, xem dưới) (user 2026-10-29: "phần cánh tay chưa thấy có anim, bổ sung nhé").

polish_v2 chỉ làm bàn tay đi ~3 cm/vòng thở (vai 2,5°, khuỷu 1,5°) nên nhìn như tay đứng yên. Thêm lớp tay theo cùng đường
cong thở, overlap vai → khuỷu → cổ tay → ngón (idle.md#breath-recipe: tay trễ sau vai, cổ tay/ngón trễ thêm):
- tay phải (tay không, kéo sau hông): vai lùi ra sau quanh X thế giới, khuỷu gập thêm (+Y local), cổ tay vẩy (Z), ngón nắm thêm;
- tay trái (kunai): vai nhấc (X local), khuỷu gập thêm (−Y local) nâng nắm tay, cổ tay nghiêng lưỡi kunai trễ theo (Z).
Trục đo trên rig 2026-10-29 (xoay +10° từng trục, đọc góc khuỷu / dời cổ tay): khuỷu L +Y = duỗi, khuỷu R +Y = gập.
    .venv/Scripts/python.exe -I -X utf8 work/infinite_defense/ninja_idle/polish_v3.py [--cid ID] [--dry]
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ninja_pose as N
import breath_from_f1 as B
import polish_v2 as P2

# (độ ở đỉnh hít, trễ F)
ARM = {
    "R_back": (6.0, 6),        # vai phải lùi ra sau (thay 2,5° của v2)
    "R_elbow": (7.0, 8),       # khuỷu phải gập thêm
    "R_wrist": (6.0, 10),       # cổ tay phải vẩy
    "R_fing1": (8.0, 11), "R_fing2": (6.0, 12),
    "L_lift": (4.0, 6),        # vai trái nhấc
    "L_elbow": (6.0, 8),       # khuỷu trái gập thêm (thay 1,5° của v2)
    "L_wrist": (4.0, 10),       # cổ tay trái nghiêng kunai
}
# Thân (polish_v4, user 2026-10-29: "thêm overlap nhẹ vào body của nhịp thở. hiện tại body đang thở hơi cứng"): trễ dọc cột sống
# nới theo idle.md#breath-recipe (Spine1 +2, ngực +4, bả vai +5, cổ +6, đầu bù +8), lưng uốn rõ hơn chút. Thay hằng số của blocking
# (breath_from_f1.py: trễ 1/2/3/4, ngực −2,5°) chỉ trong tiến trình này.
B.DELTA = dict(B.DELTA, **{"Spine1_M": (-1.5, 0, 0), "Chest_M": (-3.0, 0, 0), "Neck_M": (-1.0, 0, 0), "Head_M": (3.5, 0, 0)})
B.DELAY = dict(B.DELAY, **{"Spine1_M": 2, "Chest_M": 4, "Scapula_L": 5, "Scapula_R": 5, "Neck_M": 6, "Head_M": 8})
VERSION = os.environ.get("NINJA_VER", "polish_v4")
CHAIN_R = P2.CHAIN_R
qe = P2.qe


def w(key, t):
    a, d = ARM[key]; return a * B.breath(t - d)


def pose_at(t):
    F1 = B.F1
    P = P2.pose_at(t)
    L = {n: P[n] for n in P}
    # vai phải: dựng lại từ F1 với biên độ mới (v2 đã cộng 2,5°, bỏ đi)
    qp = np.array([0, 0, 0, 1.0])
    for c in CHAIN_R: qp = N.q_mul(qp, qe(L[c]))
    qw = N.q_mul(N.q_mul(B.ax([1, 0, 0], w("R_back", t)), qp), qe(F1["Shoulder_R"]["rot"]))
    Q = {"Shoulder_R": N.q_mul(N.q_inv(qp), qw)}
    Q["Elbow_R"] = N.q_mul(qe(F1["Elbow_R"]["rot"]), B.ax([0, 1, 0], w("R_elbow", t)))
    Q["Wrist_R"] = N.q_mul(qe(F1["Wrist_R"]["rot"]), B.ax([0, 0, 1], w("R_wrist", t)))
    Q["MiddleFinger1_R"] = N.q_mul(qe(F1["MiddleFinger1_R"]["rot"]), B.ax([0, 0, 1], w("R_fing1", t)))
    Q["MiddleFinger2_R"] = N.q_mul(qe(F1["MiddleFinger2_R"]["rot"]), B.ax([0, 0, 1], w("R_fing2", t)))
    Q["Shoulder_L"] = N.q_mul(qe(F1["Shoulder_L"]["rot"]), B.ax([1, 0, 0], w("L_lift", t)))
    Q["Elbow_L"] = N.q_mul(qe(F1["Elbow_L"]["rot"]), B.ax([0, 1, 0], -w("L_elbow", t)))
    Q["Wrist_L"] = N.q_mul(qe(F1["Wrist_L"]["rot"]), B.ax([0, 0, 1], w("L_wrist", t)))
    for n, q in Q.items(): L[n] = [float(v) for v in N.euler_xyz_from_q(q)]
    return L


ANIMATED = sorted(set(P2.ANIMATED) | {"Shoulder_L", "Elbow_R", "Wrist_R", "MiddleFinger1_R", "MiddleFinger2_R"})


def main():
    if "--dry" in sys.argv:
        P = [pose_at(f - 1) for f in range(1, 42)]
        for n in ANIMATED:
            a = np.array([P[i][n] for i in range(41)])
            print("%-16s nối %.3f°  gia tốc max %.2f°/F²" % (n, np.abs(a[40] - a[0]).max(), np.abs(np.diff(np.vstack([a[-2:-1], a]), 2, axis=0)).max()))
        return
    cid = sys.argv[sys.argv.index("--cid") + 1] if "--cid" in sys.argv else None
    br = N.Bridge(cid)
    assert br.anim(do="info")["version"] == VERSION, "mở bản %s trước" % VERSION
    z1 = B.F1["Root_M"]["pos"][2]
    for f in range(1, 41):
        t = f - 1; P = pose_at(t)
        br.anim(do="frame", f=f)
        for n in ANIMATED:
            br.anim(do="rot", name=n, r=[round(v, 3) for v in P[n]], abs=True)
        cur = br.read(["Root_M"])["Root_M"]["pos"][2]
        want = z1 + B.ROOT_UP * B.breath(t)
        if abs(want - cur) > 0.005:
            br.anim(do="pos", name="Root_M", t=[0, 0, round(want - cur, 3)])
        br.anim(do="key")
        print("F%d" % f, flush=True)
    br.anim(do="frame", f=1)


if __name__ == "__main__":
    main()
