print(api.import_file(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\wind_chameleon\Pet_Wind_Chameleon.fbx"))
for o in ("chameleon","Chameleon_tonge"): api.rotate(o, -90, 0, 0)
api.select(["chameleon","Chameleon_tonge"]); print(api.freeze_transform()); api.select([])
