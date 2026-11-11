"""Retarget anim Mixamo (hay FBX người khác) sang khung xương team (AdvancedSkeleton: Root_M, Hip_L, ...), không Blender.

Cách làm (xoay theo world):
  1. Đọc xương + anim nguồn, bind pose nguồn (BindPose trong file) và bind pose team (json world 4x4).
  2. Nắn bind team cho hướng từng đoạn xương trùng nguồn (cả hai T-pose thì gần như không đổi).
  3. Mỗi frame: world_team = world_nguồn(f) · bind_nguồn⁻¹ · bind_team_đã_nắn (xương có trong bảng nối).
     Xương không nối (Part1 xoắn, đốt ngón thừa, accessory) giữ local bind. Joint xoắn Part1 nhận một phần
     xoắn của xương con (mặc định 50%), giống rig team.
  4. Hông (Root_M) dời theo Hips nguồn × tỉ lệ chiều cao hông (chân ngắn/dài khác nguồn).
  5. Ghi vào một FBX team làm khuôn (giữ nguyên khung xương, PreRotation, RotationOrder), chỉ thay đường cong.

Chạy:
  .venv/Scripts/python.exe -I tools/retarget/retarget.py --src "Slow Run.fbx" --template MC_Lumber_Run.fbx \
      --bind work/g_lumbercity/base/worker_bind_world.json --out out.fbx [--map tools/retarget/maps/mixamo_advskel.json]
      [--fps 30] [--inplace] [--twist 0.5]
  .venv/Scripts/python.exe -I tools/retarget/retarget.py --selftest
"""
import argparse, json, os, struct, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import fbx_fast, fbxanim
import fbx_remove_mesh as FR
fbxanim.fbxread.read = fbx_fast.read
TICK = 46186158000  # FBX ticks / giây
ORD = fbxanim.ORDERS
AX = {"X": 0, "Y": 1, "Z": 2}


# ---------- toán xoay ----------
def euler_mat(r, order):
    return fbxanim.euler_xyz(r, order)


def euler_from(R, order, prev=None):
    """Ngược của fbxanim.euler_xyz: R = M[o2] M[o1] M[o0] (o0 áp trước). Trả độ, (x, y, z); chọn nghiệm gần prev."""
    o = ORD[int(order)]
    i, j, k = AX[o[0]], AX[o[1]], AX[o[2]]
    par = 1.0 if (i, j, k) in ((0, 1, 2), (1, 2, 0), (2, 0, 1)) else -1.0
    sb = -par * R[k, i]
    b = np.arcsin(np.clip(sb, -1, 1))
    if abs(sb) < 0.999999:
        a = np.arctan2(par * R[k, j], R[k, k])
        c = np.arctan2(par * R[j, i], R[i, i])
    else:  # gimbal: dồn vào a
        c = 0.0
        a = np.arctan2(-par * R[j, k], R[j, j])
    sols = [np.array([a, b, c]), np.array([a + np.pi, np.pi - b, c + np.pi])]
    out = []
    for s in sols:
        v = np.zeros(3); v[i], v[j], v[k] = s
        v = np.degrees(v)
        if prev is not None:
            v = prev + (v - prev + 180.0) % 360.0 - 180.0
        out.append(v)
    if prev is None:
        return min(out, key=lambda v: np.abs(v).sum())
    return min(out, key=lambda v: np.abs(v - prev).sum())


def rot_between(a, b):
    """Phép xoay nhỏ nhất đưa hướng a về hướng b."""
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    v = np.cross(a, b); c = float(np.dot(a, b)); s = np.linalg.norm(v)
    if s < 1e-9:
        if c > 0:
            return np.eye(3)
        p = np.cross(a, [1, 0, 0] if abs(a[0]) < 0.9 else [0, 1, 0]); p /= np.linalg.norm(p)
        return 2 * np.outer(p, p) - np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K * ((1 - c) / s ** 2)


