# blender -b work/blender/boss_walk.blend --python work/pose_lab/fbx/make_template.py
# Template: anim-only FBX of the Walk armature (frames 1..3 baked) exported exactly like tools/blender/export_skeleton_only.py
import bpy, os
A = bpy.data.objects["Armature"]; sc = bpy.context.scene
exec(open(r"E:/AI Animation/work/walk/walk_pose.py").read())
done()
sc.frame_start, sc.frame_end = 1, 3
for o in bpy.context.selected_objects: o.select_set(False)
bpy.context.view_layer.objects.active = A; A.select_set(True)
bpy.ops.object.mode_set(mode="POSE")
for b in A.data.bones: b.select = True
bpy.ops.nla.bake(frame_start=1, frame_end=3, only_selected=False, visual_keying=True, clear_constraints=True, use_current_action=False, bake_types={"POSE"})
bpy.ops.object.mode_set(mode="OBJECT")
A.animation_data.action.name = "tmpl"
sc.name = "tmpl"
out = r"E:/AI Animation/work/pose_lab/fbx/template_walk.fbx"
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={"ARMATURE"}, add_leaf_bones=False,
    bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False,
    bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=0.0, apply_unit_scale=True, use_armature_deform_only=False)
print("TMPL", out, os.path.getsize(out))
