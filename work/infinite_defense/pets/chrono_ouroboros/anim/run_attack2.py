ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/anim/attack2.py").read(), ns)
D = "/home/ngocvb/Desktop/DataHDD/Ngoc/EndlessKicker/New_PET/Pet_25_Chrono_Ouroboros/"
api.open_scene(D + "chrono_ouroboros_rig_v2.fv")
HV = 0.392
ns['build'](api, HV); api.select([])
print(api.save_scene(D + "chrono_ouroboros_attack_v2.fv"))