def ortho(R):
    u, _, vt = np.linalg.svd(R)
    return u @ vt


def twist_about(R, axis):
    """Phần xoắn của R quanh trục (swing-twist), trả góc (rad)."""
    w = np.sqrt(max(0.0, 1 + np.trace(R))) / 2
    if w < 1e-6:
        return 0.0
    q = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (4 * w)
    p = np.dot(q, axis)
    return 2 * np.arctan2(p, w)


def axis_angle(axis, ang):
    axis = axis / np.linalg.norm(axis)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K


# ---------- đọc ----------
def short(n):
    return n.split(":")[-1]


def load_skel(path):
    models, par = fbxanim.load(path)
    names = {k: v["name"] for k, v in models.items()}
    byname = {v["name"]: k for k, v in models.items()}
    return models, par, names, byname


def bindpose(path, names):
    """BindPose trong file: tên → world 4x4."""
    _, top = fbx_fast.read(path)
    obj = [n for n in top if n[0] == "Objects"][0][2]
    out = {}
    for o in obj:
        if o[0] == "Pose" and len(o[1]) > 2 and o[1][2] == "BindPose":
            for pn in o[2]:
                if pn[0] != "PoseNode":
                    continue
                d = {k[0]: k[1] for k in pn[2]}
                nid = d["Node"][0]
                if nid in names:
                    out[names[nid]] = np.array(d["Matrix"][0], float).reshape(4, 4).T
    return out


def static_world(models, par):
    """Tư thế gốc từ giá trị tĩnh (Properties70) của từng xương, bỏ anim: dùng khi FBX không có BindPose
    (Mixamo tải 'Without Skin'). Mixamo ghi T-pose vào giá trị tĩnh."""
    def loc(m):
        g = lambda k, d: list(m["props"].get(k, d))[:3]
        pre = fbxanim.euler_xyz(g("PreRotation", [0, 0, 0])); post = fbxanim.euler_xyz(g("PostRotation", [0, 0, 0]))
        M = np.eye(4); M[:3, :3] = pre @ fbxanim.euler_xyz(g("Lcl Rotation", [0, 0, 0]), fbxanim.rot_order(m)) @ post.T @ np.diag(g("Lcl Scaling", [1, 1, 1]))
        M[:3, 3] = g("Lcl Translation", [0, 0, 0])
        return M
    W = {}

    def w(k):
        if k not in W:
            W[k] = (w(par[k]) @ loc(models[k])) if k in par and par[k] in models else loc(models[k])
        return W[k]
    return {models[k]["name"]: w(k) for k in models}


def world_at(models, par, sec):
    W = {}

    def w(k):
        if k in W:
            return W[k]
        L = fbxanim.local(models[k], sec)
        W[k] = (w(par[k]) @ L) if k in par and par[k] in models else L
        return W[k]
    for k in models:
        w(k)
    return W


def src_frames(models):
    ts = set()
    for m in models.values():
        for chans in m.get("anim", {}).values():
            for t, _, _ in chans:
                ts.update(np.round(np.asarray(t) * 1e6).astype(np.int64).tolist())
    ts = sorted(ts)
    return np.array(ts) / 1e6


