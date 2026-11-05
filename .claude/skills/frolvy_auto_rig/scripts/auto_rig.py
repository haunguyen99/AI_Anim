"""Whole game-rig flow in Frolvy, as used on Hero RPG2 (2026-11-04). Run INSIDE Frolvy (MCP execute_code):

    import sys; sys.path.insert(0, r"D:\\Project\\AI_Anim\\.claude\\skills\\frolvy_auto_rig\\scripts")
    import importlib, auto_rig as A; importlib.reload(A)

    A.survey(api)                                   # 1. meshes, shells (pieces), open sheets
    A.cut(api, "body", [3], 1, [0.4, 0.6], side="R")  #    sections of chosen shells only
    A.panels(api, "body", 7, [0.9, 0.7, 0.5])       #    a skirt: which angles are cloth, where the slits are
    A.panel_line(api, "body", 7, -150, -30, ys)     #    centre line of one panel (for its joint chain)
    #  2. write the fit table (references/make_fit_template.py, run OUTSIDE Frolvy), then:
    api.load_fit_skeleton(path)
    A.fit_diff(api, path)                           # 3. what the user moved since the last save
    A.restore_children(api, path)                   #    keep their joints, put the children back
    A.add_chains(api, rows, path)                   # 4. extra chains (skirt, scarf, cape) under Root/Chest
    A.build(api, one_side=("ScarfA", "ScarfB"))     # 5. build + clean + snug controls + checks
Rules (base joints only, Root_M = hip, DEF-only skin...) live in the frolvy_rig skill.
"""
import json
import math
import re
import sys

