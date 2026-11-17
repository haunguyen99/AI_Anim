# Dựng Attack v6 từ pose người dùng (frame 0 của idle_v12_pose_user.fv). Chạy trên Frolvy cổng 9890.
ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/anim/attack6.py", encoding="utf8").read(), ns)
D = "/home/ngocvb/Desktop/DataHDD/Ngoc/EndlessKicker/New_PET/Pet_25_Chrono_Ouroboros/"
api.save_scene("/tmp/p25/scratch_pre_attack6.fv")
ok = api.open_scene(D + "chrono_ouroboros_idle_v12_pose_user.fv")
if not ok:
    api.save_scene("/tmp/p25/scratch_pre_attack6b.fv"); ok = api.open_scene(D + "chrono_ouroboros_idle_v12_pose_user.fv")
print("open", ok)
base = ns["ns"]["read_base"](api)
ns['build'](api, base); api.select([])
print("saved", api.save_scene(D + "chrono_ouroboros_attack_v6.fv"))
