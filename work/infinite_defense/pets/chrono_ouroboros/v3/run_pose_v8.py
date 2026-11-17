# Idle v8 - POSE F0 theo concept (vòng ouroboros). Chỉ 1 key ở frame 0, chưa có chuyển động.
ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/v3/ring.py").read(), ns)
D = "/home/ngocvb/Desktop/DataHDD/Ngoc/EndlessKicker/New_PET/Pet_25_Chrono_Ouroboros/"
api.save_scene("/tmp/p25/scratch_pre.fv"); api.open_scene(D + "chrono_ouroboros_rig_v3.fv")
W = {r['name']: r['world'] for r in api.joint_info()}
P = ns['ring_pose'](W); ns['apply'](api, P); api.set_frame(3); api.set_frame(0)
ys = []
for o in ("Pet_chrono_ouroboros", "hourglass"): ys += api.mesh_data(o, True)['positions'][1::3]
P["CTL_Root_M"][4] += 0.11 - min(ys); ns['apply'](api, P); api.set_frame(3); api.set_frame(0)
print("Root ty", P["CTL_Root_M"][4])
api.set_frame_range(0, 72); api.set_frame(0); api.select(ns['CTLS']); api.set_key(); api.select([])
print(api.save_scene(D + "chrono_ouroboros_idle_v8_pose.fv"))
