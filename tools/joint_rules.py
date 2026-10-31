"""Giới hạn khớp + liên động giữa các khớp (2026-10-31): để khi AI key một khớp thì các khớp liên quan cũng đi theo
(tay giơ lên đầu → bả vai nhún + xoay theo; thân cong → chia đều các đốt; cúi người → hông góp phần...).

Luật nằm trong JSON: tools/joint_rules/biped.json (mặc định) + joint_rules.json của job (ghi đè, chỉ khoá muốn đổi).
Mỗi luật liên động: driver (số đo khớp dẫn, vd góc giơ tay) → driven (khớp theo, vd độ nhún xương đòn) qua đường cong,
đo so với pose tham chiếu (P0 đã duyệt). Loại "share" = góc của một chuỗi chia theo tỉ lệ; "check" = chỉ báo.

    import rigpose as RP, joint_rules as JR
    rules = JR.load()                                # hoặc JR.load("work/<dự án>/<job>/joint_rules.json")
    rep = JR.audit(rig, P, rules, ref=P0)            # danh sách lỗi: khớp vượt giới hạn, khớp đứng yên khi lẽ ra phải theo
    info = JR.apply(rig, P, rules, ref=P0)           # sửa tại chỗ: bả vai / đốt sống / cổ theo, bàn tay giữ nguyên chỗ (IK)

CLI (soi cả clip FBX, frame đầu làm tham chiếu):
    python -I tools/joint_rules.py audit --rig RIG.fbx --anim ANIM.fbx [--ref-frame 0] [--rules job.json] [--fix]
        [--render F --view side_r --out dir]   (--fix: chạy apply từng frame, báo đã thêm bao nhiêu độ, sai lệch tay)
"""
import os, sys, json, argparse, copy
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rigpose as RP

DEFAULT = os.path.join(HERE, "joint_rules", "biped.json")


# ------------------------------------------------------------------ luật
def _merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items(): out[k] = _merge(a.get(k), v) if k in a else v
        return out
    return copy.deepcopy(b)

def load(job_file=None):
    """Luật mặc định + ghi đè của job. couplings ghi đè theo id ({"id": "scap_elev", "curve": ...}; "off": true = tắt)."""
    R = json.load(open(DEFAULT, encoding="utf-8"))
    if job_file and os.path.isfile(job_file):
        J = json.load(open(job_file, encoding="utf-8"))
        cps = {c["id"]: c for c in R["couplings"]}
        for c in J.pop("couplings", []):
            cps[c["id"]] = _merge(cps.get(c["id"], {}), c)
        R = _merge(R, J); R["couplings"] = [c for c in cps.values() if not c.get("off")]
    return R

def limit_of(R, n):
    d = R["limits"]["defaults"]
    if n in d: return d[n]
    b = n[:-2] if n[-2:] in ("_L", "_R") else n
    return d.get(b)


