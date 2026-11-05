"""Fit Controls - make every rig control sit outside the mesh, in Frolvy.

Build Rig draws controls at a fixed size, so on a bulky character (armour,
fat bodies) many rings end up inside the mesh and cannot be clicked. This
plugin grows each hidden control, or slides it outward, until its curve is
outside the mesh.

Plugins menu:
  Build Rig + Fit Controls   - Rig Builder's Build Rig, then snug() every control, then fit() the rest
  Snug Controls to Mesh      - snug() every control again (redraws hand-edited shapes too)
  Fit Controls to Mesh       - the old grow/slide fit below

snug() (end of file) is the default since 2026-11-04: rings a few cm outside the mesh measured from
cross-sections, so it works on skirts / capes / hoods where the inside test below fails.
    import fit_controls; fit_controls.snug(api)           -> {control: what was done}

Pure Python (Frolvy's Python has no numpy). Called from outside as well:
    import fit_controls; fit_controls.fit(api)            -> report dict
How it works:
  1. Every mesh in the scene is turned into an "inside" lookup: for a grid of
     vertical lines (step = height/250) the heights where the line crosses the
     surface. A point is inside when an odd number of crossings lie above it.
  2. A control's curve is sampled in world space (its transform chain is walked
     with pickwalk("up"), the API has no parent getter).
  3. The share of samples inside the mesh decides: grow (x1.15 .. x3.2, fingers
     at most x1.75 so they do not swallow each other), or for switch icons,
     prop/armour controls and the head, slide the shape outward (sideways; up
     for the head and shoulder pads; behind the back for a centre switch).
  4. Left/right pairs get the same answer, mirrored.
Only control SHAPES change (CVs). Pivots, joints, skin and keys are untouched.
The whole fit is one undo step when run from the menu.
"""
import math
import re

GOAL = 0.02                 # at most this share of a ring may stay inside
SCALES = (1.0, 1.15, 1.3, 1.5, 1.75, 2.0, 2.4, 2.8, 3.2, 3.8, 4.5, 5.2, 6.0)
FINGER_MAX = 3.0            # user 2026-10-30: FK controls must show, even if finger rings overlap
PENALTY = 0.005             # cost of each x1 of growth, in "share of the ring hidden"
SHIFT_PENALTY = 0.3         # cost of sliding a shape by the character's whole height
MAX_TOTAL = 6.0             # a control is never grown past this over all runs together
FIT_ATTR = "fitScale"       # non-keyable dial on each control: growth applied so far (runs used to compound: x6 then x6 = x36)
SHIFTABLE = re.compile(r"Switch|Pad|Head|Flask|Weapon|Arrow|Prop|Bend", re.I)


# ── maths ─────────────────────────────────────────────────────────────────
def _rot(rx, ry, rz):
    x, y, z = (math.radians(v) for v in (rx, ry, rz))
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    X = ((1, 0, 0), (0, cx, -sx), (0, sx, cx))
    Y = ((cy, 0, sy), (0, 1, 0), (-sy, 0, cy))
    Z = ((cz, -sz, 0), (sz, cz, 0), (0, 0, 1))
    return _mm(Z, _mm(Y, X))


