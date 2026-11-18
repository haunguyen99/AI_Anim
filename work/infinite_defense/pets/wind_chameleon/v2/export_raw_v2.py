# Trong Frolvy 9885: mo file .fv da gop -> xuat raw FBX (Base 0-1 o bind pose; Idle 0-48; Attack 0-30). KHONG luu scene sau khi bake. Dat KIND truoc.
import time
P = "/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_16_Wind_Chameleon/"
T = "/home/ngocvb/Projects/AI_animation/work/infinite_defense/pets/wind_chameleon/fbx_tmp/"
api.save_scene("/tmp/wc_scratch_%d.fv" % int(time.time() * 1000))
src = {"Base": "wind_chameleon_rig.fv", "Idle": "wind_chameleon_idle.fv", "Attack": "wind_chameleon_attack.fv"}[KIND]
print("open", api.open_scene(P + src), api.texture_state("M_Pet_WindChameleon"))
n = {"Base": 1, "Idle": 48, "Attack": 30}[KIND]
api.set_frame(1); api.set_frame(0)
defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
if KIND != "Base":
    api.set_frame_range(0, n)
    print("bake", api.bake_keys(defs, 0, n, 1, "all", True))
else:
    api.set_frame_range(0, 1)
print("export", api.export_scene(T + "raw_%s.fbx" % KIND, "fbx", True, 0, n, 30), len(defs), "DEF")
