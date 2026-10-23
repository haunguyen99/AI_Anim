# Solve blocking key poses from motion measured on the reference (docs/pipeline_v2.md, step 4).
# Run in the LIVE Blender (MCP):
#   KEYS = [1, 17, ...]; exec(open(r"E:/AI Animation/tools/blender/solve_keys.py").read())
# Needs: P0 on the deform armature at frame 1 (captured into P0 by the caller or here), the CTRL rig,
# and work/idle/analysis/motion.json (tools/ref_timing.py).
# Each key frame: 12 animator channels (offsets from P0, character axes) are solved with damped
# Gauss-Newton so that model points move like the tracked reference regions. Returns SOL {frame: params}.
import json

import numpy as np

exec(open(r"E:/AI Animation/tools/blender/anim_helpers.py").read())

MOTION = json.load(open(r"E:/AI Animation/work/idle/analysis/motion.json"))
PARAMS = ["root_z", "root_y", "lean", "twist", "head_yaw", "head_pitch", "head_roll",
          "scap_L", "scap_R", "armR_x", "armR_z", "elbowR", "wpn_x", "wpn_y", "wpn_z", "wpn_tx", "wpn_ty", "wpn_tz", "neck_side",
          "grip_slide", "grip_roll", "pole_swing", "protract", "root_yaw", "root_pitch"]
# soft prior (1 sigma) per channel, cm or deg
PRIOR = np.array([3, 3, 4, 25, 60, 20, 8, 10, 10, 15, 15, 12, 6, 6, 6, 2, 2, 2, 10, 10, 30, 40, 10, 20, 15], float)
BODY = ["Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M", "Scapula_L", "Scapula_R", "Shoulder_R", "Elbow_R"]


def apply(p):
    """Pose = P0 + channel offsets. Order root -> spine -> chest -> neck -> head -> scapulae -> right arm."""
    restore(ARM, P0)
    restore(CTRL, CP0)
    rz, ry, lean, tw, hy, hp, hr, sl, sr, ax, az, eb, wx, wy, wz, tx, ty, tz, ns, gs, gr, ps, pr, ryaw, rpitch = p
    move_char(ARM, "Root_M", (0, ry / 100, rz / 100))
    if ryaw or rpitch:
        rotate_char(ARM, "Root_M", (rpitch, 0, ryaw))          # stance: hips facing / tilt
    rotate_char(ARM, "Spine1_M", (0.4 * lean, 0, 0.4 * tw))
    rotate_char(ARM, "Chest_M", (0.6 * lean, 0, 0.6 * tw))
    rotate_char(ARM, "Neck_M", (0.4 * hp, ns, 0.4 * hy))   # ns: side bend, + = toward character's right
    rotate_char(ARM, "Head_M", (0.6 * hp, hr, 0.6 * hy))
    rotate_char(ARM, "Scapula_L", (0, sl, pr))     # pr: protraction, rolls both shoulders forward/in
    rotate_char(ARM, "Scapula_R", (0, -sr, -pr))
    rotate_char(ARM, "Shoulder_R", (ax, 0, az))
    rotate_char(ARM, "Elbow_R", (eb, 0, 0))
    rotate_char(CTRL, "CTRL_weapon", (wx, wy, wz))   # the weapon pivots on its round end, on the shoulder
    move_char(CTRL, "CTRL_weapon", (tx / 100, ty / 100, tz / 100))
    grip(gs, gr, ps)


def grip(slide_cm, roll_deg, swing_deg):
    """Left-hand grip on the shaft: slide along it, roll around it (hand target keeps its distance to the axis),
    and swing the elbow pole around the shoulder->hand line."""
    if not (slide_cm or roll_deg or swing_deg):
        return
    cw = CTRL.matrix_world
    W = cw @ CTRL.pose.bones["CTRL_weapon"].matrix
    ax = W.col[1].xyz.normalized(); h = W.translation.copy()
    hb = CTRL.pose.bones["CTRL_hand_ik_L"]
    Hm = cw @ hb.matrix
    T = Matrix.Translation(ax * slide_cm / 100) @ Matrix.Translation(h) @         Matrix.Rotation(math.radians(roll_deg), 4, ax) @ Matrix.Translation(-h)
    hb.matrix = cw.inverted() @ (T @ Hm)
    bpy.context.view_layer.update()
    sh = ARM.matrix_world @ ARM.pose.bones["Shoulder_L"].head
    hand = (cw @ hb.matrix).translation
    a2 = (hand - sh).normalized()
    pb = CTRL.pose.bones["CTRL_elbow_pole_L"]
    Pm = cw @ pb.matrix
    R = Matrix.Translation(sh) @ Matrix.Rotation(math.radians(swing_deg), 4, a2) @ Matrix.Translation(-sh)
    pb.matrix = cw.inverted() @ (R @ Pm)
    bpy.context.view_layer.update()


