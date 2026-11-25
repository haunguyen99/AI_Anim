"""Cấu hình idle PeaceGirl: đứng THỞ (loop 90F = 3 s một nhịp), đầu + hai tay overlap trễ sau ngực, tóc bên physics, chớp mắt.
Bộ máy tools/spine/idle_engine.py (skill /skillidle). Chạy: .venv/Scripts/python.exe -I work/peace_girl/spine/PeaceGirl/idle_cfg.py

Vai trò xương: hip > spine > chest (thở: nâng + nở nhẹ) > neck > head (> eye_L / eye_R, hair_F, hair_B, hairL1 > hairL2, hairR1 > hairR2)
chest > upper_arm_X > forearm_X > hand_X (noScale). Con của chest / hip xoay 90°: trục X local = DỌC (dời lên xuống ghi vào X).
Thở: ngực nâng lúc hít (42% nhịp), hạ lúc thở ra (58%). Overlap = lò xo đuổi theo phần ngực mang đi: đầu trễ ~3F, hai tay trễ ~6F,
cẳng tay / bàn tay còn trễ thêm (quán tính theo góc cha). Tóc bên = physics chuỗi 2 đốt, tóc mái chỉ scale + nhích.
Chớp mắt: scaleX xương mắt (trục X = dọc mắt) 100% -> 8% (2F) giữ 1F -> 100% (3F).
"""
import math, os, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "tools", "spine"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import anim_kit as K
from anim_kit import Chain, FPS
from anim_params import Params

FOLDER = os.path.join(ROOT, "work", "peace_girl", "spine", "PeaceGirl")
PATH = os.environ.get("ANIM_KIT_PATH") or os.path.join(FOLDER, "peacegirl.json")
ANIM = "idle"

P = Params(os.path.dirname(PATH), "idle", "Idle", anim="idle", run=["idle_cfg.py"])
END = P.num("end", 90, 60, 150, 6, "Độ dài loop (frame, 90 = 3 s một nhịp thở)")
A_BREATH = P.num("breath", 1.0, 0, 3, 0.1, "Thở: ngực lên / xuống (x, 1 = 2,5 px + nở 0,6%)")
A_HEAD = P.num("head", 1.0, 0, 3, 0.1, "Đầu overlap: ngả theo độ trễ + nghiêng nhẹ (x)")
A_ARM = P.num("arms", 1.0, 0, 3, 0.1, "Hai tay overlap: cánh tay / cẳng tay / bàn tay (x)")
A_SWAY = P.num("sway", 1.0, 0, 3, 0.1, "Thân nghiêng nhẹ (x, 1 = 0,4°)")
HEAD_HZ = P.num("head_hz", 1.1, 0.5, 4, 0.05, "Đầu đuổi theo ngực: độ cứng (Hz, nhỏ = trễ nhiều)")
ARM_HZ = P.num("arm_hz", 0.80, 0.4, 3, 0.05, "Hai tay đuổi theo ngực: độ cứng (Hz, nhỏ = trễ nhiều)")
HEAD_G = P.num("head_gain", 0.95, 0.5, 1.3, 0.01, "Đầu: biên độ so với ngực (<1 = trễ xuống ở đỉnh hít)")
ARM_G = P.num("arm_gain", 0.90, 0.5, 1.5, 0.01, "Hai tay: biên độ lên xuống so với ngực")
HAIR_HZ = P.num("hair_hz", 1.5, 0.5, 3, 0.05, "Tóc bên: độ cứng (Hz, nhỏ = mềm)")
HAIR_Z = P.num("hair_damp", 0.30, 0.05, 1, 0.01, "Tóc bên: giảm chấn")
HAIR_W = P.num("hair_wind", 45.0, 0, 300, 5, "Tóc bên: gió nhẹ")
BLINK_F = P.num("blink", 58, 1, 160, 1, "Chớp mắt bắt đầu (frame)")
if not os.environ.get("ANIM_KIT_PATH"):
    P.save()

