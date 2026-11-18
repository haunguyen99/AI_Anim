# Night Bat v2 skin (mesh moi: 1 object, 3 mảnh rời = than + 2 canh). Chay SAU rig_build_v2.py. Bind khi moi control = 0.
import math
SMOOTH_PASSES = 4
TRANSFER = False   # body: trong so cu (do nguoi dung chinh) chuyen theo dinh gan nhat, bo phan Wing (canh gio la manh roi)
for _c in api.ls("Curve"):
    if _c.startswith("CTL_") and _c != "CTL_Main": api.rotate(_c, 0, 0, 0); api.move(_c, 0, 0, 0)
api.set_frame(3); api.set_frame(0)
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_") and "Muzzle" not in j]
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t * t * (3 - 2 * t)
M = "Pet_Night_Bat"
md = api.mesh_data(M); idx = list(md['vertices']); P = md['positions']; P = [P[i * 3:i * 3 + 3] for i in range(len(idx))]
pos = {v: i for i, v in enumerate(idx)}; par = list(range(len(idx)))
def find(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
c = 0
for s in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c + s]]; c += s
    for k in cs[1:]: par[find(k)] = find(cs[0])
roots = {}
for i in range(len(idx)): roots.setdefault(find(i), []).append(i)
body_root = max(roots, key=lambda r: len(roots[r]))
isbody = [find(i) == body_root for i in range(len(idx))]
print("shells", sorted(len(v) for v in roots.values()))
api.select([M])
try: api.unbind_skin()
except Exception: pass
api.select([M]); api.bind_skin(DEF)
WX = [0.09, 0.20, 0.277, 0.38]
def wing(x, s):
    ax = abs(x)
    if ax <= WX[0]: w = [1, 0, 0, 0]
    elif ax >= WX[3]: w = [0, 0, 0, 1]
    else:
        w = [0, 0, 0, 0]
        for k in range(3):
            if WX[k] <= ax <= WX[k + 1]:
                t = sm((ax - WX[k]) / (WX[k + 1] - WX[k])); w[k] = 1 - t; w[k + 1] = t
    return {"DEF_Wing%d_%s" % (k + 1, s): w[k] for k in range(4) if w[k] > 0}
def body(x, y, z):
    ax = abs(x); s = "L" if x > 0 else "R"
    q = (((ax / 0.19) ** 2) + (((y - 0.345) / 0.175) ** 2) + (((z - 0.15) / 0.18) ** 2)) ** 0.5
    outside = sm(ramp(q, 1.0, 1.25))
    ew = sm(ramp(y, 0.43, 0.50)) * sm(ramp(ax, 0.05, 0.10)) * outside
    rest = 1 - ew
    hw = sm(ramp(y, 0.165, 0.215)); sp = (1 - hw) * sm(ramp(y, 0.04, 0.14)); rt = 1 - hw - sp
    if ew > 0: hw, sp, rt = 1.0, 0.0, 0.0
    jw = sm(ramp(0.287 - y, 0, 0.02)) * ramp(z, 0.22, 0.26) * (1 - sm(ramp(ax, 0.03, 0.05)))
    f2 = sm(ramp(y, 0.54, 0.62))
    b = {"DEF_Root_M": rt * rest, "DEF_Spine1_M": sp * rest, "DEF_Head_M": hw * rest * (1 - jw), "DEF_Jaw_M": hw * rest * jw,
         "DEF_Ear1_" + s: ew * (1 - f2), "DEF_Ear2_" + s: ew * f2}
    return b
def fin(w):
    r = [(j, v) for j, v in w.items() if v > 0.01]; r.sort(key=lambda t: -t[1]); r = r[:4]; t = sum(v for _, v in r); return [(j, v / t) for j, v in r]
raw = []
for i in range(len(idx)):
    x, y, z = P[i]
    raw.append(body(x, y, z) if isbody[i] else wing(x, "L" if x > 0 else "R"))
# lam mem cho mep tai-dau: vung y 0.36-0.62 (khong dung mat/ham), 4 luot tron 50% voi trung binh hang xom => chuyen dan qua vai vong luoi
nb = [set() for _ in idx]; c = 0
for s in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c + s]]; c += s
    for k in range(s): a, b2 = cs[k], cs[(k + 1) % s]; nb[a].add(b2); nb[b2].add(a)
zone = [isbody[i] and 0.36 < P[i][1] < 0.62 and abs(P[i][0]) > 0.03 for i in range(len(idx))]
for _ in range(SMOOTH_PASSES):
    new = list(raw)
    for i in range(len(idx)):
        if not zone[i]: continue
        acc = {}
        for j, v in raw[i].items(): acc[j] = acc.get(j, 0) + 0.5 * v
        for n in nb[i]:
            for j, v in raw[n].items(): acc[j] = acc.get(j, 0) + 0.5 * v / len(nb[i])
        new[i] = acc
    raw = new
if TRANSFER:
    import json
    d = json.load(open("/home/ngocvb/Projects/AI_animation/work/infinite_defense/pets/night_bat/_old_skin_v1.json"))
    OP = d["P"]; OW = d["W"]; no = len(OP) // 3
    OPt = [(OP[i*3], OP[i*3+1], OP[i*3+2]) for i in range(no)]
    # chi lay dinh cu KHONG phai canh (co trong so Wing > 0.5 => bo qua nguon)
    src = [i for i in range(no) if sum(w for j, w in OW[i] if "Wing" in j) < 0.5]
    far = 0; used = 0; dmax = 0.0
    for i in range(len(idx)):
        if not isbody[i]: continue
        x, y, z = P[i]; best = None; bd = 9
        for k in src:
            q = OPt[k]; dd = (q[0]-x)**2 + (q[1]-y)**2 + (q[2]-z)**2
            if dd < bd: bd = dd; best = k
        bd = bd ** 0.5; dmax = max(dmax, bd)
        w = {j: v for j, v in OW[best] if "Wing" not in j}
        t = sum(w.values())
        if bd > 0.03 or t < 0.5: far += 1; continue
        raw[i] = {j: v / t for j, v in w.items()}; used += 1
    print("transfer used", used, "kept formula", far, "max dist", round(dmax, 3))
rows = [fin(w) for w in raw]
api.select([M]); api.set_skin_weights(idx, rows)
print("skinned", len(idx))
