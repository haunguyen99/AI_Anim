"""Cấu hình active: nhân vật cầm cờ ĐƯA TAY + CỜ LÊN, nhún xuống nhỏ, NẢY LÊN dứt khoát, lắng về idle.
GỌN 50F = 1,67 s (một lần, vào / ra đúng idle F0). Bộ máy tools/spine/active_engine.py (skill /skillactive); idle lấy từ idle_cfg.py.
Chạy: .venv/Scripts/python.exe -I work/daily_reward/spine/FlagChar/active_cfg.py

Nhịp (50F; ngực dẫn, đầu trễ ~2-3F, bàn tay trễ sau cánh tay ~3F; cán cờ (pole) dính tay, chỉ vải cờ vung physics):
  F0-8    lấy đà NHANH: đưa tay + cờ lên (raise ~18 px), ngực ngửa nhẹ
  F8-16   nhún xuống nhỏ (dip ~12 px), đáy ngắn F16-19
  F19-26  NẢY LÊN dứt khoát: 7 frame, giữa dốc đứng, dừng gọn ở đỉnh; ngực bật +7 px, tay + cờ vọt qua idle ~26 px (kick), đầu ngẩng
  F26-50  hồi về gọn: xuống nhẹ qua idle (F34) rồi lên lại nhỏ (F41), về idle F0 ở F50
Góc âm = chúi về trước (nhân vật nhìn sang phải). Trục X local của chest / spine / grip = DỌC, trục Y local = -X thế giới (ra trước).
"""
import importlib.util, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "tools", "spine"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import anim_kit as K
from anim_kit import Chain, spl
from anim_params import Params

spec = importlib.util.spec_from_file_location("idle_cfg", os.path.join(HERE, "idle_cfg.py"))
IDLE = importlib.util.module_from_spec(spec); spec.loader.exec_module(IDLE)
ANIM = "active"

P = Params(os.path.dirname(IDLE.PATH), "active", "Active", anim="active", run=["active_cfg.py"])
L = P.num("end", 50, 36, 120, 2, "Độ dài (frame)")
RAISE = P.num("raise", 18.0, 0, 50, 1, "Đưa tay + cờ lên lúc lấy đà (px)")
DIP = P.num("dip", 12.0, 0, 70, 1, "Nhún: hạ tay + cờ xuống dưới idle (px)")
KICK = P.num("kick", 26.0, 0, 60, 1, "Nảy lên: tay + cờ vọt qua idle (px)")
SQUAT = P.num("squat", 1.0, 0, 2.5, 0.1, "Nhún thân xuống (x)")
BOW = P.num("bow", 1.0, 0, 2.5, 0.1, "Thân chúi (x)")
NOD = P.num("nod", 1.0, 0, 2.5, 0.1, "Đầu gật (x)")
HND = P.num("hands", 1.0, 0, 2.5, 0.1, "Bàn tay overlap sau cánh tay: trễ + ngả (x)")
HLAG = P.num("hand_lag", 1.0, 0.3, 3, 0.1, "Bàn tay trễ sau cánh tay (x; 1 = 4F / 6F)")
BLINK_F = P.num("blink", 14, 1, 48, 1, "Chớp mắt lúc nhún xuống (frame)")
FL_K = P.num("flag_hz", 1.6, 0.4, 2.5, 0.05, "Cờ: độ cứng lúc diễn (x, nhỏ = mềm, vung nhiều)")
FL_ZA = P.num("flag_damp_act", 0.22, 0.05, 1, 0.01, "Cờ: giảm chấn lúc diễn (nhỏ = nảy nhiều nhịp)")
FL_DRV = P.num("flag_drive", 1.8, 0, 3, 0.1, "Cờ: bị tay kéo theo nhịp (x; vọt lên = cờ ngả ra sau, hạ = cờ hất ra trước)")
FL_LIM = P.num("flag_max", 55.0, 10, 80, 1, "Cờ: góc vung tối đa (độ)")
if not os.environ.get("ANIM_KIT_PATH"):
    P.save()
K_ = L / 50.0                                     # mốc viết cho 50F; đổi độ dài thì giãn đều
S = lambda keys, amp=1.0: spl(keys, amp, K_)

# dọc = local X: tay + cờ (raise -> dip nhỏ -> nảy lên dứt khoát). Key (36, 0.55 * KICK) nằm giữa dốc: tốc độ lớn nhất giữa cú nảy, hai đầu êm
GRIP_V = S([(0, 0), (8, RAISE), (16, -DIP), (19, -DIP * 1.08), (23, KICK * 0.55), (26, KICK), (34, -0.22 * KICK), (41, 0.07 * KICK), (45, 0), (50, 0)])
_fwd = S([(0, 0), (8, -3), (18, 4), (26, -5), (38, 1), (50, 0)])
lag_fn = lambda fn, d: (lambda f: fn(f - d * K_))
HR_LAG = HL_LAG = 3.0 * HLAG                                # hai bàn tay trễ ĐỀU sau cánh tay: cán cờ (trung bình) khớp cả hai tay
_end = lambda f: 1 - K.ss(43 * K_, 50 * K_, f)              # phần trễ của bàn tay tắt hẳn ở cuối (khớp idle F0)

