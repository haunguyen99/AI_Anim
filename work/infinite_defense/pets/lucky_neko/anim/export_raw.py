# Run in Frolvy (own port 9891) with the clip's scene open when the user says "chot": bake the DEF joints and write raw_<NAME>.fbx (unprocessed). Set NAME / FRAMES in the line above.
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_14_Lucky_Neko"
api.set_frame(1); api.set_frame(0)
defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
api.set_frame_range(0, FRAMES)
print(NAME, len(defs), "DEF joints; bake", api.bake_keys(defs, 0, FRAMES, 1, 'all', True), "export", api.export_scene(D + r"\raw_%s.fbx" % NAME, 'fbx', True, 0, FRAMES, 30))
