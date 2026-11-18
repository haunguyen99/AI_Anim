# import FBX, xoay -90 X (Y len, mat +Z), freeze
print(api.import_file(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\tiny_chick\Pet_Tiny_Chick.fbx"))
api.rotate("Pet_Tiny_Chick", -90, 0, 0); api.select(["Pet_Tiny_Chick"]); print(api.freeze_transform()); api.select([])
