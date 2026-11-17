"""Chrono Ouroboros Idle v6 - uốn lượn hình SỐ 8 / vô cực (GDD).
Mỗi điểm thân: lên-xuống 1 nhịp/vòng (sóng S đứng chạy dọc thân) + lắc ngang 2 nhịp/vòng => vẽ số 8 nhìn từ trước. [v2:] TRƯỜN chữ S. 90f lặp (f90==f0).
Sóng chữ S (MẶT PHẲNG ĐỨNG: lên/xuống) chạy dọc thân từ đầu về đuôi (thân đi theo đường đầu vạch): góc tiếp tuyến theta(s,t)=env(s)*A*sin(k*s + p), s = độ dài cung từ hông,
xoay cục bộ mỗi khớp = theta(s_i) - theta(s_cha). Sóng dọc nhỏ lệch 90° cho cảm giác lướt. Lơ lửng 12 cm. Frame 0 = pose chữ S."""
import math
N = 72
SP = ["Spine1", "Spine2", "Spine3", "Spine4"]; NK = ["Neck1", "Neck2", "Head"]; TL = ["Tail1", "Tail2", "Tail3", "Tail4", "Tail5"]
LEG = ["%s%s_%s" % (a, b, s) for a in ("Fore", "Hind") for b in ("Leg1", "Leg2", "Foot") for s in "LR"]
CTLS = ["CTL_%s_M" % n for n in ["Root"] + SP + NK + ["Jaw"] + TL] + ["CTL_" + l for l in LEG]
LAMBDA = 2.4; K = 2 * math.pi / LAMBDA
AMP = 15.0; PAMP = 14.0   # AMP = uốn ngang (nhỏ), PAMP = sóng chữ S theo chiều dọc (chính)
HOVER = 0.28   # nâng nền để đáy sóng vẫn cách đất ~12 cm
CHAIN = [("Root", None)] + [("Spine1", "Root"), ("Spine2", "Spine1"), ("Spine3", "Spine2"), ("Spine4", "Spine3"), ("Neck1", "Spine4"), ("Neck2", "Neck1"), ("Head", "Neck2"),
         ("Tail1", "Root"), ("Tail2", "Tail1"), ("Tail3", "Tail2"), ("Tail4", "Tail3"), ("Tail5", "Tail4")]
def arc(api):
    W = {r['name']: r['world'] for r in api.joint_info()}
    import math as m
    def d(a, b): return m.dist(W["DEF_%s_M" % a], W["DEF_%s_M" % b])
    S = {"Root": 0.0}
    for n, p in CHAIN[1:]:
        sgn = -1 if n.startswith("Tail") else 1
        S[n] = S[p] + sgn * d(n, p)
    return S, W
def env(n, s):
    if n == "Head": return 0.45
    if n.startswith("Neck"): return 0.7
    if n.startswith("Tail"): return 1.0 + 0.1 * int(n[-1])
    return 1.0
def make_pose(S, W):
    PAR = dict(CHAIN)
    def pose(f):
        p = 2 * math.pi * f / N; s_ = math.sin
        th = lambda n: env(n, S[n]) * AMP * s_(K * S[n] + 2 * p + 0.5)   # ngang: 2 nhịp/vòng => số 8
        tp = lambda n: env(n, S[n]) * PAMP * s_(K * S[n] + p)
        P = {k: [0, 0, 0, 0, 0, 0] for k in CTLS}
        for n, par in CHAIN:
            ry = th(n) - (th(par) if par else 0.0)
            rx = -(tp(n) - (tp(par) if par else 0.0))
            P["CTL_%s_M" % n][0] = rx; P["CTL_%s_M" % n][1] = ry
        P["CTL_Root_M"][4] = HOVER + 0.015 * s_(2 * p + 0.6)
        P["CTL_Jaw_M"][0] = 2.0 + 1.0 * s_(p - 0.8)
        for l in LEG:
            side = l[-1]; k = 1 if side == "L" else -1; part = l[4:-2]; fore = l.startswith("Fore")
            sl = S["Spine4"] if fore else -0.15          # vị trí chân dọc thân
            amp = {"Leg1": 5, "Leg2": 7, "Foot": 9}[part]; lag = {"Leg1": 0.0, "Leg2": 0.5, "Foot": 1.0}[part]
            ph = p + K * sl - lag
            P["CTL_" + l][0] = amp * s_(ph) + (4 if part != "Leg1" else 0)
            P["CTL_" + l][2] = k * 0.5 * amp * s_(ph + 0.9)
        return P
    return pose
def apply(api, P):
    for c, v in P.items(): api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
def build(api):
    S, W = arc(api); pose = make_pose(S, W)
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1): api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, N + 1): api.set_frame(f); apply(api, pose(f)); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
