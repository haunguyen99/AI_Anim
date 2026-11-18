"""Kabuto Striker Attack 30f: ha thap + cui dau (dau sung chia ra truoc) f0-8, HUC TU DUOI LEN f8-12, FIRE = frame 12 (dau sung hat len cao nhat, than lao toi), theo da f12-22, f30 == Idle f0.
Can idle_pose (idle.pose) trong globals. Delta tren Idle f0, Catmull-Rom, key moi frame."""
import math
N = 30
CH = ("rx", "ry", "rz", "tx", "ty", "tz", "sx", "sy", "sz")
FIRE = 12
KF = [0, 4, 8, 10, 12, 14, 18, 22, 26, 30]
D = {
 "CTL_Root_M":   {"rx": [0, 3, 8, 0, -9, -6, -2, 0, 0, 0], "ty": [0, -.05, -.12, -.02, .12, .10, .05, .02, 0, 0], "tz": [0, -.04, -.08, .10, .22, .18, .08, .03, .005, 0]},
 "CTL_Spine1_M": {"rx": [0, 1, 3, -1, -3, -2, 0, 0, 0, 0]},
 "CTL_Chest_M":  {"rx": [0, 1, 3, -2, -3, -2, 0, 0, 0, 0]},
 "CTL_Neck_M":   {"rx": [0, 3, 6, -4, -7, -4, -1, 0, 0, 0]},
 "CTL_Head_M":   {"rx": [0, 4, 10, -6, -14, -8, -3, 0, 0, 0]},
 "CTL_SkirtF_M": {"rx": [0, 0, -4, 6, 10, 8, 2, -2, 0, 0]},
 "CTL_SkirtB_M": {"rx": [0, 0, 4, -4, -12, -10, -3, 2, 0, 0]},
}
for s, k in (("L", 1), ("R", -1)):
    D["CTL_Horn1_" + s] = {"rx": [0, 0, 3, 2, 6, 8, -5, 3, -1, 0], "rz": [k * v for v in [0, 0, -4, -4, 3, 5, 0, 0, 0, 0]]}
    D["CTL_Horn2_" + s] = {"rx": [0, 0, 4, 3, 10, 12, -8, 4, -1, 0], "rz": [k * v for v in [0, 0, -3, -3, 4, 6, 1, 0, 0, 0]]}
    D["CTL_Sode_" + s] = {"rz": [k * v for v in [0, -2, -4, 6, 12, 10, 3, -2, 0, 0]], "rx": [0, 0, 1, -2, -4, -3, 0, 0, 0, 0]}
    D["CTL_SkirtS_" + s] = {"rz": [k * v for v in [0, 0, -3, 4, 10, 8, 3, 0, 0, 0]]}
    D["CTL_FFoot_" + s] = {"rx": [0, -4, -10, -2, 18, 24, 10, -4, 2, 0]}
    D["CTL_RFoot_" + s] = {"rx": [0, -3, -9, -3, 14, 22, 12, -2, 1, 0]}
def cr(vals, f):
    for i in range(len(KF) - 1):
        if KF[i] <= f <= KF[i + 1]:
            t = (f - KF[i]) / (KF[i + 1] - KF[i]); p0 = vals[max(i - 1, 0)]; p1 = vals[i]; p2 = vals[i + 1]; p3 = vals[min(i + 2, len(KF) - 1)]
            return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
    return vals[-1]
def pose(f):
    P = idle_pose(0)
    for c, d in D.items():
        for a, vals in d.items(): P[c][CH.index(a)] += cr(vals, f)
    return P
def apply(api, P):
    for c, v in P.items():
        for a, x in zip(CH, v): api.set_attr(c + "." + a, float(x))
def build(api):
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1): api.set_frame(f); api.select(list(idle_pose(0))); api.set_key()
    for f in range(0, N + 1): api.set_frame(f); P = pose(f); apply(api, P); api.select(list(P)); api.set_key()
    api.set_frame(1); api.set_frame(0)
