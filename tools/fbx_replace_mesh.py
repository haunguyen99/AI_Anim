# Thay hình + skin của mesh trong FBX binary bằng mesh lấy từ FBX khác; mọi thứ còn lại giữ nguyên từng byte.
# Giữ: Model (tên, transform, cha), Geometry id, Skin, Cluster (bone, Transform, TransformLink), bind pose, material.
# Đổi:  Vertices, PolygonVertexIndex, Edges, Normals(+W), UV, UVIndex của Geometry; Indexes + Weights của từng Cluster.
# Thư viện (dùng từ script riêng của từng việc, xem work/shoot_die_repeat/map3_props/replace_props.py); `--selftest` ghi lại file không đổi gì.
import os, struct, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import fbx_remove_mesh as F


class Fbx:
    def __init__(self, path):
        self.path = path
        self.raw = open(path, "rb").read()
        self.ver, self.hdr, self.top, self.foot, self.after = F.parse(self.raw)
        self.T = {n[0]: n for n in self.top}
        self.obj = {}
        for o in self.T["Objects"][3]:
            pr = F.props(o[2], o[1])
            self.obj[pr[0]] = (o, pr)
        self.conns = [F.props(k[2], k[1]) for k in self.T["Connections"][3]]

    def name(self, i): return self.obj[i][1][1].split("\x00")[0]
    def kind(self, i): return self.obj[i][0][0]

    def model(self, name):
        for i, (o, pr) in self.obj.items():
            if o[0] == "Model" and pr[2] == "Mesh" and self.name(i) == name: return i
        raise SystemExit("Không thấy mesh %s trong %s" % (name, self.path))

    def children(self, parent, kind):
        return [c[1] for c in self.conns if c[2] == parent and c[1] in self.obj and self.kind(c[1]) == kind]

    def geometry(self, model_id): return self.children(model_id, "Geometry")[0]

    def clusters(self, geo_id):
        """[(cluster_id, tên xương)] của skin gắn vào geometry."""
        out = []
        for s in self.children(geo_id, "Deformer"):
            for c in self.children(s, "Deformer"):
                bones = [self.name(x) for x in self.children(c, "Model")]
                out.append((c, bones[0] if bones else None))
        return out

    def props70(self, node_id):
        p70 = F.child(self.obj[node_id][0], "Properties70")
        return {F.props(p[2], p[1])[0]: list(F.props(p[2], p[1])[4:]) for p in (p70[3] if p70 else [])}

    def world(self, model_id):
        """Ma trận thế giới 4x4 của Model (Lcl T/R/S + pivot + offset + Geometric*, gộp cha là Model)."""
        pr = self.props70(model_id)
        g = lambda k, d: np.array(pr.get(k, d), float)
        z, one = [0, 0, 0], [1, 1, 1]
        Rp, Sp = g("RotationPivot", z), g("ScalingPivot", z)
        L = (_tr(g("Lcl Translation", z)) @ _tr(g("RotationOffset", z)) @ _tr(Rp) @ _rot(g("PreRotation", z))
             @ _rot(g("Lcl Rotation", z)) @ np.linalg.inv(_rot(g("PostRotation", z))) @ _tr(-Rp)
             @ _tr(g("ScalingOffset", z)) @ _tr(Sp) @ _sc(g("Lcl Scaling", one)) @ _tr(-Sp))
        G = _tr(g("GeometricTranslation", z)) @ _rot(g("GeometricRotation", z)) @ _sc(g("GeometricScaling", one))
        par = [p for p in self.children_of(model_id, "Model")]
        W = self.world(par[0]) if par else np.eye(4)
        return W @ L @ G

    def children_of(self, child, kind):
        return [c[2] for c in self.conns if c[1] == child and c[2] in self.obj and self.kind(c[2]) == kind]

    def save(self, path):
        open(path, "wb").write(F.serialize(self.ver, self.hdr, self.top, F.footer_info(self.raw, self.after), None))


def _rot(e):
    x, y, z = np.radians(e)
    Rx = np.array([[1, 0, 0], [0, np.cos(x), -np.sin(x)], [0, np.sin(x), np.cos(x)]])
    Ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    Rz = np.array([[np.cos(z), -np.sin(z), 0], [np.sin(z), np.cos(z), 0], [0, 0, 1]])
    M = np.eye(4); M[:3, :3] = Rz @ Ry @ Rx; return M
