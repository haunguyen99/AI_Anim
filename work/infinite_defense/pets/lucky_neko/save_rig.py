for c in api.ls("Curve"):
    if c.startswith("CTL_"): api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0) if c != "CTL_Main" else None
api.set_frame(3); api.set_frame(0)
api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(False); api.select([])
api.look_through('persp')
mx = 0; nondef = set(); un = 0
for o in api.ls("Object"):
    for v in list(api.mesh_data(o)['vertices']):
        w = api.vertex_weights(v); mx = max(mx, len(w)); un += abs(sum(x for _, x in w) - 1) > 0.01
        nondef.update(j for j, _ in w if not j.startswith("DEF_"))
print("max influences", mx, "non-DEF", nondef, "unnormalized", un)
print(api.check_rig())
print(api.save_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_14_Lucky_Neko\lucky_neko_rig.fv"))
