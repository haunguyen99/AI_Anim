# Gan texture moi len mesh (Frolvy 9885). Dat TEX truoc khi exec.
M = "Pet_Wind_Chameleon"; MAT = "M_Pet_WindChameleon"
if MAT not in api.materials():
    api.create_material(MAT)
    api.set_material(MAT, 1.0, 1.0, 1.0, 0.0, 0.6, 0.0, 0.0, 0.0, 1.0, False)
api.set_texture(MAT, TEX)
sel = list(api.selection())
api.assign_material(MAT, [M]); api.select(sel)
print(api.texture_state(MAT), api.materials())
