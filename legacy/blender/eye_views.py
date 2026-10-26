"""Render the current pose through every Ref_* camera (live Blender), for REF|ANIM eye checks with tools/eye_side.py.

  OUT = ROOT + r"/work/attack/look_v4"; TAG = "f13_a"; exec(open(ROOT + r"/legacy/blender/eye_views.py").read())
Writes OUT/<TAG>_<view>.png (RGBA, workbench studio solid, transparent film, 1920x1080) for front/back/left/right/top.
Render settings and the scene camera are restored afterwards.
"""
import os
ROOT = (globals().get("ROOT") or os.environ.get("AI_ANIM_ROOT") or os.getcwd()).replace("\\", "/").rstrip("/")   # project folder: set ROOT = r"<folder>" before exec(), or env AI_ANIM_ROOT, or run from the project folder
if not os.path.exists(ROOT + "/MAP.md"):
    raise RuntimeError("Project folder not found: set ROOT = r'<project folder>' or env AI_ANIM_ROOT")

import bpy

_sc = bpy.context.scene
_out = globals().get("OUT", ROOT + r"/work/attack/look_v4")
_tag = globals().get("TAG", "pose")
_views = globals().get("VIEWS", ["front", "back", "left", "right", "top"])
os.makedirs(_out, exist_ok=True)
_r, _d = _sc.render, _sc.display.shading
_save = (_r.engine, _sc.camera, _r.filepath, _r.film_transparent, _r.resolution_percentage, _r.resolution_x,
         _r.resolution_y, _d.light, _d.color_type, _d.show_object_outline, _r.image_settings.color_mode)
_hidden = {o.name: o.hide_render for o in bpy.data.objects}
try:
    try:
        _r.engine = "BLENDER_WORKBENCH"
    except TypeError as e:
        print(e)
    _r.film_transparent = True
    _r.resolution_x, _r.resolution_y, _r.resolution_percentage = 1920, 1080, 100
    _d.light, _d.color_type, _d.show_object_outline = "STUDIO", "SINGLE", False
    _r.image_settings.color_mode = "RGBA"
    for o in bpy.data.objects:
        if o.type != "MESH":
            o.hide_render = True
    for v in _views:
        _sc.camera = bpy.data.objects[f"Ref_{v}"]
        _r.filepath = os.path.join(_out, f"{_tag}_{v}.png")
        bpy.ops.render.render(write_still=True)
finally:
    (_r.engine, _sc.camera, _r.filepath, _r.film_transparent, _r.resolution_percentage, _r.resolution_x,
     _r.resolution_y, _d.light, _d.color_type, _d.show_object_outline, _r.image_settings.color_mode) = _save
    for n, h in _hidden.items():
        bpy.data.objects[n].hide_render = h
print("eye_views:", _tag, _views)
