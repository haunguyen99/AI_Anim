"""Hậu xử lý active: làm mượt đoạn cuối (F40 -> F72) bằng lọc Gaussian trên góc xoay mọi xương, giảm tốc liền một mạch
về idle F0 (không dừng rồi bật lại). Đầu F0 và F cuối giữ nguyên (trùng idle). Chạy sau active_cfg.py."""
import os, sys
os.environ.setdefault("ANIM_KIT_DRY", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools", "spine"))
import anim_kit as K

PATH = os.path.join(HERE, "mascot.json")
L, SIG = 72, float(os.environ.get("SMOOTH_SIG", "3.5"))
sk = K.load(PATH)
act, idle = sk["animations"]["active"], sk["animations"]["idle"]
W = lambda f: K.ss(38, 58, f) * (1 - K.ss(66, 72, f))
n = 0
for b, tl in act["bones"].items():
    if "rotate" not in tl:
        continue
    ga = K.spine_curve(tl["rotate"])
    gi = K.spine_curve(idle["bones"][b]["rotate"]) if b in idle["bones"] and "rotate" in idle["bones"][b] else (lambda f: 0.0)
    pad = int(3 * SIG) + 2
    ext = [ga(f) for f in range(0, L + 1)] + [gi(f) for f in range(1, pad + 1)]   # sau F72: idle tiếp tục
    bl = K.blur(ext, SIG)
    vals = [ga(f) * (1 - W(f)) + bl[f] * W(f) for f in range(L + 1)]
    tl["rotate"] = K.curve_keys([vals], ["value"], 0.08)
    n += 1
K.write_anim(PATH, "active", act, skel=sk)
K.mix(sk, "idle", "active", "mix", t_first=3.0)
K.write_anim(PATH, "mix", sk["animations"]["mix"], skel=sk)
print("làm mượt đuôi", n, "xương, sigma", SIG)
