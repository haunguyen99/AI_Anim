# Sau rig_add_wing_joint.py: joint Wing2/Wing3 bi lech (offset constraint) -> dat local = local cua group control, tao lai constraint. Chay o frame 5 (control = 0).
api.set_frame(1); api.set_frame(5)
ALL = [c for c in api.ls("Curve") if c.startswith("CTL_") and c != "CTL_Main"]
print("max ctl abs", max(abs(api.get_attr(c + "." + a)) for c in ALL for a in ("rx", "ry", "rz", "tx", "ty", "tz")))
LOC = {"2": (0.094, 0.041, -0.01), "3": (0.086, 0.059, -0.01), "4": (0.12, -0.04, -0.03)}
for s, k in (("L", 1), ("R", -1)):
    names = ["DEF_Wing%s_%s" % (n, s) for n in ("2", "3", "4")]
    api.select(names); api.remove_constraints(); api.select([])
    for n in ("2", "3", "4"):
        j = "DEF_Wing%s_%s" % (n, s); v = LOC[n]
        api.rotate(j, 0, 0, 0); api.move(j, v[0] * k, v[1], v[2])
    for n in ("2", "3", "4"):
        api.select(["CTL_Wing%s_%s" % (n, s), "DEF_Wing%s_%s" % (n, s)]); api.constrain("parent", True)
api.select([])
for n in ("1", "2", "3", "4"):
    j = "DEF_Wing%s_L" % n
    print(j, [round(api.get_attr(j + "." + a), 3) for a in ("tx", "ty", "tz", "rx", "ry", "rz")])
print(len(api.constraints()))