# ---------- retarget ----------
def retarget(src, template, bind_json, mp, fps=30, inplace=False, twist=0.5, hip_scale=None, align=True, leg_ik=True, leg_scale=None, log=print):
    S, Spar, Snm, Sby = load_skel(src)
    T, Tpar, Tnm, Tby = load_skel(template)
    sbind = bindpose(src, Snm)
    if not sbind:
        sbind = static_world(S, Spar)
        log("nguồn không có BindPose: lấy tư thế gốc từ giá trị tĩnh của xương")
    tbind = {k: np.array(v, float) for k, v in json.load(open(bind_json, encoding="utf-8")).items()}
    bones = mp["bones"]  # team → nguồn (tên ngắn, không "mixamorig:")
    Sshort = {short(n): n for n in Sby}
    miss = [t for t, s in bones.items() if s not in Sshort or t not in Tby]
    if miss:
        log("bỏ qua (không có ở một bên): %s" % ", ".join(miss))
    bones = {t: s for t, s in bones.items() if t not in miss}
    for t, s in bones.items():
        if Sshort[s] not in sbind:
            raise SystemExit("Nguồn thiếu bind pose cho %s" % s)

    # thứ tự cha → con của team
    order = []

    def visit(k):
        order.append(k)
        for c in [c for c, p in Tpar.items() if p == k and c in T]:
            visit(c)
    for k in T:
        if k not in Tpar or Tpar[k] not in T:
            visit(k)
    tnames = [Tnm[k] for k in order]
    tparent = {Tnm[k]: Tnm[Tpar[k]] for k in order if k in Tpar and Tpar[k] in T}
    for n in tnames:
        if n not in tbind:
            # accessory/null không có trong bind json: dựng từ cha + local tĩnh của khuôn
            p = tparent.get(n)
            L = fbxanim.local(T[Tby[n]], -1e9)
            tbind[n] = (tbind[p] @ L) if p else L
    tbl = {n: (np.linalg.inv(tbind[tparent[n]]) @ tbind[n]) if n in tparent else tbind[n] for n in tnames}

    # 2. nắn bind team theo hướng xương nguồn
    chain_child = {}
    for t in bones:
        # con gần nhất (theo cây team) cũng có trong bảng nối
        best = None
        for c in tnames:
            p = tparent.get(c)
            d = 0
            while p is not None and p != t:
                p = tparent.get(p); d += 1
            if p == t and c in bones and (best is None or d < best[1]):
                if c in mp.get("chain_child", {}).get(t, [c]):
                    best = (c, d)
        if t in mp.get("no_align", []) or not align:
            best = None
        if best:
            chain_child[t] = best[0]
    al = {}
    for n in tnames:
        p = tparent.get(n)
        W = (al[p] @ tbl[n]) if p else tbl[n].copy()
        if n in chain_child:
            c = chain_child[n]
            # vị trí con dưới pose đang nắn: đi theo local bind từ n xuống c
            path = [c]
            while tparent[path[-1]] != n:
                path.append(tparent[path[-1]])
            Wc = W.copy()
            for x in reversed(path):
                Wc = Wc @ tbl[x]
            dt = Wc[:3, 3] - W[:3, 3]
            sb, sc = sbind[Sshort[bones[n]]], sbind[Sshort[bones[c]]]
            ds = sc[:3, 3] - sb[:3, 3]
            Q = rot_between(dt, ds)
            W[:3, :3] = Q @ W[:3, :3]
        al[n] = W
    align_deg = {n: np.degrees(np.arccos(np.clip((np.trace(al[n][:3, :3].T @ tbind[n][:3, :3]) - 1) / 2, -1, 1))) for n in bones}
    log("nắn bind team theo nguồn (độ): " + ", ".join("%s %.1f" % (n, a) for n, a in align_deg.items() if a > 1.0))
    alL = {n: (np.linalg.inv(al[tparent[n]]) @ al[n]) if n in tparent else al[n] for n in tnames}
    off = {t: np.linalg.inv(sbind[Sshort[s]][:3, :3]) @ al[t][:3, :3] for t, s in bones.items()}

    # 4. tỉ lệ hông
    hips_s = Sshort[mp["hips"][1]]; hips_t = mp["hips"][0]
    lt = [x for x in mp.get("leg_height", [])]
    if hip_scale is None:
        hs = sbind[Sshort[lt[1]]][1, 3] if lt else sbind[hips_s][1, 3]
        ht = tbind[lt[0]][1, 3] if lt else tbind[hips_t][1, 3]
        hip_scale = ht / hs
    log("tỉ lệ dời hông: %.3f" % hip_scale)

    secs = src_frames(S)
    if len(secs) == 0:
        raise SystemExit("Nguồn không có anim")
    nfr = int(round((secs[-1] - secs[0]) * fps)) + 1
    times = secs[0] + np.arange(nfr) / fps
    twist_pairs = mp.get("twist", {})  # joint Part1 → xương con mang xoắn
    legs = [tuple(x) for x in mp.get("legs", [])] if leg_ik else []
    leg_ratio = {}
    for th, kn, an in legs:
        tl = np.linalg.norm(tbind[kn][:3, 3] - tbind[th][:3, 3]) + np.linalg.norm(tbind[an][:3, 3] - tbind[kn][:3, 3])
        s3 = [sbind[Sshort[bones[x]]][:3, 3] for x in (th, kn, an)]
        leg_ratio[th] = leg_scale or tl / (np.linalg.norm(s3[1] - s3[0]) + np.linalg.norm(s3[2] - s3[1]))
    if legs:
        log("IK chân, tỉ lệ dài chân: " + ", ".join("%s %.3f" % kv for kv in leg_ratio.items()))
    frames = []
    hips0 = None
    for sec in times:
        Ws = world_at(S, Spar, sec)
        Wsn = {Snm[k]: v for k, v in Ws.items()}
        hp = Wsn[hips_s][:3, 3]
        if hips0 is None:
            hips0 = sbind[hips_s][:3, 3].copy()
        Rw = {n: ortho(Wsn[Sshort[bones[n]]][:3, :3] @ off[n]) for n in bones}
        hipW = al[hips_t][:3, 3] + (hp - hips0) * hip_scale
        if inplace:
            hipW[0] = al[hips_t][0, 3]; hipW[2] = al[hips_t][2, 3]

        def build():
            Wt = {}
            for n in tnames:
                p = tparent.get(n)
                if n in bones:
                    W = np.eye(4); W[:3, :3] = Rw[n]
                    W[:3, 3] = hipW if n == hips_t else (Wt[p] @ alL[n])[:3, 3]
                else:
                    W = (Wt[p] @ alL[n]) if p else alL[n].copy()
                Wt[n] = W
            return Wt
        Wt = build()
        # IK chân: cổ chân bám vị trí nguồn theo tỉ lệ dài chân, gối theo mặt phẳng gối nguồn, hướng bàn chân giữ FK
        for th, kn, an in legs:
            sh = Wsn[Sshort[bones[th]]][:3, 3]; sk = Wsn[Sshort[bones[kn]]][:3, 3]; sa = Wsn[Sshort[bones[an]]][:3, 3]
            H = Wt[th][:3, 3]
            l1 = np.linalg.norm(Wt[kn][:3, 3] - H); l2 = np.linalg.norm(Wt[an][:3, 3] - Wt[kn][:3, 3])
            A = H + (sa - sh) * leg_ratio[th]
            # độ cao cổ chân tính từ sàn (không theo hông): chạm sàn đúng như nguồn, không lún / bay
            A[1] = tbind[an][1, 3] + (sa[1] - sbind[Sshort[bones[an]]][1, 3]) * leg_ratio[th]
            d = A - H; dist = np.linalg.norm(d)
            if dist > 0.999 * (l1 + l2):
                A = H + d / dist * 0.999 * (l1 + l2); d = A - H; dist = np.linalg.norm(d)
            u = d / dist
            pole = (sk - sh) - np.dot(sk - sh, (sa - sh) / np.linalg.norm(sa - sh)) * (sa - sh) / np.linalg.norm(sa - sh)
            pole = pole - np.dot(pole, u) * u
            if np.linalg.norm(pole) < 1e-6:
                pole = (Wt[kn][:3, 3] - H) - np.dot(Wt[kn][:3, 3] - H, u) * u
            pole /= np.linalg.norm(pole)
            x = (l1 ** 2 - l2 ** 2 + dist ** 2) / (2 * dist)
            K = H + u * x + pole * np.sqrt(max(l1 ** 2 - x ** 2, 0.0))
            Rw[th] = rot_between(Wt[kn][:3, 3] - H, K - H) @ Rw[th]
            Wt = build()
            Rw[kn] = rot_between(Wt[an][:3, 3] - Wt[kn][:3, 3], A - Wt[kn][:3, 3]) @ Rw[kn]
            Wt = build()
        # local
        L = {n: (np.linalg.inv(Wt[tparent[n]]) @ Wt[n]) if n in tparent else Wt[n] for n in tnames}
        # chia xoắn: Part1 nhận twist*xoắn của con (quanh trục xương), con giữ phần còn lại
        for part, child in twist_pairs.items():
            if part not in L or child not in L:
                continue
            Lc = L[child][:3, :3]; Lr = alL[child][:3, :3]
            D = Lr.T @ Lc  # xoay thêm so với bind, trong hệ của bind con
            axis = alL[child][:3, 3] / (np.linalg.norm(alL[child][:3, 3]) + 1e-12)
            axis_c = Lr.T @ axis
            ang = twist_about(D, axis_c) * twist
            Tw = axis_angle(axis, ang)  # trong hệ của Part1
            L[part][:3, :3] = L[part][:3, :3] @ Tw
            L[child][:3, :3] = Tw.T @ L[child][:3, :3]
            L[child][:3, 3] = Tw.T @ L[child][:3, 3]
        frames.append(L)
    return dict(names=tnames, parent=tparent, frames=frames, fps=fps, T=T, Tby=Tby, nfr=nfr, hip_scale=hip_scale)


