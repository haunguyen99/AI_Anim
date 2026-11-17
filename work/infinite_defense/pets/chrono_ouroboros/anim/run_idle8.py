# Dựng Idle v14 từ pose người dùng đã sửa. Chạy trên Frolvy (cổng 9890).
import json
ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/anim/idle6.py", encoding="utf8").read(), ns)
D = "/home/ngocvb/Desktop/DataHDD/Ngoc/EndlessKicker/New_PET/Pet_25_Chrono_Ouroboros/"
api.save_scene("/tmp/p25/scratch_pre_build.fv")
print(api.open_scene(D + "chrono_ouroboros_idle_v12_pose_user.fv"))
base = ns['read_base'](api)
fr = ns['build'](api, base)
api.select([])
print("saved", api.save_scene(D + "chrono_ouroboros_idle_v14.fv"))
