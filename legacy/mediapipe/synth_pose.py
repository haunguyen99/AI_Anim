"""Make a synthetic pose.json by animating the test rig procedurally.

blender -b --factory-startup -P tests/synth_pose.py -- RIG.blend OUT_pose.json
Landmarks come from the posed joints, so a perfect retarget onto the same rig
should score ~0 deg on limb directions.
"""
import json
import math
import sys

import bpy
from mathutils import Euler, Vector

rig_path, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.open_mainfile(filepath=rig_path)
arm = bpy.data.objects["CustomRig"]
P = arm.pose.bones
N = 90
NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer", "right_eye_inner",
    "right_eye", "right_eye_outer", "left_ear", "right_ear", "mouth_left",
    "mouth_right", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky", "left_index",
    "right_index", "left_thumb", "right_thumb", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle", "left_heel",
    "right_heel", "left_foot_index", "right_foot_index",
]


def pose_at(t):
    s = math.sin(t * 2 * math.pi)
    for pb in P:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0, 0, 0)
    P["Pelvis"].rotation_euler = Euler((0.15 * s, 0.0, 0.4 * s))       # twist + lean
    P["Torso_Up"].rotation_euler = Euler((0.2 * s, 0.25 * s, 0))
    P["NeckBone"].rotation_euler = Euler((0.2, 0, 0.3 * s))
    P["Arm_Up.L"].rotation_euler = Euler((0.3, 0.6 * s, -0.9 - 0.5 * s))
    P["Arm_Low.L"].rotation_euler = Euler((0, 0, -1.2 * (0.5 + 0.5 * s)))
    P["Arm_Up.R"].rotation_euler = Euler((-0.4 * s, 0.2, 0.7))
    P["Arm_Low.R"].rotation_euler = Euler((0, 0, 0.9 * (0.5 - 0.5 * s)))
    P["Palm.L"].rotation_euler = Euler((0.4 * s, 0, 0.3))
    P["Leg_Up.L"].rotation_euler = Euler((-0.6 * s, 0, 0.1))
    P["Leg_Low.L"].rotation_euler = Euler((1.0 * (0.5 + 0.5 * s), 0, 0))
    P["Leg_Up.R"].rotation_euler = Euler((0.5 * s, 0, -0.1))
    P["Leg_Low.R"].rotation_euler = Euler((0.8 * (0.5 - 0.5 * s), 0, 0))
    P["Foot.L"].rotation_euler = Euler((0.3 * s, 0, 0))
    P["Pelvis"].location = (0, 0.05 * s, 0)   # bone-local Y = world up for pelvis
    bpy.context.view_layer.update()


def W(v):
    return arm.matrix_world @ v


frames = []
truth = []
for k in range(N):
    pose_at(k / N)
    truth.append({pb.name: list((arm.matrix_world @ pb.matrix).to_quaternion()) for pb in P})
    lm = {}
    for s, lr in (("L", "left"), ("R", "right")):
        lm[f"{lr}_hip"] = W(P[f"Leg_Up.{s}"].head)
        lm[f"{lr}_knee"] = W(P[f"Leg_Low.{s}"].head)
        lm[f"{lr}_ankle"] = W(P[f"Foot.{s}"].head)
        lm[f"{lr}_foot_index"] = W(P[f"Toe.{s}"].tail)
        lm[f"{lr}_heel"] = W(P[f"Foot.{s}"].head) - Vector((0, 0, 0.05))
        lm[f"{lr}_shoulder"] = W(P[f"Arm_Up.{s}"].head)
        lm[f"{lr}_elbow"] = W(P[f"Arm_Low.{s}"].head)
        lm[f"{lr}_wrist"] = W(P[f"Palm.{s}"].head)
        hm = arm.matrix_world @ P[f"Palm.{s}"].matrix
        z = hm.to_3x3() @ Vector((0, 0, 0.02))
        tip = W(P[f"Palm.{s}"].tail)
        lm[f"{lr}_index"] = tip + z
        lm[f"{lr}_pinky"] = tip - z
        lm[f"{lr}_thumb"] = tip
    hm = (arm.matrix_world @ P["HeadBone"].matrix).to_3x3().normalized()
    hh = W(P["HeadBone"].head)
    # head bone points up (local Y); local X = character side, local -Z ~ forward for this rig
    side = hm @ Vector((1, 0, 0))
    up = hm @ Vector((0, 1, 0))
    fwd = side.cross(up)
    ear = hh + up * 0.115
    lm["left_ear"], lm["right_ear"] = ear + side * 0.069, ear - side * 0.069
    lm["nose"] = ear + fwd * 0.08 - up * 0.028
    for n in NAMES:
        lm.setdefault(n, lm["nose"])
    hip = (lm["left_hip"] + lm["right_hip"]) / 2
    frames.append({
        "world": [list(lm[n] - hip) for n in NAMES],
        "image": [[0.5 + lm[n].x / 3, 0.5 - (lm[n].z - 1.0) / 3] for n in NAMES],
        "vis": [1.0] * 33,
        "detected": True,
    })

with open(out, "w") as f:
    json.dump({"source": "synthetic", "fps": 30.0, "width": 1000, "height": 1000, "first_frame": 0,
               "frame_count": N, "detected_ratio": 1.0, "landmark_names": NAMES, "frames": frames}, f)
with open(out.replace(".json", ".truth.json"), "w") as f:
    json.dump(truth, f)
print("wrote", out)
