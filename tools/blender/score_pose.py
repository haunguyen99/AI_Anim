# Score the CURRENT pose of "Armature" against the original animation (answer key; never used to set the pose).
#   SCORE_FRAME = 1; SCORE_TAG = "legs K4"; SCORE_BONES = [...]; exec(open(r".../score_pose.py").read())
# Appends a line to work/idle/original/tests.jsonl: per-bone position error (cm, character axes) and rotation error (deg).
import json
import math

import bpy
import numpy as np

_O = json.load(open(r"E:/AI Animation/work/idle/original/orig_joints.json"))
_f = globals().get("SCORE_FRAME", 1); _i = _O["frames"].index(_f)
_arm = bpy.data.objects["Armature"]; _mw = _arm.matrix_world
_res = {}
for _n in SCORE_BONES:  # noqa: F821
    _M = _mw @ _arm.pose.bones[_n].matrix
    _t = np.array(_M.to_translation()); _q = _M.to_quaternion()
    _o = _O["bones"][_n][_i]
    _d = (_t - np.array(_o[:3])) * np.array([-1, -1, 1]) * 100          # character axes, cm
    _dot = abs(_q.w * _o[3] + _q.x * _o[4] + _q.y * _o[5] + _q.z * _o[6])
    _res[_n] = {"err_cm": round(float(np.linalg.norm(_d)), 1), "dxyz_cm": np.round(_d, 1).tolist(),
                "rot_deg": round(math.degrees(2 * math.acos(min(1.0, _dot))), 1)}
_line = {"tag": globals().get("SCORE_TAG", ""), "frame": _f, "bones": _res,
         "mean_cm": round(float(np.mean([v["err_cm"] for v in _res.values()])), 1)}
open(r"E:/AI Animation/work/idle/original/tests.jsonl", "a").write(json.dumps(_line) + "\n")
print(json.dumps(_line))
