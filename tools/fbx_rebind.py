# Rebind: đưa mesh MỚI (model tĩnh của 3D, chỉ mesh) vào FBX rig CŨ đang chạy trong game, một lệnh.
# Giữ file rig (xương, tên, cây, bind pose, anim, material: từng byte), chỉ thay hình + UV + skin từng mesh (fbx_replace_mesh).
#
#   .venv\Scripts\python.exe -I tools\fbx_rebind.py <rig> <model> <thư mục ra> [tuỳ chọn]
#     <rig>, <model>: đường dẫn, hoặc "git:REV:đường/dẫn/trong/repo/Unity" (vd git:1a686d894:Assets/_Game/3D/Model/Pirate/EN_zom1_map4.fbx).
#       File nằm trong repo Unity mà khác bản trên origin/<--branch> -> tự lấy bản origin (bản local hay cũ hơn bản 3D vừa đẩy).
#     --map CŨ=MỚI      ghép mesh khác tên (mặc định ghép theo tên)
#     --mode MESH=hard|blend   ép cách chuyển skin (mặc định: thử cả hai trên anim, chọn bản ít giãn/lật hơn)
#     --anims DIR --pattern 'Zombie_*'   anim để kiểm (mặc định Animations/Share/Zombie_*.fbx của G-DieLoop)
#     --unity DIR --branch TungNV_Dev
# Ra: <thư mục ra>/<tên rig>.fbx, src/ (bản gốc), report.md, look/{rest_cmp,anim_old,anim_new,closeup}.png
#
# Luật (rút từ zom2_map6 2026-11-03, zom1_map4 2026-11-04, xem .claude/skills/animation/knowledge/details/export.md):
# - Đặt: ICP đồng dạng mesh lớn nhất mới -> cũ. s≈1 và xoay≈0 -> dời thuần, y giữ chân chạm đất như cũ; không thì dùng ICP đủ.
# - Mesh cũ chỉ bám 1 xương (súng, dao) = prop: khớp cứng riêng (24 hướng trục + ICP), 100% xương đó.
# - Skin: đỉnh cũ gần nhất CÙNG BÊN trái/phải. "hard" = chép đúng 1 đỉnh (giữ ranh giới cứng của thân xương);
#   "blend" = đỉnh xa > 0,3 cm trộn 4 đỉnh theo 1/d² (vải). Theo khối rời: khối có bản cũ chỉ lấy từ chính mesh cũ đó,
#   khối mới hẳn lấy từ mọi mesh cũ; khối nhỏ < 14 cm (nút, khuy, vòng) = một trọng số chung.
# - KHÔNG thêm cluster: prefab Unity đã unpack giữ m_Bones = số cluster mỗi mesh. Khối cần xương mà mesh không có cluster
#   -> chuyển khối sang mesh có cluster đó; điền cluster rỗng sẵn thì được.
# - Kiểm trên mọi anim (mỗi 2 frame): giãn cạnh ≥ 2 cm (max tỉ lệ, số cạnh > 1,5×) + lật mặt (> 120°), CŨ vs MỚI.
import os, sys, argparse, itertools, subprocess, fnmatch, re, shutil
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")
import fbx_replace_mesh as R
import fbx_remove_mesh as F
import fbxanim

UNITY = r"E:\Horus\shot-die-repeat"
SHARE = "Assets/_Game/Animations/Share"


# ---------------------------------------------------------------- nguồn file
def git(*a, cwd=UNITY, binary=False):
    r = subprocess.run(["git", "-C", cwd] + list(a), capture_output=True)
    if r.returncode: raise SystemExit("git %s: %s" % (" ".join(a), r.stderr.decode("utf-8", "replace")))
    return r.stdout if binary else r.stdout.decode("utf-8").strip()


