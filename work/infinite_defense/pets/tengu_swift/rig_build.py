# Tengu Swift: joint + FK control. Chay trong Frolvy 9886 sau rig_import.py (mesh Y len, mat +Z). Chi build MOT lan.
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(j)
    except Exception: pass
# name: (parent, (x,y,z), side, label)   x>0 = L (mat +Z, trai nhan vat = +X)
J = [
 ("DEF_Root_M", None, (0, 0.22, 0), "centre", "root"),
 ("DEF_Spine1_M", "DEF_Root_M", (0, 0.32, 0), "centre", "spine"),
 ("DEF_Head_M", "DEF_Spine1_M", (0, 0.43, 0), "centre", "head"),
 ("DEF_Hair1_M", "DEF_Head_M", (0, 0.68, -0.12), "centre", "hair1"),
 ("DEF_Hair2_M", "DEF_Hair1_M", (0, 0.74, -0.30), "centre", "hair2"),
]
for s, sx in (("L", 1), ("R", -1)):
    side = "left" if s == "L" else "right"
    J += [("DEF_Tuft1_%s" % s, "DEF_Head_M", (0.17*sx, 0.60, -0.10), side, "tuft1"),
          ("DEF_Tuft2_%s" % s, "DEF_Tuft1_%s" % s, (0.25*sx, 0.60, -0.22), side, "tuft2"),
          ("DEF_Arm_%s" % s, "DEF_Spine1_M", (0.16*sx, 0.335, -0.04), side, "arm"),
          ("DEF_Hand_%s" % s, "DEF_Arm_%s" % s, (0.30*sx, 0.335, -0.04), side, "hand"),
          ("DEF_Leg_%s" % s, "DEF_Root_M", (0.095*sx, 0.19, 0.0), side, "leg"),
          ("DEF_Foot_%s" % s, "DEF_Leg_%s" % s, (0.095*sx, 0.06, 0.0), side, "foot")]
J += [("DEF_Fan1_R", "DEF_Hand_R", (-0.319, 0.340, -0.037), "right", "fan1"),
      ("DEF_Fan2_R", "DEF_Fan1_R", (-0.322, 0.495, -0.037), "right", "fan2"),
      ("DEF_Muzzle_M", "DEF_Fan2_R", (-0.322, 0.607, -0.037), "centre", "muzzle")]
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
cm = {"Main": ctl("CTL_Main", (0, 0.0, 0.0), 0.5, "y", YEL)}
RAD = {"Root_M": (0.2, "y"), "Spine1_M": (0.2, "y"), "Head_M": (0.25, "y"), "Fan1_R": (0.08, "z"), "Fan2_R": (0.06, "z")}
for n, par, p, side, lab in J:
    if n == "DEF_Muzzle_M": continue
    short = n[4:]
    rad, ax = RAD.get(short, (0.05, "x"))
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
