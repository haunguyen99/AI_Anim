import sys
for _p in (r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_auto_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_rig\scripts"): sys.path.insert(0, _p)
import auto_rig as A
api.set_frame(1); api.set_frame(0)
for j in ("DEF_Arm2_L","DEF_Arm3_L","DEF_Glove_L"): print(j,[round(v,3) for v in A.R.P(api,j)])
