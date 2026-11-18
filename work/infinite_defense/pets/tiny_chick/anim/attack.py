"""Tiny Chick Attack 30f: crouch (0-6), spring up (6-10), peck lunge, FIRE = frame 12, recoil, settle back to Idle f0 at f30.
Needs idle_pose (idle.pose) in globals. Deltas on top of Idle f0; interpolated with Catmull-Rom, keyed every frame."""
import math
N = 30
FIRE = 12
KF = [0, 5, 8, 10, 12, 15, 19, 24, 30]
# per control: channel -> values at KF. channels rx ry rz tx ty tz
D = {
 "CTL_Root_M":   {"rx": [0, -4, -6, 5, 14, 6, -2, 1, 0], "ty": [0, -0.05, 0.03, 0.17, 0.20, 0.10, 0.0, 0.012, 0], "tz": [0, -0.05, -0.08, 0.04, 0.22, 0.06, -0.015, 0.0, 0]},
 "CTL_Spine1_M": {"rx": [0, -3, -4, 3, 8, 4, -1, 0, 0]},
 "CTL_Head_M":   {"rx": [0, -3, -6, 5, 12, 5, -2, 0, 0], "tz": [0, -0.02, -0.04, 0.02, 0.07, 0.02, 0, 0, 0]},
 "CTL_Beak_M":   {"rx": [0, -2, -3, 3, 6, 2, -1, 0, 0]},
 "CTL_Cap_M":    {"rx": [0, 6, 22, -28, -18, 10, -6, 2, 0], "rz": [0, 0, 4, -3, 5, -2, 1, 0, 0]},
 "CTL_Shell_M":  {"rx": [0, 4, 8, -14, -10, 6, -4, 1, 0], "rz": [0, 0, 5, -4, 3, -2, 1, 0, 0]},
 "CTL_Ankle_L":  {"rx": [0, 12, 26, 48, 38, 28, 6, 2, 0]},
 "CTL_Ankle_R":  {"rx": [0, 12, 26, 48, 38, 28, 6, 2, 0]},
 "CTL_Toes_L":   {"rx": [0, 8, 15, 20, 12, 14, 0, 0, 0]},
 "CTL_Toes_R":   {"rx": [0, 8, 15, 20, 12, 14, 0, 0, 0]},
 "CTL_WingA_L":  {"rz": [0, -10, -22, 38, 20, 24, 6, 0, 0]},
 "CTL_WingA_R":  {"rz": [0, 10, 22, -38, -20, -24, -6, 0, 0]},
 "CTL_WingB_L":  {"rz": [0, -6, -10, 22, 10, 16, 4, 0, 0]},
 "CTL_WingB_R":  {"rz": [0, 6, 10, -22, -10, -16, -4, 0, 0]},
}
IDX = {"rx": 0, "ry": 1, "rz": 2, "tx": 3, "ty": 4, "tz": 5}
def cr(f, vals):
    i = max(j for j in range(len(KF) - 1) if KF[j] <= f)
    t = (f - KF[i]) / (KF[i + 1] - KF[i])
    p0 = vals[max(i - 1, 0)]; p1 = vals[i]; p2 = vals[i + 1]; p3 = vals[min(i + 2, len(vals) - 1)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
def side_w(f):   # idle f0 has a sideways wiggle; during the attack the strike must be straight ahead -> fade it out, back in at the end
    a = min(1.0, max(0.0, (f - 1) / 5.0)); b = min(1.0, max(0.0, (f - 21) / 9.0))
    return (1 - a * a * (3 - 2 * a)) + b * b * (3 - 2 * b) * a * a * (3 - 2 * a)
def pose(f):
    P = idle_pose(0); w = side_w(f)
    for c, v in P.items():
        if "Wing" in c: continue
        v[1] *= w; v[2] *= w; v[3] *= w
    for c, chs in D.items():
        for ch, vals in chs.items(): P[c][IDX[ch]] += cr(f, vals)
    return P
def build(api):
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):
        api.set_frame(f); P = pose(f)
        for c, v in P.items():
            api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
        api.select(list(P)); api.set_key()
    api.set_frame(1); api.set_frame(0)
    P = pose(0)
    for c, v in P.items():
        api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
    api.select(list(P)); api.set_key(); api.set_frame(1); api.set_frame(0)
