import math
O = api.ls("Object")[0]
CT = [c for c in api.ls("Curve") if c.startswith("CTL_") and c != "CTL_Main"]
def setpose(d):
    for c in CT: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    for c, v in d.items(): api.rotate(c, *v)
    api.set_frame(3); api.set_frame(0)
setpose({}); md = api.mesh_data(O); idx = list(md['vertices']); P = md['positions']; P0 = [P[i*3:i*3+3] for i in range(len(idx))]
pos = {v: i for i, v in enumerate(idx)}; E = set(); c = 0
for s in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c+s]]; c += s
    for k in range(s): E.add(tuple(sorted((cs[k], cs[(k+1) % s]))))
def report(name, d):
    setpose(d); Pf = api.mesh_data(O, True)['positions']; Q = [Pf[i*3:i*3+3] for i in range(len(idx))]
    mv = max(math.dist(Q[i], P0[i]) for i in range(len(idx))); w = []
    for a, b in E:
        l0 = math.dist(P0[a], P0[b])
        if l0 < 1e-4: continue
        l1 = math.dist(Q[a], Q[b]); w.append((l1 - l0, l1 / l0, [round(x, 2) for x in P0[a]]))
    w.sort(key=lambda t: -t[0]); mn = min(w, key=lambda t: t[1])
    print("%-18s move %.3f | worst +%.3f x%.1f @%s | min x%.2f @%s" % (name, mv, w[0][0], w[0][1], w[0][2], mn[1], mn[2]))
POSES = {
 "head up 25": {"CTL_Head_M": (-25, 0, 0)}, "head turn 40": {"CTL_Head_M": (0, 40, 0)}, "head tilt 25": {"CTL_Head_M": (0, 0, 25)},
 "spine fwd 20": {"CTL_Spine1_M": (20, 0, 0)}, "root tilt 20": {"CTL_Root_M": (0, 0, 20)},
 "fleg back 35": {"CTL_FLeg1_L": (-35, 0, 0), "CTL_FLeg1_R": (-35, 0, 0)}, "fleg fwd 35": {"CTL_FLeg1_L": (35, 0, 0), "CTL_FLeg1_R": (35, 0, 0)},
 "bleg back 35": {"CTL_BLeg1_L": (-35, 0, 0), "CTL_BLeg1_R": (-35, 0, 0)}, "bleg fwd 35": {"CTL_BLeg1_L": (35, 0, 0), "CTL_BLeg1_R": (35, 0, 0)},
 "knees 30": {"CTL_FLeg2_L": (30, 0, 0), "CTL_BLeg2_R": (-30, 0, 0)},
 "tail 30": {"CTL_Tail1_M": (0, 0, 30), "CTL_Tail2_M": (0, 0, 30)}, "tail up 30": {"CTL_Tail1_M": (-30, 0, 0)},
 "gauge 90": {"CTL_Gauge_M": (0, 0, 90)}, "valve 45": {"CTL_Valve_M": (0, 45, 0)}, "exhaust 25": {"CTL_Exhaust_M": (25, 0, 0)},
 "goggles 20": {"CTL_Goggles_M": (-20, 0, 0)},
}
for n, d in POSES.items(): report(n, d)
setpose({})
