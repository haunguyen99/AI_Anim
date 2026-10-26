"""Render flat white silhouettes of the character (body + prop meshes) through Ref_* cameras.

blender -b FILE.blend -P legacy/blender/sil_render.py -- OUTDIR FRAMES [CAMS]
  FRAMES: comma list, e.g. 1,13,33 ; CAMS default Ref_front,Ref_back,Ref_left,Ref_right,Ref_top
Writes OUTDIR/<cam>_<frame:03d>.png (1920x1080, white on black). Does not save the .blend.
Pair with legacy/blender_tools/sil_compare.py (IoU + overlay against the reference frame).
"""
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
out, frames = argv[0], [int(f) for f in argv[1].split(",")]
cams = argv[2].split(",") if len(argv) > 2 else ["Ref_front", "Ref_back", "Ref_left", "Ref_right", "Ref_top"]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
try:
    sc.render.engine = "BLENDER_WORKBENCH"
except TypeError as e:
    print(e)
sh = sc.display.shading
sh.light, sh.color_type, sh.single_color = "FLAT", "SINGLE", (1, 1, 1)
sh.show_object_outline = False
sh.background_type = "WORLD" if hasattr(sh, "background_type") else None
if sc.world is None:
    sc.world = bpy.data.worlds.new("w")
sc.world.color = (0, 0, 0)
sc.render.film_transparent = False
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "BW"
sc.view_settings.view_transform = "Standard"
for o in bpy.data.objects:
    if o.type not in ("MESH",):
        o.hide_render = True
for f in frames:
    sc.frame_set(f)
    for c in cams:
        sc.camera = bpy.data.objects[c]
        sc.render.filepath = os.path.join(out, f"{c}_{f:03d}.png")
        bpy.ops.render.render(write_still=True)
print("done", len(frames) * len(cams))
