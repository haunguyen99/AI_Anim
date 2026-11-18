# Replace the mesh objects with a fresh import of the source FBX (Y-up, face +Z). The rig (joints/controls) is untouched. Then run rig_split_ears.py + rig_skin.py.
import re
for o in [o for o in api.ls("Object") if o.startswith("Pet_Night_Bat")]:
    try: api.delete_node(o)
    except Exception as e: print("del", o, e)
before = set(api.ls("Object"))
print(api.import_file(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\night_bat\Pet_Night_Bat.fbx"))
new = [o for o in api.ls("Object") if o not in before]
print("imported", new)
if new[0] != "Pet_Night_Bat": print(api.rename(new[0], "Pet_Night_Bat"))
api.rotate("Pet_Night_Bat", -90, 0, 0); api.select(["Pet_Night_Bat"]); print(api.freeze_transform()); api.select([])
print(api.ls("Object"))
