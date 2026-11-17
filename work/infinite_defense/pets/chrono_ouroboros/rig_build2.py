# Dung rig tu joint nguoi dung da xep (nua trai): doi ten spine, mirror sang R, control FK. Chay 1 lan tren scene co mesh + joint.
LABEL = {"Root_M": "root", "Spine1_M": "spine", "Spine2_M": "spine2", "Spine3_M": "spine3", "Spine4_M": "spine4", "Neck1_M": "neck", "Neck2_M": "neck2",
         "Head_M": "head", "Jaw_M": "jaw", "Muzzle_M": "muzzle", "ForeLeg1": "arm1", "ForeLeg2": "arm2", "ForeFoot": "hand", "HindLeg1": "leg1", "HindLeg2": "leg2", "HindFoot": "foot"}
names = set(api.ls("Joint"))
if "joint1" in names:     # nguoi dung them 2 joint giua Spine1 va Spine2 -> Spine2, Spine3; Spine2 cu -> Spine4
    api.rename("DEF_Spine2_M", "DEF_Spine4_M"); api.rename("joint1", "DEF_Spine3_M"); api.rename("joint2", "DEF_Spine2_M")
info = {r['name']: r for r in api.joint_info()}
def lab(n, side):
    k = n[4:]; k = k[:-2] if k.endswith(("_L", "_R")) else k
    try: api.set_joint_label(n, side, LABEL.get(k if k.endswith("_M") else k, "other"))
    except Exception as e: print("label", n, e)
for n in info:
    if n.endswith("_M"): lab(n, "centre")
    elif n.endswith("_L"): lab(n, "left")
made = {}
for n, r in list(info.items()):
    if n.endswith("_L"):
        x, y, z = r['world']; api.select([]); j = api.create_joint(); api.select([]); api.move(j, -x, y, z); made[n[:-2] + "_R"] = (j, r['parent'])
for rn, (j, par) in made.items():
    api.parent(j, par[:-2] + "_R" if par.endswith("_L") else par)
for rn, (j, par) in made.items():
    api.rename(j, rn); lab(rn, "right")
api.select([])
info = {r['name']: r for r in api.joint_info()}
print(len(info), "joints")
def ctl(name, pos, radius, axis, color):
    c = api.create_circle(radius, axis); api.move(c, *pos)
    g = api.create_group(); api.move(g, *pos); api.parent(c, g)
    api.rename(c, name); api.rename(g, name + "_grp"); api.set_curve_color(name, *color); return name
YEL, RED, BLU = (1, .9, .1), (.9, .2, .2), (.2, .4, 1)
ctl("CTL_Main", (0, 0, 0), 0.8, "y", YEL)
RAD = {"Root_M": (0.25, "z"), "Spine1_M": (0.22, "z"), "Spine2_M": (0.22, "z"), "Spine3_M": (0.22, "z"), "Spine4_M": (0.22, "z"), "Neck1_M": (0.2, "z"), "Neck2_M": (0.17, "z"), "Head_M": (0.2, "z"), "Jaw_M": (0.08, "x")}
for t in range(1, 6): RAD["Tail%d_M" % t] = (0.17 - 0.02 * t, "z")
order = list(info)
for n in order:
    if n == "DEF_Muzzle_M": continue
    s = n[4:]; rad, ax = RAD.get(s, (0.07, "y"))
    col = YEL if s.endswith("_M") else (BLU if s.endswith("_L") else RED)
    ctl("CTL_" + s, info[n]['world'], rad, ax, col)
api.parent("CTL_Root_M_grp", "CTL_Main")
for n in order:
    p = info[n]['parent']
    if n == "DEF_Muzzle_M" or not p or n == "DEF_Root_M": continue
    api.parent("CTL_%s_grp" % n[4:], "CTL_%s" % p[4:])
for n in order:
    if n == "DEF_Muzzle_M": continue
    api.select(["CTL_" + n[4:], n]); api.constrain("parent", True)
api.select([])
for c in api.ls("Curve"): api.lock_channels(c, "sx sy sz", False)
print("controls", len(api.ls("Curve"))); print(api.check_rig())
