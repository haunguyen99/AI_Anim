import sys
for _p in (r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_auto_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\tools\frolvy_plugins\fit_controls"): sys.path.insert(0, _p)
import auto_rig as A
R=A.R
for c in api.ls("Curve"):
    if c.startswith("CTL_"): api.rotate(c,0,0,0); api.move(c,0,0,0) if c=="CTL_Main" else api.move(c,0,0,0)
api.set_frame(1); api.set_frame(0)
def t(ctl, j, ax, v):
    b=R.P(api,j); 
    r=[0,0,0]; r["xyz".index(ax)]=v; api.rotate(ctl,*r); a=R.P(api,j); api.rotate(ctl,0,0,0)
    print(ctl,ax,v,[round(a[i]-b[i],3) for i in range(3)])
for ax in "xyz": t("CTL_Arm1_L","DEF_Glove_L",ax,30)
for ax in "xyz": t("CTL_Arm1_R","DEF_Glove_R",ax,30)
for ax in "xyz": t("CTL_Head_M","DEF_BandB2_M",ax,30)
for ax in "xyz": t("CTL_Root_M","DEF_Head_M",ax,30)
for ax in "xyz": t("CTL_LegM_L","DEF_LegMTip_L",ax,30)
