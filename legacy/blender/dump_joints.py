# Dump world-space joint transforms of an armature for every frame (for comparing two animations of the same rig).
# Headless:  blender -b -P legacy/blender/dump_joints.py -- --fbx ORIG.fbx --out orig_joints.json
# Live (MCP): DUMP_OUT = r".../ours.json"; exec(open(r".../dump_joints.py").read())   (uses object "Armature")
# JSON: {"frames": [...], "bones": {name: [[x,y,z, qw,qx,qy,qz], ...]}}  world metres / world rotation (unit quaternion)
import json
import sys

import bpy


def dump(arm, frames, out):
    sc = bpy.context.scene
    data = {n: [] for n in [b.name for b in arm.pose.bones]}
    for f in frames:
        sc.frame_set(f)
        mw = arm.matrix_world
        for pb in arm.pose.bones:
            M = mw @ pb.matrix
            q = M.to_quaternion(); t = M.to_translation()
            data[pb.name].append([round(t.x, 5), round(t.y, 5), round(t.z, 5),
                                  round(q.w, 6), round(q.x, 6), round(q.y, 6), round(q.z, 6)])
    json.dump({"frames": list(frames), "bones": data}, open(out, "w"))
    print("dumped", len(frames), "frames to", out)


if "--" in sys.argv:
    argv = sys.argv[sys.argv.index("--") + 1:]
    fbx = argv[argv.index("--fbx") + 1]; out = argv[argv.index("--out") + 1]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx)
    a = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
    r = a.animation_data.action.frame_range
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = int(r[0]), int(r[1])
    dump(a, range(int(r[0]), int(r[1]) + 1), out)
else:
    dump(bpy.data.objects["Armature"], range(1, 134), DUMP_OUT)  # noqa: F821
