"""Pose helpers that run INSIDE Cascadeur (mcp__cascadeur__run_script), for a Quick-Rig + AutoPosing character.

    import sys; sys.path.insert(0, r"E:\\AI Animation\\tools\\cascadeur")
    import casc_pose as cp
    cp.points(scene, ["Root_M_MainPoint"])                 # {name: (x, y, z)} global, cm
    cp.set_points(scene, {"Root_M_MainPoint": (0, 78, -8)}) # one modify, one AutoPosing update
    cp.move_foot(scene, "r", dx=-15, dz=34)                 # rigid move (+ yaw about Y) of the 5 foot points + knee dir

World: cm, Y up, character faces +Z, character's left = +X. Point names come from the Quick Rig
(Ankle_MainPoint_l, Toes_DirectionPoint_r, Root_M_MainPoint, ...). Edits show up in the NEXT run_script call.
"""
import math

import numpy as np

FOOT = ("Ankle_MainPoint", "Ankle_Self0Point", "Toes_MainPoint", "Toes_DirectionPoint", "Toes_AdditionalPoint",
        "Knee_LimbDir")


def _ids(scene):
    mv = scene.model_viewer()
    return {mv.get_object_name(o): o for o in mv.get_objects()}


def points(scene, names, frame=0):
    mv = scene.model_viewer()
    dv, bv = mv.data_viewer(), mv.behaviour_viewer()
    ids = _ids(scene)
    out = {}
    for n in names:
        tb = bv.get_behaviour_by_name(ids[n], "Transform")
        v = dv.get_data_value(bv.get_behaviour_data(tb, "global_position"), frame)
        out[n] = tuple(float(x) for x in v)
    return out


def set_points(scene, targets, frame=0, name="casc_pose.set_points"):
    """targets: {point name: (x, y, z)}. Returns the modify result (False = callback failed, see the log)."""
    ids = _ids(scene)

    def mod(model, update, updater):
        changed = set()
        for n, p in targets.items():
            node = update.get_object_by_id(ids[n]).root_group().node_deep("Position")
            node.set_value(np.array(p, dtype=np.float32).reshape(3, 1), frame)
            changed.add(node.data_id())
        updater.run_update(changed, frame)

    return scene.modify_update(name, mod)


def ensure_key(scene, frame):
    """Key every layer at `frame` (no-op where a key exists). Values set on a frame with no key do not stick:
    the next evaluation interpolates the neighbouring keys again. Run it in its own run_script call before set_points."""
    lv = scene.layers_viewer()
    ids = [i for i in lv.all_layer_ids() if lv.layer(i) is not None and not lv.layer(i).is_key(frame)]

    def mod(model, update, scene_):
        le = model.layers_editor()
        for i in ids:
            le.set_fixed_interpolation_or_key_if_need(i, frame, True)

    return scene.modify(f"ensure_key {frame}", mod) if ids else True


def joint_world(scene, name, frame=0):
    """(position, 3x3 rotation matrix) of a joint in world space."""
    mv = scene.model_viewer()
    dv, bv = mv.data_viewer(), mv.behaviour_viewer()
    tb = bv.get_behaviour_by_name(_ids(scene)[name], "Transform")
    p = np.array(dv.get_data_value(bv.get_behaviour_data(tb, "global_position"), frame), dtype=float).ravel()
    r = np.array(dv.get_data_value(bv.get_behaviour_data(tb, "global_rotation"), frame).to_rotation_matrix(), dtype=float)
    return p, r


def set_joint_local(scene, name, pos=None, rot=None, frame=0):
    """Key a joint that has no rig controller (e.g. the root-level prop joint `Weapon`) directly:
    pos = local position (cm), rot = 3x3 local rotation matrix. For a child of the origin `root`, local == world."""
    import csc
    oid = _ids(scene)[name]

    def mod(model, update, updater):
        g = update.get_object_by_id(oid).root_group()
        changed = set()
        if pos is not None:
            n = g.node_deep("Position")
            n.set_value(np.array(pos, dtype=np.float32).reshape(3, 1), frame)
            changed.add(n.data_id())
        if rot is not None:
            n = g.node_deep("Rotation")
            n.set_value(csc.math.Rotation.from_rotation_matrix(np.array(rot, dtype=np.float32)), frame)
            changed.add(n.data_id())
        updater.run_update(changed, frame)

    return scene.modify_update(f"set_joint_local {name}", mod)


