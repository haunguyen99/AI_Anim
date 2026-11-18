# Chay trong Frolvy 9885: xoa mesh cu, bind mesh moi vao DEF_*, ap trong so tu /tmp/wc_weights_v2.json (tinh boi skin_v2.py)
import json
for o in ("chameleon", "Chameleon_tonge"):
    if o in api.ls("Object"):
        api.delete_node(o)
M = "Pet_Wind_Chameleon"
# tra khop luoi ve cho cu (rig_v2 dau tien dich +0.099)
HEAD = (0.0, 0.45, 0.22)
# Mat (vom trang tren dau) va Ma (2 qua cau xanh): dat joint + nhom control (toa do cuc bo theo Head)
for s_, sx in (("L", 1), ("R", -1)):
    for j, g, w in (("DEF_Eye_" + s_, "CTL_Eye_%s_grp" % s_, (0.19 * sx, 0.465, 0.285)), ("DEF_Cheek_" + s_, "CTL_Cheek_%s_grp" % s_, (0.21 * sx, 0.315, 0.303))):
        api.move(j, w[0] - HEAD[0], w[1] - HEAD[1], w[2] - HEAD[2]); api.move(g, w[0] - HEAD[0], w[1] - HEAD[1], w[2] - HEAD[2])
for n in ("DEF_Tongue1_M", "CTL_Tongue1_M_grp"):
    api.move(n, 0.0 - HEAD[0], 0.33 - HEAD[1], 0.24 - HEAD[2])
for j in list(api.ls("Joint")) + list(api.ls("Curve")):
    pass
d = json.load(open("/tmp/wc_weights_v2.json"))
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_")]
api.select([M])
try: api.unbind_skin()
except Exception: pass
ids0 = list(api.mesh_data(M)["vertices"])
tp = [c for p in d["tongue_pos"] for c in p]
api.set_vertex_positions([ids0[i] for i in d["tongue"]], tp)   # luoi lui ve (mesh o bind, chua skin)
api.select([M]); api.bind_skin(DEF)
ids = list(api.mesh_data(M)["vertices"])   # ids vat ly: sau khi xoa mesh cu id doi ve 0..N-1
assert len(ids) == len(d["rows"])
api.select([M]); api.set_skin_weights(ids, d["rows"])
api.select([])
print("bind", len(DEF), "joints,", len(d["idx"]), "dinh")
print(api.skin_message() if hasattr(api, "skin_message") else "")
