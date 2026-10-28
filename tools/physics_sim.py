"""Pose Lab physics layer, Python twin of computePhys in work/pose_lab/index.html (docs/poselab_physics_p1.md).
Same steps as the page: parts in order (joints/hinges by depth, then props, then elbow swings), 8 sub-steps (64 for
props), under-damped spring in world space toward the key pose, soft limit, pinned frames, ease onto the key pose over
the last frames, prop soft pad against colliders, arm two-bone IK onto the grip. Used to cross-check the page and to
run the same physics from Python (AI side) on any clip.

Input: a dump from the page (base locals per frame, prop points, config): {frames, loop, cfg, base, pts}.
Locals are three.js packs [qx, qy, qz, qw, px, py, pz] in the bones' own frames (cm), the same as the FBX locals.
usage: python tools/physics_sim.py <dump.json> [--compare]   (--compare: diff against the page's `out` in the dump)"""
import sys, json, math, numpy as np

PRESETS = {"light": (8, 0.62, 12), "medium": (12, 0.68, 15), "heavy": (15, 0.72, 24), "vheavy": (20, 0.75, 30)}
SUB, SUBP, PIN_RAMP, TOL = 8, 64, 3, 0.05      # cm units (page: x0.01 world)
FLOOR_BOUNCE, FLOOR_TH_CM = 0.15, 2.0           # fall pack (docs/poselab_physics_p4_fall.md)
ARMS = {"L": ("Shoulder_L", "Elbow_L", "Wrist_L"), "R": ("Shoulder_R", "Elbow_R", "Wrist_R")}

# ---------------- rotations (3x3) ----------------
def q2m(q):
    x, y, z, w = q; n = math.sqrt(x * x + y * y + z * z + w * w); x, y, z, w = x / n, y / n, z / n, w / n
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
def m2q(R):
    t = np.trace(R)
    if t > 0:
        s = math.sqrt(t + 1) * 2; return np.array([(R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s, s / 4])
    i = int(np.argmax(np.diag(R)))
    if i == 0: s = math.sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2]) * 2; return np.array([s / 4, (R[0, 1] + R[1, 0]) / s, (R[0, 2] + R[2, 0]) / s, (R[2, 1] - R[1, 2]) / s])
    if i == 1: s = math.sqrt(1 + R[1, 1] - R[0, 0] - R[2, 2]) * 2; return np.array([(R[0, 1] + R[1, 0]) / s, s / 4, (R[1, 2] + R[2, 1]) / s, (R[0, 2] - R[2, 0]) / s])
    s = math.sqrt(1 + R[2, 2] - R[0, 0] - R[1, 1]) * 2; return np.array([(R[0, 2] + R[2, 0]) / s, (R[1, 2] + R[2, 1]) / s, s / 4, (R[1, 0] - R[0, 1]) / s])
def rvec(A, B):                     # rotation taking A to B, world rotation vector (rad)
    D = B @ A.T; c = max(-1.0, min(1.0, (np.trace(D) - 1) / 2)); th = math.acos(c)
    if th < 1e-9: return np.zeros(3)
    v = np.array([D[2, 1] - D[1, 2], D[0, 2] - D[2, 0], D[1, 0] - D[0, 1]])
    if th > math.pi - 1e-6:          # 180 deg: axis from the symmetric part
        w, V = np.linalg.eigh((D + D.T) / 2); return V[:, int(np.argmax(w))] * th
    return v / (2 * math.sin(th)) * th
def rot(v):
    a = np.linalg.norm(v)
    if a < 1e-12: return np.eye(3)
    k = v / a; K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
def slerp(A, B, t): return rot(rvec(A, B) * t) @ A
def from_to(u, v):
    u = u / np.linalg.norm(u); v = v / np.linalg.norm(v); c = np.cross(u, v); s = np.linalg.norm(c)
    if s < 1e-12: return np.eye(3)
    return rot(c / s * math.atan2(s, np.dot(u, v)))
def soft_limit(a, L):
    k = 0.6 * L; return a if a <= k else k + (L - k) * math.tanh((a - k) / (L - k))
