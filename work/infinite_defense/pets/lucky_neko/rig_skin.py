# Lucky Neko bind + weights. Chay SAU rig_build.py. Bind khi MOI control = 0.
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
def fin(w):
    r = [(j, v) for j, v in w.items() if v > 0.01]; r.sort(key=lambda t: -t[1]); r = r[:4]; t = sum(v for _, v in r); return [(j, v / t) for j, v in r]
def rigid(m, j):
    md = api.mesh_data(m); idx = list(md['vertices']); bind(m); api.select([m]); api.set_skin_weights(idx, [[(j, 1.0)] for _ in idx])
def jar_skin():
    # jar body 100% Jar_M; 2 tassels (small shells): chain of 3 by height, top fades into the jar
    m = "Pet_lucky_neko.001"; md = api.mesh_data(m); idx = list(md['vertices']); Pj = md['positions']; Pj = [Pj[i * 3:i * 3 + 3] for i in range(len(idx))]
    par = list(range(len(idx)))
    def fnd(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    pos = {}
    for i, p in enumerate(Pj):
        k = (round(p[0], 4), round(p[1], 4), round(p[2], 4))
        if k in pos: par[fnd(i)] = fnd(pos[k])
        else: pos[k] = i
    c = 0
    for sz in md['face_sizes']:
        F = md["face_corners"][c:c + sz]; c += sz
        for k in range(1, sz): par[fnd(F[k])] = fnd(F[0])
    shells = {}
    for i in range(len(idx)): shells.setdefault(fnd(i), []).append(i)
    small = [v for v in shells.values() if len(v) <= 60]
    small.sort(key=lambda v: -min(Pj[i][0] for i in v))          # [0] = A (closer to the jar centre), [1] = B
    owner = {}
    for name, v in zip("AB", small):
        for i in v: owner[i] = name
    rows = []
    for i in range(len(idx)):
        if i not in owner: rows.append([("DEF_Jar_M", 1.0)]); continue
        n = owner[i]; y = Pj[i][1]
        jar = sm(ramp(y, 0.125, 0.152))
        u = ramp(0.14 - y, 0.0, 0.10)                                  # 0 at the top, 1 at the tip
        w2 = 1 - abs(u * 2 - 1) if True else 0
        w1 = 1 - sm(ramp(u, 0.0, 0.5)); w3 = sm(ramp(u, 0.5, 1.0)); w2 = 1 - w1 - w3
        r = {"DEF_Jar_M": jar, "DEF_Tassel%s1_M" % n: (1 - jar) * w1, "DEF_Tassel%s2_M" % n: (1 - jar) * w2, "DEF_Tassel%s3_M" % n: (1 - jar) * w3}
        rows.append(fin(r))
    bind(m); api.select([m]); api.set_skin_weights(idx, rows)
    print("jar tassels", {k: len(v) for k, v in zip("AB", small)})
jar_skin(); rigid("Pet_lucky_neko.002", "DEF_Coin_L")

BODY = "Pet_lucky_neko"
md = api.mesh_data(BODY); idx = list(md['vertices']); P = md['positions']; P = [P[i * 3:i * 3 + 3] for i in range(len(idx))]
bind(BODY)
# shells (welded by position): head shells = glasses + head (+ bell) -> Head / ears; the rest = body
par = list(range(len(idx)))
def fnd(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
pos = {}
for i, p in enumerate(P):
    k = (round(p[0], 4), round(p[1], 4), round(p[2], 4))
    if k in pos: par[fnd(i)] = fnd(pos[k])
    else: pos[k] = i
vpos = {v: i for i, v in enumerate(idx)}; c = 0
for sz in md['face_sizes']:
    F = md["face_corners"][c:c + sz]; c += sz
    for k in range(1, sz): par[fnd(F[k])] = fnd(F[0])
shells = {}
for i in range(len(idx)): shells.setdefault(fnd(i), []).append(i)
HEAD = set()
for v in shells.values():
    if min(P[i][1] for i in v) > 0.2: HEAD.update(v)
print("head verts", len(HEAD), "of", len(idx), "shells", sorted(len(v) for v in shells.values()))
EAR = {(0.099, 0.532, 0.021): 1.0, (0.08, 0.53, 0.022): 1.0, (0.098, 0.523, 0.04): 1.0, (0.08, 0.517, 0.042): 1.0, (0.124, 0.515, 0.018): 1.0, (0.118, 0.506, 0.039): 1.0,
       (0.048, 0.51, 0.023): 0.15, (0.059, 0.498, 0.043): 0.15, (0.144, 0.482, 0.014): 0.92, (0.133, 0.474, 0.038): 0.87, (0.017, 0.468, 0.021): 0.84, (0.041, 0.464, 0.044): 0.73,
       (0.038, 0.46, -0.001): 0.99, (0.061, 0.458, 0.035): 0.97, (0.05, 0.457, 0.057): 0.14, (0.154, 0.447, 0.012): 0.46, (0.07, 0.444, -0.016): 0.89, (0.138, 0.441, 0.039): 0.99,
       (0.109, 0.427, 0.031): 0.87, (0.114, 0.421, -0.029): 0.99, (0.136, 0.395, -0.016): 0.64, (0.152, 0.377, 0.015): 0.19}
def row(i):
    b = row0(i); x, y, z = P[i]
    bd = (x * x + (y - 0.215) ** 2 + (z - 0.165) ** 2) ** 0.5
    k = 1 - sm(ramp(bd, 0.03, 0.05))
    if k <= 0 or z < 0.12: return b
    base = {"DEF_Spine1_M": 1.0} if (y > 0.17 and k > 0.3) else b                 # the bell hangs on the chest: its neighbours follow Spine1, not the head
    r = {j: v * (1 - k) for j, v in base.items()}; r['DEF_Bell_M'] = k; return r
def row0(i):
    x, y, z = P[i]; s = "L" if x > 0 else "R"; ax = abs(x)
    # head ellipsoid: q<1 inside the head; ears = outside it, high up
    q = (((ax / 0.162) ** 2) + (((y - 0.375) / 0.15) ** 2) + (((z - 0.02) / 0.17) ** 2)) ** 0.5
    if i in HEAD:
        # ear weights follow the area the user painted (EAR table = total ear weight per vertex, left side, mirrored); split Ear1 (base) / Ear2 (upper ear) by height
        tot = EAR.get((round(ax, 3), round(y, 3), round(z, 3)), 0.0)
        if tot <= 0: return {"DEF_Head_M": 1.0}
        e2 = sm(ramp(y, 0.485, 0.52))
        return {"DEF_Head_M": 1 - tot, "DEF_Ear1_" + s: tot * (1 - e2), "DEF_Ear2_" + s: tot * e2}
    # --- below the head: torso / neck / arms / legs / tail
    neck = sm(ramp(y, 0.225, 0.255)) * (1 - sm(ramp(ax, 0.07, 0.10)))   # Spine1 -> Head, only on the neck column (not the shoulders)
    torso = {"DEF_Spine1_M": 1 - neck, "DEF_Head_M": neck}
    # tail (thin rod behind the hips)
    b = None
    if z < -0.07 and y < 0.155:
        t = sm(ramp(-z, 0.07, 0.09)); zz = -z
        t1 = 1 - sm(ramp(zz, 0.075, 0.14)); t3 = sm(ramp(zz, 0.14, 0.20)); t2 = 1 - t1 - t3
        tail = {"DEF_Root_M": 1 - t, "DEF_Tail1_M": t * t1, "DEF_Tail2_M": t * t2, "DEF_Tail3_M": t * t3}
        return tail
    # arms
    if y > 0.17:
        a = sm(ramp(ax, 0.115, 0.15))
        w_el_up = sm(ramp(ax, 0.10, 0.165)); w_wr = sm(ramp(ax, 0.165, 0.21))
        arm = {"DEF_Shoulder_" + s: 1 - w_el_up, "DEF_Elbow_" + s: w_el_up * (1 - w_wr), "DEF_Wrist_" + s: w_wr}
        base = {"DEF_Spine1_M": 1 - neck, "DEF_Head_M": neck}
        r = {}
        for j, v in base.items(): r[j] = r.get(j, 0) + v * (1 - a)
        for j, v in arm.items(): r[j] = r.get(j, 0) + v * a
        # shoulder takes some of the torso weight beside the arm root
        return r
    # legs / lower body
    body = {}
    sp = sm(ramp(y, 0.10, 0.17))                             # Root -> Spine1
    body["DEF_Spine1_M"] = sp; body["DEF_Root_M"] = 1 - sp
    if y < 0.105:
        h = sm(ramp(0.105 - y, 0.0, 0.035))                  # Root -> Hip
        an = sm(ramp(0.062 - y, 0.0, 0.02))                  # Hip -> Ankle
        to = sm(ramp(z, 0.04, 0.075)) * sm(ramp(0.05 - y, 0.0, 0.03))   # Ankle -> Toes
        r = {"DEF_Root_M": (1 - h)}
        r["DEF_Hip_" + s] = h * (1 - an)
        r["DEF_Ankle_" + s] = h * an * (1 - to)
        r["DEF_Toes_" + s] = h * an * to
        for j, v in body.items():
            if j != "DEF_Root_M": r[j] = r.get(j, 0) + v * (1 - h)
        r["DEF_Root_M"] = r.get("DEF_Root_M", 0) + body["DEF_Root_M"] * (1 - h) - (1 - h)
        return r
    return body
raw = [row(i) for i in range(len(idx))]
for i, r in enumerate(raw):
    if "DEF_Root_M" in r and r["DEF_Root_M"] < 0: r["DEF_Root_M"] = 0
api.select([BODY]); api.set_skin_weights(idx, [fin(w) for w in raw])
print("skinned body", len(idx))
