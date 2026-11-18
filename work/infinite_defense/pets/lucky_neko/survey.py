for o in api.ls("Object"):
    md = api.mesh_data(o); P = md['positions']; n = len(P)//3
    par = list(range(n))
    def f(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    c = 0
    for s in md['face_sizes']:
        F = md['face_corners'][c:c+s]; c += s
        for k in range(1, s): par[f(F[k])] = f(F[0])
    # weld by position (uv seams)
    pos = {}
    for i in range(n):
        key = (round(P[3*i],4), round(P[3*i+1],4), round(P[3*i+2],4))
        if key in pos: par[f(i)] = f(pos[key])
        else: pos[key] = i
    sh = {}
    for i in range(n): sh.setdefault(f(i), []).append(i)
    print(o, n, "shells", len(sh))
    for k, v in sorted(sh.items(), key=lambda t: -len(t[1])):
        xs = [P[3*i] for i in v]; ys = [P[3*i+1] for i in v]; zs = [P[3*i+2] for i in v]
        print("  %4d v x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f" % (len(v), min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
