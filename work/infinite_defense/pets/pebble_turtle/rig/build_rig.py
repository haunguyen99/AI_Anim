# Chay trong Frolvy cong 9881 sau khi da import FBX + xoay mesh ve Y-up (+Z la huong mat).
import math
for j in list(api.ls("Joint")) + [c for c in api.ls("Curve")] + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(j)
    except Exception: pass
MESH = dict(shell="tripo_node_20d58e65", head="tripo_node_20d58e65.001", front="tripo_node_20d58e65.002", back="tripo_node_20d58e65.003")

# name: (parent, (x,y,z), side, label)
J = [
 ("DEF_Root_M", None, (0, 0.30, 0.0), "centre", "root"),
 ("DEF_Tail1_M", "DEF_Root_M", (0, 0.14, -0.28), "centre", "tail1"),
 ("DEF_Tail2_M", "DEF_Tail1_M", (0, 0.10, -0.46), "centre", "tail2"),
 ("DEF_Neck_M", "DEF_Root_M", (0, 0.26, 0.26), "centre", "neck"),
 ("DEF_Head_M", "DEF_Neck_M", (0, 0.30, 0.38), "centre", "head"),
 ("Muzzle", "DEF_Head_M", (0, 0.24, 0.58), "centre", "muzzle"),
]
for s, sx in (("L", 1), ("R", -1)):
    for pre, hip, ank, toe in (("Front", (0.22, 0.21, 0.26), (0.26, 0.07, 0.36), (0.30, 0.0, 0.44)),
                               ("Back", (0.28, 0.20, -0.20), (0.33, 0.07, -0.21), (0.37, 0.0, -0.15))):
        side = "left" if s == "L" else "right"
        J += [("DEF_%sHip_%s" % (pre, s), "DEF_Root_M", (hip[0]*sx, hip[1], hip[2]), side, pre.lower()+"hip"),
              ("DEF_%sAnkle_%s" % (pre, s), "DEF_%sHip_%s" % (pre, s), (ank[0]*sx, ank[1], ank[2]), side, pre.lower()+"ankle"),
              ("DEF_%sToe_%s" % (pre, s), "DEF_%sAnkle_%s" % (pre, s), (toe[0]*sx, toe[1], toe[2]), side, pre.lower()+"toe")]
made = {}
for n, par, p, side, lab in J:
    api.select([])
    j = api.create_joint(); api.select([])
    api.move(j, *p)
    made[n] = j
for n, par, p, side, lab in J:
    if par: api.parent(made[n], made[par])
for n, par, p, side, lab in J:
    api.rename(made[n], n)
    try: api.set_joint_label(n, side, lab)
    except Exception as e: print("label", n, e)
    made[n] = n
api.select([])
print(len(api.ls("Joint")), "joints")

# ---------------- controls (FK): CTL_x in group CTL_x_grp, hierarchy mirrors the joints
def ctl(name, pos, radius, axis, color):
    c = api.create_circle(radius, axis)
    api.move(c, *pos)
    g = api.create_group(); api.move(g, *pos)
    api.parent(c, g)
    api.rename(c, name); api.rename(g, name + "_grp")
    api.set_curve_color(name, *color)
    return name
cmap = {}
YEL, RED, BLU, GRN = (1, .9, .1), (.9, .2, .2), (.2, .4, 1), (.2, .9, .3)
cmap["Main"] = ctl("CTL_Main", (0, 0.0, 0.0), 0.85, "y", YEL)
for n, par, p, side, lab in J:
    if n == "Muzzle": continue
    short = n[4:]
    if short == "Root_M": rad, ax, col = 0.55, "y", YEL
    elif short in ("Neck_M", "Head_M"): rad, ax, col = (0.14 if short == "Neck_M" else 0.2), "z", YEL
    elif "Tail" in short: rad, ax, col = 0.07, "y", YEL
    else:
        rad, ax = (0.07 if "Hip" in short else 0.055), "x"
        col = BLU if short.endswith("_L") else RED
    cmap[short] = ctl("CTL_" + short, p, rad, ax, col)
# control hierarchy
api.parent("CTL_Root_M_grp", "CTL_Main")
for n, par, p, side, lab in J:
    if n == "Muzzle" or par is None: continue
    api.parent("CTL_%s_grp" % n[4:], "CTL_%s" % par[4:])
# drive joints
for n, par, p, side, lab in J:
    if n == "Muzzle": continue
    api.select(["CTL_" + n[4:], n])
    api.constrain("parent", True)
api.select([])
for n in list(cmap.values()):
    api.lock_channels(n, "sx sy sz", False)
print("controls", len(api.ls("Curve")))
print(api.check_rig())
