n=0
for j in api.ls("Joint"):
    for a in ("rx","ry","rz","tx","ty","tz","sx","sy","sz"):
        for f in list(api.list_keys(j+"."+a)): api.delete_key(j+"."+a, int(round(f))); n+=1
print("joint keys removed", n)
api.set_frame(5); api.set_frame(1); api.set_frame(0)
print([ (j, round(api.get_attr(j+".ry"),2)) for j in ("DEF_Arm1_R","DEF_Arm2_L","DEF_Head_M","DEF_Root_M")])
print(api.save_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa\pinchy_rig.fv"))
