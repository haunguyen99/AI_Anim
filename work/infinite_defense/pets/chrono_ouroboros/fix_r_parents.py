for a, p in [("HindLeg2_R", "HindLeg1_R"), ("HindFoot_R", "HindLeg2_R"), ("ForeLeg2_R", "ForeLeg1_R"), ("ForeFoot_R", "ForeLeg2_R")]:
    api.parent("DEF_" + a, "DEF_" + p)
    api.parent("CTL_%s_grp" % a, "CTL_" + p)
for r in api.joint_info():
    if r['name'].endswith("_R"): print(r['name'], '<-', r['parent'], [round(v, 2) for v in r['world']])
for c in ("CTL_HindLeg2_R", "CTL_ForeFoot_R"): print(c, api.get_attr(c + ".tx") if hasattr(api, "get_attr") else "")
print(api.check_rig())
