# Night Bat: chay trong Frolvy cong 9883 sau khi import FBX + xoay -90 X + freeze (Y len, mat +Z). Joint + control FK.
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(j)
    except Exception: pass
# name: (parent, (x,y,z), side, label)   x>0 = L
J = [
 ("DEF_Root_M", None, (0, 0.09, 0.05), "centre", "root"),
 ("DEF_Spine1_M", "DEF_Root_M", (0, 0.19, 0.07), "centre", "spine"),
 ("DEF_Head_M", "DEF_Spine1_M", (0, 0.27, 0.10), "centre", "head"),
 ("DEF_Jaw_M", "DEF_Head_M", (0, 0.27, 0.17), "centre", "jaw"),
 ("DEF_Muzzle_M", "DEF_Jaw_M", (0, 0.285, 0.30), "centre", "muzzle"),
]
for s, sx in (("L", 1), ("R", -1)):
    side = "left" if s == "L" else "right"
    J += [("DEF_Ear1_%s" % s, "DEF_Head_M", (0.12*sx, 0.45, 0.04), side, "ear1"),
          ("DEF_Ear2_%s" % s, "DEF_Ear1_%s" % s, (0.20*sx, 0.58, 0.0), side, "ear2"),
          ("DEF_Wing1_%s" % s, "DEF_Spine1_M", (0.10*sx, 0.19, 0.05), side, "wing1"),
          ("DEF_Wing2_%s" % s, "DEF_Wing1_%s" % s, (0.194*sx, 0.231, 0.04), side, "wing2"),
          ("DEF_Wing3_%s" % s, "DEF_Wing2_%s" % s, (0.28*sx, 0.29, 0.03), side, "wing3"),
          ("DEF_Wing4_%s" % s, "DEF_Wing3_%s" % s, (0.40*sx, 0.25, 0.0), side, "wing4")]
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
RAD = {"Root_M": (0.2, "y"), "Spine1_M": (0.17, "y"), "Head_M": (0.2, "y"), "Jaw_M": (0.05, "x")}
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
