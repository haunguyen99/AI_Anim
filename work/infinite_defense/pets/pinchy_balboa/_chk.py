import sys
for _p in (r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_auto_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\tools\frolvy_plugins\fit_controls"): sys.path.insert(0, _p)
import auto_rig as A
R=A.R
bad=0
for j in api.ls("Joint"):
    if j=="DEF_Muzzle_M": continue
    c="CTL_"+j[4:]; a=R.P(api,j); b=R.P(api,c)
    if max(abs(a[i]-b[i]) for i in range(3))>0.002: bad+=1; print("off",j,[round(v,3) for v in a],[round(v,3) for v in b])
print("control/joint mismatches:", bad)
b0=R.P(api,"DEF_Glove_L"); api.rotate("CTL_Arm1_L",0,-40,0); a=R.P(api,"DEF_Glove_L"); api.rotate("CTL_Arm1_L",0,0,0)
print("glove moved", [round(a[i]-b0[i],3) for i in range(3)])
print(api.check_rig()[:2] if api.check_rig() else "check_rig empty")
api.set_frame(1); api.set_frame(0)
print(api.save_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa\pinchy_rig.fv"))
