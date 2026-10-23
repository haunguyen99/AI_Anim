# Render trials on top of the accepted P0 stages (work/idle/p0_stages.json) and write the projected pixel box of a body
# part for region IoU / close-ups.
#   TRIALS = {"A1": {"Shoulder_R.rx": 10}}; PART_BONES = ["Shoulder_R", "Elbow_R", "Wrist_R"]; PART = "armR"
#   exec(open(r"E:/AI Animation/tools/blender/stage_trials.py").read())
# -> eye_<tag>_<view>.png, work/idle/analysis/part_<PART>.json (box per view, from the first trial), limit report
import json
import os

import bpy

_S = json.load(open(r"E:/AI Animation/work/idle/p0_stages.json"))
_base = dict(_S["stage1_legs"]["TRIAL_CH"])
for _k, _st in _S.items():
    if _k != "stage1_legs":
        _base.update(_st.get("TRIAL_CH_add", {}))
STANCE = _S["stage1_legs"]["STANCE"]
_post = _S["stage1_legs"]["POST"]
for _k, _st in _S.items():
    if _k != "stage1_legs" and _st.get("POST_add"):
        _post += "; " + _st["POST_add"]
_boxes = None
for TAG, _extra in TRIALS.items():  # noqa: F821
    TRIAL_CH = dict(_base, **{k: v for k, v in _extra.items() if not k.startswith("_")})
    TRIAL_POST = _post + ("; " + _extra["_post"] if "_post" in _extra else "")
    exec(open(r"E:/AI Animation/tools/blender/leg_trial.py").read().replace("print(TAG, _j", "pass #"))
    _bad = {}
    for _n in globals().get("PART_BONES", []):
        _lim = next((v for k, v in LIMITS["limits"].items() if fnmatch.fnmatch(_n, k)), None)
        if _lim:
            _a = joint_angles(ARM.pose.bones[_n])
            _b = {k: round(_a[k], 1) for k in ("twist", "bendY", "bendZ") if not _lim[k][0] <= _a[k] <= _lim[k][1]}
            if _b:
                _bad[_n] = _b
    print(TAG, "limit violations:", _bad)
    if _boxes is None and globals().get("PART_BONES") and not os.path.exists(f"E:/AI Animation/work/idle/analysis/part_{PART}.json"):  # noqa: F821
        # box is fixed once per part, so IoU stays comparable across runs
        _boxes = {}
        _pts = []
        for _n in PART_BONES:  # noqa: F821
            _pb = ARM.pose.bones[_n]
            _pts += [ARM.matrix_world @ _pb.head, ARM.matrix_world @ _pb.tail]
        for _v in ("front", "left", "back", "right"):
            _c = bpy.data.objects["Ref_" + _v]; _s = 1920 / _c.data.ortho_scale; _uv = []
            for _p in _pts:
                _q = _c.matrix_world.inverted() @ _p
                _uv.append((960 + _q.x * _s - _c.data.shift_x * 1920, 540 - _q.y * _s + _c.data.shift_y * 1920))
            _us = [u for u, _ in _uv]; _vs = [v for _, v in _uv]
            _boxes[_v] = [int(min(_us)) - 60, int(min(_vs)) - 60, int(max(_us)) + 60, int(max(_vs)) + 60]
        json.dump(_boxes, open(f"E:/AI Animation/work/idle/analysis/part_{PART}.json", "w"))  # noqa: F821
TRIAL_POST = None