def smooth01(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
def parse_set(s):
    o = set()
    for part in str(s or "").split(","):
        part = part.strip()
        if not part: continue
        a, _, b = part.partition("-"); a = int(a); b = int(b or a); o.update(range(min(a, b), max(a, b) + 1))
    return o

# ---------------- skeleton (locals as (R, p)) ----------------
class Rig:
    def __init__(self, par, local):  # par: bone -> parent bone (None = top); local: bone -> (R, p)
        self.par, self.L = par, {n: (R.copy(), p.copy()) for n, (R, p) in local.items()}
    def world(self, n):
        R, p = self.L[n]; pa = self.par.get(n)
        if pa is None or pa not in self.L: return R.copy(), p.copy()
        PR, Pp = self.world(pa); return PR @ R, PR @ p + Pp
    def wq(self, n): return self.world(n)[0]
    def wp(self, n): return self.world(n)[1]
    def set_world_rot(self, n, Rw):
        pa = self.par.get(n); PR = self.wq(pa) if pa in self.L else np.eye(3)
        self.L[n] = (PR.T @ Rw, self.L[n][1])
    def set_world(self, n, Rw, pw):
        pa = self.par.get(n)
        if pa in self.L: PR, Pp = self.world(pa); self.L[n] = (PR.T @ Rw, PR.T @ (pw - Pp))
        else: self.L[n] = (Rw.copy(), pw.copy())
    def rotate_world(self, n, Q): self.set_world_rot(n, Q @ self.wq(n))
    def solve2(self, chain, target, endR):       # the page's two-bone IK (bend plane from the current middle joint)
        h, k, a = chain; hip, knee, ank = self.wp(h), self.wp(k), self.wp(a)
        la, lb = np.linalg.norm(knee - hip), np.linalg.norm(ank - knee)
        d = target - hip; dist = min(max(np.linalg.norm(d), 1e-4), la + lb - 1e-4); d = d / max(np.linalg.norm(d), 1e-12)
        pole = (knee - hip) - d * np.dot(knee - hip, d)
        pole = np.array([0.0, 0.0, 1.0]) if np.dot(pole, pole) < 1e-8 else pole / np.linalg.norm(pole)
        cosA = max(-1.0, min(1.0, (la * la + dist * dist - lb * lb) / (2 * la * dist)))
        kneeT = hip + d * la * cosA + pole * la * math.sqrt(1 - cosA * cosA)
        self.rotate_world(h, from_to(knee - hip, kneeT - hip))
        knee2, ank2 = self.wp(k), self.wp(a)
        self.rotate_world(k, from_to(ank2 - knee2, hip + d * dist - knee2))
        self.set_world_rot(a, endR)

def unpack(v): return q2m(v[:4]), np.array(v[4:7], float)
def pack(R, p): return [*m2q(R).tolist(), *p.tolist()]
def gap(pts, R, pos, c):
    w = pts @ R.T + pos; d = np.linalg.norm(w - c, axis=1); i = int(np.argmin(d)); return d[i], w[i]


# ---------------- body collision (phase 2, docs/poselab_physics_p2.md): same steps as the page ----------------
GRIP_CM, BODY_TOL = 6.0, 0.05
def seg_seg(p1, q1, p2, q2):
    d1, d2, r = q1 - p1, q2 - p2, p1 - p2; a, e, f = d1 @ d1, d2 @ d2, d2 @ r; c, b = d1 @ r, d1 @ d2; den = a * e - b * b
    sp = min(1.0, max(0.0, (b * f - c * e) / den)) if den > 1e-12 else 0.0; t = (b * sp + f) / e if e > 1e-12 else 0.0
    if t < 0: t = 0.0; sp = min(1.0, max(0.0, -c / a)) if a > 1e-12 else 0.0
    elif t > 1: t = 1.0; sp = min(1.0, max(0.0, (b - c) / a)) if a > 1e-12 else 0.0
    return float(np.linalg.norm(p1 + d1 * sp - (p2 + d2 * t)))
def closest_on(P, a, b):            # closest points on segment a-b for rows of P
    ab = b - a; t = np.clip((P - a) @ ab / max(ab @ ab, 1e-12), 0, 1); return a + t[:, None] * ab
class Body:
    def __init__(self, d, par, A=None):   # page dump (bone unit frames, cm); A: python world -> page world
        A = np.eye(4) if A is None else A; self.UP = A[1, :3] / np.linalg.norm(A[1, :3])
        self.ycm = lambda W: (W @ A[1, :3] + A[1, 3]) * 100.0
        self.caps = {k: (np.array(c["a"]), np.array(c["b"]), c["r"]) for k, c in d["caps"].items()}
        self.shells = {k: np.array(v, float) for k, v in d["shells"].items()}
        self.reach = d["reach"]; self.pairs = [tuple(x) for x in d["pairs"]]; self.props = d["props"]; self.par = par
    def movers(self, bone):
        out = []
        for k in self.caps:
            x = k
            while x is not None:
                if x == bone: out.append(k); break
                x = self.par.get(x)
        return out
    def link(self, bone):
        mov = self.movers(bone); ms = set(mov); ok = set(); obs = []
        for a, b in self.pairs:
            if a in self.props or b in self.props: continue
            if a in ms and b not in ms:
                if b not in obs: obs.append(b)
                ok.add((a, b))
            elif b in ms and a not in ms:
                if a not in obs: obs.append(a)
                ok.add((b, a))
        O = [o for o in obs if o in self.caps] + ["__floor"]                 # fall pack: the floor for every moved segment
        return dict(mov=mov, obs=O, valid=[[o == "__floor" or (k, o) in ok for k in mov] for o in O])
    def mov_pts(self, rig, bone, L):
        Rb, pb = rig.world(bone); X, R, K, ax = [], [], [], []
        for ki, k in enumerate(L["mov"]):
            Rk, pk = rig.world(k); a, b, r = self.caps[k]
            to_b = lambda q: Rb.T @ (Rk @ q + pk - pb)
            for i, q in enumerate(self.shells.get(k, [])):
                if i % 2: continue
                X.append(to_b(q)); R.append(0.0); K.append(ki)
            for i in range(5): X.append(to_b(a + (b - a) * (i / 4))); R.append(r); K.append(ki)
            ax.append((to_b(a), to_b(b), self.reach[k]))
        return dict(X=np.array(X), R=np.array(R), K=np.array(K), ax=ax)
    def obs_world(self, rig, L):
        out = []
        for o in L["obs"]:
            if o == "__floor": out.append(None); continue
            Ro, po = rig.world(o); a, b, r = self.caps[o]; out.append((Ro @ a + po, Ro @ b + po, r))
        return out
    def overlaps(self, q, pivot, mp, ob, L, allow):   # -> list of (pen, w, c, oi, ki)
        res = []; W = mp["X"] @ q.T + pivot
        wa = [(q @ a + pivot, q @ b + pivot, rr) for a, b, rr in mp["ax"]]
        for oi, o in enumerate(ob):
            if o is None:                              # the floor plane: a point (radius R) may not go below page y 0
                ok = [L["valid"][oi][ki] and min(self.ycm(wa[ki][0]), self.ycm(wa[ki][1])) - wa[ki][2] < 5.0 for ki in range(len(L["mov"]))]
                if not any(ok): continue
                idx = np.nonzero(np.array([ok[k] for k in mp["K"]]))[0]
                if not len(idx): continue
                al = np.array([allow[oi][mp["K"][i]] for i in idx]) if allow is not None else 0.0
                pen = mp["R"][idx] - self.ycm(W[idx]) - al
                for j in np.nonzero(pen > 0)[0]: res.append((pen[j], W[idx[j]], W[idx[j]] - self.UP, oi, mp["K"][idx[j]]))
                continue
            a, b, r = o
            ok = [L["valid"][oi][ki] and seg_seg(wa[ki][0], wa[ki][1], a, b) <= wa[ki][2] + r for ki in range(len(L["mov"]))]
            if not any(ok): continue
            idx = np.nonzero(np.array([ok[k] for k in mp["K"]]))[0]
            if not len(idx): continue
            C = closest_on(W[idx], a, b); d = np.linalg.norm(C - W[idx], axis=1)
            al = np.array([allow[oi][mp["K"][i]] for i in idx]) if allow is not None else 0.0
            pen = r + mp["R"][idx] - d - al
            for j in np.nonzero(pen > 0)[0]: res.append((pen[j], W[idx[j]], C[j], oi, mp["K"][idx[j]]))
        return res
    def allow(self, q, pivot, mp, ob, L):
        al = [np.zeros(len(L["mov"])) for _ in ob]
        for pen, w, c, oi, ki in self.overlaps(q, pivot, mp, ob, L, None):
            if pen > al[oi][ki]: al[oi][ki] = pen
        return al
    def excess(self, q, pivot, mp, ob, L, allow):
        return max([0.0] + [x[0] for x in self.overlaps(q, pivot, mp, ob, L, allow)])
    def push(self, st, pivot, mp, ob, L, allow):
        hits = self.overlaps(st["S"], pivot, mp, ob, L, allow)
        if not hits: return False
        tq = np.zeros(3); mm = np.zeros(3); sw = 0.0; floor_hit = any(ob[h[3]] is None for h in hits)
        for pen, w, c, oi, ki in hits:
            axv = np.cross(w - pivot, c - w); l = np.linalg.norm(axv)
            if l < 1e-10: continue
            tq += axv * (pen * pen / l); mm += w * pen; sw += pen
        if not sw: return False
        axv = tq / sw; pen = np.linalg.norm(axv)
        if pen < 1e-10: return False
        axv = axv / pen; lever = max(np.linalg.norm(mm / sw - pivot), 1.0)
        st["S"] = rot(-axv * pen / lever) @ st["S"]
        vin = st["vel"] @ axv
        if vin > 0: st["vel"] = st["vel"] - axv * vin * (1 + (FLOOR_BOUNCE if floor_hit else 0))   # a small bounce off the floor
        return True
    def safe(self, T, o, pivot, mp, ob, L, allow):
        if not ob or self.excess(o, pivot, mp, ob, L, allow) <= BODY_TOL: return o, False, 1.0
        lo, hi = 0.0, 1.0
        for _ in range(18):
            m = (lo + hi) / 2
            if self.excess(slerp(T, o, m), pivot, mp, ob, L, allow) <= BODY_TOL: lo = m
            else: hi = m
        return slerp(T, o, lo), True, lo

def simulate(dump, par):
    cfg, NF, loop = dump["cfg"], dump["frames"], dump["loop"]
    N = NF - 1 if loop else NF; last = N
    pins = parse_set(cfg.get("pin"))
    def pin_w(f):
        if not pins: return 1.0
        d = min((min(abs(p - f), N - abs(p - f)) if loop else abs(p - f)) for p in pins)
        return 1.0 if d >= PIN_RAMP else smooth01(d / PIN_RAMP)
    def end_w(f):
        E = 0 if loop else max(0, int(cfg.get("end", 8) or 0))
        return 1.0 if not E or f <= last - E else 1 - smooth01((f - (last - E)) / E)
    def depth(n):
        d, x = 0, par.get(n)
        while x is not None and x in par: d += 1; x = par.get(x)
        return d
    parts = []
    for p in cfg["parts"]:
        pr = PRESETS.get(p.get("preset"), PRESETS["medium"])
        period, bounce, limit = p.get("period", pr[0]), p.get("bounce", pr[1]), p.get("limit", pr[2])
        z = max(0.0, min(0.98, 1 - bounce)); w0 = 2 * math.pi / max(2, period)
        side = p["bone"][-1] if p["type"] == "swing" else p.get("hand", "L")
        ord_ = 1e3 if p["type"] == "prop" else 2e3 if p["type"] == "swing" else depth(p["bone"])
        parts.append(dict(p, K=w0 * w0, C=2 * z * w0, L=math.radians(limit), side=side, S=None, vel=np.zeros(3), ord=ord_, aux={}))
    parts.sort(key=lambda x: x["ord"])
    cols = cfg.get("colliders", [])
    A = np.array(dump.get("arm", np.eye(4).flatten()), float).reshape(4, 4).T     # three.js column-major -> page world (m)
    UP = A[1, :3] / np.linalg.norm(A[1, :3])                                      # page "up" in this frame
    ycm = lambda W: (W @ A[1, :3] + A[1, 3]) * 100.0                              # page world height, cm
    pts = {k: np.array(v, float) for k, v in dump.get("pts", {}).items()}
    INJ, Sw = dump.get("inj") or {}, A[:3, :3] / np.linalg.norm(A[:3, 0])            # impacts: turn speed given to the springs (page world)
    inj = lambda f, b: Sw.T @ np.array(INJ[str(f)][b]) if b in INJ.get(str(f), {}) else None
    BODY = Body(dump["body"], par, A) if dump.get("body") else None
    seq = [(f, r == (1 if loop else 0)) for r in range(2 if loop else 1) for f in range(1, last + 1)]
    out = {}
    for f, rec in seq:
        rig = Rig(par, {n: unpack(v) for n, v in dump["base"][str(f)].items()})
        first = (not loop) and f == 1; wp_, we = pin_w(f), end_w(f)
        for p in parts:
            t = p["type"]
            if t in ("joint", "hinge"):
                T = rig.wq(p["bone"])
                if p["S"] is None: p["S"], p["Tp"] = T.copy(), T.copy()
                iw = None if first else inj(f, p["bone"])
                if iw is not None: p["vel"] = p["vel"] + iw
                if BODY:
                    L = p.get("link") or p.setdefault("link", BODY.link(p["bone"])); pivot = rig.wp(p["bone"])
                    mp = BODY.mov_pts(rig, p["bone"], L); ob = BODY.obs_world(rig, L); allow = BODY.allow(T, pivot, mp, ob, L)
                h = 1 / SUB
                for s in range(1, 0 if first else SUB + 1):
                    tg = slerp(p["Tp"], T, s * h); err = rvec(p["S"], tg)
                    p["vel"] = p["vel"] + err * p["K"] * h; p["vel"] = p["vel"] - p["vel"] * p["C"] * h
                    p["S"] = rot(p["vel"] * h) @ p["S"]
                    if BODY and ob: BODY.push(p, pivot, mp, ob, L, allow)
                d = rvec(T, p["S"]); a = np.linalg.norm(d)
                if a > 1e-9: p["S"] = rot(d * (soft_limit(a, p["L"]) / a)) @ T
                if wp_ < 1: p["S"] = slerp(T, p["S"], wp_); p["vel"] = p["vel"] * wp_
                o = slerp(T, p["S"], we)
                if t == "hinge":
                    ax = T @ np.array([0.0, 0.0, 1.0]); dd = rvec(T, o); o = rot(ax * np.dot(dd, ax)) @ T
                if BODY: o = BODY.safe(T, o, pivot, mp, ob, L, allow)[0]
                rig.set_world_rot(p["bone"], o); p["Tp"] = T
            elif t == "prop":
                bone, wr = p["bone"], ARMS[p["side"]][2]
                (T, tp), (WR, g) = rig.world(bone), rig.world(wr)
                Gp = T.T @ (g - tp); Gq = T.T @ WR                       # grip (wrist) in the prop's frame
                P_ = pts.get(bone, np.zeros((0, 3))) if cols else np.zeros((0, 3))
                cs = [rig.wp(c["bone"]) for c in cols]
                at = lambda R, gg: gg - R @ Gp
                need = []
                for ci, c in enumerate(cs):
                    g0 = gap(P_, T, at(T, g), c)[0] if len(P_) else 1e9
                    p["aux"].setdefault(ci, g0); need.append(min(p["aux"][ci], g0))
                ALL = pts.get(bone, np.zeros((0, 3)))                   # floor: never below 0 or the key pose (page world y)
                floorY = min(0.0, float(np.min(ycm(ALL @ T.T + at(T, g))))) if len(ALL) else -1e9
                if p["S"] is None: p["S"], p["Tp"], p["gp"], p["cp"], p["fp"] = T.copy(), T.copy(), g.copy(), [c.copy() for c in cs], floorY
                iw = None if first else inj(f, bone)
                if iw is not None: p["vel"] = p["vel"] + iw
                bobs = []
                if BODY and len(ALL):
                    if "pax" not in p:                                   # the prop's long axis + radius, for pruning
                        m_ = ALL.mean(0); far = ALL[int(np.argmax(np.linalg.norm(ALL - m_, axis=1)))]
                        dr = (far - m_) / np.linalg.norm(far - m_); tt = (ALL - m_) @ dr; lo_, hi_ = min(0.0, tt.min()), max(0.0, tt.max())
                        pa_, pb_ = m_ + dr * lo_, m_ + dr * hi_; p["pax"] = (pa_, pb_, float(np.max(np.linalg.norm(ALL - closest_on(ALL, pa_, pb_), axis=1))))
                    def capW(k):
                        R_, p_ = rig.world(k); a, b, r = BODY.caps[k]; return R_ @ a + p_, R_ @ b + p_, r
                    KP0 = ALL @ T.T + at(T, g)
                    depth_in = lambda a, b, r: float(np.max(r - np.linalg.norm(closest_on(KP0, a, b) - KP0, axis=1)))
                    held = {p["side"]}
                    for hs in "LR":
                        if "Wrist_" + hs in BODY.caps:
                            a, b, r = capW("Wrist_" + hs)
                            if depth_in(a, b, r + GRIP_CM) > 0: held.add(hs)
                    paxW = (T @ p["pax"][0] + at(T, g), T @ p["pax"][1] + at(T, g))
                    for k in BODY.caps:
                        if (k.startswith("Wrist_") or k.startswith("Elbow_")) and k[-1] in held: continue
                        a, b, r = capW(k); near = seg_seg(paxW[0], paxW[1], a, b) <= p["pax"][2] + r
                        bobs.append((a, b, r, r - (max(0.0, depth_in(a, b, r)) if near else 0.0)))
                def contact(Pts, org, gg, depth_of, away_of, bounce=0.0):
                    W = Pts @ p["S"].T + org; pen_i = depth_of(W); m = pen_i > 0
                    if not m.any(): return
                    Wm, pm = W[m], pen_i[m]; ax_i = np.cross(Wm - gg, away_of(Wm)); l = np.linalg.norm(ax_i, axis=1); k = l > 1e-7
                    if not k.any(): return
                    Wm, pm, ax_i, l = Wm[k], pm[k], ax_i[k], l[k]
                    tq = (ax_i * (pm ** 2 / l)[:, None]).sum(0) / pm.sum(); wc = (Wm * pm[:, None]).sum(0) / pm.sum()
                    pen = np.linalg.norm(tq); ax = tq / pen; lever = max(np.linalg.norm(wc - gg), 1.0)
                    p["S"] = rot(-ax * pen / lever) @ p["S"]
                    vin = np.dot(p["vel"], ax)
                    if vin > 0: p["vel"] = p["vel"] - ax * vin * (1 + bounce)
                h = 1 / SUBP
                for s in range(1, 0 if first else SUBP + 1):
                    u = s * h; tg = slerp(p["Tp"], T, u); gg = p["gp"] + (g - p["gp"]) * u; err = rvec(p["S"], tg)
                    p["vel"] = p["vel"] + err * p["K"] * h; p["vel"] = p["vel"] - p["vel"] * p["C"] * h
                    p["S"] = rot(p["vel"] * h) @ p["S"]
                    fy = p["fp"] + (floorY - p["fp"]) * u
                    if len(ALL): contact(ALL, at(p["S"], gg), gg, lambda W: fy - ycm(W), lambda W: np.tile(-UP, (len(W), 1)), FLOOR_BOUNCE)
                    for ci, c in enumerate(cs):
                        if not len(P_): continue
                        cc = p["cp"][ci] + (c - p["cp"][ci]) * u
                        contact(P_, at(p["S"], gg), gg, lambda W: need[ci] - np.linalg.norm(W - cc, axis=1), lambda W: cc - W)
                    if bobs and (s % 4 == 0 or s == SUBP):
                        org = at(p["S"], gg); pa_, pb_ = p["S"] @ p["pax"][0] + org, p["S"] @ p["pax"][1] + org
                        for a, b, r, nd in bobs:
                            if seg_seg(pa_, pb_, a, b) <= p["pax"][2] + r:
                                contact(ALL[::2], org, gg, lambda W: nd - np.linalg.norm(closest_on(W, a, b) - W, axis=1), lambda W: closest_on(W, a, b) - W)
                d = rvec(T, p["S"]); a = np.linalg.norm(d)
                if a > 1e-9: p["S"] = rot(d * (soft_limit(a, p["L"]) / a)) @ T
                if wp_ < 1: p["S"] = slerp(T, p["S"], wp_); p["vel"] = p["vel"] * wp_
                o = slerp(T, p["S"], we)
                for ci, c in enumerate(cs):
                    if not len(P_) or gap(P_, o, at(o, g), c)[0] >= need[ci] - TOL: continue
                    lo, hi = 0.0, 1.0
                    for _ in range(20):
                        m = (lo + hi) / 2; q = slerp(T, o, m)
                        if gap(P_, q, at(q, g), c)[0] >= need[ci] - TOL: lo = m
                        else: hi = m
                    o = slerp(T, o, lo)
                rig.set_world(bone, o, at(o, g)); rig.solve2(ARMS[p["side"]], g, o @ Gq)
                p["Tp"], p["gp"], p["cp"], p["fp"] = T, g.copy(), [c.copy() for c in cs], floorY
            elif t == "swing":
                sn, en, wn = ARMS[p["side"]]
                S_, E, Wr = rig.wp(sn), rig.wp(en), rig.wp(wn); u = (Wr - S_) / np.linalg.norm(Wr - S_)
                dv = (E - S_) - u * np.dot(E - S_, u); dv /= np.linalg.norm(dv)
                if "ref" not in p["aux"]: p["aux"]["ref"] = dv.copy()
                r = p["aux"]["ref"] - u * np.dot(p["aux"]["ref"], u); r /= np.linalg.norm(r)
                th = math.atan2(np.dot(np.cross(r, dv), u), np.dot(r, dv))
                wrap = lambda x: (x + math.pi) % (2 * math.pi) - math.pi
                if p["S"] is None: p["S"], p["Tp"], p["v"] = th, th, 0.0
                h = 1 / SUB
                for s in range(1, 0 if first else SUB + 1):
                    tg = p["Tp"] + wrap(th - p["Tp"]) * s * h; p["v"] += h * (p["K"] * wrap(tg - p["S"]) - p["C"] * p["v"]); p["S"] += p["v"] * h
                off = wrap(p["S"] - th); off = math.copysign(soft_limit(abs(off), p["L"]), off)
                off *= wp_; p["v"] *= wp_; p["S"] = th + off
                o_ = off * we; WRq = rig.wq(wn); Tq = rig.wq(sn)
                if BODY:
                    L = p.get("link") or p.setdefault("link", BODY.link(sn)); mp = BODY.mov_pts(rig, sn, L); ob = BODY.obs_world(rig, L)
                    allow = BODY.allow(Tq, S_, mp, ob, L); _, used, m = BODY.safe(Tq, rot(u * o_) @ Tq, S_, mp, ob, L, allow)
                    if used: o_ *= m; p["S"] = th + o_; p["v"] = 0.0
                rig.rotate_world(sn, rot(u * o_)); rig.set_world_rot(wn, WRq)
                p["Tp"] = th
        if rec: out[f] = {n: pack(*rig.L[n]) for n in rig.L}
    return out


# ---------------- balance (phase 3, docs/poselab_physics_p3.md): same steps as the page ----------------
BAL_G, BAL_GROUND_CM, BAL_OUT_CM, BAL_RUN = 9.81, 5.0, 5.0, 3
def hull2(pts):
    pts = sorted(map(tuple, pts))
    if len(pts) < 3: return [list(p) for p in pts]
    cr = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]); lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return [list(p) for p in lo[:-1] + up[:-1]]
