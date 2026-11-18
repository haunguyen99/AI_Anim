# Night Bat bind + weights. Run AFTER rig_build.py (and rig_split_ears.py if the ears were detached into Pet_Night_Bat1 / 2).
# Bind must happen in the true bind pose: every control at 0 (a posed control at bind time = corrupt bind = wings stuck to face/ears).
import heapq, math
for _c in api.ls("Curve"):
    if _c.startswith("CTL_") and _c != "CTL_Main": api.rotate(_c, 0, 0, 0); api.move(_c, 0, 0, 0)
api.set_frame(3); api.set_frame(0)
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_") and "Muzzle" not in j]
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t * t * (3 - 2 * t)
OBJS = [o for o in api.ls("Object") if o.startswith("Pet_Night_Bat")]
BODY = "Pet_Night_Bat"
EARS = [o for o in OBJS if o != BODY]          # detached ear shells (100% ear weights, no wing, no head)

def bind(m):
    api.select([m])
    try: api.unbind_skin()
    except Exception: pass
    api.select([m]); api.bind_skin(DEF)

def ear_row(x, y, z):
    # ear shell: pure ear weights, except the base next to the head fades into the Head weights (q = distance from the head ellipsoid) so no gap opens when the ear tilts
    s = "L" if x > 0 else "R"; f2 = sm(ramp(y, 0.54, 0.62))
    q = (((abs(x) / 0.19) ** 2) + (((y - 0.345) / 0.175) ** 2) + (((z - 0.15) / 0.18) ** 2)) ** 0.5
    hw = 1 - sm(ramp(q, 1.1, 1.55))
    r = {"DEF_Head_M": hw, "DEF_Ear1_" + s: (1 - hw) * (1 - f2), "DEF_Ear2_" + s: (1 - hw) * f2}
    return [(j, v) for j, v in r.items() if v > 0.005]

for e in EARS:
    md = api.mesh_data(e); P = md['positions']; idx = list(md['vertices'])
    bind(e); api.select([e]); api.set_skin_weights(idx, [ear_row(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]) for i in range(len(idx))])
    print("ear shell", e, len(idx))

md = api.mesh_data(BODY); idx = list(md['vertices']); P = md['positions']; P = [P[i * 3:i * 3 + 3] for i in range(len(idx))]
have_split = bool(EARS)
bind(BODY)
def row(i):
    # groups: WING (Wing1-4), EAR, HEAD (Head, Jaw), BODY (Root, Spine1). Never wing+head / wing+ear.
    x, y, z = P[i]; s = "L" if x > 0 else "R"; ax = abs(x)
    q = (((ax / 0.19) ** 2) + (((y - 0.345) / 0.175) ** 2) + (((z - 0.15) / 0.18) ** 2)) ** 0.5   # head ellipsoid: q<1 inside = head only
    outside = sm(ramp(q, 1.0, 1.2))
    d = y - (0.345 - 0.1 * (ax - 0.14))
    ew = 0.0 if have_split else sm(ramp(d, 0.0, 0.035)) * sm(ramp(ax, 0.06, 0.11)) * outside
    ww = sm(ramp(ax, 0.15, 0.20)) * (1 - sm(ramp(z, 0.07, 0.12))) * outside * ((1 - sm(ramp(y, 0.40, 0.44))) if have_split else 1.0)   # wing sheet: thin, behind the face; split mode: nothing above y=0.44 follows the wing (ear base ring + head side stay with the head)
    if ew >= ww and ew > 0.02: ww = 0.0
    elif ww > 0: ew = 0.0
    rest = 1 - ew - ww
    hw = sm(ramp(y, 0.165, 0.215))
    k = min(1.0, ww / 0.25)                                                        # in the wing zone the non-wing part is BODY, never head
    hw_eff = hw * (1 - k)
    sp = (1 - hw_eff) * sm(ramp(y, 0.04, 0.14)); rt = 1 - hw_eff - sp
    if ew > 0: hw_eff, sp, rt = 1.0, 0.0, 0.0
    jw = sm(ramp(0.287 - y, 0, 0.02)) * ramp(z, 0.22, 0.26) * (1 - sm(ramp(ax, 0.03, 0.05)))
    b = {"DEF_Root_M": rt * rest, "DEF_Spine1_M": sp * rest, "DEF_Head_M": hw_eff * rest * (1 - jw), "DEF_Jaw_M": hw_eff * rest * jw}
    f2 = sm(ramp(y, 0.54, 0.62))
    b["DEF_Ear1_" + s] = ew * (1 - f2); b["DEF_Ear2_" + s] = ew * f2
    w2 = sm(ramp(ax, 0.14, 0.19)); w3 = sm(ramp(ax, 0.22, 0.27)); w4 = sm(ramp(ax, 0.30, 0.38))
    b["DEF_Wing1_" + s] = ww * (1 - w2); b["DEF_Wing2_" + s] = ww * w2 * (1 - w3)
    b["DEF_Wing3_" + s] = ww * w2 * w3 * (1 - w4); b["DEF_Wing4_" + s] = ww * w2 * w3 * w4
    return b
