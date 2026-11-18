# (build with temp names '__t' so stale animation curves of deleted nodes do not attach during the build; renamed at the end)
T = lambda n: n + '__t'
# Pinchy Balboa: chay trong Frolvy cong 9885 sau khi import FBX (mesh da Y-up, mat +Z). x>0 = L (R = -x, tay phai co Muzzle).
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(j)
    except Exception: pass
J = [
 ("DEF_Root_M", None, (0, 0.22, 0.0), "centre", "root"),
 ("DEF_Head_M", "DEF_Root_M", (0, 0.34, 0.0), "centre", "head"),
 ("DEF_BandA1_M", "DEF_Head_M", (-0.08, 0.44, -0.12), "centre", "bandA1"),
 ("DEF_BandA2_M", "DEF_BandA1_M", (-0.26, 0.46, -0.25), "centre", "bandA2"),
 ("DEF_BandB1_M", "DEF_Head_M", (-0.03, 0.47, -0.13), "centre", "bandB1"),
 ("DEF_BandB2_M", "DEF_BandB1_M", (-0.17, 0.60, -0.25), "centre", "bandB2"),
]
for s, sx in (("L", 1), ("R", -1)):
    side = "left" if s == "L" else "right"
    J += [("DEF_Arm1_%s" % s, "DEF_Root_M", (0.226*sx, 0.286, 0.033), side, "arm1"),
          ("DEF_Arm2_%s" % s, "DEF_Arm1_%s" % s, (0.282*sx, 0.286, 0.033), side, "arm2"),
          ("DEF_Arm3_%s" % s, "DEF_Arm2_%s" % s, (0.375*sx, 0.286, 0.033), side, "arm3"),
          ("DEF_Glove_%s" % s, "DEF_Arm3_%s" % s, (0.469*sx, 0.286, 0.033), side, "glove")]
    for lg, z in (("F", 0.10), ("M", -0.02), ("B", -0.17)):
        J += [("DEF_Leg%s_%s" % (lg, s), "DEF_Root_M", (0.22*sx, 0.16, z), side, "leg" + lg),
              ("DEF_Leg%sTip_%s" % (lg, s), "DEF_Leg%s_%s" % (lg, s), (0.29*sx, 0.02, z), side, "leg%stip" % lg)]
J.append(("DEF_Muzzle_M", "DEF_Glove_R", (-0.58, 0.286, 0.033), "centre", "muzzle"))
made = {}
for n, par, p, side, lab in J:
    api.select([]); j = api.create_joint(); api.select([]); api.move(j, *p); made[n] = j
for n, par, p, side, lab in J:
    if par: api.parent(made[n], made[par])
for n, par, p, side, lab in J:
    api.rename(made[n], T(n))
    try: api.set_joint_label(T(n), side, lab)
    except Exception as e: print("label", n, e)
api.select([])
print(len(api.ls("Joint")), "joints")
def ctl(name, pos, radius, axis, color):
    c = api.create_circle(radius, axis); api.move(c, *pos)
    g = api.create_group(); api.move(g, *pos); api.parent(c, g)
    api.rename(c, T(name)); api.rename(g, T(name + "_grp")); api.set_curve_color(T(name), *color); return T(name)
YEL, RED, BLU = (1, .9, .1), (.9, .2, .2), (.2, .4, 1)
cm = {"Main": ctl("CTL_Main", (0, 0.0, 0.0), 0.7, "y", YEL)}
RAD = {"Root_M": (0.3, "y"), "Head_M": (0.28, "y"), "Glove_L": (0.12, "x"), "Glove_R": (0.12, "x")}
for n, par, p, side, lab in J:
    if n == "DEF_Muzzle_M": continue
    short = n[4:]
    rad, ax = RAD.get(short, (0.06 if "Arm" in short else 0.04, "x"))
    col = YEL if side == "centre" else (BLU if short.endswith("_L") else RED)
    cm[short] = ctl("CTL_" + short, p, rad, ax, col)
api.parent(T("CTL_Root_M_grp"), T("CTL_Main"))
for n, par, p, side, lab in J:
    if n == "DEF_Muzzle_M" or par is None: continue
    api.parent(T("CTL_%s_grp" % n[4:]), T("CTL_%s" % par[4:]))
for n, par, p, side, lab in J:
    if n == "DEF_Muzzle_M": continue
    api.select([T("CTL_" + n[4:]), T(n)]); api.constrain("parent", True)
api.select([])
for n in cm.values(): api.lock_channels(n, "sx sy sz", False)
print("controls", len(api.ls("Curve"))); print(api.check_rig())

# finalize: drop the suffix (stale curves attach now), neutralise them, then the rig is clean
for n in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g.endswith("__t")]:
    if n.endswith("__t"): api.rename(n, n[:-3])
C = [c for c in api.ls("Curve") if c.startswith("CTL_")]
api.set_frame_range(0, 48); api.set_frame(1)
for j in api.ls("Joint"):
    for a in ("rx", "ry", "rz", "tx", "ty", "tz", "sx", "sy", "sz"):
        for f in list(api.list_keys(j + "." + a)): api.delete_key(j + "." + a, int(round(f)))
for f in range(0, 49):
    api.set_frame(f)
    for c in C: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    api.select(C); api.set_key()
api.set_frame(1); api.set_frame(0); api.select([])
print("rig built clean", len(api.ls("Joint")), len(C))
