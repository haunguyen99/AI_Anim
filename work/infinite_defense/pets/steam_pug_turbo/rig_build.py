# Steam-Pug Turbo: joint DEF + control FK (kieu Night Bat). Mesh Y len, mat +Z, x>0 = L. Chay 1 lan tren scene co mesh vua import.
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(j)
    except Exception: pass
J = [
 ("DEF_Root_M", None, (0, 0.33, -0.12), "centre", "root"),
 ("DEF_Spine1_M", "DEF_Root_M", (0, 0.38, 0.05), "centre", "spine"),
 ("DEF_Head_M", "DEF_Spine1_M", (0, 0.55, 0.15), "centre", "head"),
 ("DEF_Goggles_M", "DEF_Head_M", (0, 0.92, 0.28), "centre", "other"),
 ("DEF_Gauge_M", "DEF_Spine1_M", (0, 0.30, 0.30), "centre", "other"),
 ("DEF_Tail1_M", "DEF_Root_M", (0, 0.38, -0.34), "centre", "other"),
 ("DEF_Tail2_M", "DEF_Tail1_M", (0, 0.45, -0.40), "centre", "other"),
 ("DEF_Valve_M", "DEF_Spine1_M", (0, 0.45, -0.22), "centre", "other"),
 ("DEF_Exhaust_M", "DEF_Spine1_M", (0, 0.44, -0.30), "centre", "other"),
 ("DEF_Muzzle_M", "DEF_Exhaust_M", (0, 0.44, -0.47), "centre", "other"),
]
for s, sx in (("L", 1), ("R", -1)):
    side = "left" if s == "L" else "right"
    J += [("DEF_Pipe_%s" % s, "DEF_Spine1_M", (0.12*sx, 0.45, -0.28), side, "other"),
          ("DEF_Tank_%s" % s, "DEF_Spine1_M", (0.20*sx, 0.43, -0.18), side, "other"),
          ("DEF_FLeg1_%s" % s, "DEF_Spine1_M", (0.17*sx, 0.22, 0.16), side, "other"),
          ("DEF_FLeg2_%s" % s, "DEF_FLeg1_%s" % s, (0.17*sx, 0.10, 0.16), side, "other"),
          ("DEF_FPaw_%s" % s, "DEF_FLeg2_%s" % s, (0.17*sx, 0.01, 0.22), side, "other"),
          ("DEF_BLeg1_%s" % s, "DEF_Root_M", (0.12*sx, 0.22, -0.27), side, "other"),
          ("DEF_BLeg2_%s" % s, "DEF_BLeg1_%s" % s, (0.12*sx, 0.10, -0.27), side, "other"),
          ("DEF_BPaw_%s" % s, "DEF_BLeg2_%s" % s, (0.12*sx, 0.01, -0.21), side, "other")]
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
RAD = {"Root_M": (0.22, "y"), "Spine1_M": (0.2, "y"), "Head_M": (0.28, "y"), "Goggles_M": (0.08, "y"), "Gauge_M": (0.05, "z"),
       "Valve_M": (0.06, "y"), "Exhaust_M": (0.05, "z")}
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
