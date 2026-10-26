# QA report on the live Idle action (docs/pipeline_v2.md step 6). Every frame 1..N.
#   exec(open(ROOT + r"/legacy/blender/qa_report.py").read())   -> prints PASS/FAIL table, sets QA dict
import os
ROOT = (globals().get("ROOT") or os.environ.get("AI_ANIM_ROOT") or os.getcwd()).replace("\\", "/").rstrip("/")   # project folder: set ROOT = r"<folder>" before exec(), or env AI_ANIM_ROOT, or run from the project folder
if not os.path.exists(ROOT + "/MAP.md"):
    raise RuntimeError("Project folder not found: set ROOT = r'<project folder>' or env AI_ANIM_ROOT")
import json
import math

import bpy
import numpy as np

_sc = bpy.context.scene; _A = bpy.data.objects["Armature"]; _mw = _A.matrix_world; _P = _A.pose.bones
LIMITS = ROOT + r"/work/idle/joint_limits.json"; FRAMES = []
exec(open(ROOT + r"/legacy/blender/joint_limits.py").read())
N = _sc.frame_end
_sc.frame_set(1)
_a0 = {s: np.array(_mw @ _P["Ankle_" + s].head) for s in "LR"}


def _hand_rel():
    W = _mw @ _P["Weapon"].matrix
    return np.array(W.inverted() @ (_mw @ _P["Wrist_L"].head)) * W.to_scale()[0]


_r0 = _hand_rel()
TRACK = ["Root_M", "Chest_M", "Head_M", "Wrist_R", "Wrist_L", "Weapon", "Elbow_R", "Elbow_L"]
pos = {b: [] for b in TRACK}
slide = drift = 0.0; viol = {}
for f in range(1, N + 1):
    _sc.frame_set(f)
    slide = max(slide, max(np.linalg.norm(np.array(_mw @ _P["Ankle_" + s].head) - _a0[s]) for s in "LR"))
    drift = max(drift, np.linalg.norm(_hand_rel() - _r0))
    for b in TRACK:
        pos[b].append(np.array(_mw @ _P[b].head))
    for v in check_pose(f):
        if "Finger" in v[1] or "Knee" in v[1]:       # fingers: generic limits; knees: inherited from the rig's P0
            continue
        viol.setdefault(v[1], []).append(f)
_sc.frame_set(1)
# loop seam: velocity at N-1 -> N vs 1 -> 2 (frame N == frame 1)
seam = {}
jit = {}
for b, p in pos.items():
    p = np.array(p)
    v_end = p[-1] - p[-2]; v_start = p[1] - p[0]
    seam[b] = float(np.linalg.norm(v_end - v_start) * 100)
    acc = np.linalg.norm(p[2:] - 2 * p[1:-1] + p[:-2], axis=1) * 100
    jit[b] = float(acc.max())
QA = {"foot_slide_cm": round(slide * 100, 2), "hand_drift_cm": round(drift * 100, 2),
      "limit_violations": {k: [v[0], v[-1], len(v)] for k, v in viol.items()},
      "loop_seam_dv_cm": {k: round(v, 2) for k, v in seam.items()},
      "max_accel_cm_per_f2": {k: round(v, 2) for k, v in jit.items()}}
rows = [("Foot slide", QA["foot_slide_cm"], "< 0.3 cm", QA["foot_slide_cm"] < 0.3),
        ("Hand drift on weapon", QA["hand_drift_cm"], "< 0.3 cm", QA["hand_drift_cm"] < 0.3),
        ("Joint limits", sum(len(v) for v in viol.values()), "0 frames", not viol),
        ("Loop seam (max dv)", max(seam.values()), "< 0.3 cm/F", max(seam.values()) < 0.3),
        ("Jitter (max accel)", max(jit.values()), "< 1.5 cm/F^2", max(jit.values()) < 1.5)]
for name, val, thr, ok in rows:
    print(f"{'PASS' if ok else 'FAIL'}  {name:22s} {val:8.2f}   ({thr})")
print(json.dumps({k: v for k, v in QA.items() if k in ("limit_violations",)}))
print("worst seam:", max(seam, key=seam.get), "worst accel:", max(jit, key=jit.get), round(max(jit.values()), 2))
json.dump(QA, open(ROOT + r"/work/idle/qa.json", "w"), indent=1)
