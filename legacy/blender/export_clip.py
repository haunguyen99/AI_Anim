# Step 7 export (docs/pipeline_v2.md): bake the visual pose of the live CTRL rig onto the deform joints, export FBX for
# Unity (armature + meshes, one take), re-import and compare per frame, and save <scene>_<clip>_baked.blend with the
# baked action on the joints and the CTRL rig / constraints removed. The working scene is reopened untouched.
#   EXPORT = dict(take="EN_M11_Boss_Gaygor_Idle_Front", f0=1, f1=60,
#                 fbx=ROOT + r"/work/idle_front/export/EN_M11_Boss_Gaygor_Idle_Front.fbx",
#                 baked_blend=ROOT + r"/work/blender/boss_idle_front_baked.blend")
#   exec(open(ROOT + r"/legacy/blender/export_clip.py").read())
import os

import bpy

E = EXPORT  # noqa: F821
sc = bpy.context.scene
work = bpy.data.filepath
bpy.ops.wm.save_mainfile()
A = bpy.data.objects["Armature"]
meshes = [o for o in bpy.data.objects if o.type == "MESH" and any(m.type == "ARMATURE" and m.object == A for m in o.modifiers)]

# reference world matrices from the live rig
ref = {}
for f in range(E["f0"], E["f1"] + 1):
    sc.frame_set(f)
    ref[f] = {pb.name: (A.matrix_world @ pb.matrix).copy() for pb in A.pose.bones}

# 1. bake
for o in bpy.context.selected_objects:
    o.select_set(False)
bpy.context.view_layer.objects.active = A; A.select_set(True)
bpy.ops.object.mode_set(mode="POSE")
for b in A.data.bones:
    b.select = True
bpy.ops.nla.bake(frame_start=E["f0"], frame_end=E["f1"], only_selected=False, visual_keying=True,
                 clear_constraints=True, use_current_action=False, bake_types={"POSE"})
bpy.ops.object.mode_set(mode="OBJECT")
baked = A.animation_data.action; baked.name = E["take"]; baked.use_fake_user = True
ctrl = bpy.data.objects.get("CTRL")
if ctrl:
    bpy.data.objects.remove(ctrl, do_unlink=True)
sc.frame_start, sc.frame_end = E["f0"], E["f1"]
err = 0.0
for f in range(E["f0"], E["f1"] + 1):
    sc.frame_set(f)
    for pb in A.pose.bones:
        err = max(err, ((A.matrix_world @ pb.matrix).to_translation() - ref[f][pb.name].to_translation()).length)
print("bake vs live rig: max joint offset %.4f cm" % (err * 100))

# 2. FBX (the exporter names the single take after the scene: name it after the clip so Unity shows the right take)
os.makedirs(os.path.dirname(E["fbx"]), exist_ok=True)
sc.name = E["take"]
for o in bpy.context.selected_objects:
    o.select_set(False)
A.select_set(True)
for m in meshes:
    m.select_set(True)
bpy.context.view_layer.objects.active = A
bpy.ops.export_scene.fbx(filepath=E["fbx"], use_selection=True, object_types={"ARMATURE", "MESH"},
                         add_leaf_bones=False, bake_anim=True, bake_anim_use_all_bones=True,
                         bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False,
                         bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=0.0,
                         apply_unit_scale=True, use_armature_deform_only=False)
print("FBX", E["fbx"], "%.1f MB" % (os.path.getsize(E["fbx"]) / 1e6))

# 3. baked .blend (joints carry the keys, no CTRL)
bpy.ops.wm.save_as_mainfile(filepath=E["baked_blend"], copy=True)
print("baked blend", E["baked_blend"])

# 4. re-import the FBX into a scratch scene and compare per frame
scratch = bpy.data.scenes.new("fbx_check"); bpy.context.window.scene = scratch
bpy.ops.import_scene.fbx(filepath=E["fbx"], automatic_bone_orientation=False)
B = next(o for o in scratch.objects if o.type == "ARMATURE")
best = None
for shift in (-1, 0, 1):          # Blender's FBX importer may place the take one frame later (time origin)
    err = 0.0; n = 0
    for f in range(E["f0"], E["f1"] + 1 - abs(shift)):
        scratch.frame_set(f + shift)
        for name, M in ref[f].items():
            if name in B.pose.bones:
                err = max(err, ((B.matrix_world @ B.pose.bones[name].matrix).to_translation() - M.to_translation()).length); n += 1
    if best is None or err < best[0]:
        best = (err, shift, n)
print("FBX re-import vs live rig: max joint offset %.4f cm over %d joint-frames (frame shift %+d on import)"
      % (best[0] * 100, best[2], best[1]))

# 5. back to the untouched working scene
bpy.ops.wm.open_mainfile(filepath=work)
print("reopened", bpy.data.filepath)
