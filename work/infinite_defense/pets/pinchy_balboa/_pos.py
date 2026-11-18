import sys
for _p in (r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_auto_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\tools\frolvy_plugins\fit_controls"): sys.path.insert(0, _p)
import auto_rig as A
R=A.R
api.set_frame(1); api.set_frame(0)
for j in ("DEF_Root_M","DEF_Head_M","DEF_Arm1_L","DEF_Arm2_L","DEF_Glove_L","DEF_BandB2_M","DEF_LegFTip_R"):
    print(j,[round(v,3) for v in R.P(api,j)])
for c in ("CTL_Root_M","CTL_Arm1_L","CTL_Glove_L","CTL_Main"):
    print(c,[round(v,3) for v in R.P(api,c)])
print(api.ls("Group")[:8])
print("---")
for n in ("CTL_Arm1_L_grp","CTL_Arm1_L","CTL_Root_M","CTL_Root_M_grp","CTL_Main_grp"):
    print(n,[round(v,3) for v in R.P(api,n)], [round(api.get_attr(n+"."+a),3) for a in ("tx","ty","tz","rx","ry","rz","sx","sy","sz")])
