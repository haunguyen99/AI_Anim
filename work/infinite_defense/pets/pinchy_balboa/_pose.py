api.set_frame(5); api.set_frame(0)
for c in api.ls("Curve"):
    if c.startswith("CTL_"): api.rotate(c,0,0,0); api.move(c,0,0,0)
R=api.rotate
R("CTL_Head_M",12,18,12); R("CTL_Root_M",8,10,-8)
for s,k in (("R",1),("L",-1)):
    R("CTL_Arm1_"+s,0,k*25,-k*10); R("CTL_Arm2_"+s,0,k*30,-k*5); R("CTL_Arm3_"+s,0,k*35,-k*4); R("CTL_Glove_"+s,0,k*10,0)
    for g in "FMB": R("CTL_Leg%s_%s"%(g,s),k*18,0,10); R("CTL_Leg%sTip_%s"%(g,s),-25,0,0)
R("CTL_BandA1_M",0,20,25); R("CTL_BandB2_M",0,10,-30)
api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])
