# Objective skin check inside Frolvy: mesh_data(posed=True) vs bind. Per pose: max move per group + worst edge stretches (per object, so detached ears are checked on their own).
import math
OBJS = [o for o in api.ls("Object") if o.startswith("Pet_Night_Bat")]
CT = [c for c in api.ls("Curve") if c.startswith("CTL_") and c != "CTL_Main"]
def setpose(d):
    for c in CT: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    for c, v in d.items(): api.rotate(c, v[0], v[1], v[2])
    api.set_frame(3); api.set_frame(0)
GRP = lambda j: "W" if "Wing" in j else "E" if "Ear" in j else "H" if ("Head" in j or "Jaw" in j) else "B"
def dom(w):
    g = {}
    for j, v in w: g[GRP(j)] = g.get(GRP(j), 0) + v
    return max(g, key=g.get)
setpose({}); DATA = {}
for o in OBJS:
    md = api.mesh_data(o); idx = list(md['vertices']); P = md['positions']; P0 = [P[i * 3:i * 3 + 3] for i in range(len(idx))]
    pos = {v: i for i, v in enumerate(idx)}; E = set(); c = 0
    for s in md['face_sizes']:
        cs = [pos.get(q, q) for q in md['face_corners'][c:c + s]]; c += s
        for k in range(s): E.add(tuple(sorted((cs[k], cs[(k + 1) % s]))))
    DATA[o] = (idx, P0, sorted(E), [dom(api.vertex_weights(v)) if True else "B" for v in idx])
def report(name, d, top=5):
    setpose(d); mv = {g: 0.0 for g in "WEHB"}; worst = []
    for o in OBJS:
        idx, P0, E, DG = DATA[o]; md = api.mesh_data(o, True); Pf = md['positions']; Q = [Pf[i * 3:i * 3 + 3] for i in range(len(idx))]
        for i in range(len(idx)): mv[DG[i]] = max(mv[DG[i]], math.dist(Q[i], P0[i]))
        for a, b in E:
            l0 = math.dist(P0[a], P0[b])
            if l0 < 1e-4: continue
            l1 = math.dist(Q[a], Q[b]); worst.append((l1 - l0, l1 / l0, o[-1], DG[a] + DG[b], [round(x, 2) for x in P0[a]]))
    worst.sort(key=lambda t: -t[0])
    print("%-16s move wing %.3f ear %.3f head %.3f body %.3f | worst edges: %s" % (name, mv["W"], mv["E"], mv["H"], mv["B"], "; ".join("+%.3f x%.1f %s@%s" % (w[0], w[1], w[3], w[4]) for w in worst[:top])))
POSES = {
 "wings down 48": {"CTL_Wing1_L": (0, 0, -48), "CTL_Wing1_R": (0, 0, 48)},
 "wings up 48": {"CTL_Wing1_L": (0, 0, 48), "CTL_Wing1_R": (0, 0, -48)},
 "wings fwd 40": {"CTL_Wing1_L": (0, -40, 0), "CTL_Wing1_R": (0, 40, 0)},
 "wings back 40": {"CTL_Wing1_L": (0, 40, 0), "CTL_Wing1_R": (0, -40, 0)},
 "ears out 25": {"CTL_Ear1_L": (0, 0, -25), "CTL_Ear1_R": (0, 0, 25)},
 "ears fwd 25": {"CTL_Ear1_L": (25, 0, 0), "CTL_Ear1_R": (25, 0, 0)},
 "head up 25": {"CTL_Head_M": (-25, 0, 0)},
 "head fwd 25 jaw": {"CTL_Head_M": (25, 0, 0), "CTL_Jaw_M": (30, 0, 0)},
}
for n, d in POSES.items(): report(n, d)
setpose({})