# ------------------------------------------------------------------ toán quay
def nrm3(M): return M / np.linalg.norm(M, axis=0)
def quat(R):          # (w, x, y, z)
    t = np.trace(R)
    if t > 0:
        s = np.sqrt(t + 1) * 2; return np.array([s / 4, (R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s])
    i = int(np.argmax([R[0, 0], R[1, 1], R[2, 2]])); j, k = (i + 1) % 3, (i + 2) % 3
    s = np.sqrt(1 + R[i, i] - R[j, j] - R[k, k]) * 2
    q = np.zeros(4); q[0] = (R[k, j] - R[j, k]) / s; q[1 + i] = s / 4
    q[1 + j] = (R[j, i] + R[i, j]) / s; q[1 + k] = (R[k, i] + R[i, k]) / s
    return q
def rot_angle(R): return float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
def slerp_I(R, t):    # quay một phần t của R (từ I)
    q = quat(R); q = q if q[0] >= 0 else -q
    a = 2 * np.arctan2(np.linalg.norm(q[1:]), q[0])
    if a < 1e-9: return np.eye(3)
    return RP.axis_angle(q[1:], np.degrees(a * t))

def decompose(Rrel):
    """Rrel = rest_local^T · local → (gập quanh Z, dạng quanh Y, xoắn quanh X dọc xương), độ. Rrel = swing · twist."""
    q = quat(Rrel); q = q if q[0] >= 0 else -q
    tw = 2 * np.degrees(np.arctan2(q[1], q[0])); tw = (tw + 180) % 360 - 180
    d = Rrel[:, 0]   # trục X (dọc xương) sau khi quay: swing không đổi nó bởi twist
    bend = np.degrees(np.arctan2(d[1], d[0])); spread = np.degrees(np.arctan2(-d[2], np.hypot(d[0], d[1])))
    return float(bend), float(spread), float(tw)

def compose(bend, spread, tw):
    b, s = np.radians(bend), np.radians(spread)
    d = np.array([np.cos(s) * np.cos(b), np.cos(s) * np.sin(b), -np.sin(s)])
    return RP.rot_between(np.array([1.0, 0, 0]), d) @ RP.axis_angle([1, 0, 0], tw)

def lrot(P, n): return nrm3(P[n][:3, :3].copy())
def set_lrot(P, n, R3):
    sc = np.linalg.norm(P[n][:3, :3], axis=0); P[n][:3, :3] = R3 @ np.diag(sc)


# ------------------------------------------------------------------ số đo
class Ctx:
    """Số đo một pose: khung ngực / hông theo rest, hướng tay, xương đòn."""
    def __init__(self, rig, P, R):
        self.rig, self.P, self.R = rig, P, R
        self.W = rig.world(P)
        if not hasattr(rig, "_jr_rest"):
            W0 = rig.world(rig.rest_pose); rig._jr_rest = {n: nrm3(M[:3, :3]) for n, M in W0.items()}
        self.W0 = rig._jr_rest
        F = R["frame"]; self.up0, self.fwd0, self.left0 = (np.array(F[k], float) for k in ("up", "fwd", "left"))
    def rw(self, n): return nrm3(self.W[n][:3, :3])
    def p(self, n): return self.W[n][:3, 3]
    def F(self, n): return self.rw(n) @ self.W0[n].T            # quay của xương so với rest (world)
    def axes(self, n="Chest_M"):
        F = self.F(n); return F @ self.up0, F @ self.fwd0, F @ self.left0
    def lat(self, s, n="Chest_M"):
        up, fwd, left = self.axes(n); return up, fwd, (-left if s == "R" else left)
    def arm(self, s):
        up, fwd, lat = self.lat(s)
        u = self.p("Elbow_" + s) - self.p("Shoulder_" + s); u /= np.linalg.norm(u)
        elev = RP.ang(u, -up); hflex = float(np.degrees(np.arctan2(u @ fwd, u @ lat)))
        return elev, hflex
    def clav(self, s):
        up, fwd, lat = self.lat(s)
        v = self.p("Shoulder_" + s) - self.p("Scapula_" + s); v /= np.linalg.norm(v)
        return float(np.degrees(np.arcsin(np.clip(v @ up, -1, 1)))), float(np.degrees(np.arctan2(v @ fwd, v @ lat)))
    def tilt(self, n):
        up, _, _ = self.axes(n); return RP.ang(up, self.up0)

def curve(c, x):
    xs, ys = zip(*c); return float(np.interp(x, xs, ys))
def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1); return float(t * t * (3 - 2 * t))

def expect(cp, C, s):
    """Giá trị driven mà luật mong đợi (tuyệt đối, chưa trừ ref)."""
    elev, hflex = C.arm(s)
    if cp["driver"] == "arm_elev": return curve(cp["curve"], elev)
    if cp["driver"] == "arm_hflex":
        w = smooth(elev, 20, 70) if cp.get("weight_by_elev") else 1.0
        return w * curve(cp["curve"], hflex)
    raise ValueError(cp["driver"])
def driven(cp, C, s):
    e, p = C.clav(s); return {"clav_elev": e, "clav_prot": p}[cp["driven"]]
