# save_scene khong ghi de duoc file co san (tra False): xoa file cu cua v2 roi luu. Dung: exec trong Frolvy, SAVE_AS = duong dan.
import os
D = "/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_15_Night_Bat/v2_mesh_moi/"
def save(name):
    p = D + name
    if os.path.exists(p): os.remove(p)
    ok = api.save_scene(p); print("saved", name, ok, os.path.getsize(p)); return ok