T = END / FPS
s = lambda amp, freq=1, ph=0.0: K.wave(amp, freq, ph, T)


def warp(u):
    """hít 42% nhịp, thở ra 58%; đạo hàm 0 ở hai đầu và ở đỉnh -> mượt"""
    u %= 1.0
    return 0.5 * u / 0.42 if u < 0.42 else 0.5 + 0.5 * (u - 0.42) / 0.58


br = lambda t: 0.5 - 0.5 * math.cos(2 * math.pi * warp(t / T))             # 0 -> 1 -> 0, F0 = 0
Y_CHEST = lambda t: 2.5 * A_BREATH * br(t)


def spring_follow(drive, hz, zeta, cycles=8, sub=16):
    """lò xo bậc 2 đuổi theo drive(t) tuần hoàn T; chạy `cycles` vòng tới tuần hoàn, lấy vòng cuối, khép loop."""
    n = END * sub
    dt = T / n; w0 = 2 * math.pi * hz
    x, v = drive(0.0), 0.0
    rec = []
    for c in range(cycles):
        rec = []
        for i in range(n):
            t = i * dt
            v += (w0 * w0 * (drive(t) - x) - 2 * zeta * w0 * v) * dt
            x += v * dt
            rec.append(x)
    rec = np.array(rec + [rec[0]])
    tab = np.linspace(0.0, T, n + 1)
    return lambda t: float(np.interp(t % T, tab, rec))


SP_SC = lambda t: 0.003 * A_BREATH * br(t)            # scale dọc của spine / chest (xem SCALE): nở ngực đẩy các điểm phía trên lên
CH_SC = lambda t: 0.006 * A_BREATH * br(t)
Y_SPINE0, Y_CHEST0 = 860, 700                          # độ cao ảnh gốc của gốc spine / chest
Y_HEAD0, Y_NECK0, Y_ARM0 = 316, 372, 395               # gốc đầu / cổ / vai


def carry(y_img, t):
    """độ dời THẬT theo phương dọc của điểm ở độ cao ảnh y_img do chuỗi spine > chest mang đi (dời ngực + nở ngực)"""
    return Y_CHEST(t) + max(0.0, Y_SPINE0 - y_img) * SP_SC(t) + max(0.0, Y_CHEST0 - y_img) * CH_SC(t)


HEAD_C = lambda t: carry(Y_HEAD0, t)
NECK_C = lambda t: carry(Y_NECK0, t)
ARM_C = lambda t: carry(Y_ARM0, t)
HEAD_Y = spring_follow(lambda t: HEAD_G * HEAD_C(t), HEAD_HZ, 0.45)
NECK_Y = spring_follow(lambda t: 0.97 * NECK_C(t), HEAD_HZ * 1.4, 0.5)
ARM_Y = spring_follow(lambda t: ARM_G * ARM_C(t), ARM_HZ, 0.40)
ARM_R_Y = spring_follow(ARM_Y, ARM_HZ * 1.15, 0.40)                       # tay phải (viewer) trễ thêm một chút so với tay trái

