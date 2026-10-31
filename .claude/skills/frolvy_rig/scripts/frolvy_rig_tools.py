"""Helpers for rigging game characters in Frolvy, run INSIDE Frolvy through the MCP
execute_code tool (the `api` object is Frolvy's). Pure Python: Frolvy's Python has no numpy.

    import sys; sys.path.insert(0, r"D:\\Project\\AI_Anim\\.claude\\skills\\frolvy_rig\\scripts")
    import importlib, frolvy_rig_tools as R; importlib.reload(R)
    R.check_model(api)                      # step 1: read the model
    R.zero_controls(api)                    # before ANY Build / Rebuild Rig
    R.after_rebuild(api, one_side=("Weapon","Arrow"), prop_side="_R")   # after every Rebuild
    R.skin_report(api, "Body")              # audit, then fix with the skin_* helpers
    R.deform_test(api, "Body", [("CTL_Hip_L",(-70,0,0))])

Every execute_code call is one undo step. Frolvy's undo stack also holds the user's own UI
actions, so prefer fixing forward over undo. Frolvy refuses a graph with a loop and then the
whole rig stops moving - after any new constraint or wire, rotate a control and check a DEF
joint really moves (see check_rig_moves)."""
import collections
import math
import re

# ----------------------------------------------------------------- small math

def P(api, n):
    return list(api.world_matrix(n)[12:15])


def Rw(api, n):
    """World rotation, rows = world axes, columns = the node's X Y Z."""
    m = api.world_matrix(n)
    return [[m[0], m[4], m[8]], [m[1], m[5], m[9]], [m[2], m[6], m[10]]]


def M34(api, n):
    m = api.world_matrix(n)
    return [[m[0], m[4], m[8], m[12]], [m[1], m[5], m[9], m[13]], [m[2], m[6], m[10], m[14]]]


def inv_rigid(R):
    r = [[R[c][k] for c in range(3)] for k in range(3)]
    t = [R[i][3] for i in range(3)]
    return [r[i] + [-sum(r[i][k] * t[k] for k in range(3))] for i in range(3)]


def mul34(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) + (A[i][3] if j == 3 else 0) for j in range(4)]
            for i in range(3)]


def ramp(v, a, b):
    return max(0.0, min(1.0, (v - a) / (b - a)))


def seg_dist(p, a, b):
    ab = [b[i] - a[i] for i in range(3)]
    ap = [p[i] - a[i] for i in range(3)]
    L = sum(v * v for v in ab)
    t = 0 if L < 1e-12 else max(0, min(1, sum(ab[i] * ap[i] for i in range(3)) / L))
    return math.dist(p, [a[i] + ab[i] * t for i in range(3)])


def parent(api, n):
    api.select([n]); api.pickwalk("up"); s = api.selection(); api.select([])
    return s[0] if s and s[0] != n else None


def children(api, n):
    api.select([n]); api.pickwalk("down"); s = api.selection(); out = []; seen = set()
    while s and s[0] != n and s[0] not in seen:
        seen.add(s[0]); out.append(s[0]); api.pickwalk("right"); s = api.selection()
    api.select([])
    return out


def controls(api):
    return sorted(c for c in api.ls("Curve")
                  if c.startswith("CTL_") and not c.endswith(("_grp", "_follow")))

# ----------------------------------------------------------------- mesh reading