def to_char(v):
    return np.array([v.dot(CHAR["x"]), v.dot(CHAR["y"]), v.dot(CHAR["z"])])


def points():
    mw = ARM.matrix_world
    P = ARM.pose.bones
    h = (mw @ P["Head_M"].tail + mw @ P["HeadEnd_M"].head) / 2
    return {"head": to_char(h), "weapon": to_char(mw @ P["Weapon"].head), "fist": to_char(mw @ P["Wrist_R"].tail),
            "shR": to_char(mw @ P["Shoulder_R"].head), "shL": to_char(mw @ P["Shoulder_L"].head),
            "chest": to_char(mw @ P["Spine1_M"].head), "pelvis": to_char(mw @ P["Root_M"].head),
            "handL": to_char(mw @ P["Wrist_L"].head),
            "wtail": to_char(mw @ (P["Weapon"].head * 0.15 + P["Weapon"].tail * 0.85))}


def m(view, reg, ch, f):
    return MOTION[view][reg][ch][f - 1]


def targets(f):
    """(point, axis, metres, weight). Front view: image right = character's left -> x = -dx.
    Left view: character faces image left -> forward y = -dx. Back view: image right = character's right."""
    T = []
    def add(pt, ax, val_cm, w):
        T.append((pt, ax, val_cm / 100, w))
    add("head", 0, -m("front", "head", "dx_cm", f), 1.0)
    add("head", 2, (m("front", "head", "dy_cm", f) + m("left", "head", "dy_cm", f)) / 2, 1.0)
    add("head", 1, -m("left", "head", "dx_cm", f), 0.5)
    add("weapon", 0, -m("front", "weapon_head", "dx_cm", f), 1.0)
    add("weapon", 2, (m("front", "weapon_head", "dy_cm", f) + m("left", "weapon_head", "dy_cm", f)) / 2, 1.5)
    add("weapon", 1, -m("left", "weapon_head", "dx_cm", f), 1.5)
    add("wtail", 0, m("back", "weapon_tail", "dx_cm", f), 1.0)
    add("wtail", 2, m("back", "weapon_tail", "dy_cm", f), 1.0)
    add("wtail", 1, -m("left", "weapon_tail", "dx_cm", f), 0.7)
    add("handL", 2, m("front", "hand_L", "dy_cm", f), 0.7)
    add("handL", 1, -m("left", "hand_L", "dx_cm", f), 0.7)
    add("fist", 0, -m("front", "fist_R", "dx_cm", f), 0.8)
    add("fist", 2, m("front", "fist_R", "dy_cm", f), 0.8)
    add("fist", 1, -m("left", "fist_R", "dx_cm", f), 0.6)
    add("shR", 2, m("front", "shoulder_R", "dy_cm", f), 1.2)
    add("shL", 2, m("front", "shoulder_L", "dy_cm", f), 0.8)
    add("chest", 2, (m("front", "chest", "dy_cm", f) + m("left", "chest", "dy_cm", f)) / 2, 1.2)
    add("pelvis", 2, (m("front", "pelvis", "dy_cm", f) + m("back", "pelvis", "dy_cm", f)) / 2, 1.5)
    add("pelvis", 1, -m("left", "pelvis", "dx_cm", f), 0.8)
    return T


# ---- silhouette term: model vertices (+ edge midpoints) projected through the Ref_* ortho cameras vs the
# reference masks (precomputed distance maps + contour samples in work/idle/analysis/silref.npz)
SILREF = np.load(r"E:/AI Animation/work/idle/analysis/silref.npz")
SIL_VIEWS = ["front", "back", "left", "right"]
SIL_W = globals().get("SIL_W", 0.0)      # weight per silhouette sample (0 = tracking only)
PX_CM = 2.06
_MESHES = ["EN_M11_Boss_Gaygor", "EN_M11_Boss_Gaygor_VK"]
_EDGES = []
for _n in _MESHES:
    _me = bpy.data.objects[_n].data
    _e = np.empty(len(_me.edges) * 2, np.int32); _me.edges.foreach_get("vertices", _e)
    _EDGES.append(_e.reshape(-1, 2))
_CAMS = {}
for _v in SIL_VIEWS:
    _c = bpy.data.objects["Ref_" + _v]
    _CAMS[_v] = (np.array(_c.matrix_world.inverted()), 1920 / _c.data.ortho_scale, _c.data.shift_x * 1920, _c.data.shift_y * 1920)


