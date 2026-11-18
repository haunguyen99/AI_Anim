# Lucky Neko: joint DEF + control FK (kieu Night Bat). Y len, mat +Z, L = +x. Chay trong Frolvy cong 9891 sau rig_import.py.
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(j)
    except Exception: pass
J = [
 ("DEF_Root_M", None, (0, 0.095, 0.02), "centre", "root"),
 ("DEF_Spine1_M", "DEF_Root_M", (0, 0.17, 0.02), "centre", "spine"),
 ("DEF_Head_M", "DEF_Spine1_M", (0, 0.262, 0.02), "centre", "head"),
 ("DEF_Tail1_M", "DEF_Root_M", (0, 0.115, -0.075), "centre", "tail1"),
 ("DEF_Tail2_M", "DEF_Tail1_M", (0, 0.115, -0.14), "centre", "tail2"),
 ("DEF_Tail3_M", "DEF_Tail2_M", (0, 0.115, -0.20), "centre", "tail3"),
 ("DEF_Jar_M", "DEF_Root_M", (-0.411, 0.112, 0.0), "centre", "jar"),
]
for s, sx in (("L", 1), ("R", -1)):
    side = "left" if s == "L" else "right"
    J += [("DEF_Ear1_%s" % s, "DEF_Head_M", (0.088*sx, 0.458, 0.027), side, "ear1"),
          ("DEF_Ear2_%s" % s, "DEF_Ear1_%s" % s, (0.095*sx, 0.498, 0.027), side, "ear2"),
          ("DEF_Shoulder_%s" % s, "DEF_Spine1_M", (0.10*sx, 0.215, 0.02), side, "shoulder"),
          ("DEF_Elbow_%s" % s, "DEF_Shoulder_%s" % s, (0.165*sx, 0.222, 0.02), side, "elbow"),
          ("DEF_Wrist_%s" % s, "DEF_Elbow_%s" % s, (0.21*sx, 0.222, 0.02), side, "wrist"),
          ("DEF_Hip_%s" % s, "DEF_Root_M", (0.06*sx, 0.075, 0.03), side, "hip"),
          ("DEF_Ankle_%s" % s, "DEF_Hip_%s" % s, (0.06*sx, 0.035, 0.025), side, "ankle"),
          ("DEF_Toes_%s" % s, "DEF_Ankle_%s" % s, (0.06*sx, 0.012, 0.075), side, "toes")]
J += [("DEF_Coin_L", "DEF_Wrist_L", (0.468, 0.126, 0.0), "left", "coin"),
      ("DEF_Muzzle_M", "DEF_Coin_L", (0.468, 0.126, 0.03), "centre", "muzzle")]
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
cm = {"Main": ctl("CTL_Main", (0, 0.0, 0.0), 0.3, "y", YEL)}
RAD = {"Root_M": (0.15, "y"), "Spine1_M": (0.13, "y"), "Head_M": (0.18, "y"), "Jar_M": (0.11, "z"), "Coin_L": (0.13, "z"),
       "Tail1_M": (0.04, "z"), "Tail2_M": (0.035, "z"), "Tail3_M": (0.03, "z")}
for k in ("Shoulder", "Elbow", "Wrist"): RAD[k] = (0.04, "x")
for k in ("Hip", "Ankle", "Toes"): RAD[k] = (0.035, "y")
for k in ("Ear1", "Ear2"): RAD[k] = (0.035, "y")
for n, par, p, side, lab in J:
    if n == "DEF_Muzzle_M": continue
    short = n[4:]; key = short[:-2] if short[-2:] in ("_L", "_R") else short
    rad, ax = RAD.get(short, RAD.get(key, (0.05, "x")))
    col = GRN if short in ("Jar_M", "Coin_L") else (YEL if side == "centre" else (BLU if short.endswith("_L") else RED))
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
