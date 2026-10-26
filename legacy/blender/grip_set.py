# Explicit left-hand grip on the weapon shaft (shaft axis measured from the weapon mesh, not the Weapon bone).
# exec after solve_keys.py / eye_part.py (needs ARM, CTRL, CHAR, to_char, np).
#   set_grip(t, up_out, dist, palm_axis, inward_tilt)  -> places CTRL_hand_ik_L
#   set_pole(char_point)                               -> places CTRL_elbow_pole_L at a point in character space (m)
import bpy
from mathutils import Matrix, Vector


def shaft():
    dg = bpy.context.evaluated_depsgraph_get()
    o = bpy.data.objects["EN_M11_Boss_Gaygor_VK"].evaluated_get(dg)
    a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
    M = np.array(o.matrix_world); V = a @ M[:3, :3].T + M[:3, 3]
    c = V.mean(0); _, _, Vt = np.linalg.svd(V - c); ax = Vt[0]
    if ax @ np.array([0, 1, 1]) < 0:
        ax = -ax
    return c, ax


def char_vec(v):
    return CHAR["x"] * v[0] + CHAR["y"] * v[1] + CHAR["z"] * v[2]


def set_grip(t=-0.62, up_out=(-0.35, 0.0, 1.0), dist=0.36, palm_axis="-z", inward_tilt=0.0):
    """Wrist on the shaft at axis parameter t (m from the mesh centre, negative = toward the round end), on the side
    given by UP_OUT (character-space direction, projected perpendicular to the shaft), DIST from the axis.
    The hand (wrist->knuckles, bone y) lies tangent to the shaft pointing to the character's right (inward), tilted
    toward the round end by INWARD_TILT degrees; PALM_AXIS is the wrist bone axis that faces the shaft."""
    c, ax = shaft()
    axv = Vector(ax.tolist())
    r = char_vec(up_out); r = (r - axv * r.dot(axv)).normalized()
    pos = Vector(c.tolist()) + axv * t + r * dist
    d = axv.cross(r).normalized()
    if d.dot(CHAR["x"]) < 0:
        d = -d
    if inward_tilt:
        d = (Matrix.Rotation(math.radians(inward_tilt), 3, r) @ d).normalized()
    n = -r                                           # palm normal, toward the shaft
    y = d; sign = -1 if palm_axis.startswith("-") else 1; k = palm_axis[-1]
    if k == "z":
        z = n * sign; x = y.cross(z).normalized(); z = x.cross(y).normalized()
    else:
        x = n * sign; z = x.cross(y).normalized(); x = y.cross(z).normalized()
    R = Matrix((x, y, z)).transposed().to_4x4()
    W = Matrix.Translation(pos) @ R
    hb = CTRL.pose.bones["CTRL_hand_ik_L"]
    hb.matrix = CTRL.matrix_world.inverted() @ W
    bpy.context.view_layer.update()


def set_pole(char_point):
    pb = CTRL.pose.bones["CTRL_elbow_pole_L"]
    M = CTRL.matrix_world @ pb.matrix
    w = char_vec(char_point)
    pb.matrix = CTRL.matrix_world.inverted() @ (Matrix.Translation(w - M.translation) @ M)
    bpy.context.view_layer.update()


def grip_report():
    c, ax = shaft()
    mw = ARM.matrix_world; P = ARM.pose.bones
    out = {}
    for n, pt in (("wrist", np.array(mw @ P["Wrist_L"].head)), ("knuckle", np.array(mw @ P["Wrist_L"].tail)),
                  ("elbow", np.array(mw @ P["Elbow_L"].head))):
        d = pt - c; tt = d @ ax; out[n] = (round(float(tt), 3), round(float(np.linalg.norm(d - tt * ax)), 3),
                                          to_char(pt).round(2).tolist())
    return out


_FINGER_Q0 = {}


def set_fingers(k=0.35, thumb_k=None, side="L"):
    """Scale the P0 finger curl of one hand: 0 = straight (rest), 1 = P0 fist."""
    from mathutils import Quaternion
    names = [b.name for b in ARM.pose.bones if b.name.endswith("_" + side) and "Finger" in b.name]
    for n in names:
        pb = ARM.pose.bones[n]
        pb.rotation_mode = "QUATERNION"
        if n not in _FINGER_Q0:
            _FINGER_Q0[n] = pb.rotation_quaternion.copy()
        kk = thumb_k if (thumb_k is not None and n.startswith("Thumb")) else k
        pb.rotation_quaternion = Quaternion().slerp(_FINGER_Q0[n], kk)
    bpy.context.view_layer.update()


# ---- anatomical left arm: no twist at the elbow, hinge bend only, wrist without twist -----------------------------
# Bones of this FBX rig run along local -X; Y is the hinge axis (fingers curl about Y).
def _rest_local(child):
    D = ARM.data.bones
    return (D[D[child].parent.name].matrix_local.inverted() @ D[child].matrix_local).to_3x3()


