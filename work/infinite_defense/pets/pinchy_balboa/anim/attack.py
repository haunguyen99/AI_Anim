"""Pinchy Balboa Attack 30f: weave (0-8), wind-up right glove back + body twist (11), straight punch forward with the right glove (body twists 45 deg), FIRE = frame 16, recoil, settle to Idle f0 at f30.
Needs idle_pose in globals. Deltas on Idle f0, Catmull-Rom, keyed every frame. Right = -x."""
import math
N = 30
FIRE = 16
KF = [0, 4, 8, 11, 14, 16, 19, 23, 30]
D = {
 "CTL_Root_M": {"rz": [0, -10, 10, 4, 0, 0, 0, 0, 0], "tx": [0, 0.05, -0.05, -0.03, 0, 0, 0, 0, 0],
                "ty": [0, -0.04, -0.06, -0.04, 0.02, 0.03, 0, 0, 0], "ry": [0, 2, 4, -18, 25, 45, 35, 10, 0],
                "rx": [0, 3, 12, 6, 8, 12, 6, 2, 0], "tz": [0, 0, -0.02, -0.04, 0.08, 0.15, 0.10, 0.02, 0]},
 "CTL_Head_M": {"ry": [0, 3, 0, 8, -12, -22, -15, -4, 0], "rx": [0, -3, -6, -4, 2, 5, 2, 0, 0]},
 "CTL_Arm1_R": {"ry": [0, 0, -5, -25, 5, 10, 8, 3, 0], "rz": [0, 0, 3, 10, -15, -25, -18, -6, 0]},
 "CTL_Arm2_R": {"ry": [0, 0, 3, 15, 4, 8, 6, 2, 0], "rz": [0, 0, 0, -15, 25, 55, 38, 12, 0]},
 "CTL_Arm3_R": {"ry": [0, 0, 2, 8, 2, 4, 3, 1, 0], "rz": [0, 0, 0, -5, 6, 10, 7, 2, 0]},
 "CTL_Glove_R": {"rz": [0, 0, 0, -5, 8, 15, 10, 3, 0]},
 "CTL_Arm1_L": {"rz": [0, 3, 4, 5, 6, 5, 3, 1, 0], "ry": [0, -3, -5, -6, -8, -6, -3, 0, 0]},
 "CTL_Arm2_L": {"rz": [0, 2, 3, 3, 4, 3, 2, 0, 0]}, "CTL_Arm3_L": {"rz": [0, 2, 2, 3, 4, 3, 1, 1, 0]},
 "CTL_BandA1_M": {"rz": [0, 6, 10, 14, -12, -20, -8, -2, 0]}, "CTL_BandA2_M": {"rz": [0, 6, 12, 18, -16, -26, -10, -2, 0]},
 "CTL_BandB1_M": {"rz": [0, 5, 8, 12, -10, -18, -7, -2, 0]}, "CTL_BandB2_M": {"rz": [0, 5, 10, 16, -14, -24, -9, -2, 0]},
}
for g in "FMB":
    for sd in "LR":
        D["CTL_Leg%s_%s" % (g, sd)] = {"rx": [0, 3, 6, 10, -6, -10, -3, 0, 0]}
        D["CTL_Leg%sTip_%s" % (g, sd)] = {"rx": [0, 5, 10, 18, -8, -12, -4, 0, 0]}
# Faster, heavier punch: wind-up (f11) held to f13, snap to the fire pose in 2 frames (f13 -> f15), impact held f15-17, quick recoil, settle f30.
# Values below were keyed on the old timing [0,4,8,11,14,16,19,23,30]; map them to the new one.
KF = [0, 4, 8, 11, 13, 15, 17, 21, 30]; FIRE = 15
for _c, _chs in D.items():
    for _ch, L in _chs.items():
        _chs[_ch] = [L[0], L[1], L[2], L[3], L[3], L[5], L[5] * 0.97, L[6] * 0.55, L[8]]
D["CTL_Root_M"]["ry"][3] = D["CTL_Root_M"]["ry"][4] = -26       # bigger wind-up twist
D["CTL_Arm1_R"]["ry"][3] = D["CTL_Arm1_R"]["ry"][4] = -35       # right arm pulled further back
D["CTL_Root_M"]["rx"][5] = 14; D["CTL_Root_M"]["ty"][5] = -0.01  # body drops into the punch
IDX = {"rx": 0, "ry": 1, "rz": 2, "tx": 3, "ty": 4, "tz": 5}
LAGS = {"Arm2": 0.3, "Arm3": 0.3, "Glove": 0.5, "Tip": 1.0, "A2": 2.0, "B2": 2.0}
def cr(f, vals):
    i = min(max(j for j in range(len(KF) - 1) if KF[j] <= f), len(KF) - 2)
    t = (f - KF[i]) / (KF[i + 1] - KF[i])
    p0 = vals[max(i - 1, 0)]; p1 = vals[i]; p2 = vals[i + 1]; p3 = vals[min(i + 2, len(vals) - 1)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
def _ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def _sm(t): return t * t * (3 - 2 * t)
def pose(f):
    P = idle_pose(0)
    for c, chs in D.items():
        lag = max([v for k, v in LAGS.items() if k in c] or [0.0])
        ff = max(0.0, f - lag * (1 - _sm(_ramp(f, 21, 28))))      # trailing joints; lag fades so f30 == Idle f0
        for ch, vals in chs.items(): P[c][IDX[ch]] += cr(ff, vals)
    return P
def build(api):
    CT = list(idle_pose(0))
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):
        api.set_frame(f); api.select(CT); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); P = pose(f)
        for c, v in P.items(): api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
        api.select(CT); api.set_key()
    api.set_frame(1); api.set_frame(0)
