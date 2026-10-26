# Joint limit check for a rig (docs/pipeline_v2.md step 3 + QA step 6).
#   LIMITS = ROOT + r"/work/idle/joint_limits.json"; FRAMES = [1, 45]
#   exec(open(ROOT + r"/legacy/blender/joint_limits.py").read())   -> prints violations, sets JL_REPORT
# Each pose bone is compared with its rest relation to the parent: twist about the length axis, then the swing as
# Euler YZX bends. Bones are matched against the patterns in the limits file (fnmatch, first match wins).
import os
ROOT = (globals().get("ROOT") or os.environ.get("AI_ANIM_ROOT") or os.getcwd()).replace("\\", "/").rstrip("/")   # project folder: set ROOT = r"<folder>" before exec(), or env AI_ANIM_ROOT, or run from the project folder
if not os.path.exists(ROOT + "/MAP.md"):
    raise RuntimeError("Project folder not found: set ROOT = r'<project folder>' or env AI_ANIM_ROOT")
import fnmatch
import json
import math

import bpy
from mathutils import Quaternion, Vector

_cfg = json.load(open(globals().get("LIMITS", ROOT + r"/work/idle/joint_limits.json")))
_len_axis = {"X": 0, "Y": 1, "Z": 2}[_cfg["axes"]["length"][-1]]
_arm = bpy.data.objects["Armature"]


def joint_angles(pb):
    D = _arm.data.bones; par = pb.parent
    q = (D[par.name].matrix_local.inverted() @ D[pb.name].matrix_local).to_quaternion().inverted() @ \
        (par.matrix.inverted() @ pb.matrix).to_quaternion()
    ax = Vector((0, 0, 0)); ax[_len_axis] = 1
    p = Vector((q.x, q.y, q.z)).project(ax)
    t = Quaternion((q.w, p.x, p.y, p.z)); t.normalize()
    tw = math.degrees(2 * math.atan2(Vector((t.x, t.y, t.z)).dot(ax), t.w)); tw = (tw + 180) % 360 - 180
    e = (q @ t.inverted()).to_euler("YZX")
    return {"twist": tw, "bendY": math.degrees(e.y), "bendZ": math.degrees(e.z)}


def check_pose(frame=None):
    if frame is not None:
        bpy.context.scene.frame_set(frame)
    bad = []
    for pb in _arm.pose.bones:
        if not pb.parent:
            continue
        lim = next((v for k, v in _cfg["limits"].items() if fnmatch.fnmatch(pb.name, k)), None)
        if not lim:
            continue
        a = joint_angles(pb)
        for k, (lo, hi) in ((k, v) for k, v in lim.items() if k in a):
            if not lo <= a[k] <= hi:
                bad.append((frame, pb.name, k, round(a[k], 1), (lo, hi)))
    return bad


JL_REPORT = []
for _f in globals().get("FRAMES", [None]):
    JL_REPORT += check_pose(_f)
for _b in JL_REPORT:
    print(f"f{_b[0]} {_b[1]:16s} {_b[2]:6s} {_b[3]:+7.1f} outside {_b[4]}")
print("joint limit violations:", len(JL_REPORT))
