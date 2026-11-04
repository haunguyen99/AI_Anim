"""Cấu hình active mẫu: Cừu Sakura — cá giãy nhảy lên, cừu hớn hở như cưỡi bò tót (bản giao 2026-11-02).
Bộ máy: tools/spine/active_engine.py, idle lấy từ ../../skillidle/examples/cuusakura_idle_cfg.py.
Chép sang thư mục anim của nhân vật mới (active_cfg.py), đổi IDLE + vai trò xương + mốc, chạy:
  .venv/Scripts/python.exe -I <thư mục anim>/active_cfg.py

Nhịp (72F): F0-10 lấy đà (ctrl chúi, hạ thấp) · F10-30 bật lên ~150 px, ngóc mũi theo vận tốc · trên không: một cú
quẫy đuôi, nhân vật nhắm mắt cười, vẫy tay · F47 rơi sâu hơn idle 32 px, đuôi văng xuống · nảy nhẹ F57 · lắng về idle F72.
Bản giao có key tay người dùng (active_user_keys.json: fish3, fish_tail, spine2, head, arm_L1) đè lên phần tính.
"""
import importlib.util, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "tools", "spine"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import anim_kit as K
from anim_kit import Chain, spl, lag
from anim_params import Params

spec = importlib.util.spec_from_file_location("idle_cfg", os.path.join(HERE, "..", "..", "skillidle", "examples", "cuusakura_idle_cfg.py"))
IDLE = importlib.util.module_from_spec(spec); spec.loader.exec_module(IDLE)
ANIM = "active"

P = Params(os.path.dirname(IDLE.PATH), "active", "Active", anim="active", run=["active_cfg.py"])
L = P.num("end", 72, 48, 120, 6, "Độ dài (frame)")
JUMP = P.num("jump", 150, 0, 400, 5, "Ctrl bay lên cao (px)")
ROTX = P.num("fish_rot", 1.0, 0, 2.5, 0.1, "Ctrl ngóc / chúi (x)")
WIG = P.num("wiggle", 1.0, 0, 2.5, 0.1, "Cú quẫy đuôi (x)")
SHEEP = P.num("sheep", 1.0, 0, 2.5, 0.1, "Nhân vật nảy (x)")
ARMS = P.num("arms", 1.0, 0, 2.5, 0.1, "Tay vung (x)")
MOUTH = P.num("mouth", 1.28, 1, 1.45, 0.01, "Miệng cười to (scaleX)")
EYE0 = P.num("eye_close", 20, 4, 40, 1, "Nhắm mắt cười từ frame")
EYE1 = P.num("eye_open", 44, 20, 66, 1, "Mở mắt lại ở frame")
DIP = P.num("dip", 32, 0, 120, 1, "Rơi sâu hơn idle (px)")
TAIL_OV = P.num("tail_overlap", 1.0, 0, 2.5, 0.1, "Thân / đuôi overlap (x)")
PH_K = P.num("phys_hz", 1.0, 0.4, 2.5, 0.05, "Physics lúc nhảy: độ cứng (x)")
PH_A = P.num("phys_max", 1.0, 0.3, 2.5, 0.05, "Physics lúc nhảy: góc văng tối đa (x)")
SH_K = P.num("sheep_hz", 1.0, 0.4, 2.5, 0.05, "Nhân vật: độ cứng thân (x, nhỏ = overlap nhiều)")
FB_GAIN = P.num("sheep_follow", 1.0, 0, 2.5, 0.05, "Nhân vật: ăn theo nhịp quẫy thân vật cưỡi (x)")
if not os.environ.get("ANIM_KIT_PATH"):
    P.save()
K_ = K_SCALE = L / 72.0
S = lambda keys, amp=1.0: spl(keys, amp, K_)
LG = lambda g, d, a=1.0: lag(g, d * K_, a)

# ---- đường bay của ctrl: chỉ key Y; góc ngóc / chúi và gia tốc suy từ đường bay (xoay luôn khớp dời) ----
FISH_X = S([(0, 0), (12, -3), (30, 8), (48, -3), (60, 1), (72, 0)])
FISH_Y = S([(0, 0), (10, -12), (30, JUMP), (47, -DIP), (57, DIP * 0.15), (66, -DIP * 0.03), (72, 0)])
ROT1, ACC, RAMP = K.path_drive(FISH_Y, L, max_rot=14.0 * ROTX, max_acc=14.0, ramp=8 * K_)
FLICK = S([(0, 0), (9, -3), (21, 15), (33, 2), (44, 0)], WIG)           # một cú quẫy đuôi lên lúc bật
# thân / đuôi: một tín hiệu chạy dọc thân = quẫy + quán tính gia tốc (bị chặn ở đáy -> đuôi văng xuống) + quán tính góc ctrl
PAD = 40
TAIL = K.arr_fn([(FLICK(f) - TAIL_OV * ACC(f) + 0.6 * TAIL_OV * (ROT1(f - 3) - ROT1(f))) * RAMP(f)
                 for f in range(-PAD, L + PAD + 1)], PAD)

