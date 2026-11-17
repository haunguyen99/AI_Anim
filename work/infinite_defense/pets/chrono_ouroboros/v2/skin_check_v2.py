import math
OB = "Pet_chrono_ouroboros"
CT = [c for c in api.ls("Curve") if c.startswith("CTL_") and c != "CTL_Main"]
def setpose(d):
    for c in CT: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    for c, v in d.items(): api.rotate("CTL_" + c, v[0], v[1], v[2])
    api.set_frame(3); api.set_frame(0)
setpose({})
md = api.mesh_data(OB); idx = list(md['vertices']); P = md['positions']; P0 = [P[i*3:i*3+3] for i in range(len(idx))]
pos = {v: i for i, v in enumerate(idx)}; E = set(); c = 0
for s in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c+s]]; c += s
    for k in range(s): E.add(tuple(sorted((cs[k], cs[(k+1) % s]))))
E = sorted(E)
def report(name, d):
    setpose(d); Pf = api.mesh_data(OB, True)['positions']; Q = [Pf[i*3:i*3+3] for i in range(len(idx))]
    mv = max(math.dist(Q[i], P0[i]) for i in range(len(idx))); w = []
    for a, b in E:
        l0 = math.dist(P0[a], P0[b])
        if l0 < 1e-4: continue
        w.append((math.dist(Q[a], Q[b]) - l0, math.dist(Q[a], Q[b]) / l0, [round(x, 2) for x in P0[a]]))
    w.sort(key=lambda t: -t[0])
    print("%-18s maxmove %.3f | worst: %s" % (name, mv, "; ".join("+%.3f x%.1f@%s" % t for t in w[:3])))
POSES = {
 "spine S pitch 12": {"Spine1_M": (12, 0, 0), "Spine2_M": (-12, 0, 0), "Spine3_M": (12, 0, 0), "Spine4_M": (-12, 0, 0)},
 "spine yaw 10": {"Spine1_M": (0, 10, 0), "Spine2_M": (0, -10, 0), "Spine3_M": (0, 10, 0), "Spine4_M": (0, -10, 0)},
 "tail wave 25": {"Tail1_M": (-25, 0, 0), "Tail2_M": (25, 0, 0), "Tail3_M": (-25, 0, 0), "Tail4_M": (25, 0, 0)},
 "tail yaw 25": {"Tail1_M": (0, 25, 0), "Tail2_M": (0, -25, 0), "Tail3_M": (0, 25, 0), "Tail4_M": (0, -25, 0)},
 "neck up 25": {"Neck1_M": (-25, 0, 0), "Neck2_M": (-15, 0, 0), "Head_M": (-20, 0, 0)},
 "neck yaw 25": {"Neck1_M": (0, 25, 0), "Neck2_M": (0, 15, 0), "Head_M": (0, 20, 0)},
 "head down 25": {"Head_M": (25, 0, 0)},
 "jaw open 30": {"Jaw_M": (30, 0, 0)},
 "hourglass spin 90": {"Hourglass_M": (0, 90, 0)},
}
for n, d in POSES.items(): report(n, d)
setpose({})
