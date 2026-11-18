exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\pinchy_balboa\anim\make_clips.py").read())
api.set_frame_range(0, 30); clear(30); g['build'](api)
import sys
for _p in (r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_auto_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_rig\scripts"): sys.path.insert(0, _p)
import auto_rig as A
for f in (11,12,13,14,15,16,17,19,21,30):
    api.set_frame(1); api.set_frame(f)
    print(f, {j[4:]:[round(v,2) for v in A.R.P(api,j)] for j in ("DEF_Arm1_R","DEF_Arm3_R","DEF_Glove_R","DEF_Muzzle_M","DEF_Head_M")})
api.set_frame(1); api.set_frame(0)