def fetch_src(spec, dst, unity, branch, log):
    """Chép file nguồn vào src/; git:REV:path lấy từ repo Unity; file trong repo khác origin -> lấy bản origin."""
    if spec.startswith("git:"):
        rev, path = spec[4:].split(":", 1)
        open(dst, "wb").write(git("show", "%s:%s" % (rev, path), cwd=unity, binary=True))
        log("- `%s` lấy từ commit %s" % (path, rev)); return dst, path
    ab = os.path.abspath(spec); ur = os.path.abspath(unity)
    rel = os.path.relpath(ab, ur).replace("\\", "/") if ab.lower().startswith(ur.lower()) else None
    if rel:
        try:
            git("fetch", "-q", "origin", branch, cwd=unity)
            ob = git("rev-parse", "origin/%s:%s" % (branch, rel), cwd=unity)
            lb = git("hash-object", ab, cwd=unity)
            if ob != lb:
                open(dst, "wb").write(git("show", "origin/%s:%s" % (branch, rel), cwd=unity, binary=True))
                log("- `%s`: bản trên máy KHÁC origin/%s -> dùng bản origin (%s)" % (rel, branch, ob[:8])); return dst, rel
        except SystemExit as e:
            log("- (không so được với origin: %s)" % str(e).strip()[:120])
    shutil.copyfile(ab, dst); log("- `%s` lấy file trên máy" % (rel or ab)); return dst, rel


# ---------------------------------------------------------------- hình học
def near(A, B, k=1):
    out_d = np.empty((len(B), k)); out_j = np.empty((len(B), k), int)
    for s in range(0, len(B), 512):
        d = np.linalg.norm(B[s:s + 512, None] - A[None], axis=2)
        j = np.argsort(d, axis=1)[:, :k]; out_j[s:s + 512] = j; out_d[s:s + 512] = np.take_along_axis(d, j, 1)
    return out_d, out_j


def icp(P0, Q, s=1.0, Rm=None, t=None, scale=True, n=60):
    Rm = np.eye(3) if Rm is None else Rm; t = np.zeros(3) if t is None else t
    for _ in range(n):
        P = s * (Rm @ P0.T).T + t; _, j = near(Q, P); Qm = Q[j[:, 0]]
        pc, qc = P.mean(0), Qm.mean(0); H = (P - pc).T @ (Qm - qc); U, S, Vt = np.linalg.svd(H)
        D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))]); dR = Vt.T @ D @ U.T
        ds = (S * np.diag(D)).sum() / ((P - pc) ** 2).sum() if scale else 1.0
        Rm = dR @ Rm; s *= ds; t = ds * (dR @ (t - pc)) + qc
    return s, Rm, t


def rot_deg(Rm): return float(np.degrees(np.arccos(np.clip((np.trace(Rm) - 1) / 2, -1, 1))))


def polys_of(P):
    out, cur = [], []
    for pos, i in enumerate(P):
        cur.append(pos)
        if i < 0: out.append(cur); cur = []
    return out


def tris_of(P):
    T = []
    for poly in polys_of(P):
        v = [P[q] if P[q] >= 0 else ~P[q] for q in poly]
        for k in range(1, len(v) - 1): T.append((v[0], v[k], v[k + 1]))
    return np.array(T, int)


def sub(d, vmask):
    """Phần mesh gồm các đa giác có mọi đỉnh trong vmask."""
    P = d["P"]; vid = lambda i: ~i if i < 0 else i
    keep = [p for p in polys_of(P) if all(vmask[vid(P[q])] for q in p)]
    order = [q for p in keep for q in p]
    vmap = np.full(len(vmask), -1, int); vmap[np.nonzero(vmask)[0]] = np.arange(vmask.sum())
    pmap = {q: n for n, q in enumerate(order)}
    out = dict(V=d["V"][vmask], P=np.array([(~vmap[~P[q]] if P[q] < 0 else vmap[P[q]]) for q in order], int),
               E=np.array([pmap[e] for e in d["E"] if e in pmap], int), N=d["N"][order], UV=d["UV"], UVI=d["UVI"][order])
    if "C" in d: out["C"] = d["C"][order]
    return out


def merge(a, b):
    nv, npv, nuv = len(a["V"]), len(a["P"]), len(a["UV"]) // 2
    out = dict(V=np.r_[a["V"], b["V"]], P=np.r_[a["P"], np.where(b["P"] < 0, b["P"] - nv, b["P"] + nv)],
               E=np.r_[a["E"], b["E"] + npv], N=np.r_[a["N"], b["N"]], UV=np.r_[a["UV"], b["UV"]], UVI=np.r_[a["UVI"], b["UVI"] + nuv])
    if "C" in a or "C" in b: out["C"] = np.r_[a["C"], b["C"]]
    return out


