C=[c for c in api.ls("Curve") if c.startswith("CTL_")]
for f in range(0,49):
    api.set_frame(f)
    for c in C: api.rotate(c,0,0,0); api.move(c,0,0,0)
    api.select(C); api.set_key()
api.set_frame(1); api.set_frame(0); api.select([])
mx=0
for c in C:
    for a in ("rx","ry","rz","tx","ty","tz"):
        for f in api.list_keys(c+"."+a): pass
import math
print("DEF_Head_M", api.get_attr("DEF_Head_M.ty"), api.get_attr("DEF_Arm1_R.ry"), api.get_attr("CTL_Root_M.ty"))
print(api.save_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa\pinchy_rig.fv"))