def mesh_points():
    dg = bpy.context.evaluated_depsgraph_get()
    out = []
    for n, E in zip(_MESHES, _EDGES):
        o = bpy.data.objects[n].evaluated_get(dg)
        a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
        a = np.vstack([a, (a[E[:, 0]] + a[E[:, 1]]) / 2])
        M = np.array(o.matrix_world)
        out.append(a @ M[:3, :3].T + M[:3, 3])
    return np.vstack(out)


def sil_residual(f):
    P = mesh_points()
    sc_ = float(SILREF["scale"])
    r = []
    for v in SIL_VIEWS:
        Mi, s, shx, shy = _CAMS[v]
        q = P @ Mi[:3, :3].T + Mi[:3, 3]
        uv = np.c_[960 + q[:, 0] * s - shx, 540 - q[:, 1] * s + shy]
        dt = SILREF[v + "_dt"][f - 1].astype(np.float32); box = SILREF[v + "_box"]
        iu = np.clip(((uv[:, 0] - box[0]) * sc_).astype(int), 0, dt.shape[1] - 1)
        iv = np.clip(((uv[:, 1] - box[1]) * sc_).astype(int), 0, dt.shape[0] - 1)
        out_d = np.minimum(dt[iv, iu], 30.0)[::4]                       # model outside the reference
        ct = SILREF[v + "_ct"][f - 1]
        sub = uv[::2]
        in_d = np.minimum(np.sqrt(((ct[:, None, :] - sub[None, :, :]) ** 2).sum(2)).min(1), 30.0)   # reference not covered
        r.append(out_d); r.append(in_d)
    return np.concatenate(r) / PX_CM


def weapon_out(f):
    """Mean distance (ref px) of the weapon mesh (_VK) vertices outside the reference silhouette, all views."""
    dg = bpy.context.evaluated_depsgraph_get()
    o = bpy.data.objects[_MESHES[1]].evaluated_get(dg)
    a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
    M = np.array(o.matrix_world); P = a @ M[:3, :3].T + M[:3, 3]
    sc_ = float(SILREF["scale"]); tot = []
    for v in SIL_VIEWS:
        Mi, s, shx, shy = _CAMS[v]
        q = P @ Mi[:3, :3].T + Mi[:3, 3]
        uv = np.c_[960 + q[:, 0] * s - shx, 540 - q[:, 1] * s + shy]
        dt = SILREF[v + "_dt"][f - 1].astype(np.float32); box = SILREF[v + "_box"]
        iu = np.clip(((uv[:, 0] - box[0]) * sc_).astype(int), 0, dt.shape[1] - 1)
        iv = np.clip(((uv[:, 1] - box[1]) * sc_).astype(int), 0, dt.shape[0] - 1)
        tot.append(np.minimum(dt[iv, iu], 80.0))
    return float(np.mean(np.concatenate(tot)))


def residual(p, T, base, f=None):
    apply(p)
    pts = points()
    r = [w * ((pts[pt][ax] - base[pt][ax]) - val) * 100 for pt, ax, val, w in T]   # cm
    r += list(p / PRIOR)
    if SIL_W and f is not None:
        r += list(SIL_W * sil_residual(f))
    return np.array(r)


def solve(f, p0=None, iters=6):
    T = targets(f)
    apply(np.zeros(len(PARAMS)))
    base = points()
    p = np.zeros(len(PARAMS)) if p0 is None else np.array(p0, float)
    lam = 1.0
    r = residual(p, T, base, f)
    for _ in range(iters):
        J = np.zeros((len(r), len(p)))
        for i in range(len(p)):
            d = np.zeros(len(p)); d[i] = 0.5
            J[:, i] = (residual(p + d, T, base, f) - r) / 0.5
        A = J.T @ J + lam * np.eye(len(p))
        step = -np.linalg.solve(A, J.T @ r)
        rn = residual(p + step, T, base, f)
        if rn @ rn < r @ r:
            p, r, lam = p + step, rn, lam * 0.5
        else:
            lam *= 4
            residual(p, T, base, f)
    n = len(T)
    err = np.sqrt(np.mean((r[:n] / np.array([t[3] for t in T])) ** 2))
    apply(p)
    sil = sil_residual(f) * PX_CM
    return p, (err, float(np.mean(sil)))


if "P0" not in dir():
    bpy.context.scene.frame_set(1)
    P0 = capture(ARM, BODY)
if "CP0" not in dir():
    CP0 = capture(CTRL, ["CTRL_weapon"])
