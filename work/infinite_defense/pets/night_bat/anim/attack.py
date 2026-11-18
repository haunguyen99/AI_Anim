"""Night Bat Attack 30f: fold wings + rear head back to charge (0-9), burst (11-13), FIRE = frame 13 (wings wide, mouth open, ears flared, body thrust),
recoil/flap settle, back to Idle f0 at f30. Needs idle_pose in globals. Deltas on Idle f0, Catmull-Rom, keyed every frame."""
import math
N = 30
FIRE = 13
KF = [0, 4, 8, 11, 13, 16, 20, 25, 30]
def mir(v): return [-x for x in v]
W1z = [0, -10, -34, -4, 24, 14, 5, 2, 0]; W2z = [0, -3, -9, -2, 6, 3.5, 1.2, 0.5, 0]; W3z = W2z; W4z = [0, -5, -14, -4, 8, 5, 2, 1, 0]
W1y = [0, -6, -22, -5, 20, 10, 2, 0, 0]
E1x = [0, -5, -22, -10, 24, 10, 0, 0, 0]; E1z = [0, 0, 6, 0, -22, -12, -4, 0, 0]; E2x = [0, -4, -15, -5, 28, 12, -4, 0, 0]
D = {
 "CTL_Root_M":   {"rx": [0, -6, -14, -6, 10, 6, 2, 0, 0], "ty": [0, -0.03, -0.05, 0.04, 0.08, 0.04, 0.0, 0.01, 0], "tz": [0, -0.02, -0.05, 0.03, 0.12, 0.05, 0.0, 0, 0]},
 "CTL_Spine1_M": {"rx": [0, -3, -8, -3, 6, 3, 0, 0, 0]},
 "CTL_Head_M":   {"rx": [0, -6, -22, -12, 12, 4, 0, 0, 0]},
 "CTL_Jaw_M":    {"rx": [0, 0, 2, 0, 30, 22, 6, 0, 0]},
 "CTL_Wing1_L": {"rz": W1z, "ry": W1y}, "CTL_Wing1_R": {"rz": mir(W1z), "ry": mir(W1y)},
 "CTL_Wing2_L": {"rz": W2z}, "CTL_Wing2_R": {"rz": mir(W2z)},
 "CTL_Wing3_L": {"rz": W3z}, "CTL_Wing3_R": {"rz": mir(W3z)},
 "CTL_Wing4_L": {"rz": W4z}, "CTL_Wing4_R": {"rz": mir(W4z)},
 "CTL_Ear1_L": {"rx": E1x, "rz": E1z}, "CTL_Ear1_R": {"rx": E1x, "rz": mir(E1z)},
 "CTL_Ear2_L": {"rx": E2x}, "CTL_Ear2_R": {"rx": E2x},
}
IDX = {"rx": 0, "ry": 1, "rz": 2, "tx": 3, "ty": 4, "tz": 5}
def cr(f, vals):
    i = max(j for j in range(len(KF) - 1) if KF[j] <= f)
    i = min(i, len(KF) - 2)
    t = (f - KF[i]) / (KF[i + 1] - KF[i])
    p0 = vals[max(i - 1, 0)]; p1 = vals[i]; p2 = vals[i + 1]; p3 = vals[min(i + 2, len(vals) - 1)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
LAG = {"1": 0.0, "2": 1.0, "3": 2.0, "4": 3.0}      # frames each wing joint trails the one before (whip / overlap)
def _ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def _sm(t): return t * t * (3 - 2 * t)
def pose(f):
    P = idle_pose(0)
    for c, chs in D.items():
        n = c[8] if c.startswith("CTL_Wing") else None
        for ch, vals in chs.items():
            ff = f
            if n:                                         # wing joints trail their parent; the lag fades out so f30 == Idle f0 exactly
                ff = max(0.0, f - LAG[n] * (1 - _sm(_ramp(f, 21, 28))))
            P[c][IDX[ch]] += cr(ff, vals)
    # secondary motion on ry (wings swing forward/back, no up/down bounce): shiver while the wings are folded (f5-10), flutter that dies out after the burst (f13 on). Each joint lags 1.2 frames more.
    for side, k in (("L", 1), ("R", -1)):
        for n, amp in (("1", 16.0), ("2", 8.0), ("3", 9.0), ("4", 12.0)):
            lag = 1.2 * (int(n) - 1)
            t = f - lag
            shiver = 2.2 * math.sin(2 * math.pi * f / 3.0 + int(n)) * _sm(_ramp(f, 4, 6)) * (1 - _sm(_ramp(f, 10, 11.5)))
            flutter = amp * math.exp(-max(0.0, t - FIRE) / 8.0) * math.sin(2 * math.pi * (t - FIRE) / 9.0) * _sm(_ramp(t, FIRE - 0.5, FIRE + 1.5)) * (1 - _sm(_ramp(f, 24, 30)))
            P["CTL_Wing%s_%s" % (n, side)][1] += k * (shiver + flutter)      # FORWARD/BACK bounce (ry), not up/down
    return P
def build(api):
    CT = list(D) and list(idle_pose(0))
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):
        api.set_frame(f); api.select(CT); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); P = pose(f); [ (api.rotate(c, v[0], v[1], v[2]), api.move(c, v[3], v[4], v[5])) for c, v in P.items() ]
        api.select(CT); api.set_key()
    api.set_frame(1); api.set_frame(0)