def drv_val(cp, C, s):
    elev, hflex = C.arm(s); return elev if cp["driver"] == "arm_elev" else hflex

def chain_angles(rig, P, cp, ref):
    """góc mỗi đốt so với ref + tổng góc cả chuỗi (độ)."""
    base = ref if ref is not None else rig.rest_pose
    a = [rot_angle(lrot(base, n).T @ lrot(P, n)) for n in cp["chain"]]
    W, Wb = rig.world(P), rig.world(base)
    end = cp["chain"][-1]
    tot = rot_angle(nrm3(W[end][:3, :3]) @ nrm3(Wb[end][:3, :3]).T @ nrm3(Wb[cp["parent"]][:3, :3]) @ nrm3(W[cp["parent"]][:3, :3]).T)
    return a, tot


# ------------------------------------------------------------------ audit
def audit(rig, P, R, ref=None):
    """Lỗi của một pose: [{rule, joint, msg, value, want}]."""
    out, C = [], Ctx(rig, P, R)
    Cr = Ctx(rig, ref, R) if ref is not None else None
    # giới hạn khớp (so rest)
    for n in rig.order:
        lim = limit_of(R, n)
        if not lim or n not in rig.rest_pose: continue
        b, sp, tw = decompose(lrot(rig.rest_pose, n).T @ lrot(P, n))
        lim = widen(lim, rig, ref, n)
        for nm, v, lo, hi in (("gập", b, lim[0], lim[1]), ("dạng", sp, lim[2], lim[3]), ("xoắn", tw, lim[4], lim[5])):
            if v < lo - 0.5 or v > hi + 0.5:
                out.append({"rule": "limit", "joint": n, "msg": "%s %s %.0f° ngoài [%g, %g]" % (n, nm, v, lo, hi),
                            "value": round(v, 1), "want": [lo, hi], "fixable": n in R["limits"]["clamp"]})
    for cp in R["couplings"]:
        t = cp.get("type", "follow")
        if t == "follow":
            for s in cp.get("side", "LR"):
                if "Scapula_" + s not in rig.parent: continue
                want = expect(cp, C, s) - (expect(cp, Cr, s) if Cr else 0)
                got = driven(cp, C, s) - (driven(cp, Cr, s) if Cr else 0)
                if abs(want - got) > cp.get("tol", 5):
                    out.append({"rule": cp["id"], "joint": "Scapula_" + s, "value": round(got, 1), "want": round(want, 1), "fixable": cp.get("fix", False),
                                "msg": "%s: %s %.0f° → xương đòn nên %+.0f°, đang %+.0f°" % (cp["label"], cp["driver"], drv_val(cp, C, s), want, got)})
        elif t == "share":
            if not all(n in rig.parent for n in cp["chain"]): continue
            a, tot = chain_angles(rig, P, cp, ref)
            if tot < cp.get("min_total", 10) or sum(a) < 1e-6: continue
            sh = [x / sum(a) for x in a]; lo, hi = cp["band"]
            if any(x < lo or x > hi for x in sh):
                out.append({"rule": cp["id"], "joint": "/".join(cp["chain"]), "value": [round(x, 2) for x in sh], "want": cp["weights"], "fixable": cp.get("fix", False),
                            "msg": "%s: tổng %.0f°, chia %s (nên ~%s)" % (cp["label"], tot, "/".join("%d%%" % (100 * x) for x in sh), "/".join("%d%%" % (100 * w) for w in cp["weights"]))})
        elif t == "check" and cp["measure"] == "pelvis_share":
            tc = C.tilt("Chest_M") - (Cr.tilt("Chest_M") if Cr else 0); tp = C.tilt("Root_M") - (Cr.tilt("Root_M") if Cr else 0)
            if tc >= cp["when_total"] and tp / tc < cp["min"]:
                out.append({"rule": cp["id"], "joint": "Root_M", "value": round(tp / tc, 2), "want": cp["min"], "fixable": False,
                            "msg": "%s: ngực ngả %.0f°, hông chỉ %.0f° (%d%%, nên ≥ %d%%)" % (cp["label"], tc, tp, 100 * tp / tc, 100 * cp["min"])})
        elif t == "check" and cp["measure"] == "elbow_twist":
            for s in "LR":
                n = "Elbow_" + s
                if n not in rig.parent: continue
                tw = decompose(lrot(rig.rest_pose, n).T @ lrot(P, n))[2]
                tw0 = decompose(lrot(rig.rest_pose, n).T @ lrot(ref, n))[2] if ref is not None else 0
                d = (tw - tw0 + 180) % 360 - 180
                if abs(d) > cp["max"]:
                    out.append({"rule": cp["id"], "joint": n, "value": round(d, 1), "want": cp["max"], "fixable": False,
                                "msg": "%s: khuỷu %s xoắn %+.0f° so P0 (≤ %g)" % (cp["label"], s, d, cp["max"])})
    return out