# ---------- ghi ----------
def _arr(t, a):
    a = np.ascontiguousarray(a, {"l": "<i8", "f": "<f4", "i": "<i4", "d": "<f8"}[t])
    data = a.tobytes()
    return t.encode() + struct.pack("<III", len(a), 0, len(data)) + data


def write(res, template, out):
    b = open(template, "rb").read()
    ver, hdr, top, footer, after = FR.parse(b)
    TT = {n[0]: n for n in top}
    objs = TT["Objects"][3]
    info = {}
    for o in objs:
        pr = FR.props(o[2], o[1])
        info[pr[0]] = (o, pr)
    conns = [FR.props(k[2], k[1]) for k in TT["Connections"][3]]
    cnode_of = {}  # model id → {prop: curvenode id}
    curves = {}  # curvenode id → {d|X: curve id}
    for c in conns:
        if c[0] == "OP" and c[1] in info and info[c[1]][0][0] == "AnimationCurveNode" and c[2] in info and info[c[2]][0][0] == "Model":
            cnode_of.setdefault(c[2], {})[c[3]] = c[1]
        if c[0] == "OP" and c[1] in info and info[c[1]][0][0] == "AnimationCurve" and c[2] in info:
            curves.setdefault(c[2], {})[c[3]] = c[1]
    T, Tby, fps, nfr = res["T"], res["Tby"], res["fps"], res["nfr"]
    keyt = (np.arange(nfr) * (TICK // fps)).astype(np.int64)
    done = set()
    for n in res["names"]:
        mid = Tby[n]; m = T[mid]
        ro = fbxanim.rot_order(m)
        pre = euler_mat(m["props"].get("PreRotation", [0, 0, 0])[:3], 0)
        post = euler_mat(m["props"].get("PostRotation", [0, 0, 0])[:3], 0)
        rv, tv, prev = [], [], None
        for L in res["frames"]:
            E = pre.T @ L[n][:3, :3] @ post
            prev = euler_from(E, ro, prev); rv.append(prev); tv.append(L[n][:3, 3])
        rv, tv = np.array(rv), np.array(tv)
        vals = {"Lcl Rotation": rv, "Lcl Translation": tv, "Lcl Scaling": np.ones((nfr, 3))}
        for prop, cn in cnode_of.get(mid, {}).items():
            if prop not in vals:
                continue
            for ax_i, ax in enumerate(("d|X", "d|Y", "d|Z")):
                cid = curves.get(cn, {}).get(ax)
                if cid is None:
                    continue
                set_curve(info[cid][0], keyt, vals[prop][:, ax_i])
                done.add(cid)
    # mọi đường cong còn lại (vật thể phụ): giữ giá trị frame đầu, đủ số key
    for cid, (o, pr) in info.items():
        if o[0] == "AnimationCurve" and cid not in done:
            kv = FR.props(FR.child(o, "KeyValueFloat")[2], 1)[0]
            set_curve(o, keyt, np.full(nfr, kv[0] if kv else 0.0))
    stop = int(keyt[-1])
    for o, pr in info.values():
        if o[0] == "AnimationStack":
            p70 = FR.child(o, "Properties70")
            if p70:
                for p in p70[3]:
                    q = FR.props(p[2], p[1])
                    if q[0] in ("LocalStop", "ReferenceStop"):
                        p[2] = p[2][:-8] + struct.pack("<q", stop)
    takes = TT.get("Takes")
    if takes:
        for tk in takes[3]:
            for q in tk[3]:
                if q[0] in ("LocalTime", "ReferenceTime"):
                    q[2] = b"L" + struct.pack("<q", 0) + b"L" + struct.pack("<q", stop)
    o = FR.serialize(ver, hdr, top, FR.footer_info(b, after), None)
    open(out, "wb").write(o)
    return len(done)


def set_curve(node, keyt, vals):
    n = len(keyt)
    for k in node[3]:
        if k[0] == "KeyTime":
            k[2] = _arr("l", keyt)
        elif k[0] == "KeyValueFloat":
            k[2] = _arr("f", vals)
        elif k[0] == "KeyAttrRefCount":
            k[2] = _arr("i", [n]); k[1] = 1
        elif k[0] == "KeyAttrFlags":
            fl = FR.props(k[2], 1)[0][:1] or [24840]
            k[2] = _arr("i", fl)
        elif k[0] == "KeyAttrDataFloat":
            d = FR.props(k[2], 1)[0][:4] or [0, 0, 0, 0]
            k[2] = _arr("f", d)
        elif k[0] == "Default":
            k[2] = b"D" + struct.pack("<d", float(vals[0]))


def selftest():
    rng = np.random.default_rng(1)
    worst = 0
    for o in range(6):
        for _ in range(300):
            r = rng.uniform(-180, 180, 3)
            M = euler_mat(r, o)
            e = euler_from(M, o)
            worst = max(worst, np.abs(euler_mat(e, o) - M).max())
    print("euler đi-về lệch tối đa:", worst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src"); ap.add_argument("--template"); ap.add_argument("--bind"); ap.add_argument("--out")
    ap.add_argument("--map", default=os.path.join(HERE, "maps", "mixamo_advskel.json"))
    ap.add_argument("--fps", type=int, default=30); ap.add_argument("--inplace", action="store_true")
    ap.add_argument("--twist", type=float, default=0.5); ap.add_argument("--hip-scale", type=float)
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--no-align", action="store_true"); ap.add_argument("--no-leg-ik", action="store_true"); ap.add_argument("--leg-scale", type=float)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    mp = json.load(open(a.map, encoding="utf-8"))
    dfl = mp.get("defaults", {})
    hs = a.hip_scale if a.hip_scale is not None else dfl.get("hip_scale")
    align = dfl.get("align", True) and not a.no_align
    res = retarget(a.src, a.template, a.bind, mp, a.fps, a.inplace, a.twist, hs, align, not a.no_leg_ik, a.leg_scale)
    n = write(res, a.template, a.out)
    print("ghi %s: %d frame, %d đường cong" % (a.out, res["nfr"], n))


if __name__ == "__main__":
    main()
