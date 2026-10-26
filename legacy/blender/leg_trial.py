# One stance trial: original P0 + STANCE (feet) + CH (fullbody_solve channels), rendered through the 5 Ref cameras.
#   TAG = "L1"; STANCE = dict(r=(x, y), l=(x, y), l_yaw=deg, r_yaw=deg); TRIAL_CH = {"Root_M.rz": 15}
#   exec(open(ROOT + r"/legacy/blender/leg_trial.py").read())    -> eye_<TAG>_<view>.png, prints joints + limits
import os
ROOT = (globals().get("ROOT") or os.environ.get("AI_ANIM_ROOT") or os.getcwd()).replace("\\", "/").rstrip("/")   # project folder: set ROOT = r"<folder>" before exec(), or env AI_ANIM_ROOT, or run from the project folder
if not os.path.exists(ROOT + "/MAP.md"):
    raise RuntimeError("Project folder not found: set ROOT = r'<project folder>' or env AI_ANIM_ROOT")
import bpy

FB_NO_RUN = True
exec(open(ROOT + r"/legacy/blender/fullbody_solve.py").read())
setup_base()
_p = np.zeros(len(NAMES))
for _k, _v in TRIAL_CH.items():  # noqa: F821
    _p[NAMES.index(_k)] = _v
apply(_p)
if globals().get("TRIAL_POST"):
    exec(TRIAL_POST)
_sc = bpy.context.scene; _c = bpy.data.objects["CTRL"]
_saved = (_sc.render.engine, _sc.camera, _sc.render.filepath, _sc.render.film_transparent, _sc.render.resolution_percentage)
_sc.render.engine = "BLENDER_WORKBENCH"; _sc.render.film_transparent = True; _sc.render.resolution_percentage = 50
_c.hide_render = True
_body = bpy.data.objects["EN_M11_Boss_Gaygor"]; _vk = bpy.data.objects["EN_M11_Boss_Gaygor_VK"]
_hb, _hv = _body.hide_render, _vk.hide_render
try:
    _body.hide_render = False; _vk.hide_render = False
    for _v in ("front", "left", "back", "right", "top"):
        _sc.camera = bpy.data.objects["Ref_" + _v]
        _sc.render.filepath = f"{ROOT}/work/blender/look/eye_{TAG}_{_v}.png"  # noqa: F821
        bpy.ops.render.render(write_still=True)
    if globals().get("ALSO_WEAPON_ONLY"):      # weapon-only renders for outline checks -> part_<TAG>_<view>.png
        _body.hide_render = True
        for _v in ("front", "left", "back", "right"):
            _sc.camera = bpy.data.objects["Ref_" + _v]
            _sc.render.filepath = f"{ROOT}/work/blender/look/part_{TAG}_{_v}.png"  # noqa: F821
            bpy.ops.render.render(write_still=True)
    _body.hide_render, _vk.hide_render = _hb, _hv
finally:
    _sc.render.engine, _sc.camera, _sc.render.filepath, _sc.render.film_transparent, _sc.render.resolution_percentage = _saved
    _c.hide_render = False
_mw = ARM.matrix_world
_j = {n: [round(-(_mw @ ARM.pose.bones[n].head).x, 2), round(-(_mw @ ARM.pose.bones[n].head).y, 2),
          round((_mw @ ARM.pose.bones[n].head).z, 2)] for n in ("Root_M", "Knee_L", "Knee_R", "Ankle_L", "Ankle_R")}
_bad = {}
for _n in ("Hip_L", "Hip_R", "Knee_L", "Knee_R", "Ankle_L", "Ankle_R"):
    _lim = next((v for k, v in LIMITS["limits"].items() if fnmatch.fnmatch(_n, k)), None); _a = joint_angles(ARM.pose.bones[_n])
    _b = {k: round(_a[k], 1) for k in ("twist", "bendY", "bendZ") if not _lim[k][0] <= _a[k] <= _lim[k][1]}
    if _b:
        _bad[_n] = _b
print(TAG, _j, "limit violations:", _bad)  # noqa: F821