raw = [row(i) for i in range(len(idx))]
GRP = lambda j: "W" if "Wing" in j else "E" if "Ear" in j else "H" if ("Head" in j or "Jaw" in j) else "B"
def dom(w):
    g = {}
    for j, v in w.items(): g[GRP(j)] = g.get(GRP(j), 0) + v
    return max(g, key=g.get)
# The mesh is ONE welded shell: wing root and head are joined by faces. Head vertices are FROZEN; the wing sheet fades into the head weights over a BAND
# measured along the surface (+ hop count), so the join stretches over a band instead of one long face.
pos = {v: i for i, v in enumerate(idx)}; nb = [set() for _ in idx]; c = 0
for sz in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c + sz]]; c += sz
    for k in range(sz): a, b2 = cs[k], cs[(k + 1) % sz]; nb[a].add(b2); nb[b2].add(a)
dg = [dom(w) for w in raw]
if have_split:
    BAND, HOPS = 0.12, 4
    dist = [1e9] * len(idx); src = [None] * len(idx); hops = [99] * len(idx); hq = []
    for i in range(len(idx)):
        if dg[i] in ("E", "H") and any(dg[n] == "W" for n in nb[i]):
            dist[i] = 0.0; src[i] = i; hops[i] = 0; heapq.heappush(hq, (0.0, i))
    while hq:
        d0, i = heapq.heappop(hq)
        if d0 > dist[i] + 1e-12: continue
        for n in nb[i]:
            if dg[n] != "W": continue
            nd = d0 + math.dist(P[i], P[n])
            if hops[i] + 1 < hops[n] and nd < 0.3: hops[n] = hops[i] + 1; dist[n] = nd; src[n] = src[i]; heapq.heappush(hq, (nd, n))
    new = list(raw)
    for i in range(len(idx)):
        if dg[i] == "W" and src[i] is not None:
            t = 1.0 if dist[i] >= BAND else min(1.0, dist[i] / BAND, hops[i] / HOPS); f = t * t * (3 - 2 * t)
            acc = {}
            for j, v in raw[i].items(): acc[j] = acc.get(j, 0) + f * v
            for j, v in raw[src[i]].items(): acc[j] = acc.get(j, 0) + (1 - f) * v
            new[i] = acc
    raw = new
else:
    # welded ears: ear + head vertices FROZEN, only the WING side of a junction is softened (3 rings, 4 passes of 50/50 averaging with the neighbours)
    from collections import deque
    depth = [99] * len(idx); q = deque()
    for i in range(len(idx)):
        if dg[i] == "W" and any(dg[n] in ("E", "H") for n in nb[i]): depth[i] = 0; q.append(i)
    while q:
        i = q.popleft()
        for n in nb[i]:
            if dg[n] == "W" and depth[n] > depth[i] + 1 and depth[i] + 1 <= 3: depth[n] = depth[i] + 1; q.append(n)
    for _ in range(4):
        new = list(raw)
        for i, w in enumerate(raw):
            if depth[i] <= 3:
                acc = {}
                for j, v in w.items(): acc[j] = acc.get(j, 0) + 0.5 * v
                for n in nb[i]:
                    for j, v in raw[n].items(): acc[j] = acc.get(j, 0) + 0.5 * v / len(nb[i])
                new[i] = acc
        raw = new
def fin(w):
    r = [(j, v) for j, v in w.items() if v > 0.01]; r.sort(key=lambda t: -t[1]); r = r[:4]; t = sum(v for _, v in r); return [(j, v / t) for j, v in r]
api.select([BODY]); api.set_skin_weights(idx, [fin(w) for w in raw])
print("skinned body", len(idx), "ear shells", EARS)
