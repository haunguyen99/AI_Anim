# Đọc FBX binary (không Blender): mesh + skeleton bind + skin weights -> JSON.
# Chạy: .venv\Scripts\python.exe -I work\rig_lab\extract_fbx.py <fbx> <outdir>
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pose_lab", "fbx"))
import fbxread
import numpy as np

fbx, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
_, top = fbxread.read(fbx)
T = {n[0]: n for n in top}
objs = T["Objects"][2]
nm = lambda s: s.split("\x00")[0]
byid = {o[1][0]: o for o in objs}
conns = [(c[1][0], c[1][1], c[1][2]) for c in T["Connections"][2] if c[0] == "C"]
child_of = {}   # child id -> [parent ids]
for t, a, b in conns:
    child_of.setdefault(a, []).append(b)

models = {o[1][0]: o for o in objs if o[0] == "Model"}
bones = {i: o for i, o in models.items() if o[1][2] == "LimbNode"}
meshes = {i: o for i, o in models.items() if o[1][2] == "Mesh"}

def sub(o, name):
    return next((k for k in o[2] if k[0] == name), None)

# bone world bind from cluster TransformLink
clusters = {i: o for i, o in byid.items() if o[0] == "Deformer" and o[1][2] == "Cluster"}
bone_of_cluster, skin_of_cluster = {}, {}
for t, a, b in conns:
    if b in clusters and a in bones: bone_of_cluster[b] = a
    if a in clusters and b in byid and byid[b][0] == "Deformer": skin_of_cluster[a] = b
geom_of_skin = {}
for t, a, b in conns:
    if a in byid and byid[a][0] == "Deformer" and byid[a][1][2] == "Skin" and b in byid and byid[b][0] == "Geometry":
        geom_of_skin[a] = b
    if b in byid and byid[b][0] == "Deformer" and byid[b][1][2] == "Skin" and a in byid and byid[a][0] == "Geometry":
        geom_of_skin[b] = a
bind = {}
for c, bid in bone_of_cluster.items():
    m = np.array(sub(clusters[c], "TransformLink")[1][0]).reshape(4, 4).T  # FBX column-major
    bind[bid] = m
skel = []
for bid, o in bones.items():
    par = [p for p in child_of.get(bid, []) if p in bones]
    props = {p[1][0]: p[1][4:] for p in (sub(o, "Properties70") or (0, 0, []))[2]}
    skel.append(dict(id=bid, name=nm(o[1][1]), parent=bones[par[0]][1][1].split("\x00")[0] if par else None,
                     lcl_t=props.get("Lcl Translation"), lcl_r=props.get("Lcl Rotation"), lcl_s=props.get("Lcl Scaling"),
                     bind_pos=(bind[bid][:3, 3].tolist() if bid in bind else None),
                     bind_mat=(bind[bid].flatten().tolist() if bid in bind else None)))
for s in skel: s.pop("id")

def _rot(e):  # FBX mặc định thứ tự XYZ (R = Rz·Ry·Rx), độ
    x, y, z = np.radians(e)
    Rx = np.array([[1, 0, 0], [0, np.cos(x), -np.sin(x)], [0, np.sin(x), np.cos(x)]])
    Ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    Rz = np.array([[np.cos(z), -np.sin(z), 0], [np.sin(z), np.cos(z), 0], [0, 0, 1]])
    M = np.eye(4); M[:3, :3] = Rz @ Ry @ Rx; return M
def _tr(v):
    M = np.eye(4); M[:3, 3] = v; return M
def _sc(v):
    return np.diag([v[0], v[1], v[2], 1.0])
def model_matrix(o):
    """World matrix của node mesh (gộp cả cha là Model), theo công thức transform FBX."""
    pr = {p[1][0]: list(p[1][4:]) for p in (sub(o, "Properties70") or (0, 0, []))[2]}
    g = lambda k, d: np.array(pr.get(k, d), float)
    z, one = [0, 0, 0], [1, 1, 1]
    Rp, Sp = g("RotationPivot", z), g("ScalingPivot", z)
    L = (_tr(g("Lcl Translation", z)) @ _tr(g("RotationOffset", z)) @ _tr(Rp) @ _rot(g("PreRotation", z))
         @ _rot(g("Lcl Rotation", z)) @ np.linalg.inv(_rot(g("PostRotation", z))) @ _tr(-Rp)
         @ _tr(g("ScalingOffset", z)) @ _tr(Sp) @ _sc(g("Lcl Scaling", one)) @ _tr(-Sp))
    G = _tr(g("GeometricTranslation", z)) @ _rot(g("GeometricRotation", z)) @ _sc(g("GeometricScaling", one))
    par = [p for p in child_of.get(o[1][0], []) if p in models]
    W = model_matrix(models[par[0]]) if par else np.eye(4)
    return W @ L @ G

# mesh model -> geometry
meshout = []
for mid, mo in meshes.items():
    g = next((byid[p] for p in child_of.get(mid, []) if p in byid and byid[p][0] == "Geometry") , None)
    if g is None:
        g = next((byid[a] for t, a, b in conns if b == mid and a in byid and byid[a][0] == "Geometry"), None)
    gid = g[1][0]
    V = np.array(sub(g, "Vertices")[1][0]).reshape(-1, 3)
    # áp transform của node mesh (Lcl T/R/S + pivot + Geometric*); trước đây bỏ qua → zom1 Items/Bloods lệch 3,58 cm
    V = (model_matrix(mo) @ np.c_[V, np.ones(len(V))].T).T[:, :3]
    P = sub(g, "PolygonVertexIndex")[1][0]
    tris, poly = [], []
    for i in P:
        if i < 0: poly.append(~i); 
        else: poly.append(i); continue
        for k in range(1, len(poly) - 1): tris.append([poly[0], poly[k], poly[k + 1]])
        poly = []
    # skin weights
    W = {}
    skin = next((s for s, gg in geom_of_skin.items() if gg == gid), None)
    for c, s in skin_of_cluster.items():
        if s != skin or c not in bone_of_cluster: continue
        ix, wt = sub(clusters[c], "Indexes"), sub(clusters[c], "Weights")
        if ix is None: continue
        W[nm(bones[bone_of_cluster[c]][1][1])] = [ix[1][0], wt[1][0]]
    meshout.append(dict(name=nm(mo[1][1]), verts=np.round(V, 4).flatten().tolist(), tris=np.array(tris).flatten().tolist(), weights=W))
    print(nm(mo[1][1]), len(V), "verts", len(tris), "tris", len(W), "weighted bones, bbox", V.min(0).round(1), V.max(0).round(1))
json.dump(skel, open(os.path.join(out, "ref_skeleton.json"), "w"))
json.dump(meshout, open(os.path.join(out, "ref_mesh.json"), "w"))
print(len(skel), "bones")
for s in skel: print(s["name"], "<-", s["parent"], None if s["bind_pos"] is None else np.round(s["bind_pos"], 1).tolist())
