api.set_frame(15)
for n in ("CTL_Tail5_1_L_grp","CTL_Tail5_1_L","CTL_Tail5_2_L","CTL_Tail5_3_L","CTL_Tail4_1_L_grp","CTL_Tail4_1_L","CTL_Tail4_2_L"):
    print(n,[round(api.get_attr(n+"."+a),1) for a in ("rx","ry","rz","tx","ty","tz")])
print("fan",api.get_attr("CTL_TailFan.fan"))
api.set_frame(0)
