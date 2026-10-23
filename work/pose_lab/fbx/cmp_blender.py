# blender -b --python cmp_blender.py -- <ref.fbx> <mine.fbx> : import both, compare bone world positions + rotations per frame
import bpy, sys
from mathutils import Matrix
a, b = sys.argv[sys.argv.index("--") + 1:][:2]
def imp(p):
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.import_scene.fbx(filepath=p, automatic_bone_orientation=False)
    A = next(o for o in bpy.data.objects if o.type == "ARMATURE"); sc = bpy.context.scene
    act = A.animation_data.action; f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    out = {}
    for f in range(f0, f1 + 1):
        sc.frame_set(f); out[f] = {pb.name: (A.matrix_world @ pb.matrix).copy() for pb in A.pose.bones}
    return out, (f0, f1)
ra, ia = imp(a); rb, ib = imp(b)
print("RANGES", ia, ib)
fa = sorted(ra); fb = sorted(rb)
for shift in (0,):
    import math
    bad = {}
    pe = re = 0.0
    for fi, fj in zip(fa, fb):
        for n, M in ra[fi].items():
            if n in rb[fj]:
                N = rb[fj][n]; pe = max(pe, (M.to_translation() - N.to_translation()).length)
                d = M.to_quaternion().rotation_difference(N.to_quaternion()); ang = 2*math.acos(min(1.0, abs(d.w)))
                if (M.to_translation() - N.to_translation()).length > 0.002 or ang > 0.02: bad.setdefault(n, []).append((fi, round((M.to_translation() - N.to_translation()).length, 4), round(math.degrees(ang), 2)))
                re = max(re, ang)
    import math
    print("CMP frames", len(fa), len(fb), "max pos err %.5f" % pe, "max rot err deg %.4f" % math.degrees(re))

for n, v in list(bad.items())[:12]: print('BAD', n, len(v), v[:3])
