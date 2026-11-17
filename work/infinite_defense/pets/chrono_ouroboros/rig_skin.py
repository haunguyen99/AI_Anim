# Chrono Ouroboros bind + weights. Chay SAU rig_build.py. Bind khi moi control = 0.
import math
for _c in api.ls("Curve"):
    if _c.startswith("CTL_") and _c != "CTL_Main": api.rotate(_c, 0, 0, 0); api.move(_c, 0, 0, 0)
api.set_frame(3); api.set_frame(0)
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_") and "Muzzle" not in j]
BODY = "Pet_Chrono_Ouroboros"
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t * t * (3 - 2 * t)
md = api.mesh_data(BODY); idx = list(md['vertices']); P = md['positions']; P = [P[i * 3:i * 3 + 3] for i in range(len(idx))]
# small components (eyes) -> Head 100%
pos = {v: i for i, v in enumerate(idx)}; par = list(range(len(idx)))
def fd(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
c = 0
for sz in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c + sz]]; c += sz
    for k in range(1, sz): par[fd(cs[k])] = fd(cs[0])
from collections import Counter
cnt = Counter(fd(i) for i in range(len(idx))); big = cnt.most_common(1)[0][0]
EYE = [fd(i) != big for i in range(len(idx))]
api.select([BODY])
try: api.unbind_skin()
except Exception: pass
api.select([BODY]); api.bind_skin(DEF)
# trunk chain by z (tent functions)
CH = [("DEF_Tail5_M", (0, 0.60, -1.64)), ("DEF_Tail4_M", (0, 0.54, -1.48)), ("DEF_Tail3_M", (0, 0.46, -1.32)), ("DEF_Tail2_M", (0, 0.40, -1.15)), ("DEF_Tail1_M", (0, 0.36, -0.95)),
      ("DEF_Root_M", (0, 0.36, -0.55)), ("DEF_Spine1_M", (0, 0.36, -0.05)), ("DEF_Spine2_M", (0, 0.37, 0.48)), ("DEF_Neck1_M", (0, 0.36, 0.80)), ("DEF_Neck2_M", (0, 0.54, 0.87)), ("DEF_Head_M", (0, 0.75, 1.01))]
def trunk(p, ch=None):
    CH_ = ch or CH
    # project on the joint polyline (3D), tent weights along it
    best = None
    for k in range(len(CH_) - 1):
        (a, A), (b, B) = CH_[k], CH_[k + 1]
        AB = [B[i] - A[i] for i in range(3)]; L2 = sum(v * v for v in AB)
        t = max(0.0, min(1.0, sum((p[i] - A[i]) * AB[i] for i in range(3)) / L2))
        d = math.dist(p, [A[i] + t * AB[i] for i in range(3)])
        if best is None or d < best[0] - 1e-9: best = (d, k, t)
    _, k, t = best; t = sm(t)
    return {CH_[k][0]: 1 - t, CH_[k + 1][0]: t}
def legrow(side, front, y):
    p = "Fore" if front else "Hind"
    l1 = sm(ramp(y, 0.15, 0.24)); ft = 1 - sm(ramp(y, 0.04, 0.10)); l2 = max(0.0, 1 - l1 - ft)
    if l1 + ft > 1: s = l1 + ft; l1, ft = l1 / s, ft / s
    return {"DEF_%sLeg1_%s" % (p, side): l1, "DEF_%sLeg2_%s" % (p, side): l2, "DEF_%sFoot_%s" % (p, side): ft}
def row(i):
    x, y, z = P[i]
    if EYE[i]: return {"DEF_Head_M": 1.0}
    side = "L" if x > 0 else "R"
    w = trunk(P[i])
    mm = sm(ramp(y, 0.50, 0.62)) * sm(ramp(z, 0.45, 0.60)) * (1 - sm(ramp(z, 0.98, 1.08)))   # mane / crest spikes: follow the neck, not the back
    if mm > 0:
        wn = trunk(P[i], CH[-3:])
        w = {k: v * (1 - mm) for k, v in w.items()}
        for k, v in wn.items(): w[k] = w.get(k, 0) + mm * v
    # legs
    for front, zc in ((True, 0.78), (False, -0.75)):
        gz = 1 - sm(ramp(abs(z - zc), 0.20, 0.30))
        lw = sm(ramp(0.32 - y, 0, 0.12)) * gz * sm(ramp(abs(x), 0.0, 0.03))
        if lw > 0:
            w = {k: v * (1 - lw) for k, v in w.items()}
            for k, v in legrow(side, front, y).items(): w[k] = w.get(k, 0) + lw * v
    # jaw: lower part of the mouth
    jw = sm(ramp(0.68 - y, 0, 0.07)) * ramp(z, 1.06, 1.20)
    if jw > 0 and "DEF_Head_M" in w:
        h = w.pop("DEF_Head_M"); w["DEF_Head_M"] = h * (1 - jw); w["DEF_Jaw_M"] = h * jw
    return w
def fin(w):
    r = [(j, v) for j, v in w.items() if v > 0.01]; r.sort(key=lambda t: -t[1]); r = r[:4]; t = sum(v for _, v in r); return [(j, v / t) for j, v in r]
api.select([BODY]); api.set_skin_weights(idx, [fin(row(i)) for i in range(len(idx))])
print("skinned", len(idx), "eye verts", sum(EYE))
