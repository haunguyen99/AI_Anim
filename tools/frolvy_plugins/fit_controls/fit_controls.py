"""Fit Controls - make every rig control sit outside the mesh, in Frolvy.

Build Rig draws controls at a fixed size, so on a bulky character (armour,
fat bodies) many rings end up inside the mesh and cannot be clicked. This
plugin grows each hidden control, or slides it outward, until its curve is
outside the mesh.

Plugins menu:
  Fit Controls to Mesh       - fit the controls of the rig in the scene
  Build Rig + Fit Controls   - Rig Builder's Build Rig, then the fit

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

GOAL = 0.08                 # at most this share of a ring may stay inside
SCALES = (1.0, 1.15, 1.3, 1.5, 1.75, 2.0, 2.4, 2.8, 3.2, 3.8, 4.5, 5.2, 6.0)
FINGER_MAX = 1.75
PENALTY = 0.04              # cost of each x1 of growth, in "share of the ring hidden"
SHIFT_PENALTY = 0.3         # cost of sliding a shape by the character's whole height
SHIFTABLE = re.compile(r"Switch|Pad|Head|Flask|Weapon|Arrow|Prop", re.I)


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
        scales = [s for s in SCALES if not finger or s <= FINGER_MAX]
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
        d["pts"] = [tuple(new[3 * j:3 * j + 3]) for j in range(len(d["pts"]))]
        d["smp"] = _samples(d["pts"])
        report[c] = {"scale": k, "shift": [round(v, 4) for v in off],
                     "inside_before": round(p["before"], 2), "inside_after": round(frac(c, 1.0), 2)}
    still = {c: r["inside_after"] for c, r in report.items() if r["inside_after"] > GOAL}
    log("Fit Controls: %d of %d controls changed; %d still partly inside %s"
        % (len(report), len(data), len(still), sorted(still)))
    return report


def build_and_fit(api, log=print):
    ok = api.build_rig()
    log("Fit Controls: Build Rig %s" % ("done" if ok else "refused"))
    return fit(api, log=log) if ok else {}


def register(api):
    say = lambda m: api.log(m)
    api.command("Fit Controls to Mesh", lambda: fit(api, log=say))
    api.command("Build Rig + Fit Controls", lambda: build_and_fit(api, log=say))
