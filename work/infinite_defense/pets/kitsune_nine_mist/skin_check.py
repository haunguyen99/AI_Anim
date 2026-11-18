import math
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read())
CT = [c for c in api.ls("Curve") if c.startswith("CTL_") and c not in ("CTL_Main", "CTL_TailFan")]
def setpose(d, fan=0.0):
    for c in CT: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    api.set_attr("CTL_TailFan.fan", fan)
    for c, v in d.items(): api.rotate(c, v[0], v[1], v[2])
    api.set_frame(3); api.set_frame(0)
GRP = lambda j: "T" if "Tail" in j else "E" if "Ear" in j else "L" if "Leg" in j else "H" if "Head" in j else "B"
setpose({}); DG = {}
for i in range(len(IDX)):
    w = api.vertex_weights(IDX[i]); g = {}
    for j, v in w:
        if v > 0: g[GRP(j)] = g.get(GRP(j), 0) + v
    DG[i] = max(g, key=g.get)
E = set()
for i in range(len(IDX)):
    for n in NB[i]: E.add((min(i, n), max(i, n)))
P0 = V
def report(name, d, fan=0.0, top=4):
    setpose(d, fan); md = api.mesh_data(MESH, True); Pf = md['positions']; Q = [Pf[i * 3:i * 3 + 3] for i in range(len(IDX))]
    mv = {g: 0.0 for g in "TELHB"}; worst = []
    for i in range(len(IDX)): mv[DG[i]] = max(mv[DG[i]], math.dist(Q[i], P0[i]))
    for a, b in E:
        l0 = math.dist(P0[a], P0[b])
        if l0 < 1e-4: continue
        l1 = math.dist(Q[a], Q[b]); worst.append((l1 - l0, l1 / l0, DG[a] + DG[b], [round(x, 2) for x in P0[a]]))
    worst.sort(key=lambda t: -t[0])
    print("%-18s move tail %.2f ear %.2f leg %.2f head %.2f body %.2f | %s" % (name, mv["T"], mv["E"], mv["L"], mv["H"], mv["B"], "; ".join("+%.3f x%.1f %s@%s" % (w[0], w[1], w[2], w[3]) for w in worst[:top])))
POSES = {
 "fan closed": ({}, -1.0), "fan open": ({}, 1.0),
 "tail3L rz 30": ({"CTL_Tail3_1_L": (0, 0, 30)}, 0), "tail3L ry 30": ({"CTL_Tail3_1_L": (0, 30, 0)}, 0),
 "tail1 rx 30": ({"CTL_Tail1_1_M": (30, 0, 0)}, 0), "tail1 bend all": ({"CTL_Tail1_1_M": (20, 0, 0), "CTL_Tail1_2_M": (20, 0, 0), "CTL_Tail1_3_M": (20, 0, 0)}, 0),
 "ears out 25": ({"CTL_Ear1_L": (0, 0, -25), "CTL_Ear1_R": (0, 0, 25)}, 0), "ears fwd 25": ({"CTL_Ear1_L": (25, 0, 0), "CTL_Ear1_R": (25, 0, 0)}, 0),
 "head turn 30": ({"CTL_Head_M": (0, 30, 0)}, 0), "head nod 25": ({"CTL_Head_M": (25, 0, 0)}, 0), "head up 25": ({"CTL_Head_M": (-25, 0, 0)}, 0),
 "fleg fwd 30": ({"CTL_FLeg1_L": (-30, 0, 0), "CTL_FLeg1_R": (30, 0, 0)}, 0), "bleg fwd 30": ({"CTL_BLeg1_L": (30, 0, 0), "CTL_BLeg1_R": (-30, 0, 0)}, 0),
 "lower legs 30": ({"CTL_FLeg2_L": (30, 0, 0), "CTL_BLeg2_L": (30, 0, 0)}, 0),
 "spine 20": ({"CTL_Spine1_M": (20, 0, 0)}, 0), "root rz 15": ({"CTL_Root_M": (0, 0, 15)}, 0),
}
for n, (d, f) in POSES.items(): report(n, d, f)
setpose({})
