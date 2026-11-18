# v2 (mesh moi 2026-11-18): canh nho hon, mat na canh theo ax (khong cat theo y). Bind + weight theo vung. Mesh Pet_Tiny_Chick: than + vo trung + canh + chan + mo.
M = "Pet_Tiny_Chick"
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_")]
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t*t*(3-2*t)
md = api.mesh_data(M); P = md['positions']; P = [P[i*3:i*3+3] for i in range(len(P)//3)]
idx = list(md['vertices'])
# beak = linked component with small x extent in front
par = list(range(len(idx)))
def f(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
pos = {v: i for i, v in enumerate(idx)}
c = 0
for s in md['face_sizes']:
    cs = md['face_corners'][c:c+s]; c += s
    for q in cs[1:]: par[f(pos.get(q, q))] = f(pos.get(cs[0], cs[0]))
comp = {}
for i in range(len(idx)): comp.setdefault(f(i), []).append(i)
beak = set()
for vs in comp.values():
    if len(vs) < 200 and min(P[i][2] for i in vs) > 0.25: beak |= set(vs)
print("beak verts", len(beak), "of", len(idx))
api.select([M])
try: api.unbind_skin()
except Exception: pass
api.select([]); api.reset_transforms(all_controls=True); api.set_frame(3); api.set_frame(0)
api.select([M]); api.bind_skin(DEF)
def row(i):
    x, y, z = P[i]; s = "L" if x > 0 else "R"; ax = abs(x)
    if i in beak: return [("DEF_Beak_M", 1.0)]
    rootw = 1 - sm(ramp(y, 0.30, 0.46)); headw = sm(ramp(y, 0.48, 0.64)); spw = 1 - rootw - headw
    base = {"DEF_Root_M": rootw, "DEF_Spine1_M": spw, "DEF_Head_M": headw}
    def over(wt, jn):
        for k in base: base[k] *= (1 - wt)
        base[jn] = base.get(jn, 0) + wt
    cap = sm(ramp(y, 0.58, 0.68))
    if cap > 0: over(cap, "DEF_Cap_M")
    shell = 1 - sm(ramp(y, 0.30, 0.38))
    foot = sm(ramp(ax, 0.05, 0.12)) * (1 - sm(ramp(y, 0.08, 0.15)))   # ban chan: pha mem voi vo duoi (v2)
    if shell > 0: over(shell, "DEF_Shell_M")
    if foot > 0:
        over(foot, "DEF_Ankle_" + s)
        a_ = base["DEF_Ankle_" + s]; toe = sm(ramp(z, 0.04, 0.14))
        base["DEF_Ankle_" + s] = a_ * (1 - toe); base["DEF_Toes_" + s] = a_ * toe
    w = sm(ramp(ax, 0.355, 0.41)) * ramp(y, 0.24, 0.30) * (1 - ramp(y, 0.50, 0.54))
    if w > 0:
        tip = sm(ramp(ax, 0.43, 0.49)); over(w, "DEF_WingA_" + s)
        moved = base["DEF_WingA_" + s] * tip; base["DEF_WingA_" + s] -= moved; base["DEF_WingB_" + s] = moved
    r = [(j, v) for j, v in base.items() if v > 0.01]
    r.sort(key=lambda t: -t[1]); r = r[:4]; t = sum(v for _, v in r); return [(j, v/t) for j, v in r]
api.select([M]); api.set_skin_weights(idx, [row(i) for i in range(len(idx))])
print("skinned", len(idx))
