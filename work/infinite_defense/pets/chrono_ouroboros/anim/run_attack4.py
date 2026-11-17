# Dựng Attack v4 từ pose người dùng (frame 0 của idle_v12_pose_user.fv). Chạy trên Frolvy cổng 9890.
ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/anim/attack4.py", encoding="utf8").read(), ns)
D = "/home/ngocvb/Desktop/DataHDD/Ngoc/EndlessKicker/New_PET/Pet_25_Chrono_Ouroboros/"
api.save_scene("/tmp/p25/scratch_pre_attack.fv")
print(api.open_scene(D + "chrono_ouroboros_idle_v12_pose_user.fv"))
base = ns["ns"]["read_base"](api)
ns['build'](api, base); api.select([])
print("saved", api.save_scene(D + "chrono_ouroboros_attack_v4.fv"))