def side(V, eps=1.0): return np.where(V[:, 0] > eps, 1, np.where(V[:, 0] < -eps, -1, 0))


def transfer(Vn, Vo, Wo, mode, k=4):
    """Skin từ đỉnh cũ gần nhất cùng bên. mode hard: chép 1 đỉnh; blend: đỉnh xa > 0,3 cm trộn k đỉnh 1/d²."""
    sn, so = side(Vn), side(Vo, 0.5)
    Wn = np.zeros((len(Vn), Wo.shape[1])); d0 = np.zeros(len(Vn))
    for sg in (-1, 0, 1):
        m = sn == sg
        if not m.any(): continue
        pool = np.nonzero(so != -sg)[0] if sg else np.arange(len(Vo))
        dist, j = near(Vo[pool], Vn[m], k); j = pool[j]
        W = Wo[j[:, 0]].copy()
        if mode == "blend":
            far = dist[:, 0] > 0.3
            if far.any():
                w = 1.0 / (dist[far] ** 2 + 1e-6); w /= w.sum(1, keepdims=True)
                W[far] = np.einsum("nk,nkb->nb", w, Wo[j[far]])
        Wn[m] = W; d0[m] = dist[:, 0]
    return Wn, d0


def finish(Wn, P, Vw, rigid_max=14.0):
    Wn = Wn.copy(); nrig = 0
    for isl in R.islands(len(Vw), P):
        ix = np.array(sorted(isl))
        if np.linalg.norm(Vw[ix].max(0) - Vw[ix].min(0)) < rigid_max: Wn[ix] = Wn[ix].mean(0); nrig += 1
    order = np.argsort(-Wn, axis=1)
    np.put_along_axis(Wn, order[:, 4:], 0.0, axis=1)
    Wn[Wn < 1e-3] = 0.0
    Wn /= np.maximum(Wn.sum(1, keepdims=True), 1e-12)
    return Wn, nrig


def humanoid(rig, A):
    """Pose như Unity Humanoid: lấy góc xoay từ anim, độ dài xương của rig (Root_M lấy cả dời)."""
    P = rig.rest()
    for n, M in A.items():
        M = M.copy()
        if n != "Root_M": M[:3, 3] = rig.rest_pose[n][:3, 3]
        P[n] = M
    return P


# ---------------------------------------------------------------- kiểm biến dạng (LBS numpy, bind của rig cũ)
class Checker:
    def __init__(self, rig_path, anim_files, step=2):
        from rigpose import Rig
        self.rig = Rig(rig_path)
        self.frames = []   # (anim, frame, {bone: skin matrix})
        for path in anim_files:
            models, _ = fbxanim.load(path)
            by = {m["name"]: m for m in models.values() if m["type"] == "LimbNode"}
            last = int(max(fbxanim.key_times(models)))
            for f in range(0, last + 1, step):
                P = humanoid(self.rig, {n: fbxanim.local(by[n], f / 30.0) for n in by if n in self.rig.rest_pose})
                W = self.rig.world(P)
                self.frames.append((os.path.basename(path)[:-4], f, {n: W[n] @ self.rig.bind_inv[n] for n in W}))

    def scan(self, V, W, bones, T):
        """V world rest (n,3), W (n,nb). Trả {anim: (max giãn, frame, số cạnh >1.5, số lật max, frame lật, tâm vùng)}."""
        E = np.unique(np.sort(np.r_[T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]], 1), axis=0)
        L0 = np.linalg.norm(V[E[:, 0]] - V[E[:, 1]], axis=1); ok = L0 > 2.0
        N0 = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]); okt = np.linalg.norm(N0, axis=1) > 1e-6
        dom = W.argmax(1)[T[:, 0]]
        Vh = np.c_[V, np.ones(len(V))]; out = {}
        for a, f, S in self.frames:
            M = np.stack([S.get(b, np.eye(4)) for b in bones])               # nb,4,4
            Vs = np.einsum("nb,bij,nj->ni", W, M, Vh)[:, :3]
            L = np.linalg.norm(Vs[E[:, 0]] - Vs[E[:, 1]], axis=1); r = np.where(ok, L / np.maximum(L0, 1e-9), 1.0)
            k = int(r.argmax()); nbad = int((ok & ((r > 1.5) | (r < 0.5))).sum())
            N = np.cross(Vs[T[:, 1]] - Vs[T[:, 0]], Vs[T[:, 2]] - Vs[T[:, 0]])
            Ex = np.einsum("nij,nj->ni", M[dom][:, :3, :3], N0)
            c = (N * Ex).sum(1) / (np.linalg.norm(N, axis=1) * np.linalg.norm(Ex, axis=1) + 1e-12)
            fl = np.nonzero(okt & (c < -0.5))[0]
            o = out.get(a, (0, 0, 0, -1, 0, None, None))
            st = (r[k], f, nbad, Vs[E[k, 0]]) if r[k] > o[0] else (o[0], o[1], o[2], o[5])
            fp = (len(fl), f, Vs[T[fl[0], 0]] if len(fl) else None) if len(fl) > o[3] else (o[3], o[4], o[6])
            out[a] = (st[0], st[1], st[2], fp[0], fp[1], st[3], fp[2])
        return out


