import numpy as np, fbxread
def euler_xyz(r):
    rx, ry, rz = np.radians(r)
    cx, sx, cy, sy, cz, sz = np.cos(rx), np.sin(rx), np.cos(ry), np.sin(ry), np.cos(rz), np.sin(rz)
    X = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Y = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]); Z = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    return Z @ Y @ X
def load(path):
    ver, top = fbxread.read(path)
    obj = [n for n in top if n[0] == "Objects"][0][2]; con = [n for n in top if n[0] == "Connections"][0][2]
    models = {}; cn = {}; cv = {}
    for o in obj:
        if o[0] == "Model": models[o[1][0]] = dict(name=o[1][1].split("\x00")[0], type=o[1][2], props={p[1][0]: p[1][4:] for p in [k for k in o[2] if k[0] == "Properties70"][0][2]})
        if o[0] == "AnimationCurveNode": cn[o[1][0]] = o[1][1].split("\x00")[0]
        if o[0] == "AnimationCurve":
            kv = [k for k in o[2] if k[0] == "KeyValueFloat"][0][1][0]; cv[o[1][0]] = kv
    par = {}; node_prop = {}; curve_of = {}
    for c in con:
        t, a, b = c[1][0], c[1][1], c[1][2]
        if t == "OO" and a in models and b in models: par[a] = b
        if t == "OP" and a in cn and b in models: node_prop[a] = (b, c[1][3])
        if t == "OP" and a in cv and b in cn: curve_of.setdefault(b, {})[c[1][3]] = a
    for nid, (mid, prop) in node_prop.items():
        ch = curve_of.get(nid, {})
        models[mid].setdefault("anim", {})[prop] = [cv[ch[k]] for k in ("d|X", "d|Y", "d|Z")]
    return models, par
def locals_at(models, k):
    L = {}
    for mid, m in models.items():
        T = list(m["props"].get("Lcl Translation", [0, 0, 0])); R = list(m["props"].get("Lcl Rotation", [0, 0, 0])); S = list(m["props"].get("Lcl Scaling", [1, 1, 1]))
        for prop, arr in (("Lcl Translation", T), ("Lcl Rotation", R), ("Lcl Scaling", S)):
            a = m.get("anim", {}).get(prop)
            if a:
                for i in range(3): arr[i] = a[i][min(k, len(a[i]) - 1)]
        M = np.eye(4); M[:3, :3] = euler_xyz(R) * np.array(S); M[:3, 3] = T
        L[mid] = M
    return L
def worlds(models, par, L):
    W = {}
    def w(i):
        if i not in W: W[i] = (w(par[i]) @ L[i]) if i in par else L[i]
        return W[i]
    for i in models: w(i)
    return W
