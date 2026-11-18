"""Pinchy Balboa Idle, 48 frames loop (f0 == f48). Boxer bob + weight shift, hover. Run in Frolvy 9885 after rig + skin."""
import math
N = 48
LEGS = [("Leg%s_%s" % (g, s)) for g in "FMB" for s in "LR"]
CTLS = ["CTL_Root_M", "CTL_Head_M", "CTL_BandA1_M", "CTL_BandA2_M", "CTL_BandB1_M", "CTL_BandB2_M"]
for s in "LR": CTLS += ["CTL_Arm1_" + s, "CTL_Arm2_" + s, "CTL_Arm3_" + s, "CTL_Glove_" + s]
for g in "FMB":
    for s in "LR": CTLS += ["CTL_Leg%s_%s" % (g, s), "CTL_Leg%sTip_%s" % (g, s)]
HOVER = 0.12
GUARD = (25, 20, 10, 0, -25, 55, 10, 15)   # (Arm1 ry, Arm2 ry, Arm3 ry, Glove ry, Arm1 rz, Arm2 rz, Arm3 rz) boxer guard: Arm1 ry, Arm2 ry, Glove ry (forward, bent in), Arm1 rz, Arm2 rz (raise)
def pose(f):
    u = 2 * math.pi * f / 24; p = 2 * math.pi * f / N
    c = math.cos; s = math.sin
    P = {k: [0, 0, 0, 0, 0, 0] for k in CTLS}       # rx ry rz tx ty tz
    P["CTL_Root_M"] = [2 * c(u - 0.3), 2.5 * s(p + 0.5), -3 * s(p), 0.025 * s(p), HOVER + 0.035 * c(u), 0.012 * s(u + 1)]
    P["CTL_Head_M"][:3] = [2 * c(u - 1.2), 3 * s(p - 0.8), -2.5 * s(p - 1.2)]
    for n, (a, b, ph) in {"A1": (8, 10, 1.5), "A2": (14, 16, 2.4), "B1": (6, 9, 2.0), "B2": (12, 14, 2.9)}.items():
        P["CTL_Band%s_M" % n][:3] = [0, a * s(u - ph), b * s(p - ph)]
    for sd, k in (("R", 1), ("L", -1)):               # guard hands: R ry+ = forward, L ry- = forward; rz: R+ down / L+ up
        o = 0 if sd == "R" else math.pi
        P["CTL_Arm1_" + sd][1] = k * (GUARD[0] + 1.0 * s(u - 1.0) + 1.2 * s(p - 0.3 + o))
        P["CTL_Arm1_" + sd][2] = -k * (GUARD[4] + 1.0 * c(u - 0.8) + 0.6 * s(p + o))
        P["CTL_Arm2_" + sd][1] = k * (GUARD[1] + 1.4 * s(u - 1.6) + 1.2 * s(p - 0.7 + o))
        P["CTL_Arm2_" + sd][2] = -k * (GUARD[5] + 1.2 * c(u - 1.4))
        P["CTL_Arm3_" + sd][1] = k * (GUARD[2] + 1.8 * s(u - 2.2) + 1.2 * s(p - 1.1 + o))
        P["CTL_Arm3_" + sd][2] = -k * (GUARD[6] + 1.4 * c(u - 2.0))
        P["CTL_Glove_" + sd][1] = k * (GUARD[3] + 1.5 * s(u - 2.8) + 1.0 * s(p - 1.5 + o))
        P["CTL_Glove_" + sd][2] = -k * (GUARD[7] + 1.5 * c(u - 2.6))
    for i, g in enumerate("FMB"):                     # legs dangle, alternate sides (boxer foot change)
        for sd in "LR":
            o = 0 if sd == "L" else math.pi
            ph = 0.6 * i
            P["CTL_Leg%s_%s" % (g, sd)][0] = 8 * s(u - ph + o)
            P["CTL_Leg%s_%s" % (g, sd)][2] = (1 if sd == "L" else -1) * 4 * c(u - ph + o)
            P["CTL_Leg%sTip_%s" % (g, sd)][0] = 14 * s(u - ph - 0.9 + o)
    return P
def build(api, step=1):
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):                          # key zero everywhere first (a channel must exist before rotate works)
        api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, N + 1, step):
        api.set_frame(f); P = pose(f)
        for c, v in P.items(): api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
        api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
