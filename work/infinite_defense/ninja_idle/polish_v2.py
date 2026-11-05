"""Ninja Idle polish_v2: key mọi frame F1–F40 (F41 = F1) từ blocking b50_v2 (user 2026-10-29: "giờ làm polish t xem đi").

Giữ nguyên công thức của blocking (`breath_from_f1.py`: F1 = pose user k10_v5, đường cong thở hít 16F / thở ra 24F, trễ theo chuỗi),
nhưng lấy mẫu MỌI frame thay vì nội suy spline giữa 9 key, và thêm:
- khăn: gốc Scarf1 lắc trái–phải ±15° chu kỳ 40F như blocking (không gió, hai dây cùng nhịp); Scarf2–4 chạy overlap theo kiểu
  "đuôi đi theo đường của gốc" (timing_spline.md#secondary-cloth, rope_follow): hướng đoạn j = hướng gốc lúc (t − j·LAG),
  góc local khớp j = hiệu hướng hai đoạn kề → sóng chạy gốc → đuôi, đuôi lắc tiếp khi gốc đã đổi chiều;
- cổ tay trái (kunai) vẩy nhẹ theo sau khuỷu (trễ 4→7F), ±2°;
- đầu lệch hướng rất nhẹ 0,8° theo chu kỳ 40F để không đứng chết.
Mọi góc tính sẵn (không đọc lại từng khớp), mỗi frame chỉ đọc độ cao hông để dời bằng IK.
Chạy khi Studio đang mở anim Ninja_Idle bản polish_v2:
    .venv/Scripts/python.exe -I -X utf8 work/infinite_defense/ninja_idle/polish_v2.py [--cid ID] [--dry]
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ninja_pose as N
import breath_from_f1 as B

FRAMES = list(range(1, 41))
LAG = 3.0                      # F, trễ mỗi đốt khăn (sóng gốc → đuôi)
TAIL_GAIN = [1.0, 1.0, 1.15, 1.3]   # đốt sau văng thêm chút (đuôi nhẹ)
SWAY = B.WIND[1][1]            # 15°
CHAIN_R = ["Root_M", "Spine1_M", "Chest_M", "Scapula_R"]   # cha của Shoulder_R


def qe(e): return N.q_from_euler_xyz(e)


def sway(t):                   # hướng (góc quanh Y local) của gốc khăn lúc t, như blocking
    return SWAY * math.sin(2 * math.pi * (t - B.WIND_STEP) / B.SWAY_PERIOD)


def pose_at(t):
    """Góc local (độ, XYZ) mọi khớp được anim ở frame t (t = f − 1)."""
    F1 = B.F1
    L = {n: list(F1[n]["rot"]) for n in F1 if "rot" in F1[n]}
    for n, d in B.DELTA.items():
        w = B.breath(t - B.DELAY[n])
        L[n] = [a + b * w for a, b in zip(F1[n]["rot"], d)]
    Q = {}
    # khuỷu trái gập thêm khi hít (bản lề Y local)
    Q["Elbow_L"] = N.q_mul(qe(F1["Elbow_L"]["rot"]), B.ax([0, 1, 0], B.ELBOW_L_FLEX * B.breath(t - B.DELAY["Elbow_L"])))
    # cổ tay trái vẩy nhẹ theo sau khuỷu
    Q["Wrist_L"] = N.q_mul(qe(F1["Wrist_L"]["rot"]), B.ax([0, 0, 1], 2.0 * (B.breath(t - 7) - B.breath(t - 4))))
    # đầu lệch hướng rất nhẹ
    Q["Head_M"] = N.q_mul(qe(L["Head_M"]), B.ax([0, 1, 0], 0.8 * math.sin(2 * math.pi * t / 40 + 1.0)))
    # tay phải lùi ra sau khi hít: xoay vai quanh X thế giới, cha tính từ góc local frame này
    qp = np.array([0, 0, 0, 1.0])
    for c in CHAIN_R: qp = N.q_mul(qp, qe(L[c]))
    qw = N.q_mul(N.q_mul(B.ax([1, 0, 0], B.ARM_R_BACK * B.breath(t - B.DELAY["Shoulder_R"])), qp), qe(F1["Shoulder_R"]["rot"]))
    Q["Shoulder_R"] = N.q_mul(N.q_inv(qp), qw)
    # khăn: đốt j hướng = sway(t − j·LAG); local = hiệu hướng đốt j và j−1 (đốt 1 = hướng tuyệt đối)
    for s in "LR":
        prev = 0.0
        for j in range(1, 5):
            n = "Scarf%d_%s" % (j, s)
            ang = sway(t - (j - 1) * LAG) * TAIL_GAIN[j - 1]
            r = list(F1[n]["rot"]); r[1] += ang - prev; prev = ang
            L[n] = r
    out = {n: list(v) for n, v in L.items()}
    for n, q in Q.items(): out[n] = [float(v) for v in N.euler_xyz_from_q(q)]
    return out


ANIMATED = sorted(set(B.DELTA) | {"Elbow_L", "Wrist_L", "Head_M", "Shoulder_R"} | {"Scarf%d_%s" % (j, s) for j in range(1, 5) for s in "LR"})


def main():
    dry = "--dry" in sys.argv
    if dry:
        # kiểm loop + độ mượt: góc mỗi khớp F1..F41, đạo hàm bậc 2 lớn nhất
        P = [pose_at(f - 1) for f in range(1, 42)]
        for n in ANIMATED:
            a = np.array([P[i][n] for i in range(41)])
            seam = np.abs(a[40] - a[0]).max(); acc = np.abs(np.diff(np.vstack([a[-2:-1], a]), 2, axis=0)).max()
            print("%-16s nối %.3f°  gia tốc max %.2f°/F²  biên %.1f°" % (n, seam, acc, (a.max(0) - a.min(0)).max()))
        return
    cid = sys.argv[sys.argv.index("--cid") + 1] if "--cid" in sys.argv else None
    br = N.Bridge(cid)
    assert br.anim(do="info")["version"] == "polish_v2", "mở bản polish_v2 trước"
    z1 = B.F1["Root_M"]["pos"][2]
    for f in FRAMES:
        t = f - 1
        P = pose_at(t)
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
    print(br.anim(do="info")["keys"])


if __name__ == "__main__":
    main()
