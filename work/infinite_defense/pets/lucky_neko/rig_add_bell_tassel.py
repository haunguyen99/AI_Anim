# Them chuong co (DEF_Bell_M) + 2 tua tua cua hu (DEF_TasselA1..3_M, DEF_TasselB1..3_M) vao rig dang mo (khong dung lai rig). Sau do chay rig_skin.py.
J = [("DEF_Bell_M", "DEF_Spine1_M", (0, 0.24, 0.15), "centre", "bell"),
     ("DEF_TasselA1_M", "DEF_Jar_M", (-0.417, 0.14, 0.025), "centre", "tasselA1"),
     ("DEF_TasselA2_M", "DEF_TasselA1_M", (-0.432, 0.085, 0.062), "centre", "tasselA2"),
     ("DEF_TasselA3_M", "DEF_TasselA2_M", (-0.431, 0.04, 0.068), "centre", "tasselA3"),
     ("DEF_TasselB1_M", "DEF_Jar_M", (-0.424, 0.14, 0.019), "centre", "tasselB1"),
     ("DEF_TasselB2_M", "DEF_TasselB1_M", (-0.472, 0.09, 0.037), "centre", "tasselB2"),
     ("DEF_TasselB3_M", "DEF_TasselB2_M", (-0.478, 0.05, 0.043), "centre", "tasselB3")]
RAD = {"Bell_M": (0.04, "x")}
made = {}
for n, par, p, side, lab in J:
    api.select([]); j = api.create_joint(); api.select([]); api.move(j, *p); made[n] = j
for n, par, p, side, lab in J:
    api.parent(made[n], made.get(par, par))
for n, par, p, side, lab in J:
    api.rename(made[n], n)
    try: api.set_joint_label(n, side, lab)
    except Exception as e: print("label", n, e)
api.select([])
def ctl(name, pos, radius, axis, color):
    c = api.create_circle(radius, axis); api.move(c, *pos)
    g = api.create_group(); api.move(g, *pos); api.parent(c, g)
    api.rename(c, name); api.rename(g, name + "_grp"); api.set_curve_color(name, *color); return name
GRN = (.2, .9, .3); YEL = (1, .9, .1)
for n, par, p, side, lab in J:
    short = n[4:]; rad, ax = RAD.get(short, (0.025, "y"))
    ctl("CTL_" + short, p, rad, ax, YEL if short == "Bell_M" else GRN)
for n, par, p, side, lab in J:
    api.parent("CTL_%s_grp" % n[4:], "CTL_%s" % par[4:])
    api.select(["CTL_" + n[4:], n]); api.constrain("parent", True)
api.select([])
for n, par, p, side, lab in J: api.lock_channels("CTL_" + n[4:], "sx sy sz", False)
print(len(api.ls("Joint")), "joints", len(api.ls("Curve")), "controls"); print(api.check_rig())
