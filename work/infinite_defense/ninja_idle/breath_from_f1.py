"""Ninja Idle b50_v2: vòng thở 40F (F41 = F1) dựng từ pose F1 user tự chỉnh (k10_v5), user 2026-10-29: "triển khai từ f1 t đã pose đi".

F1 giữ nguyên đúng pose của user. Mỗi khớp: góc local = F1 + Δ·w(f − trễ), w = đường cong thở (hít 16F, thở ra 24F, analysis.md mục D),
trễ theo mục E (hông 0 → lưng 1 → ngực 2 → cổ/bả vai 3 → đầu 4 → tay 4–6). Δ = đỉnh hít (F17): hông nhấc 0,8 cm, lưng/ngực ưỡn,
đầu bù để vẫn nhìn thẳng, vai nhô; tay phải lùi thêm ra sau, khuỷu trái gập thêm, ngón phải nắm thêm. Khăn: sóng gió 20F truyền gốc → đuôi.
Chạy khi Studio mở anim ninja_idle bản b50_v2:  .venv/Scripts/python.exe -I -X utf8 work/infinite_defense/ninja_idle/breath_from_f1.py [--cid ID]
"""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ninja_pose as N

HERE = os.path.dirname(os.path.abspath(__file__))
F1 = json.load(open(os.path.join(HERE, "keys", "F1_user_k10_v5.json"), encoding="utf8"))["joints"]
KEYS = [1, 5, 9, 13, 17, 23, 29, 33, 35]   # 13, 33: hai điểm cực lắc ngang của khăn (thiếu key ở cực thì khăn khựng, user 2026-10-29)
PERIOD, RISE = 40, 16
# Δ ở đỉnh hít (độ, cộng vào góc local XYZ của F1)
DELTA = {"Spine1_M": (-1.0, 0, 0), "Chest_M": (-2.5, 0, 0), "Neck_M": (-0.5, 0, 0), "Head_M": (3.0, 0, 0),
         "Scapula_L": (0, 0, 3.0), "Scapula_R": (0, 0, -3.0),
         "MiddleFinger1_R": (0, 0, 4.0), "MiddleFinger2_R": (0, 0, 3.0)}
DELAY = {"Root_M": 0, "Spine1_M": 1, "Chest_M": 2, "Neck_M": 3, "Scapula_L": 3, "Scapula_R": 3, "Head_M": 4,
         "Shoulder_R": 4, "Elbow_L": 5, "MiddleFinger1_R": 6, "MiddleFinger2_R": 7}
ROOT_UP = 0.8          # cm
ARM_R_BACK = 2.5       # độ, xoay vai phải quanh trục X thế giới (tay đang ở sau hông → lùi thêm khi hít)
ELBOW_L_FLEX = -1.5    # độ, quanh Y local (trái: âm = gập thêm)
WIND = {1: (0.0, 15.0)}   # chỉ khớp gốc Scarf1: (nhún quanh X, lắc trái–phải quanh Y) độ. User: "cho anim lắc ở joint đầu thôi, sau làm polish sẽ chạy overlap"
# user 2026-10-29: "2 dây áo choàng đằng sau cho bay sang trái phải trông sẽ đẹp hơn ở góc ingame" → lắc ngang lớn, 1 nhịp mỗi vòng thở
SWAY_PERIOD = 40
WIND_PERIOD, WIND_STEP, LR_PHASE = 20, 2, 0   # user 2026-10-29: "tắt gió, cho khăn lắc đều nhau và lắc sang trái phải thôi" → không nhún, hai dây cùng pha


def breath(t):
    t = t % PERIOD
    return 0.5 - 0.5 * math.cos(math.pi * t / RISE) if t <= RISE else 0.5 + 0.5 * math.cos(math.pi * (t - RISE) / (PERIOD - RISE))


def ax(axis, deg):
    a = math.radians(deg) / 2; v = np.asarray(axis, float) * math.sin(a); return np.array([v[0], v[1], v[2], math.cos(a)])


def main():
    cid = sys.argv[sys.argv.index("--cid") + 1] if "--cid" in sys.argv else None
    br = N.Bridge(cid)
    assert br.anim(do="info")["version"] == "b50_v2", "mở bản b50_v2 trước"
    z1 = F1["Root_M"]["pos"][2]
    scarf = [f"Scarf{i}_{s}" for s in "LR" for i in WIND]   # Scarf2–4 giữ nguyên F1 (overlap làm ở polish)
    for f in KEYS:
        t = f - 1
        br.anim(do="frame", f=f)
        # cột sống, cổ, đầu, bả vai, ngón: F1 + Δ·w
        for n, d in DELTA.items():
            w = breath(t - DELAY[n])
            br.anim(do="rot", name=n, r=[round(a + b * w, 3) for a, b in zip(F1[n]["rot"], d)], abs=True)
        # khuỷu trái gập thêm (bản lề quanh Y local)
        q = N.q_mul(N.q_from_euler_xyz(F1["Elbow_L"]["rot"]), ax([0, 1, 0], ELBOW_L_FLEX * breath(t - DELAY["Elbow_L"])))
        br.anim(do="rot", name="Elbow_L", r=[round(float(v), 3) for v in N.euler_xyz_from_q(q)], abs=True)
        # tay phải lùi thêm: xoay vai quanh X thế giới (cha đã đặt ở frame này)
        br.anim(do="rot", name="Shoulder_R", r=F1["Shoulder_R"]["rot"], abs=True)
        qw = br.world_q("Shoulder_R")
        br.set_world("Shoulder_R", N.q_mul(ax([1, 0, 0], ARM_R_BACK * breath(t - DELAY["Shoulder_R"])), qw))
        # khăn: sóng gió truyền gốc → đuôi, hai đuôi lệch pha
        for n in scarf:
            i, side = int(n[5]), n[-1]
            ph = 2 * math.pi * (t - WIND_STEP * i - (LR_PHASE if side == "R" else 0)) / WIND_PERIOD
            ampx, ampy = WIND[i]
            sw = 2 * math.pi * (t - WIND_STEP * i - (LR_PHASE if side == "R" else 0)) / SWAY_PERIOD   # cùng chiều, đuôi phải trễ 5F
            r = list(F1[n]["rot"]); r[0] += ampx * math.sin(ph); r[1] += ampy * math.sin(sw)
            br.anim(do="rot", name=n, r=[round(v, 3) for v in r], abs=True)
        # hông nhấc theo nhịp thở (chân giữ bằng IK)
        cur = br.read(["Root_M"])["Root_M"]["pos"][2]
        want = z1 + ROOT_UP * breath(t)
        if abs(want - cur) > 0.005:
            br.anim(do="pos", name="Root_M", t=[0, 0, round(want - cur, 3)])
        br.anim(do="key")
        print("F%d thở %.2f" % (f, breath(t)), flush=True)
    print(br.anim(do="info")["keys"])


if __name__ == "__main__":
    main()
