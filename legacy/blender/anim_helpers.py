# Helpers for keying in the LIVE Blender scene (exec'd through MCP).
#   exec(open(ROOT + r"/legacy/blender/anim_helpers.py").read())
# Character axes (world): right = -X, forward = -Y, up = +Z (the Boss faces -Y).
import math

import bpy
from mathutils import Matrix, Quaternion, Vector

ARM = bpy.data.objects["Armature"]
CTRL = bpy.data.objects.get("CTRL")
CHAR = {"x": Vector((-1, 0, 0)), "y": Vector((0, -1, 0)), "z": Vector((0, 0, 1))}


def ensure_action(obj, name):
    obj.animation_data_create()
    act = bpy.data.actions.get(name) or bpy.data.actions.new(name)
    act.use_fake_user = True
    obj.animation_data.action = act
    return act


def key_bones(obj, names, frame, loc=True):
    for n in names:
        pb = obj.pose.bones[n]
        pb.rotation_mode = "QUATERNION"
        pb.keyframe_insert("rotation_quaternion", frame=frame, group=n)
        if loc:
            pb.keyframe_insert("location", frame=frame, group=n)


def rotate_char(obj, name, deg_xyz):
    """Rotate a pose bone about its own head by degrees around the CHARACTER axes (x right, y fwd, z up)."""
    pb = obj.pose.bones[name]
    mw = obj.matrix_world
    M = mw @ pb.matrix
    q = Quaternion()
    for ax, d in zip("xyz", deg_xyz):
        if d:
            q = Quaternion(CHAR[ax], math.radians(d)) @ q
    R = q.to_matrix().to_4x4()
    head = M.to_translation()
    Mn = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ M
    pb.matrix = mw.inverted() @ Mn
    bpy.context.view_layer.update()


def move_char(obj, name, metres_xyz):
    pb = obj.pose.bones[name]
    mw = obj.matrix_world
    d = CHAR["x"] * metres_xyz[0] + CHAR["y"] * metres_xyz[1] + CHAR["z"] * metres_xyz[2]
    M = mw @ pb.matrix
    pb.matrix = mw.inverted() @ (Matrix.Translation(d) @ M)
    bpy.context.view_layer.update()


def capture(obj, names):
    return {n: obj.pose.bones[n].matrix_basis.copy() for n in names}


def restore(obj, snap):
    for n, m in snap.items():
        obj.pose.bones[n].matrix_basis = m
    bpy.context.view_layer.update()


def set_interp(obj, kind="BEZIER", handles="AUTO_CLAMPED"):
    act = obj.animation_data.action
    for fc in getattr(act, "fcurves", []):
        for kp in fc.keyframe_points:
            kp.interpolation = kind
            kp.handle_left_type = kp.handle_right_type = handles
        fc.update()
