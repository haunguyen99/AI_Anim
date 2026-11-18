"""Dung lai Idle + Attack cu tren rig_v2 (mesh moi): chay trong Frolvy 9883 khi dang mo tiny_chick_rig_v2.fv. Khong xuat FBX."""
D = "/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_13_Tiny_Chick/v2_mesh_moi/"
W = "/home/ngocvb/Projects/AI_animation/work/infinite_defense/pets/tiny_chick/anim/"
ns = {}; exec(open(W + "idle.py").read(), ns)
g = {"idle_pose": ns['pose'], "api": api}; exec(open(W + "attack.py").read(), g)
ALL = ns['CTLS']
def clear():
    for j in list(api.ls('Joint')) + list(api.ls('Curve')):
        for a in ('tx','ty','tz','rx','ry','rz','sx','sy','sz'):
            for f in list(api.list_keys(j + '.' + a)): api.delete_key(j + '.' + a, int(round(f)))
    api.select([]); api.reset_transforms(all_controls=True); api.set_frame(5); api.set_frame(0)
def finish(name, n):
    api.set_frame(1); api.set_frame(0); api.set_frame_range(0, n)
    print(name, 'save', api.save_scene(D + "tiny_chick_%s_v2.fv" % name.lower()))
clear(); ns['build'](api); finish("Idle", 48)
clear(); g['build'](api); finish("Attack", 30)