ACT_ROT = {
    "spine": S([(0, 0), (8, 0.5), (15, -1.2), (20, -1.0), (28, 1.2), (37, -0.4), (50, 0)], BOW),
    "chest": S([(0, 0), (8, 1.2), (16, -2.8), (20, -2.4), (27, 2.6), (36, -0.8), (50, 0)], BOW),
    "head": S([(0, 0), (9, 2.0), (18, -7.0), (22, -5.5), (30, 4.5), (40, -1.2), (50, 0)], NOD),     # cúi thêm: đáy -7° (trước -3.8°)
    # bàn tay kéo lê theo cánh tay: cánh tay đi lên mà bàn tay còn thấp -> mũi bàn tay cụp (-); tay hạ nhanh -> mũi hất lên (+)
    "hand_R": lambda f: -0.30 * HND * _end(f) * (GRIP_V(f) - GRIP_V(f - HR_LAG * K_)),
    "hand_L": lambda f: -0.30 * HND * _end(f) * (GRIP_V(f) - GRIP_V(f - HL_LAG * K_)),
}
_ZERO = S([(0, 0), (50, 0)])
_hx = lambda lag: (lambda f: HND * 0.6 * _end(f) * (GRIP_V(f - lag * K_) - GRIP_V(f)))      # bàn tay trễ thêm theo phương dọc
ACT_TR = {
    "spine": (S([(0, 0), (8, 1.5), (15, -2.0), (19, -1.8), (26, 4.0), (36, -0.5), (50, 0)], SQUAT), _ZERO),
    "chest": (S([(0, 0), (8, 2.5), (15, -3.2), (19, -2.8), (26, 7.0), (36, -1.0), (44, 0.3), (50, 0)], SQUAT), _ZERO),
    "grip": (GRIP_V, lambda f: -_fwd(f)),
    "hand_R": (_ZERO, _hx(HR_LAG)),
    "hand_L": (_ZERO, _hx(HL_LAG)),
    "pole": (_ZERO, _hx(0.5 * (HR_LAG + HL_LAG))),         # cán cờ đi cùng trung bình hai bàn tay: không trôi khỏi tay
}
# ép dọc nhẹ lúc nhún, kéo dãn dọc lúc nảy lên (cộng lên scale idle)
_sq = S([(0, 0), (14, 0.8), (19, 0.7), (25, -1.3), (34, 0.2), (50, 0)], SQUAT)
ACT_SCALE = {
    "chest": lambda f, sx, sy: (sx * (1 - 0.030 * _sq(f)), sy * (1 + 0.014 * _sq(f))),
    "spine": lambda f, sx, sy: (sx * (1 - 0.015 * _sq(f)), sy * (1 + 0.007 * _sq(f))),
}
# vải cờ treo dọc nên chỉ dời dọc thì không vung ngang: đích lò xo ngả theo tốc độ dọc của tay (px/frame) = cờ bị kéo / hất theo nhịp người,
# lò xo mềm + giảm chấn thấp làm cờ nảy thêm vài nhịp sau mỗi cú; đốt cuối ngả nhiều hơn đốt giữa
_gv = lambda f: (GRIP_V(f + 0.5 * K_) - GRIP_V(f - 0.5 * K_)) / K_
# giai đoạn cờ F28 (cú nảy F19-26 kéo cờ ngả ra sau) hơi quá đà: giảm lực kéo 20% trong cửa sổ F18-30 (hai đầu mượt) => góc cờ quanh F28 giảm ~10% (lò xo lọc bớt)
_cut = lambda f: 1 - 0.20 * K.ss(16 * K_, 20 * K_, f) * (1 - K.ss(28 * K_, 32 * K_, f))
REST_TGT = {"flag1": lambda f: -0.9 * FL_DRV * _gv(f) * _cut(f), "flag2": lambda f: -1.6 * FL_DRV * _gv(f) * _cut(f)}
CHAINS = [Chain(["prop"], 1.8, 0.35, 0.0, 0.0, (1.0, 0.0), hz_act=2.2, zeta_act=0.35, lim=12),
          Chain(["flag1", "flag2"], IDLE.FL_HZ, IDLE.FL_Z, IDLE.FL_W, 0.4, (1.0, -0.2),
                hz_act=IDLE.FL_HZ * 0.85 * FL_K, zeta_act=FL_ZA, lim=FL_LIM)]
USER_KEYS = os.path.join(HERE, "active_user_keys.json")      # key tay của người dùng (nếu có) được giữ nguyên
K_SCALE = K_
BLEND = dict(base=(8, 36), env=(44, 50), phys=(0, 4, 42, 50), stiff=(0, 7, 34, 45))   # (mốc 50F, tự giãn theo K_SCALE) physics chạy tới F42: cờ còn nảy theo cú vọt
EYES_CLOSED = None

if __name__ == "__main__":
    from active_engine import build_active
    anim = build_active(sys.modules[__name__], write=False)
    IDLE.add_blink(anim, int(BLINK_F))
    K.write_anim(IDLE.PATH, ANIM, anim)
    print(f"{ANIM}: {L} frame, {len(anim['bones'])} xương (chớp mắt F{int(BLINK_F)}) -> {IDLE.PATH}")
    if not os.environ.get("ANIM_KIT_PATH") and not os.environ.get("ANIM_KIT_DRY"):      # IK -> key xoay cho arm_R / arm_L (xem bake_arms.py)
        import subprocess
        subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "bake_arms.py"), "active"])
