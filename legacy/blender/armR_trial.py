# Try right-arm edits on frame F of the live action (nothing keyed), render 5 views to eye_<tag>_<view>.png.
#   AR = {"tag": "python using rl(bone, axis_idx, deg)"}; AR_FRAME = 1; exec(open(r".../armR_trial.py").read())
# rl(): rotate a pose bone about its own local axis (0=x length axis of this rig, 1=y, 2=z hinge) around its head.
import os
ROOT = (globals().get("ROOT") or os.environ.get("AI_ANIM_ROOT") or os.getcwd()).replace("\\", "/").rstrip("/")   # project folder: set ROOT = r"<folder>" before exec(), or env AI_ANIM_ROOT, or run from the project folder
if not os.path.exists(ROOT + "/MAP.md"):
    raise RuntimeError("Project folder not found: set ROOT = r'<project folder>' or env AI_ANIM_ROOT")
import math

import bpy
from mathutils import Matrix

_A = bpy.data.objects["Armature"]; _C = bpy.data.objects["CTRL"]; _sc = bpy.context.scene
_F = globals().get("AR_FRAME", 1)


def rl(name, idx, deg, keep_child_world=None):
    pb = _A.pose.bones[name]; mw = _A.matrix_world; M = mw @ pb.matrix
    ax = M.to_3x3().normalized().col[idx].normalized(); h = M.to_translation()
    W = (mw @ _A.pose.bones[keep_child_world].matrix).copy() if keep_child_world else None
    pb.matrix = mw.inverted() @ (Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, ax) @ Matrix.Translation(-h) @ M)
    bpy.context.view_layer.update()
    if W is not None:
        _A.pose.bones[keep_child_world].matrix = mw.inverted() @ Matrix.LocRotScale(
            (mw @ _A.pose.bones[keep_child_world].matrix).translation, W.to_quaternion(), W.to_scale())
        bpy.context.view_layer.update()


_act = _A.animation_data.action
_save = (_sc.render.engine, _sc.camera, _sc.render.filepath, _sc.render.film_transparent, _sc.render.resolution_percentage)
_sc.render.engine = "BLENDER_WORKBENCH"; _sc.render.film_transparent = True; _sc.render.resolution_percentage = 50
_C.hide_render = True
try:
    for _tag, _code in AR.items():  # noqa: F821
        _A.animation_data.action = _act; _sc.frame_set(_F)
        _snap = {pb.name: pb.matrix_basis.copy() for pb in _A.pose.bones}
        _A.animation_data.action = None
        for n, m in _snap.items():
            _A.pose.bones[n].matrix_basis = m
        bpy.context.view_layer.update()
        exec(_code)
        for _v in ("front", "left", "back", "right", "top"):
            _sc.camera = bpy.data.objects["Ref_" + _v]
            _sc.render.filepath = f"{ROOT}/work/blender/look/eye_{_tag}_{_v}.png"
            bpy.ops.render.render(write_still=True)
finally:
    _A.animation_data.action = _act
    (_sc.render.engine, _sc.camera, _sc.render.filepath, _sc.render.film_transparent, _sc.render.resolution_percentage) = _save
    _C.hide_render = False
    _sc.frame_set(1)
print("rendered", list(AR))  # noqa: F821
