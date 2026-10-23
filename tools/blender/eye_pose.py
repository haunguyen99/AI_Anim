# Eye-keying helper: apply channel offsets (solve_keys.PARAMS) on top of the ORIGINAL P0 (Idle_Breath f1)
# and render the five reference views (front/left/back/right/top) for a side-by-side check against the ref.
#   TRIALS = {"a": {"grip_roll": -40}, "b": {...}}; exec(open(r"E:/AI Animation/tools/blender/eye_pose.py").read())
# then:  python tools/eye_compare.py --frame 1 --trials a,b
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
exec(open(r"E:/AI Animation/tools/blender/solve_keys.py").read())
exec(open(r"E:/AI Animation/tools/blender/grip_set.py").read())

_sc = bpy.context.scene
_save = (_sc.render.engine, _sc.camera, _sc.render.filepath, _sc.render.film_transparent, _sc.render.resolution_percentage,
         _sc.display.shading.color_type, _sc.render.use_border)
_sc.render.engine = "BLENDER_WORKBENCH"; _sc.display.shading.color_type = "TEXTURE"; _sc.render.film_transparent = True
_sc.render.resolution_percentage = 50; _sc.render.use_border = False
_ctrl.hide_render = True
try:
    for _tag, _d in TRIALS.items():  # noqa: F821
        _p = np.zeros(len(PARAMS))
        for _k, _v in _d.items():
            if not _k.startswith("_"):
                _p[PARAMS.index(_k)] = _v
        apply(_p)
        if "_post" in _d:          # extra python run after the channels, e.g. set_grip(...) from grip_set.py
            exec(_d["_post"])
        for _v in ("front", "left", "back", "right", "top"):
            _sc.camera = bpy.data.objects["Ref_" + _v]
            _sc.render.filepath = f"E:/AI Animation/work/blender/look/eye_{_tag}_{_v}.png"
            bpy.ops.render.render(write_still=True)
finally:
    (_sc.render.engine, _sc.camera, _sc.render.filepath, _sc.render.film_transparent, _sc.render.resolution_percentage,
     _sc.display.shading.color_type, _sc.render.use_border) = _save
    _ctrl.hide_render = False
print("rendered", list(TRIALS))  # noqa: F821
