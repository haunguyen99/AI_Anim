# blender -b --python cmp_page_track.py -- <page.fbx> <page_track.json>
# Imports the FBX the page exported and compares a few bones' world positions on every frame with the positions the
# page itself showed (glTF world, Y up, metres) -> max error in cm. Checks that the FBX carries the spline + foot lock.
import bpy, sys, json
a, t = sys.argv[sys.argv.index("--") + 1:][:2]
track = json.load(open(t))
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.fbx(filepath=a, automatic_bone_orientation=False)
A = next(o for o in bpy.data.objects if o.type == "ARMATURE"); sc = bpy.context.scene
f0, f1 = (int(x) for x in A.animation_data.action.frame_range)
print("RANGE", f0, f1, "page frames", len(next(iter(track.values()))))
worst = 0.0
for n, pts in track.items():
    e = 0.0
    for i, (x, y, z) in enumerate(pts):
        sc.frame_set(f0 + i)
        w = A.matrix_world @ A.pose.bones[n].head
        e = max(e, ((w.x - x) ** 2 + (w.y - (-z)) ** 2 + (w.z - y) ** 2) ** 0.5)
    worst = max(worst, e); print("BONE", n, "max err %.3f cm" % (e * 100))
print("WORST %.3f cm" % (worst * 100))
