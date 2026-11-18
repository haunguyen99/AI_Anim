api.rename("Pet_Pinchy_Balboa_mesh_original1", "Pet_Pinchy_Balboa"); print(api.ls("Object"))
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\pinchy_balboa\rig_build.py").read())
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\pinchy_balboa\rig_skin.py").read())
print(sorted(api.ls("Joint"))[:3], len(api.ls("Joint")))
