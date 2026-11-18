# Quet moi frame: do gian canh (edge) lon nhat + dich chuyen dinh so voi bind, per nhom. Chay trong Frolvy (scene da co anim).
import math
o = "Pet_Night_Bat"
for c in api.ls("Curve"): pass
f0, f1 = api.frame_range()
api.set_frame(1); api.set_frame(0)
md = api.mesh_data(o); idx = list(md['vertices']); P0 = md['positions']
pos = {v: i for i, v in enumerate(idx)}; E = set(); c = 0
for s in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c + s]]; c += s
    for k in range(s): E.add(tuple(sorted((cs[k], cs[(k + 1) % s]))))
E = sorted(E)
# bind lengths: control-zero pose
CT = [x for x in api.ls("Curve") if x.startswith("CTL_") and x != "CTL_Main"]
saved = {}
worst = []
def lengths(P):
    return [math.dist(P[a*3:a*3+3], P[b*3:b*3+3]) for a, b in E]
# bind = frame-independent: use mesh_data(False)
L0 = lengths(P0)
for f in range(f0, f1 + 1):
    api.set_frame(f); Pf = api.mesh_data(o, True)['positions']; L = lengths(Pf)
    mx = max(((L[i] - L0[i], L[i] / L0[i], E[i]) for i in range(len(E)) if L0[i] > 1e-4), key=lambda t: t[0])
    mn = min(((L[i] / L0[i], E[i]) for i in range(len(E)) if L0[i] > 1e-4), key=lambda t: t[0])
    worst.append((f, round(mx[0], 3), round(mx[1], 2), round(mn[0], 2)))
api.set_frame(0)
w = sorted(worst, key=lambda t: -t[1])[:6]
print("frames", f0, f1, "worst stretch (frame, +len, ratio, minratio):", w)
print("max ratio overall", max(t[2] for t in worst), "min ratio", min(t[3] for t in worst))
