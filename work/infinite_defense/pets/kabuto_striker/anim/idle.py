"""Kabuto Striker Idle 48f loop (f0==f48). Thu the vo si: hover 12 cm bobbing, nhun nhe, sung rung nhe thi uy (4 chu ky/loop), giap vai / vat ao / chan tha tre pha."""
import math
N = 48
CTLS = ["CTL_Root_M", "CTL_Spine1_M", "CTL_Chest_M", "CTL_Neck_M", "CTL_Head_M", "CTL_SkirtF_M", "CTL_SkirtB_M"] + \
       ["CTL_%s_%s" % (a, s) for s in "LR" for a in ("Horn1", "Horn2", "Sode", "SkirtS", "FFoot", "RFoot")]
HOVER = 0.12
CH = ("rx", "ry", "rz", "tx", "ty", "tz", "sx", "sy", "sz")
def pose(f):
    p = 2 * math.pi * f / N; c, s = math.cos, math.sin
    P = {k: [0, 0, 0, 0, 0, 0, 1, 1, 1] for k in CTLS}
    P["CTL_Root_M"][4] = HOVER + 0.022 * c(p - 0.3)
    P["CTL_Root_M"][5] = 0.010 * s(p)
    P["CTL_Root_M"][:3] = [1.5 * c(p - 0.5), 1.2 * s(p), 1.8 * s(p + 0.8)]
    P["CTL_Spine1_M"][:3] = [-0.8 * c(p - 0.9), 0.8 * s(p - 0.4), 0.8 * s(p - 0.2)]
    P["CTL_Chest_M"][:3] = [1.0 * c(2 * p - 1.2), 0.8 * s(p - 0.8), 0.6 * s(p - 0.6)]
    P["CTL_Neck_M"][:3] = [-1.0 * c(p - 1.2), 1.5 * s(p - 1.2), 0]
    P["CTL_Head_M"][:3] = [-1.0 * c(p - 1.6) + 0.8 * c(2 * p), 2.5 * s(p - 1.6), 0.8 * s(p - 1.0)]
    for sd, k in (("L", 1), ("R", -1)):
        q = 0.0 if sd == "L" else 0.6
        sh = 1.6 * s(4 * p + q) * (0.6 + 0.4 * c(p - 0.4))          # sung rung nhe thi uy (4 nhip / loop)
        P["CTL_Horn1_" + sd][:3] = [0.6 * s(4 * p + q - 0.5), 0, k * sh]
        P["CTL_Horn2_" + sd][:3] = [1.0 * s(4 * p + q - 1.0), 0, k * 1.6 * s(4 * p + q - 0.9)]
        P["CTL_Sode_" + sd][:3] = [1.0 * s(p - 2.0 - q), 0, k * (1.5 + 2.0 * s(p - 1.6 - q))]
        P["CTL_SkirtS_" + sd][:3] = [0, 0, k * (1.5 + 2.5 * s(p - 2.0 - q))]
        P["CTL_FFoot_" + sd][:3] = [5 + 4 * s(p - 1.6 - q), 0, k * (2 + 2 * s(p - 1.2 - q))]
        P["CTL_RFoot_" + sd][:3] = [5 + 4 * s(p - 2.2 - q), 0, k * (2 + 2 * s(p - 1.8 - q))]
    P["CTL_SkirtF_M"][0] = 1.5 + 2 * s(p - 1.8)
    P["CTL_SkirtB_M"][0] = -1.5 - 2 * s(p - 2.2)
    return P
def apply(api, P):
    for c, v in P.items():
        for a, x in zip(CH, v): api.set_attr(c + "." + a, float(x))
def build(api, step=2):
    # Frolvy 0.9.59: set_key o frame MOI luu gia tri noi suy -> luot 1 tao key, luot 2 dat gia tri
    api.set_frame_range(0, N); frames = list(range(0, N + 1, step)); api.set_frame(1)
    for f in frames: api.set_frame(f); api.select(CTLS); api.set_key()
    for f in frames: api.set_frame(f); P = pose(f); apply(api, P); api.select(list(P)); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in CH:
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
