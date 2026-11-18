import math
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read())
E = [(i, n) for i in range(len(IDX)) for n in NB[i] if i < n and math.dist(V[i], V[n]) > 1e-4]
for f in (6, 7, 8, 9):
    api.set_frame(f); md = api.mesh_data(MESH, True); Pf = md['positions']; Q = [Pf[i * 3:i * 3 + 3] for i in range(len(IDX))]
    w = sorted(((math.dist(Q[a], Q[b]) - math.dist(V[a], V[b]), math.dist(V[a], V[b]), a) for a, b in E), reverse=True)[:3]
    print(f, "min y cm", round(min(q[1] for q in Q) * 100, 1), [(round(d * 100, 1), round(l * 100, 1), [round(x, 2) for x in V[a]], [j for j, v in api.vertex_weights(IDX[a]) if v > 0.25]) for d, l, a in w])
api.set_frame(0)