SOL = {}
prev = None
for _f in KEYS:  # noqa: F821
    _p, _e = solve(_f, prev)
    SOL[_f] = _p
    prev = _p
    print(f"f{_f:3d} track {_e[0]:4.1f}cm sil {_e[1]:4.1f}px  " + " ".join(f"{k}={v:+.1f}" for k, v in zip(PARAMS, _p)))
restore(ARM, P0)
restore(CTRL, CP0)


# ---- head-only silhouette (side and back views, where the head stands out against the background)
_HEAD_IDX = None


def head_vertex_index():
    global _HEAD_IDX
    if _HEAD_IDX is None:
        o = bpy.data.objects[_MESHES[0]]
        gi = {g.index for g in o.vertex_groups if g.name in ("Head_M", "HeadEnd_M")}
        _HEAD_IDX = np.array([v.index for v in o.data.vertices
                              if sum(g.weight for g in v.groups if g.group in gi) > 0.5])
    return _HEAD_IDX


def head_sil(f, views=("left", "right", "back"), roi=None):
    """Mean px: head vertices outside the reference mask + reference contour points inside the head ROI
    that no model vertex covers. ROI (per view, x0,y0,x1,y1) defaults to the projected head bbox + 30 px."""
    dg = bpy.context.evaluated_depsgraph_get()
    o = bpy.data.objects[_MESHES[0]].evaluated_get(dg)
    a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
    M = np.array(o.matrix_world); P = a @ M[:3, :3].T + M[:3, 3]
    H = P[head_vertex_index()]
    sc_ = float(SILREF["scale"]); cost = []; rois = {}
    for v in views:
        Mi, s, shx, shy = _CAMS[v]
        def pj(X):
            q = X @ Mi[:3, :3].T + Mi[:3, 3]
            return np.c_[960 + q[:, 0] * s - shx, 540 - q[:, 1] * s + shy]
        uh, ua = pj(H), pj(P)
        dt = SILREF[v + "_dt"][f - 1].astype(np.float32); box = SILREF[v + "_box"]
        iu = np.clip(((uh[:, 0] - box[0]) * sc_).astype(int), 0, dt.shape[1] - 1)
        iv = np.clip(((uh[:, 1] - box[1]) * sc_).astype(int), 0, dt.shape[0] - 1)
        cost.append(np.minimum(dt[iv, iu], 40.0))
        r = roi[v] if roi else (*(uh.min(0) - 30), *(uh.max(0) + 30))
        rois[v] = r
        ct = SILREF[v + "_ct"][f - 1]
        sel = ct[(ct[:, 0] > r[0]) & (ct[:, 0] < r[2]) & (ct[:, 1] > r[1]) & (ct[:, 1] < r[3])]
        if len(sel):
            cost.append(np.minimum(np.sqrt(((sel[:, None, :] - ua[None, ::2, :]) ** 2).sum(2)).min(1), 40.0))
    return float(np.mean(np.concatenate(cost))), rois


_PART_IDX = {}


def part_out(f, key, groups, views=("front", "back", "left", "right")):
    """Mean distance (ref px) of main-mesh vertices weighted > 0.5 to GROUPS that fall outside the reference mask."""
    o0 = bpy.data.objects[_MESHES[0]]
    if key not in _PART_IDX:
        gi = {g.index for g in o0.vertex_groups if any(g.name.startswith(x) or (x.startswith("*") and g.name.endswith(x[1:])
                                                            and ("Finger" in g.name or "Thumb" in g.name)) for x in groups)}
        _PART_IDX[key] = np.array([v.index for v in o0.data.vertices
                                   if sum(g.weight for g in v.groups if g.group in gi) > 0.5])
    dg = bpy.context.evaluated_depsgraph_get()
    o = o0.evaluated_get(dg)
    a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
    M = np.array(o.matrix_world); P = (a @ M[:3, :3].T + M[:3, 3])[_PART_IDX[key]]
    sc_ = float(SILREF["scale"]); tot = []
    for v in views:
        Mi, s, shx, shy = _CAMS[v]
        q = P @ Mi[:3, :3].T + Mi[:3, 3]
        uv = np.c_[960 + q[:, 0] * s - shx, 540 - q[:, 1] * s + shy]
        dt = SILREF[v + "_dt"][f - 1].astype(np.float32); box = SILREF[v + "_box"]
        iu = np.clip(((uv[:, 0] - box[0]) * sc_).astype(int), 0, dt.shape[1] - 1)
        iv = np.clip(((uv[:, 1] - box[1]) * sc_).astype(int), 0, dt.shape[0] - 1)
        tot.append(np.minimum(dt[iv, iu], 80.0))
    return float(np.mean(np.concatenate(tot)))