for _p in (r"D:\Project\AI_Anim\.claude\skills\frolvy_rig\scripts", r"D:\Project\AI_Anim\tools\frolvy_plugins\fit_controls"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import frolvy_rig_tools as R      # noqa: E402
import fit_controls as FC         # noqa: E402


def _obj(api, name):
    """Accept a short name ("body") for a mesh ("char_main_t2_body")."""
    objs = api.ls("Object")
    if name in objs:
        return name
    hit = [o for o in objs if o.lower().endswith(name.lower())]
    if len(hit) != 1:
        raise ValueError("mesh %r: %s" % (name, hit or objs))
    return hit[0]


# ----------------------------------------------------------------- 1. read the model

def survey(api):
    """Every mesh: size, axis, mirror, and every shell (separate piece) with its bounds and how open it is.
    Open pieces (boundary edges) are sheets: skirt, cape, scarf, hood. They need their own joints or rules."""
    R.check_model(api)
    for o in api.ls("Object"):
        m = R.Mesh(api, o)
        md = api.mesh_data(o); fc = md["face_corners"]; fs = md["face_sizes"]
        # boundary edges by welded position (FBX splits UV seams)
        P = [tuple(md["positions"][3 * k:3 * k + 3]) for k in range(len(md["positions"]) // 3)]
        w = lambda v: (round(P[v][0], 4), round(P[v][1], 4), round(P[v][2], 4))  # noqa: E731
        cnt = {}; i = 0
        for s in fs:
            F = fc[i:i + s]; i += s
            for k in range(s):
                e = tuple(sorted((w(F[k]), w(F[(k + 1) % s]))))
                cnt[e] = cnt.get(e, 0) + 1
        print("%s: %d verts, %d shells" % (o, m.n, len(m.shells)))
        for si, sh in enumerate(m.shells):
            pts = [m.p(v) for v in sh]
            b = [(min(p[k] for p in pts), max(p[k] for p in pts)) for k in range(3)]
            print("  shell %2d %4d v  x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % (si, len(sh), b[0][0], b[0][1], b[1][0], b[1][1], b[2][0], b[2][1]))
        nb = sum(1 for v in cnt.values() if v == 1)
        print("  open edges: %d of %d%s" % (nb, len(cnt), "  (sheet pieces: check which shells)" if nb else ""))


def cut(api, obj, shells, axis, values, side=None, extra=None):
    """Edge cross-sections of the chosen shells only (R.sections cuts the biggest piece only).
    side "R" keeps x<0, "L" x>0. Prints bounds and centre per cut; returns [(value, centre, lo, hi)]."""
    m = R.Mesh(api, _obj(api, obj)); S = set()
    for i in shells:
        S.update(m.shells[i])
    o = [i for i in range(3) if i != axis]; out = []
    for v in values:
        pts = []
        for a, b in m.edges:
            if a in S and b in S:
                pa, pb = m.p(a), m.p(b)
                if (pa[axis] - v) * (pb[axis] - v) < 0:
                    t = (v - pa[axis]) / (pb[axis] - pa[axis]); q = [pa[k] + (pb[k] - pa[k]) * t for k in range(3)]
                    if (side == "R" and q[0] > 0) or (side == "L" and q[0] < 0) or (extra and not extra(q)):
                        continue
                    pts.append(q)
        if not pts:
            print("%s=%.3f -" % ("xyz"[axis], v)); continue
        lo = [min(q[k] for q in pts) for k in range(3)]; hi = [max(q[k] for q in pts) for k in range(3)]
        c = [(lo[k] + hi[k]) / 2 for k in range(3)]
        print("%s=%.3f  " % ("xyz"[axis], v) + "  ".join("%s %.3f..%.3f (c %.3f)" % ("xyz"[k], lo[k], hi[k], c[k]) for k in o) + "  n%d" % len(pts))
        out.append((v, c, lo, hi))
    return out


def _ring_points(m, S, y):
    pts = []
    for a, b in m.edges:
        if a in S and b in S:
            pa, pb = m.p(a), m.p(b)
            if (pa[1] - y) * (pb[1] - y) < 0:
                t = (y - pa[1]) / (pb[1] - pa[1]); pts.append([pa[k] + (pb[k] - pa[k]) * t for k in range(3)])
    return pts


def panels(api, obj, shell, ys, centre_z=None, gap_deg=20):
    """A skirt / cape seen from above at each height: angle 0 = front (+Z), +-180 = back, negative = right.
    Prints the angle ranges that are cloth and the gaps (slits) between them."""
    m = R.Mesh(api, _obj(api, obj)); S = set(m.shells[shell])
    if centre_z is None:
        r = R.P(api, "Root") if "Root" in api.ls("Joint") else [0, 0, 0]
        centre_z = r[2]
    for y in ys:
        pts = _ring_points(m, S, y)
        if not pts:
            print("y%.2f -" % y); continue
        # whole degrees in -180..179 (180 and -180 are one spot, or the back seam shows as two slits)
        ang = sorted(set((round(math.degrees(math.atan2(q[0], q[2] - centre_z))) + 180) % 360 - 180 for q in pts))
        gaps = [(ang[i], ang[i + 1]) for i in range(len(ang) - 1) if ang[i + 1] - ang[i] > gap_deg]
        if ang[0] + 360 - ang[-1] > gap_deg:
            gaps.append((ang[-1], ang[0]))
        print("y%.2f n%d  cloth %d..%d  slits %s" % (y, len(pts), ang[0], ang[-1], gaps))


def panel_line(api, obj, shell, lo_deg, hi_deg, ys, centre_z=None):
    """Centre line of one panel between two angles (lo > hi wraps through the back, e.g. 155, -155).
    Returns [(y, x, z)] - the joint chain goes along it, top joint at the waistband."""
    m = R.Mesh(api, _obj(api, obj)); S = set(m.shells[shell])
    if centre_z is None:
        r = R.P(api, "Root") if "Root" in api.ls("Joint") else [0, 0, 0]
        centre_z = r[2]
    out = []
    for y in ys:
        pts = []
        for q in _ring_points(m, S, y):
            an = math.degrees(math.atan2(q[0], q[2] - centre_z))
            if (lo_deg <= an <= hi_deg) if lo_deg < hi_deg else (an >= lo_deg or an <= hi_deg):
                pts.append(q)
        if pts:
            c = [(min(q[k] for q in pts) + max(q[k] for q in pts)) / 2 for k in range(3)]
            print("  y%.2f n%2d c(%.3f, %.3f)  x %.3f..%.3f  z %.3f..%.3f" % (y, len(pts), c[0], c[2],
                  min(q[0] for q in pts), max(q[0] for q in pts), min(q[2] for q in pts), max(q[2] for q in pts)))
            out.append((y, c[0], c[2]))
    low = min(m.p(v)[1] for v in S)
    print("  lowest y %.3f" % low)
    return out


# ----------------------------------------------------------------- 3. after the user moves joints

def _quat(q):
    x, y, z, w = q
    return ((1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)),
            (2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)),
            (2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)))


def _saved(path):
    """Saved fit: world position, world rotation, parent and local frame (translate + rotation) per joint.
    Joints the user ROTATED carry it in 'rotate' (quaternion) / 'orient' (degrees): their children are
    placed through that rotation, so plain sums of translates are wrong (Hero SkirtSide1, MiddleFinger1)."""
    J = json.load(open(path, encoding="utf-8"))["joints"]
    W, ROT, LOC = {}, {}, {}
    for j in J:
        n = j["name"]
        o = j.get("orient") or [0.0, 0.0, 0.0]
        lr = FC._mm(FC._rot(*o), _quat(j.get("rotate") or [0.0, 0.0, 0.0, 1.0]))
        if j["parent"] >= 0:
            p = J[j["parent"]]["name"]
            W[n] = tuple(a + b for a, b in zip(FC._mv(ROT[p], j["translate"]), W[p]))
            ROT[n] = FC._mm(ROT[p], lr)
        else:
            W[n] = tuple(j["translate"]); ROT[n] = lr
        LOC[n] = (tuple(j["translate"]), lr)
    par = {j["name"]: (J[j["parent"]]["name"] if j["parent"] >= 0 else None) for j in J}
    return W, par, LOC


def _now(api, n):
    M = api.world_matrix(n)
    R3 = ((M[0], M[4], M[8]), (M[1], M[5], M[9]), (M[2], M[6], M[10]))
    return R3, (M[12], M[13], M[14])


def _local_now(api, n, p):
    R3, T = _now(api, n)
    if not p:
        return T, R3
    PR, PT = _now(api, p); I = FC._inv3(PR)
    return FC._mv(I, tuple(T[k] - PT[k] for k in range(3))), FC._mm(I, R3)


def fit_diff(api, path, tol=1e-4, rtol=1e-3):
    """Compare the fit skeleton in the scene with the saved .fvfit.
    changed = the user moved or rotated it (its frame relative to its parent differs);
    moved = only dragged along by a parent."""
    W, par, LOC = _saved(path)
    have = set(api.ls("Joint"))
    changed, moved = [], []
    for n in W:
        if n not in have:
            print("  gone:", n); continue
        t, r = _local_now(api, n, par[n])
        st, sr = LOC[n]
        dt = max(abs(t[k] - st[k]) for k in range(3))
        dr = max(abs(r[i][k] - sr[i][k]) for i in range(3) for k in range(3))
        w = _now(api, n)[1]
        if dt > tol or dr > rtol:
            changed.append(n)
            print("  CHANGED %-14s %s%s now %s was %s" % (n, "move " if dt > tol else "", "rotate" if dr > rtol else "",
                  [round(v, 4) for v in w], [round(v, 4) for v in W[n]]))
        elif max(abs(w[k] - W[n][k]) for k in range(3)) > tol:
            moved.append(n)
    new = [n for n in have if n not in W and not re.match(r"(DEF|CTL|PIV|IK)_", n)]
    print("changed %d, dragged along %d, new %s" % (len(changed), len(moved), new))
    return changed, moved


def restore_children(api, path, keep=None, save=True):
    """Keep every joint the user changed; put each direct child of a changed joint back at its saved
    world spot, so hands, feet, scarf, etc. stay on the mesh (deeper joints follow). Saves the fit."""
    W, par, LOC = _saved(path)
    changed, _ = fit_diff(api, path)
    keep = set(keep or ()) | set(changed)
    have = set(api.ls("Joint"))
    fixed = []
    for n, p in par.items():
        if p in changed and n not in keep and n in have:
            PR, PT = _now(api, p)
            api.move(n, *FC._mv(FC._inv3(PR), tuple(W[n][k] - PT[k] for k in range(3))))
            fixed.append(n)
    now = {r["name"]: tuple(r["world"]) for r in api.joint_info()}
    off = [(n, round(max(abs(now[n][k] - W[n][k]) for k in range(3)), 4)) for n in W
           if n in now and n not in keep and max(abs(now[n][k] - W[n][k]) for k in range(3)) > 1e-4]
    print("kept (user):", sorted(changed)); print("put back:", fixed); print("still off saved spot:", off)
    if save:
        print("saved fit:", api.save_fit_skeleton(path))
    return fixed


# ----------------------------------------------------------------- 4. extra chains

def add_chains(api, rows, path=None):
    """rows: [(name, parent, (x,y,z) world, side, label, radius)], parents first. label "prop" for
    cloth/armour links, "" for the end joint. Draw only centre + right; Build mirrors the right side.
    Note api.parent(n) with ONE argument UN-parents n: never use it to ask for the parent."""
    have = set(api.ls("Joint"))
    for n, p, w, side, lab, r in rows:
        if n not in have:
            api.select([p]); j = api.create_joint()
            if j != n:
                api.rename(j, n)
        api.parent(n, p)
    for n, p, w, side, lab, r in rows:
        pw = R.P(api, p)
        api.move(n, *(w[k] - pw[k] for k in range(3)))
        api.set_joint_label(n, side, lab); api.set_joint_radius(n, r)
    api.select([])
    info = {x["name"]: x for x in api.joint_info()}
    bad = [(n, info[n]["parent"], p) for n, p, *_ in rows if info[n]["parent"] != p]
    err = max(max(abs(info[n]["world"][k] - w[k]) for k in range(3)) for n, p, w, *_ in rows)
    print("added %d joints, parent errors %s, max position error %.4f" % (len(rows), bad, err))
    if path:
        print("saved fit:", api.save_fit_skeleton(path))
    return not bad


# ----------------------------------------------------------------- 5. build

def build(api, one_side=(), prop_side="_R", save_to=None):
    """Game-rig Build Rig: no helper set / twist / bendy, then clean what Build mirrored or dropped,
    then draw the controls snug to the mesh, then check. one_side: PREFIXES of one-sided chains whose
    mirrored copy is deleted ("ScarfA" takes ScarfA1..ScarfAEnd). Two-handed props (dual blades) stay out."""
    R.zero_controls(api)
    api.set_helper_set(False); api.set_bendy_limbs(False)
    if not api.build_rig():
        print("Build Rig refused"); return False
    J = api.ls("Joint")
    extra = [j for j in J if re.search(r"Twist|Bend|^PRT|^HLP|^MUS", j)]
    print("DEF joints:", len([j for j in J if j.startswith("DEF_")]), "| twist/helper:", extra)
    R.after_rebuild(api, one_side=tuple(one_side), prop_side=prop_side)
    other = "_L" if prop_side == "_R" else "_R"
    left = [n for n in api.ls() if any(re.match(r"^(CTL|DEF)_%s\w*%s(_grp)?$" % (re.escape(p), other), n) for p in one_side)]
    print("mirrored one-sided leftovers:", left)
    done = FC.snug(api)
    rest = [c for c in sorted(c for c in api.ls("Curve") if c.startswith("CTL_")) if c not in done or "Switch" in c]
    FC.fit(api, controls=rest)
    R.match_switches(api)        # L/R switch icons: same size, mirrored place (fit() moves only one side out)
    sw = {g: R.parent(api, g) for g in ("CTL_ArmSwitch_L_grp", "CTL_ArmSwitch_R_grp", "CTL_LegSwitch_L_grp",
                                        "CTL_LegSwitch_R_grp", "CTL_SpineSwitch_M_grp") if g in api.ls()}
    print("switch parents:", sw)
    print("DEF vs fit (current / FK):", R.def_vs_fit_both(api))
    print("check_rig:", [x for x in api.check_rig() if "fng_cy" not in x])
    ok = R.check_rig_moves(api)
    if save_to:
        print("saved scene:", api.save_scene(save_to))
    return ok


# ----------------------------------------------------------------- 6. skin by rules
# Characters made of many separate pieces (Hero: pants, boots, skirt, guards, pads, hood, scarves)
# skin best by writing every vertex's weights from rules, piece by piece, instead of cleaning a bind.

def ramp(v, a, b):
    """0 at a, 1 at b (either direction), clamped."""
    if a == b:
        return 1.0 if v >= b else 0.0
    t = (v - a) / (b - a)
    return 0.0 if t < 0 else 1.0 if t > 1 else t


_POS = {}


def _jp(api, j):
    """Joint REST position (bind pose), cached during one write_skin run. Not R.P: that is the
    current pose, and skinning while the user has a leg posed in IK put weights on the wrong bones."""
    if j not in _POS:
        M = api.rest_matrix(j)
        _POS[j] = (M[12], M[13], M[14])
    return _POS[j]


def _seg(p, a, b):
    ab = [b[k] - a[k] for k in range(3)]; L = sum(x * x for x in ab) or 1e-12
    t = sum((p[k] - a[k]) * ab[k] for k in range(3)) / L
    tc = 0.0 if t < 0 else 1.0 if t > 1 else t
    q = [a[k] + ab[k] * tc for k in range(3)]
    return math.dist(p, q), t


def chain_w(api, p, joints, parent=None, top=0.35):
    """Cloth chain (skirt panel, scarf, cape): find the nearest bone of the chain [j1..jn, end] and
    blend linearly between its two joints (end joint's share goes to the last real joint, ends are
    not skinned). Above j1 (t<0 on the first bone) blend into `parent` over `top` of that bone."""
    P_ = [_jp(api, j) for j in joints]
    best = None
    for k in range(len(P_) - 1):
        d, t = _seg(p, P_[k], P_[k + 1])
        if best is None or d < best[0]:
            best = (d, k, t)
    d, k, t = best
    n_real = len(joints) - 1
    if k == 0 and t < 0 and parent:
        f = ramp(t, -top, 0.0)
        return {parent: 1 - f, joints[0]: f}
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    a, b = joints[k], joints[min(k + 1, n_real - 1)]
    if k + 1 >= n_real:                 # last bone: all on the last real joint
        return {a: 1.0}
    return {a: 1 - t, b: t} if a != b else {a: 1.0}


def bone_w(api, p, bones, blend=0.25):
    """Limb / hand pieces: owner = joint of the nearest bone (a, b); near b the share slides to b
    (50% at the joint), near a to a's parent bone owner given as bones' third item (or none)."""
    best = None
    for a, b, pa in bones:
        d, t = _seg(p, _jp(api, a), _jp(api, b))
        if best is None or d < best[0]:
            best = (d, a, b, pa, t)
    d, a, b, pa, t = best
    w = {a: 1.0}
    if t > 1 - blend and not re.search(r"End_|Finger4_", b):
        f = 0.5 * ramp(t, 1 - blend, 1.0); w = {a: 1 - f, b: f}
    elif t < blend and pa:
        f = 0.5 * ramp(t, blend, 0.0); w = {a: 1 - f, pa: f}
    return w


def write_skin(api, obj, fn, max_inf=4, min_w=0.01):
    """fn(i, (x,y,z), shell) -> {joint: weight}; prune < min_w, keep max_inf, normalise, set all."""
    _POS.clear()
    m = R.Mesh(api, _obj(api, obj))
    shell_of = {}
    for si, sh in enumerate(m.shells):
        for i in sh:
            shell_of[i] = si
    vs, rows = [], []
    for i in range(m.n):
        d = fn(i, m.p(i), shell_of[i])
        if not d:
            continue
        acc = {}
        for j, w in d.items():
            acc[j] = acc.get(j, 0) + w
        keep = sorted([(j, w) for j, w in acc.items() if w >= min_w], key=lambda t: -t[1])[:max_inf]
        s = sum(w for j, w in keep)
        vs.append(m.G[i]); rows.append([(j, w / s) for j, w in keep])
    api.set_skin_weights(vs, rows)
    return len(vs)


def save_weights(api, path):
    """Every skinned vertex's weights to JSON (global vertex id), to put back if the user prefers."""
    out = {}
    for o in api.ls("Object"):
        m = R.Mesh(api, o)
        out[o] = {str(g): api.vertex_weights(g) for g in m.G}
    json.dump(out, open(path, "w")); return path


def load_weights(api, path):
    data = json.load(open(path))
    for o, d in data.items():
        vs = [int(g) for g in d if d[g]]
        api.set_skin_weights(vs, [[tuple(x) for x in d[str(g)]] for g in vs])


def keep_pose(api, fn):
    """Run fn() (a deform / stretch test) and put every control and switch back exactly as the user
    left them. R.fk_rest zeroes controls: without this, testing reset the user's test pose (Hero
    2026-11-04: 4, then 2 controls the user had posed were zeroed)."""
    T = {c: api.transform(c) for c in R.controls(api)}
    SW = {s: {a: api.get_attr(s + "." + a) for a in ("autoSnap", "fkIk") if api.get_attr(s + "." + a) is not None}
          for s in R.SWITCHES if s in api.ls()}
    try:
        return fn()
    finally:
        # order matters: with autoSnap on, setting fkIk SNAPS the IK controls onto the FK pose and the
        # user's IK pose is lost (Hero 2026-11-04: the left IK hand went back to 0). So: autoSnap off,
        # switches back, controls back, then autoSnap back.
        for s, v in SW.items():
            if "autoSnap" in v:
                api.set_attr(s + ".autoSnap", 0.0)
            if "fkIk" in v:
                api.set_attr(s + ".fkIk", v["fkIk"])
        for c, t in T.items():
            api.set_transform(c, t[:3], t[3:6], t[6:9])
        for s, v in SW.items():
            if "autoSnap" in v:
                api.set_attr(s + ".autoSnap", v["autoSnap"])


def smooth_pairs(api, obj, pairs, iters=3, k=0.5, skip_shells=(), skip=None):
    """Smooth the hand-over between two joints at each joint (user 2026-11-04: "smooth a little at
    the joints"). pairs: (j1, j2) or (j1, j2, skip(i, p)). For every vertex carrying j1 and/or j2, only the SPLIT between them is averaged with
    its neighbours on the same piece (the pair's total and every other joint stay as they are), so
    rigid pieces, the crotch seam, the collar rule etc. are not touched. skip_shells: shell indices
    left alone (rigid pieces); skip(i, p) -> True leaves a vertex alone. Returns vertices changed."""
    m = R.Mesh(api, _obj(api, obj))
    shell_of = {}
    for si, sh in enumerate(m.shells):
        for i in sh:
            shell_of[i] = si
    nb = {i: set() for i in range(m.n)}
    for a, b in m.edges:
        nb[a].add(b); nb[b].add(a)
    W = {i: dict(api.vertex_weights(m.G[i])) for i in range(m.n)}
    changed = set()
    for pr in pairs:
        j1, j2 = pr[0], pr[1]
        own_skip = pr[2] if len(pr) > 2 else None        # per-pair: keep a deliberately tight band
        zone = [i for i in range(m.n) if (W[i].get(j1, 0) + W[i].get(j2, 0)) > 1e-4
                and shell_of[i] not in skip_shells and not (skip and skip(i, m.p(i)))
                and not (own_skip and own_skip(i, m.p(i)))]
        zs = set(zone)
        for _ in range(iters):
            new = {}
            for i in zone:
                tot = W[i].get(j1, 0) + W[i].get(j2, 0)
                own = W[i].get(j1, 0) / tot
                ns = [W[n].get(j1, 0) / (W[n].get(j1, 0) + W[n].get(j2, 0)) for n in nb[i] if n in zs]
                if ns:
                    new[i] = (1 - k) * own + k * sum(ns) / len(ns)
            for i, f in new.items():
                tot = W[i].get(j1, 0) + W[i].get(j2, 0)
                a, b = tot * f, tot * (1 - f)
                if abs(a - W[i].get(j1, 0)) > 1e-5:
                    changed.add(i)
                W[i][j1] = a; W[i][j2] = b
    rows, vs = [], []
    for i in changed:
        keep = sorted([(j, w) for j, w in W[i].items() if w >= 0.01], key=lambda t: -t[1])[:4]
        s = sum(w for j, w in keep)
        vs.append(m.G[i]); rows.append([(j, w / s) for j, w in keep])
    if vs:
        api.set_skin_weights(vs, rows)
    return len(vs)
