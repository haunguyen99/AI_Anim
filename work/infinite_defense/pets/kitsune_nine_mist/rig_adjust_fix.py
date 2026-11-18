exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read())
_src = open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\rig_build.py", encoding="utf-8").read()
exec(_src[_src.index("R = lambda"):_src.index("made = {}")])
P = {n: p for n, par, p, s, l in J}
for n, par, p, s, l in J:
    pp = P[par] if par else (0, 0, 0)
    gp = P[par] if par else (0, 0, 0.1)   # CTL_Main centre
    if "Muzzle" not in n: api.move("CTL_%s_grp" % n[4:], *[p[i] - gp[i] for i in range(3)])
api.move("CTL_TailFan_grp", 0, 0.55 - 0.24, -0.50 - 0.14)
api.set_frame(3); api.set_frame(0)
for n, par, p, s, l in J:
    pp = P[par] if par else (0, 0, 0)
    api.move(n, *[p[i] - pp[i] for i in range(3)])
api.set_frame(3); api.set_frame(0)
bad = 0
for n, par, p, s, l in J:
    m = api.world_matrix(n); q = (m[12], m[13], m[14])
    if math.dist(q, p) > 0.003: bad += 1; print("off", n, [round(x, 3) for x in q], p)
for c in api.ls("Curve"):
    if c.startswith("CTL_") and c not in ("CTL_Main", "CTL_TailFan"):
        m = api.world_matrix(c); n = "DEF_" + c[4:]
        if n in P and math.dist((m[12], m[13], m[14]), P[n]) > 0.003: bad += 1; print("ctl off", c, [round(x, 3) for x in (m[12], m[13], m[14])], P[n])
print("bad", bad); print(api.check_rig())