def _mm(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def _mv(m, v):
    return tuple(sum(m[i][k] * v[k] for k in range(3)) for i in range(3))


def _local(t):
    r = _rot(t[3], t[4], t[5])
    m = tuple(tuple(r[i][j] * t[6 + j] for j in range(3)) for i in range(3))
    return m, (t[0], t[1], t[2])


def _compose(a, b):           # world = a * b  (a parent, b child)
    ma, ta = a
    mb, tb = b
    return _mm(ma, mb), tuple(x + y for x, y in zip(_mv(ma, tb), ta))


def _inv3(m):
    a, b, c = m[0]; d, e, f = m[1]; g, h, i = m[2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-12:
        return ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    return tuple(tuple(v / det for v in row) for row in (
        (e * i - f * h, c * h - b * i, b * f - c * e),
        (f * g - d * i, a * i - c * g, c * d - a * f),
        (d * h - e * g, b * g - a * h, a * e - b * d)))


# ── the mesh as an inside test ────────────────────────────────────────────
class Inside:
    def __init__(self, api):
        tris = []
        lo = [1e30] * 3
        hi = [-1e30] * 3
        for obj in api.ls("Object"):
            m = api.mesh_data(obj)
            p = m["positions"]
            P = [(p[3 * k], p[3 * k + 1], p[3 * k + 2]) for k in range(len(p) // 3)]
            for q in P:
                for a in range(3):
                    lo[a] = min(lo[a], q[a]); hi[a] = max(hi[a], q[a])
            i = 0
            for s in m["face_sizes"]:
                f = m["face_corners"][i:i + s]; i += s
                for k in range(1, s - 1):
                    tris.append((P[f[0]], P[f[k]], P[f[k + 1]]))
        self.ok = bool(tris)
        if not self.ok:
            return
        self.lo, self.hi = lo, hi
        self.h = max(hi[1] - lo[1], 1e-6) / 250.0
        self.cols = {}
        h = self.h
        for a, b, c in tris:
            x0, x1 = min(a[0], b[0], c[0]), max(a[0], b[0], c[0])
            z0, z1 = min(a[2], b[2], c[2]), max(a[2], b[2], c[2])
            for ix in range(int(math.floor(x0 / h)), int(math.floor(x1 / h)) + 1):
                for iz in range(int(math.floor(z0 / h)), int(math.floor(z1 / h)) + 1):
                    self.cols.setdefault((ix, iz), []).append((a, b, c))
        self.hits = {}

    def _column(self, key):
        got = self.hits.get(key)
        if got is not None:
            return got
        x, z = (key[0] + 0.5) * self.h, (key[1] + 0.5) * self.h
        ys = []
        for a, b, c in self.cols.get(key, ()):
            # barycentric test in the xz plane, then height on the triangle
            d = (b[2] - c[2]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[2] - c[2])
            if abs(d) < 1e-14:
                continue
            l1 = ((b[2] - c[2]) * (x - c[0]) + (c[0] - b[0]) * (z - c[2])) / d
            l2 = ((c[2] - a[2]) * (x - c[0]) + (a[0] - c[0]) * (z - c[2])) / d
            l3 = 1 - l1 - l2
            if l1 >= 0 and l2 >= 0 and l3 >= 0:
                ys.append(l1 * a[1] + l2 * b[1] + l3 * c[1])
        ys.sort()
        self.hits[key] = ys
        return ys

    def __call__(self, p):
        if not self.ok:
            return False
        ys = self._column((int(math.floor(p[0] / self.h)), int(math.floor(p[2] / self.h))))
        return sum(1 for y in ys if y > p[1]) % 2 == 1


# ── controls ──────────────────────────────────────────────────────────────
def _parent(api, name, cache):
    if name in cache:
        return cache[name]
    api.select([name])
    api.pickwalk("up")
    sel = api.selection()
    par = sel[0] if sel and sel[0] != name else None
    cache[name] = par
    return par


def _world(api, name, cache, wcache):
    if name in wcache:
        return wcache[name]
    par = _parent(api, name, cache)
    loc = _local(api.transform(name))
    w = _compose(_world(api, par, cache, wcache), loc) if par else loc
    wcache[name] = w
    return w


def _samples(pts, per=4):
    out = []
    n = len(pts)
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        for s in range(per):
            t = s / per
            out.append(tuple(a[i] + t * (b[i] - a[i]) for i in range(3)))
    return out


def _outward(name, centre):
    # bendy-limb controls sit mid-bone: slide them across the bone, never along it
    if "Bend" in name:
        return (0.0, 1.0, 0.0) if re.search("Shoulder|Elbow", name) else (0.0, 0.0, 1.0)
    if "Head" in name:
        return (0.0, 1.0, 0.0)
    if "Switch" in name and name.endswith("_M"):
        return (0.0, 0.0, -1.0)
    hx, hz = centre[0], centre[2] * 0.3
    n = math.hypot(hx, hz)
    if n < 0.05 * 1.0 and abs(centre[0]) < 1e-3:
        return (0.0, 0.0, -1.0)
    d = (hx / n, 0.0, hz / n) if n > 1e-9 else (0.0, 0.0, -1.0)
    if "Pad" in name:
        d = (d[0], 1.2, d[2])
        l = math.sqrt(sum(v * v for v in d)); d = tuple(v / l for v in d)
    return d


def fit(api, controls=None, log=print):
    inside = Inside(api)
    if not inside.ok:
        log("Fit Controls: no mesh in the scene.")
        return {}
    keep_sel = api.selection()
    size = inside.hi[1] - inside.lo[1]
    ctls = controls or sorted(c for c in api.ls("Curve") if c.startswith("CTL_"))
    cache, wcache, data = {}, {}, {}
    for c in ctls:
        q = api.curve_points(c)
        pts = [(q[3 * k], q[3 * k + 1], q[3 * k + 2]) for k in range(len(q) // 3)]
        if len(pts) < 2:
            continue
        m, t = _world(api, c, cache, wcache)
        cen = tuple(sum(p[i] for p in pts) / len(pts) for i in range(3))
        data[c] = {"pts": pts, "m": m, "t": t, "cen": cen, "smp": _samples(pts)}
    api.select(keep_sel)

    def frac(c, k, off=(0.0, 0.0, 0.0)):
        d = data[c]; m, t, cen = d["m"], d["t"], d["cen"]
        n_in = 0
        for p in d["smp"]:
            lp = tuple(cen[i] + k * (p[i] - cen[i]) for i in range(3))
            w = _mv(m, lp)
            n_in += inside((w[0] + t[0] + off[0], w[1] + t[1] + off[1], w[2] + t[2] + off[2]))
        return n_in / len(d["smp"])

    plan = {}
    for c in data:
        f0 = frac(c, 1.0)
        if f0 <= GOAL:
            continue
        finger = "Finger" in c or "Cup" in c
        if finger and f0 <= 0.25:
            continue
        done = api.get_attr(c + "." + FIT_ATTR) or 1.0
        cap = (FINGER_MAX if finger else MAX_TOTAL) / max(done, 1e-6)
        scales = [s for s in SCALES if s <= cap + 1e-6] or [1.0]
        # every option has a cost: what stays hidden, plus a little for each step of growth or shift,
        # so a ring only gets big when that really brings it out of the mesh
        opts = []
        for k in scales:
            f = frac(c, k)
            opts.append((max(f, GOAL) + PENALTY * (k - 1), k, (0.0, 0.0, 0.0)))
            if f <= GOAL:
                break
        if SHIFTABLE.search(c) and not finger and min(o[0] for o in opts) > GOAL + 0.02:
            d = data[c]; wc = _mv(d["m"], d["cen"]); wc = tuple(wc[i] + d["t"][i] for i in range(3))
            u = _outward(c, wc)
            for k in (1.0, 1.3, 1.6):
                for step in range(1, 18):
                    dist = 0.05 * step * size / 2.0
                    off = tuple(u[i] * dist for i in range(3))
                    f = frac(c, k, off)
                    if f <= GOAL:
                        opts.append((GOAL + PENALTY * (k - 1) + SHIFT_PENALTY * dist / size, k, off))
                        break
        cost, k, off = min(opts, key=lambda o: (round(o[0], 3), o[1]))
        if k == 1.0 and not any(off):
            continue
        plan[c] = {"k": k, "off": off, "before": f0}

    # left / right pairs: the same answer, mirrored in x
    for c in list(plan):
        mm = re.match(r"(.+)_([LR])$", c)
        if not mm:
            continue
        o = mm.group(1) + "_" + ("R" if mm.group(2) == "L" else "L")
        if o not in data:
            continue
        a = plan.get(c, {"k": 1.0, "off": (0.0, 0.0, 0.0), "before": 0.0})
        b = plan.get(o, {"k": 1.0, "off": (0.0, 0.0, 0.0), "before": 0.0})
        k = max(a["k"], b["k"])
        if not any(a["off"]) and not any(b["off"]):
            # one size for both sides: the one with the lowest summed cost
            ks = sorted(set(s for s in SCALES if s <= max(a["k"], b["k"])) | {a["k"], b["k"]})
            k = min(ks, key=lambda s: (round(max(frac(c, s), GOAL) + max(frac(o, s), GOAL)
                                             + 2 * PENALTY * (s - 1), 3), s))
            # the two sides may not be in the same pose (one arm in FK): never let the shared size
            # hide more of a side than its own answer did
            if frac(c, k) > max(GOAL, frac(c, a["k"])) + 0.03 or frac(o, k) > max(GOAL, frac(o, b["k"])) + 0.03:
                continue
        src, flip = (a, False) if sum(v * v for v in a["off"]) >= sum(v * v for v in b["off"]) else (b, True)
        off = (-src["off"][0], src["off"][1], src["off"][2]) if flip else src["off"]
        plan[c] = dict(a, k=k, off=off)
        plan[o] = dict(b, k=k, off=(-off[0], off[1], off[2]))

    report = {}
    for c, p in plan.items():
        d = data[c]; k, off = p["k"], p["off"]
        lo = _mv(_inv3(d["m"]), off)
        cen = d["cen"]
        new = []
        for q in d["pts"]:
            new += [cen[i] + k * (q[i] - cen[i]) + lo[i] for i in range(3)]
        api.set_curve_points(c, list(range(len(d["pts"]))), new)
        total = (api.get_attr(c + "." + FIT_ATTR) or 1.0) * k
        if api.get_attr(c + "." + FIT_ATTR) is None:
            api.add_attr(c, FIT_ATTR, total, 0.0, 0.0, "float", "", False)
        else:
            api.set_attr(c + "." + FIT_ATTR, total)
        d["pts"] = [tuple(new[3 * j:3 * j + 3]) for j in range(len(d["pts"]))]
        d["smp"] = _samples(d["pts"])
        report[c] = {"scale": k, "shift": [round(v, 4) for v in off],
                     "inside_before": round(p["before"], 2), "inside_after": round(frac(c, 1.0), 2)}
    still = {c: r["inside_after"] for c, r in report.items() if r["inside_after"] > GOAL}
    log("Fit Controls: %d of %d controls changed; %d still partly inside %s"
        % (len(report), len(data), len(still), sorted(still)))
    return report


# -- snug: rings a few cm outside the mesh, from cross-sections -------------
# fit() above asks "is this point inside the mesh?" by counting surface crossings on a vertical line.
# That breaks on single-layer sheets (skirts, capes, scarves, hoods): everything under a sheet counts as
# inside and rings grow to metres (Hero RPG2 2026-11-04: ankle ring 2 m, scapula 2.5 m). snug() never asks
# inside/outside. It cuts the mesh with the ring's plane, looks along 16 directions from the bone and keeps
# the layers that wrap the bone (a skirt over the thigh) but not layers a gap away (a front flap in front of
# the knee, the other leg), then draws the ring just outside them.
SNUG_ATTR = "snug"          # 1 on a control snug() drew; Rebuild keeps shapes, so later runs leave it alone
SECTORS = 16


def _mat(api, name):
    M = api.world_matrix(name)
    return ((M[0], M[4], M[8]), (M[1], M[5], M[9]), (M[2], M[6], M[10])), (M[12], M[13], M[14])


def _sub(a, b): return tuple(a[i] - b[i] for i in range(3))
def _add(a, b): return tuple(a[i] + b[i] for i in range(3))
def _mul(a, k): return tuple(v * k for v in a)
def _dot(a, b): return sum(a[i] * b[i] for i in range(3))
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _len(a): return math.sqrt(_dot(a, a))
def _lerp(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _unit(a):
    n = _len(a)
    return tuple(v / n for v in a) if n > 1e-12 else (0.0, 1.0, 0.0)


def _plane(nrm):
    nrm = _unit(nrm)
    u = _unit(_cross(nrm, (0.0, 1.0, 0.0) if abs(nrm[1]) < 0.9 else (1.0, 0.0, 0.0)))
    return nrm, u, _cross(nrm, u)


class Body:
    """Every mesh as world points and edges, plus the skeleton; sizes scale with the character's height."""
    def __init__(self, api):
        self.pts, self.edges = [], []
        lo = [1e30] * 3; hi = [-1e30] * 3
        for obj in api.ls("Object"):
            m = api.mesh_data(obj)
            p = m["positions"]
            R, T = _mat(api, obj)
            base = len(self.pts)
            for k in range(len(p) // 3):
                w = _add(_mv(R, (p[3 * k], p[3 * k + 1], p[3 * k + 2])), T)
                self.pts.append(w)
                for a in range(3):
                    lo[a] = min(lo[a], w[a]); hi[a] = max(hi[a], w[a])
            seen = set(); i = 0
            for sz in m["face_sizes"]:
                f = m["face_corners"][i:i + sz]; i += sz
                for k in range(sz):
                    a, b = base + f[k], base + f[(k + 1) % sz]
                    e = (a, b) if a < b else (b, a)
                    if e not in seen:
                        seen.add(e); self.edges.append(e)
        self.ok = bool(self.edges)
        self.lo, self.hi = lo, hi
        self.H = max(hi[1] - lo[1], 1e-6)
        self.joints = {j["name"]: j for j in api.joint_info()}
        self.kids = {}
        for n, j in self.joints.items():
            self.kids.setdefault(j["parent"], []).append(n)

    def jw(self, n):
        return tuple(self.joints[n]["world"]) if n and n in self.joints else None

    def child(self, n, skip=r"FootSide|Heel|Weapon|Arrow|Thumb|Pad|Skirt|Scarf|Cup|Index|Ring|Pinky"):
        """The joint a bone points at: the first DEF child that is not a side branch."""
        ks = [k for k in self.kids.get(n, []) if k.startswith("DEF_")]
        main = [k for k in ks if not re.search(skip, k)] or ks
        return main[0] if main else None

    def cut(self, cen, nrm):
        """Points where the mesh edges cross the plane through cen with normal nrm."""
        out = []
        d = [_dot(_sub(p, cen), nrm) for p in self.pts]
        for a, b in self.edges:
            da, db = d[a], d[b]
            if (da > 0) != (db > 0):
                t = da / (da - db)
                out.append(_lerp(self.pts[a], self.pts[b], t))
        return out

    def profile(self, cen, nrm, side=None, gap=None, maxr=None, pick=0.9):
        """How far out the layers wrapping the bone reach, as one radius (None: nothing there)."""
        gap = gap or 0.06 * self.H
        maxr = maxr or 0.45 * self.H
        nrm, u, v = _plane(nrm)
        sec = [[] for _ in range(SECTORS)]
        for p in self.cut(cen, nrm):
            if (side == "R" and p[0] > 0.005) or (side == "L" and p[0] < -0.005):
                continue
            q = _sub(p, cen); x, y = _dot(q, u), _dot(q, v); r = math.hypot(x, y)
            if r < maxr:
                k = int((math.atan2(y, x) + math.pi) / (2 * math.pi) * SECTORS) % SECTORS
                sec[k].append(r)
        reach = []
        for rs in sec:
            if not rs:
                continue
            rs.sort(); last = rs[0]
            for r in rs[1:]:
                if r - last > gap:
                    break
                last = r
            reach.append(last)
        if not reach:
            return None
        reach.sort()
        return reach[min(len(reach) - 1, int(pick * (len(reach) - 1) + 0.5))]

    def near(self, p, r):
        return [q for q in self.pts if _len(_sub(q, p)) < r]


def _ring(cen, nrm, r, n):
    nrm, u, v = _plane(nrm)
    return [_add(cen, _add(_mul(u, r * math.cos(2 * math.pi * k / n)), _mul(v, r * math.sin(2 * math.pi * k / n))))
            for k in range(n)]


def _put(api, c, world_pts):
    """Write world-space CVs into control c (its own space)."""
    R, T = _mat(api, c); I = _inv3(R)
    flat = []
    for p in world_pts:
        flat += list(_mv(I, _sub(p, T)))
    api.set_curve_points(c, list(range(len(world_pts))), flat)


def _cvs(api, c):
    q = api.curve_points(c); R, T = _mat(api, c)
    return [_add(_mv(R, (q[3 * k], q[3 * k + 1], q[3 * k + 2])), T) for k in range(len(q) // 3)]


def _plan(api, B, c):
    """('ring', centre, normal, radius) | ('box', lo, hi) | ('scale', centre, k) | None, for one control."""
    H = B.H; pad = 0.012 * H
    m = re.match(r"CTL_(.+?)(_[LRM])?$", c)
    if not m:
        return None
    base, sfx = m.group(1), (m.group(2) or "")
    side = sfx[1:] if sfx in ("_L", "_R") else None
    j = "DEF_" + base + sfx
    if "Switch" in c:
        # one size for every switch icon (Build Rig drew Hero's right arm switch 2 cm, the left 5.6 cm;
        # user: "shape control switch ở tay phải bé quá"); fit() then only slides it out of the mesh
        W = _cvs(api, c)
        if len(W) < 2:
            return None
        cen = tuple(sum(p[i] for p in W) / len(W) for i in range(3))
        ext = max(max(p[i] for p in W) - min(p[i] for p in W) for i in range(3))
        return ("scale", cen, 0.042 * H / max(ext, 1e-9))
    if re.search(r"Pole|HipSwinger|IKMid|Arrow|Bend", c):
        return None                                     # fit() still slides poles out
    if base == "Main":
        return ("ring", (0.0, B.lo[1], 0.0), (0.0, 1.0, 0.0), 0.34 * H)
    if base in ("IKAnkle", "IKFoot", "IKLeg"):           # box hugging the shoe
        a = B.jw("DEF_Ankle" + sfx)
        if not a:
            return None
        P = [p for p in B.pts if p[1] < a[1] + 0.02 * H and abs(p[0] - a[0]) < 0.1 * H
             and (side != "R" or p[0] < 0) and (side != "L" or p[0] > 0)]
        if not P:
            return None
        lo = [min(p[i] for p in P) - pad for i in range(3)]; hi = [max(p[i] for p in P) + pad for i in range(3)]
        lo[1] = B.lo[1] - 0.003 * H; hi[1] = a[1] + 0.04 * H
        return ("box", lo, hi)
    if base in ("IKWrist", "IKHand", "IKArm"):           # box hugging the hand
        w = B.jw("DEF_Wrist" + sfx); f = B.jw(B.child("DEF_Wrist" + sfx))
        if not w or not f:
            return None
        d = _unit(_sub(f, w))
        P = [p for p in B.near(w, 0.16 * H) if _dot(_sub(p, w), d) > -0.01 * H]
        if not P:
            return None
        return ("box", [min(p[i] for p in P) - pad for i in range(3)], [max(p[i] for p in P) + pad for i in range(3)])
    if j not in B.joints:
        return None
    jp = B.jw(j)
    label = (api.joint_label(j) or ["", ""])[1]
    if "Weapon" in base:                                 # small ring round the blade, in front of the hand
        e = [k for k in B.kids.get(j, []) if k.startswith("DEF_")]
        if not e:
            return None
        d = _sub(B.jw(e[0]), jp)
        return ("ring", _add(jp, _mul(_unit(d), min(0.09 * H, 0.5 * _len(d)))), d, 0.025 * H)
    if label == "prop" or re.search(r"Pad|Skirt|Scarf|Cape|Tail|Cloth", base):
        # cloth / armour piece: a small ring lying on its outer face
        root = B.jw("DEF_Root_M") or (0.0, jp[1], 0.0)
        out = (jp[0], 0.0, jp[2] - root[2])
        out = _unit(out) if math.hypot(out[0], out[2]) > 0.01 * H else (0.0, 0.0, 1.0 if jp[2] >= root[2] else -1.0)
        push = max([_dot(_sub(p, jp), out) for p in B.near(jp, 0.04 * H)] or [0.0])
        return ("ring", _add(jp, _mul(out, max(push, 0.0) + 0.008 * H)), out, 0.024 * H)
    if re.search(r"Scapula|Clavicle", base):            # above the shoulder is often under a hood: front of chest
        p = _lerp(jp, B.jw(B.child(j)) or jp, 0.45)
        front = max([q[2] for q in B.pts if math.hypot(q[0] - p[0], q[1] - p[1]) < 0.025 * H] or [p[2]])
        return ("ring", (p[0], p[1], front + 0.01 * H), (0.0, 0.0, 1.0), 0.026 * H)
    if base == "Ankle":                                  # flat ring round the boot, not across the foot
        cen = (jp[0], jp[1] + 0.04 * H, jp[2])
        r = B.profile(cen, (0.0, 1.0, 0.0), side)
        return ("ring", cen, (0.0, 1.0, 0.0), (r or 0.05 * H) + pad)
    ch = B.child(j)
    if base == "Head" and ch:
        cen = _lerp(jp, B.jw(ch), 0.55); d = _sub(B.jw(ch), jp)
        return ("ring", cen, d, (B.profile(cen, d) or 0.1 * H) + pad)
    if base == "Neck" and ch:                            # the narrowest spot between neck and head
        h = B.jw(ch); he = B.jw(B.child(ch)) or h
        end = _lerp(h, he, 0.3); d = _sub(end, jp)
        best = None
        for t in [k / 10.0 for k in range(11)]:
            cen = _lerp(jp, end, t); r = B.profile(cen, d)
            if r and (best is None or r < best[0]):
                best = (r, cen)
        return ("ring", best[1], d, best[0] + pad) if best else None
    finger = re.search(r"Finger|Thumb|Cup", base)
    if ch and not re.search(r"Root|Spine|Chest", base):
        d = _sub(B.jw(ch), jp)
        # shoulders and hips may slide a little down the bone, out from under a hood or pads
        ts = [k / 20.0 for k in range(10)] if re.search(r"Shoulder|Hip", base) else [0.45 if finger else 0.0]
        best = None
        for t in ts:
            cen = _lerp(jp, B.jw(ch), t)
            if finger:
                # thumbs: the median, or the palm next to them counts; fingers: most of the way round
                r = B.profile(cen, d, side, gap=0.006 * H, maxr=0.06 * H, pick=0.5 if "Thumb" in base else 0.9)
            else:
                r = B.profile(cen, d, side)
            if r and (best is None or r < best[0] - 0.005 * H):
                best = (r, cen)
        return ("ring", best[1], d, best[0] + (0.006 * H if finger else pad)) if best else None
    # spine and root rings: keep the shape Build Rig drew, size it from the section in its own plane
    W = _cvs(api, c)
    if len(W) < 3:
        return None
    cen = tuple(sum(p[i] for p in W) / len(W) for i in range(3))
    nrm = (0.0, 0.0, 0.0)
    for k in range(len(W)):
        nrm = _add(nrm, _cross(_sub(W[k], cen), _sub(W[(k + 1) % len(W)], cen)))
    if _len(nrm) < 1e-9:
        return None
    r = B.profile(cen, nrm)
    if not r:
        return None
    if base == "Root":
        r *= 1.25                                        # outside RootX
    now = sum(_len(_sub(p, cen)) for p in W) / len(W)
    return ("scale", cen, (r + pad) / max(now, 1e-9))


def snug(api, controls=None, force=False, log=print):
    """Draw controls a few cm outside the mesh. Skips controls snug() drew before and hand-made ones
    (fitScale >= 6) unless force=True. Returns {control: what was done}."""
    B = Body(api)
    if not B.ok:
        log("Snug Controls: no mesh in the scene.")
        return {}
    ctls = controls or sorted(c for c in api.ls("Curve") if c.startswith("CTL_"))
    plans = {}
    for c in ctls:
        if not force and ((api.get_attr(c + "." + SNUG_ATTR) or 0) >= 1
                          or (api.get_attr(c + "." + FIT_ATTR) or 0) >= MAX_TOTAL):
            continue
        p = _plan(api, B, c)
        if p:
            plans[c] = p
    # left / right rings get one size, the smaller: an odd piece on one side (a flap hanging lower
    # on the right, Hero's front flap at the knee) must not blow up one ring only
    for c, p in plans.items():
        o = c[:-2] + ("_L" if c.endswith("_R") else "_R")
        if c[-2:] in ("_L", "_R") and p[0] == "ring" and plans.get(o, ("",))[0] == "ring":
            r = min(p[3], plans[o][3])
            plans[c] = p[:3] + (r,)
    report = {}
    for c, p in plans.items():
        W = _cvs(api, c); n = len(W)
        closed = n > 2 and _len(_sub(W[0], W[-1])) < 1e-6
        if p[0] == "ring":
            if n < 4:
                continue
            cen, nrm, r = p[1], p[2], p[3]
            pts = _ring(cen, nrm, r, n - 1 if closed else n)
            new = pts + [pts[0]] if closed else pts
            report[c] = "ring r %.3f" % r
        elif p[0] == "box":
            lo, hi = p[1], p[2]
            a = [min(q[i] for q in W) for i in range(3)]; b = [max(q[i] for q in W) for i in range(3)]
            new = [tuple(lo[i] + (q[i] - a[i]) / ((b[i] - a[i]) or 1.0) * (hi[i] - lo[i]) for i in range(3)) for q in W]
            report[c] = "box %s" % [round(hi[i] - lo[i], 3) for i in range(3)]
        else:
            cen, k = p[1], p[2]
            new = [_add(cen, _mul(_sub(q, cen), k)) for q in W]
            report[c] = "scale x%.2f" % k
        _put(api, c, new)
        for attr, val in ((SNUG_ATTR, 1.0), (FIT_ATTR, MAX_TOTAL)):
            if api.get_attr(c + "." + attr) is None:
                api.add_attr(c, attr, val, 0.0, 0.0, "float", "", False)
            else:
                api.set_attr(c + "." + attr, val)
    log("Snug Controls: %d of %d controls drawn snug to the mesh" % (len(report), len(ctls)))
    return report


def build_and_fit(api, log=print):
    """Build Rig, then snug() every control, then fit() what snug() leaves (switches, poles)."""
    ok = api.build_rig()
    log("Fit Controls: Build Rig %s" % ("done" if ok else "refused"))
    if not ok:
        return {}
    done = snug(api, log=log)
    # switches: snug() sized them, fit() may still slide them out of the mesh (their fitScale cap stops growth)
    rest = [c for c in sorted(c for c in api.ls("Curve") if c.startswith("CTL_")) if c not in done or "Switch" in c]
    return {"snug": done, "fit": fit(api, controls=rest, log=log) if rest else {}}


def register(api):
    say = lambda m: api.log(m)
    api.command("Fit Controls to Mesh", lambda: fit(api, log=say))
    api.command("Snug Controls to Mesh", lambda: snug(api, force=True, log=say))
    api.command("Build Rig + Fit Controls", lambda: build_and_fit(api, log=say))
