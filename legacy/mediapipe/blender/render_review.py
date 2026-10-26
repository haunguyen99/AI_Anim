"""Render sample frames of the animated rig from the reference camera's viewpoint.

blender -b -P tools/blender/render_review.py -- RESULT_BLEND --frames 1,20,40 --outdir work/review
        [--armature NAME] [--size 512]

Writes render_XXXXX.png (Workbench) plus joints_XXXXX.json (2D bone segments,
normalised 0..1) so the skeleton can be drawn even if the model has no mesh.
The camera looks along +Y (the reference camera in pose.json space).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bl_common as C  # noqa: E402
import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from mathutils import Euler, Vector  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("blend")
    ap.add_argument("--frames", required=True, help="comma-separated scene frames")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--armature", default=None)
    ap.add_argument("--mapping", default=None, help="mapping.json, to project landmark-equivalent joints")
    ap.add_argument("--size", type=int, default=512)
    a = ap.parse_args(C.script_args())

    C.load_model(a.blend)
    mapping = C.load_json(a.mapping) if a.mapping else {}
    arm = C.find_armature(a.armature or mapping.get("armature"))
    joints = {k: v for k, v in mapping.get("joints", {}).items() if "bone" in v}
    scene = bpy.context.scene
    frames = [int(x) for x in a.frames.split(",") if x.strip()]

    # bounds of all bone heads/tails over the sampled frames
    pts = []
    for fr in frames:
        scene.frame_set(fr)
        if joints:  # frame the character, not stray prop/root bones
            for spec in joints.values():
                pb = arm.pose.bones[spec["bone"]]
                pts.append(arm.matrix_world @ (pb.tail if spec.get("end") == "tail" else pb.head))
        else:
            for pb in arm.pose.bones:
                pts += [arm.matrix_world @ pb.head, arm.matrix_world @ pb.tail]
    if joints:  # joints stop at the neck/feet; leave room for the head
        h = max(p.z for p in pts) - min(p.z for p in pts)
        pts.append(Vector((pts[0].x, pts[0].y, max(p.z for p in pts) + 0.3 * h)))
    lo =Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center = (lo + hi) / 2
    extent = max(hi.x - lo.x, hi.z - lo.z) * 1.15

    cam_data = bpy.data.cameras.new("ReviewCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = extent
    cam = bpy.data.objects.new("ReviewCam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (center.x, lo.y - extent * 3, center.z)
    cam.rotation_euler = Euler((1.5707963, 0, 0))
    cam_data.clip_end = extent * 20
    scene.camera = cam

    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "OBJECT"
    scene.render.resolution_x = a.size
    scene.render.resolution_y = a.size
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    for o in scene.objects:
        if o.type == "MESH":
            o.color = (0.75, 0.6, 0.45, 1)

    os.makedirs(a.outdir, exist_ok=True)
    for fr in frames:
        scene.frame_set(fr)
        proj = lambda p: (lambda c: [c.x, 1 - c.y])(world_to_camera_view(scene, cam, arm.matrix_world @ p))  # noqa: E731
        segs = [{"bone": pb.name, "a": proj(pb.head), "b": proj(pb.tail)} for pb in arm.pose.bones]
        lms = {}
        for name, spec in joints.items():
            pb = arm.pose.bones[spec["bone"]]
            lms[name] = proj(pb.tail if spec.get("end") == "tail" else pb.head)
        C.save_json(os.path.join(a.outdir, f"joints_{fr:05d}.json"), {"bones": segs, "landmarks": lms})
        scene.render.filepath = os.path.abspath(os.path.join(a.outdir, f"render_{fr:05d}.png"))
        bpy.ops.render.render(write_still=True)
    print(f"Rendered {len(frames)} frames to {a.outdir}")


main()