def poly_margin(poly, q):
    if not poly: return -1e9
    def seg_d(a, b):
        ex, ey = b[0] - a[0], b[1] - a[1]; L2 = ex * ex + ey * ey
        t = max(0.0, min(1.0, ((q[0] - a[0]) * ex + (q[1] - a[1]) * ey) / L2)) if L2 > 1e-12 else 0.0
        return math.hypot(a[0] + ex * t - q[0], a[1] + ey * t - q[1])
    if len(poly) < 3: return -min(seg_d(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))
    inside, md = True, 1e9
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        if (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) < 0: inside = False
        md = min(md, seg_d(a, b))
    return md if inside else -md
def balance(dump, par):
    """per frame CoM / support / capture point and the step-aware issues, in page units turned to cm"""
    A = np.array(dump["arm"], float).reshape(4, 4).T; S = A[:3, :3]; s = np.linalg.norm(S[:, 0])
    to_page = lambda W: (W @ S.T + A[:3, 3]) * 100.0                     # python world (local units) -> page world, cm
    body = dump["body"]; caps = {k: (np.array(c["a"]), np.array(c["b"]), c["r"]) for k, c in body["caps"].items()}
    shells = {k: np.array(v, float) for k, v in body["shells"].items()}; props = body["props"]
    lanes = {k: parse_set(v) for k, v in (dump.get("lanes") or {}).items()}; use_lanes = any(lanes.get(k) for k in "LR")
    NF, loop, fps = dump["frames"], dump["loop"], dump.get("fps", 30); rows = []
    for f in range(1, NF + (0 if loop else 1)):
        rig = Rig(par, {n: unpack(v) for n, v in dump["base"][str(f)].items()})
        W = {k: rig.world(k) for k in set(caps) | set(shells)}
        cw = {k: (to_page(W[k][0] @ a + W[k][1]), to_page(W[k][0] @ b + W[k][1]), r) for k, (a, b, r) in caps.items()}       # cm
        sw = {k: to_page(v @ W[k][0].T + W[k][1]) for k, v in shells.items() if len(v)}
        M, c = 0.0, np.zeros(3)
        for a, b, r in cw.values(): L = np.linalg.norm(b - a); v = math.pi * r * r * L + 4 / 3 * math.pi * r ** 3; M += v; c += (a + b) / 2 * v
        pm = M * dump["propMass"] / 100
        for p in props:
            if p in sw and len(sw[p]) and pm > 0: c += sw[p].mean(0) * pm; M += pm
        c /= M; touch, pts, feet = set(), [], []
        for side in "LR":
            sh = sw.get("Ankle_" + side)
            if sh is None or not len(sh): continue
            lo = sh[:, 1].min(); on = (((f - 1) % (NF - 1)) + 1 if loop else f) in lanes.get(side, set()) if use_lanes else lo < BAL_GROUND_CM
            if not on: continue
            touch.add(side); fp = [[p[0], p[2]] for p in sh if p[1] < (lo + 3 if use_lanes else BAL_GROUND_CM)]; pts += fp; feet += fp
        for p in props:
            low = [q for q in sw.get(p, []) if q[1] < BAL_GROUND_CM]
            if low: touch.add("P"); pts += [[q[0], q[2]] for q in low]
        body_low = 1e9
        for k, sh in sw.items():                    # lying / kneeling: body segments on the floor hold the body too
            if k in props or k.startswith("Ankle_"): continue
            body_low = min(body_low, float(sh[:, 1].min()))
            low = [q for q in sh if q[1] < BAL_GROUND_CM]
            if low: touch.add("T:" + k); pts += [[q[0], q[2]] for q in low]
        floor = {k: round(-float(sh[:, 1].min())) for k, sh in sw.items() if -float(sh[:, 1].min()) > FLOOR_TH_CM}   # sunk into the floor
        rows.append(dict(f=f, com=c, h=max(30.0, c[1]), sup=hull2(pts), feet=feet, touch=touch, bodyLow=body_low, floor=floor))
    N = len(rows); at = (lambda i: rows[i % N]) if loop else (lambda i: rows[max(0, min(N - 1, i))])
    for i, r in enumerate(rows):
        a, b = at(i - 1), at(i + 1); span = 2 if loop else (min(N - 1, i + 1) - max(0, i - 1)) or 1
        v = (b["com"] - a["com"]) * fps / span; w = math.sqrt(BAL_G / (r["h"] / 100))
        r["cap"] = [r["com"][0] + v[0] / w, r["com"][2] + v[2] / w]
        r["mCom"] = poly_margin(r["sup"], [r["com"][0], r["com"][2]]); r["mCap"] = poly_margin(r["sup"], r["cap"])
        r["out"] = len(r["sup"]) > 0 and r["mCap"] < -BAL_OUT_CM; r["state"] = "ok"
    issues = []; i = 0
    while i < N:
        if not rows[i]["out"]: i += 1; continue
        j, land = i, -1
        while True:
            nk = j + 1
            if (nk >= N and not loop) or nk >= N + i: break
            prev, cur = at(j), at(nk)
            if cur["touch"] - prev["touch"]: land = nk; break
            if not cur["out"] or nk >= N: break
            j = nk
        run = rows[i:j + 1]; worst = min(run, key=lambda r: r["mCap"]); com_out = any(r["mCom"] < -BAL_OUT_CM for r in run); kind = None
        if land >= 0:
            L = at(land)
            if poly_margin(L["sup"], [L["com"][0], L["com"][2]]) <= -BAL_OUT_CM: kind = "missed"
        elif len(run) > BAL_RUN: kind = "lean" if com_out else "momentum"
        for r in run: r["state"] = "bad" if kind else "step"
        if kind == "lean": w2 = min(run, key=lambda r: r["mCom"]); issues.append(dict(kind=kind, frm=rows[i]["f"], to=rows[j]["f"], cm=round(-w2["mCom"]), at=w2["f"]))
        elif kind: issues.append(dict(kind=kind, frm=rows[i]["f"], to=rows[j]["f"], cm=round(-worst["mCap"]), at=worst["f"]))
        i = j + 1
    i = 0
    while i < N:                                  # airborne: the CoM must fall with g
        if rows[i]["touch"]: i += 1; continue
        j = i
        while j + 1 < N and not rows[j + 1]["touch"]: j += 1
        if j - i + 1 >= 3:
            acc = sum((at(k + 1)["com"][1] - 2 * rows[k]["com"][1] + at(k - 1)["com"][1]) * fps * fps / 100 for k in range(i, j + 1)) / (j - i + 1)
            ratio = -acc / BAL_G
            if ratio < 0.7 or ratio > 1.3:
                for k in range(i, j + 1): rows[k]["state"] = "bad"
                issues.append(dict(kind="air", frm=rows[i]["f"], to=rows[j]["f"], ratio=round(ratio, 2), at=rows[i]["f"]))
        i = j + 1
    falls = bal_falls(rows, fps)
    issues = [it for it in issues if not any(it["frm"] <= fl["to"] and it["to"] >= fl["from"] for fl in falls)]
    for fl in falls:
        d = 0 if fl["refF"] is None else fl["animF"] - fl["refF"]
        if abs(d) >= FALL_TOL_F or fl["easeOut"]: issues.append(dict(kind="fall", frm=fl["from"], to=fl["to"], d=round(d, 1), at=fl["from"], easeOut=fl["easeOut"]))
    return rows, issues, falls

