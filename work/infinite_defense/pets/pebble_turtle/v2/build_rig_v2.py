# Pebble Turtle v2 (mesh moi 703 dinh, 6 manh roi). Chay trong Frolvy cong 9882 (python3 -I tools/frolvy_port.py 9882 <file>).
# Mo rig cu, xoa 4 mesh cu, nhap mesh moi, bind o pose 0 (moi control = 0), trong so theo luat cu theo tung manh.
D = "/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_12_Pebble_Turtle/"
V2 = D + "v2_mesh_moi/"
NEWFBX = "/home/ngocvb/Projects/endless-kicker/Assets/Kho/Skin/mesh/Pet_new/mesh/Pet_Pebble_Turtle.fbx"
V2 = D + "v2_mesh_moi/"
SRC, DST = "PebbleTurtle_rig.fv", "PebbleTurtle_rig_v2.fv"   # doi cho idle / attack
import builtins
if "SRC_OVERRIDE" in globals(): SRC, DST = SRC_OVERRIDE
if not api.open_scene(D + SRC):   # Frolvy tu choi mo khi scene dang do: luu tam ra file roi mo lai
    api.save_scene(V2 + "_tmp_dirty.fv")
    assert api.open_scene(D + SRC), "open_scene that bai"
for o in list(api.ls("Object")):
    api.delete_node(o)
api.import_file(NEWFBX)
M = api.ls("Object")[0]; print("mesh", M, api.ls("Object"))
if SRC == "PebbleTurtle_rig.fv":
    for _c in api.ls("Curve"):
        if _c.startswith("CTL_") and _c != "CTL_Main": api.rotate(_c, 0, 0, 0); api.move(_c, 0, 0, 0)
api.set_frame(3); api.set_frame(0)
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_")]
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
md = api.mesh_data(M); idx = list(md['vertices']); P = md['positions']; n = len(idx)
P = [P[i*3:i*3+3] for i in range(n)]
pos = {v: i for i, v in enumerate(idx)}; par = list(range(n))
def f(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
c = 0
for s in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c+s]]; c += s
    for k in range(1, s): par[f(cs[k])] = f(cs[0])
comps = {}
for i in range(n): comps.setdefault(f(i), []).append(i)
kind = {}
for r, m in comps.items():
    xs = [P[i][0] for i in m]; ys = [P[i][1] for i in m]; zs = [P[i][2] for i in m]
    cz = sum(zs)/len(zs); cx = sum(xs)/len(xs)
    if len(m) > 300: k = "shell"
    elif max(xs) - min(xs) > 0.4: k = "head"
    elif cz > 0: k = "front"
    else: k = "back"
    for i in m: kind[i] = k
print({k: sum(1 for v in kind.values() if v == k) for k in set(kind.values())})
api.select([M]); api.bind_skin(DEF)
def norm(row):
    row = [(j, w) for j, w in row if w > 0.01]
    s = sum(w for _, w in row); return [(j, w/s) for j, w in row]
def shell(p):
    x, y, z = p
    t2 = ramp(z, -0.36, -0.47) * ramp(0.30, y, 0.20)
    t1 = ramp(z, -0.22, -0.34) * ramp(0.30, y, 0.20) - t2
    t1 = max(0.0, t1)
    return [("DEF_Tail2_M", t2), ("DEF_Tail1_M", t1), ("DEF_Root_M", max(0.0, 1 - t1 - t2))]
def leg(pre, p):
    x, y, z = p; s = "L" if x > 0 else "R"
    hipw = ramp(y, 0.11, 0.19); toe = ramp(0.05, y, 0.0)
    return [("DEF_%sHip_%s" % (pre, s), hipw), ("DEF_%sAnkle_%s" % (pre, s), (1-hipw)*(1-toe)), ("DEF_%sToe_%s" % (pre, s), (1-hipw)*toe)]
rows = []
for i in range(n):
    k = kind[i]
    r = shell(P[i]) if k == "shell" else [("DEF_Head_M", 1.0)] if k == "head" else leg("Front" if k == "front" else "Back", P[i])
    rows.append(norm(r))
api.select([M]); api.set_skin_weights(idx, rows)
api.select([])
print(api.check_rig())
print("save", api.save_scene(V2 + DST), V2 + DST)
print("saved")
