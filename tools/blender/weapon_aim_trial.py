# Try a constant extra rotation of CTRL_weapon (character axes, about its own head) on frame F of the live action,
# render 5 views to eye_<tag>_<view>.png, then restore (nothing is keyed).
#   WA = {"a": (rx, ry, rz)}; WA_FRAME = 1; exec(open(r".../weapon_aim_trial.py").read())
import os
ROOT = (globals().get("ROOT") or os.environ.get("AI_ANIM_ROOT") or os.getcwd()).replace("\\", "/").rstrip("/")   # project folder: set ROOT = r"<folder>" before exec(), or env AI_ANIM_ROOT, or run from the project folder
if not os.path.exists(ROOT + "/MAP.md"):
    raise RuntimeError("Project folder not found: set ROOT = r'<project folder>' or env AI_ANIM_ROOT")
import bpy

exec(open(ROOT + r"/tools/blender/anim_helpers.py").read())
_sc = bpy.context.scene
_sc.frame_set(globals().get("WA_FRAME", 1))
_wb = CTRL.pose.bones["CTRL_weapon"]
_save = (_sc.render.engine, _sc.camera, _sc.render.filepath, _sc.render.film_transparent, _sc.render.resolution_percentage)
_sc.render.engine = "BLENDER_WORKBENCH"; _sc.render.film_transparent = True; _sc.render.resolution_percentage = 50
CTRL.hide_render = True
_act = CTRL.animation_data.action
try:
    for _tag, _r in WA.items():  # noqa: F821
        _sc.frame_set(globals().get("WA_FRAME", 1))
        CTRL.animation_data.action = None
        _m = _wb.matrix_basis.copy()
        CTRL.animation_data.action = _act; _sc.frame_set(globals().get("WA_FRAME", 1))
        _m = _wb.matrix_basis.copy(); CTRL.animation_data.action = None; _wb.matrix_basis = _m
        bpy.context.view_layer.update()
        rotate_char(CTRL, "CTRL_weapon", _r)
        for _v in ("front", "left", "back", "right", "top"):
            _sc.camera = bpy.data.objects["Ref_" + _v]
            _sc.render.filepath = f"{ROOT}/work/blender/look/eye_{_tag}_{_v}.png"
            bpy.ops.render.render(write_still=True)
        CTRL.animation_data.action = _act
finally:
    CTRL.animation_data.action = _act
    (_sc.render.engine, _sc.camera, _sc.render.filepath, _sc.render.film_transparent, _sc.render.resolution_percentage) = _save
    CTRL.hide_render = False
    _sc.frame_set(1)
print("rendered", list(WA))  # noqa: F821
