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
HEADRX = [(0, 0), (4, 12), (7, 24), (9, 22), (12, -8), (14, -8), (18, 2), (22, -1), (30, 0)]
EARRX = [(0, 0), (7, -16), (12, 10), (14, 9), (18, -3), (22, 2), (26, -1), (30, 0)]
EARRZ = [(0, 0), (8, 6), (12, -8), (14, -6), (18, 1), (30, 0)]            # nhân k (L âm = ra ngoài)
LEG1 = [(0, 0), (8, 10), (12, -12), (14, -10), (18, 6), (22, -2), (30, 0)]
LEG2 = [(0, 0), (8, 20), (12, -6), (14, -4), (18, 8), (22, -3), (30, 0)]
LEG3 = [(0, 0), (8, 15), (12, 0), (14, 0), (18, 8), (22, -3), (30, 0)]
FAN = [(0, 0), (3, -0.35), (6, -0.93), (7, -0.96), (8, -0.96), (11, -0.1), (12, 1.0), (14, 1.0), (16, 0.85), (18, 0.5), (22, 0.2), (26, 0.06), (30, 0)]   # delta so với FAN0
CURL = [(0, 0), (8.5, 0.0), (10, -0.2), (12, -0.8), (14, -0.6), (18, 0.25), (22, -0.1), (26, 0.03), (30, 0)]
CN = (3, 6, 9, 11, 13)
TUCK = [(0, 0), (3, 0.3), (6, 0.9), (7, 1.0), (8.5, 1.0), (10, 0.35), (12, -0.05), (14, 0), (30, 0)]   # đuôi cụp hẳn vào người ở F7-8
TG = {1: 0.0, 2: 0.2, 3: 0.6, 4: 1.0, 5: 1.0}
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
        off0 = 0.3 * abs(idx - 4)
        for n in range(5):
            LS = min(1.0, max(0.0, (f - 8.5) / 2.5)); off = off0 * LS; nl = n * LS    # gồng: mọi đuôi/đốt đồng nhất; trễ chỉ vào từ lúc bung
            ff = f - nl * 1.0 - off; K = T(CURL, ff); w = wig(f - n * 1.2 - off0); c = CN[n]
            c_ = P["CTL_Tail%d_%d_%s" % (k, n + 1, s)]
            tk = T(TUCK, f - nl * 0.5 - off * 0.5)
            for _i in range(3): c_[_i] *= (1 - 0.85 * max(0.0, min(1.0, tk)))    # gồng: bỏ dần sóng idle để mọi đuôi cụp đồng nhất
            back = c * K; down = -0.5 * c * K + 0.6 * c * w; cross = 0.5 * c * w
            ex_back = 0.0; ex_down = 0.0
            if s == "L": c_[1] += back + cross + ex_back; c_[2] += down + ex_down
            elif s == "R": c_[1] -= back + cross + ex_back; c_[2] -= down + ex_down
            else: c_[0] += -back + cross; c_[2] += down * 0.3
    fan = FAN0 + T(FAN, f)
    return P, fan
# ---- cụm đuôi hạ xuống sau lưng (pitch cả bó quanh trục X thế giới quanh gốc từng đuôi) ----
PITCH = -78.0    # độ; bó đuôi nằm xuôi ra sau, hơi chúc xuống (~15° dưới ngang, đo ảnh bên)
TP = [(0, 0), (3, 0.35), (6, 0.9), (7, 1.0), (8, 1.0), (12, 0.0), (30, 0)]
def _rx(a):
    c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a)); return [[1, 0, 0], [0, c, -s_], [0, s_, c]]
def _ry(a):
    c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a)); return [[c, 0, s_], [0, 1, 0], [-s_, 0, c]]
def _rz(a):
    c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a)); return [[c, -s_, 0], [s_, c, 0], [0, 0, 1]]
def _mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def _euler(M):   # R = Rz Ry Rx (Maya XYZ)
    b = math.asin(max(-1.0, min(1.0, -M[2][0]))); a = math.atan2(M[2][1], M[2][2]); c = math.atan2(M[1][0], M[0][0])
    return [math.degrees(a), math.degrees(b), math.degrees(c)]
def pitch_tails(P, alphas, f):
    w = T(TP, f)
    if abs(w) < 1e-6: return
    th = PITCH * w
    for (k, s), al in alphas.items():
        c_ = P["CTL_Tail%d_1_%s" % (k, s)]
        Rex = _mm(_rz(c_[2]), _mm(_ry(c_[1]), _rx(c_[0])))
        L = _mm(_rz(-al), _mm(_rx(th), _rz(al)))
        c_[0], c_[1], c_[2] = _euler(_mm(L, Rex))
def build_atk(api):
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):
        api.set_frame(f); api.select(KEYED); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); P, fan = pose_atk(f)
        api.set_attr("CTL_TailFan.fan", fan)
        al = {}
        for k, s in TAILS:
            al[(k, s)] = 0.0 if k == 1 else api.get_attr("CTL_Tail%d_1_%s_grp.rz" % (k, s))
        pitch_tails(P, al, f)
        apply(api, P, fan); api.select(KEYED); api.set_key()
    api.set_frame(1); api.set_frame(0); api.select([])