def score(res): return sum(v[0] + 0.05 * v[2] + 0.1 * max(v[3], 0) for v in res.values())


# ---------------------------------------------------------------- chính
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rig"); ap.add_argument("model"); ap.add_argument("out")
    ap.add_argument("--map", action="append", default=[]); ap.add_argument("--mode", action="append", default=[])
    ap.add_argument("--anims", default=None); ap.add_argument("--pattern", default="Zombie_*")
    ap.add_argument("--unity", default=UNITY); ap.add_argument("--branch", default="TungNV_Dev")
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "src"), exist_ok=True); os.makedirs(os.path.join(a.out, "look"), exist_ok=True)
    rep = []; log = lambda s: (rep.append(s), print(s))
    log("# Rebind %s\n\n## Nguồn" % os.path.basename(a.rig.split(":")[-1]))
    rig_name = os.path.basename(a.rig.split(":")[-1])
    rig_path, rig_rel = fetch_src(a.rig, os.path.join(a.out, "src", "rig_" + rig_name), a.unity, a.branch, log)
    mdl_path, _ = fetch_src(a.model, os.path.join(a.out, "src", "model_" + os.path.basename(a.model.split(":")[-1])), a.unity, a.branch, log)
    out_fbx = os.path.join(a.out, rig_name)
    dst, src = R.Fbx(rig_path), R.Fbx(mdl_path)
    mesh_names = lambda f: [f.name(i) for i, (o, pr) in f.obj.items() if o[0] == "Model" and pr[2] == "Mesh"]
    old_names, new_names = mesh_names(dst), mesh_names(src)
    pairs = dict(m.split("=", 1) for m in a.map)
    for n in old_names:
        if n not in pairs and n in new_names: pairs[n] = n
    miss = [n for n in old_names if n not in pairs]
    if miss: raise SystemExit("Không ghép được mesh cũ %s; mesh mới có %s -> dùng --map CŨ=MỚI" % (miss, new_names))
    modes_forced = dict(m.split("=", 1) for m in a.mode)

    # ---- đọc mesh cũ (world cm, skin) + mesh mới (world, mét -> cm)
    old = {}
    for n in old_names:
        mid = dst.model(n); gid = dst.geometry(mid); d = R.geo_data(dst, gid); M = dst.world(mid)
        W = {}
        for cid, bone in dst.clusters(gid):
            ix = F.child(dst.obj[cid][0], "Indexes")
            if ix is None: continue
            wt = F.child(dst.obj[cid][0], "Weights")
            W[bone] = (np.array(F.props(ix[2], ix[1])[0], int), np.array(F.props(wt[2], wt[1])[0], float))
        old[n] = dict(mid=mid, M=M, V=(M[:3, :3] @ d["V"].T).T + M[:3, 3], W=W, P=d["P"],
                      clusters=[b for _, b in dst.clusters(gid)])
    unit = 100.0 if np.ptp(np.concatenate([R.geo_data(src, src.geometry(src.model(pairs[n])))["V"] for n in old_names]), 0).max() < 10 else 1.0
    new = {}
    for n in old_names:
        mid = src.model(pairs[n]); d = R.geo_data(src, src.geometry(mid)); M = src.world(mid)
        d["V"] = ((M[:3, :3] @ d["V"].T).T + M[:3, 3]) * unit; d["N"] = (M[:3, :3] @ d["N"].T).T
        dp, dv, _ = R.clean_mesh(d, tol=1e-5)
        if dp or dv: log("- dọn %s: bỏ %d polyvertex, %d đỉnh trùng" % (pairs[n], dp, dv))
        new[n] = d
    bones = sorted(set(b for n in old for b in old[n]["W"]))
    props = [n for n in old_names if len(old[n]["W"]) == 1]
    soft = [n for n in old_names if n not in props]
    body = max(soft, key=lambda n: len(old[n]["V"]))

    # ---- đặt
    log("\n## Đặt")
    Vb, Vob = new[body]["V"], old[body]["V"]
    t0 = (Vob.max(0) + Vob.min(0)) / 2 - (Vb.max(0) + Vb.min(0)) / 2
    s, Rm, t = icp(Vb, Vob, t=t0)
    log("- ICP đồng dạng `%s` mới→cũ: s=%.4f, xoay %.2f°, dời %s cm" % (body, s, rot_deg(Rm), t.round(2)))
    if abs(s - 1) < 0.01 and rot_deg(Rm) < 0.5:
        ground = min(old[n]["V"][:, 1].min() for n in soft) - min(new[n]["V"][:, 1].min() for n in soft)
        s, Rm, t = 1.0, np.eye(3), np.array([t[0], ground, t[2]])
        log("- s≈1, xoay≈0 -> dùng dời thuần %s (y giữ chân chạm đất như cũ)" % t.round(2))
    else:
        log("- dùng ICP đồng dạng (tỉ lệ / xoay khác rõ)")
    Vw = {}
    for n in soft:
        Vw[n] = s * (Rm @ new[n]["V"].T).T + t
        new[n]["N"] = (Rm @ new[n]["N"].T).T
        dd = near(old[n]["V"], Vw[n])[0][:, 0]
        log("- `%s`: %d đỉnh (cũ %d), tới mesh cũ TB %.2f, P95 %.2f, max %.2f cm" % (n, len(Vw[n]), len(old[n]["V"]), dd.mean(), np.percentile(dd, 95), dd.max()))
    for n in props:   # prop: khớp cứng riêng, 24 hướng trục
        Vo = old[n]["V"]; c0 = new[n]["V"].mean(0); best = None
        for perm in itertools.permutations(range(3)):
            for sg in itertools.product([1, -1], repeat=3):
                Q = np.zeros((3, 3))
                for r_, (c, g) in enumerate(zip(perm, sg)): Q[r_, c] = g
                if np.linalg.det(Q) < 0: continue
                tt = Vo.mean(0) - s * Q @ c0; Pp = s * (Q @ new[n]["V"].T).T + tt
                e = near(Vo, Pp)[0].mean() + near(Pp, Vo)[0].mean()
                if best is None or e < best[0]: best = (e, Q, tt)
        _, Rp, tp = icp(new[n]["V"], Vo, s=s, Rm=best[1], t=best[2], scale=False)
        Vw[n] = s * (Rp @ new[n]["V"].T).T + tp; new[n]["N"] = (Rp @ new[n]["N"].T).T
        dd = near(Vo, Vw[n])[0][:, 0]
        log("- prop `%s`: khớp cứng, tới prop cũ TB %.2f max %.2f cm, 100%% %s" % (n, dd.mean(), dd.max(), list(old[n]["W"])[0]))

    # ---- skin
    log("\n## Skin")
    dense = lambda n: (lambda Wm: [Wm.__setitem__((ix, bones.index(b)), w) for b, (ix, w) in old[n]["W"].items()] and Wm)(np.zeros((len(old[n]["V"]), len(bones))))
    Wold = {n: dense(n) for n in old_names}
    Vall = np.concatenate([old[n]["V"] for n in soft]); Wall = np.concatenate([Wold[n] for n in soft])
    anim_dir = a.anims or os.path.join(a.unity, SHARE)
    anim_files = sorted(os.path.join(anim_dir, f) for f in os.listdir(anim_dir) if f.endswith(".fbx") and fnmatch.fnmatch(f[:-4], a.pattern))
    log("- kiểm trên %d anim `%s/%s`" % (len(anim_files), anim_dir.replace("\\", "/").split("/Assets/")[-1], a.pattern))
    chk = Checker(rig_path, anim_files)

    def weights_for(n, mode):
        W, dist = transfer(Vw[n], old[n]["V"], Wold[n], mode)
        far = np.zeros(len(Vw[n]), bool)
        for isl in R.islands(len(Vw[n]), new[n]["P"]):
            ix = np.array(sorted(isl))
            if np.median(dist[ix]) > 2.5: far[ix] = True
        if far.any(): W[far] = transfer(Vw[n][far], Vall, Wall, "hard")[0]
        return W, far

    res_old = {n: chk.scan(old[n]["V"], Wold[n], bones, tris_of(old[n]["P"])) for n in soft}
    Wnew, farm, chosen, res_new = {}, {}, {}, {}
    for n in soft:
        cands = [modes_forced[n]] if n in modes_forced else ["hard", "blend"]
        best = None
        for mode in cands:
            W, far = weights_for(n, mode); Wf, _ = finish(W, new[n]["P"], Vw[n])
            r_ = chk.scan(Vw[n], Wf, bones, tris_of(new[n]["P"])); sc = score(r_)
            log("- `%s` thử %s: điểm %.1f (cũ %.1f)" % (n, mode, sc, score(res_old[n])))
            if best is None or sc < best[0]: best = (sc, mode, W, far)
        _, chosen[n], Wnew[n], farm[n] = best
        log("- `%s`: chọn **%s**%s; %d đỉnh thuộc khối mới hẳn lấy skin từ mọi mesh cũ" % (
            n, chosen[n], " (ép)" if n in modes_forced else "", farm[n].sum()))
    for n in props:
        Wnew[n] = np.zeros((len(Vw[n]), len(bones))); Wnew[n][:, bones.index(list(old[n]["W"])[0])] = 1.0; farm[n] = np.zeros(len(Vw[n]), bool)

    # khối cần xương mà mesh không có cluster -> chuyển sang mesh có
    for n in soft:
        have = set(old[n]["clusters"]); move = np.zeros(len(Vw[n]), bool); target = None
        for isl in R.islands(len(Vw[n]), new[n]["P"]):
            ix = np.array(sorted(isl))
            need = {bones[k] for k in np.nonzero(Wnew[n][ix].max(0) > 1e-3)[0]}
            if need <= have: continue
            homes = [m for m in soft if m != n and need <= set(old[m]["clusters"])]
            if not homes:
                log("- ⚠ khối %d đỉnh của `%s` cần %s, không mesh nào có cluster -> bỏ xương đó" % (len(ix), n, sorted(need - have)))
                for b in need - have: Wnew[n][ix, bones.index(b)] = 0.0
                continue
            move[ix] = True; target = homes[0]
            log("- khối %d đỉnh tại %s của `%s` cần %s (không có cluster) -> chuyển sang `%s`" % (
                len(ix), Vw[n][ix].mean(0).round(1), n, sorted(need - have), target))
        if move.any():
            new[target] = merge(new[target], sub(new[n], move)); Wnew[target] = np.r_[Wnew[target], Wnew[n][move]]
            Vw[target] = np.r_[Vw[target], Vw[n][move]]
            new[n] = sub(new[n], ~move); Wnew[n] = Wnew[n][~move]; Vw[n] = Vw[n][~move]

    # ---- ghi
    for n in old_names:
        Wf, nrig = finish(Wnew[n], new[n]["P"], Vw[n]) if n in soft else (Wnew[n], 0)
        Wnew[n] = Wf
        gid = dst.geometry(old[n]["mid"])
        for cid, b in dst.clusters(gid):
            c = dst.obj[cid][0]
            if b in bones and Wf[:, bones.index(b)].any() and F.child(c, "Indexes") is None:
                pos = [k[0] for k in c[3]].index("Transform")
                c[3][pos:pos] = [["Indexes", 1, R.arr_raw("i", [0]), [], False], ["Weights", 1, R.arr_raw("d", [0.0]), [], False]]
        Mi = np.linalg.inv(old[n]["M"]); d = new[n]
        d["V"] = (Mi[:3, :3] @ Vw[n].T).T + Mi[:3, 3]
        Nn = (Mi[:3, :3] @ d["N"].T).T; d["N"] = Nn / (np.linalg.norm(Nn, axis=1, keepdims=True) + 1e-12)
        w = {}
        for k, b in enumerate(bones):
            ix = np.nonzero(Wf[:, k])[0]
            if len(ix): w[b] = (ix, Wf[ix, k])
        R.replace_mesh(dst, old[n]["mid"], d, w)
        if nrig: log("- `%s`: %d khối nhỏ cứng" % (n, nrig))
    dst.save(out_fbx)
    # xác minh: mọi object ngoài Geometry/Deformer giữ nguyên, số cluster giữ nguyên
    import pickle
    A, B = R.Fbx(rig_path), R.Fbx(out_fbx)
    diff = [A.name(i) for i, (o, _) in A.obj.items() if o[0] not in ("Geometry", "Deformer") and (i not in B.obj or pickle.dumps(o) != pickle.dumps(B.obj[i][0]))]
    ncl = lambda f, n: len(f.clusters(f.geometry(f.model(n))))
    log("\n## File ra\n- `%s`" % out_fbx.replace("\\", "/"))
    log("- object ngoài mesh/skin khác bản cũ: %s; số object %d → %d; cluster %s" % (
        diff or "không", len(A.obj), len(B.obj), ", ".join("%s %d→%d" % (n, ncl(A, n), ncl(B, n)) for n in old_names)))

    # ---- bảng kiểm
    log("\n## Kiểm biến dạng (CŨ → MỚI): giãn max (frame, số cạnh >1,5×) | lật mặt max")
    worst = []
    for n in soft:
        rn = chk.scan(Vw[n], Wnew[n], bones, tris_of(new[n]["P"])); ro = res_old[n]; res_new[n] = rn
        log("\n**%s** (skin %s)\n\n| anim | giãn cũ | giãn mới | lật cũ | lật mới | |\n|---|---|---|---|---|---|" % (n, chosen[n]))
        for an in sorted(rn):
            o, w = ro[an], rn[an]
            flag = "⚠" if (w[0] > o[0] + 0.15 or w[3] > o[3] + 1) else ""
            log("| %s | %.2f (F%d, %d) | %.2f (F%d, %d) | %d | %d (F%d) | %s |" % (an, o[0], o[1] + 1, o[2], w[0], w[1] + 1, w[2], o[3], w[3], w[4] + 1, flag))
            worst.append((w[0] - o[0], an, w[1], w[5], n, "stretch"))
            if w[6] is not None: worst.append(((w[3] - o[3]) * 0.1, an, w[4], w[6], n, "flip"))
    nflag = sum(1 for l in rep if l.endswith("⚠ |"))
    log("\n**Tổng: %d dòng ⚠ (mới tệ hơn cũ: giãn +0,15 hoặc lật +2).** Lỗi có sẵn ở rig cũ không tính." % nflag)

    if not a.no_images:
        images(rig_path, out_fbx, a.out, anim_files, sorted(worst, key=lambda x: -x[0])[:4], soft, log)
    open(os.path.join(a.out, "report.md"), "w", encoding="utf-8").write("\n".join(rep) + "\n")
    prefab_check(a.unity, rig_rel, {n: ncl(B, n) for n in old_names}, log)
    open(os.path.join(a.out, "report.md"), "w", encoding="utf-8").write("\n".join(rep) + "\n")
    print("Ghi", os.path.join(a.out, "report.md"))


