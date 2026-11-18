"""Night Bat Idle 48f loop (f0==f48). Hover 12 cm, fast wing flap (6 per loop = 8 frames each), ears twist to scan, head looks around slowly."""
import math
N = 48
CTLS = ["CTL_Root_M", "CTL_Spine1_M", "CTL_Head_M", "CTL_Jaw_M"] + ["CTL_%s_%s" % (n, s) for n in ("Ear1", "Ear2", "Wing1", "Wing2", "Wing3", "Wing4") for s in "LR"]
HOVER = 0.12
def pose(f):
    p = 2 * math.pi * f / N; u = 6 * p                 # u: flap, 6 per loop
    c, s = math.cos, math.sin
    P = {k: [0, 0, 0, 0, 0, 0] for k in CTLS}          # rx ry rz tx ty tz
    P["CTL_Root_M"][4] = HOVER + 0.014 * s(p - 0.3) - 0.014 * s(u - 0.3)   # slow bob + lift on each downstroke
    P["CTL_Root_M"][5] = 0.008 * s(p + 0.8)
    P["CTL_Root_M"][:3] = [2 + 1.5 * s(u + 0.4) + 1.0 * s(p), 2.5 * s(p), 1.5 * s(2 * p + 0.5)]
    P["CTL_Spine1_M"][:3] = [-1.0 * s(u + 0.2), 1.5 * s(p - 0.4), 0]
    P["CTL_Head_M"][:3] = [-2 + 1.0 * s(u + 0.9) - 1.0 * s(p), 4 * s(p - 0.7), 1.5 * s(2 * p - 0.3)]
    P["CTL_Jaw_M"][0] = 2.0 + 1.5 * s(u - 0.6)
    for side, k, ph in (("L", 1, 0.0), ("R", -1, 0.3)):
        # downstroke is the strong beat, upstroke stays low (tips never reach the ears); 4 joints lag one after another = whip
        P["CTL_Wing1_" + side][2] = k * (-6 + 18 * s(u + ph) + 3 * s(2 * u + ph))
        P["CTL_Wing1_" + side][1] = k * (-2 + 8 * s(u + ph + 0.6))
        P["CTL_Wing2_" + side][2] = k * (7 * s(u + ph - 0.55))
        P["CTL_Wing3_" + side][2] = k * (8 * s(u + ph - 1.1))
        P["CTL_Wing4_" + side][2] = k * (-3 + 10 * s(u + ph - 1.7))
    # ears scan: asynchronous twist (2 and 3 cycles/loop) + flutter on the flap
    P["CTL_Ear1_L"][:3] = [4 * s(u - 1.1), 24 * s(2 * p), -3 * s(u - 1.3) - 4]
    P["CTL_Ear1_R"][:3] = [4 * s(u - 1.4), -24 * s(3 * p + 1.0), 3 * s(u - 1.6) + 4]
    P["CTL_Ear2_L"][:3] = [9 * s(u - 1.9), 10 * s(2 * p - 0.8), -4 * s(u - 2.0)]
    P["CTL_Ear2_R"][:3] = [9 * s(u - 2.2), -10 * s(3 * p + 0.2), 4 * s(u - 2.3)]
    return P

def apply(api, P):
    for c, v in P.items():
        api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])

def build(api, step=1):
    # curves must already hold a key at every frame before rotate sticks (empty/sparse curves ignore rotate): pre-key zeros, then write values
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):
        api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); P = pose(f); apply(api, P); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
