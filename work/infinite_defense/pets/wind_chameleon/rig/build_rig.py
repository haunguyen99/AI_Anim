# Wind Chameleon: joints + FK controls (chay trong Frolvy 9884 sau khi import FBX, xoay -90 X, freeze: Y len, mat +Z)
api.select(list(api.ls("Joint")) + list(api.ls("Curve"))); api.remove_constraints(); api.select([])
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(j)
    except Exception: pass
# name: (parent, (x,y,z), side, label)   x>0 = L
J = [
 ("DEF_Root_M", None, (0, .20, -.12), "centre", "root"),
 ("DEF_Spine1_M", "DEF_Root_M", (0, .26, -.02), "centre", "spine"),
 ("DEF_Chest_M", "DEF_Spine1_M", (0, .33, .08), "centre", "chest"),
 ("DEF_Neck_M", "DEF_Chest_M", (0, .40, .15), "centre", "neck"),
 ("DEF_Head_M", "DEF_Neck_M", (0, .45, .22), "centre", "head"),
 ("DEF_Crest_M", "DEF_Head_M", (0, .62, .15), "centre", "crest"),
 ("DEF_Jaw_M", "DEF_Head_M", (0, .31, .22), "centre", "jaw"),
 ("DEF_Mouth_M", "DEF_Head_M", (0, .335, .45), "centre", "mouth"),   # scale joint: squeezes the mouth hole shut (sy ~0.1) / widens it
 ("DEF_Tongue1_M", "DEF_Head_M", (0, .33, .24), "centre", "tongue1"),
 ("DEF_Tongue2_M", "DEF_Tongue1_M", (0, .33, .38), "centre", "tongue2"),
 ("DEF_Tongue3_M", "DEF_Tongue2_M", (0, .33, .50), "centre", "tongue3"),
 ("DEF_Tongue4_M", "DEF_Tongue3_M", (0, .33, .59), "centre", "tongue4"),
 ("DEF_Muzzle_M", "DEF_Tongue4_M", (0, .33, .65), "centre", "muzzle"),
]
TAIL = [(0, .21, -.30), (0, .27, -.43), (0, .41, -.46), (0, .55, -.41), (0, .66, -.33), (0, .70, -.17), (0, .62, -.04), (0, .51, -.06), (0, .48, -.16), (0, .56, -.21)]
prev = "DEF_Root_M"
for i, p in enumerate(TAIL, 1):
    n = "DEF_Tail%d_M" % i; J.append((n, prev, p, "centre", "tail%d" % i)); prev = n
for s, sx in (("L", 1), ("R", -1)):
    side = "left" if s == "L" else "right"
    J += [("DEF_Cheek_%s" % s, "DEF_Head_M", (.13*sx, .32, .34), side, "cheek"),
          ("DEF_Eye_%s" % s, "DEF_Head_M", (.24*sx, .335, .30), side, "eye"),
          ("DEF_FHip_%s" % s, "DEF_Chest_M", (.17*sx, .22, .12), side, "fhip"),
          ("DEF_FAnkle_%s" % s, "DEF_FHip_%s" % s, (.21*sx, .07, .15), side, "fankle"),
          ("DEF_FToes_%s" % s, "DEF_FAnkle_%s" % s, (.21*sx, .03, .24), side, "ftoes"),
          ("DEF_RHip_%s" % s, "DEF_Root_M", (.20*sx, .21, -.10), side, "rhip"),
          ("DEF_RAnkle_%s" % s, "DEF_RHip_%s" % s, (.23*sx, .07, -.17), side, "rankle"),
          ("DEF_RToes_%s" % s, "DEF_RAnkle_%s" % s, (.23*sx, .03, -.10), side, "rtoes")]
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
cm = {"Main": ctl("CTL_Main", (0, 0.0, 0.0), 0.6, "y", YEL)}
RAD = {"Root_M": (.30, "y"), "Spine1_M": (.27, "y"), "Chest_M": (.27, "y"), "Neck_M": (.2, "y"), "Head_M": (.28, "y"),
       "Crest_M": (.07, "x"), "Jaw_M": (.09, "x")}
SKIP = ("DEF_Muzzle_M",)
for n, par, p, side, lab in J:
    if n in SKIP: continue
    short = n[4:]
    rad, ax = RAD.get(short, (.06, "x"))
    if short.startswith("Tongue"): ax = "z"
    col = YEL if side == "centre" else (BLU if short.endswith("_L") else RED)
    if short.startswith("Tail"): col = GRN
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
