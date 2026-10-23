# Right arm FK -> IK on the live CTRL rig (same layout as the left arm, see build_ctrl_rig.py), keeping the current motion.
#   exec(open(r"E:/AI Animation/tools/blender/arm_ik_R.py").read())            # build once + key from the FK action
#   ik_R_breath(lift_cm=4, fwd_cm=0, lag=2)                                     # then: hand rises more than the shoulder
# Layout: FOLLOW_scap_R (child of Scapula_R) > CTRL_upper_R > CTRL_fore_R (IK -> CTRL_hand_ik_R, pole CTRL_elbow_pole_R)
#         CTRL_hand_ik_R under FOLLOW_root (keyed); pole under FOLLOW_scap_R (rides the shrug, not keyed)
#         H_Shoulder_R (keyed: upper-arm twist = shield roll), H_Elbow_R, H_Wrist_R -> deform bones copy loc+rot.
import math

import bpy
from mathutils import Matrix, Vector

_A = bpy.data.objects["Armature"]; _C = bpy.data.objects["CTRL"]; _sc = bpy.context.scene
_mw = _A.matrix_world; _cw = _C.matrix_world
_P = _A.pose.bones
_CHAIN = ("Shoulder_R", "Elbow_R", "Wrist_R")


def _wm(name):
    M = _mw @ _P[name].matrix
    return Matrix.Translation(M.to_translation()) @ M.to_3x3().normalized().to_4x4()


def _keyframes(obj, bone):
    return sorted({int(round(k.co[0])) for fc in obj.animation_data.action.fcurves
                   if fc.data_path.startswith(f'pose.bones["{bone}"]') for k in fc.keyframe_points})


def _set_world(pb, M):
    """Pose a CTRL bone to world matrix M (rotation normalised)."""
    pb.matrix = _cw.inverted() @ M
    bpy.context.view_layer.update()


def _key(pb, f):
    pb.keyframe_insert("location", frame=f); pb.keyframe_insert("rotation_quaternion", frame=f)


def ik_R_build():
    if "CTRL_hand_ik_R" in _C.data.bones:
        return False
    _sc.frame_set(1)
    sh, el, wr = (_mw @ _P[n].head for n in _CHAIN)
    ci = _cw.inverted()
    mats = {n: _wm(n) for n in _CHAIN}
    for o in list(bpy.context.selected_objects):
        o.select_set(False)
    bpy.context.view_layer.objects.active = _C; _C.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    E = _C.data.edit_bones

    def bone(name, head, tail, parent=None, connect=False):
        b = E.new(name); b.head, b.tail = ci @ head, ci @ tail; b.use_deform = False
        if parent:
            b.parent = E[parent]; b.use_connect = connect
        return b

    def matbone(name, M, length, parent):
        b = E.new(name); b.head, b.tail = (0, 0, 0), (0, length, 0); b.matrix = ci @ M; b.length = length
        b.use_deform = False; b.parent = E[parent]
        return b

    bone("FOLLOW_scap_R", _mw @ _P["Scapula_R"].head, sh)
    bone("CTRL_upper_R", sh, el, "FOLLOW_scap_R")
    bone("CTRL_fore_R", el, wr, "CTRL_upper_R", connect=True)
    matbone("CTRL_hand_ik_R", mats["Wrist_R"], 0.15, "FOLLOW_root")
    pole = el + (el - (sh + wr) / 2).normalized() * 0.5
    bone("CTRL_elbow_pole_R", pole, pole + Vector((0, 0, 0.12)), "FOLLOW_scap_R")
    matbone("H_Shoulder_R", mats["Shoulder_R"], 0.08, "CTRL_upper_R")
    matbone("H_Elbow_R", mats["Elbow_R"], 0.08, "CTRL_fore_R")
    matbone("H_Wrist_R", mats["Wrist_R"], 0.08, "CTRL_hand_ik_R")
    bpy.ops.object.mode_set(mode="OBJECT")
    for b in ("FOLLOW_scap_R", "H_Shoulder_R", "H_Elbow_R", "H_Wrist_R"):
        _C.data.bones[b].hide = True
    CP = _C.pose.bones
    for n in ("CTRL_hand_ik_R", "CTRL_elbow_pole_R", "H_Shoulder_R", "CTRL_upper_R", "CTRL_fore_R"):
        CP[n].rotation_mode = "QUATERNION"
    c = CP["FOLLOW_scap_R"].constraints.new("CHILD_OF"); c.name = "CTRL_follow"
    c.target, c.subtarget = _A, "Scapula_R"; c.inverse_matrix = (_mw @ _P["Scapula_R"].matrix).inverted()
    bpy.context.view_layer.update()
    # FOLLOW_root may not sit at its rest at f1: put the hand target on the FK wrist before solving the pole angle
    _set_world(CP["CTRL_hand_ik_R"], mats["Wrist_R"])
    ik = CP["CTRL_fore_R"].constraints.new("IK"); ik.name = "CTRL_ik"
    ik.target, ik.subtarget = _C, "CTRL_hand_ik_R"; ik.pole_target, ik.pole_subtarget = _C, "CTRL_elbow_pole_R"
    ik.chain_count = 2
    best = None
    for a in range(-180, 180):
        ik.pole_angle = math.radians(a); bpy.context.view_layer.update()
        e = ((_cw @ CP["CTRL_fore_R"].head) - el).length
        if best is None or e < best[0]:
            best = (e, a)
    ik.pole_angle = math.radians(best[1]); bpy.context.view_layer.update()
    print(f"IK R: pole angle {best[1]}, elbow error {best[0] * 100:.2f} cm")
    return True


