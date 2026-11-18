for c in api.ls("Curve"):
    if c.startswith("CTL_"): api.rotate(c,0,0,0); api.move(c,0,0,0)
api.set_frame(5); api.set_frame(0)
print(api.save_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa\pinchy_rig_skin_user.fv"))
