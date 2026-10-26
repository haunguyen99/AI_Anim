# FBX with armature + animation only (no meshes), from a baked .blend made by export_clip.py:
#   blender -b <scene>_baked.blend --python tools/blender/export_skeleton_only.py -- <take> <out.fbx>
import bpy, sys, os
take, out = sys.argv[sys.argv.index("--") + 1:][:2]
A = bpy.data.objects["Armature"]
act = bpy.data.actions.get(take)
A.animation_data.action = act
sc = bpy.context.scene; sc.name = take
sc.frame_start, sc.frame_end = int(act.frame_range[0]), int(act.frame_range[1])
for o in bpy.context.selected_objects: o.select_set(False)
A.select_set(True); bpy.context.view_layer.objects.active = A
os.makedirs(os.path.dirname(out), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={"ARMATURE"}, add_leaf_bones=False,
                         bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=False,
                         bake_anim_use_all_actions=False, bake_anim_force_startend_keying=True, bake_anim_step=1.0,
                         bake_anim_simplify_factor=0.0, apply_unit_scale=True, use_armature_deform_only=False)
print("SKEL", out, os.path.getsize(out) // 1024, "KB", sc.frame_start, sc.frame_end)
