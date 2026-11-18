"""Tengu Swift Idle 48f loop (f0==f48). Lo lung 12 cm, bong benh 1 nhip/vong; tay phai cam quat, toc/tuft/chan tre theo than."""
import math
N = 48
NAMES = ["Root_M", "Spine1_M", "Head_M", "Hair1_M", "Hair2_M", "Fan1_R", "Fan2_R"] + ["%s_%s" % (n, s) for n in ("Tuft1", "Tuft2", "Arm", "Hand", "Leg", "Foot") for s in "LR"]
CTLS = ["CTL_" + n for n in NAMES]
HOVER = 0.12
FAN_OFF = (0, 0, 0)       # quat nam trong tay phai (Base: quat nam canh nguoi)
def pose(f):
    p = 2 * math.pi * f / N
    s, c = math.sin, math.cos
    P = {k: [0, 0, 0, 0, 0, 0] for k in CTLS}          # rx ry rz tx ty tz
    P["CTL_Root_M"][4] = HOVER + 0.020 * s(p)
    P["CTL_Root_M"][5] = 0.012 * s(p + 1.0)
    P["CTL_Root_M"][:3] = [3 * s(p - 0.5), 4 * s(p), 4 * s(p + 1.2)]
    P["CTL_Spine1_M"][:3] = [-2 * s(p - 1.0), 2.5 * s(p - 0.6), -2 * s(p + 0.2)]
    P["CTL_Head_M"][:3] = [-1 + 3 * s(p - 1.4), 7 * s(p - 0.9), 2 * s(p - 1.0)]
    P["CTL_Hair1_M"][0] = -9 * s(p - 1.1) - 2
    P["CTL_Hair2_M"][0] = -12 * s(p - 1.9) - 3
    for side, k, ph in (("L", 1, 0.0), ("R", -1, 0.5)):
        P["CTL_Tuft1_" + side][1] = k * (7 + 7 * s(p - 1.2 - ph)) * -1
        P["CTL_Tuft2_" + side][1] = k * (6 * s(p - 2.0 - ph)) * -1
        P["CTL_Leg_" + side][0] = -9 - 7 * s(p - 1.3 - ph)
        P["CTL_Foot_" + side][0] = 12 + 9 * s(p - 2.2 - ph)
        P["CTL_Leg_" + side][2] = k * 3 * s(p - 0.8)
    # tay trai buong thong, vay nhe; tay phai nang quat truoc ngua
    P["CTL_Arm_L"][:3] = [0, -6 + 5 * s(p - 1.0), -38 + 7 * s(p - 0.4)]
    P["CTL_Hand_L"][:3] = [0, 0, -14 + 12 * s(p - 1.5)]
    P["CTL_Arm_R"][:3] = [0, 24 + 4 * s(p - 0.8), 18 + 4 * s(p - 0.3)]
    P["CTL_Hand_R"][:3] = [0, 0, 6 + 6 * s(p - 1.3)]
    # quat: lech tay quay Y (cam)  + tre theo than
    P["CTL_Fan1_R"][:3] = [4 * s(p - 1.6), 0, 8 * s(p - 1.6)]
    P["CTL_Fan2_R"][:3] = [0, 0, 6 * s(p - 2.3)]
    P["CTL_Fan1_R"][3:] = list(FAN_OFF)
    return P

def apply(api, P):
    for c, v in P.items():
        api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])

def build(api, step=1, posefn=None, n=None):
    posefn = posefn or pose; n = n or N
    api.set_frame_range(0, n); api.set_frame(1)
    for f in range(0, n + 1):
        api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, n + 1):
        api.set_frame(f); apply(api, posefn(f)); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try: api.set_infinity(c + "." + a, "cycle" if n == N and posefn is pose else "constant", "cycle" if n == N and posefn is pose else "constant")
            except Exception: pass

def hold_fix(api, n):
    """Pivot cua control khong nam dung tren joint (ca rig): xoay CTL_Fan1_R lam joint quat troi khoi tay. Moi frame: do joint Fan1 lech bao nhieu so voi vi tri co dinh trong he truc ban tay (do o f0 idle), cong phan lech vao tx ty tz cua CTL_Fan1_R roi key."""
    def hm(): m = api.world_matrix("DEF_Hand_R"); return m
    api.set_frame(1); api.set_frame(0)
    m = hm(); fp = api.world_matrix("DEF_Fan1_R")[12:15]
    d0 = [fp[i] - m[12 + i] for i in range(3)]
    lr = [sum(d0[k] * m[r * 4 + k] for k in range(3)) for r in range(3)]
    for f in range(0, n + 1):
        api.set_frame(f); m = hm(); fp = api.world_matrix("DEF_Fan1_R")[12:15]
        exp = [m[12 + i] + sum(lr[r] * m[r * 4 + i] for r in range(3)) for i in range(3)]
        err = [exp[i] - fp[i] for i in range(3)]
        loc = [sum(err[k] * m[r * 4 + k] for k in range(3)) for r in range(3)]
        cur = [api.get_attr("CTL_Fan1_R.t" + a) for a in "xyz"]
        api.move("CTL_Fan1_R", cur[0] + loc[0], cur[1] + loc[1], cur[2] + loc[2]); api.select(["CTL_Fan1_R"]); api.set_key()
    api.set_frame(1); api.set_frame(0)
