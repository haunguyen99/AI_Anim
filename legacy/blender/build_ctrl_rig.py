# Build an animator control rig ("CTRL" armature) for the Boss rig in the LIVE Blender scene.
# Run via MCP:  exec(open(ROOT + r"/legacy/blender/build_ctrl_rig.py").read())
# The deform armature must already be in the base pose (P0) at the current frame.
#   legs   : clean IK chains (hip->knee->ankle), planted foot controls, knee poles
#   weapon : CTRL_weapon follows Chest_M (child-of), animatable on top
#   L arm  : IK to CTRL_hand_ik_L, which rides on the weapon; elbow pole follows the chest
# Deform bones copy location+rotation (world) from hidden helper bones H_*.
import math

import bpy
from mathutils import Matrix, Vector

sc = bpy.context.scene
arm = bpy.data.objects["Armature"]
mw = arm.matrix_world
P = arm.pose.bones


def wpos(n, end="head"):
    pb = P[n]
    return mw @ (pb.head if end == "head" else pb.tail)


def wmat(n):
    M = mw @ P[n].matrix
    return Matrix.Translation(M.to_translation()) @ M.to_3x3().normalized().to_4x4()


old = bpy.data.objects.get("CTRL")
if old:
    bpy.data.objects.remove(old, do_unlink=True)
for pb in P:
    for c in list(pb.constraints):
        if c.name.startswith("CTRL_"):
            pb.constraints.remove(c)
bpy.context.view_layer.update()

ad = bpy.data.armatures.new("CTRL")
ctrl = bpy.data.objects.new("CTRL", ad)
sc.collection.objects.link(ctrl)
ad.display_type = "STICK"
ctrl.show_in_front = True
for o in list(bpy.context.selected_objects):
    o.select_set(False)
bpy.context.view_layer.objects.active = ctrl
ctrl.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
E = ad.edit_bones


def bone(name, head, tail, parent=None, connect=False):
    b = E.new(name)
    b.head, b.tail = head, tail
    if parent:
        b.parent = E[parent]
        b.use_connect = connect
    return b


def matbone(name, M, length, parent=None, deform=False):
    b = E.new(name)
    b.head, b.tail = (0, 0, 0), (0, length, 0)   # non-zero length first, then the matrix sticks
    b.matrix = M
    b.length = length
    b.use_deform = deform
    if parent:
        b.parent = E[parent]
    return b


bone("FOLLOW_root", wpos("Root_M"), wpos("Root_M") + Vector((0, 0, 0.15)))
bone("FOLLOW_chest", wpos("Chest_M"), wpos("Chest_M") + Vector((0, 0, 0.15)))
bone("FOLLOW_scap_L", wpos("Scapula_L"), wpos("Shoulder_L"))
for s in ("L", "R"):
    hip, knee, ank, toe = wpos(f"Hip_{s}"), wpos(f"Knee_{s}"), wpos(f"Ankle_{s}"), wpos(f"ToesEnd_{s}")
    bone(f"CTRL_thigh_{s}", hip, knee, "FOLLOW_root")
    bone(f"CTRL_shin_{s}", knee, ank, f"CTRL_thigh_{s}", connect=True)
    matbone(f"CTRL_foot_ik_{s}", wmat(f"Ankle_{s}"), 0.25)
    # user 2026-10-22 "Hãy làm vậy với IK chân luôn": the knee pole is a child of the foot control, so the knee
    # follows where the foot points (turn the foot -> the knee turns with it) instead of staying fixed in world space
    bone(f"CTRL_knee_pole_{s}", knee + Vector((0, -0.6, 0)), knee + Vector((0, -0.75, 0)), f"CTRL_foot_ik_{s}")
    matbone(f"H_Hip_{s}", wmat(f"Hip_{s}"), 0.08, f"CTRL_thigh_{s}")
    matbone(f"H_Knee_{s}", wmat(f"Knee_{s}"), 0.08, f"CTRL_shin_{s}")
    matbone(f"H_Ankle_{s}", wmat(f"Ankle_{s}"), 0.08, f"CTRL_foot_ik_{s}")
