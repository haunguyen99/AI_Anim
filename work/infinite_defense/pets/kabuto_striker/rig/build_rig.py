# Kabuto Striker: joints DEF_* + FK controls (cong 9887). Mesh da import (Y len, mat +Z). x>0 = L
api.select(list(api.ls("Joint")) + list(api.ls("Curve"))); api.remove_constraints(); api.select([])
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(j)
    except Exception: pass
J = [
 ("DEF_Root_M", None, (0, .24, -.08), "centre", "root"),
 ("DEF_Spine1_M", "DEF_Root_M", (0, .36, -.06), "centre", "spine"),
 ("DEF_Chest_M", "DEF_Spine1_M", (0, .48, -.04), "centre", "chest"),
 ("DEF_Neck_M", "DEF_Chest_M", (0, .55, -.02), "centre", "neck"),
 ("DEF_Head_M", "DEF_Neck_M", (0, .62, -.02), "centre", "head"),
 ("DEF_Muzzle_M", "DEF_Head_M", (0, .97, 0.0), "centre", "muzzle"),
 ("DEF_SkirtF_M", "DEF_Root_M", (0, .30, .18), "centre", "skirtf"),
 ("DEF_SkirtFEnd_M", "DEF_SkirtF_M", (0, .08, .22), "centre", "skirtfend"),
 ("DEF_SkirtB_M", "DEF_Root_M", (0, .30, -.38), "centre", "skirtb"),
 ("DEF_SkirtBEnd_M", "DEF_SkirtB_M", (0, .08, -.42), "centre", "skirtbend"),
]
for s, sx in (("L", 1), ("R", -1)):
    side = "left" if s == "L" else "right"
    J += [("DEF_Horn1_%s" % s, "DEF_Head_M", (.17*sx, .74, -.02), side, "horn1"),
          ("DEF_Horn2_%s" % s, "DEF_Horn1_%s" % s, (.36*sx, .84, -.02), side, "horn2"),
          ("DEF_HornEnd_%s" % s, "DEF_Horn2_%s" % s, (.30*sx, .97, -.02), side, "hornend"),
          ("DEF_Sode_%s" % s, "DEF_Chest_M", (.30*sx, .50, -.04), side, "sode"),
          ("DEF_SodeEnd_%s" % s, "DEF_Sode_%s" % s, (.46*sx, .36, -.04), side, "sodeend"),
          ("DEF_SkirtS_%s" % s, "DEF_Root_M", (.36*sx, .30, -.10), side, "skirts"),
          ("DEF_SkirtSEnd_%s" % s, "DEF_SkirtS_%s" % s, (.40*sx, .08, -.10), side, "skirtsend"),
          ("DEF_FFoot_%s" % s, "DEF_Root_M", (.27*sx, .11, .02), side, "ffoot"),
          ("DEF_FFootEnd_%s" % s, "DEF_FFoot_%s" % s, (.27*sx, .0, .04), side, "ffootend"),
          ("DEF_RFoot_%s" % s, "DEF_Root_M", (.19*sx, .11, -.17), side, "rfoot"),
          ("DEF_RFootEnd_%s" % s, "DEF_RFoot_%s" % s, (.19*sx, .0, -.19), side, "rfootend")]
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
RAD = {"Root_M": (.5, "y"), "Spine1_M": (.44, "y"), "Chest_M": (.42, "y"), "Neck_M": (.30, "y"), "Head_M": (.36, "y")}
SKIP = ("DEF_Muzzle_M",) + tuple(n for n, *_ in J if n.endswith(("End_M", "End_L", "End_R")))
for n, par, p, side, lab in J:
    if n in SKIP: continue
    short = n[4:]
    rad, ax = RAD.get(short, (.08, "x"))
    col = YEL if side == "centre" else (BLU if short.endswith("_L") else RED)
    cm[short] = ctl("CTL_" + short, p, rad, ax, col)
api.parent("CTL_Root_M_grp", "CTL_Main")
for n, par, p, side, lab in J:
    if n in SKIP or par is None: continue
    api.parent("CTL_%s_grp" % n[4:], "CTL_%s" % par[4:])
for n, par, p, side, lab in J:
    if n in SKIP: continue
    api.select(["CTL_" + n[4:], n]); api.constrain("parent", True)
api.select([])
for n in cm.values(): api.lock_channels(n, "sx sy sz", False)
print("controls", len(api.ls("Curve"))); print(api.check_rig())
