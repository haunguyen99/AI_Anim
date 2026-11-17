# Chrono Ouroboros: chay trong Frolvy cong 9883 sau khi import FBX + xoay -90 X + freeze (Y len, mat +Z). Joint + control FK.
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(j)
    except Exception: pass
# name: (parent, (x,y,z), side, label)   x>0 = L ; mesh Y up, head +Z
J = [
 ("DEF_Root_M", None, (0, 0.36, -0.55), "centre", "root"),
 ("DEF_Spine1_M", "DEF_Root_M", (0, 0.36, -0.05), "centre", "spine"),
 ("DEF_Spine2_M", "DEF_Spine1_M", (0, 0.37, 0.48), "centre", "spine2"),
 ("DEF_Neck1_M", "DEF_Spine2_M", (0, 0.36, 0.80), "centre", "neck"),
 ("DEF_Neck2_M", "DEF_Neck1_M", (0, 0.54, 0.87), "centre", "neck2"),
 ("DEF_Head_M", "DEF_Neck2_M", (0, 0.75, 1.01), "centre", "head"),
 ("DEF_Jaw_M", "DEF_Head_M", (0, 0.70, 1.19), "centre", "jaw"),
 ("DEF_Muzzle_M", "DEF_Jaw_M", (0, 0.64, 1.39), "centre", "muzzle"),
 ("DEF_Tail1_M", "DEF_Root_M", (0, 0.36, -0.95), "centre", "tail1"),
 ("DEF_Tail2_M", "DEF_Tail1_M", (0, 0.40, -1.15), "centre", "tail2"),
 ("DEF_Tail3_M", "DEF_Tail2_M", (0, 0.46, -1.32), "centre", "tail3"),
 ("DEF_Tail4_M", "DEF_Tail3_M", (0, 0.54, -1.48), "centre", "tail4"),
 ("DEF_Tail5_M", "DEF_Tail4_M", (0, 0.60, -1.64), "centre", "tail5"),
]
for s, sx in (("L", 1), ("R", -1)):
    side = "left" if s == "L" else "right"
    J += [("DEF_ForeLeg1_%s" % s, "DEF_Spine2_M", (0.12*sx, 0.30, 0.76), side, "arm1"),
          ("DEF_ForeLeg2_%s" % s, "DEF_ForeLeg1_%s" % s, (0.12*sx, 0.17, 0.79), side, "arm2"),
          ("DEF_ForeFoot_%s" % s, "DEF_ForeLeg2_%s" % s, (0.13*sx, 0.04, 0.77), side, "hand"),
          ("DEF_HindLeg1_%s" % s, "DEF_Root_M", (0.17*sx, 0.30, -0.72), side, "leg1"),
          ("DEF_HindLeg2_%s" % s, "DEF_HindLeg1_%s" % s, (0.17*sx, 0.14, -0.75), side, "leg2"),
          ("DEF_HindFoot_%s" % s, "DEF_HindLeg2_%s" % s, (0.17*sx, 0.04, -0.75), side, "foot")]
made = {}
for n, par, p, side, lab in J:
    api.select([]); j = api.create_joint(); api.select([]); api.move(j, *p); made[n] = j
for n, par, p, side, lab in J:
    if par: api.parent(made[n], made[par])
for n, par, p, side, lab in J:
    api.rename(made[n], n)
    try: api.set_joint_label(n, side, lab)
    except Exception as e: print("label", n, e)
api.select([])
print(len(api.ls("Joint")), "joints")
def ctl(name, pos, radius, axis, color):
    c = api.create_circle(radius, axis); api.move(c, *pos)
    g = api.create_group(); api.move(g, *pos); api.parent(c, g)
    api.rename(c, name); api.rename(g, name + "_grp"); api.set_curve_color(name, *color); return name
YEL, RED, BLU = (1, .9, .1), (.9, .2, .2), (.2, .4, 1)
cm = {"Main": ctl("CTL_Main", (0, 0.0, 0.0), 0.8, "y", YEL)}
RAD = {"Root_M": (0.25, "z"), "Spine1_M": (0.22, "z"), "Spine2_M": (0.22, "z"), "Neck1_M": (0.2, "z"), "Neck2_M": (0.17, "z"), "Head_M": (0.2, "z"), "Jaw_M": (0.08, "x")}
for _t in range(1, 6): RAD["Tail%d_M" % _t] = (0.17 - 0.02 * _t, "z")
for n, par, p, side, lab in J:
    if n == "DEF_Muzzle_M": continue
    short = n[4:]
    rad, ax = RAD.get(short, (0.07, "y"))
    col = YEL if side == "centre" else (BLU if short.endswith("_L") else RED)
    cm[short] = ctl("CTL_" + short, p, rad, ax, col)
api.parent("CTL_Root_M_grp", "CTL_Main")
for n, par, p, side, lab in J:
    if n == "DEF_Muzzle_M" or par is None: continue
    api.parent("CTL_%s_grp" % n[4:], "CTL_%s" % par[4:])
for n, par, p, side, lab in J:
    if n == "DEF_Muzzle_M": continue
    api.select(["CTL_" + n[4:], n]); api.constrain("parent", True)
api.select([])
for n in cm.values(): api.lock_channels(n, "sx sy sz", False)
print("controls", len(api.ls("Curve"))); print(api.check_rig())
