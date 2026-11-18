o = "Pet_lucky_neko.001"; md = api.mesh_data(o); P = md['positions']; n = len(P)//3
par = list(range(n))
def f(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
c = 0
for s in md['face_sizes']:
    F = md['face_corners'][c:c+s]; c += s
    for k in range(1, s): par[f(F[k])] = f(F[0])
pos = {}
for i in range(n):
    k = (round(P[3*i],4), round(P[3*i+1],4), round(P[3*i+2],4))
    if k in pos: par[f(i)] = f(pos[k])
    else: pos[k] = i
sh = {}
for i in range(n): sh.setdefault(f(i), []).append(i)
for r, v in sh.items():
    if len(v) == 115 or len(v) > 100: print("jar", len(v)); continue
    print("shell", len(v))
    for y0 in [0.0 + 0.02*i for i in range(0, 9)]:
        s = [i for i in v if y0 <= P[3*i+1] < y0+0.02]
        if s: print("  y %.2f n%2d c (%.3f, %.3f, %.3f)" % (y0, len(s), sum(P[3*i] for i in s)/len(s), sum(P[3*i+1] for i in s)/len(s), sum(P[3*i+2] for i in s)/len(s)))