# ---------------- falls (fall pack, docs/poselab_physics_p4_fall.md): same steps as the page, cm ----------------
FALL_K, FALL_TOL_F = 30.0, 2
def fall_ref(rows, i, land, fps):
    r0, prev, nxt, L = rows[i], rows[max(0, i - 1)], rows[min(len(rows) - 1, i + 1)], rows[land]
    src = prev if prev["feet"] else r0; sup = src["feet"] if src["feet"] else src["sup"]
    d = np.array([L["com"][0] - r0["com"][0], L["com"][2] - r0["com"][2]]); d = d / np.linalg.norm(d) if d @ d > 1e-4 else np.array([1.0, 0.0])
    piv = max(sup, key=lambda p: p[0] * d[0] + p[1] * d[1]) if sup else [r0["com"][0], r0["com"][2]]
    arm = lambda c: (c[0] - piv[0], c[1], c[2] - piv[1])
    tilt = lambda c: math.atan2(arm(c)[0] * d[0] + arm(c)[2] * d[1], arm(c)[1])
    a0 = arm(r0["com"]); h = math.hypot(a0[0] * d[0] + a0[2] * d[1], a0[1])
    span = max(1, min(len(rows) - 1, i + 1) - max(0, i - 1)); th0 = tilt(r0["com"]); w0 = (tilt(nxt["com"]) - tilt(prev["com"])) / span * fps
    horiz = math.hypot(L["com"][0] - r0["com"][0], L["com"][2] - r0["com"][2]); drop = r0["com"][1] - L["com"][1]
    kind = "collapse" if horiz < 0.3 * drop else "topple"; g = BAL_G * 100; t_hit = None
    if kind == "topple":
        th, w, t, dt, A = th0, w0, 0.0, 1 / (fps * 50), g * h / (h * h + FALL_K * FALL_K)
        for _ in range(fps * 50 * 6):
            if h * math.cos(th) <= L["com"][1] or th >= math.pi / 2: t_hit = t; break
            w += A * math.sin(th) * dt; th += w * dt; t += dt
    else:
        v0 = min(0.0, (nxt["com"][1] - prev["com"][1]) / span * fps)
        t_hit = (v0 + math.sqrt(v0 * v0 + 2 * g * max(0.0, drop))) / g
    vs = [-(rows[k]["com"][1] - rows[k - 1]["com"][1]) * fps / 100 for k in range(i + 1, land + 1)]
    peak = max(vs + [0.0]); last_v = vs[-1] if vs else 0.0
    return dict(kind=kind, **{"from": r0["f"]}, to=L["f"], animF=L["f"] - r0["f"], refF=None if t_hit is None else round(t_hit * fps, 1),
                easeOut=len(vs) >= 3 and peak > 0.5 and last_v < 0.6 * peak)
def bal_falls(rows, fps):
    out = []
    for k in range(1, len(rows)):
        if not (rows[k]["bodyLow"] <= FLOOR_TH_CM and rows[k - 1]["bodyLow"] > FLOOR_TH_CM): continue
        s = k
        while s > 0 and rows[s - 1]["com"][1] >= rows[s]["com"][1] - 0.2 and k - s < 2 * fps: s -= 1
        while s < k and not rows[s]["out"] and rows[s]["mCom"] > 5.0: s += 1
        if s >= k or rows[s]["com"][1] - rows[k]["com"][1] < 25.0: continue
        out.append(fall_ref(rows, s, k, fps))
    return out

# ---------------- impacts (p5 step 1, docs/poselab_physics_p5_impact.md): same steps as the page, page world (m) ----------------
IMP_RHO, IMP_TONE, IMP_HIP = 1000.0, 0.6, 0.08
IMP_SPR = {"trunk": (15, 0.55, 20), "head": (12, 0.62, 30), "arm": (8, 0.62, 35), "rootRot": (18, 0.4, 18)}
IMP_ROOT_K, IMP_ROOT_C = (2 * math.pi / 12) ** 2, 2 * 0.6 * 2 * math.pi / 12
IMP_STEP = dict(out=0.05, maxLen=0.8, minWidth=0.2, lift=0.06, max=3)
IMP_LEVEL = {"light": (0.3, 1), "medium": (1.0, 2), "strong": (2.5, 3), "launch": (5.0, 5)}
GROUND = 0.05
def imp_spring(n): return IMP_SPR["trunk"] if n in ("Root_M", "Spine1_M", "Chest_M") else IMP_SPR["head"] if n in ("Neck_M", "Head_M") else IMP_SPR["arm"]
def imp_k(sp):
    w = 2 * math.pi / sp[0]; z = 1 - sp[1]; return dict(w=w, z=z, wd=w * math.sqrt(max(1e-6, 1 - z * z)), L=math.radians(sp[2]))
def imp_g(k, t): return 0.0 if t <= 0 else math.exp(-k["z"] * k["w"] * t) * math.sin(k["wd"] * t) / k["wd"]
def poly_clamp(poly, q, out=0.0):
    if poly_margin(poly, q) >= -out: return list(q)
    best, bd = None, 1e9
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]; ex, ey = b[0] - a[0], b[1] - a[1]; L2 = ex * ex + ey * ey
        t = max(0.0, min(1.0, ((q[0] - a[0]) * ex + (q[1] - a[1]) * ey) / L2)) if L2 > 1e-12 else 0.0
        p2 = [a[0] + ex * t, a[1] + ey * t]; d = math.hypot(p2[0] - q[0], p2[1] - q[1])
        if d < bd: bd, best = d, p2
    if best and out:
        dx, dz = q[0] - best[0], q[1] - best[1]; l = math.hypot(dx, dz)
        if l > 1e-9: best = [best[0] + dx / l * out, best[1] + dz / l * out]
    return best or list(q)
class PageView:                     # a Rig seen in the page's world (metres; bone unit frames)
    def __init__(self, rig, A):
        self.rig, self.A = rig, A; s = np.linalg.norm(A[:3, 0]); self.S = A[:3, :3] / s
    def world(self, n): R, p = self.rig.world(n); return self.S @ R, self.A[:3, :3] @ p + self.A[:3, 3]
    def wq(self, n): return self.world(n)[0]
    def wp(self, n): return self.world(n)[1]
    def to_py_p(self, p): return np.linalg.solve(self.A[:3, :3], p - self.A[:3, 3])
    def set_world(self, n, R, p): self.rig.set_world(n, self.S.T @ R, self.to_py_p(p))
    def rotate_world(self, n, Q): self.rig.rotate_world(n, self.S.T @ Q @ self.S)
