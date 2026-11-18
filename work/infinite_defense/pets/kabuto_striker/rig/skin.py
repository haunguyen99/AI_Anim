import math
M = "Pet_Kabuto_Striker"
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_") and "Muzzle" not in j and not j.endswith(("End_M","End_L","End_R"))]
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t*t*(3-2*t)
def dist(a, b): return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))
md = api.mesh_data(M); P = md['positions']; idx = list(md['vertices']); P = [P[i*3:i*3+3] for i in range(len(idx))]
pos = {v: i for i, v in enumerate(idx)}; nb = [set() for _ in idx]; c = 0
for s in md['face_sizes']:
    cs = [pos[q] for q in md['face_corners'][c:c+s]]; c += s
    for a in range(s):
        nb[cs[a]].add(cs[(a+1) % s]); nb[cs[(a+1) % s]].add(cs[a])
TR = [("DEF_Root_M", .24), ("DEF_Spine1_M", .33), ("DEF_Chest_M", .42), ("DEF_Neck_M", .56), ("DEF_Head_M", .70)]
def trunk(y):
    if y <= TR[0][1]: return {TR[0][0]: 1.0}
    if y >= TR[-1][1]: return {TR[-1][0]: 1.0}
    for i in range(len(TR)-1):
        if TR[i][1] <= y <= TR[i+1][1]:
            t = sm((y - TR[i][1]) / (TR[i+1][1] - TR[i][1])); return {TR[i][0]: 1-t, TR[i+1][0]: t}
HORN = [(.17, .74), (.36, .84), (.30, .97)]    # |x|, y of Horn1, Horn2, HornEnd (z ~ -.02)
def horn_w(p, s):
    x, y, z = p; q = (abs(x), y)
    best = None
    for i in range(2):
        a = HORN[i]; b = HORN[i+1]; ab = (b[0]-a[0], b[1]-a[1]); L2 = ab[0]**2 + ab[1]**2
        t = max(0.0, min(1.0, ((q[0]-a[0])*ab[0] + (q[1]-a[1])*ab[1]) / L2)); d = math.hypot(q[0]-a[0]-ab[0]*t, q[1]-a[1]-ab[1]*t)
        if best is None or d < best[0]: best = (d, i, t)
    d, i, t = best; t = sm(t)
    j = ["DEF_Horn1_" + s, "DEF_Horn2_" + s]
    return {j[0]: 1-t, j[1]: t} if i == 0 else {j[1]: 1.0}
FEET = [("DEF_FFoot_L", .27, .02), ("DEF_FFoot_R", -.27, .02), ("DEF_RFoot_L", .19, -.17), ("DEF_RFoot_R", -.19, -.17)]
def row(p):
    x, y, z = p; ax = abs(x); s = "L" if x > 0 else "R"
    base = trunk(y)
    def over(wt, new):
        if wt <= 0: return
        for k in base: base[k] *= (1 - wt)
        for k, v in new.items(): base[k] = base.get(k, 0) + wt * v
    # sode (shoulder plates)
    over(sm(ramp(ax, .31, .39)) * sm(ramp(y, .28, .34)) * sm(ramp(.56, y, .50)), {"DEF_Sode_" + s: 1.0})
    # horns (above the helmet crown)
    over(sm(ramp(y, .73, .78)) * sm(ramp(ax, .08, .16)), horn_w(p, s))
    # skirt plates by direction around the body centre
    th = math.atan2(x, z + .10); wF = max(0, math.cos(th))**2 if z + .10 > 0 else 0.0
    wB = max(0, -math.cos(th))**2 if z + .10 < 0 else 0.0; wS = abs(math.sin(th))**2
    tot = wF + wB + wS
    sk = {"DEF_SkirtF_M": wF/tot, "DEF_SkirtB_M": wB/tot, "DEF_SkirtS_" + s: wS/tot}
    over(sm(ramp(.30 - y, 0.0, .12)) * 0.95, sk)
    # feet
    for jn, fx, fz in FEET:
        d = math.hypot(x - fx, z - fz); over((1 - sm(ramp(d, .07, .13))) * sm(ramp(.16 - y, 0.0, .08)), {jn: 1.0})
    r = sorted([(j, v) for j, v in base.items() if v > 0.01], key=lambda t: -t[1])[:4]; t = sum(v for _, v in r)
    return dict((j, v/t) for j, v in r)
rows = [row(p) for p in P]
for _ in range(2):
    new = []
    for i, r in enumerate(rows):
        if not nb[i]: new.append(r); continue
        acc = {}
        for j, v in r.items(): acc[j] = acc.get(j, 0) + 0.6 * v
        for n in nb[i]:
            for j, v in rows[n].items(): acc[j] = acc.get(j, 0) + 0.4 * v / len(nb[i])
        rr = sorted(acc.items(), key=lambda t: -t[1])[:4]; t = sum(v for _, v in rr); new.append(dict((j, v/t) for j, v in rr))
    rows = new
api.select([M])
try: api.unbind_skin()
except Exception: pass
api.select([M]); api.bind_skin(DEF)
api.select([M]); api.set_skin_weights(idx, [list(r.items()) for r in rows]); api.select([])
api.set_frame(3); api.set_frame(0)
print("skinned", len(idx), "verts", len(DEF), "joints")
