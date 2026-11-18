"""Mecha Pup Idle, 48 frames loop (f0 == f48). Run in Frolvy 9879 after the rig is built."""
import math
N = 48
CTLS = ["CTL_Root_M", "CTL_Spine1_M", "CTL_Chest_M", "CTL_Neck_M", "CTL_Head_M", "CTL_Ear1_R", "CTL_Ear1_L", "CTL_Ear2_R", "CTL_Ear2_L",
        "CTL_Tail1_M", "CTL_Tail2_M", "CTL_Backpack_M", "CTL_Ant1_M", "CTL_Ant2_M", "CTL_Dish_M",
        "CTL_IKAnkle_R", "CTL_IKAnkle_L", "CTL_IKWrist_R", "CTL_IKWrist_L"]
HOVER = 0.12      # pets float: body hover height above the ground, no foot contact
def pose(f):
    u = 2 * math.pi * f / 24; p = 2 * math.pi * f / N; w = 2 * math.pi * f / 16
    c = math.cos; s = math.sin
    P = {c_: [0, 0, 0, 0, 0, 0] for c_ in CTLS}      # rx ry rz tx ty tz
    P["CTL_Root_M"][4] = HOVER + 0.03 * c(u)      # floating bob (period 24)
    P["CTL_Root_M"][5] = 0.012 * s(p)
    for side in ("R", "L"):                          # dangling paws: follow the body with a lag (overlap), small paddling
        P["CTL_IKAnkle_" + side][4] = HOVER - 0.02 + 0.03 * c(u - 0.9); P["CTL_IKAnkle_" + side][5] = -0.02 * s(u - 0.9)
        P["CTL_IKWrist_" + side][4] = HOVER + 0.05 + 0.025 * c(u - 0.7); P["CTL_IKWrist_" + side][5] = 0.02 * s(u - 0.7)   # paws kept inside arm reach (full stretch = pop/jitter)
    P["CTL_Spine1_M"][0] = 2.5 * c(u - 0.4)
    P["CTL_Chest_M"][0] = 2.5 * c(u - 0.9)
    P["CTL_Neck_M"][0] = 3 * c(u - 1.3)
    P["CTL_Head_M"][:3] = [5 * c(u - 1.8), 7 * s(p), 3 * s(p + 1)]
    for side, k in (("R", 1), ("L", -1)):
        P["CTL_Ear1_" + side][:3] = [0, k * 8 * c(u - 1.6), k * 6 * s(p)]
        P["CTL_Ear2_" + side][:3] = [0, k * 14 * c(u - 2.4), k * 8 * s(p - 0.6)]
    P["CTL_Tail1_M"][:3] = [6 * c(u - 1.2), 20 * s(p - 0.6), 0]
    P["CTL_Tail2_M"][:3] = [8 * c(u - 1.8), 28 * s(p - 1.3), 0]
    P["CTL_Backpack_M"][0] = 2 * c(u - 1.5)
    P["CTL_Ant1_M"][:3] = [5 * c(u - 2.0), 0, 9 * s(w - 0.8)]
    P["CTL_Ant2_M"][:3] = [8 * c(u - 2.8), 0, 14 * s(w - 1.6)]
    P["CTL_Dish_M"][2] = 6 * s(w - 2.4)
    return P

def build(api, step=2):
    api.set_frame_range(0, N)
    api.set_frame(1)    # Frolvy: set_frame(0) while already on 0 does not re-evaluate -> first key was stale
    api.set_attr("CTL_SpineSwitch_M.fkIk", 0.0)
    for f in list(range(0, N + 1, step)):
        api.set_frame(f)
        P = pose(f)
        for c, v in P.items():
            api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
        api.select(list(P)); api.set_key()
    # Frolvy: the first key at frame 0 comes out as the zero pose -> key frame 0 again now that curves exist
    api.set_frame(1); api.set_frame(0)
    P = pose(0)
    for c, v in P.items():
        api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
    api.select(list(P)); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
