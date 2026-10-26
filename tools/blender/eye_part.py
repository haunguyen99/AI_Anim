# Render only one part (weapon mesh by default) for several trial poses, so its outline can be drawn on the reference.
#   TRIALS = {"a": {"wpn_x": 5}}; exec(open(ROOT + r"/tools/blender/eye_part.py").read())
# Poses are channel offsets (solve_keys.PARAMS) on top of the ORIGINAL P0. Writes work/blender/look/part_<tag>_<view>.png
# Then:  python tools/eye_outline.py --trials a,b
import os
ROOT = (globals().get("ROOT") or os.environ.get("AI_ANIM_ROOT") or os.getcwd()).replace("\\", "/").rstrip("/")   # project folder: set ROOT = r"<folder>" before exec(), or env AI_ANIM_ROOT, or run from the project folder
if not os.path.exists(ROOT + "/MAP.md"):
    raise RuntimeError("Project folder not found: set ROOT = r'<project folder>' or env AI_ANIM_ROOT")
import bpy

_arm = bpy.data.objects["Armature"]; _ctrl = bpy.data.objects["CTRL"]
BODY = ["Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M", "Scapula_L", "Scapula_R", "Shoulder_R", "Elbow_R"]
_CB = ["CTRL_weapon", "CTRL_hand_ik_L", "CTRL_elbow_pole_L", "H_Shoulder_L", "H_Elbow_L",
       "CTRL_foot_ik_L", "CTRL_foot_ik_R", "CTRL_knee_pole_L", "CTRL_knee_pole_R"]
_arm.animation_data.action = bpy.data.actions["Idle_Breath"]; _ctrl.animation_data.action = bpy.data.actions["Idle_Breath_CTRL"]
bpy.context.scene.frame_set(1)
P0 = {n: _arm.pose.bones[n].matrix_basis.copy() for n in BODY}
CP0 = {n: _ctrl.pose.bones[n].matrix_basis.copy() for n in _CB}
_arm.animation_data.action = None; _ctrl.animation_data.action = None
bpy.context.view_layer.update()
SIL_W = 0.0; KEYS = []
exec(open(ROOT + r"/tools/blender/solve_keys.py").read())
exec(open(ROOT + r"/tools/blender/grip_set.py").read())
PART = globals().get("PART", "weapon")      # weapon | body | all
_sc = bpy.context.scene
_body = bpy.data.objects["EN_M11_Boss_Gaygor"]; _vk = bpy.data.objects["EN_M11_Boss_Gaygor_VK"]
_save = (_sc.render.engine, _sc.camera, _sc.render.filepath, _sc.render.film_transparent, _sc.render.resolution_percentage,
         _sc.render.use_border, _body.hide_render, _vk.hide_render, _ctrl.hide_render)
_sc.render.engine = "BLENDER_WORKBENCH"; _sc.render.film_transparent = True; _sc.render.resolution_percentage = 50
_sc.render.use_border = False; _ctrl.hide_render = True
_body.hide_render = PART == "weapon"; _vk.hide_render = PART == "body"
try:
    for _tag, _d in TRIALS.items():  # noqa: F821
        _p = np.zeros(len(PARAMS))
        for _k, _v in _d.items():
            if not _k.startswith("_"):
                _p[PARAMS.index(_k)] = _v
        apply(_p)
        if "_post" in _d:          # extra python run after the channels, e.g. set_grip(...) from grip_set.py
            exec(_d["_post"])
        for _v in ("front", "left", "back", "right"):
            _sc.camera = bpy.data.objects["Ref_" + _v]
            _sc.render.filepath = f"{ROOT}/work/blender/look/part_{_tag}_{_v}.png"
            bpy.ops.render.render(write_still=True)
finally:
    (_sc.render.engine, _sc.camera, _sc.render.filepath, _sc.render.film_transparent, _sc.render.resolution_percentage,
     _sc.render.use_border, _body.hide_render, _vk.hide_render, _ctrl.hide_render) = _save
print("rendered", list(TRIALS))  # noqa: F821
