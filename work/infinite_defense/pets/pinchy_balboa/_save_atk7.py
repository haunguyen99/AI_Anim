api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(False); api.select([]); api.look_through('persp')
api.set_frame(1); api.set_frame(0)
print(api.save_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa\pinchy_attack_v7.fv"))
