"""Full-orientation error (deg) of result.blend vs synth_pose truth, per bone.

blender -b --factory-startup -P tests/compare_truth.py -- RESULT.blend TRUTH.json
"""
import json
import math
import sys

import bpy
from mathutils import Quaternion

blend, truth_path = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.open_mainfile(filepath=blend)
arm = bpy.data.objects["CustomRig"]
truth = json.load(open(truth_path))
errs = {}
for k, t in enumerate(truth):
    bpy.context.scene.frame_set(k + 1)
    for pb in arm.pose.bones:
        q = (arm.matrix_world @ pb.matrix).to_quaternion()
        d = math.degrees(q.rotation_difference(Quaternion(t[pb.name])).angle)
        errs.setdefault(pb.name, []).append(min(d, 360 - d))
for n, v in sorted(errs.items(), key=lambda kv: -sum(kv[1])):
    print(f"{n:12s} mean {sum(v) / len(v):6.2f}  max {max(v):6.2f}")
