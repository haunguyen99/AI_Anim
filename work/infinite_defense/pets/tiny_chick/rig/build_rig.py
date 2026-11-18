# Tiny Chick: chay trong Frolvy cong 9882 sau khi import FBX + xoay -90 X + freeze (Y len, mat +Z). Joint + control FK.
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(j)
    except Exception: pass
# name: (parent, (x,y,z), side, label)   x>0 = L
J = [
 ("DEF_Root_M", None, (0, 0.40, 0.0), "centre", "root"),
 ("DEF_Spine1_M", "DEF_Root_M", (0, 0.48, 0.0), "centre", "spine"),
 ("DEF_Head_M", "DEF_Spine1_M", (0, 0.58, 0.0), "centre", "head"),
 ("DEF_Cap_M", "DEF_Head_M", (0, 0.64, -0.20), "centre", "cap"),
 ("CapTip", "DEF_Cap_M", (0, 0.90, -0.10), "centre", "captip"),
 ("DEF_Beak_M", "DEF_Head_M", (0, 0.505, 0.30), "centre", "beak"),
 ("DEF_Muzzle_M", "DEF_Beak_M", (0, 0.505, 0.44), "centre", "muzzle"),
 ("DEF_Shell_M", "DEF_Root_M", (0, 0.30, 0.0), "centre", "shell"),
]
for s, sx in (("L", 1), ("R", -1)):
    side = "left" if s == "L" else "right"
    J += [("DEF_WingA_%s" % s, "DEF_Spine1_M", (0.34*sx, 0.38, 0.05), side, "wing1"),
          ("DEF_WingB_%s" % s, "DEF_WingA_%s" % s, (0.46*sx, 0.42, 0.07), side, "wing2"),
          ("DEF_Ankle_%s" % s, "DEF_Root_M", (0.20*sx, 0.08, -0.02), side, "ankle"),
          ("DEF_Toes_%s" % s, "DEF_Ankle_%s" % s, (0.20*sx, 0.03, 0.13), side, "toes")]
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
YEL, RED, BLU, GRN = (1, .9, .1), (.9, .2, .2), (.2, .4, 1), (.2, .9, .3)
cm = {"Main": ctl("CTL_Main", (0, 0.0, 0.0), 0.7, "y", YEL)}
RAD = {"Root_M": (0.45, "y"), "Spine1_M": (0.4, "y"), "Head_M": (0.36, "y"), "Cap_M": (0.2, "y"), "Beak_M": (0.08, "z"), "Shell_M": (0.42, "y")}
for n, par, p, side, lab in J:
    if n in ("DEF_Muzzle_M", "CapTip"): continue
    short = n[4:]
    rad, ax = RAD.get(short, (0.07, "x"))
    col = YEL if side == "centre" else (BLU if short.endswith("_L") else RED)
    cm[short] = ctl("CTL_" + short, p, rad, ax, col)
api.parent("CTL_Root_M_grp", "CTL_Main")
for n, par, p, side, lab in J:
    if n in ("DEF_Muzzle_M", "CapTip") or par is None: continue
    api.parent("CTL_%s_grp" % n[4:], "CTL_%s" % par[4:])
for n, par, p, side, lab in J:
    if n in ("DEF_Muzzle_M", "CapTip"): continue
    api.select(["CTL_" + n[4:], n]); api.constrain("parent", True)
api.select([])
for n in cm.values(): api.lock_channels(n, "sx sy sz", False)
print("controls", len(api.ls("Curve"))); print(api.check_rig())
