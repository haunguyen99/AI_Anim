# Gan texture moi len mesh (Frolvy hien texture PNG lat doc: dung ban lat top-bottom chep canh file .fv)
import os
TEX = r"/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_13_Tiny_Chick/tex/T_Pet_tiny_chick_flipped_for_frolvy.png"
M = "Pet_Tiny_Chick"; mat = "M_Pet_Tiny_Chick"
if mat not in list(api.materials()) if callable(getattr(api, 'materials', None)) else True:
    try: api.create_material(mat)
    except Exception as e: print("create", e)
api.set_material(mat, 1.0, 1.0, 1.0, 0.0, 0.6, 0.0, 0.0, 0.0, 1.0, False)
print("tex", api.set_texture(mat, TEX), api.texture_state(mat))
api.assign_material(mat, [M]); api.select([])
