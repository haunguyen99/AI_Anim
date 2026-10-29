# Dựng lại xương khách (ref_<id>/ref_skeleton.json + ref_mesh.json) từ skin weights trong chars/<id>/mesh_cm.json,
# khi máy không có FBX gốc. Khớp = tâm vùng chuyển trọng số giữa xương và xương cha (vòng da ở chỗ gập);
# không có vùng chung thì lấy trung điểm các cạnh nối vùng của xương với vùng xương cha. Cha theo quy ước Advanced Skeleton.
# python work/rig_lab/skel_from_weights.py <id>
import json, os, re, sys
import numpy as np

R = os.path.dirname(os.path.abspath(__file__))

AS_PARENT = {"Spine1_M": "Root_M", "Chest_M": "Spine1_M", "Neck_M": "Chest_M", "Head_M": "Neck_M", "HeadEnd_M": "Head_M",
             "Hip": "Root_M", "Knee": "Hip", "Ankle": "Knee", "Toes": "Ankle", "ToesEnd": "Toes",
             "Scapula": "Chest_M", "Shoulder": "Scapula", "Elbow": "Shoulder", "Wrist": "Elbow", "Cup": "Wrist"}


def as_parent(n, names):
    if n in AS_PARENT:
        return AS_PARENT[n]
    m = re.match(r"^(\w+?)(\d*)_([RLM])$", n)
    if not m:
        return None
    base, i, side = m.groups()
    if base.endswith("Finger") and i:
        p = "Wrist_" + side if i == "1" else "%s%d_%s" % (base, int(i) - 1, side)
        if p == "Wrist_" + side and base in ("RingFinger", "PinkyFinger") and "Cup_" + side in names:
            p = "Cup_" + side
        return p
    if base in AS_PARENT:
        p = AS_PARENT[base]
        return p if p.endswith("_M") else p + "_" + side
    return None


