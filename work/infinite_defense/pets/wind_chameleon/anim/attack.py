"""Wind Chameleon Attack 30f: lean back + cheeks puff to max (f4-11), FIRE = frame 13 (tongue shot out fully, cheeks collapse, jaw open),
reel the tongue back f15-22, settle, f30 == Idle f0. Needs idle_pose (idle.pose) in globals. Deltas on Idle f0, Catmull-Rom, keyed every frame."""
import math
N = 30
CH = ("rx", "ry", "rz", "tx", "ty", "tz", "sx", "sy", "sz")
FIRE = 13
KF = [0, 4, 8, 11, 12, 13, 15, 18, 22, 26, 30]
def tail(i):                       # whip travels along the tail
    k = 0.6 + 0.07 * i
    return {"rx": [v * k for v in [0, 3, 6, 6, 2, -5, -3, 2, -1, 0, 0]], "rz": [v * k for v in [0, 0, 1, 1, 0, 3, 2, -1, 0.5, 0, 0]]}
D = {
 "CTL_Root_M":   {"rx": [0, -4, -9, -10, -2, 7, 4, 1, -1, 0, 0], "ty": [0, -.02, -.03, -.03, 0, .02, .01, 0, 0, 0, 0], "tz": [0, -.02, -.05, -.06, .03, .08, .05, .02, .005, 0, 0]},
 "CTL_Spine1_M": {"rx": [0, -2, -4, -4, 0, 3, 2, 0, 0, 0, 0]},
 "CTL_Chest_M":  {"rx": [0, -2, -3, -3, 0, 3, 1, 0, 0, 0, 0]},
 "CTL_Neck_M":   {"rx": [0, -3, -6, -6, 0, 4, 2, 0, 0, 0, 0]},
 "CTL_Head_M":   {"rx": [0, -3, -6, -6, 0, 5, 2, -1, 0, 0, 0]},
 "CTL_Crest_M":  {"rx": [0, 6, 14, 14, 4, -12, -6, 3, 0, 0, 0]},
 "CTL_Jaw_M":    {"rx": [0, 0, 4, 8, 22, 30, 26, 18, 8, 0, 0]},   # jaw: small anticipation, wide at the shot (f13), shut by f26
 "CTL_Mouth_M":  {"sy": [0, 0, .38, .55, 1.0, 1.4, 1.3, .9, .35, 0, 0]},   # hole widens (delta on the closed scale 0.12)   # mouth opens: small anticipation on the wind-up, wide at the shot (f13), closes by f26
 "CTL_Tongue2_M": {"rx": [0, 0, 0, 0, 0, -5, 5, -3, 1, 0, 0]},
 "CTL_Tongue3_M": {"rx": [0, 0, 0, 0, 0, -8, 8, -5, 2, 0, 0]},
 "CTL_Tongue4_M": {"rx": [0, 0, 0, 0, 0, -10, 10, -6, 2, 0, 0]},
 "CTL_Tongue1_M": {"tz": [0, 0, 0, 0, .20, .31, .27, .15, .02, 0, 0], "sz": [0, 0, 0, 0, .10, .22, .18, .08, 0, 0, 0]},   # sz is a delta on scale
 "CTL_Cheek_L":  {"sx": [0, .25, .75, .95, -.15, -.15, -.05, 0, 0, 0, 0]},
 "CTL_Cheek_R":  {"sx": [0, .25, .75, .95, -.15, -.15, -.05, 0, 0, 0, 0]},
 "CTL_Eye_L":    {"ry": [0, -6, -10, -10, -10, -8, -4, 0, 0, 0, 0]},
 "CTL_Eye_R":    {"ry": [0, 6, 10, 10, 10, 8, 4, 0, 0, 0, 0]},
}
for i in range(1, 11): D["CTL_Tail%d_M" % i] = tail(i)
# The idle holds the head turned a little (yaw/roll on spine..head). When the jaw opens that reads as a crooked mouth: straighten the head axis for the shot (f8-f15), back to idle at the ends.
IDX0 = {"rx": 0, "ry": 1, "rz": 2}
_YK = [0, .3, .8, 1, 1, 1, 1, .6, .2, 0, 0]
_I0 = idle_pose(0)
for _c in ("CTL_Root_M", "CTL_Spine1_M", "CTL_Chest_M", "CTL_Neck_M", "CTL_Head_M"):
    for _a in ("ry", "rz"):
        _b = _I0[_c][IDX0[_a]]
        if abs(_b) > 1e-6: D.setdefault(_c, {})[_a] = [-_b * k for k in _YK]
