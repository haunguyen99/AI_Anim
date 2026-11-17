# Rig v3 (2026-11-17): chuỗi thân/đuôi dày hơn để uốn thành vòng tròn (concept ouroboros). Chạy trên scene có 2 mesh (mở joints_v2.fv).
# Thân Spine1-8 (cách ~0,18 m), cổ Neck1-2 + Head + Jaw + Muzzle như v2, đuôi Tail1-7 (~0,17 m) nội suy theo đường đuôi v2, Hourglass con của Root.
import math
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp", "top", "front", "side")]:
    try: api.delete_node(j)
    except Exception: pass
YC = .30
J = [("DEF_Root_M", None, (0, YC, -0.50), "root")]
prev = "DEF_Root_M"
for k in range(1, 9):
    n = "DEF_Spine%d_M" % k; J.append((n, prev, (0, YC, -0.50 + k * 1.42 / 8), "spine" if k == 1 else "other")); prev = n
for n, p, lab in (("Neck1", (0, YC, 1.05), "neck"), ("Neck2", (0, YC, 1.17), "neck2"), ("Head", (0, YC, 1.28), "head")):
    J.append(("DEF_%s_M" % n, prev, p, lab)); prev = "DEF_%s_M" % n
J += [("DEF_Jaw_M", "DEF_Head_M", (0, .08, 1.38), "jaw"), ("DEF_Muzzle_M", "DEF_Jaw_M", (0, -.15, 1.42), "muzzle")]
TP = [(-0.50, .30), (-0.95, .29), (-1.15, .30), (-1.32, .33), (-1.50, .40), (-1.65, .50)]   # (z, y) đường đuôi v2
cum = [0.0]
for a, b in zip(TP, TP[1:]): cum.append(cum[-1] + math.dist(a, b))
NT = 7; prev = "DEF_Root_M"
for k in range(1, NT + 1):
    s = cum[-1] * k / NT
    for i in range(len(TP) - 1):
        if cum[i] <= s <= cum[i + 1] + 1e-9: break
    u = (s - cum[i]) / (cum[i + 1] - cum[i]); z = TP[i][0] + u * (TP[i + 1][0] - TP[i][0]); y = TP[i][1] + u * (TP[i + 1][1] - TP[i][1])
    n = "DEF_Tail%d_M" % k; J.append((n, prev, (0, round(y, 3), round(z, 3)), "tail1" if k == 1 else "other")); prev = n
J.append(("DEF_Hourglass_M", "DEF_Root_M", (0, YC, 0.0), "other"))
made = {}
for n, par, p, lab in J:
    api.select([]); j = api.create_joint(); api.select([]); api.move(j, *p); made[n] = j
for n, par, p, lab in J:
    if par: api.parent(made[n], made[par])
for n, par, p, lab in J:
    api.rename(made[n], n)
    try: api.set_joint_label(n, "centre", lab)
    except Exception as e: print("label", n, e)
api.select([]); api.set_frame(0)
print(len(api.ls("Joint")), "joints")
