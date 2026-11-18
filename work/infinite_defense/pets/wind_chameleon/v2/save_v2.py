# luu: hien control + joint, ve control ve 0, luu vao thu muc v2_mesh_moi. Dat NAME truoc khi exec.
import sys
D = "/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_16_Wind_Chameleon/v2_mesh_moi/"
api.select(list(api.ls("Curve")) + list(api.ls("Joint"))); api.hide(False); api.select([])
print(api.save_scene(D + NAME))
