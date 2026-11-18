# Do gian canh sau skin cho vai pose thu (chay trong Frolvy). In pose -> max gian, so canh >1.5x, vi tri dinh xau nhat.
import math
M = "Pet_Tiny_Chick"
md0 = api.mesh_data(M); P0 = md0['positions']; P0 = [P0[i*3:i*3+3] for i in range(len(P0)//3)]
idx = list(md0['vertices']); pos = {v: i for i, v in enumerate(idx)}
E = set(); c = 0
for s in md0['face_sizes']:
    cs = [pos.get(q, q) for q in md0['face_corners'][c:c+s]]; c += s
    for k in range(s): a, b = cs[k], cs[(k+1) % s]; E.add((min(a, b), max(a, b)))
def d(P, a, b): return math.dist(P[a], P[b])
POSES = {
 "shell5": [("CTL_Shell_M", 0, 5, 5)], "shell10": [("CTL_Shell_M", 0, 10, 10)],
 "cap25": [("CTL_Cap_M", 25, 0, 0)], "cap-15": [("CTL_Cap_M", -15, 0, 15)],
 "wingL50": [("CTL_WingA_L", 0, 0, 50), ("CTL_WingB_L", 0, 0, 30)], "wingR50": [("CTL_WingA_R", 0, 0, -50), ("CTL_WingB_R", 0, 0, -30)],
 "wingUp": [("CTL_WingA_L", 0, 0, -40), ("CTL_WingA_R", 0, 0, 40)],
 "nod40": [("CTL_Root_M", 40, 0, 0), ("CTL_Beak_M", 15, 0, 0)], "head20": [("CTL_Head_M", 20, 25, 0)],
 "beak20": [("CTL_Beak_M", 25, 0, 0)],
 "ankleL40": [("CTL_Ankle_L", 40, 0, 0), ("CTL_Toes_L", 30, 0, 0)], "ankleR-30": [("CTL_Ankle_R", -30, 0, 0)],
 "yaw": [("CTL_Root_M", 0, 8, 4), ("CTL_Spine1_M", 0, -5, -2.5)],
}
for n, spec in POSES.items():
    api.select([]); api.reset_transforms(all_controls=True)
    for ctl, x, y, z in spec: api.rotate(ctl, x, y, z)
    api.set_frame(1); api.set_frame(0)
    P = api.mesh_data(M, posed=True)['positions']; P = [P[i*3:i*3+3] for i in range(len(P)//3)]
    r = sorted(((d(P, a, b) / max(d(P0, a, b), 1e-6), a, b) for a, b in E), reverse=True)
    bad = [x for x in r if x[0] > 1.5 and d(P0, x[1], x[2]) > 0.01]
    w = r[0]; pa = P0[w[1]]
    print("%-9s max %.2f  >1.5x: %3d  worst at (%.2f,%.2f,%.2f)" % (n, w[0], len(bad), pa[0], pa[1], pa[2]))
api.select([]); api.reset_transforms(all_controls=True); api.set_frame(1); api.set_frame(0)
