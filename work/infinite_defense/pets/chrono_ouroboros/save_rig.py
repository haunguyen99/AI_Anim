for c in api.ls("Curve"):
    if c.startswith("CTL_"): api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0) if c != "CTL_Main" else None
api.set_frame(3); api.set_frame(0)
api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(False); api.select([])
api.look_through('persp')
print(api.check_rig())
print(api.save_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_25_Chrono_Ouroboros\chrono_ouroboros_rig.fv"))
