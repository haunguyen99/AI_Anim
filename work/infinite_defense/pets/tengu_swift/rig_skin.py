# Tengu Swift bind + weights (chay SAU rig_build.py). Bind khi moi control = 0.
for _c in api.ls("Curve"):
    if _c.startswith("CTL_") and _c != "CTL_Main": api.rotate(_c, 0, 0, 0); api.move(_c, 0, 0, 0)
api.set_frame(3); api.set_frame(0)
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_") and "Muzzle" not in j]
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t * t * (3 - 2 * t)
def bind(m):
    api.select([m])
    try: api.unbind_skin()
    except Exception: pass
    api.select([m]); api.bind_skin(DEF)
BODY, FAN = "Pet_tengu_swift", "Vu_khi_Pet_tengu_swift"
# ---- fan: handle -> Fan1, blade -> Fan2
md = api.mesh_data(FAN); idx = list(md['vertices']); P = md['positions']
bind(FAN)
rows = []
for i in range(len(idx)):
    y = P[i*3+1]; w2 = sm(ramp(y - 0.345, 0.03, 0.12)); rows.append([("DEF_Fan1_R", 1 - w2), ("DEF_Fan2_R", w2)])
rows = [[(j, v) for j, v in r if v > 0.005] for r in rows]
api.select([FAN]); api.set_skin_weights(idx, rows); print("fan", len(idx))
# ---- body
md = api.mesh_data(BODY); idx = list(md['vertices']); P = md['positions']; P = [P[i*3:i*3+3] for i in range(len(idx))]
par = list(range(len(idx)))
def f(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
pos = {v: i for i, v in enumerate(idx)}; c = 0
for s in md['face_sizes']:
    cs = md['face_corners'][c:c+s]; c += s
    for q in cs[1:]: par[f(pos.get(q, q))] = f(pos.get(cs[0], cs[0]))
comp = {}
for i in range(len(idx)): comp.setdefault(f(i), []).append(i)
KIND = {}
for vs in comp.values():
    ys = [P[i][1] for i in vs]; xs = [abs(P[i][0]) for i in vs]; y0, y1, x0 = min(ys), max(ys), min(xs)
    k = "head" if (y0 > 0.30 and y1 > 0.5) else "arm" if (y0 > 0.28 and y1 < 0.39 and x0 > 0.15) else "leg" if y1 <= 0.19 else "torso"
    for i in vs: KIND[i] = k
from collections import Counter
print(Counter(KIND.values()))
def row(i):
    x, y, z = P[i]; ax = abs(x); s = "L" if x > 0 else "R"; k = KIND[i]; b = {}
    if k == "head":
        tf = sm(ramp(ax, 0.17, 0.24)) * sm(ramp(-z, 0.05, 0.12)) * sm(ramp(y, 0.42, 0.50))
        hf = sm(ramp(-z, 0.10, 0.18)) * sm(ramp(y, 0.62, 0.70)) * (1 - tf)
        t2 = sm(ramp(ax, 0.20, 0.27)); h2 = sm(ramp(-z, 0.20, 0.30))
        b = {"DEF_Head_M": 1 - tf - hf, "DEF_Tuft1_" + s: tf * (1 - t2), "DEF_Tuft2_" + s: tf * t2, "DEF_Hair1_M": hf * (1 - h2), "DEF_Hair2_M": hf * h2}
    elif k == "arm":
        sp = 1 - sm(ramp(ax, 0.16, 0.21)); h = sm(ramp(ax, 0.23, 0.30))
        b = {"DEF_Spine1_M": sp, "DEF_Arm_" + s: (1 - sp) * (1 - h), "DEF_Hand_" + s: (1 - sp) * h}
    elif k == "leg":
        ff = sm(ramp(0.14 - y, 0.0, 0.07)); b = {"DEF_Leg_" + s: 1 - ff, "DEF_Foot_" + s: ff}
    else:
        rt = 1 - sm(ramp(y, 0.17, 0.30)); b = {"DEF_Root_M": rt, "DEF_Spine1_M": 1 - rt}
    return [(j, v) for j, v in b.items() if v > 0.01]
bind(BODY)
rows = []
for i in range(len(idx)):
    r = sorted(row(i), key=lambda t: -t[1])[:4]; t = sum(v for _, v in r); rows.append([(j, v / t) for j, v in r])
api.select([BODY]); api.set_skin_weights(idx, rows); print("body", len(idx))
