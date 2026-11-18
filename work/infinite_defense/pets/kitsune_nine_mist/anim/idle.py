"""Kitsune Nine-Mist Idle 48f loop (f0==f48). Hover 12 cm; body bobs slowly, legs/ears/head follow late, 9 tails ripple root->tip.
Axes (đo 2026-11-14, xoay + 20°): tail L: rz+ = đầu đuôi lên, ry+ = ra sau; tail R mirror (rz, ry đảo dấu); tail giữa: rz+ = sang -X, rx+ = ra trước.
Chân: rx+ = bàn chân ra sau, rz+ = ra ngoài (L). Đầu: rx+ = gật xuống, ry+ = quay trái (+X). Tai: rx+ = ra trước, rz+ = vào trong (L)."""
import math
N = 48
S = math.sin
TAILS = [(5, "L"), (4, "L"), (3, "L"), (2, "L"), (1, "M"), (2, "R"), (3, "R"), (4, "R"), (5, "R")]
TCTL = ["CTL_Tail%d_%d_%s" % (k, n, s) for k, s in TAILS for n in range(1, 6)]
CTLS = ["CTL_Root_M", "CTL_Spine1_M", "CTL_Head_M"] + ["CTL_%s_%s" % (n, s) for n in ("Ear1", "Ear2", "FLeg1", "FLeg2", "FLeg3", "BLeg1", "BLeg2", "BLeg3") for s in "LR"] + TCTL
HOVER = 0.12
AMP = (2.4, 3.9, 5.4, 6.9, 8.4)    # độ mỗi đốt (cộng dồn theo chuỗi)
LAG = 0.52                          # 4F mỗi đốt
def pose(f):
    p = 2 * math.pi * f / N
    P = {k: [0, 0, 0, 0, 0, 0] for k in CTLS}     # rx ry rz tx ty tz
    P["CTL_Root_M"][:3] = [1.5 * S(p - 0.6), 1.5 * S(p + 0.5), 2.5 * S(p + 1.0)]
    P["CTL_Root_M"][3:] = [0.008 * S(p + 1.6), HOVER + 0.015 * S(p), 0.006 * S(p + 0.8)]
    P["CTL_Spine1_M"][:3] = [1.5 * S(p - 0.9), 2.0 * S(p - 0.4), 1.0 * S(p - 1.2)]
    P["CTL_Head_M"][:3] = [-1 + 2.0 * S(p - 1.6), 5.0 * S(p - 0.7) + 1.5 * S(2 * p), 1.5 * S(p - 2.0)]
    for s, k, ph in (("L", 1, 0.0), ("R", -1, 0.8)):
        P["CTL_Ear1_" + s][:3] = [4 * S(p - 2.2 - ph), 0, k * (-3 - 3 * S(p - 2.0 - ph))]
        P["CTL_Ear2_" + s][:3] = [5 * S(p - 2.8 - ph), 0, k * (-3 * S(p - 2.9 - ph))]
        for pre, lg in (("FLeg", 0.0), ("BLeg", 0.5)):
            q = p - 0.9 - lg - (0.3 if s == "R" else 0)
            P["CTL_%s1_%s" % (pre, s)][:3] = [4 * S(q), 0, k * 2 * S(q - 0.5)]
            P["CTL_%s2_%s" % (pre, s)][:3] = [4 * S(q - 0.5), 0, 0]
            P["CTL_%s3_%s" % (pre, s)][:3] = [5 * S(q - 1.0), 0, 0]
    for idx, (k, s) in enumerate(TAILS):
        ph = 0.45 * (idx - 4); sc = 0.85 + 0.05 * abs(idx - 4)
        for n in range(5):
            q = p - LAG * n + ph; a = AMP[n] * sc
            main = a * (S(q) + 0.3 * S(2 * q + 0.7)); cross = 0.6 * a * S(q + 1.57)
            c = P["CTL_Tail%d_%d_%s" % (k, n + 1, s)]
            if s == "L": c[2] = main; c[1] = cross
            elif s == "R": c[2] = -main; c[1] = -cross
            else: c[2] = main; c[0] = cross
    fan = 0.05 + 0.10 * S(p - 1.2)
    return P, fan
def apply(api, P, fan):
    for c, v in P.items():
        api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
    api.set_attr("CTL_TailFan.fan", fan)
KEYED = CTLS + ["CTL_TailFan"]
def build(api):
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):                      # key vỡ kênh rỗng: key 0 mọi frame trước rồi mới ghi giá trị
        api.set_frame(f); api.select(KEYED); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); P, fan = pose(f); apply(api, P, fan); api.select(KEYED); api.set_key()
    api.set_frame(1); api.set_frame(0); api.select([])
    for c in CTLS:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
    try: api.set_infinity("CTL_TailFan.fan", "cycle", "cycle")
    except Exception as e: print("inf fan", e)
