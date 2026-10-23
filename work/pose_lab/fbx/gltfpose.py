import json, base64, struct, numpy as np
def load(path):
    j = json.load(open(path)); buf = base64.b64decode(j["buffers"][0]["uri"].split(",", 1)[1])
    def acc(i):
        a = j["accessors"][i]; bv = j["bufferViews"][a["bufferView"]]
        nc = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[a["type"]]
        dt = {5126: "f4", 5123: "u2", 5125: "u4"}[a["componentType"]]
        off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        arr = np.frombuffer(buf, dtype=dt, count=a["count"] * nc, offset=off).reshape(a["count"], nc)
        return arr
    return j, acc
def local_mats(j, acc, k):
    """Local 4x4 per node at animation key k (static TRS where a node has no channel)."""
    N = j["nodes"]; T = {}; R = {}; S = {}
    for i, n in enumerate(N):
        T[i] = np.array(n.get("translation", [0, 0, 0]), float); R[i] = np.array(n.get("rotation", [0, 0, 0, 1]), float); S[i] = np.array(n.get("scale", [1, 1, 1]), float)
    for a in j.get("animations", [])[:1]:
        for ch in a["channels"]:
            s = a["samplers"][ch["sampler"]]; v = acc(s["output"]); i = ch["target"]["node"]; p = ch["target"]["path"]
            kk = min(k, len(v) - 1)
            if p == "translation": T[i] = v[kk].astype(float)
            elif p == "rotation": R[i] = v[kk].astype(float)
            elif p == "scale": S[i] = v[kk].astype(float)
    M = {}
    for i in range(len(N)):
        x, y, z, w = R[i]
        r = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
        m = np.eye(4); m[:3, :3] = r * S[i]; m[:3, 3] = T[i]; M[i] = m
    return M
def world(j, M):
    N = j["nodes"]; par = {}
    for i, n in enumerate(N):
        for c in n.get("children", []): par[c] = i
    W = {}
    def w(i):
        if i not in W: W[i] = (w(par[i]) @ M[i]) if i in par else M[i]
        return W[i]
    for i in range(len(N)): w(i)
    return W, par
