"""Ninja Idle b50_v1: blocking 50% trên Studio (lớp Anim) từ 2 pose chính đã duyệt k10_v1 (F1 đáy, F17 đỉnh hít).

Mỗi khớp: góc local = P1 + (P2 − P1)·w(f − trễ), w = đường cong thở (hít 16F ease sine, thở ra 24F), chu kỳ 40F.
Khăn: thêm sóng gió chu kỳ 20F truyền từ gốc ra đuôi (+2F mỗi xương), hai đuôi lệch pha 5F.
Loop 41F: F41 = F1 (chu kỳ 40 và 20 đều chia hết 40).
Chạy khi trang Studio đang mở anim ninja_idle bản b50_v1:  .venv/Scripts/python.exe -I -X utf8 work/infinite_defense/ninja_idle/blocking_b50.py
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ninja_pose as N

KEYS = [1, 5, 9, 13, 17, 23, 29, 35, 41]
PERIOD, RISE = 40, 16
# trễ (frame) so với hông — analysis.md mục E
DELAY = {"Root_M": 0, "Spine1_M": 1, "Chest_M": 2, "Neck_M": 3, "Scapula_L": 3, "Scapula_R": 3, "Head_M": 4,
         "Shoulder_L": 3, "Shoulder_R": 3, "Elbow_L": 4, "Elbow_R": 4, "Wrist_L": 5, "Wrist_R": 5, "Weapon": 5}
for s in "LR":
    for i in (1, 2, 3, 4):
        DELAY[f"Scarf{i}_{s}"] = 3 + 2 * i
    for n in ("MiddleFinger1", "MiddleFinger2", "ThumbFinger1", "ThumbFinger2"):
        DELAY[f"{n}_{s}"] = 6
# sóng gió trên khăn (độ, cộng vào góc local): lên/xuống quanh X, lắc ngang quanh Y; tăng dần ra đuôi
WIND_X = {1: 2.0, 2: 3.0, 3: 3.5, 4: 4.0}
WIND_Y = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5}
WIND_PERIOD, WIND_STEP, LR_PHASE = 20, 2, 5


def breath(t):
    t = t % PERIOD
    if t <= RISE:
        return 0.5 - 0.5 * math.cos(math.pi * t / RISE)
    return 0.5 + 0.5 * math.cos(math.pi * (t - RISE) / (PERIOD - RISE))


def main():
    br = N.Bridge()
    names = list(DELAY)
    br.anim(do="frame", f=1); P1 = br.read(names)
    br.anim(do="frame", f=17); P2 = br.read(names)
    z1, z2 = P1["Root_M"]["pos"][2], P2["Root_M"]["pos"][2]
    moving = [n for n in names if max(abs(a - b) for a, b in zip(P1[n]["rot"], P2[n]["rot"])) > 0.05]
    print("khớp đổi giữa 2 pose:", moving)
    for f in KEYS:
        br.anim(do="frame", f=f)
        t = f - 1
        for n in names:
            w = breath(t - DELAY[n])
            r = [a + (b - a) * w for a, b in zip(P1[n]["rot"], P2[n]["rot"])]
            if n.startswith("Scarf"):
                i, side = int(n[5]), n[-1]
                ph = 2 * math.pi * (t - WIND_STEP * i - (LR_PHASE if side == "R" else 0)) / WIND_PERIOD
                r[0] += WIND_X[i] * math.sin(ph)
                r[1] += WIND_Y[i] * math.sin(ph / 2 + (0.0 if side == "L" else math.pi)) * (1 if side == "L" else -1)
            if n in moving or n.startswith("Scarf"):
                br.anim(do="rot", name=n, r=[round(v, 3) for v in r], abs=True)
        z = z1 + (z2 - z1) * breath(t)
        cur = br.read(["Root_M"])["Root_M"]["pos"][2]
        if abs(z - cur) > 0.005:
            br.anim(do="pos", name="Root_M", t=[0, 0, round(z - cur, 3)])
        br.anim(do="key")
        print("F%d  thở %.2f" % (f, breath(t)))
    print(br.anim(do="info")["keys"])


if __name__ == "__main__":
    main()
