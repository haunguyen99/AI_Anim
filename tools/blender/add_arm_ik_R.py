# Add a right-arm IK chain to the existing CTRL rig (live Blender, boss_attack.blend):
#   CTRL_upper_R / CTRL_fore_R (child of FOLLOW_scap_R), CTRL_hand_ik_R (child of CTRL_weapon),
#   CTRL_elbow_pole_R (child of FOLLOW_chest), helpers H_Shoulder_R/H_Elbow_R/H_Wrist_R.
# Shoulder_R/Elbow_R/Wrist_R get COPY_LOCATION/ROTATION constraints whose influence is keyed:
# 1 while the right hand grips the weapon, 0 when the arm is FK (idle hang).
# Built at frame 1 (P0).   exec(open(ROOT + r"/tools/blender/add_arm_ik_R.py").read())
import math

import bpy
from mathutils import Matrix, Vector

sc = bpy.context.scene
arm = bpy.data.objects["Armature"]
ctrl = bpy.data.objects["CTRL"]
mw = arm.matrix_world
P = arm.pose.bones
sc.frame_set(1)
# arm must be at P0 with no R-arm constraints
for n in ("Shoulder_R", "Elbow_R", "Wrist_R"):
    for c in list(P[n].constraints):
        if c.name.startswith("CTRL_"):
            P[n].constraints.remove(c)
bpy.context.view_layer.update()


def wpos(n, end="head"):
    pb = P[n]
    return mw @ (pb.head if end == "head" else pb.tail)


def wmat(n):
    M = mw @ P[n].matrix
    return Matrix.Translation(M.to_translation()) @ M.to_3x3().normalized().to_4x4()


for o in list(bpy.context.selected_objects):
    o.select_set(False)
bpy.context.view_layer.objects.active = ctrl
ctrl.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
E = ctrl.data.edit_bones
for n in ("FOLLOW_scap_R", "CTRL_upper_R", "CTRL_fore_R", "CTRL_hand_ik_R", "CTRL_elbow_pole_R",
          "H_Shoulder_R", "H_Elbow_R", "H_Wrist_R"):
    if n in E:
        E.remove(E[n])


def bone(name, head, tail, parent=None, connect=False):
    b = E.new(name)
    b.head, b.tail = head, tail
    if parent:
        b.parent = E[parent]
        b.use_connect = connect
    return b


def matbone(name, M, length, parent=None):
    b = E.new(name)
    b.head, b.tail = (0, 0, 0), (0, length, 0)
    b.matrix = M
    b.length = length
    b.use_deform = False
    if parent:
        b.parent = E[parent]
    return b


bone("FOLLOW_scap_R", wpos("Scapula_R"), wpos("Shoulder_R"))
sh, el, wr = wpos("Shoulder_R"), wpos("Elbow_R"), wpos("Wrist_R")
bone("CTRL_upper_R", sh, el, "FOLLOW_scap_R")
bone("CTRL_fore_R", el, wr, "CTRL_upper_R", connect=True)
matbone("CTRL_hand_ik_R", wmat("Wrist_R"), 0.15, "CTRL_weapon")
pole = el + (el - (sh + wr) / 2).normalized() * 0.5
bone("CTRL_elbow_pole_R", pole, pole + Vector((0, 0, 0.12)), "FOLLOW_chest")
matbone("H_Shoulder_R", wmat("Shoulder_R"), 0.08, "CTRL_upper_R")
matbone("H_Elbow_R", wmat("Elbow_R"), 0.08, "CTRL_fore_R")
matbone("H_Wrist_R", wmat("Wrist_R"), 0.08, "CTRL_hand_ik_R")
bpy.ops.object.mode_set(mode="OBJECT")

CP = ctrl.pose.bones
c = CP["FOLLOW_scap_R"].constraints.new("CHILD_OF")
c.name = "CTRL_follow"
c.target, c.subtarget = arm, "Scapula_R"
c.inverse_matrix = (mw @ P["Scapula_R"].matrix).inverted()
bpy.context.view_layer.update()

joint = (ctrl.matrix_world @ CP["CTRL_fore_R"].head).copy()
ik = CP["CTRL_fore_R"].constraints.new("IK")
ik.name = "CTRL_ik"
ik.target, ik.subtarget = ctrl, "CTRL_hand_ik_R"
ik.pole_target, ik.pole_subtarget = ctrl, "CTRL_elbow_pole_R"
ik.chain_count = 2
best = None
for a in range(-180, 180, 1):
    ik.pole_angle = math.radians(a)
    bpy.context.view_layer.update()
    e = ((ctrl.matrix_world @ CP["CTRL_fore_R"].head) - joint).length
    if best is None or e < best[0]:
        best = (e, a)
ik.pole_angle = math.radians(best[1])
print(f"CTRL_fore_R: pole angle {best[1]}, joint error {best[0] * 100:.2f} cm")

for d, h in (("Shoulder_R", "H_Shoulder_R"), ("Elbow_R", "H_Elbow_R"), ("Wrist_R", "H_Wrist_R")):
    for typ in ("COPY_LOCATION", "COPY_ROTATION"):
        cc = P[d].constraints.new(typ)
        cc.name = "CTRL_" + typ.lower()
        cc.target, cc.subtarget = ctrl, h
        cc.influence = 0.0
for b in ctrl.data.bones:
    if b.name.startswith(("H_", "FOLLOW_")):
        b.hide = True
bpy.context.view_layer.objects.active = arm
bpy.context.view_layer.update()
print("right-arm IK added")