SP1 = S([(0, 0), (11, 3.5), (24, -5), (40, 4), (51, 4.5), (61, -1), (72, 0)], SHEEP)
ARM_L = S([(0, 0), (12, 5), (26, -12), (42, -8), (54, 3), (64, 0), (72, 0)], ARMS)    # âm = giơ quạt lên
ARM_R = S([(0, 0), (12, -5), (28, 28), (44, 18), (58, 3), (72, 0)], ARMS)
LEG = S([(0, 0), (11, 3), (26, -7), (42, 8), (56, -2), (72, 0)], SHEEP)
SP1_Y = S([(0, 0), (20, -4), (37, 8), (49, -6), (58, 1), (72, 0)], SHEEP)          # nhổm khỏi lưng rồi dồn xuống
FMOUTH = S([(0, 0), (14, 0.1), (30, -0.12), (48, 0.05), (72, 0)])

ACT_ROT = {
    "fish1": ROT1,
    "fish2": LG(TAIL, 1, 0.35), "fish3": LG(TAIL, 3, 0.65), "fish_tail": LG(TAIL, 5, 1.0),
    "arm_L1": ARM_L, "arm_L2": LG(ARM_L, 3, 0.8), "fan": LG(ARM_L, 5, 1.2),
    "arm_R1": ARM_R, "arm_R2": LG(ARM_R, 3, 0.7),
    "leg_L": LEG, "leg_R": LG(LEG, 2, -1.0),
}
ACT_TR = {"fish1": (FISH_X, FISH_Y), "spine1": (lambda f: 0.0, SP1_Y)}
happy = lambda f: K.ss(12 * K_, 18 * K_, f) * (1 - K.ss(46 * K_, 56 * K_, f))
land = S([(0, 0), (44, 0), (49, 1), (56, -0.4), (64, 0), (72, 0)])
ACT_SCALE = {
    "mouth": lambda f, sx, sy: (sx * (1 - happy(f)) + MOUTH * happy(f), sy),
    "fish_mouth": lambda f, sx, sy: (sx + FMOUTH(f), sy + FMOUTH(f)),
    "hair_F": lambda f, sx, sy: (sx + 0.02 * land(f), sy + 0.05 * land(f)),
}
# nhân vật = chuỗi physics do ctrl kéo: spine1 cứng tự giữ thăng bằng (bù 3/4 góc ctrl), spine2 / head overlap tự sinh
REST_TGT = {"spine1": lambda f: -0.75 * ROT1(f), "spine2": lambda f: 0.0, "head": lambda f: 0.0}
REST_FB = {"spine1": (0.07, 2, "fish3"), "spine2": (0.10, 5, "fish3")}   # chỗ ngồi nghiêng theo nhịp quẫy thân vật cưỡi
CHAINS = [Chain(["spine1"], 3.2 * SH_K, 0.7, hz_act=3.2 * SH_K * PH_K, lim=12 * PH_A),
          Chain(["spine2"], 3.2 * SH_K, 0.65, hz_act=3.2 * SH_K * PH_K, lim=12 * PH_A),
          Chain(["head"], 3.2 * SH_K, 0.7, hz_act=3.2 * SH_K * PH_K, lim=10 * PH_A),
          Chain(["cloth1", "cloth2"], IDLE.CL_HZ, IDLE.CL_Z, IDLE.CL_W, 0.4, (1.0, -0.25), 2.2 * PH_K, 0.4, 55 * PH_A),
          Chain(["fin_side"], IDLE.FN_HZ, IDLE.FN_Z, IDLE.FN_W, 1.9, (0.3, -1.0), 2.4 * PH_K, 0.6, 22 * PH_A),
          Chain(["fin_bottom"], IDLE.FN_HZ * 1.1, IDLE.FN_Z, IDLE.FN_W, 3.1, (0.4, -1.0), 2.6 * PH_K, 0.6, 22 * PH_A),
          Chain(["ear_L1", "ear_L2"], 1.3, 0.3, 60.0, 4.2, (1.0, 0.0), 3.2 * PH_K, 0.55, 35 * PH_A),
          Chain(["ear_R1", "ear_R2"], 1.35, 0.3, 60.0, 5.1, (1.0, 0.0), 3.3 * PH_K, 0.55, 35 * PH_A),
          Chain(["horn_L"], 4.0, 0.5, hz_act=4.0 * PH_K, lim=4 * PH_A), Chain(["horn_R"], 4.0, 0.5, hz_act=4.0 * PH_K, lim=4 * PH_A),
          Chain(["bell1"], 1.5, 0.22, hz_act=2.0 * PH_K, zeta_act=0.4, lim=45 * PH_A),
          Chain(["bell2", "bell3"], 1.3, 0.22, hz_act=1.9 * PH_K, zeta_act=0.4, lim=45 * PH_A)]
USER_KEYS = os.path.join(os.path.dirname(IDLE.PATH), "active_user_keys.json")
EYES_CLOSED = dict(e0=EYE0, e1=EYE1, eyes=IDLE.EYES, brows=IDLE.BROWS, dx=-6.0)

if __name__ == "__main__":
    from active_engine import build_active
    build_active(sys.modules[__name__])
