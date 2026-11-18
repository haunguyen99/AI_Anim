# Bind + weight Wind Chameleon (chay sau build_rig.py). Mesh: chameleon (than) + Chameleon_tonge (luoi)
import math
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_")]
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t*t*(3-2*t)
# joint world positions (from J table in build_rig)
src = open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\wind_chameleon\rig\build_rig.py").read()
import re
TAIL = [(0, .21, -.30), (0, .27, -.43), (0, .41, -.46), (0, .55, -.41), (0, .66, -.33), (0, .70, -.17), (0, .62, -.04), (0, .51, -.06), (0, .48, -.16), (0, .56, -.21)]
SPINE = [("DEF_Root_M", (0, .20, -.12)), ("DEF_Spine1_M", (0, .26, -.02)), ("DEF_Chest_M", (0, .33, .08)), ("DEF_Neck_M", (0, .40, .15)), ("DEF_Head_M", (0, .45, .22))]
TCH = [("DEF_Root_M", (0, .20, -.12))] + [("DEF_Tail%d_M" % (i+1), p) for i, p in enumerate(TAIL)]
def dist(a, b): return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))
def proj(p, chain):
    """nearest point on polyline chain [(name,pos)] -> (distance, hat weights {name:w})"""
    best = None; acc = 0.0
    for i in range(len(chain)-1):
        a = chain[i][1]; b = chain[i+1][1]; ab = [b[k]-a[k] for k in range(3)]; L2 = sum(c*c for c in ab)
        t = max(0.0, min(1.0, sum((p[k]-a[k])*ab[k] for k in range(3)) / L2)); q = [a[k]+ab[k]*t for k in range(3)]
        d = dist(p, q)
        if best is None or d < best[0]: best = (d, i, t)
    d, i, t = best; t = sm(t)
    return d, {chain[i][0]: 1-t, chain[i+1][0]: t}
