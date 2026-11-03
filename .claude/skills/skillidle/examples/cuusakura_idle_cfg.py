"""Cấu hình idle mẫu: Cừu Sakura cưỡi cá koi (work/test/spine/CuuSakura), bản đã duyệt 2026-11-02.
Bộ máy: tools/spine/idle_engine.py. Chép file này sang thư mục anim của nhân vật mới (đặt tên idle_cfg.py), đổi PATH
và bảng vai trò xương, rồi chạy:
  .venv/Scripts/python.exe -I <thư mục anim>/idle_cfg.py

Vai trò xương ở nhân vật này (đổi tên theo rig mới):
  ctrl tổng (vật cưỡi) fish1 · thân vật cưỡi fish2 -> fish3 -> fish_tail · vây fin_side / fin_bottom (physics)
  nhân vật spine1 -> spine2 -> head · tay quạt arm_L1 -> arm_L2 -> fan · tay kia arm_R1 -> arm_R2 · chân leg_L / leg_R
  phần mềm: tai ear_*1-2, chuông bell1 / bell2-3 (quán tính), khăn đầu cloth1-2 (physics), sừng horn_* (nhích nhẹ)
  mặt: mouth (scaleX = mở), mắt eye_L / eye_R (slot có eyeClose_*), mày eyebrow_*, tóc mái hair_F (chỉ scale)
"""
import math, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "tools", "spine"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import anim_kit as K
from anim_kit import Chain, FPS
from anim_params import Params

FOLDER = os.path.join(ROOT, "work", "test", "spine", "CuuSakura")
PATH = os.environ.get("ANIM_KIT_PATH") or os.path.join(FOLDER, "cuusakura.json")
ANIM = "idle"

# ---- tham số chỉnh trên Spine Live (thanh trượt "Tham số anim"); số mặc định = bản đã duyệt ----
P = Params(os.path.dirname(PATH), "idle", "Idle", anim="idle", run=["idle_cfg.py"])
END = P.num("end", 96, 48, 180, 6, "Độ dài loop (frame)")
A_FISH = P.num("fish", 1.0, 0, 3, 0.1, "Ctrl xoay / nhấp nhô (x)")
A_WAVE = P.num("wave", 1.0, 0, 3, 0.1, "Thân / đuôi vật cưỡi uốn (x)")
A_SHEEP = P.num("sheep", 1.0, 0, 3, 0.1, "Nhân vật ngả nghiêng (x)")
A_FAN = P.num("fan", 1.0, 0, 3, 0.1, "Tay cầm đồ vẫy (x)")
A_LEG = P.num("leg", 1.0, 0, 3, 0.1, "Chân đung đưa (x)")
G_OVL = P.num("overlap", 1.0, 0, 3, 0.1, "Overlap tai / chuông (x)")
L_OVL = P.num("lag", 1.0, 0.3, 3, 0.1, "Độ trễ overlap (x)")
A_MOUTH = P.num("mouth", 0.18, 0, 0.4, 0.01, "Miệng mở thêm tối đa (0.18 = +18%)")
A_HORN = P.num("horn", 1.0, 0, 3, 0.1, "Sừng lắc (x)")
BLINK_F = P.num("blink", 62, 1, 160, 1, "Chớp mắt bắt đầu (frame)")
CL_HZ = P.num("cloth_hz", 0.9, 0.3, 3, 0.05, "Khăn: độ cứng (Hz, nhỏ = mềm)")
CL_Z = P.num("cloth_damp", 0.22, 0.05, 1, 0.01, "Khăn: giảm chấn")
CL_W = P.num("cloth_wind", 320.0, 0, 800, 10, "Khăn: gió")
FN_HZ = P.num("fin_hz", 1.2, 0.3, 4, 0.05, "Vây: độ cứng (Hz)")
FN_Z = P.num("fin_damp", 0.30, 0.05, 1, 0.01, "Vây: giảm chấn")
FN_W = P.num("fin_water", 500.0, 0, 1500, 10, "Vây: nước đẩy")
if not os.environ.get("ANIM_KIT_PATH"):
    P.save()

T = END / FPS
s = lambda amp, freq=1, ph=0.0: K.wave(amp, freq, ph, T)

