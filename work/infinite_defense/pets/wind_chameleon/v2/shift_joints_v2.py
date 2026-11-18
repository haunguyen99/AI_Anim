# Dich joint + nhom control cho khop hinh khoi mesh moi (chay trong Frolvy 9885, rig khong co key, moi control = 0)
# Luoi: +0.099 theo z (mesh moi luoi z .316-.735, cu .216-.636). Mat: tam cau moi (+-.21,.315,.303), cu (+-.24,.335,.30).
# LUU Y: api.move la toa do CUC BO theo cha (cha = Head, bind khong xoay) -> dat = dich the gioi - vi tri Head.
def pos(n): return api.world_matrix(n)[12:15]
HEAD = (0.0, 0.45, 0.22)
targets = {("DEF_Tongue1_M", "CTL_Tongue1_M_grp"): (0.0, 0.33, 0.339)}
for s, sx in (("L", 1), ("R", -1)):
    targets[("DEF_Eye_" + s, "CTL_Eye_%s_grp" % s)] = (0.21 * sx, 0.315, 0.303)
for (j, g), w in targets.items():
    loc = (w[0] - HEAD[0], w[1] - HEAD[1], w[2] - HEAD[2])
    api.move(j, *loc); api.move(g, *loc)
for n in ("DEF_Tongue1_M", "DEF_Tongue2_M", "DEF_Tongue3_M", "DEF_Tongue4_M", "DEF_Muzzle_M", "CTL_Tongue1_M", "CTL_Tongue4_M", "DEF_Eye_L", "CTL_Eye_L", "DEF_Eye_R", "CTL_Eye_R", "DEF_Head_M", "CTL_Head_M"):
    print(n, [round(x, 3) for x in pos(n)])