def _set_world_rot(ctrl_bone, R3, pos=None):
    pb = CTRL.pose.bones[ctrl_bone]
    M = CTRL.matrix_world @ pb.matrix
    W = R3.to_4x4(); W.translation = M.translation if pos is None else pos
    pb.matrix = CTRL.matrix_world.inverted() @ W
    bpy.context.view_layer.update()


def arm_twist_report(side="L"):
    D = ARM.data.bones; P = ARM.pose.bones; out = {}
    for n in (f"Shoulder_{side}", f"Elbow_{side}", f"Wrist_{side}"):
        pb = P[n]; par = pb.parent
        q = (D[par.name].matrix_local.inverted() @ D[n].matrix_local).to_quaternion().inverted() @ \
            (par.matrix.inverted() @ pb.matrix).to_quaternion()
        p = Vector((q.x, q.y, q.z)).project(Vector((1, 0, 0)))
        from mathutils import Quaternion
        t = Quaternion((q.w, p.x, p.y, p.z)); t.normalize()
        tw = math.degrees(2 * math.atan2(t.x, t.w)); tw = (tw + 180) % 360 - 180
        e = (q @ t.inverted()).to_euler("YZX")
        out[n] = (round(tw, 1), round(math.degrees(e.y), 1), round(math.degrees(e.z), 1))
    return out


def fk_left_arm(flex=30.0, dev=0.0, hand_dir=None, elbow_pick=0, fore_twist=0.0, wrist_twist=0.0, dry=False):
    """Re-orient the IK-placed left arm anatomically (positions unchanged):
    upper-arm roll chosen so the forearm lies in the elbow hinge plane (closest to zero twist, ELBOW_PICK flips),
    elbow = pure hinge, wrist = forearm frame with no twist, bent FLEX about Y and DEV about Z.
    If HAND_DIR (world Vector) is given, flex/dev are searched (|flex|<=75, |dev|<=35) to aim the hand along it."""
    mw = ARM.matrix_world; P = ARM.pose.bones
    S = mw @ P["Shoulder_L"].head; E = mw @ P["Elbow_L"].head; Wp = mw @ P["Wrist_L"].head
    Rs0 = (mw @ P["Shoulder_L"].matrix).to_3x3().normalized()
    Rl_e = _rest_local("Elbow_L"); Rl_w = _rest_local("Wrist_L")
    df = (Wp - E).normalized()
    cands = []
    for i in range(720):
        phi = math.radians(i * 0.5)
        Rs = Rs0 @ Matrix.Rotation(phi, 3, "X")
        ye = Rs @ Rl_e @ Vector((0, 0, 1))          # elbow hinge = local Z (joint_limits.json)
        cands.append((abs(df.dot(ye)), i * 0.5, Rs))
    # the two roots of the hinge condition
    cands.sort(key=lambda c: c[0])
    roots = [cands[0]]
    for c in cands[1:]:
        if abs(((c[1] - roots[0][1]) + 180) % 360 - 180) > 30:
            roots.append(c); break
    # twist of each root relative to the REST upper arm: prefer the smaller one (or the other with ELBOW_PICK)
    Rpar = (mw @ P["Scapula_L"].matrix).to_3x3().normalized(); Rl_s = _rest_local("Shoulder_L")

    def rest_twist(Rs_):
        q = (Rl_s.inverted() @ Rpar.inverted() @ Rs_).to_quaternion()
        from mathutils import Quaternion
        pp = Vector((q.x, q.y, q.z)).project(Vector((1, 0, 0)))
        t = Quaternion((q.w, pp.x, pp.y, pp.z)); t.normalize()
        return abs(((math.degrees(2 * math.atan2(t.x, t.w))) + 180) % 360 - 180)
    roots.sort(key=lambda c: rest_twist(c[2]))
    _, phi_deg, Rs = roots[min(elbow_pick, len(roots) - 1)]
    # elbow frame: pure hinge about the shared Y
    ze = (Rs @ Rl_e @ Vector((0, 0, 1))).normalized()     # hinge axis shared with the upper arm
    xe = (-df - ze * (-df).dot(ze)).normalized()
    ye = ze.cross(xe).normalized()
    Re = Matrix((xe, ye, ze)).transposed() @ Matrix.Rotation(math.radians(fore_twist), 3, "X")   # pronation/supination share
    def wrist_R(fl, dv):
        return Re @ Rl_w @ Matrix.Rotation(math.radians(wrist_twist), 3, "X") @             Matrix.Rotation(math.radians(fl), 3, "Y") @ Matrix.Rotation(math.radians(dv), 3, "Z")
    if hand_dir is not None:
        hd = hand_dir.normalized(); best = None
        for fl in range(-75, 76, 3):
            for dv in range(-35, 36, 5):
                h = -(wrist_R(fl, dv) @ Vector((1, 0, 0)))
                s = h.dot(hd)
                if best is None or s > best[0]:
                    best = (s, fl, dv)
        _, flex, dev = best
    if dry:                         # only report the wrist rotation this setting would give
        return wrist_R(flex, dev)
    _set_world_rot("H_Shoulder_L", Rs)
    _set_world_rot("H_Elbow_L", Re)
    _set_world_rot("CTRL_hand_ik_L", wrist_R(flex, dev))
    return {"upper_roll": phi_deg, "flex": flex, "dev": dev}