class Mesh:
    """Positions, global vertex ids, faces, edges and connected shells of one object."""

    def __init__(self, api, obj):
        md = api.mesh_data(obj)
        self.obj = obj
        self.P = md["positions"]
        self.G = md["vertices"]                    # global vertex ids (needed by skin calls)
        self.n = len(self.G)
        self.faces = []
        k = 0
        for s in md["face_sizes"]:
            self.faces.append(md["face_corners"][k:k + s]); k += s
        par = list(range(self.n))

        def f(a):
            while par[a] != a:
                par[a] = par[par[a]]; a = par[a]
            return a
        self.edges = set()
        for c in self.faces:
            for j in c[1:]:
                par[f(j)] = f(c[0])
            for a in range(len(c)):
                u, v = c[a], c[(a + 1) % len(c)]
                self.edges.add((min(u, v), max(u, v)))
        g = collections.defaultdict(list)
        for i in range(self.n):
            g[f(i)].append(i)
        self.shells = sorted(g.values(), key=len, reverse=True)
        self.main = set(self.shells[0])

    def p(self, i):
        return self.P[3 * i:3 * i + 3]

    def box(self, ids):
        return ([min(self.P[3 * i + a] for i in ids) for a in range(3)],
                [max(self.P[3 * i + a] for i in ids) for a in range(3)])

    def cut(self, axis, value, keep=lambda p: True, main_only=True):
        """Points where mesh edges cross the plane axis=value (a clean cross-section,
        better than slicing vertices on a low-poly mesh)."""
        out = []
        for a, b in self.edges:
            if main_only and a not in self.main:
                continue
            pa, pb = self.p(a), self.p(b)
            if (pa[axis] - value) * (pb[axis] - value) < 0:
                t = (value - pa[axis]) / (pb[axis] - pa[axis])
                q = [pa[i] + (pb[i] - pa[i]) * t for i in range(3)]
                if keep(q):
                    out.append(q)
        return out


