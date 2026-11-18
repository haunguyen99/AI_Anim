"""Kitsune Nine-Mist Attack 30f (0-30). F0 = F30 = Idle F0. F12 = BAN (event). Cong thuc cong len pose Idle F0 (dùng chiều xoay trong idle.py)."""
import math
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\anim\idle.py").read())
N = 30
P0, FAN0 = pose(0)
def T(pts, f):
    # Catmull-Rom (tiep tuyen theo thoi gian) qua cac key (frame, gia tri); ngoai khoang = giu
    if f <= pts[0][0]: return pts[0][1]
    if f >= pts[-1][0]: return pts[-1][1]
    for i in range(len(pts) - 1):
        if pts[i][0] <= f <= pts[i + 1][0]: break
    t0, v0 = pts[i]; t1, v1 = pts[i + 1]; h = t1 - t0; u = (f - t0) / h
    def tan(j):
        if j <= 0 or j >= len(pts) - 1: return 0.0
        return (pts[j + 1][1] - pts[j - 1][1]) / (pts[j + 1][0] - pts[j - 1][0])
    m0 = tan(i) * h; m1 = tan(i + 1) * h
    return (2*u**3 - 3*u**2 + 1) * v0 + (u**3 - 2*u**2 + u) * m0 + (-2*u**3 + 3*u**2) * v1 + (u**3 - u**2) * m1
# (frame, value) - 8 = gồng, 12 = bắn, 14 = hết giữ, 30 = idle
HOV = [(0, 0), (8, -0.04), (10, 0.0), (12, 0.06), (14, 0.06), (18, -0.03), (22, 0.012), (26, -0.004), (30, 0)]
FWD = [(0, 0), (8, -0.03), (12, 0.06), (14, 0.06), (18, 0.01), (22, 0), (30, 0)]
ROOTRX = [(0, 0), (8, -6), (12, 4), (14, 4), (18, -1.5), (22, 0.5), (30, 0)]
SPRX = [(0, 0), (8, -5), (12, 4), (14, 4), (18, -1), (22, 0.5), (30, 0)]
HEADRX = [(0, 0), (8, 8), (12, -8), (14, -8), (18, 2), (22, -1), (30, 0)]
EARRX = [(0, 0), (8, -12), (12, 10), (14, 9), (18, -3), (22, 2), (26, -1), (30, 0)]
EARRZ = [(0, 0), (8, 6), (12, -8), (14, -6), (18, 1), (30, 0)]            # nhân k (L âm = ra ngoài)
LEG1 = [(0, 0), (8, 10), (12, -12), (14, -10), (18, 6), (22, -2), (30, 0)]
LEG2 = [(0, 0), (8, 20), (12, -6), (14, -4), (18, 8), (22, -3), (30, 0)]
LEG3 = [(0, 0), (8, 15), (12, 0), (14, 0), (18, 8), (22, -3), (30, 0)]
FAN = [(0, 0), (7, -0.7), (10, 0.35), (12, 1.0), (14, 1.0), (16, 0.85), (18, 0.5), (22, 0.2), (26, 0.06), (30, 0)]   # delta so với FAN0
CURL = [(0, 0), (7, 1.0), (10, -0.2), (12, -0.8), (14, -0.6), (18, 0.25), (22, -0.1), (26, 0.03), (30, 0)]
CN = (2, 5, 8, 10, 12)
def wig(f):   # rung tắt dần sau khi bắn
    t = f - 14; return 0.0 if t < 0 else math.exp(-t / 5.0) * math.sin(2 * math.pi * t / 6.0)
def pose_atk(f):
    P = {k: list(v) for k, v in P0.items()}; fan = FAN0
    if f >= N: return P, fan
    r = P["CTL_Root_M"]; r[4] += T(HOV, f); r[5] += T(FWD, f); r[0] += T(ROOTRX, f)
    P["CTL_Spine1_M"][0] += T(SPRX, f)
    P["CTL_Head_M"][0] += T(HEADRX, f - 1)
    for s, k in (("L", 1), ("R", -1)):
        P["CTL_Ear1_" + s][0] += T(EARRX, f - 1); P["CTL_Ear1_" + s][2] += k * T(EARRZ, f - 1)
        P["CTL_Ear2_" + s][0] += 0.8 * T(EARRX, f - 2); P["CTL_Ear2_" + s][2] += k * 0.8 * T(EARRZ, f - 2)
        for pre in ("FLeg", "BLeg"):
            lag = 2 + (1 if pre == "BLeg" else 0)
            P["CTL_%s1_%s" % (pre, s)][0] += T(LEG1, f - lag); P["CTL_%s2_%s" % (pre, s)][0] += T(LEG2, f - lag - 1); P["CTL_%s3_%s" % (pre, s)][0] += T(LEG3, f - lag - 2)
    for idx, (k, s) in enumerate(TAILS):
        off = 0.3 * abs(idx - 4)
        for n in range(5):
            ff = f - n * 1.0 - off; K = T(CURL, ff); w = wig(f - n * 1.2 - off); c = CN[n]
            c_ = P["CTL_Tail%d_%d_%s" % (k, n + 1, s)]
            back = c * K; down = -0.5 * c * K + 0.6 * c * w; cross = 0.5 * c * w
            if s == "L": c_[1] += back + cross; c_[2] += down
            elif s == "R": c_[1] -= back + cross; c_[2] -= down
            else: c_[0] += -back + cross; c_[2] += down * 0.3
    fan = FAN0 + T(FAN, f)
    return P, fan
def build_atk(api):
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):
        api.set_frame(f); api.select(KEYED); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); P, fan = pose_atk(f); apply(api, P, fan); api.select(KEYED); api.set_key()
    api.set_frame(1); api.set_frame(0); api.select([])
