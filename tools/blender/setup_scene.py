"""Build an animator-ready Blender scene for a job: model (textures relinked), fps/range matching
the references, one ortho camera per calibrated view with its reference video as camera
background, and MCP-for-Blender set to auto-start.

blender -b -P tools/blender/setup_scene.py -- MODEL --work work/idle_breath --refs work/idle --out work/blender/boss_idle.blend
  --work : folder with mapping.json, controls.json, cameras.json (calibration)
  --refs : folder whose refs.json lists the reference videos (full clip)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bl_common as C  # noqa: E402
import bpy  # noqa: E402
from key_pose import Rig, camera_params  # noqa: E402
from mathutils import Matrix  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--work", required=True)
    ap.add_argument("--refs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(C.script_args())

    C.load_model(a.model)
    mapping = C.load_json(os.path.join(a.work, "mapping.json"))
    controls = C.load_json(os.path.join(a.work, "controls.json"))
    cals = C.load_json(os.path.join(a.work, "cameras.json"))
    refs = C.load_json(os.path.join(a.refs, "refs.json"))
    arm = C.find_armature(mapping.get("armature"))
    rig = Rig(arm, mapping)

    scene = bpy.context.scene
    scene.render.fps = round(refs["fps"])
    scene.frame_start, scene.frame_end = 1, refs["frame_count"]
    scene.render.resolution_x, scene.render.resolution_y = 1920, 1080

    col = bpy.data.collections.new("RefCameras")
    scene.collection.children.link(col)
    for view, cal in cals.items():
        info = refs["views"][view]
        d, up, right, k, pos = camera_params(rig, view, cal, info["width"], info["height"],
                                             controls["ground_m"], controls["character_height_m"])
        cam = bpy.data.cameras.new(f"Ref_{view}")
        cam.type = "ORTHO"
        cam.sensor_fit = "HORIZONTAL"
        cam.ortho_scale = info["width"] * k
        cam.clip_end = 200
        obj = bpy.data.objects.new(f"Ref_{view}", cam)
        col.objects.link(obj)
        obj.matrix_world = Matrix(((right.x, up.x, -d.x, pos.x), (right.y, up.y, -d.y, pos.y),
                                   (right.z, up.z, -d.z, pos.z), (0, 0, 0, 1)))
        clip = bpy.data.movieclips.load(info["path"])
        clip.name = f"ref_{view}"
        clip.frame_start = 1
        cam.show_background_images = True
        bg = cam.background_images.new()
        bg.source = "MOVIE_CLIP"
        bg.clip = clip
        bg.alpha = 0.6
        bg.display_depth = "BACK"
        bg.frame_method = "FIT"
        print(f"camera Ref_{view}: {os.path.basename(info['path'])}")
    scene.camera = bpy.data.objects.get("Ref_front") or scene.camera

    if hasattr(scene, "blendermcp_auto_start_server"):
        scene.blendermcp_auto_start_server = True
    for o in bpy.data.objects:
        o.select_set(False)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.out))
    print("saved", a.out)


main()