def getmesh(M):
    md = api.mesh_data(M); P = md['positions']; return list(md['vertices']), [P[i*3:i*3+3] for i in range(len(P)//3)]
def norm(w):
    r = sorted([(j, v) for j, v in w.items() if v > 0.01], key=lambda t: -t[1])[:4]; t = sum(v for _, v in r); return [(j, v/t) for j, v in r]
SMOOTH = 3
# arc length of the tail joints along the chain, and hat weights on it
SJ = [0.0]
for i in range(1, len(TCH)): SJ.append(SJ[-1] + dist(TCH[i-1][1], TCH[i][1]))
def hat(s):
    if s <= SJ[1]: return {TCH[1][0]: 1.0} if s < SJ[1] else {TCH[1][0]: 1.0}
    if s >= SJ[-1]: return {TCH[-1][0]: 1.0}
    for i in range(1, len(SJ) - 1):
        if SJ[i] <= s <= SJ[i+1]:
            u = sm((s - SJ[i]) / (SJ[i+1] - SJ[i])); return {TCH[i][0]: 1 - u, TCH[i+1][0]: u}
def body_row(p, tail_flag, arcs=None):
    x, y, z = p; ax = abs(x); s = "L" if x > 0 else "R"
    dB, wB = proj(p, SPINE); dT, wT = proj(p, TCH[1:] if False else TCH)
    tailish = tail_flag
    if tailish and arcs is not None:
        base = dict(hat(arcs))
    elif tailish:
        base = dict(wT if (y >= 0.45 or z <= -0.26) else proj(p, TCH[:3])[1])   # back near the body: only the first tail joints
    else: base = dict(wB)
    def over(wt, jn):
        if wt <= 0: return
        for k in base: base[k] *= (1 - wt)
        base[jn] = base.get(jn, 0) + wt
    if not tailish:
        # crest
        c = sm(ramp(y, 0.54, 0.66)) * ramp(0.30, z, 0.22) * ramp(z, -0.02, 0.06)
        over(c * 0.85, "DEF_Crest_M")
        # mouth hole: rim + cavity around (0, .335) squeezed by DEF_Mouth_M (scale y)
        em = math.sqrt((x / 0.12) ** 2 + ((y - 0.335) / 0.075) ** 2)
        over((1 - sm(ramp(em, 0.9, 1.4))) * sm(ramp(z, 0.30, 0.38)), "DEF_Mouth_M")
        # jaw (under mouth line, front)
        jw = sm(ramp(0.335 - y, 0.0, 0.07)) * sm(ramp(z, 0.20, 0.31)) * ramp(0.19, ax, 0.12)
        over(jw, "DEF_Jaw_M")
        # cheek
        dc = dist(p, (0.13 if x > 0 else -0.13, 0.32, 0.34)); over(1 - sm(ramp(dc, 0.04, 0.13)), "DEF_Cheek_" + s)
        # eye
        de = dist(p, (0.24 if x > 0 else -0.24, 0.335, 0.30)); over(1 - sm(ramp(de, 0.085, 0.115)), "DEF_Eye_" + s)
    # legs
    lw = sm(ramp(0.23 - y, 0.0, 0.08)) * sm(ramp(ax, 0.10, 0.15))
    if lw > 0 and not (tailish and z < -0.3):
        fr = sm(ramp(z, -0.01, 0.04)); pre = "F" if fr > 0.5 else "R"
        hip, ank, toe = "DEF_%sHip_%s" % (pre, s), "DEF_%sAnkle_%s" % (pre, s), "DEF_%sToes_%s" % (pre, s)
        ay = 0.07; tz = 0.24 if pre == "F" else -0.10; az = 0.15 if pre == "F" else -0.17
        wa = sm(ramp(0.17 - y, 0.0, 0.08)); wt = sm(ramp(abs(z - az), 0.02, 0.08)) * (1 if ((z - az) * (tz - az)) > 0 else 0) * ramp(0.10, y, 0.05)
        over(lw, hip)
        if wa > 0: 
            moved = base[hip] * wa; base[hip] -= moved; base[ank] = moved
            if wt > 0: m2 = base[ank] * wt; base[ank] -= m2; base[toe] = m2
    return norm(base)
DRY = bool(globals().get("DRY_RUN", False))   # DRY_RUN=True before exec: only compute rows (no bind, no weights written)
for M in ("chameleon", "Chameleon_tonge"):
    if DRY: break
    api.select([M])
    try: api.unbind_skin()
    except Exception: pass
    api.select([M]); api.bind_skin(DEF)
idx, P = getmesh("chameleon")
md = api.mesh_data("chameleon"); pos = {v: i for i, v in enumerate(idx)}; nb = [set() for _ in idx]; c = 0
for s in md['face_sizes']:
    cs = [pos[q] for q in md['face_corners'][c:c+s]]; c += s
    for a in range(s):
        nb[cs[a]].add(cs[(a+1) % s]); nb[cs[(a+1) % s]].add(cs[a])
# tail / body label: clear seeds by position, the ambiguous rest is flooded along the mesh edges (dorsal spikes touch the coil in space but not in the mesh)
lab = [None] * len(P)
for i, p in enumerate(P):
    x, y, z = p; dB = proj(p, SPINE)[0]; dT = proj(p, TCH)[0]
    if (z < -0.12 and dT < dB) or (y > 0.55 and z < -0.02 and dT < dB): lab[i] = True
    elif z > -0.02 or dB < 0.12 or (z < -0.12 and dT >= dB): lab[i] = False
front = [i for i in range(len(P)) if lab[i] is not None]
while front:
    nxt = []
    for i in front:
        for n in nb[i]:
            if lab[n] is None: lab[n] = lab[i]; nxt.append(n)
    front = nxt
lab = [bool(v) for v in lab]
# geodesic distance along the tail surface from the tube cross-section near Tail1 -> arc length (fixes inner wall picking coil joints)
import heapq
arc = [None] * len(P); hp = []
for i, p in enumerate(P):
    if lab[i] and -0.34 <= p[2] <= -0.26 and p[1] < 0.32: arc[i] = SJ[1]; hp.append((SJ[1], i))
heapq.heapify(hp)
while hp:
    d, i = heapq.heappop(hp)
    if d > arc[i] + 1e-9: continue
    for n in nb[i]:
        if not lab[n] or P[n][2] > -0.26 and arc[n] is None and P[n][1] < 0.45 and False: continue
        nd = d + dist(P[i], P[n])
        if arc[n] is None or nd < arc[n] - 1e-9: arc[n] = nd; heapq.heappush(hp, (nd, n))
def sproj(p):
    best = None
    for i in range(len(TCH) - 1):
        a = TCH[i][1]; b = TCH[i+1][1]; ab = [b[k] - a[k] for k in range(3)]; L2 = sum(c * c for c in ab)
        u = max(0.0, min(1.0, sum((p[k] - a[k]) * ab[k] for k in range(3)) / L2)); q = [a[k] + ab[k] * u for k in range(3)]
        d = dist(p, q)
        if best is None or d < best[0]: best = (d, SJ[i] + u * (SJ[i+1] - SJ[i]))
    return best[1]
for i, p in enumerate(P):                       # root zone (underside / rump): the straight projection is reliable there, keep the smaller of the two
    if arc[i] is not None and lab[i] and p[2] > -0.40 and p[1] < 0.35: arc[i] = min(arc[i], sproj(p))
print("tail verts", sum(lab), "with arc", sum(1 for a in arc if a is not None))
rows = [dict(body_row(p, lab[i], arc[i] if (lab[i] and (P[i][2] < -0.26 or P[i][1] >= 0.45)) else None)) for i, p in enumerate(P)]
# smooth weights over the mesh (fixes neighbouring tail windings picking different joints)
for _ in range(SMOOTH):
    new = []
    for i, r in enumerate(rows):
        if r.get("DEF_Eye_L", 0) > 0.99 or r.get("DEF_Eye_R", 0) > 0.99 or not nb[i]: new.append(r); continue
        acc = {}
        for j, v in r.items(): acc[j] = acc.get(j, 0) + 0.5 * v
        for n in nb[i]:
            for j, v in rows[n].items(): acc[j] = acc.get(j, 0) + 0.5 * v / len(nb[i])
        new.append(dict(norm(acc)))
    rows = new
# smoothing leaks tail weights into the hip/rump and body weights into the tube: clean both sides
import re as _re
def _tn(j):
    m = _re.match(r"DEF_Tail(\d+)_M", j); return int(m.group(1)) if m else 0
for i, p in enumerate(P):
    r = rows[i]; z = p[2]; y = p[1]
    if z > -0.26 and y < 0.45:                       # hip / rump: only Root, Spine, legs and Tail1 (no Tail2..10)
        r = {j: v for j, v in r.items() if _tn(j) < 2} or r
    if z < -0.34:                                    # tube: no Root / Spine / Chest
        r = {j: v for j, v in r.items() if j not in ("DEF_Root_M", "DEF_Spine1_M", "DEF_Chest_M")} or r
    rows[i] = dict(norm(r))
if not DRY: api.select(["chameleon"]); api.set_skin_weights(idx, [list(r.items()) for r in rows]); print("body", len(idx))
idx, P = getmesh("Chameleon_tonge")
TJ = [("DEF_Tongue1_M", .24), ("DEF_Tongue2_M", .38), ("DEF_Tongue3_M", .50), ("DEF_Tongue4_M", .59)]
def trow(p):
    z = p[2]
    if z <= TJ[0][1]: return [(TJ[0][0], 1.0)]
    if z >= TJ[-1][1]: return [(TJ[-1][0], 1.0)]
    for i in range(3):
        if TJ[i][1] <= z <= TJ[i+1][1]:
            t = sm((z - TJ[i][1]) / (TJ[i+1][1] - TJ[i][1])); return [(TJ[i][0], 1-t), (TJ[i+1][0], t)]
if not DRY: api.select(["Chameleon_tonge"]); api.set_skin_weights(idx, [trow(p) for p in P]); print("tongue", len(idx))
