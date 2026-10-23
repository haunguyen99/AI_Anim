# Base FBX: joints + skinned meshes only, bind (rest) pose, no animation (SDR06 2026-10-22: "xuất giúp tôi 1 file base
# chỉ có joint và mesh"). Run on a baked blend whose hierarchy is final (e.g. *_wristR.blend: gun on Wrist_R).
#   blender -b <baked>.blend --python tools/blender/export_base.py -- <out.fbx>
import os, sys
import bpy
out = sys.argv[sys.argv.index("--") + 1]
A = bpy.data.objects["Armature"]
if A.animation_data:
    A.animation_data.action = None
for pb in A.pose.bones:
    pb.location, pb.scale = (0, 0, 0), (1, 1, 1)
    pb.rotation_quaternion, pb.rotation_euler = (1, 0, 0, 0), (0, 0, 0)
bpy.context.view_layer.update()
meshes = [o for o in bpy.data.objects if o.type == "MESH" and any(m.type == "ARMATURE" and m.object == A for m in o.modifiers)]
for o in bpy.context.selected_objects: o.select_set(False)
for o in [A] + meshes: o.select_set(True)
bpy.context.view_layer.objects.active = A
bpy.context.scene.name = os.path.splitext(os.path.basename(out))[0]
os.makedirs(os.path.dirname(out), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
                         bake_anim=False, apply_unit_scale=True, use_armature_deform_only=False)
print("BASE", out, os.path.getsize(out) // 1024, "KB, meshes", [m.name for m in meshes], "bones", len(A.data.bones))
scr = bpy.data.scenes.new("chk"); bpy.context.window.scene = scr
n0 = len(bpy.data.actions)
bpy.ops.import_scene.fbx(filepath=out, automatic_bone_orientation=False)
B = next(o for o in scr.objects if o.type == "ARMATURE")
print("CHECK bones", len(B.data.bones), "gun parent", B.data.bones["slingshot_0"].parent.name,
      "meshes", len([o for o in scr.objects if o.type == "MESH"]), "new actions", len(bpy.data.actions) - n0)
