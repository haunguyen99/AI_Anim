for c in api.ls("Curve"):
    if c.startswith("CTL_"):
        api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
api.select(list(api.ls("Curve")) + list(api.ls("Joint"))); api.hide(False); api.select([])
print(api.save_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_19_Kabuto_Striker\kabuto_striker_rig.fv"))