# ------------------------------------------------------------------ apply
def _share_fix(rig, P, cp, ref):
    base = ref if ref is not None else rig.rest_pose
    W = rig.world(P); Wb = rig.world(base)
    Rp, Re = nrm3(W[cp["parent"]][:3, :3]), nrm3(W[cp["chain"][-1]][:3, :3])
    acc = Rp.copy(); parts = []
    for n in cp["chain"]:
        acc = acc @ lrot(base, n); parts.append(acc.copy())
    D = Re @ parts[-1].T
    c = 0
    for n, w, Rb in zip(cp["chain"], cp["weights"], parts):
        c += w; rig.set_world_rot(P, n, slerp_I(D, c) @ Rb)

def widen(lim, rig, ref, n, pad=2):
    """P0 đã duyệt vượt giới hạn (vd gối dạng −17° do IK rig team) thì giới hạn nới tới đó: chỉ bắt lỗi TỆ HƠN P0."""
    if ref is None: return lim
    v = decompose(lrot(rig.rest_pose, n).T @ lrot(ref, n)); L = list(lim)
    for i, x in enumerate(v):
        L[2 * i] = min(L[2 * i], x - pad); L[2 * i + 1] = max(L[2 * i + 1], x + pad)
    return L

def _clamp(rig, P, R, ref=None):
    for n in R["limits"]["clamp"]:
        lim = limit_of(R, n)
        if not lim or n not in P: continue
        lim = widen(lim, rig, ref, n)
        Lr = lrot(rig.rest_pose, n); b, sp, tw = decompose(Lr.T @ lrot(P, n))
        c = (np.clip(b, lim[0], lim[1]), np.clip(sp, lim[2], lim[3]), np.clip(tw, lim[4], lim[5]))
        if np.allclose(c, (b, sp, tw), atol=0.3): continue
        set_lrot(P, n, Lr @ compose(*c))

def _hands(rig, P):
    """Bàn tay cần giữ: world 4x4 cổ tay + hướng khuỷu (phần vuông góc trục vai→cổ tay)."""
    W = rig.world(P); out = {}
    for s in "LR":
        if "Wrist_" + s not in W: continue
        S, E, Wr = (W[k + s][:3, 3] for k in ("Shoulder_", "Elbow_", "Wrist_"))
        ax = (Wr - S) / np.linalg.norm(Wr - S); d = (E - S) - ((E - S) @ ax) * ax
        out[s] = (W["Wrist_" + s].copy(), d / max(np.linalg.norm(d), 1e-9))
    return out

