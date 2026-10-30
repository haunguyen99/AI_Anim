"""Read bones + animation curves (with key times) from a binary FBX, no Blender. Used to bring a hand-made
blocking FBX (Assets/Boss_Gaygor/Blocking/Bloking50.fbx) into Pose Lab.
Bản dùng chung ở tools/ (chép từ work/boss_gaygor/gaygor_attack_50_blocking/fbxanim.py, 2026-10-28) cho rigpose.py."""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work", "pose_lab", "fbx"))
import fbxread
TICK = 46186158000
def load(path):
    ver, top = fbxread.read(path)
    obj = [n for n in top if n[0] == "Objects"][0][2]; con = [n for n in top if n[0] == "Connections"][0][2]
    models, cn, cv = {}, {}, {}
    for o in obj:
        if o[0] == "Model":
            pr = [k for k in o[2] if k[0] == "Properties70"]
            models[o[1][0]] = dict(name=o[1][1].split("\x00")[0], type=o[1][2], props={p[1][0]: p[1][4:] for p in (pr[0][2] if pr else [])})
        if o[0] == "AnimationCurveNode": cn[o[1][0]] = o[1][1].split("\x00")[0]
        if o[0] == "AnimationCurve":
            d = {k[0]: k[1] for k in o[2]}
            cv[o[1][0]] = (np.array(d["KeyTime"][0]) / TICK, np.array(d["KeyValueFloat"][0], float), d.get("KeyAttrFlags", [[0]])[0])
    par, node_prop, curve_of = {}, {}, {}
    for c in con:
        t, a, b = c[1][0], c[1][1], c[1][2]
        if t == "OO" and a in models and b in models: par[a] = b
        if t == "OP" and a in cn and b in models: node_prop[a] = (b, c[1][3])
        if t == "OP" and a in cv and b in cn: curve_of.setdefault(b, {})[c[1][3]] = a
    for nid, (mid, prop) in node_prop.items():
        ch = curve_of.get(nid, {})
        if all(k in ch for k in ("d|X", "d|Y", "d|Z")):
            models[mid].setdefault("anim", {})[prop] = [cv[ch[k]] for k in ("d|X", "d|Y", "d|Z")]
    return models, par
ORDERS = ["XYZ", "XZY", "YZX", "YXZ", "ZXY", "ZYX"]     # FBX RotationOrder enum; "XYZ" = X applied first
def euler_xyz(r, order=0):
    """FBX euler (degrees) -> 3x3. order = RotationOrder enum (PreRotation/PostRotation are always XYZ).
    AdvancedSkeleton rigs set ZYX/ZXY/XZY on arms, legs, neck: ignoring it broke the Attack 50% poses."""
    rx, ry, rz = np.radians(r)
    cx, sx, cy, sy, cz, sz = np.cos(rx), np.sin(rx), np.cos(ry), np.sin(ry), np.cos(rz), np.sin(rz)
    M = {"X": np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]), "Y": np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]), "Z": np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])}
    o = ORDERS[int(order)]
    return M[o[2]] @ M[o[1]] @ M[o[0]]
def rot_order(m):
    return int(m["props"].get("RotationOrder", [0])[0])
def value_at(m, prop, sec, default):
    v = list(m["props"].get(prop, default))[:3]
    a = m.get("anim", {}).get(prop)
    if a:
        for i in range(3):
            t, val, _ = a[i]; v[i] = float(np.interp(sec, t, val))
    return v
def local(m, sec):
    """FBX local matrix: T * Roff * Rp * Rpre * R * Rpost^-1 * Rp^-1 * Soff * Sp * S * Sp^-1 (pivots assumed 0)."""
    T = value_at(m, "Lcl Translation", sec, [0, 0, 0]); R = value_at(m, "Lcl Rotation", sec, [0, 0, 0]); S = value_at(m, "Lcl Scaling", sec, [1, 1, 1])
    pre = euler_xyz(m["props"].get("PreRotation", [0, 0, 0])[:3]); post = euler_xyz(m["props"].get("PostRotation", [0, 0, 0])[:3])
    M = np.eye(4); M[:3, :3] = pre @ euler_xyz(R, rot_order(m)) @ post.T @ np.diag(S); M[:3, 3] = T
    return M
def key_times(models):
    ts = set()
    for m in models.values():
        for prop, chans in m.get("anim", {}).items():
            for t, _, _ in chans: ts.update(np.round(t * 30, 3))
    return sorted(ts)