class Impacts:
    def __init__(self, dump, par):
        self.d, self.par = dump, par; b = dump["body"]
        self.caps = {k: (np.array(c["a"]) / 100, np.array(c["b"]) / 100, c["r"] / 100) for k, c in b["caps"].items()}
        self.shells = {k: np.array(v, float) / 100 for k, v in b["shells"].items()}; self.props = b["props"]
        self.A = np.array(dump["arm"], float).reshape(4, 4).T; self.fps = dump.get("fps", 30); self.cfg = dump["cfg"]
        self.lanes = {k: parse_set(v) for k, v in (dump.get("lanes") or {}).items()}; self.hand = dump["hand"]
        self.m = {}; M = 0.0
        for k, (a, bb, r) in self.caps.items(): L = np.linalg.norm(bb - a); self.m[k] = IMP_RHO * (math.pi * r * r * L + 4 / 3 * math.pi * r ** 3); M += self.m[k]
        self.pm = M * dump["propMass"] / 100; self.M = M + self.pm
        def segpar(k):
            x = par.get(k)
            while x is not None:
                if x in self.caps: return x
                x = par.get(x)
            return None
        segs = [dict(k=k, par=segpar(k)) for k in self.caps]
        def depth(s):
            n, x = 0, s["par"]
            while x: n += 1; x = next(o for o in segs if o["k"] == x)["par"]
            return n
        for s in segs: s["d"] = depth(s)
        self.segs = sorted(segs, key=lambda s: s["d"]); self.root = self.segs[0]["k"]
    def view(self, f): return PageView(Rig(self.par, {n: unpack(v) for n, v in self.d["base"][str(f)].items()}), self.A)
    def capw(self, pv, k): R, p = pv.world(k); a, b, r = self.caps[k]; return R @ a + p, R @ b + p, r
    def shellw(self, pv, k): R, p = pv.world(k); return self.shells[k] @ R.T + p
    def com(self, pv):
        c, M = np.zeros(3), 0.0
        for k in self.caps: a, b, _ = self.capw(pv, k); c += (a + b) / 2 * self.m[k]; M += self.m[k]
        pr = self.props[0] if self.props else None
        if pr and self.pm > 0: c += self.shellw(pv, pr).mean(0) * self.pm; M += self.pm
        return c / M
    def solve(self, pv, seg, x, j, tone):
        segs = self.segs; idx = {}; n = 6
        for s in segs:
            if s["par"]: idx[s["k"]] = n; n += 3
        pr = pv.wp(self.root); piv = {s["k"]: pv.wp(s["k"]) for s in segs}
        def chain(k):
            c, s = [], next(o for o in segs if o["k"] == k)
            while s and s["par"]: c.append(s["k"]); s = next(o for o in segs if o["k"] == s["par"])
            return c
        Mx = np.zeros((n, n))
        def jac(k, x0):
            Jv, Jw = np.zeros((3, n)), np.zeros((3, n)); Jv[:, 0:3] = np.eye(3)
            for c0, p in [(3, pr)] + [(idx[c], piv[c]) for c in chain(k)]:
                r = x0 - p; Jv[:, c0:c0 + 3] = np.array([[0, r[2], -r[1]], [-r[2], 0, r[0]], [r[1], -r[0], 0]]); Jw[:, c0:c0 + 3] = np.eye(3)
            return Jv, Jw
        for s in segs:
            k = s["k"]; a, b, r = self.capw(pv, k); L = np.linalg.norm(b - a); mm = self.m[k]; u = (b - a) / L
            I = mm * (3 * r * r + L * L) / 12 * (np.eye(3) - np.outer(u, u)) + 0.5 * mm * r * r * np.outer(u, u)
            Jv, Jw = jac(k, (a + b) / 2); Mx += mm * Jv.T @ Jv + Jw.T @ I @ Jw
        hk = "Wrist_" + self.hand; prop = self.props[0] if self.props else None
        if prop and self.pm > 0 and hk in self.caps: Jv, _ = jac(hk, self.shellw(pv, prop).mean(0)); Mx += self.pm * Jv.T @ Jv
        Jx, _ = jac(seg if seg in self.caps else hk, x); Q = Jx.T @ j
        Mx += np.eye(n) * 1e-9 * np.max(np.diag(Mx))
        qd = np.linalg.solve(Mx, Q); qr = np.linalg.solve(Mx[:6, :6], Q[:6])
        qd = (1 - tone) * qd; qd[:6] += tone * qr
        rel = {s["k"]: qd[idx[s["k"]]:idx[s["k"]] + 3] for s in segs if s["par"]}; ab = {}
        for s in segs: ab[s["k"]] = (ab[s["par"]] + rel[s["k"]]) if s["par"] else qd[3:6].copy()
        return dict(v=qd[0:3], w=qd[3:6], rel=rel, abs=ab, ke=0.5 * qd @ Mx @ qd)
    def point(self, pv, i):
        R, p = pv.world(i["seg"]); x = R @ np.array(i["p"]) + p
        if i.get("dirMode", "normal") == "normal" or not i.get("dir"):
            if i["seg"] in self.caps: a, b, _ = self.capw(pv, i["seg"]); d = closest_on(x[None], a, b)[0] - x
            else: d = self.shellw(pv, i["seg"]).mean(0) - x
        else: d = np.array(i["dir"], float)
        return x, d / np.linalg.norm(d)
    def contact(self, pv, s, f):
        if self.lanes.get("L") or self.lanes.get("R"): return f in self.lanes.get(s, set())
        return float(self.shellw(pv, "Ankle_" + s)[:, 1].min()) < GROUND
    def run(self):
        cfg, fps = self.cfg, self.fps; tone = cfg.get("tone") if cfg.get("tone") is not None else IMP_TONE; auto = cfg.get("autoStep", True) is not False
        hits = []
        for i in cfg["impacts"]:
            pv = self.view(i["f"]); x, d = self.point(pv, i); lv = IMP_LEVEL.get(i.get("level"))
            dv = (lv[0] if lv else i.get("dv", 1)) * i.get("mul", 1); dur = max(1, round_js(i["dur"] if i.get("dur") is not None else (lv or IMP_LEVEL["medium"])[1]))
            j = d * dv * self.M; r = self.solve(pv, i["seg"], x, j, tone)
            parQ = {k: pv.wq(next(s for s in self.segs if s["k"] == k)["par"]) for k in r["rel"]}
            hits.append(dict(f=i["f"], dur=dur, x=x, j=j, r=r, parQ=parQ))
        hits.sort(key=lambda h: h["f"]); f0 = hits[0]["f"]
        S = dict(x=np.zeros(3), v=np.zeros(3), foot={"L": np.zeros(3), "R": np.zeros(3)}, stepping=None, steps=[], need=[], fell=None, n=0,
                 comPrev=self.com(self.view(max(1, f0 - 1))))
        rec, pre = {}, {}
        rot_k = imp_k(IMP_SPR["rootRot"]); jk = {s["k"]: imp_k(imp_spring(s["k"])) for s in self.segs if s["par"]}
        for f in range(f0, self.d["frames"] + 1):
            first = f == 1; pv = self.view(f); keyCon = {s: self.contact(pv, s, f) for s in "LR"}
            keyAnk = {s: pv.world(LEGS_PY[s][2]) for s in "LR"}
            comKey = self.com(pv); vKey = (comKey - S["comPrev"]) * fps; S["comPrev"] = comKey
            if S["stepping"]:
                st = S["stepping"]; u = min(1.0, (f - st["f0"]) / (st["f1"] - st["f0"]))
                S["foot"][st["s"]] = st["from"] + (st["to"] - st["from"]) * smooth01(u); S["foot"][st["s"]][1] = math.sin(math.pi * u) * IMP_STEP["lift"]
                if u >= 1: S["foot"][st["s"]][1] = 0.0; S["stepping"] = None
            for s in "LR":
                if not keyCon[s] and not (S["stepping"] and S["stepping"]["s"] == s): S["foot"][s] = S["foot"][s] * 0.75
            feet, pts = {}, []
            for s in "LR":
                o = S["foot"][s]; feet[s] = self.shellw(pv, "Ankle_" + s) + o
                if keyCon[s] and not (S["stepping"] and S["stepping"]["s"] == s): pts += [[q[0], q[2]] for q in feet[s] if q[1] < GROUND + o[1]]
            hull = hull2(pts)
            for h in hits:
                if h["f"] <= f < h["f"] + h["dur"]: S["v"] = S["v"] + h["j"] / self.M / fps / h["dur"]
            w0 = math.sqrt(9.81 / max(0.3, comKey[1])) / fps; rest = (S["foot"]["L"] + S["foot"]["R"]) / 2; rest[1] = 0
            ptsK0 = [[(q - S["foot"][s])[0], (q - S["foot"][s])[2]] for s in "LR" if keyCon[s] for q in feet[s] if (q - S["foot"][s])[1] < GROUND]
            hk = hull2(ptsK0); copK = poly_clamp(hk, [comKey[0], comKey[2]]) if hk else [comKey[0], comKey[2]]
            if not first:
                for _ in range(8):
                    xi = [S["x"][0] + S["v"][0] / w0, S["x"][2] + S["v"][2] / w0]
                    u = [rest[0] + 2 * (xi[0] - rest[0]), rest[2] + 2 * (xi[1] - rest[2])]
                    if hull: c = poly_clamp(hull, [copK[0] + u[0], copK[1] + u[1]], IMP_HIP); u = [c[0] - copK[0], c[1] - copK[1]]
                    else: u = [S["x"][0], S["x"][2]]
                    ax, az = w0 * w0 * (S["x"][0] - u[0]), w0 * w0 * (S["x"][2] - u[1]); ay = IMP_ROOT_K * (0 - S["x"][1]) - IMP_ROOT_C * S["v"][1]
                    S["v"] = S["v"] + np.array([ax, ay, az]) / 8; S["x"] = S["x"] + S["v"] / 8
            S["x"][1] = max(-0.15, min(0.05, S["x"][1]))
            com = comKey + S["x"]; v = vKey + S["v"] * fps; wS = w0 * fps
            cp = [com[0] + v[0] / wS, com[2] + v[2] / wS]; mg = poly_margin(hull, cp) if hull else -1
            ptsK = [[(q - S["foot"][s])[0], (q - S["foot"][s])[2]] for s in "LR" if keyCon[s] for q in feet[s] if (q - S["foot"][s])[1] < GROUND]
            wK = math.sqrt(9.81 / max(0.3, comKey[1])); hK = hull2(ptsK); mgK = poly_margin(hK, [comKey[0] + vKey[0] / wK, comKey[2] + vKey[2] / wK]) if hK else 0
            worse = min(0, mgK) - mg; sp = math.hypot(S["v"][0], S["v"][2]) * fps; Ts = max(8, min(10, round_js(10 - 3 * (sp - 0.5))))
            lanes = self.lanes.get("L") or self.lanes.get("R")
            planted = lambda s: not lanes or all(((f + t) in self.lanes.get(s, set())) for t in range(Ts + 1))
            rec[f] = dict(x=S["x"].copy(), foot={s: S["foot"][s].copy() for s in "LR"}, cp=cp, mg=mg, mgK=mgK)
            if not S["stepping"] and hull and worse > IMP_STEP["out"] and f >= f0:
                dd = np.array([cp[0] - com[0], 0, cp[1] - com[2]]); dd = dd / np.linalg.norm(dd) if dd @ dd > 1e-8 else np.array([0, 0, -1.0])
                gr = math.exp(w0 * Ts); best = None
                for s in "LR":
                    o = "R" if s == "L" else "L"
                    if not keyCon[s] or not planted(s): continue
                    po = [[q[0], q[2]] for q in feet[o] if q[1] < GROUND + S["foot"][o][1]]; ho = hull2(po)
                    co = feet[o].mean(0); cs = feet[s].mean(0)
                    uo = poly_clamp(ho, cp, IMP_HIP) if ho else [co[0], co[2]]
                    T = np.array([uo[0] + (cp[0] - uo[0]) * gr, 0, uo[1] + (cp[1] - uo[1]) * gr]) + dd * 0.05
                    side = cs - co; side[1] = 0; sd = side / np.linalg.norm(side) if np.linalg.norm(side) > 1e-4 else None
                    t = T.copy(); off = (t - co); off[1] = 0; off = off @ sd
                    if off < IMP_STEP["minWidth"]: t = t + sd * (IMP_STEP["minWidth"] - off)
                    dl = t - cs; dl[1] = 0; need = np.linalg.norm(dl)
                    if need > IMP_STEP["maxLen"]: dl = dl / need * IMP_STEP["maxLen"]
                    if best is None or need < best[2]: best = (s, dl, need, cs)
                if best and S["fell"] is None and best[2] > 2 * IMP_STEP["maxLen"]: S["fell"] = f
                elif best and S["fell"] is None and auto and S["n"] < IMP_STEP["max"]:
                    S["stepping"] = dict(s=best[0], f0=f, f1=f + Ts, **{"from": S["foot"][best[0]].copy()}, to=S["foot"][best[0]] + best[1]); S["n"] += 1
                    S["steps"].append(dict(s=best[0], f0=f, f1=f + Ts, cm=round_js(np.linalg.norm(best[1]) * 100)))
                elif best and not auto:
                    if not S["need"] or f - S["need"][-1]["f"] > 6: S["need"].append(dict(f=f, s=best[0], cm=round_js(worse * 100)))
                elif S["fell"] is None and S["n"] >= IMP_STEP["max"] and not S["stepping"]: S["fell"] = f
            if S["fell"] is not None: S["v"] = S["v"] * 0.6
            # pose (trunk part only: root turn about the CoM + move, spine / neck / head offsets)
            rv = np.zeros(3); capR = rot_k["L"] * rot_k["w"] * fps
            for h in hits:
                w = h["r"]["w"].copy(); n_ = np.linalg.norm(w)
                if n_ > capR: w = w / n_ * capR
                for k in range(h["dur"]): rv += w * imp_g(rot_k, f - h["f"] - k) / fps / h["dur"]
            a = np.linalg.norm(rv)
            if a > 1e-9: rv = rv * soft_limit(a, rot_k["L"]) / a
            Q = rot(rv); Rr, pr = pv.world(self.root); to = comKey + Q @ (pr - comKey) + S["x"]
            pv.set_world(self.root, Q @ Rr, to)
            for s in self.segs:
                k = s["k"]
                if not s["par"] or k.startswith(("Hip_", "Knee_", "Ankle_", "Shoulder_", "Elbow_", "Wrist_")): continue
                sp_ = jk[k]; capW = sp_["L"] * sp_["w"] * fps; loc = np.zeros(3)
                for h in hits:
                    q = h["parQ"].get(k)
                    if q is None: continue
                    wl = q.T @ h["r"]["rel"][k]; n_ = np.linalg.norm(wl)
                    if n_ > capW: wl = wl / n_ * capW
                    for kk in range(h["dur"]): loc += wl * imp_g(sp_, f - h["f"] - kk) / fps / h["dur"]
                a = np.linalg.norm(loc)
                if a < 1e-9: continue
                loc = loc * soft_limit(a, sp_["L"]) / a
                pv.rotate_world(k, rot(pv.wq(s["par"]) @ loc))
            pre[f] = {n: pack(*pv.rig.L[n]) for n in ("Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M")}
        return dict(hits=hits, rec=rec, pre=pre, steps=S["steps"], need=S["need"], fell=S["fell"])
