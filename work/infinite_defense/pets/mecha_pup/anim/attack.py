"""Mecha Pup Attack (floating pet: no ground contact), 24 frames, SHOT (muzzle fires) at frame 9. Built on the idle f0 pose so it blends back into idle."""
import math, importlib
N = 24; SHOT = 9
IK = ["CTL_IKWrist_R", "CTL_IKWrist_L", "CTL_IKAnkle_R", "CTL_IKAnkle_L"]
def base():
    P = idle_pose(0)
    return P
def add(P, c, vals):
    P[c] = [P[c][i] + vals[i] for i in range(6)]
# overrides per key frame: {ctl: (rx,ry,rz,tx,ty,tz)} added to the idle f0 pose; R/L symmetric entries use (r, l)
def sym(P, name, r):          # ears: L mirrored (negate ry, rz)
    add(P, name + "_R", r); add(P, name + "_L", [r[0], -r[1], -r[2], r[3], r[4], r[5]])
KEYS = {}
def key(f, root=(0,0,0,0,0,0), paw=(0,0,0), spine=0, chest=0, neck=0, head=0, ant=(0,0,0), tail=(0,0), ear1=0, ear2=0, bp=0, hind=(0,0)):
    P = base()
    add(P, "CTL_Root_M", list(root)); add(P, "CTL_Spine1_M", [spine,0,0,0,0,0]); add(P, "CTL_Chest_M", [chest,0,0,0,0,0])
    add(P, "CTL_Neck_M", [neck,0,0,0,0,0]); add(P, "CTL_Head_M", [head,0,0,0,0,0])
    add(P, "CTL_Ant1_M", [ant[0],0,0,0,0,0]); add(P, "CTL_Ant2_M", [ant[1],0,0,0,0,0]); add(P, "CTL_Dish_M", [ant[2],0,0,0,0,0])
    add(P, "CTL_Backpack_M", [bp,0,0,0,0,0])
    add(P, "CTL_Tail1_M", [tail[0],0,0,0,0,0]); add(P, "CTL_Tail2_M", [tail[1],0,0,0,0,0])
    sym(P, "CTL_Ear1", [0, ear1, 0, 0, 0, 0]); sym(P, "CTL_Ear2", [0, ear2, 0, 0, 0, 0])
    for c in IK[:2]: add(P, c, [0, 0, 0, 0, paw[0], paw[1]])
    for c in IK[2:]: add(P, c, [0, 0, 0, 0, hind[0], hind[1]])
    KEYS[f] = P
def setup():
    key(0)
    key(5,  root=(7,0,0,0,-0.05,-0.06), hind=(-0.01,-0.03), spine=4, chest=4, neck=9, head=16, ant=(-8,-14,-4), tail=(12,14), ear1=10, ear2=16, bp=-3)   # anticipation: crouch, head ducks down (snaps up on the lunge)
    key(7, root=(-14,0,0,0,0.03,0.04), hind=(0.0,-0.03), paw=(0.12,0.10), spine=-4, chest=-4, neck=4, head=8, ant=(-4,-6,0), tail=(-8,-10), ear1=-12, ear2=-18)
    key(9, root=(-22,0,0,0,0.06,0.12), hind=(0.09,-0.05), paw=(0.26,0.16), spine=-6, chest=-6, neck=10, head=16, ant=(22,34,10), tail=(-14,-20), ear1=-18, ear2=-26)   # SHOT
    key(11, root=(-24,0,0,0,0.065,0.08), hind=(0.09,-0.04), paw=(0.27,0.17), spine=-6, chest=-6, neck=10, head=16, ant=(-3,-6,-2), tail=(-10,-16), ear1=-14, ear2=-22)
    key(13, root=(-14,0,0,0,0.03,0.04), hind=(0.02,-0.03), paw=(0.2,0.12), spine=-4, chest=-4, neck=6, head=8, ant=(10,14,5), tail=(0,-6), ear1=4, ear2=10)
    key(15, root=(6,0,0,0,-0.035,0.0), hind=(0.03,0.03), paw=(-0.03,0.04), spine=3, head=-4, ant=(-6,-9,-3), tail=(8,12), ear1=14, ear2=24)                        # settle dip (no landing: it hovers)
    key(19, root=(-1,0,0,0,0.0,0), ant=(6,8,3), tail=(-3,-4), ear1=-3, ear2=-5)
    key(24)
def build(api):
    api.set_frame_range(0, N)
    api.set_attr("CTL_SpineSwitch_M.fkIk", 0.0)
    api.set_frame(1); api.set_frame(0)
    for f in sorted(KEYS):
        api.set_frame(f if f else 0)
        for c, v in KEYS[f].items():
            api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
        api.select(list(KEYS[f])); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c, v in KEYS[0].items():
        api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
    api.select(list(KEYS[0])); api.set_key()
    api.set_frame(1); api.set_frame(0)
