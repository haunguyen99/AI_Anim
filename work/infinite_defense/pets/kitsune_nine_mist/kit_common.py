# Kitsune Nine-Mist: phan tich mesh (mảnh rời, đuôi, đường tâm đuôi). exec() bởi rig_build.py / rig_skin.py trong Frolvy.
import heapq, math
MESH = "Pet_Kitsune_Nine_Mist"
_md = api.mesh_data(MESH)
IDX = list(_md['vertices']); _P = _md['positions']
V = [_P[i * 3:i * 3 + 3] for i in range(len(IDX))]
_pos = {v: i for i, v in enumerate(IDX)}
NB = [dict() for _ in IDX]; _par = list(range(len(IDX)))
def _f(a):
    while _par[a] != a: _par[a] = _par[_par[a]]; a = _par[a]
    return a
_c = 0
for _s in _md['face_sizes']:
    _cs = [_pos.get(q, q) for q in _md['face_corners'][_c:_c + _s]]; _c += _s
    for k in range(_s):
        a, b = _cs[k], _cs[(k + 1) % _s]
        if a != b: NB[a][b] = math.dist(V[a], V[b]); NB[b][a] = NB[a][b]
    for k in range(1, _s): _par[_f(_cs[k])] = _f(_cs[0])
_comp = {}
for i in range(len(IDX)): _comp.setdefault(_f(i), []).append(i)
COMPS = sorted(_comp.values(), key=lambda m: -len(m))
BODY = COMPS[0]
def cen(m): return [sum(V[i][a] for i in m) / len(m) for a in range(3)]
MASK = [m for m in COMPS[1:] if cen(m)[2] > 0.25]
TAILC = []
for m in COMPS[1:]:
    if cen(m)[2] > 0.25: continue
    if len(m) > 80: TAILC += [[i for i in m if V[i][0] > 0], [i for i in m if V[i][0] <= 0]]   # hai đuôi dính nhau ở gốc
    else: TAILC.append(m)
def geo(m):
    # đường tâm đuôi = trọng tâm các vòng cắt (BFS theo số cạnh từ đỉnh sát thân), làm mượt; t = vị trí chiếu lên đường tâm theo độ dài cung
    ms = set(m); C = (0, 0.28, 0.0); r = min(m, key=lambda i: math.dist(V[i], C))
    h = {r: 0}; q = [r]
    for i in q:
        for n in NB[i]:
            if n in ms and n not in h: h[n] = h[i] + 1; q.append(n)
    H = max(h.values()); pts = []
    for k in range(H + 1):
        L = [i for i in m if h.get(i, H) == k]
        if L: pts.append([sum(V[i][a] for i in L) / len(L) for a in range(3)])
    sm_ = [pts[0]] + [[(pts[j - 1][a] + 2 * pts[j][a] + pts[j + 1][a]) / 4 for a in range(3)] for j in range(1, len(pts) - 1)] + [pts[-1]]
    pts = sm_; cum = [0.0]
    for j in range(1, len(pts)): cum.append(cum[-1] + math.dist(pts[j], pts[j - 1]))
    tot = cum[-1]; T = {}
    for i in m:
        best = (1e9, 0.0)
        for j in range(len(pts) - 1):
            A, B = pts[j], pts[j + 1]; ab = [B[a] - A[a] for a in range(3)]; l2 = sum(c * c for c in ab) or 1e-9
            u = max(0.0, min(1.0, sum((V[i][a] - A[a]) * ab[a] for a in range(3)) / l2)); d = math.dist(V[i], [A[a] + u * ab[a] for a in range(3)])
            if d < best[0]: best = (d, (cum[j] + u * (cum[j + 1] - cum[j])) / tot)
        T[i] = best[1]
    def at(f):
        x = f * tot
        for j in range(len(pts) - 1):
            if cum[j + 1] >= x: u = (x - cum[j]) / ((cum[j + 1] - cum[j]) or 1e-9); return [pts[j][a] + u * (pts[j + 1][a] - pts[j][a]) for a in range(3)]
        return pts[-1]
    GEO[id(m)] = (at, pts)
    return T, tot
GEO = {}
def centroid_at(m, T, t0, t1):
    s = [i for i in m if t0 <= T[i] <= t1]
    if len(s) < 3:
        c = (t0 + t1) / 2; s = sorted(m, key=lambda i: abs(T[i] - c))[:4]
    return [sum(V[i][a] for i in s) / len(s) for a in range(3)]
TTS = (0.0, 0.2, 0.4, 0.6, 0.8)
TAILS = []   # dict(k, s, verts, T, J (4 pos), tip)
_c5 = [m for m in TAILC if abs(cen(m)[0]) < 0.03][0]
_sides = {1: [], -1: []}
for m in TAILC:
    if m is _c5: continue
    _sides[1 if cen(m)[0] > 0 else -1].append(m)
def _mk(m, k, s):
    T, ln = geo(m)
    at, pts = GEO[id(m)]; J = [at(t) for t in TTS]; tip = pts[-1]
    TAILS.append(dict(k=k, s=s, verts=m, T=T, J=J, tip=tip, len=ln))
_mk(_c5, 1, "M")
for sg, nm in ((1, "L"), (-1, "R")):
    for k, m in enumerate(sorted(_sides[sg], key=lambda m: -cen(m)[1])): _mk(m, k + 2, nm)
def tail_name(t, n): return "DEF_Tail%d_%d_%s" % (t['k'], n, t['s'])
def muzzle_name(t): return "DEF_Muzzle_M" if t['k'] == 1 else "DEF_Muzzle%d_%s" % (t['k'], t['s'])