LEGS_PY = {"L": ("Hip_L", "Knee_L", "Ankle_L"), "R": ("Hip_R", "Knee_R", "Ankle_R")}
def round_js(x): return int(math.floor(x + 0.5))

# ---------------- ragdoll (p5 step 2): the page's XPBD solver, same operations in the same order (three.js formulas) ----------------
# Input: the page's trace (window.__ragRec): the bodies / joints / contacts at the start and each frame's muscle targets,
# strengths and kicks. Output: every body's position + turn per frame, compared with the page's own.
R_SUB, R_JIT, R_C0, R_MU_S, R_MU_D, R_DAMP = 20, 2, 1e-6, 0.8, 0.6, 18
R_PASSIVE, R_ROLL, R_LIM_A, R_LIM_D, R_SLEEP_CM, R_SLEEP_F = 8, 12, 0, 100, 2.5, 6
R_BSEP, R_BBIAS, R_SLOP, R_G, R_BOUNCE = 0.1, 2, 0.005, 9.81, 0.15
R_CB, R_CBP, R_SOLE, R_HIP = 1e-6, 2e-5, 0.02, 0.08     # step 3 balance (page: RAG_CB, RAG_CBP, RAG_SOLE, IMP_HIP)
def v_add(a, b): return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
def v_sub(a, b): return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
def v_mul(a, s): return [a[0] * s, a[1] * s, a[2] * s]
def v_dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def v_len(a): return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
def v_cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def v_div(a, s): return v_mul(a, 1 / s)
def q_mul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return [ax * bw + aw * bx + ay * bz - az * by, ay * bw + aw * by + az * bx - ax * bz, az * bw + aw * bz + ax * by - ay * bx, aw * bw - ax * bx - ay * by - az * bz]
def q_inv(q): return [-q[0], -q[1], -q[2], q[3]]
def q_norm(q):
    l = math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3])
    if l == 0: return [0.0, 0.0, 0.0, 1.0]
    l = 1 / l; return [q[0] * l, q[1] * l, q[2] * l, q[3] * l]
def q_apply(v, q):
    x, y, z = v; qx, qy, qz, qw = q
    ix = qw * x + qy * z - qz * y; iy = qw * y + qz * x - qx * z; iz = qw * z + qx * y - qy * x; iw = -qx * x - qy * y - qz * z
    return [ix * qw + iw * -qx + iy * -qz - iz * -qy, iy * qw + iw * -qy + iz * -qx - ix * -qz, iz * qw + iw * -qz + ix * -qy - iy * -qx]
def q_axis(ax, ang): s = math.sin(ang / 2); return [ax[0] * s, ax[1] * s, ax[2] * s, math.cos(ang / 2)]
def q_rv(v):
    a = v_len(v)
    return [0.0, 0.0, 0.0, 1.0] if a < 1e-12 else q_axis(v_div(v, a), a)
def q_log(q):
    w = -1 if q[3] < 0 else 1; x, y, z = q[0] * w, q[1] * w, q[2] * w; s = math.sqrt(x * x + y * y + z * z)
    if s < 1e-12: return [0.0, 0.0, 0.0]
    a = 2 * math.atan2(s, q[3] * w); return [x * a / s, y * a / s, z * a / s]
def m3_apply(v, e): x, y, z = v; return [e[0] * x + e[3] * y + e[6] * z, e[1] * x + e[4] * y + e[7] * z, e[2] * x + e[5] * y + e[8] * z]
def m3_inv(te):
    n11, n21, n31, n12, n22, n32, n13, n23, n33 = te
    t11 = n33 * n22 - n32 * n23; t12 = n32 * n13 - n33 * n12; t13 = n23 * n12 - n22 * n13; det = n11 * t11 + n21 * t12 + n31 * t13; di = 1 / det
    return [t11 * di, (n31 * n23 - n33 * n21) * di, (n32 * n21 - n31 * n22) * di, t12 * di, (n33 * n11 - n31 * n13) * di, (n31 * n12 - n32 * n11) * di,
            t13 * di, (n21 * n13 - n23 * n11) * di, (n22 * n11 - n21 * n12) * di]
def closest_seg(p, a, b):
    ab = v_sub(b, a); t = min(1, max(0, v_dot(v_sub(p, a), ab) / max(v_dot(ab, ab), 1e-12))); return v_add(a, v_mul(ab, t))
def seg_closest(p1, q1, p2, q2):
    d1, d2, r = v_sub(q1, p1), v_sub(q2, p2), v_sub(p1, p2); a, e, f = v_dot(d1, d1), v_dot(d2, d2), v_dot(d2, r)
    c, b = v_dot(d1, r), v_dot(d1, d2); den = a * e - b * b
    s = min(1, max(0, (b * f - c * e) / den)) if den > 1e-12 else 0; t = (b * s + f) / e if e > 1e-12 else 0
    if t < 0: t = 0; s = min(1, max(0, -c / a)) if a > 1e-12 else 0
    elif t > 1: t = 1; s = min(1, max(0, (b - c) / a)) if a > 1e-12 else 0
    return v_add(p1, v_mul(d1, s)), v_add(p2, v_mul(d2, t))
class RagBody:
    def __init__(s, d):
        s.k, s.m, s.c, s.I = d["k"], d["m"], d["c"], d["I"]; s.im = 1 / s.m; s.Ii = m3_inv(s.I)
        s.x, s.q, s.v, s.w = list(d["x"]), list(d["q"]), list(d["v"]), list(d["w"]); s.xp, s.qp = list(s.x), list(s.q)
        s.pts = [list(p) for p in d["pts"]]; s.ppts = [list(p) for p in d["ppts"]] if d.get("ppts") else None; s.cap = d["cap"]; s.vn = []
