# Re-parent a prop joint in a baked clip (made by export_clip.py) without changing its motion, then export FBX
# (mesh + anim-only). SDR06 2026-10-22, user: "Tôi muốn chuyển nó sang joint cổ tay phải" (gun slingshot_0:
# Chest_M -> Wrist_R). The prop's world matrix is recorded every frame, the bone is re-parented in edit mode (rest
# pose kept), then re-keyed every frame to the recorded matrix; its children (drum slingshot_1) keep their locals.
#   blender -b <clip>_baked.blend --python legacy/blender/reparent_prop.py -- <take> <prop> <new_parent> <fbx> <anim_only_fbx> <out.blend>
import os
import sys

import bpy

take, prop, parent, fbx, fbx_anim, out_blend = sys.argv[sys.argv.index("--") + 1:][:6]
sc = bpy.context.scene
A = bpy.data.objects["Armature"]
act = bpy.data.actions[take]
A.animation_data.action = act
if hasattr(A.animation_data, "action_slot") and act.slots:
    A.animation_data.action_slot = act.slots[0]
f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
sc.frame_start, sc.frame_end = f0, f1
watch = [pb.name for pb in A.pose.bones]
ref, M = {}, {}
for f in range(f0, f1 + 1):
    sc.frame_set(f)
    ref[f] = {n: (A.matrix_world @ A.pose.bones[n].matrix).copy() for n in watch}
    M[f] = A.pose.bones[prop].matrix.copy()

for o in bpy.context.selected_objects:
    o.select_set(False)
A.select_set(True); bpy.context.view_layer.objects.active = A
bpy.ops.object.mode_set(mode="EDIT")
eb = A.data.edit_bones
old = eb[prop].parent.name if eb[prop].parent else None
eb[prop].use_connect = False
eb[prop].parent = eb[parent]
bpy.ops.object.mode_set(mode="POSE")
print("REPARENT", prop, old, "->", parent)

pb = A.pose.bones[prop]
pb.rotation_mode = "QUATERNION"
for p in ("location", "rotation_quaternion", "scale"):
    for i in range(4 if p == "rotation_quaternion" else 3):
        fc = act.fcurves.find(f'pose.bones["{prop}"].{p}', index=i)
        if fc:
            act.fcurves.remove(fc)
prev = None
for f in range(f0, f1 + 1):
    sc.frame_set(f)
    pb.matrix = M[f]
    bpy.context.view_layer.update()
    if prev is not None and prev.dot(pb.rotation_quaternion) < 0:
        pb.rotation_quaternion = -pb.rotation_quaternion
    prev = pb.rotation_quaternion.copy()
    for p in ("location", "rotation_quaternion", "scale"):
        pb.keyframe_insert(p, frame=f)
for fc in act.fcurves:
    if fc.data_path.startswith(f'pose.bones["{prop}"]'):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
        fc.update()
bpy.ops.object.mode_set(mode="OBJECT")

err = 0.0
for f in range(f0, f1 + 1):
    sc.frame_set(f)
    for n in watch:
        D = (A.matrix_world @ A.pose.bones[n].matrix) - ref[f][n]
        err = max(err, max(abs(x) for r in D for x in r))
print("REPARENT world matrix max diff", err)

sc.name = take
meshes = [o for o in bpy.data.objects if o.type == "MESH" and any(m.type == "ARMATURE" and m.object == A for m in o.modifiers)]
kw = dict(use_selection=True, add_leaf_bones=False, bake_anim=True, bake_anim_use_all_bones=True,
          bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False, bake_anim_force_startend_keying=True,
          bake_anim_step=1.0, bake_anim_simplify_factor=0.0, apply_unit_scale=True, use_armature_deform_only=False)
for out, types, sel in ((fbx, {"ARMATURE", "MESH"}, [A] + meshes), (fbx_anim, {"ARMATURE"}, [A])):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in sel:
        o.select_set(True)
    bpy.context.view_layer.objects.active = A
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=out, object_types=types, **kw)
    print("FBX", out, os.path.getsize(out) // 1024, "KB")
bpy.ops.wm.save_as_mainfile(filepath=out_blend, copy=True)

scr = bpy.data.scenes.new("chk"); bpy.context.window.scene = scr
bpy.ops.import_scene.fbx(filepath=fbx, automatic_bone_orientation=False)
B = next(o for o in scr.objects if o.type == "ARMATURE")
print("IMPORTED parent of", prop, "=", B.data.bones[prop].parent.name)
best = None
for shift in (0, 1):
    e = 0.0
    for f in range(f0, f1 + 1 - shift):
        scr.frame_set(f + shift)
        for n, Mw in ref[f].items():
            if n in B.pose.bones:
                e = max(e, ((B.matrix_world @ B.pose.bones[n].matrix).to_translation() - Mw.to_translation()).length)
    best = e if best is None else min(best, e)
print("FBX re-import max joint offset cm", round(best * 100, 4))