for s in "LR":
    k = 1 if s == "L" else -1
    # front legs: swing (rx) + splay (rz), each joint lags the one above it (hip 0f, ankle 2f, toes 4f) and overshoots, so the leg flows instead of moving as one block
    D["CTL_FHip_" + s] = {"ry": [-k * v for v in [0, -5, -11, -12, 3, 16, 10, 1, -1, 0, 0]]}
    D["CTL_FAnkle_" + s] = {"ry": [-k * v for v in [0, -8, -17, -19, 9, 24, 14, -3, 2, 0, 0]]}
    D["CTL_FToes_" + s] = {"ry": [-k * v for v in [0, -8, -14, -16, 10, 22, 6, -5, 3, 0, 0]]}
    # rear legs: tuck under the body on the wind-up, get dragged back and splayed by the lunge, then swing forward again; they trail the front legs by ~2 frames
    D["CTL_RHip_" + s] = {"ry": [-k * v for v in [0, -4, -9, -10, 2, 14, 12, 4, -2, 0, 0]]}
    D["CTL_RAnkle_" + s] = {"ry": [-k * v for v in [0, -6, -14, -15, 6, 22, 17, 2, -3, 0, 0]]}
    D["CTL_RToes_" + s] = {"ry": [-k * v for v in [0, -6, -12, -13, 8, 20, 10, -4, 3, 0, 0]]}
LAG = {"FHip": 0, "FAnkle": 2, "FToes": 4, "RHip": 2, "RAnkle": 4, "RToes": 6}   # frames each front-leg joint trails behind its parent
def _lag(c):
    for k, v in LAG.items():
        if c.startswith("CTL_" + k + "_"): return v
    return 0
IDX = {"rx": 0, "ry": 1, "rz": 2, "tx": 3, "ty": 4, "tz": 5, "sx": 6, "sy": 7, "sz": 8}
def cr(f, vals):
    i = max(j for j in range(len(KF) - 1) if KF[j] <= f)
    t = (f - KF[i]) / (KF[i + 1] - KF[i])
    p0 = vals[max(i - 1, 0)]; p1 = vals[i]; p2 = vals[i + 1]; p3 = vals[min(i + 2, len(vals) - 1)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
def pose(f):
    P = idle_pose(0)
    for c, chs in D.items():
        for ch, vals in chs.items():
            d = cr(max(0, f - _lag(c)), vals)
            if ch in ("sx", "sy", "sz"):
                P[c][IDX[ch]] += d
                if c.startswith("CTL_Cheek") and ch == "sx": P[c][7] += d; P[c][8] += d
            else: P[c][IDX[ch]] += d
    if f > 26:                                   # lagged curves are not exactly zero at the end: fade the front-leg deltas to Idle f0
        base = idle_pose(0); k = (N - f) / float(N - 26)
        for c in P:
            if _lag(c):
                P[c] = [b + (x - b) * k for x, b in zip(P[c], base[c])]
    w = max(0.0, min(1.0, (28 - f) / 6.0))      # fade out f22 -> f28
    for s, ph in (("L", 0.0), ("R", 0.9)):
        if f >= 14:
            kk = 1 if s == "L" else -1
            e = math.exp(-(f - 14) / 6.0) * w
            P["CTL_FAnkle_" + s][1] += -kk * 7 * e * math.sin(0.85 * (f - 14) + ph)
            P["CTL_FToes_" + s][1] += -kk * 9 * e * math.sin(0.85 * (f - 14) + ph - 0.9)
            er = math.exp(-(f - 16) / 6.0) * w if f >= 16 else 0.0       # rear paws flick a little later and softer, opposite phase to the front
            P["CTL_RAnkle_" + s][1] += -kk * 5 * er * math.sin(0.85 * (f - 16) + ph + 2.4)
            P["CTL_RToes_" + s][1] += -kk * 7 * er * math.sin(0.85 * (f - 16) + ph + 1.5)
    return P
def apply(api, P):
    for c, v in P.items():
        for a, x in zip(CH, v): api.set_attr(c + "." + a, float(x))   # set_attr (api.move/rotate are overridden by the curve on keyed channels)

def build(api):
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):
        api.set_frame(f); api.select(list(idle_pose(0))); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); P = pose(f); apply(api, P); api.select(list(P)); api.set_key()
    api.set_frame(1); api.set_frame(0)