def images(old_fbx, new_fbx, out, anim_files, worst, soft, log):
    """Ảnh tự kiểm, chạy TUẦN TỰ (tên ảnh tạm riêng): rest 5 góc, anim 4 clip × 4 frame, cận ở frame tệ nhất."""
    from PIL import Image, ImageDraw
    from rigpose import Rig
    import render_fbx_tex as RT
    look = os.path.join(out, "look"); rigs = [("OLD", Rig(old_fbx)), ("NEW", Rig(new_fbx))]

    def pose(rig, path, f): return humanoid(rig, rig.frame_of(path, f))

    def screen(p, view):
        fwd = np.asarray(RT.VIEWS[view], float); up0 = np.array([0, 0, 1.0]) if abs(fwd[1]) > 0.9 else np.array([0, 1.0, 0])
        right = np.cross(fwd, up0); right /= np.linalg.norm(right); up = np.cross(right, fwd); return p @ right, p @ up

    def cell(rig, P, v, box, S):
        tmp = os.path.join(look, "_tmp_%d.png" % os.getpid()); rig.render(P, v, tmp, size=S, box=box)
        im = Image.open(tmp).copy(); os.remove(tmp); return im

    V5 = ["front", "back", "side_r", "side_l", "top"]; S = 420
    sh = Image.new("RGB", (S * 5, 2 * (S + 22)), "white"); d = ImageDraw.Draw(sh)
    for r, (lab, rig) in enumerate(rigs):
        for c, v in enumerate(V5):
            sh.paste(cell(rig, rig.rest(), v, (0, 95, 100) if v != "top" else (0, 0, 100), S), (c * S, r * (S + 22) + 22))
            d.text((c * S + 6, r * (S + 22) + 5), "%s rest %s" % (lab, v), fill="black")
    sh.save(os.path.join(look, "rest_cmp.png"))
    names = [os.path.basename(p)[:-4] for p in anim_files]
    pick = [n for n in ("Zombie_Walk01", "Zombie_HitBody01") if n in names] or names[:2]
    pick += [w[1] for w in worst if w[1] not in pick][:4 - len(pick)]
    for lab, rig in rigs:
        S = 360; sh = Image.new("RGB", (8 * S, len(pick) * (S + 20)), "white"); d = ImageDraw.Draw(sh)
        for r, an in enumerate(pick):
            path = anim_files[names.index(an)]; last = max(fbxanim.key_times(fbxanim.load(path)[0]))
            for k in range(4):
                f = int(round(k * last / 4)); P = pose(rig, path, f)
                for j, v in enumerate(("front", "side_r")):
                    sh.paste(cell(rig, P, v, (0, 95, 110), S), ((2 * k + j) * S, r * (S + 20) + 20))
                    d.text(((2 * k + j) * S + 6, r * (S + 20) + 4), "%s %s F%d %s" % (lab, an, f + 1, v), fill="black")
        sh.save(os.path.join(look, "anim_%s.png" % lab.lower()))
    S = 380; sh = Image.new("RGB", (4 * S, max(1, len(worst)) * (S + 20)), "white"); d = ImageDraw.Draw(sh)
    for r, (delta, an, f, p, mesh, kind) in enumerate(worst):
        path = anim_files[names.index(an)]; c = 0
        for lab, rig in rigs:
            P = pose(rig, path, f)
            for v in ("front", "side_r"):
                x, y = screen(np.asarray(p), v)
                sh.paste(cell(rig, P, v, (x, y, 28), S), (c * S, r * (S + 20) + 20))
                d.text((c * S + 6, r * (S + 20) + 4), "%s %s F%d %s (%s) %s" % (lab, an, f + 1, kind, mesh[-10:], v), fill="black"); c += 1
    sh.save(os.path.join(look, "closeup.png"))
    log("\n## Ảnh\n- `look/rest_cmp.png`, `look/anim_old.png`, `look/anim_new.png` (%s), `look/closeup.png` (vùng tệ nhất: %s)" % (
        ", ".join(pick), "; ".join("%s F%d %s %s" % (w[1], w[2] + 1, w[5], w[4]) for w in worst)))


def prefab_check(unity, rig_rel, ncl, log):
    """Prefab nào dùng rig này, m_Bones của từng SkinnedMeshRenderer có khớp số cluster không."""
    if not rig_rel: return
    meta = os.path.join(unity, rig_rel + ".meta")
    if not os.path.isfile(meta): return
    guid = re.search(r"guid: ([0-9a-f]+)", open(meta, encoding="utf-8").read()).group(1)
    log("\n## Prefab dùng rig này (guid %s)" % guid)
    root = os.path.join(unity, "Assets")
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith(".prefab"): continue
            t = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
            if guid not in t: continue
            rel = os.path.relpath(os.path.join(dp, f), unity).replace("\\", "/")
            for blk in t.split("--- !u!")[1:]:
                if not blk.startswith("137 ") or guid not in blk: continue
                nb = blk.split("m_Bones:")[1].split("m_BlendShapeWeights")[0].count("- {fileID") if "m_Bones:" in blk else -1
                log("- `%s`: SkinnedMeshRenderer %d xương (số cluster các mesh: %s)" % (rel, nb, ncl))


if __name__ == "__main__":
    main()
