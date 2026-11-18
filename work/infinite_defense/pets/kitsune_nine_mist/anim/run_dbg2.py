import math
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read())
E = [(i, n) for i in range(len(IDX)) for n in NB[i] if i < n and math.dist(V[i], V[n]) > 1e-4]
def worst():
    md = api.mesh_data(MESH, True); Pf = md['positions']; Q = [Pf[i * 3:i * 3 + 3] for i in range(len(IDX))]
    w = max((math.dist(Q[a], Q[b]) / math.dist(V[a], V[b]), a) for a, b in E); return round(w[0], 2), [round(x, 2) for x in V[w[1]]]
api.set_frame(15); print("full", worst())
T5 = ["CTL_Tail5_%d_L" % n for n in range(1, 6)]
for c in T5: api.rotate(c, 0, 0, 0)
api.set_attr("CTL_Tail5_1_L_grp.rz", -30.2); print("tail5 local zeroed, group rz kept:", worst())
api.set_attr("CTL_Tail5_1_L_grp.rz", 0); print("group zero too:", worst())
api.set_frame(0)
