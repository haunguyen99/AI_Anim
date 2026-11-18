# Thêm đốt đuôi thứ 5 + dời mọi joint/control về đúng toạ độ thế giới (move = toạ độ LOCAL, nên trừ vị trí cha). Không dựng lại rig.
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read())
_src = open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\rig_build.py", encoding="utf-8").read()
exec(_src[_src.index("R = lambda"):_src.index("made = {}")])
api.select([MESH])
try: api.unbind_skin()
except Exception: pass
api.select([])
have = set(api.ls("Joint"))
for n, par, p, side, lab in [x for x in J if x[0] not in have]:
    api.select([]); j = api.create_joint(); api.select([]); api.move(j, *p); api.parent(j, par); api.rename(j, n)
    try: api.set_joint_label(n, side, lab)
    except Exception as e: print("label", n, e)
    short = n[4:]; col = (.3, .7, 1) if side == "left" else ((1, .5, .6) if side == "right" else (.7, .3, 1))
    c = api.create_circle(0.05, "x"); api.move(c, *p); g = api.create_group(); api.move(g, *p); api.parent(c, g)
    api.rename(c, "CTL_" + short); api.rename(g, "CTL_" + short + "_grp"); api.set_curve_color("CTL_" + short, *col)
    api.parent("CTL_%s_grp" % short, "CTL_%s" % par[4:])
    api.select(["CTL_" + short, n]); api.constrain("parent", True); api.select([]); api.lock_channels("CTL_" + short, "sx sy sz", False)
    for t in TAILS:
        if n == tail_name(t, 5): api.parent(muzzle_name(t), n)
for c in api.ls("Curve"):
    if c.startswith("CTL_") and c not in ("CTL_Main", "CTL_TailFan"): api.rotate(c, 0, 0, 0)
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
