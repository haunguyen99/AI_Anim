exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\pinchy_balboa\anim\make_clips.py").read())
print(api.layers())
nk=0
for j in api.ls("Joint"):
    for a in ("rx","ry","rz","tx","ty","tz"):
        for f in list(api.list_keys(j+"."+a)): api.delete_key(j+"."+a, int(round(f))); nk+=1
print("joint keys removed", nk)
api.set_frame_range(0, 30)
for f in range(0, 31):
    api.set_frame(f)
    for c in ALL: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    api.select(ALL); api.set_key()
api.set_frame(5); api.set_frame(1); api.set_frame(0); api.set_frame_range(0, 1)
import sys
for j in ("DEF_Head_M","DEF_Arm1_R","DEF_Root_M"): print(j, api.get_attr(j+".rx"), api.get_attr(j+".ry"), api.get_attr(j+".rz"), api.get_attr(j+".ty"))
print('base export', api.export_scene(D + r"\raw_Base.fbx", 'fbx', True, 0, 1, 30))
api.set_frame_range(0, 48)