def wrap_dir(inward=1.0, wrap=0.35, toward="x"):
    """World direction for the hand to lie over the shaft from the current wrist: tangent toward the character's
    right (inward) plus a little toward the shaft axis (WRAP), so the fingers drape over the top."""
    c, ax = shaft(); axv = Vector(ax.tolist())
    w = ARM.matrix_world @ ARM.pose.bones["Wrist_L"].head
    d0 = w - Vector(c.tolist()); r = (d0 - axv * d0.dot(axv)).normalized()
    t = axv.cross(r).normalized()
    if t.dot(CHAR[toward]) < 0:          # wrap around the shaft toward this character axis (x = inward, y = forward)
        t = -t
    return (t * inward - r * wrap).normalized(), -r


def fit_hand(fore_twist=40.0, wrap=0.35, palm_w=0.6, toward="x", twist_range=range(-50, 51, 10)):
    """Search wrist flex/deviation/twist (inside the joint limits) so the hand lies along wrap_dir() with the palm (+Z)
    facing the shaft axis; the forearm keeps FORE_TWIST of the supination."""
    fk_left_arm(flex=0, fore_twist=fore_twist)               # arm chain (upper roll, hinge, forearm twist)
    Re = (CTRL.matrix_world @ CTRL.pose.bones["H_Elbow_L"].matrix).to_3x3().normalized()
    Rl_w = _rest_local("Wrist_L")
    hd, to_axis = wrap_dir(wrap=wrap, toward=toward)
    X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    best = None
    for wt in twist_range:
        Rt = Re @ Rl_w @ Matrix.Rotation(math.radians(wt), 3, "X")
        for fl in range(-20, 76, 5):
            Rf = Rt @ Matrix.Rotation(math.radians(fl), 3, "Y")
            for dv in range(-45, 46, 5):
                R = Rf @ Matrix.Rotation(math.radians(dv), 3, "Z")
                s_ = (-(R @ X)).dot(hd) + palm_w * (R @ Z).dot(to_axis) - 0.002 * (abs(wt) + abs(dv))
                if best is None or s_ > best[0]:
                    best = (s_, fl, dv, wt, R)
    _, fl, dv, wt, R = best
    _set_world_rot("CTRL_hand_ik_L", R)
    return {"flex": fl, "dev": dv, "wrist_twist": wt, "score": round(best[0], 3)}


def hand_report():
    """Hand along -X of Wrist_L (this rig), palm = +Z. Returns: wrist distance to the shaft axis, the hand-centre
    distance (8 cm along the hand), and how much the palm faces the axis (1 = straight at it)."""
    c, ax = shaft(); axv = Vector(ax.tolist()); C = Vector(c.tolist())
    M = ARM.matrix_world @ ARM.pose.bones["Wrist_L"].matrix
    R = M.to_3x3().normalized(); w = M.translation
    hdir = -(R @ Vector((1, 0, 0))); palm = R @ Vector((0, 0, 1))
    def dist(p):
        d = p - C; return (d - axv * d.dot(axv)).length
    hc = w + hdir * 0.08
    d = hc - C; r = (d - axv * d.dot(axv)).normalized()
    return {"wrist_r": round(dist(w), 3), "hand_r": round(dist(hc), 3), "palm_to_axis": round(-palm.dot(r), 2),
            "hand_dir_char": to_char(hdir).round(2).tolist()}


def set_wrist_char(p_char, dist=0.33):
    """Put the hand target (wrist) at the point of the shaft surface (DIST from the axis) nearest to P_CHAR
    (character space, metres; measured on the reference). Orientation is set later by fit_hand()."""
    c, ax = shaft(); axv = Vector(ax.tolist()); C = Vector(c.tolist())
    p = char_vec(p_char); d = p - C; t = d.dot(axv); r = (d - axv * t)
    pos = C + axv * t + r.normalized() * dist
    hb = CTRL.pose.bones["CTRL_hand_ik_L"]
    M = CTRL.matrix_world @ hb.matrix
    hb.matrix = CTRL.matrix_world.inverted() @ (Matrix.Translation(pos - M.translation) @ M)
    bpy.context.view_layer.update()
    return {"t": round(t, 3), "r_measured": round(r.length, 3)}


