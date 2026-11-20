"""Cấu hình idle: nhân vật cầm cờ đứng THỞ LÊN XUỐNG nhịp nhàng (loop 90F = 3 s một nhịp), đầu + tay + cờ overlap trễ nhịp, chớp mắt.
Bộ máy tools/spine/idle_engine.py (skill /skillidle). Chạy: .venv/Scripts/python.exe -I work/daily_reward/spine/FlagChar/idle_cfg.py

Vai trò xương: hip > spine > chest (thở: nâng lên / hạ xuống + nở nhẹ) > head (> prop cánh quạt, eye_L / eye_R) ·
chest > grip (ctrl hai tay + cờ) > hand_R / hand_L (găng), flag1 > flag2 (vải cờ, physics) · arm_R / arm_L chạy IK theo găng (không key).
Thở: ngực nâng lúc hít (42% nhịp), hạ lúc thở ra (58%). Overlap = lò xo đuổi theo chuyển động ngực:
đầu trễ ~3F, hai tay + cờ trễ ~7F (kèm vượt nhẹ ở hai đầu hơi), đầu / găng ngả theo độ trễ, cánh quạt + vải cờ lắc theo sau.
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

FOLDER = os.path.join(ROOT, "work", "daily_reward", "spine", "FlagChar")
PATH = os.environ.get("ANIM_KIT_PATH") or os.path.join(FOLDER, "flagchar.json")
ANIM = "idle"

P = Params(os.path.dirname(PATH), "idle", "Idle", anim="idle", run=["idle_cfg.py"])
END = P.num("end", 90, 60, 150, 6, "Độ dài loop (frame, 90 = 3 s một nhịp thở)")
A_BREATH = P.num("breath", 1.0, 0, 3, 0.1, "Thở: ngực lên / xuống (x, 1 = 6 px)")
A_HEAD = P.num("head", 1.0, 0, 3, 0.1, "Đầu overlap: ngả theo độ trễ (x)")
A_HAND = P.num("hands", 1.0, 0, 3, 0.1, "Tay + cờ overlap (x)")
HEAD_HZ = P.num("head_hz", 1.1, 0.5, 4, 0.05, "Đầu đuổi theo ngực: độ cứng (Hz, nhỏ = trễ nhiều)")
HAND_HZ = P.num("hand_hz", 0.70, 0.4, 3, 0.05, "Tay + cờ đuổi theo ngực: độ cứng (Hz, nhỏ = trễ nhiều)")
HEAD_G = P.num("head_gain", 0.95, 0.5, 1.3, 0.01, "Đầu: biên độ so với ngực (<1 = trễ xuống ở đỉnh hít, trễ lên ở đáy thở ra)")
HAND_G = P.num("hand_gain", 1.30, 0.5, 2.5, 0.05, "Cánh tay + cờ: biên độ lên xuống so với ngực (1 = bằng ngực, 1.4 = ~10 px)")
HAND_AMP = P.num("hand_amp", 0.3, 0, 2, 0.05, "Biên độ riêng của bàn tay (trễ thêm + cụp, x; 1 = bản cũ)")
WRIST_HZ = P.num("wrist_hz", 0.8, 0.5, 4, 0.05, "Bàn tay đuổi theo cánh tay: độ cứng (Hz, nhỏ = bàn tay trễ nhiều sau cánh tay)")
FL_HZ = P.num("flag_hz", 1.0, 0.3, 3, 0.05, "Cờ: độ cứng (Hz, nhỏ = mềm)")
FL_Z = P.num("flag_damp", 0.35, 0.05, 1, 0.01, "Cờ: giảm chấn")
FL_W = P.num("flag_wind", 70.0, 0, 400, 5, "Cờ: gió nhẹ")
A_MOUTH = P.num("mouth", 1.0, 0, 3, 0.1, "Mỏ phồng theo nhịp thở (x, 1 = +2%)")
A_MBOB = P.num("mouth_bob", 1.0, 0, 3, 0.1, "Mỏ nhấp lên xuống (x, 1 = 2 px)")
MOUTH_PH = P.num("mouth_phase", 0.40, 0, 1, 0.01, "Mỏ bắt đầu phồng ở (phần nhịp thở, 0.40 = ngay sau đỉnh hít)")
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
Y_CHEST = lambda t: 6.0 * A_BREATH * br(t)


def spring_follow(drive, hz, zeta, cycles=8, sub=16):
    """lò xo bậc 2 đuổi theo drive(t) tuần hoàn T: x'' = w0^2 (d - x) - 2 zeta w0 x' ; chạy `cycles` vòng tới tuần hoàn,
    lấy vòng cuối, khép loop; trả f(t) tuần hoàn (nội suy bảng mịn). Trễ ~ 2 zeta / w0, vượt nhẹ ở chỗ đổi chiều."""
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


SP_SC = lambda t: 0.008 * A_BREATH * br(t)           # scale dọc của spine / chest (xem SCALE): nở ngực đẩy các điểm phía trên lên
CH_SC = lambda t: 0.020 * A_BREATH * br(t)
Y_GRIP0, Y_HEAD0 = 690 - 436, 690 - 405                # độ cao (toạ độ Spine) của grip / gốc đầu ở setup; spine gốc 150, chest gốc 230


def carry(yp, t):
    """độ dời THẬT theo phương dọc của điểm đặt ở độ cao yp do chuỗi spine > chest mang đi (dời ngực + nở ngực)"""
    return Y_CHEST(t) + (yp - 150) * SP_SC(t) + (yp - 230) * CH_SC(t)


HEAD_C = lambda t: carry(Y_HEAD0, t)
HAND_C = lambda t: carry(Y_GRIP0, t)
# đầu / tay đuổi theo phần ngực mang đi với biên độ < 1 và có trễ => ở ĐỈNH hít tay + đầu còn ở DƯỚI ngực một chút, ở ĐÁY thở ra thì ở TRÊN
HEAD_Y = spring_follow(lambda t: HEAD_G * HEAD_C(t), HEAD_HZ, 0.45)          # vị trí tuyệt đối (dọc) của đầu
HAND_Y = spring_follow(lambda t: HAND_G * HAND_C(t), HAND_HZ, 0.40)          # hai tay + cờ
# mỗi găng còn trễ thêm so với ctrl grip (găng xa trễ nhiều hơn): overlap giữa hai tay + cẳng tay (IK) + cờ
HAND_R_Y = spring_follow(HAND_Y, WRIST_HZ * 1.1, 0.40)
HAND_L_Y = spring_follow(HAND_Y, WRIST_HZ * 0.9, 0.40)
GRIP_X = spring_follow(lambda t: 1.5 * A_HAND * br(t), HAND_HZ, 0.5)       # hai tay nhích ra trước khi hít

OWN = {
    # spine / chest không xoay: thở = lên xuống thuần (xoay làm tay ở xa ngực nhấp theo phương dọc, sai nhịp trễ)
    # đầu ngả sau khi ngực vọt lên (đầu trễ dưới ngực), ngả trước khi ngực hạ: góc ~ (ngực - đầu)
    "head": lambda t: A_HEAD * 0.8 * (HEAD_C(t) * HEAD_G - HEAD_Y(t)) + 0.7 * A_HEAD * math.sin(2 * math.pi * (t / T - 0.16)),
    # bàn tay chổng theo độ trễ so với cánh tay: cánh tay đi lên mà bàn tay còn thấp -> mũi bàn tay cụp xuống (âm = chúi), và ngược lại
    "hand_R": lambda t: -2.5 * A_HAND * HAND_AMP * (HAND_Y(t) - HAND_R_Y(t)),
    "hand_L": lambda t: -2.5 * A_HAND * HAND_AMP * (HAND_Y(t) - HAND_L_Y(t)),
    "prop": s(0.8, 1, 0.34),
}
INERTIA = {                      # (gain, trễ frame) theo góc thế giới của cha
    "prop": (1.2, 9),
}
TRANSLATE = {                    # px local (đầu / tay là con của chest: chỉ cộng phần chênh so với ngực)
    "chest": lambda t: (Y_CHEST(t), 0.0),            # trục X local của con chest / head / grip = DỌC (cha xoay 90°)
    "head": lambda t: (HEAD_Y(t) - HEAD_C(t), 0.0),
    "hand_R": lambda t: (0.0, A_HAND * HAND_AMP * (HAND_R_Y(t) - HAND_Y(t))),      # găng trễ thêm (grip world góc 0: local y = dọc)
    "hand_L": lambda t: (0.0, A_HAND * HAND_AMP * (HAND_L_Y(t) - HAND_Y(t))),
    "grip": lambda t: (HAND_Y(t) - HAND_C(t), -GRIP_X(t))      # local y = -x thế giới (ra trước),
}
# cán cờ (pole) bám bàn tay: trung bình phần trễ thêm của hai găng (cán cờ nằm trong tay, không được trôi so với găng)
TRANSLATE["pole"] = lambda t: (0.0, A_HAND * HAND_AMP * 0.5 * ((HAND_R_Y(t) - HAND_Y(t)) + (HAND_L_Y(t) - HAND_Y(t))))
SCALE = {                        # nở ngực nhẹ: sx = dọc thân, sy = ngang (đầu / tay / cờ noScale nên không phình)
    "spine": lambda t: (1 + SP_SC(t), 1 + 0.004 * A_BREATH * br(t)),
    "chest": lambda t: (1 + CH_SC(t), 1 + 0.008 * A_BREATH * br(t)),
}
def pop(u):
    """bật nhẹ: phồng nhanh trong 20% nhịp rồi xẹp từ từ trong 62%, nghỉ 18% (0 ở hai đầu, đạo hàm 0)"""
    u = (u - MOUTH_PH) % 1.0
    a = lambda x: min(1.0, max(0.0, x)) ** 2 * (3 - 2 * min(1.0, max(0.0, x)))
    return a(u / 0.20) * (1 - a((u - 0.20) / 0.62))


MOUTH_S = spring_follow(lambda t: 0.020 * A_MOUTH * pop(t / T), 2.5, 0.35)
MOUTH_R = 62.0                                                  # bán kính ống (px): mép trên ống dâng lên khi phồng
# mỏ nhấp lên xuống theo nhịp thở (trễ nhẹ sau đầu: lò xo mềm), biên độ nhỏ; local x của con head = dọc
MOUTH_Y = spring_follow(lambda t: 2.0 * A_MBOB * br(t - 0.06 * T), 1.6, 0.4)
TRANSLATE["mouth"] = lambda t: (MOUTH_Y(t), 0.0)
TRANSLATE["eye_R"] = lambda t: (MOUTH_R * MOUTH_S(t) + MOUTH_Y(t), 0.0)   # mắt phải tựa mép trên ống: dâng theo ống
SCALE["mouth"] = lambda t: (1 + MOUTH_S(t), 1 + MOUTH_S(t))
N_KEYS = 15

CHAINS = [Chain(["flag1", "flag2"], FL_HZ, FL_Z, FL_W, 0.4, (1.0, -0.2))]
BLINK = None                     # chớp mắt dựng riêng bên dưới (mắt = region tách khỏi Head, không có ảnh mắt nhắm)

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
    K.write_anim(PATH, ANIM, anim)
    print(f"{ANIM}: {END} frame, {len(anim['bones'])} xương có key (chớp mắt F{int(BLINK_F)}) -> {PATH}")
    if not os.environ.get("ANIM_KIT_PATH") and not os.environ.get("ANIM_KIT_DRY"):      # IK -> key xoay cho arm_R / arm_L (xem bake_arms.py)
        import subprocess
        subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "bake_arms.py"), "idle"])