def check_model(api, objs=None):
    """Step 1 report: units, bounds, symmetry and the loose shells of every mesh."""
    objs = objs or api.ls("Object")
    print("up axis", api.up_axis())
    for o in objs:
        m = Mesh(api, o)
        lo, hi = m.box(range(m.n))
        S = set((round(m.P[3 * i], 3), round(m.P[3 * i + 1], 3), round(m.P[3 * i + 2], 3)) for i in range(m.n))
        mir = sum(1 for (x, y, z) in S if (round(-x, 3), y, z) in S) / max(1, len(S))
        print("%s: %d verts, %d shells, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f, mirror %.0f%%, xf %s"
              % (o, m.n, len(m.shells), lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], 100 * mir,
                 [round(v, 3) for v in api.transform(o)]))
        for ids in m.shells[:25]:
            a, b = m.box(ids)
            print("   %4d  x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % (len(ids), a[0], b[0], a[1], b[1], a[2], b[2]))


def sections(api, obj, axis, values, keep=lambda p: True):
    """Print bounds and centre of edge cross-sections, e.g. sections(api,"Body",1,[0.5,0.9,1.3])."""
    m = Mesh(api, obj)
    o = [i for i in range(3) if i != axis]
    for v in values:
        S = m.cut(axis, v, keep)
        if not S:
            print("%s=%.3f -" % ("xyz"[axis], v)); continue
        txt = []
        for k in o:
            a = min(q[k] for q in S); b = max(q[k] for q in S)
            txt.append("%s %.3f..%.3f (c %.3f)" % ("xyz"[k], a, b, (a + b) / 2))
        print("%s=%.3f  %s  n%d" % ("xyz"[axis], v, "  ".join(txt), len(S)))

# ----------------------------------------------------------------- rig state

def zero_controls(api):
    """Every control back to 0 (switches kept). Rebuild Rig bakes the CURRENT pose into the
    control offset groups, so run this before any Build/Rebuild."""
    n = 0
    for c in controls(api):
        if "Switch" in c:
            continue
        t = api.transform(c)
        if any(abs(v) > 1e-6 for v in t[:6]):
            lk = api.locked_channels(c)
            if lk: api.lock_channels(c, " ".join(lk), False)
            api.set_transform(c, [0, 0, 0], [0, 0, 0], [1, 1, 1])
            if lk: api.lock_channels(c, " ".join(lk), True)
            n += 1
    for s in ("_L", "_R"):
        sw = "CTL_ArmSwitch" + s
        if sw in api.ls():
            for a in ("curl", "thumbCurl", "spread", "handPose", "indexCurl", "middleCurl", "ringCurl", "pinkyCurl"):
                if api.attr_info(sw, a): api.set_attr(sw + "." + a, 0.0)
    # offset groups normally carry no rotation; joints with custom axes (thumbs) are the exception
    grp = [g for g in api.ls() if g.endswith("_grp") and "Thumb" not in g
           and any(abs(v) > 0.01 for v in api.transform(g)[3:6])]
    print("controls reset:", n, "| offset groups with rotation (pose baked by an earlier Rebuild?):", grp[:8])
    return n


def fit_of(api, d, J=None):
    """World spot a DEF joint should sit on: its fit joint (mirrored for _L)."""
    J = J or set(api.ls("Joint"))
    b = d[4:]; s = b[-2:]; f = b[:-2]
    if f in J:
        w = P(api, f)
        return [w[0] * (-1 if s == "_L" else 1), w[1], w[2]]
    return None


def def_vs_fit_both(api, tol=2e-3):
    """def_vs_fit in the current mode AND in FK rest (both must be empty)."""
    now = def_vs_fit(api, tol)
    saved = fk_rest(api)
    try:
        fk = def_vs_fit(api, tol)
    finally:
        restore_switches(api, saved)
    return {"current": now, "fk": fk}


def def_vs_fit(api, tol=2e-3):
    J = set(api.ls("Joint")); bad = []
    for d in sorted(j for j in J if j.startswith("DEF_")):
        w = fit_of(api, d, J)
        if w and max(abs(P(api, d)[i] - w[i]) for i in range(3)) > tol:
            bad.append((d, [round(v, 3) for v in P(api, d)], [round(v, 3) for v in w]))
    return bad


def check_rig_moves(api, ctl="CTL_Shoulder_L", joint="DEF_Wrist_L", sw="CTL_ArmSwitch_L"):
    """True when rotating an FK control really moves a DEF joint (a graph loop freezes the rig)."""
    s0 = {a: api.get_attr(sw + "." + a) for a in ("autoSnap", "fkIk") if api.get_attr(sw + "." + a) is not None}
    for a in s0: api.set_attr(sw + "." + a, 0.0)
    a = P(api, joint); t = api.transform(ctl)
    api.set_transform(ctl, t[:3], [0, 0, -45], t[6:9]); b = P(api, joint)
    api.set_transform(ctl, t[:3], t[3:6], t[6:9])
    for k, v in s0.items(): api.set_attr(sw + "." + k, v)
    moved = math.dist(a, b) > 0.01
    print("rig moves:", moved)
    return moved

# ----------------------------------------------------------------- after a Rebuild

def delete_one_side_props(api, names=("Weapon", "Arrow"), side="_L"):
    """Build Rig mirrors every right-side joint; delete the mirrored copies of one-sided props
    and the wire_ nodes they leave (never touch wire_DEF_Root_M_*: Rig Builder's own)."""
    for nm in names:
        for n in ("CTL_%s%s_grp" % (nm, side), "DEF_%s%s" % (nm, side), "CTL_%s%s" % (nm, side)):
            if n in api.ls():
                api.select([n]); api.delete_selection()
    api.select([])
    for _ in range(2):
        for p in api.check_rig():
            w = p.split(":")[0]
            if w.startswith("wire_DEF_") and any(nm + side in w for nm in names):
                try: api.delete_node(w)
                except Exception: pass


def add_translate_wires(api):
    """Build Rig wires FK controls to DEF joints by rotation only and locks translate.
    Add tx/ty/tz 'add' nodes (control.tN + rest constant -> DEF.tN) and unlock translate.
    Switch controls stay locked."""
    GN = set(api.graph_nodes()); wired = 0
    for c in controls(api):
        if "Switch" in c:
            continue
        src = [w for w in GN if w.startswith("wire_DEF_") and (w.endswith("_rx") or w.endswith("_rx_fng"))
               and c + ".rx" in api.node_connections(w)]
        if src:
            dj = src[0][5:].rsplit("_rx", 1)[0]
            if not any(("wire_%s_%s" % (dj, ch)) in GN for ch in ("tx", "ty", "tz")):
                t = api.transform(dj)
                for k, ch in enumerate(("tx", "ty", "tz")):
                    nd = api.create_node("add", "wire_%s_%s" % (dj, ch))
                    api.connect(nd, 0, c + "." + ch); api.set_node_param(nd, 1, t[k])
                    api.set_node_output(nd, dj + "." + ch)
                wired += 1
        if "tx" in api.locked_channels(c):
            api.lock_channels(c, "tx ty tz", False)
    return wired


SWITCHES = ("CTL_ArmSwitch_L", "CTL_ArmSwitch_R", "CTL_LegSwitch_L", "CTL_LegSwitch_R", "CTL_SpineSwitch_M")


def fk_rest(api):
    """All limbs/spine to FK with autoSnap off and every control at 0, so DEF joints show the
    REST frames. Returns the saved switch values for restore_switches()."""
    saved = []
    for s in SWITCHES:
        if s in api.ls():
            v = {a: api.get_attr(s + "." + a) for a in ("autoSnap", "fkIk") if api.get_attr(s + "." + a) is not None}
            saved.append((s, v))
            if "autoSnap" in v: api.set_attr(s + ".autoSnap", 0.0)
            api.set_attr(s + ".fkIk", 0.0)
    zero_controls(api)
    return saved


def restore_switches(api, saved):
    """Back to the saved fkIk values; autoSnap stays OFF while switching (else FK/IK controls get
    snapped to whatever pose the other side has) and is restored afterwards."""
    for s, v in saved:
        if "fkIk" in v: api.set_attr(s + ".fkIk", v["fkIk"])
    zero_controls(api)
    for s, v in saved:
        if "autoSnap" in v: api.set_attr(s + ".autoSnap", v["autoSnap"])


def sync_rest(api, passes=6):
    """Put every DEF joint on its fit joint by rewriting the translate-wire constants (or the
    translate itself when unwired). Needed after Rebuild when fit joints moved or got new axes.
    Runs in FK rest: computed while a leg is in IK the parent frames are IK-rotated and the
    constants come out wrong (2026-10-31: both knees off by 7-8 mm in FK)."""
    saved = fk_rest(api)
    try:
        return _sync_rest(api, passes)
    finally:
        restore_switches(api, saved)


def _sync_rest(api, passes):
    GN = set(api.graph_nodes()); J = set(api.ls("Joint")); done = set()
    for _ in range(passes):
        for d in sorted(j for j in J if j.startswith("DEF_")):
            want = fit_of(api, d, J)
            if not want or max(abs(P(api, d)[i] - want[i]) for i in range(3)) < 5e-4:
                continue
            pj = parent(api, d); R = Rw(api, pj); pp = P(api, pj)
            dv = [want[i] - pp[i] for i in range(3)]
            loc = [sum(R[r][i] * dv[r] for r in range(3)) for i in range(3)]
            names = ["wire_%s_%s" % (d, ch) for ch in ("tx", "ty", "tz")]
            if all(nm in GN for nm in names):
                for i, nm in enumerate(names): api.set_node_param(nm, 1, loc[i])
            else:
                t = api.transform(d); api.set_transform(d, loc, t[3:6], t[6:9])
            done.add(d)
    return sorted(done)


def sync_control_pivots(api):
    """Rebuild leaves a control's pivot at the OLD joint spot when the fit joint moved.
    Move the control's _grp onto its DEF joint, keeping the curve where it is in the world."""
    GN = api.graph_nodes(); fixed = []
    for c in controls(api):
        src = [w for w in GN if w.startswith("wire_DEF_") and (w.endswith("_rx") or w.endswith("_rx_fng"))
               and c + ".rx" in api.node_connections(w)]
        if not src:
            continue
        dj = src[0][5:].rsplit("_rx", 1)[0]
        delta = [P(api, dj)[i] - P(api, c)[i] for i in range(3)]
        if max(abs(v) for v in delta) < 2e-3:
            continue
        m = api.world_matrix(c); p = api.curve_points(c)
        Wsh = [[m[0] * p[i] + m[4] * p[i + 1] + m[8] * p[i + 2] + m[12], m[1] * p[i] + m[5] * p[i + 1] + m[9] * p[i + 2] + m[13],
                m[2] * p[i] + m[6] * p[i + 1] + m[10] * p[i + 2] + m[14]] for i in range(0, len(p), 3)]
        g = parent(api, c); Rg = Rw(api, parent(api, g))
        ld = [sum(Rg[k][i] * delta[k] for k in range(3)) for i in range(3)]
        t = api.transform(g); api.set_transform(g, [t[i] + ld[i] for i in range(3)], t[3:6], t[6:9])
        R = Rw(api, c); o = P(api, c); loc = []
        for w in Wsh:
            d = [w[k] - o[k] for k in range(3)]
            loc += [sum(R[k][i] * d[k] for k in range(3)) for i in range(3)]
        api.set_curve_points(c, list(range(len(Wsh))), loc)
        fixed.append(c)
    return fixed


def fix_thumb_curl(api):
    """With custom thumb axes Rig Builder's thumb curl can open the thumb instead of closing it.
    Flip fng_c_DEF_ThumbFinger{1,2,3}_{L,R} when curl=1 moves the tip AWAY from MiddleFinger1."""
    flipped = []
    for s in ("_L", "_R"):
        sw = "CTL_ArmSwitch" + s
        if sw not in api.ls() or not api.attr_info(sw, "thumbCurl"):
            continue
        tip = "DEF_ThumbFinger4" + s; mid = P(api, "DEF_MiddleFinger1" + s)
        d0 = math.dist(P(api, tip), mid)
        api.set_attr(sw + ".thumbCurl", 1.0); d1 = math.dist(P(api, tip), mid); api.set_attr(sw + ".thumbCurl", 0.0)
        if d1 > d0:
            for k in (1, 2, 3):
                nd = "fng_c_DEF_ThumbFinger%d%s" % (k, s)
                api.set_node_param(nd, 1, -api.node_params(nd)[1])
            flipped.append(s)
    return flipped


def reparent_switches(api, where=None):
    """Switch controls cannot follow a DEF joint (it reads the switch's own fkIk -> loop).
    Default here: arm/spine switches under the FK end control, leg switches under IK foot."""
    where = where or {"CTL_ArmSwitch_L": "CTL_Wrist_L", "CTL_ArmSwitch_R": "CTL_Wrist_R",
                      "CTL_SpineSwitch_M": "CTL_Chest_M", "CTL_LegSwitch_L": "CTL_IKAnkle_L",
                      "CTL_LegSwitch_R": "CTL_IKAnkle_R"}
    for sw, tgt in where.items():
        g = sw + "_grp"
        if g not in api.ls() or tgt not in api.ls() or parent(api, g) == tgt:
            continue
        w0 = P(api, g); api.parent(g, tgt); w1 = P(api, g)
        if max(abs(w0[i] - w1[i]) for i in range(3)) > 1e-5:
            t = api.transform(g); api.set_transform(g, [t[i] + w0[i] - w1[i] for i in range(3)], t[3:6], t[6:9])


def after_rebuild(api, one_side=("Weapon", "Arrow"), prop_side="_R", labels=None, switches=None):
    """Everything Rebuild Rig drops or leaves behind, in order, then a report."""
    other = "_L" if prop_side == "_R" else "_R"
    delete_one_side_props(api, one_side, other)
    w = add_translate_wires(api)
    rest = sync_rest(api)
    piv = sync_control_pivots(api)
    th = fix_thumb_curl(api)
    reparent_switches(api, switches)
    for j, lab in (labels or {"DEF_Root_M": "root"}).items():
        if j in api.ls("Joint"): api.set_joint_label(j, "centre", lab)
    print("translate wires added:", w, "| rest synced:", rest, "| pivots moved:", piv, "| thumb curl flipped:", th)
    print("DEF vs fit:", def_vs_fit(api), "| check_rig:", api.check_rig())
    check_rig_moves(api)

# ----------------------------------------------------------------- skin

def influences(api, def_only=True, skip=r"End_|FootSide|Heel|Finger4_|Weapon|Arrow"):
    """DEF joints to bind a soft body to (game rig: DEF only, no end/pivot joints, no props)."""
    sk = re.compile(skip)
    return [j for j in api.ls("Joint") if j.startswith("DEF_") and not sk.search(j)]


def set_rigid(api, mesh, ids, joint):
    """Rigid piece (armour, mask, prop shell): every vertex 100% on one joint."""
    api.set_skin_weights([mesh.G[i] for i in ids], [[(joint, 1.0)]] * len(ids))


def rewrite(api, mesh, ids, fn, max_inf=4, min_w=0.01):
    """fn(i, weights_dict) -> new dict (or None to keep). Prunes < min_w, keeps max_inf, normalises."""
    vs = []; rows = []
    for i in ids:
        d = fn(i, dict(api.vertex_weights(mesh.G[i])))
        if d is None:
            continue
        keep = sorted([(j, w) for j, w in d.items() if w >= min_w], key=lambda t: -t[1])[:max_inf]
        t = sum(w for j, w in keep)
        if t <= 0:
            continue
        vs.append(mesh.G[i]); rows.append([(j, w / t) for j, w in keep])
    if vs:
        api.set_skin_weights(vs, rows)
    return len(vs)


def fix_cross_side(api, mesh, crotch_y=0.87, torso_x=0.08):
    """No vertex may carry the other side's joints: legs below the crotch (any |x|>3 mm),
    elsewhere beyond |x|>torso_x. Other-leg weight in the crotch crease goes to the hip root."""
    root = "DEF_Root_M" if "DEF_Root_M" in api.ls("Joint") else "DEF_Pelvis_M"

    def fn(i, d):
        x, y, z = mesh.p(i)
        if abs(x) <= 0.003:
            return None
        out = {}; ch = False
        for j, w in d.items():
            wrong = (j.endswith("_L") and x < 0) or (j.endswith("_R") and x > 0)
            if wrong and (y < crotch_y or abs(x) > torso_x or re.match(r"DEF_(Hip|Knee|Ankle|Toes)_", j)):
                ch = True
                j2 = root if (y >= crotch_y and re.match(r"DEF_(Hip|Knee|Ankle|Toes)_", j)) else j[:-1] + ("R" if j.endswith("_L") else "L")
                out[j2] = out.get(j2, 0) + w
            else:
                out[j] = out.get(j, 0) + w
        return out if ch else None
    return rewrite(api, mesh, range(mesh.n), fn)


def skin_report(api, obj):
    """Influence count, non-DEF influences, cross-side weights and far influences
    (limb joint > 12 cm farther than the nearest bone)."""
    m = Mesh(api, obj); J = api.ls("Joint")
    DEF = [j for j in J if j.startswith("DEF_")]
    kids = collections.defaultdict(list)
    for j in DEF:
        p = parent(api, j)
        if p: kids[p].append(j)
    pos = {j: P(api, j) for j in DEF}
    segs = {j: [(pos[j], pos[c]) for c in kids[j]] or [(pos[j], pos[j])] for j in DEF}
    jd = lambda j, p: min(seg_dist(p, a, b) for a, b in segs[j])
    maxinf = 0; nondef = 0; cross = 0; far = collections.Counter()
    for i in range(m.n):
        wt = api.vertex_weights(m.G[i]); p = m.p(i)
        maxinf = max(maxinf, len(wt))
        nondef += sum(1 for j, w in wt if not j.startswith("DEF_"))
        cross += any((j.endswith("_L") and p[0] < -0.08) or (j.endswith("_R") and p[0] > 0.08) for j, w in wt)
        if len(wt) > 1:
            dmin = min(jd(j, p) for j, w in wt if j in segs)
            for j, w in wt:
                if j in segs and w >= 0.02 and not re.match(r"DEF_(Root|Pelvis|Spine1|Chest)_", j) and jd(j, p) > max(0.18, dmin + 0.12):
                    far[j] += 1
    print("%s: max influences %d, non-DEF %d, cross-side verts %d, far influences %s"
          % (obj, maxinf, nondef, cross, dict(far.most_common(12))))


def deform_test(api, obj, tests, verts=None, switches=("CTL_ArmSwitch_L", "CTL_ArmSwitch_R", "CTL_LegSwitch_L", "CTL_LegSwitch_R", "CTL_SpineSwitch_M")):
    """mesh_data gives REST positions only, so compute linear-blend skinning ourselves.
    tests: [(control, (rx,ry,rz))]; limbs/spine are put in FK (autoSnap off) for the test.
    Returns {test: {vertex index: displacement}} for `verts` (all by default)."""
    m = Mesh(api, obj)
    W = {i: api.vertex_weights(m.G[i]) for i in (verts if verts is not None else range(m.n))}
    INF = sorted({j for wt in W.values() for j, w in wt})
    REST = {j: inv_rigid(M34(api, j)) for j in INF}
    saved = []
    for s in switches:
        if s in api.ls():
            v = {a: api.get_attr(s + "." + a) for a in ("autoSnap", "fkIk") if api.get_attr(s + "." + a) is not None}
            saved.append((s, v))
            for a in v: api.set_attr(s + "." + a, 0.0)
    out = {}
    try:
        for ctl, rot in tests:
            t = api.transform(ctl); api.set_transform(ctl, t[:3], list(rot), t[6:9])
            X = {j: mul34(M34(api, j), REST[j]) for j in INF}
            api.set_transform(ctl, t[:3], t[3:6], t[6:9])
            res = {}
            for i, wt in W.items():
                p = m.p(i); q = [0, 0, 0]
                for j, w in wt:
                    A = X[j]
                    for r in range(3): q[r] += w * (A[r][0] * p[0] + A[r][1] * p[1] + A[r][2] * p[2] + A[r][3])
                res[i] = math.dist(p, q)
            out[(ctl, tuple(rot))] = res
    finally:
        for s, v in saved:
            for a, val in v.items(): api.set_attr(s + "." + a, val)
    return out


def edge_stretch(api, obj, ctl, rot, region):
    """(min, max) edge length ratio inside `region` (vertex indices) for one pose: finds dents/tears."""
    m = Mesh(api, obj); reg = set(region)
    W = {i: api.vertex_weights(m.G[i]) for i in reg}
    INF = sorted({j for wt in W.values() for j, w in wt}); REST = {j: inv_rigid(M34(api, j)) for j in INF}
    t = api.transform(ctl); api.set_transform(ctl, t[:3], list(rot), t[6:9])
    X = {j: mul34(M34(api, j), REST[j]) for j in INF}; api.set_transform(ctl, t[:3], t[3:6], t[6:9])

    def q(i):
        p = m.p(i); o = [0, 0, 0]
        for j, w in W[i]:
            A = X[j]
            for r in range(3): o[r] += w * (A[r][0] * p[0] + A[r][1] * p[1] + A[r][2] * p[2] + A[r][3])
        return o
    Q = {i: q(i) for i in reg}; rs = []
    for a, b in m.edges:
        if a in reg and b in reg:
            l0 = math.dist(m.p(a), m.p(b))
            if l0 > 1e-4: rs.append((math.dist(Q[a], Q[b]) / l0, a, b))
    rs.sort()
    return rs[:5], rs[-5:]
