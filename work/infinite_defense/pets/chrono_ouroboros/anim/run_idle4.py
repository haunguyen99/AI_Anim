import math
ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/anim/idle4.py").read(), ns)
D = "/home/ngocvb/Desktop/DataHDD/Ngoc/EndlessKicker/New_PET/Pet_25_Chrono_Ouroboros/"
api.open_scene(D + "chrono_ouroboros_rig_v2.fv")
S = ns['arc'](api); hv = ns['calibrate'](api, S); print("HOVER", round(hv, 3))
ns['build'](api, hv); api.select([])
print(api.save_scene(D + "chrono_ouroboros_idle_v7.fv"))