def r_iiw(b, v): return q_apply(m3_apply(q_apply(v, q_inv(b.q)), b.Ii), b.q)
def r_w(b, r, n):
    if b is None or not b.im: return 0
    rn = v_cross(r, n); return b.im + v_dot(rn, r_iiw(b, rn))
def r_rot(b, d):
    q = b.q; dq = q_mul([d[0] * 0.5, d[1] * 0.5, d[2] * 0.5, 0], q); b.q = q_norm([q[0] + dq[0], q[1] + dq[1], q[2] + dq[2], q[3] + dq[3]])
def r_pos(b1, r1, b2, r2, n, c, alpha, h):
    w = r_w(b1, r1, n) + r_w(b2, r2, n); at = alpha / (h * h)
    if w + at < 1e-12: return 0
    dl = c / (w + at); p = v_mul(n, dl)
    if b1 is not None and b1.im: b1.x = v_add(b1.x, v_mul(p, b1.im)); r_rot(b1, r_iiw(b1, v_cross(r1, p)))
    if b2 is not None and b2.im: b2.x = v_add(b2.x, v_mul(p, -b2.im)); r_rot(b2, v_mul(r_iiw(b2, v_cross(r2, p)), -1))
    return dl
def r_ang(b1, b2, phi, alpha, h):
    th = v_len(phi)
    if th < 1e-10: return
    n = v_div(phi, th); w = (v_dot(n, r_iiw(b1, n)) if b1 else 0) + (v_dot(n, r_iiw(b2, n)) if b2 else 0); at = alpha / (h * h)
    if w + at < 1e-12: return
    p = v_mul(n, th / (w + at))
    if b1: r_rot(b1, r_iiw(b1, p))
    if b2: r_rot(b2, v_mul(r_iiw(b2, p), -1))
def r_pt(b, r): return v_add(q_apply(r, b.q), b.x)
def r_vrel(A, rA, Bb, rB, n): return v_dot(v_sub(v_sub(v_add(A.v, v_cross(A.w, rA)), Bb.v), v_cross(Bb.w, rB)), n)
def r_split(d, j):
    dq = [-d[0], -d[1], -d[2], -d[3]] if d[3] < 0 else list(d); t = j["t"]
    tw = 2 * math.atan2(dq[0] * t[0] + dq[1] * t[1] + dq[2] * t[2], dq[3])
    if tw > math.pi: tw -= 2 * math.pi
    if tw < -math.pi: tw += 2 * math.pi
    sv = q_log(q_mul(dq, q_inv(q_axis(t, tw)))); return [v_dot(sv, j["e1"]), v_dot(sv, j["e2"]), tw]
def r_join(a, j): return q_mul(q_rv(v_add(v_mul(j["e1"], a[0]), v_mul(j["e2"], a[1]))), q_axis(j["t"], a[2]))
def r_unwrap(a, prev):
    if prev is None: return a
    out = list(a); m = math.hypot(a[0], a[1])
    if m > 1e-9:
        k = (m - 2 * math.pi) / m; alt = [a[0] * k, a[1] * k]
        if math.hypot(alt[0] - prev[0], alt[1] - prev[1]) < math.hypot(a[0] - prev[0], a[1] - prev[1]): out[0], out[1] = alt
    while out[2] - prev[2] > math.pi: out[2] -= 2 * math.pi
    while out[2] - prev[2] < -math.pi: out[2] += 2 * math.pi
    return out
def r_turn(j, B_, keep=False):
    t = r_unwrap(r_split(q_mul(q_inv(j["q0"]), q_mul(q_inv(B_[j["p"]].q), B_[j["c"]].q)), j), j["prev"])
    if keep: j["prev"] = t
    return t
def rag_balance(RG, bal, h):
    B_ = RG["bodies"]; L = [B_[k] for k in RG["list"]]; pts = []
    for k in ("Ankle_L", "Ankle_R"):
        b = B_.get(k)
        if b is not None and b.vn:
            for pl in b.pts:
                p = r_pt(b, pl)
                if p[1] < R_SOLE: pts.append([p[0], p[2]])
    if not pts: return
    M, c, v = 0, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
    for b in L: c = v_add(c, v_mul(b.x, b.m)); v = v_add(v, v_mul(b.v, b.m)); M += b.m
    c = v_div(c, M); v = v_div(v, M); w0 = math.sqrt(R_G / max(0.3, c[1])); cp = [c[0] + v[0] / w0, c[2] + v[2] / w0]
    if poly_margin(hull2(pts), cp) <= -R_HIP: return
    rb = B_[RG["root"]]; s3 = bal["s"] * bal["s"] * bal["s"]
    r_ang(rb, None, q_log(q_mul(bal["qt"], q_inv(rb.q))), R_CB / s3, h)
    d = v_sub(bal["xt"], rb.x); d[1] = 0; cc = v_len(d)
    if cc > 1e-9: r_pos(rb, [0.0, 0.0, 0.0], None, None, v_div(d, cc), min(cc, R_MU_D * R_G * h * h * M / rb.m), R_CBP / s3, h)
def rag_frame(RG, targets, s_of, kicks, fps, bal=None):
    h = 1 / fps / R_SUB; B_ = RG["bodies"]; L = [B_[k] for k in RG["list"]]
    for kk in kicks:
        b = B_[kk["b"]]; r = q_apply(kk["r"], b.q); b.v = v_add(b.v, v_mul(kk["j"], b.im)); b.w = v_add(b.w, r_iiw(b, v_cross(r, kk["j"])))
    for _ in range(R_SUB):
        for b in L:
            b.xp, b.qp = list(b.x), list(b.q); b.v = [b.v[0], b.v[1] + -R_G * h, b.v[2]]; b.x = v_add(b.x, v_mul(b.v, h))
            d = q_mul([b.w[0] * 0.5 * h, b.w[1] * 0.5 * h, b.w[2] * 0.5 * h, 0], b.q); b.q = q_norm([b.q[0] + d[0], b.q[1] + d[1], b.q[2] + d[2], b.q[3] + d[3]])
        for j in RG["joints"]:
            s = s_of(j)
            if s < 0.02: continue
            c, p = B_[j["c"]], B_[j["p"]]; want = q_mul(q_mul(p.q, j["q0"]), targets[j["k"]])
            r_ang(c, p, q_log(q_mul(want, q_inv(c.q))), R_C0 / (s * s * s), h)
        if bal and bal["s"] >= 0.02: rag_balance(RG, bal, h)
        lims = []
        for _it in range(R_JIT):
            for j in RG["joints"]:
                c, p, lim = B_[j["c"]], B_[j["p"]], j["lim"]; t = r_turn(j, B_, True)
                cl = [max(lim[0], min(lim[1], t[0])), max(lim[2], min(lim[3], t[1])), max(lim[4], min(lim[5], t[2]))]
                if cl[0] != t[0] or cl[1] != t[1] or cl[2] != t[2]:
                    want = q_mul(q_mul(p.q, j["q0"]), r_join(cl, j)); phi = q_log(q_mul(want, q_inv(c.q))); th = v_len(phi)
                    if th > 1e-10: n = v_div(phi, th); lims.append((j, n, v_dot(v_sub(c.w, p.w), n)))
                    r_ang(c, p, phi, R_LIM_A, h)
            for j in RG["joints"]:
                c, p = B_[j["c"]], B_[j["p"]]; a = r_pt(c, j["rC"]); d = v_sub(r_pt(p, j["rP"]), a); cc = v_len(d)
                if cc > 1e-9: r_pos(c, q_apply(j["rC"], c.q), p, q_apply(j["rP"], p.q), v_div(d, cc), cc, 0, h)
        for b in L:
            b.vn = []
            for pl in b.pts:
                r = q_apply(pl, b.q); y = b.x[1] + r[1]
                if y >= 0: continue
                prev = v_add(q_apply(pl, b.qp), b.xp); vpre = b.v[1] + b.w[2] * r[0] - b.w[0] * r[2]
                dl = r_pos(b, r, None, None, [0, 1, 0], -y, 0, h)
                dt = v_sub(r_pt(b, pl), prev); dt[1] = 0; lt = v_len(dt)
                if lt > 1e-9 and lt < R_MU_S * -y: r_pos(b, q_apply(pl, b.q), None, None, v_mul(v_div(dt, lt), -1), lt, 0, h)
                b.vn.append((pl, dl, vpre))
        for b in L:
            b.v = v_div(v_sub(b.x, b.xp), h); dq = q_mul(b.q, q_inv(b.qp)); b.w = v_mul([dq[0], dq[1], dq[2]], 2 / h)
            if dq[3] < 0: b.w = v_mul(b.w, -1)
        for b in L:
            for pl, dl, vpre in b.vn:
                r = q_apply(pl, b.q); vp = v_add(b.v, v_cross(b.w, r)); vn = vp[1]; vt = [vp[0], 0, vp[2]]
                lt = v_len(vt); fn = dl / (h * h)
                vT = -R_BOUNCE * vpre if vpre < -2 * R_G * h else max(0, vpre); up = [0.0, 1.0, 0.0]; wn = r_w(b, r, up)
                if abs(vT - vn) > 1e-12:
                    p = v_mul(up, (vT - vn) / wn); b.v = v_add(b.v, v_mul(p, b.im)); b.w = v_add(b.w, r_iiw(b, v_cross(r, p)))
                if lt > 1e-9:
                    tt = v_div(vt, lt); vt2 = v_dot(v_add(b.v, v_cross(b.w, r)), tt); wt = r_w(b, r, tt)
                    if vt2 <= 0: continue
                    jt = min(h * R_MU_D * abs(fn), vt2 / wt); p = v_mul(tt, -jt); b.v = v_add(b.v, v_mul(p, b.im)); b.w = v_add(b.w, r_iiw(b, v_cross(r, p)))
        def vhit(A, rA, Bb, rB, n, depth):
            vr = r_vrel(A, rA, Bb, rB, n); vT = min(R_BSEP, R_BBIAS * max(0, depth - R_SLOP))
            if vr >= vT: return
            w = r_w(A, rA, n) + r_w(Bb, rB, n); p = v_mul(n, (vT - vr) / w)
            A.v = v_add(A.v, v_mul(p, A.im)); A.w = v_add(A.w, r_iiw(A, v_cross(rA, p))); Bb.v = v_add(Bb.v, v_mul(p, -Bb.im)); Bb.w = v_sub(Bb.w, r_iiw(Bb, v_cross(rB, p)))
        for pr in RG["pairs"]:
            A, Bb = B_[pr["a"]], B_[pr["b"]]; pa, pb = seg_closest(r_pt(A, A.cap["a"]), r_pt(A, A.cap["b"]), r_pt(Bb, Bb.cap["a"]), r_pt(Bb, Bb.cap["b"]))
            d = v_sub(pa, pb); dist = v_len(d); need = A.cap["r"] + Bb.cap["r"] - pr["allow"]
            if dist < need and dist > 1e-9: vhit(A, v_add(v_sub(pa, A.x), v_mul(d, -A.cap["r"] / dist)), Bb, v_add(v_sub(pb, Bb.x), v_mul(d, Bb.cap["r"] / dist)), v_div(d, dist), need - dist)
        if RG["prop"] and RG["prop"] in B_ and not RG["hold"]:
            P_ = B_[RG["prop"]]
            for b in L:
                if b is P_ or not b.cap: continue
                a0, a1 = r_pt(b, b.cap["a"]), r_pt(b, b.cap["b"]); need = b.cap["r"] - (RG["propAllow"].get(b.k) or 0)
                for pl in P_.pts:
                    p = r_pt(P_, pl); cpt = closest_seg(p, a0, a1); d = v_sub(p, cpt); dist = v_len(d)
                    if dist < need and dist > 1e-9: vhit(P_, q_apply(pl, P_.q), b, v_sub(cpt, b.x), v_div(d, dist), need - dist)
        kr = min(1, R_ROLL * h)
        for b in L:
            if b.vn: b.w = v_mul(b.w, 1 - kr)
        for j, n, vpre in lims:
            c, p = B_[j["c"]], B_[j["p"]]; vr = v_dot(v_sub(c.w, p.w), n); vT = max(0, vpre)
            if vr > vT:
                w = v_dot(n, r_iiw(c, n)) + v_dot(n, r_iiw(p, n)); pp = v_mul(n, (vT - vr) / w); c.w = v_add(c.w, r_iiw(c, pp)); p.w = v_sub(p.w, r_iiw(p, pp))
            dw = v_sub(c.w, p.w); l = v_len(dw)
            if l < 1e-9: continue
            m = v_div(dw, l); w2 = v_dot(m, r_iiw(c, m)) + v_dot(m, r_iiw(p, m)); p2 = v_mul(m, -min(1, R_LIM_D * h) * l / w2); c.w = v_add(c.w, r_iiw(c, p2)); p.w = v_sub(p.w, r_iiw(p, p2))
        for j in RG["joints"]:
            c, p = B_[j["c"]], B_[j["p"]]; s = s_of(j); kk = R_PASSIVE + (0 if s < 0.02 else R_DAMP * s)
            dw = v_sub(c.w, p.w); k = min(1, kk * h); l = v_len(dw)
            if l < 1e-9: continue
            n = v_div(dw, l); w = v_dot(n, r_iiw(c, n)) + v_dot(n, r_iiw(p, n)); pp = v_mul(n, -k * l / w); c.w = v_add(c.w, r_iiw(c, pp)); p.w = v_sub(p.w, r_iiw(p, pp))
