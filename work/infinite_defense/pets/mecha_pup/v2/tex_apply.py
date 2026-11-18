# Chay trong Frolvy: material M_Mecha_Pup + texture LAT DOC (Frolvy hien PNG nguoc; Unity dung ban goc). Chi hien thi.
import os
mat = 'M_Mecha_Pup'
if mat not in api.materials(): api.create_material(mat)
api.set_material(mat, 1.0, 1.0, 1.0, 0.0, 0.6, 0.0, 0.0, 0.0, 1.0, False)
print('tex', api.set_texture(mat, '/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_11_Mecha_Pup/tex/T_Pet_mecha_pup_flipV.png'), api.texture_state(mat))
api.select(['Pet_Mecha_Pup']); print('assign', api.assign_material(mat, ['Pet_Mecha_Pup'])); api.select([])
