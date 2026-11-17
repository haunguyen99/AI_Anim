# Model moi (2026-11-14): rong thang, dau cui xuong, KHONG chan, co dong ho cat (hourglass) o giua. Chay tren scene co 2 mesh. Chi joint (chua build).
for j in list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(j)
    except Exception: pass
J = [
 ("DEF_Root_M", None, (0, .30, -0.50), "root"),
 ("DEF_Spine1_M", "DEF_Root_M", (0, .30, -0.13), "spine"),
 ("DEF_Spine2_M", "DEF_Spine1_M", (0, .30, 0.25), "spine2"),
 ("DEF_Spine3_M", "DEF_Spine2_M", (0, .30, 0.60), "spine3"),
 ("DEF_Spine4_M", "DEF_Spine3_M", (0, .30, 0.92), "spine4"),
 ("DEF_Neck1_M", "DEF_Spine4_M", (0, .30, 1.05), "neck"),
 ("DEF_Neck2_M", "DEF_Neck1_M", (0, .30, 1.17), "neck2"),
 ("DEF_Head_M", "DEF_Neck2_M", (0, .30, 1.28), "head"),
 ("DEF_Jaw_M", "DEF_Head_M", (0, .08, 1.38), "jaw"),
 ("DEF_Muzzle_M", "DEF_Jaw_M", (0, -.15, 1.42), "muzzle"),
 ("DEF_Tail1_M", "DEF_Root_M", (0, .29, -0.95), "tail1"),
 ("DEF_Tail2_M", "DEF_Tail1_M", (0, .30, -1.15), "tail2"),
 ("DEF_Tail3_M", "DEF_Tail2_M", (0, .33, -1.32), "tail3"),
 ("DEF_Tail4_M", "DEF_Tail3_M", (0, .40, -1.50), "tail4"),
 ("DEF_Tail5_M", "DEF_Tail4_M", (0, .50, -1.65), "tail5"),
 ("DEF_Hourglass_M", "DEF_Root_M", (0, .30, 0.0), "other"),
]
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
