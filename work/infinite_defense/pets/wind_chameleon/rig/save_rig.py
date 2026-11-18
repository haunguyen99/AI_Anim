for c in api.ls("Curve"):
    if c.startswith("CTL_"):
        api.rotate(c,0,0,0); api.move(c,0,0,0)
        try: api.scale(c,1,1,1)
        except Exception: pass
print(api.save_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_16_Wind_Chameleon\wind_chameleon_rig_v3.fv"))