def _tr(v):
    M = np.eye(4); M[:3, 3] = v; return M
def _sc(v): return np.diag([v[0], v[1], v[2], 1.0])


def arr_raw(kind, values):
    """Thuộc tính mảng 'd' (double) hoặc 'i' (int32), không nén."""
    dt = {"d": "<f8", "i": "<i4"}[kind]
    data = np.asarray(values, dtype=dt).tobytes()
    return kind.encode() + struct.pack("<III", len(data) // np.dtype(dt).itemsize, 0, len(data)) + data


def set_arr(parent, name, kind, values):
    n = F.child(parent, name)
    if n is None: raise SystemExit("Thiếu node %s" % name)
    n[2] = arr_raw(kind, values)


def geo_data(fbx, geo_id):
    """Đọc mesh nguồn: đỉnh (model space), chỉ số đa giác, cạnh, normal đã mở thành mỗi-đỉnh-đa-giác, UV."""
    g = fbx.obj[geo_id][0]
    gp = lambda n: F.props(F.child(g, n)[2], F.child(g, n)[1])[0]
    V = np.array(gp("Vertices"), float).reshape(-1, 3)
    P = np.array(gp("PolygonVertexIndex"), int)
    E = np.array(gp("Edges"), int) if F.child(g, "Edges") else np.zeros(0, int)
    ln = F.child(g, "LayerElementNormal")
    lp = lambda node, n: F.props(F.child(node, n)[2], F.child(node, n)[1])[0]
    N = np.array(lp(ln, "Normals"), float).reshape(-1, 3)
    if F.child(ln, "NormalsIndex"): N = N[np.array(lp(ln, "NormalsIndex"), int)]
    assert len(N) == len(P), "normal không theo đỉnh-đa-giác"
    lu = F.child(g, "LayerElementUV")
    UV = np.array(lp(lu, "UV"), float)
    UVI = np.array(lp(lu, "UVIndex"), int)
    out = dict(V=V, P=P, E=E, N=N, UV=UV, UVI=UVI)
    lc = F.child(g, "LayerElementColor")
    if lc is not None:   # màu đỉnh: mỗi màu 4 số (RGBA), chỉ số theo đỉnh-đa-giác
        cols = np.array(lp(lc, "Colors"), float).reshape(-1, 4)
        ci = np.array(lp(lc, "ColorIndex"), int) if F.child(lc, "ColorIndex") else np.arange(len(P))
        out["C"] = cols[ci]
    return out


def clean_mesh(d, tol=1e-7):
    """Bỏ đỉnh trùng vị trí liền kề trong cùng đa giác (tứ giác 'thật ra là tam giác' bị Unity báo self-intersecting
    và xóa), rồi bỏ đỉnh không còn đa giác nào dùng. Sửa d tại chỗ; trả về (số polyvertex bỏ, số đỉnh bỏ, map đỉnh cũ→mới, -1 = bỏ)."""
    V, P = d["V"], d["P"]
    polys, cur = [], []
    for pos, i in enumerate(P):
        cur.append((pos, int(~i) if i < 0 else int(i)))
        if i < 0: polys.append(cur); cur = []
    keep = []
    for poly in polys:
        k = list(poly)
        changed = True
        while changed and len(k) > 3:
            changed = False
            for j in range(len(k)):
                a, b = k[j][1], k[(j + 1) % len(k)][1]
                if a == b or np.linalg.norm(V[a] - V[b]) < tol:
                    del k[(j + 1) % len(k)]; changed = True; break
        keep.append(k)
    dropped = len(P) - sum(len(k) for k in keep)
    newpos = {}
    P2, order = [], []
    for k in keep:
        for n, (pos, vi) in enumerate(k):
            newpos[pos] = len(P2); order.append(pos)
            P2.append(~vi if n == len(k) - 1 else vi)
    d["N"] = d["N"][order]; d["UVI"] = d["UVI"][order]
    if "C" in d: d["C"] = d["C"][order]
    d["E"] = np.array([newpos[e] for e in d["E"] if e in newpos], int)
    used = sorted({int(~i) if i < 0 else int(i) for i in P2})
    vmap = np.full(len(V), -1, int); vmap[used] = np.arange(len(used))
    d["V"] = V[used]
    d["P"] = np.array([(~vmap[~i] if i < 0 else vmap[i]) for i in P2], int)
    return dropped, len(V) - len(used), vmap


def replace_mesh(dst, dst_model_id, new, weights):
    """Ghi mesh `new` (dict như geo_data, đỉnh đã ở model space của dst) vào Geometry của dst_model_id.
    weights: {tên xương: (mảng chỉ số đỉnh, mảng trọng số)}; xương có cluster trong dst mà không có đỉnh thì báo lỗi."""
    gid = dst.geometry(dst_model_id)
    g = dst.obj[gid][0]
    set_arr(g, "Vertices", "d", new["V"].flatten())
    set_arr(g, "PolygonVertexIndex", "i", new["P"])
    if F.child(g, "Edges"): set_arr(g, "Edges", "i", new["E"])
    ln = F.child(g, "LayerElementNormal")
    ref = F.props(F.child(ln, "ReferenceInformationType")[2], 1)[0]
    if ref == "Direct":
        set_arr(ln, "Normals", "d", new["N"].flatten())
    else:   # IndexToDirect: ghi các normal khác nhau + chỉ số
        uq, inv = np.unique(np.round(new["N"], 7), axis=0, return_inverse=True)
        set_arr(ln, "Normals", "d", uq.flatten()); set_arr(ln, "NormalsIndex", "i", inv.reshape(-1))
    if F.child(ln, "NormalsW"): set_arr(ln, "NormalsW", "d", np.ones(len(new["P"])))
    lc = F.child(g, "LayerElementColor")
    if lc is not None:
        if "C" not in new: raise SystemExit("Đích có màu đỉnh mà mesh nguồn không có")
        uq, inv = np.unique(np.round(new["C"], 7), axis=0, return_inverse=True)
        set_arr(lc, "Colors", "d", uq.flatten()); set_arr(lc, "ColorIndex", "i", inv.reshape(-1))
    lu = F.child(g, "LayerElementUV")
    set_arr(lu, "UV", "d", new["UV"]); set_arr(lu, "UVIndex", "i", new["UVI"])
    done = set()
    for cid, bone in dst.clusters(gid):
        c = dst.obj[cid][0]
        if bone not in weights or len(weights[bone][0]) == 0:
            # xương không còn đỉnh nào: bỏ Indexes/Weights, đúng dạng cluster rỗng của chính file (vd. mũi tên chỉ bám một xương)
            c[3] = [k for k in c[3] if k[0] not in ("Indexes", "Weights")]
            continue
        if F.child(c, "Indexes") is None: raise SystemExit("Cluster %s rỗng sẵn nhưng mesh mới cần xương này" % bone)
        set_arr(c, "Indexes", "i", weights[bone][0]); set_arr(c, "Weights", "d", weights[bone][1])
        done.add(bone)
    extra = set(weights) - done
    if extra: raise SystemExit("Mesh đích không có cluster cho xương: %s" % sorted(extra))


def islands(nverts, P):
    """Các khối rời (danh sách chỉ số đỉnh), từ PolygonVertexIndex (~i đánh dấu đỉnh cuối đa giác)."""
    par = list(range(nverts))
    def f(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    poly = []
    for i in P:
        poly.append(int(~i) if i < 0 else int(i))
        if i < 0:
            for k in poly[1:]: par[f(k)] = f(poly[0])
            poly = []
    g = {}
    for i in range(nverts): g.setdefault(f(i), []).append(i)
    return sorted(g.values(), key=lambda v: (-len(v), v[0]))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) == 3 and sys.argv[1] == "--selftest":
        f = Fbx(sys.argv[2]); tmp = sys.argv[2] + ".selftest.tmp"
        f.save(tmp); same = open(tmp, "rb").read() == f.raw; os.remove(tmp)
        print("selftest", "TRÙNG BYTE" if same else "KHÁC")
    else:
        print(__doc__)