def ik_R_key_from_fk(fk_action):
    """Key CTRL_hand_ik_R (wrist keys) and H_Shoulder_R (shoulder keys) so the IK arm reproduces FK_ACTION exactly,
    then switch the deform chain to the helpers."""
    CP = _C.pose.bones; act = _A.animation_data.action
    _A.animation_data.action = bpy.data.actions[fk_action]
    for n in _CHAIN:
        for c in list(_P[n].constraints):
            if c.name.startswith("CTRL_"):
                _P[n].constraints.remove(c)
    fk = {}
    frames = sorted(set(_keyframes(_A, "Wrist_R")) | set(_keyframes(_A, "Shoulder_R")))
    for f in frames:
        _sc.frame_set(f); fk[f] = {n: _wm(n) for n in _CHAIN}
    # clear old keys on the new controls
    cact = _C.animation_data.action
    for fc in list(cact.fcurves):
        if any(f'"{b}"' in fc.data_path for b in ("CTRL_hand_ik_R", "H_Shoulder_R")):
            cact.fcurves.remove(fc)
    for f in _keyframes(_A, "Wrist_R"):
        _sc.frame_set(f); _set_world(CP["CTRL_hand_ik_R"], fk[f]["Wrist_R"]); _key(CP["CTRL_hand_ik_R"], f)
    for f in _keyframes(_A, "Shoulder_R"):
        _sc.frame_set(f); _set_world(CP["H_Shoulder_R"], fk[f]["Shoulder_R"]); _key(CP["H_Shoulder_R"], f)
    for n, h in zip(_CHAIN, ("H_Shoulder_R", "H_Elbow_R", "H_Wrist_R")):
        for typ in ("COPY_LOCATION", "COPY_ROTATION"):
            c = _P[n].constraints.new(typ); c.name = "CTRL_" + typ.lower(); c.target, c.subtarget = _C, h
    _A.animation_data.action = act
    bpy.context.view_layer.update()
    return fk


def ik_R_breath(fk_action="Idle_Front", lift_cm=4.0, fwd_cm=0.0, lag=2, base_cm=0.0, base_fwd_cm=0.0, smooth=0):
    """SMOOTH > 0: cyclic gaussian (sigma SMOOTH frames) on the breath weight, so a quick shrug does not yank the hand."""
    return _ik_R_breath(fk_action, lift_cm, fwd_cm, lag, base_cm, base_fwd_cm, smooth)


def _ik_R_breath(fk_action, lift_cm, fwd_cm, lag, base_cm, base_fwd_cm, smooth):
    """Re-key the hand from FK, then add LIFT_CM up (and FWD_CM toward the character front, -Y) scaled by the breath,
    on top of a constant BASE_CM up / BASE_FWD_CM forward (keeps the elbow bent at the trough - no straight arm):
    w = shoulder height normalised over the loop (0 trough, 1 peak), read LAG frames earlier (hand follows the shrug).
    The hand rises more than the shoulder -> the arm shortens -> the elbow folds toward its pole (back)."""
    _keyframes  # noqa: B018
    for n in _CHAIN:
        for c in _P[n].constraints:
            if c.name.startswith("CTRL_"):
                c.mute = True
    f0, f1 = _sc.frame_start, _sc.frame_end; per = f1 - f0
    z = {}
    for f in range(f0, f1 + 1):
        _sc.frame_set(f); z[f] = (_mw @ _P["Shoulder_R"].head).z
    for n in _CHAIN:
        for c in _P[n].constraints:
            if c.name.startswith("CTRL_"):
                c.mute = False
    ik_R_key_from_fk(fk_action)
    if smooth:
        frames = list(range(f0, f1)); r = int(3 * smooth)
        ks = [math.exp(-0.5 * (d / smooth) ** 2) for d in range(-r, r + 1)]
        zs = {f: sum(k * z[(f + d - f0) % per + f0] for d, k in zip(range(-r, r + 1), ks)) / sum(ks) for f in frames}
        zs[f1] = zs[f0]; z = zs
    lo, hi = min(z.values()), max(z.values())
    CP = _C.pose.bones; hb = CP["CTRL_hand_ik_R"]
    for f in _keyframes(_C, "CTRL_hand_ik_R"):
        src = (f - lag - f0) % per + f0
        w = (z[src] - lo) / (hi - lo)
        _sc.frame_set(f); M = (_cw @ hb.matrix).copy()
        M.translation += Vector((0, -(base_fwd_cm + fwd_cm * w) / 100, (base_cm + lift_cm * w) / 100))
        _set_world(hb, M); _key(hb, f)
    print(f"hand lift {lift_cm} cm, fwd {fwd_cm} cm, lag {lag} F; shoulder rise {(hi - lo) * 100:.1f} cm")


def ik_R_compare(fk_frames):
    """Max position/rotation difference of the IK arm vs the stored FK matrices."""
    worst = [0, 0]
    for f, mats in fk_frames.items():
        _sc.frame_set(f)
        for n, M in mats.items():
            W = _wm(n)
            worst[0] = max(worst[0], (W.to_translation() - M.to_translation()).length * 100)
            worst[1] = max(worst[1], math.degrees(W.to_quaternion().rotation_difference(M.to_quaternion()).angle))
    return worst
