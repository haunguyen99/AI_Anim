# Dựng Attack v5 (rồng quay 1 vòng, có sức sống) từ pose người dùng (frame 0 của idle_v12_pose_user.fv). Chạy trên Frolvy cổng 9890.
import json
ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/anim/attack5.py", encoding="utf8").read(), ns)
D = "/home/ngocvb/Desktop/DataHDD/Ngoc/EndlessKicker/New_PET/Pet_25_Chrono_Ouroboros/"
api.save_scene("/tmp/p25/scratch_pre_attack5.fv")
ok = api.open_scene(D + "chrono_ouroboros_idle_v12_pose_user.fv")
if not ok:
    api.save_scene("/tmp/p25/scratch_pre_attack5b.fv"); ok = api.open_scene(D + "chrono_ouroboros_idle_v12_pose_user.fv")
print("open", ok)
base = ns['ns']['read_base'](api)
ref = json.loads(open("/tmp/p25/base.json").read())
print("base khớp pose người dùng:", max(abs(base[c][i] - ref[c][i]) for c in ref for i in range(6)) < 1e-3)
ns['build'](api, base); api.select([])
print("saved", api.save_scene(D + "chrono_ouroboros_attack_v5.fv"))
