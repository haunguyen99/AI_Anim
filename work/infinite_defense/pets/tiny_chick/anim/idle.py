"""Tiny Chick Idle 48f loop (f0==f48). Float hover, butt wiggle (2 swings/loop), egg shells clatter. Pets float: no ground contact."""
import math
N = 48
CTLS = ["CTL_Root_M", "CTL_Spine1_M", "CTL_Head_M", "CTL_Cap_M", "CTL_Beak_M", "CTL_Shell_M",
        "CTL_WingA_L", "CTL_WingA_R", "CTL_WingB_L", "CTL_WingB_R", "CTL_Ankle_L", "CTL_Ankle_R", "CTL_Toes_L", "CTL_Toes_R"]
HOVER = 0.12
def pose(f):
    p = 2 * math.pi * f / N; u = 2 * p            # u: wiggle, 2 swings per loop
    c, s = math.cos, math.sin
    P = {k: [0, 0, 0, 0, 0, 0] for k in CTLS}     # rx ry rz tx ty tz
    P["CTL_Root_M"][4] = HOVER + 0.022 * c(p - 0.3)           # slow bob, 1 per loop
    P["CTL_Root_M"][3] = 0.012 * s(u)                          # butt pushes sideways
    P["CTL_Root_M"][:3] = [1.5 * c(p), 8 * s(u), 4 * s(u + 1.2)]   # yaw wiggle + small roll
    P["CTL_Spine1_M"][:3] = [1.0 * c(p - 0.5), -5 * s(u - 0.6), -2.5 * s(u - 0.2)]
    P["CTL_Head_M"][:3] = [2 * c(p - 0.9), -3.5 * s(u - 1.1), -2 * s(u - 0.8)]   # head stays looking forward
    P["CTL_Beak_M"][0] = 2.5 * s(u - 1.4)
    # bottom shell lags the butt and swings wider -> bumps against the body; top cap taps at twice the wiggle rate
    P["CTL_Shell_M"][:3] = [0, 4 * s(u - 0.9), 5 * s(u - 1.6)]
    P["CTL_Cap_M"][:3] = [3 * s(2 * u - 0.5) + 2 * c(p), 3 * s(u - 2.2), 4 * s(u - 2.0)]
    for side, k in (("L", 1), ("R", -1)):
        P["CTL_WingA_" + side][2] = k * (5 + 6 * s(u - 1.3 + (0.5 if side == "R" else 0)))
        P["CTL_WingB_" + side][2] = k * 6 * s(u - 2.1)
        P["CTL_Ankle_" + side][0] = 8 + 9 * s(u - 1.5 + (0.6 if side == "R" else 0)) + 3 * c(p)   # dangling feet, lag behind body
        P["CTL_Ankle_" + side][2] = k * 3 * s(u - 1.0)
        P["CTL_Toes_" + side][0] = 7 * s(u - 2.4)
    return P

def apply(api, P):
    for c, v in P.items():
        api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])

def build(api, step=2):
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1, step):
        api.set_frame(f); P = pose(f); apply(api, P); api.select(list(P)); api.set_key()
    api.set_frame(1); api.set_frame(0); apply(api, pose(0)); api.select(list(pose(0))); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