def align_y_to(u):
    """Smallest rotation matrix taking +Y onto unit vector u."""
    y = np.array([0.0, 1.0, 0.0])
    u = np.asarray(u, dtype=float) / np.linalg.norm(u)
    v = np.cross(y, u)
    c = float(y @ u)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3) if c > 0 else np.diag([1.0, -1.0, -1.0])
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx / (1 + c)


def axis_angle(u, deg):
    u = np.asarray(u, dtype=float) / np.linalg.norm(u)
    a = math.radians(deg)
    K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def two_bone_elbow(shoulder, wrist, l_upper, l_fore, pole):
    """Elbow position for a two-bone chain: bone lengths kept, bent toward the `pole` point.
    If the wrist is out of reach it is pulled in along the shoulder->wrist line (returned too)."""
    S, W, P = (np.asarray(x, dtype=float) for x in (shoulder, wrist, pole))
    d_vec = W - S
    d = min(np.linalg.norm(d_vec), (l_upper + l_fore) * 0.999)
    u = d_vec / np.linalg.norm(d_vec)
    W = S + u * d
    a = (l_upper ** 2 - l_fore ** 2 + d ** 2) / (2 * d)      # distance along u to the elbow's foot point
    h = math.sqrt(max(l_upper ** 2 - a ** 2, 0.0))
    side = (P - S) - ((P - S) @ u) * u
    side /= np.linalg.norm(side)
    return S + u * a + side * h, W


FINGERS = ("ThumbFinger", "IndexFinger", "MiddleFinger", "RingFinger", "PinkyFinger")


def curl_fingers(scene, side, palm_dir, angles, thumb_angles=None, frame=0):
    """Curl finger boxes toward the palm. side 'l'/'r'; palm_dir = world direction the palm faces;
    angles = (deg seg1, seg2, seg3) for the four fingers, thumb_angles for the thumb (default: angles/3).
    Each segment's Local Rotation is post-multiplied by a rotation about cross(finger dir, palm dir)
    expressed in that segment's frame, so the tip moves toward the palm (no forced hand orientation)."""
    import csc
    S = side.upper()
    ids = _ids(scene)
    palm = np.asarray(palm_dir, dtype=float) / np.linalg.norm(palm_dir)
    plan = []
    for f in FINGERS:
        ang = (thumb_angles or tuple(a / 3 for a in angles)) if f == "ThumbFinger" else angles
        for i in (1, 2, 3):
            j = f"{f}{i}_{S}"
            p, R = joint_world(scene, j, frame)
            nxt = f"{f}{i + 1}_{S}" if i < 3 else None
            d = (joint_world(scene, nxt, frame)[0] - p) if nxt else R[:, 0] * (-1 if side == "l" else 1)
            if nxt is None:  # last segment: reuse the previous segment's direction
                d = p - joint_world(scene, f"{f}{i - 1}_{S}", frame)[0]
            d /= np.linalg.norm(d)
            ax = np.cross(d, palm)
            if np.linalg.norm(ax) < 1e-6:
                continue
            plan.append((f"{f}{i}_Box_{side}", R.T @ (ax / np.linalg.norm(ax)), ang[i - 1]))

    def mod(model, update, updater):
        changed = set()
        for box, ax_local, deg in plan:
            node = update.get_object_by_id(ids[box]).root_group().node_deep("Local Rotation")
            Rl = np.array(node.value(frame).to_rotation_matrix(), dtype=float)
            new = Rl @ axis_angle(ax_local, deg)
            node.set_value(csc.math.Rotation.from_rotation_matrix(new.astype(np.float32)), frame)
            changed.add(node.data_id())
        updater.run_update(changed, frame)

    return scene.modify_update(f"curl_fingers_{side}", mod)


def foot_names(side):
    return [f"{p}_{side}" for p in FOOT]


def move_foot(scene, side, dx=0.0, dy=0.0, dz=0.0, yaw=0.0, pivot=None, frame=0, extra=None):
    """Rigid move of one foot: yaw (deg, about +Y; + turns the toes toward +X) around `pivot`
    (default: Ankle_MainPoint), then translate. `extra` = more targets set in the same update (pelvis...)."""
    names = foot_names(side)
    cur = points(scene, names, frame)
    pv = np.array(pivot if pivot is not None else cur[f"Ankle_MainPoint_{side}"], dtype=float)
    a = math.radians(yaw)
    rot = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    t = np.array([dx, dy, dz], dtype=float)
    tg = {n: tuple(rot @ (np.array(p) - pv) + pv + t) for n, p in cur.items()}
    if extra:
        tg.update(extra)
    return set_points(scene, tg, frame, f"move_foot_{side}")
