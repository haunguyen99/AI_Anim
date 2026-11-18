# Gan texture moi len mesh trong file _v2. Dat FILE (rig_v2 | idle_v2 | attack_v2) truoc khi chay. Cong 9882.
D = "/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_12_Pebble_Turtle/v2_mesh_moi/"
TEX = "/home/ngocvb/Projects/endless-kicker/Assets/Kho/Skin/mesh/Pet_new/texture/T_Pet_Pebble_Turtle.png"
path = D + "PebbleTurtle_%s.fv" % FILE
assert api.open_scene(path), "open_scene that bai"
mesh = [o for o in api.ls("Object")]
mat = "M_Pet_Pebble_Turtle"
if mat not in api.materials():
    api.create_material(mat)
    api.set_material(mat, 1.0, 1.0, 1.0, 0.0, 0.6, 0.0, 0.0, 0.0, 1.0, False)
api.set_texture(mat, TEX)
api.assign_material(mat, mesh)
print(mesh, api.texture_state(mat))
print("save", api.save_scene(path))