OWN = {
    "hip": s(0.15 * A_SWAY, 1, 0.0),
    "spine": s(0.20 * A_SWAY, 1, 0.06),
    "chest": s(0.25 * A_SWAY, 1, 0.12),
    # đầu ngả theo độ trễ so với ngực + nghiêng chậm; đầu trễ dưới ngực khi ngực vọt lên
    "head": lambda t: A_HEAD * 0.7 * (HEAD_C(t) * HEAD_G - HEAD_Y(t)) + 0.8 * A_HEAD * math.sin(2 * math.pi * (t / T - 0.20)),
    "upper_arm_L": s(0.7 * A_ARM, 1, 0.10),
    "upper_arm_R": s(-0.7 * A_ARM, 1, 0.16),
    "forearm_L": s(0.8 * A_ARM, 1, 0.22),
    "forearm_R": s(-0.8 * A_ARM, 1, 0.28),
    "hand_L": s(1.2 * A_ARM, 1, 0.34),
    "hand_R": s(-1.2 * A_ARM, 1, 0.40),
    "hair_B": s(0.5, 1, 0.30),
    "hair_F": s(0.4, 1, 0.38),
}
INERTIA = {                      # (gain, trễ frame) theo góc thế giới của cha: con giữ hướng cũ rồi đuổi theo
    "forearm_L": (0.35, 5), "forearm_R": (0.35, 6),
    "hand_L": (0.55, 5), "hand_R": (0.55, 6),
    "hair_B": (0.8, 6), "hair_F": (0.45, 4),
}
TRANSLATE = {                    # px local: con của chest / hip xoay 90° nên trục X local = DỌC
    "chest": lambda t: (Y_CHEST(t), 0.0),
    "neck": lambda t: (NECK_Y(t) - NECK_C(t), 0.0),
    "head": lambda t: (HEAD_Y(t) - HEAD_C(t) - (NECK_Y(t) - NECK_C(t)), 0.0),
    "upper_arm_L": lambda t: (ARM_Y(t) - ARM_C(t), 0.0),
    "upper_arm_R": lambda t: (ARM_R_Y(t) - ARM_C(t), 0.0),
    "hip": lambda t: (0.0, 0.8 * A_SWAY * math.sin(2 * math.pi * t / T)),       # local y = -x thế giới: hông trượt ngang ~0,8 px
}
SCALE = {                        # nở ngực nhẹ: sx = dọc thân, sy = ngang (cổ / tay noScale nên không phình); tóc mái chỉ scale
    "spine": lambda t: (1 + SP_SC(t), 1 + 0.002 * A_BREATH * br(t)),
    "chest": lambda t: (1 + CH_SC(t), 1 + 0.005 * A_BREATH * br(t)),
    "hair_F": lambda t: (1 + 0.012 * br(t - 0.08 * T), 1 + 0.004 * br(t - 0.08 * T)),
}
N_KEYS = 15

CHAINS = [Chain(["hairL1", "hairL2"], HAIR_HZ, HAIR_Z, HAIR_W, 0.0, (1.0, 0.0)),
          Chain(["hairR1", "hairR2"], HAIR_HZ * 0.92, HAIR_Z, HAIR_W, 1.3, (1.0, 0.0))]
BLINK = None                     # chớp mắt dựng riêng bên dưới (mắt = region tách khỏi mặt, không có ảnh mắt nhắm)

EYE_BONES = ("eye_L", "eye_R")
BLINK_SQUASH = 0.08


def blink_keys(f0, squash=BLINK_SQUASH):
    kt = lambda f: K.ktime(f / FPS, FPS)
    frames = [(f0, 1.0), (f0 + 2, squash), (f0 + 3, squash), (f0 + 6, 1.0)]
    out = []
    for f, v in frames:
        k = {"time": kt(f)} if f else {}
        k.update({"x": v, "y": 1.0})
        out.append(k)
    return out


def add_blink(anim, f0, squash=BLINK_SQUASH):
    for b in EYE_BONES:
        anim["bones"].setdefault(b, {})["scale"] = blink_keys(f0, squash)
    return anim


if __name__ == "__main__":
    from idle_engine import build_idle
    anim = build_idle(sys.modules[__name__], write=False)
    add_blink(anim, int(BLINK_F))
    try:
        import spine_live_cmd
        spine_live_cmd.claude_backup(PATH, "Claude gen idle")
    except Exception as e:
        print("(không ghi được backup Spine Live:", e, ")")
    K.write_anim(PATH, ANIM, anim)
    print(f"{ANIM}: {END} frame, {len(anim['bones'])} xương có key (chớp mắt F{int(BLINK_F)}) -> {PATH}")
