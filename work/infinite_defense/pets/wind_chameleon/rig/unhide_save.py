D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_16_Wind_Chameleon"
print(api.open_scene(D + r"\wind_chameleon_rig.fv"))
print(len(api.ls("Curve")), len(api.ls("Joint")))
api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(False); api.select([])
print(api.save_scene(D + r"\wind_chameleon_rig_new.fv"))
