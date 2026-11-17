"""Chrono Ouroboros Idle v7 (RIG v2: rồng thẳng không chân, có Hourglass). Hướng v6: sóng S đứng chạy dọc thân + lắc ngang 2 nhịp/vòng => số 8.
72F lặp liền (f72 == f0). Đồng hồ cát xoay ngược chiều kim đồng hồ (nhìn từ trên xuống, +Y) 1 vòng/72F.
HOVER tự hiệu chỉnh: điểm thấp nhất của mesh suốt vòng cách đất ~GAP."""
import math
N = 72
SP = ["Spine1", "Spine2", "Spine3", "Spine4"]; NK = ["Neck1", "Neck2", "Head"]; TL = ["Tail1", "Tail2", "Tail3", "Tail4", "Tail5"]
CTLS = ["CTL_%s_M" % n for n in ["Root"] + SP + NK + ["Jaw"] + TL + ["Hourglass"]]
LAMBDA = 2.4; K = 2 * math.pi / LAMBDA
AMP = 15.0; PAMP = 14.0
GAP = 0.11
CHAIN = [("Root", None), ("Spine1", "Root"), ("Spine2", "Spine1"), ("Spine3", "Spine2"), ("Spine4", "Spine3"), ("Neck1", "Spine4"), ("Neck2", "Neck1"), ("Head", "Neck2"),
         ("Tail1", "Root"), ("Tail2", "Tail1"), ("Tail3", "Tail2"), ("Tail4", "Tail3"), ("Tail5", "Tail4")]
OBS = ["Pet_chrono_ouroboros", "hourglass"]
def arc(api):
    W = {r['name']: r['world'] for r in api.joint_info()}
    d = lambda a, b: math.dist(W["DEF_%s_M" % a], W["DEF_%s_M" % b])
    S = {"Root": 0.0}
    for n, p in CHAIN[1:]:
        S[n] = S[p] + (-1 if n.startswith("Tail") else 1) * d(n, p)
    return S
def env(n):
    if n == "Head": return 0.45
    if n.startswith("Neck"): return 0.7
    if n.startswith("Tail"): return 1.0 + 0.1 * int(n[-1])
    return 1.0
def make_pose(S, hover):
    PAR = dict(CHAIN)
    def pose(f):
        p = 2 * math.pi * f / N; s_ = math.sin
        th = lambda n: env(n) * AMP * s_(K * S[n] + 2 * p + 0.5)
        tp = lambda n: env(n) * PAMP * s_(K * S[n] + p)
        P = {k: [0, 0, 0, 0, 0, 0] for k in CTLS}
        for n, par in CHAIN:
            P["CTL_%s_M" % n][0] = -(tp(n) - (tp(par) if par else 0.0))
            P["CTL_%s_M" % n][1] = th(n) - (th(par) if par else 0.0)
        P["CTL_Root_M"][4] = hover + 0.015 * s_(2 * p + 0.6)
        P["CTL_Jaw_M"][0] = 2.0 + 1.0 * s_(p - 0.8)
        P["CTL_Hourglass_M"][1] = 360.0 * f / N
        return P
    return pose
def apply(api, P):
    for c, v in P.items(): api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
def minY(api):
    return min(min(api.mesh_data(o, True)['positions'][1::3]) for o in OBS)
def calibrate(api, S):
    pose = make_pose(S, 0.0); lo = 1e9
    for f in range(0, N, 3):
        apply(api, pose(f)); api.set_frame(f + 1); api.set_frame(f); lo = min(lo, minY(api))
    apply(api, {c: [0] * 6 for c in CTLS}); api.set_frame(1); api.set_frame(0)
    return GAP - lo
def build(api, hover):
    S = arc(api); pose = make_pose(S, hover)
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1): api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, N + 1): api.set_frame(f); apply(api, pose(f)); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
