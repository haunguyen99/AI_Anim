import math
RING = "/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/v3/ring.py"
rn = {}; exec(open(RING).read(), rn)
OB = "Pet_chrono_ouroboros"
CT = [c for c in api.ls("Curve") if c.startswith("CTL_") and c != "CTL_Main"]
W = {r['name']: r['world'] for r in api.joint_info()}
def setpose(P):
    for c in CT: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    for c, v in P.items(): api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
    api.set_frame(3); api.set_frame(0)
setpose({})
md = api.mesh_data(OB); idx = list(md['vertices']); P0 = md['positions']; P0 = [P0[i*3:i*3+3] for i in range(len(idx))]
pos = {v: i for i, v in enumerate(idx)}; E = set(); c = 0
for s in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c+s]]; c += s
    for k in range(s): E.add(tuple(sorted((cs[k], cs[(k+1) % s]))))
E = sorted(E)
def report(name, P):
    setpose(P); Pf = api.mesh_data(OB, True)['positions']; Q = [Pf[i*3:i*3+3] for i in range(len(idx))]
    rs = []
    for a, b in E:
        l0 = math.dist(P0[a], P0[b])
        if l0 < 1e-3: continue
        rs.append((math.dist(Q[a], Q[b]) / l0, math.dist(Q[a], Q[b]) - l0, [round(x, 2) for x in P0[a]]))
    mx = max(rs, key=lambda t: t[1]); mn = min(rs, key=lambda t: t[0])
    print("%-22s stretch +%.3f (x%.2f)@%s | squash x%.2f@%s" % (name, mx[1], mx[0], mx[2], mn[0], mn[2]))
report("ring full", rn['ring_pose'](W))
report("ring 50%", rn['ring_pose'](W, scale=0.5))
def ex(**k): return {"CTL_%s_M" % n: (v[0], v[1], v[2], 0, 0, 0) for n, v in k.items()}
report("spine S pitch 12", ex(Spine2=(12,0,0), Spine4=(-12,0,0), Spine6=(12,0,0), Spine8=(-12,0,0)))
report("spine yaw 10", ex(Spine2=(0,10,0), Spine4=(0,-10,0), Spine6=(0,10,0), Spine8=(0,-10,0)))
report("tail wave 25", ex(Tail1=(-25,0,0), Tail3=(25,0,0), Tail5=(-25,0,0), Tail7=(25,0,0)))
report("neck up 25", ex(Neck1=(-25,0,0), Neck2=(-15,0,0), Head=(-20,0,0)))
report("jaw open 30", ex(Jaw=(30,0,0)))
report("hourglass spin 90", ex(Hourglass=(0,90,0)))
setpose({})