def keep_hand(rig, P, s, Wt, pole_dir):
    """Đưa cổ tay về Wt sau khi gốc tay (bả vai) đã dời, KHÔNG giải IK lại từ đầu: (1) gập khuỷu quanh đúng trục bản lề
    đang có cho đủ khoảng vai→cổ tay, (2) xoay vai ngắn nhất về đích, (3) cuộn vai quanh trục vai→đích cho khuỷu chĩa như
    cũ, (4) trả hướng cổ tay. Giữ chiều gập + xoắn khuỷu (ik_arm của rigpose lật khuỷu khi tay đang gập)."""
    sh, el, wr = "Shoulder_" + s, "Elbow_" + s, "Wrist_" + s
    T = Wt[:3, 3]
    W = rig.world(P); S, E = W[sh][:3, 3], W[el][:3, 3]
    hz = nrm3(W[el][:3, :3])[:, 2]
    f = W[wr][:3, 3] - E; want = np.linalg.norm(T - S)
    th = np.linspace(-60, 60, 241)
    dist = [np.linalg.norm(E + RP.axis_angle(hz, t) @ f - S) for t in th]
    k = int(np.argmin(np.abs(np.array(dist) - want))); t = th[k]
    for _ in range(20):    # tinh chỉnh
        h = 0.01; g = (np.linalg.norm(E + RP.axis_angle(hz, t + h) @ f - S) - np.linalg.norm(E + RP.axis_angle(hz, t - h) @ f - S)) / (2 * h)
        if abs(g) < 1e-9: break
        t -= (np.linalg.norm(E + RP.axis_angle(hz, t) @ f - S) - want) / g
        t = float(np.clip(t, -60, 60))
    rig.set_world_rot(P, el, RP.axis_angle(hz, t) @ nrm3(W[el][:3, :3]))
    W = rig.world(P); Wr = W[wr][:3, 3]
    rig.set_world_rot(P, sh, RP.rot_between(Wr - S, T - S) @ nrm3(W[sh][:3, :3]))
    W = rig.world(P); E = W[el][:3, 3]; ax = (T - S) / np.linalg.norm(T - S)
    d = (E - S) - ((E - S) @ ax) * ax
    if np.linalg.norm(d) > 1e-3:
        d /= np.linalg.norm(d); pd = pole_dir - (pole_dir @ ax) * ax; pd /= max(np.linalg.norm(pd), 1e-9)
        a = np.degrees(np.arctan2(np.cross(d, pd) @ ax, d @ pd))
        rig.set_world_rot(P, sh, RP.axis_angle(ax, a) @ nrm3(W[sh][:3, :3]))
    rig.set_world_rot(P, wr, nrm3(Wt[:3, :3]))
    return float(np.linalg.norm(rig.pos(P, wr) - T))

def apply(rig, P, R, ref=None, keep="hand", sides="LR", iters=3):
    """Sửa P tại chỗ theo các luật fix=true. keep='hand': bàn tay giữ vị trí + hướng world (IK lại tay, khuỷu giữ hướng cũ);
    keep='dir': giữ hướng world của cánh tay (xoay vai FK), cả tay dời theo điểm vai; keep='fk': tay quay theo bả vai. Trả {rule: độ đã thêm, 'hand_err_cm': ...}."""
    hands = _hands(rig, P) if keep == "hand" else {}
    log = {}
    for it in range(iters):
        for cp in R["couplings"]:
            if cp.get("type") == "share" and cp.get("fix") and all(n in rig.parent for n in cp["chain"]):
                a, tot = chain_angles(rig, P, cp, ref)
                if tot >= cp.get("min_total", 10) and sum(a) > 1e-6:
                    sh = [x / sum(a) for x in a]; lo, hi = cp["band"]
                    if any(x < lo or x > hi for x in sh):
                        _share_fix(rig, P, cp, ref); log[cp["id"]] = round(tot, 1)
        _clamp(rig, P, R, ref)
        for s in sides:
            sc = "Scapula_" + s
            if sc not in rig.parent: continue
            for cp in R["couplings"]:
                if cp.get("type", "follow") != "follow" or not cp.get("fix") or s not in cp.get("side", "LR"): continue
                C = Ctx(rig, P, R); Cr = Ctx(rig, ref, R) if ref is not None else None
                want = expect(cp, C, s) - (expect(cp, Cr, s) if Cr else 0)
                got = driven(cp, C, s) - (driven(cp, Cr, s) if Cr else 0)
                need = want - got
                if abs(need) < 0.3: continue
                up, fwd, lat = C.lat(s)
                v = C.p("Shoulder_" + s) - C.p(sc); L = np.linalg.norm(v); v /= L
                e, p = C.clav(s)
                if cp["driven"] == "clav_elev": e += need
                else: p += need
                e, p = np.radians(e), np.radians(p)
                vt = lat * np.cos(e) * np.cos(p) + fwd * np.cos(e) * np.sin(p) + up * np.sin(e)
                Rs = C.rw("Shoulder_" + s)
                rig.set_world_rot(P, sc, RP.rot_between(v, vt) @ C.rw(sc))
                if keep == "dir": rig.set_world_rot(P, "Shoulder_" + s, Rs)
                log["%s_%s" % (cp["id"], s)] = round(log.get("%s_%s" % (cp["id"], s), 0) + need, 1)
        _clamp(rig, P, R, ref)
        for s, (Wt, d) in hands.items():
            if s in sides: keep_hand(rig, P, s, Wt, d)
    if hands:
        W = rig.world(P)
        log["hand_err_cm"] = round(max(float(np.linalg.norm(W["Wrist_" + s][:3, 3] - Wt[:3, 3])) for s, (Wt, _) in hands.items()), 2)
    return log


