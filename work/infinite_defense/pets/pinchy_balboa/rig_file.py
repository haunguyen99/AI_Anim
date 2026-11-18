for n in list(api.ls("Object")): api.delete_node(n)
api.import_file(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa\_orig\Pet_Pinchy_Balboa_mesh_original.fbx")
o = api.ls("Object"); assert len(o) == 1, o
api.rename(o[0], "Pet_Pinchy_Balboa")
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\pinchy_balboa"
exec(open(W + r"\rig_build.py").read())
exec(open(W + r"\rig_skin.py").read())
api.select(list(api.ls('Curve')) + list(api.ls('Joint'))); api.hide(False); api.select([])
api.set_frame(1); api.set_frame(0)
import sys
for _p in (r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_auto_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\tools\frolvy_plugins\fit_controls"): sys.path.insert(0, _p)
import auto_rig as A
for j in ("DEF_Arm1_L", "DEF_Glove_L", "DEF_Glove_R", "DEF_Head_M"): print(j, [round(v, 3) for v in A.R.P(api, j)])
