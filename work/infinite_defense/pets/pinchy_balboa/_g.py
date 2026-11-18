for s,k in (("R",1),("L",-1)):
    api.rotate("CTL_Arm1_"+s,0,k*20,-k*10); api.rotate("CTL_Arm2_"+s,0,k*25,-k*5); api.rotate("CTL_Arm3_"+s,0,k*30,-k*4); api.rotate("CTL_Glove_"+s,0,k*10,0)
api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])