# ------------------------------------------------------------------ CLI
class Anim:
    def __init__(self, rig, path, fps=30):
        import fbxanim
        models, _ = fbxanim.load(path); self.fx = fbxanim
        self.by = {m["name"]: m for m in models.values() if m["type"] == "LimbNode"}; self.rig, self.fps = rig, fps
        ts = fbxanim.key_times(models); self.last = int(round(max(ts))) if ts else 0     # key_times trả số frame (30 fps)
    def frame(self, f):
        return {n: (self.fx.local(self.by[n], f / self.fps) if n in self.by else self.rig.rest_pose[n].copy()) for n in self.rig.models}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["audit"])
    ap.add_argument("--rig", required=True); ap.add_argument("--anim", required=True); ap.add_argument("--tex", default=None)
    ap.add_argument("--rules"); ap.add_argument("--ref-frame", type=int, default=0); ap.add_argument("--frames")
    ap.add_argument("--fix", action="store_true"); ap.add_argument("--json")
    ap.add_argument("--render", type=int, nargs="*"); ap.add_argument("--view", default="side_r"); ap.add_argument("--out", default=".")
    a = ap.parse_args()
    rig = RP.Rig(a.rig, tex=a.tex) if a.tex else RP.Rig(a.rig)
    R = load(a.rules); A = Anim(rig, a.anim); ref = A.frame(a.ref_frame)
    if a.frames: lo, hi = map(int, a.frames.split(":"))
    else: lo, hi = 0, A.last
    rep, by_rule = {}, {}
    for f in range(lo, hi + 1):
        P = A.frame(f); errs = audit(rig, P, R, ref)
        row = {"errors": errs}
        if a.fix:
            Q = {k: v.copy() for k, v in P.items()}; row["fix"] = apply(rig, Q, R, ref)
            row["after"] = [e["rule"] + ":" + e["joint"] for e in audit(rig, Q, R, ref)]
            if a.render and f in a.render:
                os.makedirs(a.out, exist_ok=True)
                rig.render(P, a.view, os.path.join(a.out, "f%02d_%s_before.png" % (f, a.view)))
                rig.render(Q, a.view, os.path.join(a.out, "f%02d_%s_after.png" % (f, a.view)))
        rep[f] = row
        for e in errs: by_rule.setdefault(e["rule"] + " " + e["joint"], []).append(f)
        print("F%02d %s" % (f, "OK" if not errs else ""), *("\n    - " + e["msg"] for e in errs),
              ("\n    fix: %s → còn %d lỗi %s" % (row["fix"], len(row["after"]), row["after"]) if a.fix else ""))
    print("\nTóm tắt (luật khớp → frame):")
    for k, fs in sorted(by_rule.items()): print("  %-34s %2d F: %s" % (k, len(fs), ",".join(map(str, fs))))
    if a.json: json.dump(rep, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)

if __name__ == "__main__":
    main()