def rag_split_prop(RG):
    H, B_ = RG["hold"], RG["bodies"]; h, pr = B_[RG["hand"]], B_[RG["prop"]]
    rp = q_apply(v_sub(H["cP"], H["d"]), h.q); rh = q_apply(v_mul(H["d"], -1), h.q)
    pr.x = v_add(h.x, rp); pr.q = q_mul(h.q, H["qrel"]); pr.v = v_add(h.v, v_cross(h.w, rp)); pr.w = list(h.w)
    vh = v_add(h.v, v_cross(h.w, rh)); h.x = v_add(h.x, rh); h.v = vh
    h0 = H["h0"]; h.m, h.im, h.c, h.I = h0["m"], 1 / h0["m"], h0["c"], h0["I"]; h.Ii = m3_inv(h.I); h.pts = [list(p) for p in h0["pts"]]; h.cap = h0["cap"]; h.ppts = None
    RG["hold"] = None; RG["list"].append(RG["prop"])
    for j in RG["joints"]:
        if j["c"] == RG["hand"]: j["rC"] = v_mul(h.c, -1)
def ragdoll(trace, fps):
    ini = trace["init"]; RG = dict(ini); RG["bodies"] = {k: RagBody(d) for k, d in ini["bodies"].items()}; RG["list"] = list(ini["list"])
    RG["joints"] = [dict(j) for j in ini["joints"]]; out = {}
    for fs in sorted(trace["frames"], key=int):
        fr = trace["frames"][fs]; f = int(fs)
        if fr["released"] and RG["hold"]: rag_split_prop(RG)
        sv = fr["s"]
        if not fr["asleep"]: rag_frame(RG, fr["t"], lambda j: sv[j["k"]], fr["kicks"], fps, fr.get("bal"))
        out[f] = {k: RG["bodies"][k].x + RG["bodies"][k].q for k in RG["list"]}
        if fr["asleep"] is False and f + 1 <= max(map(int, trace["frames"])) and trace["frames"][str(f + 1)]["asleep"]:
            for k in RG["list"]: RG["bodies"][k].v, RG["bodies"][k].w = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
    return out

def compare(dump, out, bones):
    rows = {}
    for n in bones:
        e = [math.degrees(np.linalg.norm(rvec(q2m(dump["out"][str(f)][n][:4]), q2m(out[f][n][:4])))) for f in sorted(out)]
        rows[n] = (max(e), sorted(out)[int(np.argmax(e))])
    return rows

if __name__ == "__main__":
    dump = json.load(open(sys.argv[1], encoding="utf8"))
    sys.path.insert(0, "work/boss_gaygor/gaygor_hit")
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()): import pose_build as pb
    par = {n: pb.PAR.get(n) for n in dump["base"]["1"]}
    if "--balance" in sys.argv:                  # balance of the shown poses vs the page's own rows
        rows, issues, falls = balance(dump, par); page = {r["f"]: r for r in dump["bal"]["rows"]}
        dc = max(abs(r["mCom"] - page[r["f"]]["mCom"]) for r in rows); dp = max(abs(r["mCap"] - page[r["f"]]["mCap"]) for r in rows)
        st = sum(r["state"] != page[r["f"]]["state"] for r in rows)
        print(f"CoM margin max diff {dc:.3f} cm, capture {dp:.3f} cm, state mismatches {st}")
        print("python issues:", [(i["kind"], i["frm"], i["to"], i.get("cm", i.get("ratio"))) for i in issues])
        print("page issues:  ", [(i["kind"], i["from"], i["to"], i.get("cm", i.get("ratio"))) for i in dump["bal"]["issues"]])
        print("python falls:", [(f_["kind"], f_["from"], f_["to"], f_["animF"], f_["refF"], f_["easeOut"]) for f_ in falls])
        print("page falls:  ", [(f_["kind"], f_["from"], f_["to"], f_["animF"], f_["refF"], f_["easeOut"]) for f_ in dump["bal"].get("falls", [])])
        fl = sorted({(k, r["f"]) for r in rows for k in r["floor"]}); print("python floor (part, frame):", len(fl), fl[:6])
        sys.exit(0)
    if "--ragdoll" in sys.argv:                  # ragdoll solver vs the page (same start state, targets, strengths, kicks)
        out = ragdoll(dump["trace"], dump.get("fps", 30)); pg = dump["bx"]; worst = []
        for f in sorted(out):
            dp = max(v_len(v_sub(out[f][k][:3], pg[str(f)][k][:3])) for k in out[f]) * 100
            da = max(math.degrees(2 * math.acos(min(1, abs(sum(a * b for a, b in zip(out[f][k][3:], pg[str(f)][k][3:])))))) for k in out[f])
            worst.append((f, dp, da))
        for f, dp, da in worst[:6] + worst[-3:]: print(f"F{f}: max body position diff {dp:.5f} cm, turn diff {da:.5f} deg")
        print("first frame over 0.1 cm:", next((f for f, dp, _ in worst if dp > 0.1), None), "| worst", max(w[1] for w in worst).__round__(3), "cm")
        sys.exit(0)
    if "--impact" in sys.argv:                   # impact stage vs the page's own (solve, hips / feet per frame, steps, trunk pose)
        im = Impacts(dump, par).run(); pg = dump["imp"]
        for h, ph in zip(im["hits"], pg["hits"]):
            dv = np.linalg.norm(h["r"]["v"] - np.array(ph["v"])); dw = np.linalg.norm(h["r"]["w"] - np.array(ph["w"]))
            print(f"hit F{h['f']}: root v diff {dv:.2e} m/s, w diff {dw:.2e} rad/s, KE {h['r']['ke']:.1f} vs {ph['ke']:.1f} J")
        dx = max(np.linalg.norm(r["x"] - np.array(pg["rec"][str(f)]["x"])) for f, r in im["rec"].items()) * 100
        dfo = max(np.linalg.norm(r["foot"][s_] - np.array(pg["rec"][str(f)]["foot"][s_])) for f, r in im["rec"].items() for s_ in "LR") * 100
        dm = max(abs(r["mg"] - pg["rec"][str(f)]["mg"]) for f, r in im["rec"].items()) * 100
        print(f"per frame: hips offset max diff {dx:.4f} cm, foot offsets {dfo:.4f} cm, capture margin {dm:.4f} cm")
        print("python steps:", [(x["s"], x["f0"], x["f1"], x["cm"]) for x in im["steps"]], "need", [(x["s"], x["f"], x["cm"]) for x in im["need"]], "fell", im["fell"])
        print("page steps:  ", [(x["s"], x["f0"], x["f1"], x["cm"]) for x in pg["steps"]], "need", [(x["s"], x["f"], x["cm"]) for x in pg["need"]], "fell", pg["fell"])
        worst = (0, None, None)
        for f, bones in im["pre"].items():
            for n, v in bones.items():
                e = math.degrees(np.linalg.norm(rvec(q2m(pg["pre"][str(f)][n][:4]), q2m(v[:4])))); dp = np.linalg.norm(np.array(pg["pre"][str(f)][n][4:]) - np.array(v[4:]))
                if e > worst[0]: worst = (e, n, f)
        print(f"trunk pose (root, spine, chest, neck, head): max diff {worst[0]:.4f} deg ({worst[1]} F{worst[2]})")
        sys.exit(0)
    out = simulate(dump, par)
    if "--compare" in sys.argv:
        bones = [p["bone"] for p in dump["cfg"]["parts"] if p["type"] != "swing"] + ["Shoulder_L", "Elbow_L", "Wrist_L"]
        for n, (e, f) in compare(dump, out, bones).items(): print(f"{n:12s} max diff {e:.4f} deg (F{f})")
