# Kitsune Nine-Mist: joint DEF + control FK + CTL_TailFan (xòe quạt chung). Chạy 1 lần trong scene vừa import mesh (Y lên, mặt +Z).
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read())
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp", "top", "front", "side")]:
    try: api.delete_node(j)
    except Exception: pass
R = lambda p: tuple(round(x, 4) for x in p)
# name: (parent, pos, side, label)
J = [
 ("DEF_Root_M", None, (0, 0.24, 0.14), "centre", "root"),
 ("DEF_Spine1_M", "DEF_Root_M", (0, 0.30, 0.22), "centre", "spine"),
 ("DEF_Head_M", "DEF_Spine1_M", (0, 0.39, 0.27), "centre", "head"),
]
for s, sx in (("L", 1), ("R", -1)):
    side = "left" if s == "L" else "right"
    J += [("DEF_Ear1_%s" % s, "DEF_Head_M", (0.17 * sx, 0.60, 0.20), side, "ear1"),
          ("DEF_Ear2_%s" % s, "DEF_Ear1_%s" % s, (0.185 * sx, 0.72, 0.21), side, "ear2"),
          ("DEF_FLeg1_%s" % s, "DEF_Spine1_M", (0.11 * sx, 0.19, 0.25), side, "fleg1"),
          ("DEF_FLeg2_%s" % s, "DEF_FLeg1_%s" % s, (0.07 * sx, 0.10, 0.257), side, "fleg2"),
          ("DEF_FLeg3_%s" % s, "DEF_FLeg2_%s" % s, (0.08 * sx, 0.03, 0.295), side, "fleg3"),
          ("DEF_BLeg1_%s" % s, "DEF_Root_M", (0.125 * sx, 0.19, 0.057), side, "bleg1"),
          ("DEF_BLeg2_%s" % s, "DEF_BLeg1_%s" % s, (0.135 * sx, 0.105, 0.0), side, "bleg2"),
          ("DEF_BLeg3_%s" % s, "DEF_BLeg2_%s" % s, (0.142 * sx, 0.03, 0.022), side, "bleg3")]
for t in TAILS:
    side = {"M": "centre", "L": "left", "R": "right"}[t['s']]; prev = "DEF_Root_M"
    for n in range(5):
        nm = tail_name(t, n + 1); J.append((nm, prev, R(t['J'][n]), side, "tail%d_%d" % (t['k'], n + 1))); prev = nm
    J.append((muzzle_name(t), prev, R(t['tip']), side, "muzzle%d" % t['k']))
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
YEL, RED, BLU, PUR = (1, .9, .1), (.9, .2, .2), (.2, .4, 1), (.7, .3, 1)
cm = {"Main": ctl("CTL_Main", (0, 0.0, 0.1), 0.55, "y", YEL)}
RAD = {"Root_M": (0.2, "y"), "Spine1_M": (0.17, "y"), "Head_M": (0.26, "y")}
def axis_of(a, b):
    d = [abs(b[i] - a[i]) for i in range(3)]; return "xyz"[d.index(max(d))]
AX = {}
for t in TAILS:
    P = [t['J'][i] for i in range(5)] + [t['tip']]
    for n in range(5): AX[tail_name(t, n + 1)] = (0.075 - 0.012 * n, axis_of(P[n], P[n + 1]))
for n, par, p, side, lab in J:
    if "Muzzle" in n: continue
    short = n[4:]
    rad, ax = RAD.get(short, AX.get(n, (0.05, "x")))
    col = YEL if side == "centre" else (BLU if short.endswith("_L") else RED)
    if short.startswith("Tail"): col = PUR if side == "centre" else ((.3, .7, 1) if side == "left" else (1, .5, .6))
    cm[short] = ctl("CTL_" + short, p, rad, ax, col)
api.parent("CTL_Root_M_grp", "CTL_Main")
for n, par, p, side, lab in J:
    if "Muzzle" in n or par is None: continue
    api.parent("CTL_%s_grp" % n[4:], "CTL_%s" % par[4:])
for n, par, p, side, lab in J:
    if "Muzzle" in n: continue
    api.select(["CTL_" + n[4:], n]); api.constrain("parent", True)
api.select([])
for n in cm.values(): api.lock_channels(n, "sx sy sz", False)
# control xòe quạt chung: attr fan (-1 khép .. +1 xòe) lái xoay Z của group gốc từng đuôi (driven key trên group => control vẫn key tự do)
fc = ctl("CTL_TailFan", (0, 0.55, -0.50), 0.09, "z", PUR)
api.parent("CTL_TailFan_grp", "CTL_Root_M")
api.add_attr(fc, "fan", 0.0, -1.0, 1.0, "float", "", True)
api.lock_channels(fc, "tx ty tz rx ry rz sx sy sz", True)
FAN = {}
for t in TAILS:
    if t['k'] == 1: continue
    P0, P3 = t['J'][0], t['tip']; phi = abs(math.degrees(math.atan2(P3[0] - P0[0], P3[1] - P0[1])))
    sg = 1 if t['s'] == "L" else -1
    FAN[t['k'], t['s']] = (phi, sg)
    g = "CTL_Tail%d_1_%s_grp" % (t['k'], t['s'])
    for fv, mult in ((-1.0, +0.55), (0.0, 0.0), (1.0, -0.30)):
        api.set_driven_key("CTL_TailFan.fan", g + ".rz", fv, sg * mult * phi)
print("fan", {k: round(v[0]) for k, v in FAN.items()})
print("controls", len(api.ls("Curve"))); print(api.check_rig())
