# Quet gian canh theo frame trong clip dang mo (Frolvy). In frame co max gian lon + cac frame mau chot.
import math
M = "Pet_Tiny_Chick"
md0 = api.mesh_data(M); idx = list(md0['vertices']); pos = {v: i for i, v in enumerate(idx)}
api.set_frame(0); api.set_frame(1); api.set_frame(0)
# bind-pose edge lengths: lay o pose rest = tinh tu weights khong co -> dung mesh_data (chua bien dang)
P0 = md0['positions']; P0 = [P0[i*3:i*3+3] for i in range(len(P0)//3)]
E = set(); c = 0
for s in md0['face_sizes']:
    cs = [pos.get(q, q) for q in md0['face_corners'][c:c+s]]; c += s
    for k in range(s): a, b = cs[k], cs[(k+1) % s]; E.add((min(a, b), max(a, b)))
E = [(a, b, math.dist(P0[a], P0[b])) for a, b in E if math.dist(P0[a], P0[b]) > 0.01]
lo, hi = api.frame_range()
res = []
for f in range(int(lo), int(hi)+1):
    api.set_frame(f)
    P = api.mesh_data(M, posed=True)['positions']; P = [P[i*3:i*3+3] for i in range(len(P)//3)]
    r = sorted(((math.dist(P[a], P[b]) / l, a) for a, b, l in E), reverse=True)
    res.append((f, r[0][0], sum(1 for x in r if x[0] > 1.5), sum(1 for x in r if x[0] > 2.0)))
worst = sorted(res, key=lambda t: -t[1])[:6]
print("frames", lo, hi, "max stretch per frame (top):", [(f, round(m, 2), n15, n20) for f, m, n15, n20 in worst])
print("mean max %.2f, mean >1.5x edges %.1f" % (sum(r[1] for r in res)/len(res), sum(r[2] for r in res)/len(res)))
api.set_frame(0)