matbone("CTRL_weapon", wmat("Weapon"), 0.4, "FOLLOW_scap_L")   # the weapon rests on the left shoulder
matbone("H_Weapon", wmat("Weapon"), 0.08, "CTRL_weapon")
sh, el, wr = wpos("Shoulder_L"), wpos("Elbow_L"), wpos("Wrist_L")
bone("CTRL_upper_L", sh, el, "FOLLOW_scap_L")
bone("CTRL_fore_L", el, wr, "CTRL_upper_L", connect=True)
matbone("CTRL_hand_ik_L", wmat("Wrist_L"), 0.15, "CTRL_weapon")
pole = el + (el - (sh + wr) / 2).normalized() * 0.5
bone("CTRL_elbow_pole_L", pole, pole + Vector((0, 0, 0.12)), "FOLLOW_chest")
matbone("H_Shoulder_L", wmat("Shoulder_L"), 0.08, "CTRL_upper_L")
matbone("H_Elbow_L", wmat("Elbow_L"), 0.08, "CTRL_fore_L")
matbone("H_Wrist_L", wmat("Wrist_L"), 0.08, "CTRL_hand_ik_L")
bpy.ops.object.mode_set(mode="OBJECT")

CP = ctrl.pose.bones
for cb, sub in (("FOLLOW_root", "Root_M"), ("FOLLOW_chest", "Chest_M"), ("FOLLOW_scap_L", "Scapula_L")):
    c = CP[cb].constraints.new("CHILD_OF")
    c.name = "CTRL_follow"
    c.target, c.subtarget = arm, sub
    c.inverse_matrix = (mw @ P[sub].matrix).inverted()
bpy.context.view_layer.update()


def add_ik(end, target, pole_name):
    joint = (ctrl.matrix_world @ CP[end].head).copy()
    c = CP[end].constraints.new("IK")
    c.name = "CTRL_ik"
    c.target, c.subtarget = ctrl, target
    c.pole_target, c.pole_subtarget = ctrl, pole_name
    c.chain_count = 2
    best = None
    for a in range(-180, 180, 1):
        c.pole_angle = math.radians(a)
        bpy.context.view_layer.update()
        e = ((ctrl.matrix_world @ CP[end].head) - joint).length
        if best is None or e < best[0]:
            best = (e, a)
    c.pole_angle = math.radians(best[1])
    print(f"{end}: pole angle {best[1]}, joint error {best[0] * 100:.2f} cm")


for s in ("L", "R"):
    add_ik(f"CTRL_shin_{s}", f"CTRL_foot_ik_{s}", f"CTRL_knee_pole_{s}")
add_ik("CTRL_fore_L", "CTRL_hand_ik_L", "CTRL_elbow_pole_L")

pairs = [(f"{b}_{s}", f"H_{b}_{s}") for s in ("L", "R") for b in ("Hip", "Knee", "Ankle")]
pairs += [("Shoulder_L", "H_Shoulder_L"), ("Elbow_L", "H_Elbow_L"), ("Wrist_L", "H_Wrist_L"), ("Weapon", "H_Weapon")]
before = {d: (mw @ P[d].matrix).copy() for d, _ in pairs}
for d, h in pairs:
    for typ in ("COPY_LOCATION", "COPY_ROTATION"):
        c = P[d].constraints.new(typ)
        c.name = "CTRL_" + typ.lower()
        c.target, c.subtarget = ctrl, h
bpy.context.view_layer.update()
worst_pos = max(((mw @ P[d].matrix).to_translation() - before[d].to_translation()).length for d, _ in pairs)
worst_rot = max(math.degrees((mw @ P[d].matrix).to_quaternion().rotation_difference(before[d].to_quaternion()).angle)
                for d, _ in pairs)
print(f"rig built: max joint shift {worst_pos * 100:.2f} cm, max rotation change {worst_rot:.2f} deg")
# hide helpers, colour controls
for b in ad.bones:
    if b.name.startswith(("H_", "FOLLOW_")):
        b.hide = True
bpy.context.view_layer.objects.active = arm