# sóng riêng (độ): (biên độ, số nhịp / loop, pha theo vòng). Nhịp 1 = cả loop, nhịp 2 = vẫy / quẫy nhanh hơn.
# Pha tăng dần dọc chuỗi = đốt sau trễ hơn đốt trước.
OWN = {
    "fish1": s(3 * A_FISH),
    "fish2": s(2 * A_WAVE, 2, 0.15), "fish3": s(3.5 * A_WAVE, 2, 0.30), "fish_tail": s(7 * A_WAVE, 2, 0.45),
    "spine1": s(2 * A_SHEEP, 1, 0.10), "spine2": s(1.5 * A_SHEEP, 1, 0.18), "head": s(2.5 * A_SHEEP, 1, 0.28),
    "arm_L1": s(4 * A_FAN, 2, 0.0), "arm_L2": s(6 * A_FAN, 2, 0.10), "fan": s(10 * A_FAN, 2, 0.22),
    "arm_R1": s(4 * A_SHEEP, 1, 0.20), "arm_R2": s(5 * A_SHEEP, 1, 0.30),
    "leg_L": s(4 * A_LEG, 1, 0.30), "leg_R": s(4 * A_LEG, 1, -0.20),
    "ear_L1": s(3, 1, 0.35), "ear_L2": s(4, 1, 0.45), "ear_R1": s(3, 1, 0.40), "ear_R2": s(4, 1, 0.50),
    "bell1": s(5, 1, 0.30), "bell2": s(4, 1, 0.35), "bell3": s(6, 1, 0.50),
    "horn_L": s(0.8 * A_HORN, 1, 0.30), "horn_R": s(0.8 * A_HORN, 1, 0.36),
}
# quán tính (gain, trễ frame): gain > 1 = vật treo lỏng (tai, chuông)
INERTIA = {
    "fish2": (0.5, 4), "fish3": (0.5, 4), "fish_tail": (0.8, 5),
    "spine1": (1.0, 8), "spine2": (0.6, 5), "head": (0.7, 6),
    "arm_L1": (0.5, 5), "arm_L2": (0.5, 5), "fan": (0.6, 5), "arm_R1": (0.6, 6), "arm_R2": (0.6, 5),
    "leg_L": (0.5, 6), "leg_R": (0.5, 6),
    "ear_L1": (1.2 * G_OVL, 8), "ear_L2": (1.2 * G_OVL, 6), "ear_R1": (1.2 * G_OVL, 8), "ear_R2": (1.2 * G_OVL, 6),
    "bell1": (1.5 * G_OVL, 10), "bell2": (1.5 * G_OVL, 10), "bell3": (1.3 * G_OVL, 6),
    "horn_L": (0.25 * A_HORN, 6), "horn_R": (0.25 * A_HORN, 6),
}
TRANSLATE = {"fish1": lambda t: (0.0, 6 * A_FISH * math.cos(2 * math.pi * t / T))}   # ctrl nhấp nhô, lệch 1/4 nhịp so với xoay
SCALE = {
    "fish_mouth": lambda t: (1 - 0.05 * (1 - math.cos(4 * math.pi * t / T)),) * 2,
    "mouth": lambda t: (1 + A_MOUTH / 2 * (1 - math.cos(2 * math.pi * t / T)), 1.0),      # chỉ scaleX = mở miệng
    "hair_F": lambda t: (1 + 0.015 * math.sin(2 * math.pi * t / T), 1 + 0.035 * math.sin(2 * math.pi * t / T)),
}
CHAINS = [Chain(["cloth1", "cloth2"], CL_HZ, CL_Z, CL_W, 0.4, (1.0, -0.25)),
          Chain(["fin_side"], FN_HZ, FN_Z, FN_W, 1.9, (0.3, -1.0)),
          Chain(["fin_bottom"], FN_HZ * 1.1, FN_Z, FN_W, 3.1, (0.4, -1.0))]
EYES = [("eye_L", "eyeClose_L", "eye_L", "eye_L"), ("eye_R", "eyeClose_R", "eye_R", "eye_R")]
BROWS = ["eyebrow_L", "eyebrow_R"]
BLINK = dict(frame=BLINK_F, eyes=EYES, brows=BROWS, dx=-6.0)

if __name__ == "__main__":
    from idle_engine import build_idle
    build_idle(sys.modules[__name__])
