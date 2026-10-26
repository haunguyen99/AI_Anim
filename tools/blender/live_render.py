# Run inside the live Blender (MCP execute_blender_code):
#   FRAMES = [1, 17]; VIEWS = ["front", "left"]; exec(open(ROOT + r"/tools/blender/live_render.py").read())
# Renders the scene through Ref_<view> cameras (Workbench, transparent) to work/blender/look/r_<view>_<frame>.png,
# restoring the user's render settings, camera and frame afterwards.
import os
ROOT = (globals().get("ROOT") or os.environ.get("AI_ANIM_ROOT") or os.getcwd()).replace("\\", "/").rstrip("/")   # project folder: set ROOT = r"<folder>" before exec(), or env AI_ANIM_ROOT, or run from the project folder
if not os.path.exists(ROOT + "/MAP.md"):
    raise RuntimeError("Project folder not found: set ROOT = r'<project folder>' or env AI_ANIM_ROOT")
import os

import bpy

_sc = bpy.context.scene
_out = ROOT + r"/work/blender/look"
os.makedirs(_out, exist_ok=True)
_saved = dict(engine=_sc.render.engine, cam=_sc.camera, frame=_sc.frame_current, path=_sc.render.filepath,
              transp=_sc.render.film_transparent, pct=_sc.render.resolution_percentage,
              fmt=_sc.render.image_settings.file_format, mode=_sc.render.image_settings.color_mode,
              light=_sc.display.shading.light, ctype=_sc.display.shading.color_type)
_hidden = [o for o in bpy.data.objects if o.name == "CTRL" and not o.hide_render]
for o in _hidden:
    o.hide_render = True
try:
    _sc.render.engine = "BLENDER_WORKBENCH"
    _sc.display.shading.light = "STUDIO"
    _sc.display.shading.color_type = "TEXTURE"
    _sc.render.film_transparent = True
    _sc.render.resolution_percentage = 50
    _sc.render.image_settings.file_format = "PNG"
    _sc.render.image_settings.color_mode = "RGBA"
    for _f in FRAMES:  # noqa: F821
        _sc.frame_set(_f)
        for _v in VIEWS:  # noqa: F821
            _sc.camera = bpy.data.objects[f"Ref_{_v}"]
            _sc.render.filepath = os.path.join(_out, f"r_{_v}_{_f:04d}.png")
            bpy.ops.render.render(write_still=True)
finally:
    _sc.render.engine = _saved["engine"]; _sc.camera = _saved["cam"]; _sc.frame_set(_saved["frame"])
    _sc.render.filepath = _saved["path"]; _sc.render.film_transparent = _saved["transp"]
    _sc.render.resolution_percentage = _saved["pct"]; _sc.render.image_settings.file_format = _saved["fmt"]
    _sc.render.image_settings.color_mode = _saved["mode"]
    _sc.display.shading.light = _saved["light"]; _sc.display.shading.color_type = _saved["ctype"]
    for o in _hidden:
        o.hide_render = False
print("rendered", len(FRAMES) * len(VIEWS), "images")  # noqa: F821
