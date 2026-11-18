# Them 1 dot canh (Wing2 moi giua Wing1 va Wing2 cu): doi ten Wing3->Wing4, Wing2->Wing3, tao Wing2 moi. Chay 1 lan, o pose 0, tren scene da co rig.
api.set_frame(1); api.set_frame(0)
NEW = (0.194, 0.231, 0.04)
for s, k in (("L", 1), ("R", -1)):
    side = "left" if s == "L" else "right"
    for old, new in (("3", "4"), ("2", "3")):
        api.rename("DEF_Wing%s_%s" % (old, s), "DEF_Wing%s_%s" % (new, s))
        api.rename("CTL_Wing%s_%s" % (old, s), "CTL_Wing%s_%s" % (new, s))
        api.rename("CTL_Wing%s_%s_grp" % (old, s), "CTL_Wing%s_%s_grp" % (new, s))
    p = (NEW[0] * k, NEW[1], NEW[2])
    api.select([]); j = api.create_joint(); api.select([]); api.move(j, *p)          # world (no parent yet)
    api.rename(j, "DEF_Wing2_%s" % s)
    try: api.set_joint_label("DEF_Wing2_%s" % s, side, "wing2")
    except Exception as e: print("label", e)
    api.parent("DEF_Wing2_%s" % s, "DEF_Wing1_%s" % s)
    api.parent("DEF_Wing3_%s" % s, "DEF_Wing2_%s" % s)
    # control
    c = api.create_circle(0.05, "x"); api.move(c, *p)
    g = api.create_group(); api.move(g, *p); api.parent(c, g)
    api.rename(c, "CTL_Wing2_%s" % s); api.rename(g, "CTL_Wing2_%s_grp" % s)
    api.set_curve_color("CTL_Wing2_%s" % s, *((.2, .4, 1) if s == "L" else (.9, .2, .2)))
    api.parent("CTL_Wing2_%s_grp" % s, "CTL_Wing1_%s" % s)
    api.parent("CTL_Wing3_%s_grp" % s, "CTL_Wing2_%s" % s)
    api.select(["CTL_Wing2_%s" % s, "DEF_Wing2_%s" % s]); api.constrain("parent", True)
    api.lock_channels("CTL_Wing2_%s" % s, "sx sy sz", False)
api.select([])
print(api.constraints()[-4:], len(api.ls("Joint")), len(api.ls("Curve")))
for n in ("DEF_Wing1_L", "DEF_Wing2_L", "DEF_Wing3_L", "DEF_Wing4_L"): print(n, api.get_hierarchy(n) if hasattr(api, "get_hierarchy") else "")
