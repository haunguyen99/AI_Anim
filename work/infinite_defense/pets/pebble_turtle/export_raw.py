"""Pebble Turtle: gan lai texture (tex/ trong thu muc Pet) + xuat FBX tho vao /tmp/pet12 (Frolvy cong 9882).
Dat FILE = 'rig' | 'idle' | 'attack' truoc khi chay. Cua so Frolvy phai moi khoi dong (open_scene khong mo khi scene dang do)."""
P = "/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_12_Pebble_Turtle/"
TEX = P + "tex/T_Pet_Pebble_Turtle.png"
OUT = "/tmp/pet12/"
path = P + "PebbleTurtle_%s.fv" % FILE
assert api.open_scene(path), "open_scene that bai"
mat = "M_Pet_Pebble_Turtle"
api.set_texture(mat, TEX)
api.assign_material(mat, list(api.ls("Object")))
print("texture", api.texture_state(mat), "save", api.save_scene(path))
if FILE == "rig":
    api.select([]); api.reset_transforms(all_controls=True)
    api.set_frame(1); api.set_frame(0); api.set_frame_range(0, 1)
    print("export base", api.export_scene(OUT + "raw_Base.fbx", "fbx", True, 0, 1, 30))
else:
    f0, n = api.frame_range()
    api.set_frame(1); api.set_frame(0)
    defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
    print(FILE, "range", f0, n, "joints", len(defs), "bake", api.bake_keys(defs, 0, n, 1, "all", True),
          "export", api.export_scene(OUT + "raw_%s.fbx" % FILE.capitalize(), "fbx", True, 0, n, 30))
