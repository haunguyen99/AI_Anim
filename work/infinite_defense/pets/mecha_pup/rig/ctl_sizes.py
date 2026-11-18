"""Shrink Mecha Pup controls to fit a 1.1 m / 0.9 m wide pet (user 2026-11-11: too big, cluttered). Target = largest extent in m."""
T = {"Main": .80, "Root_M": .86, "RootX_M": .50, "IKChest_M": .52, "IKMid_M": .46, "HipSwinger_M": .0,
     "Chest_M": .60, "Spine1_M": .46, "Neck_M": .42, "Head_M": .72,
     "Hip": .34, "Knee": .30, "Ankle": .30, "Toes": .22, "Shoulder": .30, "Elbow": .26, "Wrist": .26,
     "IKWrist": .16, "IKAnkle": .16, "PoleArm": .12, "PoleLeg": .10}
def run(api):
    for c in sorted(n for n in api.ls("Curve") if n.startswith("CTL_")):
        key = c[4:]; base = key.rsplit("_", 1)[0] if key[-2:] in ("_L", "_R") else key
        tgt = T.get(key, T.get(base))
        if not tgt: continue
        p = api.curve_points(c); cur = max(max(p[i::3]) - min(p[i::3]) for i in range(3))
        if cur > tgt * 1.02: api.scale_curve_shape(c, tgt / cur)

UP = {"Ant1_M": .13, "Ant2_M": .13, "Dish_M": .13, "Backpack_M": .15, "Tail1_M": .14, "Tail2_M": .12, "Ear1": .12, "Ear2": .12, "FToes": .10}
def run_up(api):
    for c in sorted(n for n in api.ls("Curve") if n.startswith("CTL_")):
        key = c[4:]; base = key.rsplit("_", 1)[0] if key[-2:] in ("_L", "_R") else key
        tgt = UP.get(key, UP.get(base))
        if not tgt: continue
        p = api.curve_points(c); cur = max(max(p[i::3]) - min(p[i::3]) for i in range(3))
        if cur < tgt * 0.98: api.scale_curve_shape(c, tgt / cur)