def main(cid):
    C = json.load(open(f"{R}/chars/{cid}.json", encoding="utf8"))
    meshes = json.load(open(f"{R}/chars/{cid}/mesh_cm.json"))
    body = next(m for m in meshes if m["name"] == C["body"])
    if not body.get("weights"):
        raise SystemExit("mesh thân không có skin weights: không suy được xương")
    V = np.array(body["verts"]).reshape(-1, 3)
    T = np.array(body["tris"]).reshape(-1, 3)
    names = list(body["weights"])
    W = np.zeros((len(V), len(names)))
    for j, n in enumerate(names):
        ix, ws = body["weights"][n]
        W[ix, j] = ws
    W /= np.maximum(W.sum(1, keepdims=True), 1e-9)
    dom = W.argmax(1)
    col = {n: j for j, n in enumerate(names)}
    E = np.unique(np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), axis=1), axis=0)

    def adjacency(j):   # cha cho xương lạ: xương chung trọng số nhiều nhất, không có thì vùng chạm vùng của j nhiều nhất
        share = np.minimum(W[:, [j]], W).sum(0); share[j] = 0; share[col["Root_M"]] *= 0.5
        if share.max() > 1e-6:
            return names[int(share.argmax())]
        a, b = dom[E[:, 0]], dom[E[:, 1]]
        nb = np.concatenate([b[a == j], a[b == j]]); nb = nb[nb != j]
        if len(nb):
            return names[np.bincount(nb).argmax()]
        w = W[:, j]
        if w.max() > 0:   # vài đỉnh: lấy xương có trọng số lớn nhất ở đó
            o = W[w > 0].sum(0); o[j] = 0
            return names[int(o.argmax())]
        return None

    parent = {}
    for n in names:
        p = as_parent(n, names)
        parent[n] = p if p in col else (None if n == "Root_M" else adjacency(col[n]))

    def joint(n):
        j, p = col[n], parent[n]
        if p is None:
            return None
        k = col[p]
        w = np.minimum(W[:, j], W[:, k])
        if (w > 0.05).sum() >= 6:
            return (V * w[:, None]).sum(0) / w.sum()
        a, b = dom[E[:, 0]], dom[E[:, 1]]
        e = E[((a == j) & (b == k)) | ((a == k) & (b == j))]
        return V[e].mean((0, 1)) if len(e) else V[dom == j].mean(0) if (dom == j).any() else None

    pos = {n: joint(n) for n in names}
    # khớp cuối (ngón 4, ToesEnd) và xương lạ không có vùng chuyển: điểm xa nhất của vùng theo hướng cha → ông
    for n in names:
        if pos[n] is not None or parent[n] is None:
            continue
        p = parent[n]; pp = parent.get(p)
        reg = V[W[:, col[n]] > 0.3] if (W[:, col[n]] > 0.3).any() else V[W[:, col[p]] > 0.3]
        if pos.get(p) is not None and pp and pos.get(pp) is not None and len(reg):
            d = pos[p] - pos[pp]; d = d / (np.linalg.norm(d) or 1)
            far = reg[np.argmax((reg - pos[p]) @ d)]
            pos[n] = pos[p] + d * max(0.6 * np.linalg.norm(pos[p] - pos[pp]), (far - pos[p]) @ d * 0.6)
        elif len(reg):
            pos[n] = reg.mean(0)
    # Root_M: giữa hai khớp hông theo x,y; z theo vùng Root
    hips = [pos[h] for h in ("Hip_R", "Hip_L") if pos.get(h) is not None]
    rz = V[dom == col["Root_M"]][:, 2].mean() if (dom == col["Root_M"]).any() else 0
    if hips:
        pos["Root_M"] = np.array([0.0, float(np.mean([h[1] for h in hips])), float(rz)])
    # vai: vòng chuyển Scapula→Shoulder nằm ở mép trong giáp vai nên hay lệch ra sau; đặt z vào tâm mặt cắt tay ngay ngoài khớp
    for sd, sg in (("R", -1), ("L", 1)):
        n = "Shoulder_" + sd
        if pos.get(n) is not None:
            x = pos[n][0] + sg * 4
            sl = V[(np.abs(V[:, 0] - x) < 2.5) & (np.abs(V[:, 1] - pos[n][1]) < 25)]
            if len(sl) > 8:
                pos[n] = np.array([x, pos[n][1], (sl[:, 2].min() + sl[:, 2].max()) / 2])
    # đối xứng: trung bình R với gương L để hai bên khớp nhau
    for n in names:
        if n.endswith("_R") and n[:-1] + "L" in pos and pos[n] is not None and pos[n[:-1] + "L"] is not None:
            r, l = pos[n], pos[n[:-1] + "L"]
            m = (r + l * [-1, 1, 1]) / 2
            pos[n], pos[n[:-1] + "L"] = m, m * [-1, 1, 1]
    for n in ("Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M"):
        if pos.get(n) is not None:
            pos[n][0] = 0.0
    sc = C.get("scale", 1) or 1   # ref_* lưu theo đơn vị file; build_char.py nhân lại scale
    sk = [{"name": n, "parent": parent[n], "bind_pos": None if pos[n] is None else [round(float(v) / sc, 3) for v in pos[n]]} for n in names]
    order = {n: 0 for n in names}
    for n in names:   # cha trước con
        d, p = 0, parent[n]
        while p and d < 50:
            d += 1; p = parent.get(p)
        order[n] = d
    sk.sort(key=lambda s: order[s["name"]])
    ref = f"{R}/{C.get('ref_dir') or 'ref_' + cid}"
    os.makedirs(ref, exist_ok=True)
    json.dump(sk, open(f"{ref}/ref_skeleton.json", "w"), separators=(",", ":"))
    raw = [dict(m, verts=[round(v / sc, 4) for v in m["verts"]]) for m in meshes]
    json.dump(raw, open(f"{ref}/ref_mesh.json", "w"), separators=(",", ":"))
    print(len(sk), "bones ->", ref)
    return sk


if __name__ == "__main__":
    main(sys.argv[1])
