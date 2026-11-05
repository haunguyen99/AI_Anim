"""Helpers for rigging game characters in Frolvy, run INSIDE Frolvy through the MCP
execute_code tool (the `api` object is Frolvy's). Pure Python: Frolvy's Python has no numpy.

    import sys; sys.path.insert(0, r"D:\\Project\\AI_Anim\\.claude\\skills\\frolvy_rig\\scripts")
    import importlib, frolvy_rig_tools as R; importlib.reload(R)
    R.check_model(api)                      # step 1: read the model
    R.zero_controls(api)                    # before ANY Build / Rebuild Rig
    R.after_rebuild(api, one_side=("Weapon","Arrow"), prop_side="_R")   # after every Rebuild; names are prefixes ("ScarfA" = whole chain)
    R.skin_report(api, "Body")              # audit, then fix with the skin_* helpers
    R.skin_pass(api, "Body", R.BASTION_SKIN, head_neck_keep=ids, profile=True)   # after bind
    R.skin_pass(api, "Body", R.BASTION_SKIN, head_neck_keep=ids, profile=False)  # after a smooth
    R.thumb_into_palm(api)                  # thumb curls into the palm (after_rebuild calls it)
    R.deform_test(api, "Body", [("CTL_Hip_L",(-70,0,0))])
    R.pose_stretch(api, m, region, rest_fn, pose_fn)   # stretch in the user's real pose

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
    # fkIk back BEFORE autoSnap: restoring autoSnap first makes the fkIk change snap the
    # FK pose onto the IK controls (2026-11-03: CTL_PoleLeg_R/L ended 10-24 cm off, legs uneven)
    for k in ("fkIk", "autoSnap"):
        if k in s0: api.set_attr(sw + "." + k, s0[k])
    moved = math.dist(a, b) > 0.01
    print("rig moves:", moved)
    return moved

# ----------------------------------------------------------------- after a Rebuild

def delete_one_side_props(api, names=("Weapon", "Arrow"), side="_L"):
    """Build Rig mirrors every right-side joint; delete the mirrored copies of one-sided props
    and the wire_ nodes they leave (never touch wire_DEF_Root_M_*: Rig Builder's own)."""
    api.set_component_mode("object")   # delete_selection in face/vertex mode deletes scene-wide faces
    # names are prefixes: "ScarfA" takes the whole chain ScarfA1..ScarfAEnd. Chain controls are
    # NOT nested under the first one's _grp (Hero 2026-11-04), so every link is deleted itself.
    pat = re.compile(r"^(CTL|DEF)_(%s)\w*%s(_grp)?$" % ("|".join(map(re.escape, names)), side))
    found = [n for n in api.ls() if pat.match(n)]
    found.sort(key=lambda n: (not n.endswith("_grp"), not n.startswith("DEF_")))
    for n in found:
        if n in api.ls():
            api.select([n])
            if api.selection() == [n] and api.component_mode() == "object":
                api.delete_selection()
            if n in api.ls():
                print("WARNING could not delete", n)
    api.select([])
    for _ in range(2):
        for p in api.check_rig():
            w = p.split(":")[0]
            if w.startswith("wire_DEF_") and pat.match(w[5:].split("_" + side[1:] + "_")[0] + side):
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


def thumb_into_palm(api, gain=0.55, ry_ratio=-0.3, base=(35.0, 50.0, 60.0)):
    """Make curl/handPose turn the thumb INTO the palm (across, toward the pinky) like a human thumb.
    Rig Builder drives only the thumb's local Y (tip goes to the back of the hand or hangs down).
    Into-palm = local Z (with thumb axes X down the bone, Z = X x dir-to-MiddleFinger1).
    rz = fng_c (gain * base), ry = -ry_ratio * fng_c via a multiply node fng_cy_*.
    Bastion 2026-10-31: gain 0.55, ry_ratio -0.3 puts the fist thumb tip on the index/middle middle phalanges.
    Re-run after every Rebuild (it recreates the fng nodes). The rz input must be (re)connected
    explicitly: node_connections may list fng_c on rz_fng while it does not evaluate."""
    for s, sg in (("_L", 1.0), ("_R", -1.0)):
        for k in (1, 2, 3):
            fc = "fng_c_DEF_ThumbFinger%d%s" % (k, s)
            if fc not in api.graph_nodes():
                continue
            api.set_node_param(fc, 1, sg * base[k - 1] * gain)
            cy = "fng_cy_DEF_ThumbFinger%d%s" % (k, s)
            if cy not in api.graph_nodes():
                cy = api.create_node("multiply", cy)
            api.connect(cy, 0, fc); api.set_node_param(cy, 1, -ry_ratio)
            api.connect("wire_DEF_ThumbFinger%d%s_ry_fng" % (k, s), 1, cy)
            api.connect("wire_DEF_ThumbFinger%d%s_rz_fng" % (k, s), 1, fc)


def fix_thumb_curl(api):
    """With custom thumb axes Rig Builder's thumb curl can open the thumb instead of closing it.
    Flip fng_c_DEF_ThumbFinger{1,2,3}_{L,R} when curl=1 moves the tip AWAY from MiddleFinger1."""
    flipped = []
    hand = ("handPose", "curl", "spread", "thumbCurl")
    saved = {}
    for s in ("_L", "_R"):   # measure from an open hand: a fist left on the switch fakes the test
        sw = "CTL_ArmSwitch" + s
        if sw in api.ls():
            for a in hand:
                if api.attr_info(sw, a):
                    saved[(sw, a)] = api.get_attr(sw + "." + a); api.set_attr(sw + "." + a, 0.0)
    try:
        _fix_thumb_curl(api, flipped)
    finally:
        for (sw, a), v in saved.items():
            api.set_attr(sw + "." + a, v)
    return flipped


def _thumb_tip(api, s):
    """Last thumb joint: Human05 has ThumbFinger4; mitten rigs (Windy) end at ThumbFinger3."""
    names = set(api.ls())
    for k in (4, 3, 2):
        if "DEF_ThumbFinger%d%s" % (k, s) in names:
            return "DEF_ThumbFinger%d%s" % (k, s)


def _fix_thumb_curl(api, flipped):
    for s in ("_L", "_R"):
        sw = "CTL_ArmSwitch" + s
        if sw not in api.ls() or not api.attr_info(sw, "thumbCurl"):
            continue
        tip = _thumb_tip(api, s); mid = P(api, "DEF_MiddleFinger1" + s)
        d0 = math.dist(P(api, tip), mid)
        api.set_attr(sw + ".thumbCurl", 1.0); d1 = math.dist(P(api, tip), mid); api.set_attr(sw + ".thumbCurl", 0.0)
        if d1 > d0:
            flip = lambda: [api.set_node_param(nd, 1, -api.node_params(nd)[1])
                            for nd in ("fng_c_DEF_ThumbFinger%d%s" % (k, s) for k in (1, 2, 3))
                            if nd in api.ls()]
            flip()
            api.set_attr(sw + ".thumbCurl", 1.0); d2 = math.dist(P(api, tip), mid); api.set_attr(sw + ".thumbCurl", 0.0)
            if d2 >= d0:      # flipping did not close the thumb either: undo, report
                flip(); flipped.append(s + "?")
            else:
                flipped.append(s)
    # final check the user sees: curl / handPose must bring the tip closer to MiddleFinger1
    for s in ("_L", "_R"):
        sw = "CTL_ArmSwitch" + s
        if sw not in api.ls():
            continue
        tip = _thumb_tip(api, s); mid = P(api, "DEF_MiddleFinger1" + s); d0 = math.dist(P(api, tip), mid)
        old = api.get_attr(sw + ".handPose"); api.set_attr(sw + ".handPose", 1.0)
        d1 = math.dist(P(api, tip), mid); api.set_attr(sw + ".handPose", old)
        if d1 >= d0:
            print("WARNING thumb%s opens on handPose=1 (%.3f -> %.3f): flip fng_c_DEF_ThumbFinger*%s" % (s, d0, d1, s))
    return flipped


def reparent_switches(api, where=None):
    """Put each switch under Rig Builder's <FK end>_follow group (parent-constrained to the DEF joint):
    it then follows the limb in IK AND FK with no loop (Hero 2026-11-04, tested both modes).
    Under the FK end control (the old default) it stays behind when the limb is in IK - user:
    "khi di chuyển ik tay, switch control chưa đi theo". Falls back to the old parents when a rig
    has no _follow groups."""
    old = {"CTL_ArmSwitch_L": "CTL_Wrist_L", "CTL_ArmSwitch_R": "CTL_Wrist_R",
           "CTL_SpineSwitch_M": "CTL_Chest_M", "CTL_LegSwitch_L": "CTL_IKAnkle_L",
           "CTL_LegSwitch_R": "CTL_IKAnkle_R"}
    follow = {"CTL_ArmSwitch_L": "CTL_Wrist_L_follow", "CTL_ArmSwitch_R": "CTL_Wrist_R_follow",
              "CTL_SpineSwitch_M": "CTL_Chest_M_follow", "CTL_LegSwitch_L": "CTL_Ankle_L_follow",
              "CTL_LegSwitch_R": "CTL_Ankle_R_follow"}
    have = set(api.ls())
    where = where or {sw: (follow[sw] if follow[sw] in have else old[sw]) for sw in old}
    for sw, tgt in where.items():
        g = sw + "_grp"
        if g not in api.ls() or tgt not in api.ls() or parent(api, g) == tgt:
            continue
        w0 = P(api, g); api.parent(g, tgt); w1 = P(api, g)
        if max(abs(w0[i] - w1[i]) for i in range(3)) > 1e-5:
            t = api.transform(g); api.set_transform(g, [t[i] + w0[i] - w1[i] for i in range(3)], t[3:6], t[6:9])


def _curve_world(api, c):
    q = api.curve_points(c); M = api.world_matrix(c)
    return [(M[0] * q[i] + M[4] * q[i + 1] + M[8] * q[i + 2] + M[12],
             M[1] * q[i] + M[5] * q[i + 1] + M[9] * q[i + 2] + M[13],
             M[2] * q[i] + M[6] * q[i + 1] + M[10] * q[i + 2] + M[14]) for i in range(0, len(q), 3)]


def match_switches(api, pairs=(("CTL_ArmSwitch", "DEF_Wrist"), ("CTL_LegSwitch", "DEF_Ankle"))):
    """Left and right switch icons the same size and in mirrored places, at the REST pose.
    Build Rig + fit() left Hero's right arm switch 2 cm wide, inside the hand, while the left one was
    5.6 cm and 35 cm above / 22 cm outside the wrist (user: "shape control switch ở tay phải bé quá",
    "đặt vị trí giống tay trái để dễ nhìn hơn"). The side whose icon sits farther from its joint
    (the one fit() slid out of the mesh) is copied onto the other."""
    for sw, jn in pairs:
        L, Rr = sw + "_L", sw + "_R"
        if L not in api.ls() or Rr not in api.ls():
            continue
        cen = lambda c: [sum(p[k] for p in _curve_world(api, c)) / len(_curve_world(api, c)) for k in range(3)]  # noqa: E731
        ext = lambda c: max(max(p[k] for p in _curve_world(api, c)) - min(p[k] for p in _curve_world(api, c)) for k in range(3))  # noqa: E731
        dist = {s: math.dist(cen(sw + s), P(api, jn + s)) for s in ("_L", "_R")}
        src, dst = ("_L", "_R") if dist["_L"] >= dist["_R"] else ("_R", "_L")
        S, D = sw + src, sw + dst
        # size: scale the shape about its own centre
        q = api.curve_points(D); n = len(q) // 3
        lc = [sum(q[3 * i + k] for i in range(n)) / n for k in range(3)]
        k = ext(S) / max(ext(D), 1e-9)
        api.set_curve_points(D, list(range(n)), [lc[j] + (q[3 * i + j] - lc[j]) * k for i in range(n) for j in range(3)])
        # place: mirror the source centre across x, move the group in its parent's space
        cs, cd = cen(S), cen(D)
        d = (-cs[0] - cd[0], cs[1] - cd[1], cs[2] - cd[2])
        g = D + "_grp"; M = api.world_matrix(parent(api, g))
        R3 = ((M[0], M[4], M[8]), (M[1], M[5], M[9]), (M[2], M[6], M[10]))
        dl = _solve3(R3, d)
        t = api.transform(g); api.set_transform(g, [t[i] + dl[i] for i in range(3)], t[3:6], t[6:9])
        cd2 = cen(D)
        print("%s: %s copied onto %s (size x%.2f, mirror error %.4f)" % (sw, src, dst, k, math.dist((-cs[0], cs[1], cs[2]), cd2)))


def _solve3(m, v):
    """Solve m * x = v for a 3x3 m (rows)."""
    (a, b, c), (d, e, f), (g, h, i) = m
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-12:
        return v
    inv = ((e * i - f * h, c * h - b * i, b * f - c * e),
           (f * g - d * i, a * i - c * g, c * d - a * f),
           (d * h - e * g, b * g - a * h, a * e - b * d))
    return tuple(sum(inv[r][k] * v[k] for k in range(3)) / det for r in range(3))


def after_rebuild(api, one_side=("Weapon", "Arrow"), prop_side="_R", labels=None, switches=None):
    """Everything Rebuild Rig drops or leaves behind, in order, then a report."""
    other = "_L" if prop_side == "_R" else "_R"
    delete_one_side_props(api, one_side, other)
    w = add_translate_wires(api)
    rest = sync_rest(api)
    piv = sync_control_pivots(api)
    thumb_into_palm(api)
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
        # fkIk back BEFORE autoSnap (else the switch snaps FK pose onto IK/pole controls:
        # 2026-11-03 Ninja poles ended 7.6 cm off, FK arm got 0.2-0.4 deg)
        for k in ("fkIk", "autoSnap"):
            for s, v in saved:
                if k in v: api.set_attr(s + "." + k, v[k])
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


# ----------------------------------------------------------------- skin pass by region
# Rules the user settled on (Boss Bastion, 2026-10-31). Heights are metres in the bind pose;
# measure them on a new character (joint heights, belt edges, knee, boot top) and pass a cfg.
# Order matters: each step only redistributes ONE family of joints and keeps the others,
# and rigid shells are re-applied LAST because every height split or smooth bends them.

BASTION_SKIN = {
    "torso_x": 0.34,            # |x| inside which a vertex is torso (outside = arms)
    "lower_belt_top": 1.115,    # lower belt / hip armour: Root, with a little Spine1 at its top
    "lower_belt_spine1": 0.15,  # Spine1 share at that top edge, fading to 0 at lower_belt_fade
    "lower_belt_fade": 1.0,
    "root_spine1": (1.115, 1.20),   # Root -> Spine1 blend, inside the upper belt
    "spine1_chest": (1.26, 1.40),   # Spine1 -> Chest blend
    "hip_knee": (0.57, 0.65),       # knee joint at 0.60
    "knee_ankle": (0.24, 0.30),     # ankle joint at 0.21, boot top just above
    "toes_z": (0.10, 0.18), "toes_y": (0.10, 0.16),   # toe cap: in front of the toe joint, low
    "armpit_shoulder": (0.29, 0.36),  # Shoulder fades out inside the shoulder joint (|x|)
    "armpit_scapula": (0.20, 0.33),   # front-chest Scapula at most half, less toward the middle
    # shell index -> joint (or {"top_y": y, "top": joint, "rest": joint} for a hinged pad)
    "rigid": {1: "DEF_Head_M", 17: "DEF_Head_M", 18: "DEF_Head_M",
              4: "DEF_ShoulderPad_L", 10: "DEF_ShoulderPad_L", 5: "DEF_ShoulderPad_R",
              6: "DEF_HipPad2_L", 8: "DEF_HipPad2_R",
              7: {"top_y": 1.09, "top": "DEF_Root_M", "rest": "DEF_HipPad1_L"},
              9: {"top_y": 1.09, "top": "DEF_Root_M", "rest": "DEF_HipPad1_R"},
              11: "DEF_Knee_L", 13: "DEF_Knee_L", 14: "DEF_Knee_L",
              12: "DEF_Knee_R", 15: "DEF_Knee_R", 16: "DEF_Knee_R", 19: "DEF_Wrist_L"},
}
SPINE = ("DEF_Root_M", "DEF_Spine1_M", "DEF_Chest_M")


def _leg(s):
    return ("DEF_Hip" + s, "DEF_Knee" + s, "DEF_Ankle" + s, "DEF_Toes" + s)


def skin_torso(api, m, cfg=BASTION_SKIN, ids=None):
    """Re-split each torso vertex's Root+Spine1+Chest share by height; arm/leg/pad weights stay.
    Default bind smeared Root 40% into the belly and put Root 89% next to Chest on the ribs
    (x25 tear on a spine twist); after this the worst was x1.9."""
    a0, a1 = cfg["root_spine1"]; b0, b1 = cfg["spine1_chest"]
    top, f_top, fade = cfg["lower_belt_top"], cfg["lower_belt_spine1"], cfg["lower_belt_fade"]

    def fn(i, d):
        x, y, z = m.p(i)
        if abs(x) > cfg["torso_x"]:
            return None
        sp = sum(d.get(j, 0) for j in SPINE)
        if sp <= 0:
            return None
        if y < top:
            a = f_top * ramp(y, fade, top); b = 0.0
        else:
            a = ramp(y, a0, a1); b = ramp(y, b0, b1)
        out = {j: w for j, w in d.items() if j not in SPINE}
        for j, f in (("DEF_Root_M", 1 - a), ("DEF_Spine1_M", a * (1 - b)), ("DEF_Chest_M", a * b)):
            if f > 1e-3:
                out[j] = out.get(j, 0) + sp * f
        return out
    return rewrite(api, m, ids if ids is not None else range(m.n), fn)


def skin_legs(api, m, cfg=BASTION_SKIN, ids=None):
    """Re-split each leg vertex's Hip+Knee+Ankle+Toes share by height (Root share kept).
    Default bind let Hip reach the shin, Knee the foot, Ankle/Toes the calf: lifting the leg
    crushed the knee and turning the foot dented the calf."""
    h0, h1 = cfg["hip_knee"]; k0, k1 = cfg["knee_ankle"]
    allj = _leg("_L") + _leg("_R")

    def fn(i, d):
        x, y, z = m.p(i)
        s = "_L" if x > 0 else "_R"
        share = sum(w for j, w in d.items() if j in allj)
        if share <= 0:
            return None
        hk = ramp(y, h0, h1); ka = ramp(y, k0, k1)
        toe = ramp(z, *cfg["toes_z"]) * (1 - ramp(y, *cfg["toes_y"]))
        prof = {"Hip": hk, "Knee": (1 - hk) * ka, "Ankle": (1 - hk) * (1 - ka) * (1 - toe),
                "Toes": (1 - hk) * (1 - ka) * toe}
        out = {j: w for j, w in d.items() if j not in allj}
        for k, f in prof.items():
            if f > 1e-3:
                out["DEF_" + k + s] = out.get("DEF_" + k + s, 0) + share * f
        return out
    return rewrite(api, m, ids if ids is not None else range(m.n), fn)


def skin_armpit(api, m, cfg=BASTION_SKIN, ids=None):
    """Chest plate beside the armpit must not follow the arm: Shoulder fades to 0 inside the
    shoulder joint, front-chest Scapula at most half. Removed weight goes to Chest."""
    s0, s1 = cfg["armpit_shoulder"]; c0, c1 = cfg["armpit_scapula"]

    def fn(i, d):
        x, y, z = m.p(i); ax = abs(x); out = {}; moved = 0.0
        if not (cfg.get("armpit_y", (1.15, 1.56))[0] < y < cfg.get("armpit_y", (1.15, 1.56))[1]):
            return None          # only the chest plate beside the armpit, not the shoulder top
        for j, w in d.items():
            cap = 1.0            # caps, not factors: running the rule twice changes nothing
            if j.startswith("DEF_Shoulder_") and ax < s1:
                cap = 0.5 * ramp(ax, s0, s1)
            elif j.startswith("DEF_Scapula_") and z > 0.03 and ax < c1 and y < 1.5:
                cap = 0.35 * ramp(ax, c0, c1)    # none toward the sternum
            k = min(w, cap)
            out[j] = out.get(j, 0) + k; moved += w - k
        if moved < 1e-4:
            return None
        out["DEF_Chest_M"] = out.get("DEF_Chest_M", 0) + moved
        return out
    return rewrite(api, m, ids if ids is not None else range(m.n), fn)


def skin_no_head_neck(api, m, keep):
    """Only `keep` (helmet, mask, real neck: vertex indices) may carry Head/Neck, so the collar
    and chest stay still when the head or neck turns (user: no Head/Neck on the collar, ever)."""
    keep = set(keep)

    def fn(i, d):
        if i in keep:
            return None
        n = d.pop("DEF_Neck_M", 0) + d.pop("DEF_Head_M", 0)
        if not n:
            return None
        d["DEF_Chest_M"] = d.get("DEF_Chest_M", 0) + n
        return d
    return rewrite(api, m, range(m.n), fn)


def skin_rigid(api, m, cfg=BASTION_SKIN):
    """Rigid armour/prop shells back to one joint each (hinged pads: top row on `top`)."""
    n = 0
    for k, tgt in cfg["rigid"].items():
        if k >= len(m.shells):
            continue
        s = m.shells[k]
        if isinstance(tgt, dict):
            top = [i for i in s if m.p(i)[1] > tgt["top_y"]]
            set_rigid(api, m, top, tgt["top"])
            set_rigid(api, m, [i for i in s if i not in set(top)], tgt["rest"])
        else:
            set_rigid(api, m, s, tgt)
        n += len(s)
    return n


def skin_lower_belt(api, m, cfg=BASTION_SKIN):
    """Lower belt / hip armour below lower_belt_top: spine share back to Root with only a little
    Spine1 at its top edge (user: Spine1 made it cave in; then 'a little, so it is not stiff')."""
    top, f_top, fade = cfg["lower_belt_top"], cfg["lower_belt_spine1"], cfg["lower_belt_fade"]

    def fn(i, d):
        x, y, z = m.p(i)
        if abs(x) > cfg["torso_x"] or y >= top:
            return None
        sp = sum(d.get(j, 0) for j in SPINE)
        if sp <= 0:
            return None
        a = f_top * ramp(y, fade, top)
        out = {j: w for j, w in d.items() if j not in SPINE}
        out["DEF_Root_M"] = out.get("DEF_Root_M", 0) + sp * (1 - a)
        if a > 1e-3:
            out["DEF_Spine1_M"] = out.get("DEF_Spine1_M", 0) + sp * a
        return out
    return rewrite(api, m, range(m.n), fn)


def skin_pass(api, obj="Body", cfg=BASTION_SKIN, head_neck_keep=None, profile=True):
    """The whole agreed clean-up, in order. profile=True right after a bind (re-split torso and
    legs by height); profile=False after a smooth/hammer (keep the smoothing, only re-apply the
    hard rules: lower belt, armpit, no Head/Neck on the collar, no cross-side, rigid shells).
    head_neck_keep: vertex indices allowed to keep Head/Neck (helmet, mask, real neck)."""
    m = Mesh(api, obj)
    out = {}
    if profile:
        out["torso"] = skin_torso(api, m, cfg); out["legs"] = skin_legs(api, m, cfg)
    out["lower_belt"] = skin_lower_belt(api, m, cfg)
    out["armpit"] = skin_armpit(api, m, cfg)
    if head_neck_keep is not None:
        out["no_head_neck"] = skin_no_head_neck(api, m, head_neck_keep)
    out["cross_side"] = fix_cross_side(api, m)
    out["rigid"] = skin_rigid(api, m, cfg)
    print("skin_pass:", out)
    return out


def pose_stretch(api, m, region, rest, pose):
    """Edge length ratios of `region` between the bind pose and a pose, both set by callables
    (rest() puts the posed controls at 0, pose() sets the user's pose). Use this, not
    edge_stretch, when the scene is already posed: edge_stretch takes the CURRENT pose as rest.
    Returns (sorted [(ratio, a, b)], {vertex: posed position})."""
    reg = set(region); W = {i: api.vertex_weights(m.G[i]) for i in reg}
    INF = sorted({j for wt in W.values() for j, w in wt})
    rest(); REST = {j: inv_rigid(M34(api, j)) for j in INF}
    pose(); X = {j: mul34(M34(api, j), REST[j]) for j in INF}

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
            if l0 > 2e-3: rs.append((math.dist(Q[a], Q[b]) / l0, a, b))
    rs.sort()
    return rs, Q
