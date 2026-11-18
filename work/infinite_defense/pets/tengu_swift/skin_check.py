import math
OBJS = ["Pet_tengu_swift", "Vu_khi_Pet_tengu_swift"]
CT = [c for c in api.ls("Curve") if c.startswith("CTL_") and c != "CTL_Main"]
def setpose(d):
    for c in CT: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    for c, v in d.items(): api.rotate(c, v[0], v[1], v[2])
    api.set_frame(3); api.set_frame(0)
setpose({}); DATA = {}
for o in OBJS:
    md = api.mesh_data(o); idx = list(md['vertices']); P = md['positions']; P0 = [P[i*3:i*3+3] for i in range(len(idx))]
    pos = {v: i for i, v in enumerate(idx)}; E = set(); c = 0
    for s in md['face_sizes']:
        cs = [pos.get(q, q) for q in md['face_corners'][c:c+s]]; c += s
        for k in range(s): E.add(tuple(sorted((cs[k], cs[(k+1) % s]))))
    DATA[o] = (idx, P0, sorted(E))
def report(name, d):
    setpose(d); worst = []; mv = 0
    for o in OBJS:
        idx, P0, E = DATA[o]; Pf = api.mesh_data(o, True)['positions']; Q = [Pf[i*3:i*3+3] for i in range(len(idx))]
        for i in range(len(idx)): mv = max(mv, math.dist(Q[i], P0[i]))
        for a, b in E:
            l0 = math.dist(P0[a], P0[b])
            if l0 < 1e-4: continue
            l1 = math.dist(Q[a], Q[b]); worst.append((l1 - l0, l1 / l0, [round(x, 2) for x in P0[a]]))
    worst.sort(key=lambda t: -t[0])
    print("%-14s move %.3f | %s" % (name, mv, "; ".join("+%.3f x%.1f @%s" % w for w in worst[:3])))
POSES = {
 "head yaw 40": {"CTL_Head_M": (0, 40, 0)}, "head nod 30": {"CTL_Head_M": (30, 0, 0)},
 "spine bend 25": {"CTL_Spine1_M": (25, 0, 0), "CTL_Root_M": (0, 0, 15)},
 "arm L up 60": {"CTL_Arm_L": (0, 0, 60)}, "arm L fwd 60": {"CTL_Arm_L": (0, -60, 0)}, "hand R 50": {"CTL_Hand_R": (0, 0, -50)},
 "arm R down 50": {"CTL_Arm_R": (0, 0, 50)},
 "leg fwd 40": {"CTL_Leg_L": (-40, 0, 0), "CTL_Leg_R": (40, 0, 0)}, "foot 35": {"CTL_Foot_L": (35, 0, 0)},
 "tuft 35": {"CTL_Tuft1_L": (0, 35, 0), "CTL_Tuft2_L": (0, 30, 0), "CTL_Hair1_M": (30, 0, 0), "CTL_Hair2_M": (30, 0, 0)},
 "fan 40": {"CTL_Fan1_R": (0, 0, 40), "CTL_Fan2_R": (20, 0, 0)},
}
for n, d in POSES.items(): report(n, d)
setpose({})
