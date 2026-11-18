# Steam-Pug Turbo bind + weights. Chay SAU rig_build.py. Bind khi MOI control = 0.
for _c in api.ls("Curve"):
    if _c.startswith("CTL_") and _c != "CTL_Main": api.rotate(_c, 0, 0, 0); api.move(_c, 0, 0, 0)
api.set_frame(3); api.set_frame(0)
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_") and "Muzzle" not in j]
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t * t * (3 - 2 * t)
BODY = api.ls("Object")[0]
md = api.mesh_data(BODY); idx = list(md['vertices']); P = md['positions']; P = [P[i*3:i*3+3] for i in range(len(idx))]
pos = {v: i for i, v in enumerate(idx)}; par = list(range(len(idx)))
def f(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
c = 0
for s in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c+s]]; c += s
    for q in cs[1:]: par[f(q)] = f(cs[0])
roots = {}
for i in range(len(idx)): roots.setdefault(f(i), []).append(i)
comps = sorted(roots.values(), key=len, reverse=True)
cid = [0] * len(idx)
for k, cc in enumerate(comps):
    for i in cc: cid[i] = k
api.select([BODY])
try: api.unbind_skin()
except Exception: pass
api.select([BODY]); api.bind_skin(DEF)
def row(i):
    x, y, z = P[i]; s = "L" if x > 0 else "R"; ax = abs(x); k = cid[i]
    if k == 1: return {"DEF_Goggles_M": 1}
    if k == 2: return {"DEF_Root_M": 1}
    if k == 3: return {"DEF_Valve_M": 1}
    if k in (4, 5): return {"DEF_Pipe_" + s: 1}
    if k == 6: return {"DEF_Exhaust_M": 1}
    if k == 7: return {"DEF_Gauge_M": 1}
    if k in (8, 9): return {"DEF_Tank_" + s: 1}
    # --- than + dau (manh 0)
    hw = sm(ramp(y, 0.34, 0.50)) * sm(ramp(z, -0.24, -0.12))     # dau tren co (khong lan ra lung/duoi)
    ew = sm(ramp(ax, 0.29, 0.34)) * sm(ramp(y, 0.42, 0.50))       # tai (hang ngoai)
    f2 = sm(ramp(0.76 - y, 0.0, 0.16))                            # tai thap -> Ear2
    sp = sm(ramp(z, -0.10, 0.10))                                 # Spine1 phia truoc, Root phia sau
    tw = sm(ramp(-z, 0.30, 0.35)) * sm(ramp(y, 0.26, 0.32)) * (1 - hw)   # duoi
    lw = (1 - sm(ramp(y, 0.20, 0.30))) * sm(ramp(ax, 0.02, 0.07))   # chan (giua bung = than)
    front = z > -0.02
    l1 = sm(ramp(y, 0.12, 0.22)); pw = 1 - sm(ramp(y, 0.03, 0.08)); l2 = 1 - l1 - pw
    if l2 < 0: l2 = 0
    pre = "F" if front else "B"
    b = {}
    body_w = 1 - hw - tw
    b["DEF_Head_M"] = hw
    rest = max(0.0, body_w) * (1 - lw)
    b["DEF_Spine1_M"] = rest * sp; b["DEF_Root_M"] = rest * (1 - sp)
    lg = max(0.0, body_w) * lw
    fz = sm(ramp(z, -0.08, 0.04))
    for pre, q in (("F", fz), ("B", 1 - fz)):
        b["DEF_%sLeg1_%s" % (pre, s)] = lg * q * l1; b["DEF_%sLeg2_%s" % (pre, s)] = lg * q * l2; b["DEF_%sPaw_%s" % (pre, s)] = lg * q * pw
    t2 = sm(ramp(-z, 0.36, 0.42))
    b["DEF_Tail1_M"] = tw * (1 - t2); b["DEF_Tail2_M"] = tw * t2
    return b
def fin(w):
    r = [(j, v) for j, v in w.items() if v > 0.01]; r.sort(key=lambda t: -t[1]); r = r[:4]; t = sum(v for _, v in r); return [(j, v / t) for j, v in r]
raw = [row(i) for i in range(len(idx))]
# lam trong weight: manh 0 (than+dau+chan) lam mem 3 luot theo ke ben; manh roi giu nguyen. Khong cho tran sang ben trai/phai doi dien.
nb = [set() for _ in idx]; c = 0
for sz in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c+sz]]; c += sz
    for k in range(sz):
        a, b2 = cs[k], cs[(k+1) % sz]; nb[a].add(b2); nb[b2].add(a)
main = [i for i in range(len(idx)) if cid[i] == 0]
for _ in range(3):
    new = list(raw)
    for i in main:
        acc = {}
        for j, v in raw[i].items(): acc[j] = acc.get(j, 0) + 0.5 * v
        for n in nb[i]:
            for j, v in raw[n].items(): acc[j] = acc.get(j, 0) + 0.5 * v / len(nb[i])
        x = P[i][0]
        for j in list(acc):
            if j[-2:] == "_L" and x < -0.04 or j[-2:] == "_R" and x > 0.04: del acc[j]
        new[i] = acc
    raw = new
api.select([BODY]); api.set_skin_weights(idx, [fin(w) for w in raw])
print("skinned", len(idx), "comps", len(comps))