def fit_hand_full(wrap=0.45, palm_w=0.6, toward="y", fore_range=range(-60, 61, 10)):
    """fit_hand() over forearm supination too; penalises twist so the most natural reachable grip wins."""
    best = None
    for ft in fore_range:
        r = fit_hand(ft, wrap=wrap, palm_w=palm_w, toward=toward)
        jl = arm_twist_report()["Wrist_L"]
        over = max(0, abs(jl[0]) - 50) + max(0, abs(jl[1]) - 75) + max(0, abs(jl[2]) - 45)
        s = r["score"] - 0.003 * abs(ft) - 0.02 * over
        if best is None or s > best[0]:
            best = (s, ft)
    r = fit_hand(best[1], wrap=wrap, palm_w=palm_w, toward=toward)
    r["fore_twist"] = best[1]
    return r


def set_stance(r_move=(0, 0), l_move=(0, 0), r_yaw=0.0, l_yaw=0.0, root_yaw=0.0, root_pitch=0.0, root_roll=0.0):
    """Feet (IK controls, character metres / degrees about up, + = toes toward the character's left) then hips."""
    move_char(CTRL, "CTRL_foot_ik_R", (r_move[0], r_move[1], 0))
    move_char(CTRL, "CTRL_foot_ik_L", (l_move[0], l_move[1], 0))
    for s, mv in (("R", r_move), ("L", l_move)):          # knee poles follow their foot
        move_char(CTRL, f"CTRL_knee_pole_{s}", (mv[0], mv[1], 0))
    if r_yaw:
        rotate_char(CTRL, "CTRL_foot_ik_R", (0, 0, r_yaw))
    if l_yaw:
        rotate_char(CTRL, "CTRL_foot_ik_L", (0, 0, l_yaw))
    if root_yaw or root_pitch or root_roll:
        rotate_char(ARM, "Root_M", (root_pitch, root_roll, root_yaw))


def stance_report():
    mw = ARM.matrix_world; P = ARM.pose.bones; out = {}
    for n in ("Ankle_L", "Ankle_R", "ToesEnd_L", "ToesEnd_R"):
        out[n] = to_char(mw @ P[n].head).round(2).tolist()
    return out


def make_fist(side="R", curl=(80, 95, 70), thumb=(20, 35, 35), sign=1.0):
    """Close a hand: finger joints 1/2/3 curl about local Y (this rig), thumb less. SIGN flips the curl direction."""
    from mathutils import Quaternion
    for pb in ARM.pose.bones:
        if not (pb.name.endswith("_" + side) and "Finger" in pb.name):
            continue
        k = int(pb.name[-3]) - 1                       # ...Finger1_R -> 0
        a = (thumb if pb.name.startswith("Thumb") else curl)[k]
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = Quaternion((0, 1, 0), math.radians(a * sign))
    bpy.context.view_layer.update()


def elbow_out(side="R", deg=20.0, back=0.0):
    """Swing the elbow about the shoulder->wrist line (hand stays where it is), then restore the hand's world rotation.
    + = elbow away from the body (checked against the character's side)."""
    mw = ARM.matrix_world; P = ARM.pose.bones
    sh = mw @ P[f"Shoulder_{side}"].head; wr = mw @ P[f"Wrist_{side}"].head; el = mw @ P[f"Elbow_{side}"].head
    Wm = (mw @ P[f"Wrist_{side}"].matrix).copy()
    ax = (wr - sh).normalized()
    out = (CHAR["x"] if side == "R" else -CHAR["x"]) - CHAR["y"] * back     # BACK > 0: also toward the back
    # choose the rotation sense that moves the elbow outward
    for s in (1, -1):
        R = Matrix.Rotation(math.radians(deg * s), 4, ax)
        e2 = sh + (R.to_3x3() @ (el - sh))
        if (e2 - el).dot(out) > 0:
            break
    pb = P[f"Shoulder_{side}"]; M = mw @ pb.matrix
    pb.matrix = mw.inverted() @ (Matrix.Translation(sh) @ R @ Matrix.Translation(-sh) @ M)
    bpy.context.view_layer.update()
    P[f"Wrist_{side}"].matrix = mw.inverted() @ Matrix.LocRotScale((mw @ P[f"Wrist_{side}"].matrix).translation, Wm.to_quaternion(), Wm.to_scale())
    bpy.context.view_layer.update()


def scapula_keep_weapon(deg_xyz):
    """Rotate Scapula_L (character axes) while the weapon stays where it is in the world (it is parented to the scapula)."""
    wb = CTRL.pose.bones["CTRL_weapon"]; cw = CTRL.matrix_world
    W = (cw @ wb.matrix).copy()
    rotate_char(ARM, "Scapula_L", deg_xyz)
    wb.matrix = cw.inverted() @ W
    bpy.context.view_layer.update()
