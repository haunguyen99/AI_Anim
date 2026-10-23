# Retarget a dumped animation (dump_joints.py JSON: world position + rotation per bone per frame) onto the scene rig by
# copying WORLD rotations (both rigs share the bone axis convention; their rest poses may differ) and the root position.
#   SRC = r".../orig_joints.json"; ACT = "ORIG_retarget"; exec(open(r".../retarget_world.py").read())
# Creates action ACT on "Armature" (keys every frame, all bones). CTRL_* constraints must be muted when it is used.
import json

import bpy
from mathutils import Matrix, Quaternion, Vector

_src = json.load(open(SRC))  # noqa: F821
_arm = bpy.data.objects["Armature"]
_mw = _arm.matrix_world
_sc = _mw.to_scale()


def _depth(b):
    d = 0
    while b.parent:
        b = b.parent; d += 1
    return d


_order = sorted([pb for pb in _arm.pose.bones if pb.name in _src["bones"]], key=lambda pb: _depth(pb.bone))
_act = bpy.data.actions.get(ACT) or bpy.data.actions.new(ACT)  # noqa: F821
_act.use_fake_user = True
for fc in list(_act.fcurves):
    _act.fcurves.remove(fc)
_prev = _arm.animation_data.action
_arm.animation_data.action = _act
for _i, _f in enumerate(_src["frames"]):
    for pb in _order:
        x, y, z, qw, qx, qy, qz = _src["bones"][pb.name][_i]
        W = Matrix.LocRotScale(Vector((x, y, z)), Quaternion((qw, qx, qy, qz)), _sc)
        pb.matrix = _mw.inverted() @ W
        bpy.context.view_layer.update()
    for pb in _order:
        pb.rotation_mode = "QUATERNION"
        pb.keyframe_insert("rotation_quaternion", frame=_f, group=pb.name)
        pb.keyframe_insert("location", frame=_f, group=pb.name)
_arm.animation_data.action = _prev
print("retargeted", len(_src["frames"]), "frames,", len(_order), "bones ->", ACT)  # noqa: F821
