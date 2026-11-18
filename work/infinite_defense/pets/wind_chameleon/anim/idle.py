"""Wind Chameleon Idle 48f loop (f0==f48). Float hover 12 cm, tail ripple, eyes roam independently, legs dangle.
Pets float: no ground contact. Tongue stays pulled back inside the mouth (CTL_Tongue1_M tz)."""
import math
N = 48
TAILS = ["CTL_Tail%d_M" % i for i in range(1, 11)]
CTLS = ["CTL_Root_M", "CTL_Spine1_M", "CTL_Chest_M", "CTL_Neck_M", "CTL_Head_M", "CTL_Crest_M", "CTL_Jaw_M", "CTL_Mouth_M",
        "CTL_Tongue1_M", "CTL_Tongue2_M", "CTL_Tongue3_M", "CTL_Tongue4_M", "CTL_Cheek_L", "CTL_Cheek_R", "CTL_Eye_L", "CTL_Eye_R"] + TAILS + \
       ["CTL_%s%s_%s" % (a, b, s) for s in "LR" for a in "FR" for b in ("Hip", "Ankle", "Toes")]
HOVER = 0.12
TONGUE_IN = -0.26
JAW_SHUT = 0.0
MOUTH_SHUT = 0.12   # CTL_Mouth_M scale y when the mouth is closed (1 = bind pose = hole open)
CH = ("rx", "ry", "rz", "tx", "ty", "tz", "sx", "sy", "sz")
def pose(f):
    p = 2 * math.pi * f / N
    c, s = math.cos, math.sin
    P = {k: [0, 0, 0, 0, 0, 0, 1, 1, 1] for k in CTLS}
    P["CTL_Root_M"][4] = HOVER + 0.025 * c(p - 0.3)
    P["CTL_Root_M"][5] = 0.012 * s(p)
    P["CTL_Root_M"][:3] = [2.0 * c(p - 0.6), 2.5 * s(p), 1.5 * s(p + 0.8)]
    P["CTL_Spine1_M"][:3] = [1.0 * c(p - 1.0), 1.5 * s(p - 0.4), 1.0 * s(p - 0.2)]
    P["CTL_Chest_M"][:3] = [1.2 * c(2 * p - 1.2), 1.5 * s(p - 0.8), 0.8 * s(p - 0.6)]        # breathing 2/loop
    P["CTL_Neck_M"][:3] = [-1.5 * c(p - 1.2), 3.0 * s(p - 1.2), 0]
    P["CTL_Head_M"][:3] = [-1.0 * c(p - 1.6) + 1.0 * c(2 * p), 5.0 * s(p - 1.6), 1.5 * s(p - 1.0)]   # slow look around, nose level
    P["CTL_Crest_M"][:3] = [2.5 * s(p - 2.3), 0, 1.5 * s(p - 2.0)]
    P["CTL_Jaw_M"][0] = JAW_SHUT                                                               # mouth shut (the bind pose has the mouth open)
    P["CTL_Mouth_M"][7] = MOUTH_SHUT
    P["CTL_Tongue1_M"][5] = TONGUE_IN
    for side, ph in (("L", 0.0), ("R", 1.9)):
        P["CTL_Eye_" + side][:3] = [4 * s(2 * p + ph), 14 * s(p + ph * 1.3 + 0.7), 0]         # eyes roam independently
        sc = 1 + 0.03 * s(2 * p - 0.4); P["CTL_Cheek_" + side][6:9] = [sc, sc, sc]
    for i, t in enumerate(TAILS):                                                             # ripple travels up the tail
        a = 2.2 + 0.25 * i
        P[t][0] = a * s(p - 0.5 * i - 0.6) + 0.8 * s(2 * p - 0.9 * i)
        P[t][2] = 1.3 * s(p - 0.45 * i - 1.4)
    for sd, k in (("L", 1), ("R", -1)):
        for a, ph in (("F", 0.0), ("R", 1.2)):
            q = ph + (0.7 if sd == "R" else 0)
            P["CTL_%sHip_%s" % (a, sd)][:3] = [5 + 4 * s(p - 1.4 - q), 0, k * (3 + 2 * s(p - 1.0 - q))]
            P["CTL_%sAnkle_%s" % (a, sd)][:3] = [8 + 6 * s(p - 2.0 - q) + 2 * c(2 * p), 0, k * 2 * s(p - 1.8 - q)]
            P["CTL_%sToes_%s" % (a, sd)][0] = 7 * s(p - 2.7 - q)
    return P

def apply(api, P):
    for c, v in P.items():
        for a, x in zip(CH, v): api.set_attr(c + "." + a, float(x))   # set_attr (api.move/rotate are overridden by the curve on keyed channels)

def build(api, step=2):
    # Frolvy 0.9.59: set_key at a NEW frame stores the curve-evaluated value, not the edited one -> pass 1 creates every key, pass 2 sets the values
    api.set_frame_range(0, N); frames = list(range(0, N + 1, step)); api.set_frame(1)
    for f in frames:
        api.set_frame(f); api.select(CTLS); api.set_key()
    for f in frames:
        api.set_frame(f); P = pose(f); apply(api, P); api.select(list(P)); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in CH:
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
