import math
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read())
E = [(i, n) for i in range(len(IDX)) for n in NB[i] if i < n and math.dist(V[i], V[n]) > 1e-4]
for f in (13, 14, 15, 16, 17):
    api.set_frame(f)
    md = api.mesh_data(MESH, True); Pf = md['positions']; Q = [Pf[i * 3:i * 3 + 3] for i in range(len(IDX))]
    w = sorted(((math.dist(Q[a], Q[b]) - math.dist(V[a], V[b]), math.dist(V[a], V[b]), a) for a, b in E), reverse=True)[:2]
    print(f, [(round(d * 100, 1), round(l * 100, 1), [round(x, 2) for x in V[a]], [j for j, v in api.vertex_weights(IDX[a]) if v > 0.2]) for d, l, a in w])
    print("   T5L rot", [round(api.get_attr("CTL_Tail5_%d_L.%s" % (n, a)), 1) for n in (1, 2, 3, 4, 5) for a in ("ry",)], "rz", [round(api.get_attr("CTL_Tail5_%d_L.rz" % n), 1) for n in (1, 2, 3, 4, 5)])
api.set_frame(0)
