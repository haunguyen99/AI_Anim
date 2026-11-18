"""Chi dung lai Attack: xoa key, dung, luu tiny_chick_attack_new.fv, bake DEF, xuat raw_Attack.fbx (Frolvy 9882)."""
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_13_Tiny_Chick"
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\tiny_chick\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = {"idle_pose": ns['pose'], "api": api}; exec(open(W + r"\attack.py").read(), g)
for j in list(api.ls('Joint')) + list(api.ls('Curve')):
    for a in ('tx','ty','tz','rx','ry','rz','sx','sy','sz'):
        for f in list(api.list_keys(j + '.' + a)): api.delete_key(j + '.' + a, int(round(f)))
api.select([]); api.reset_transforms(all_controls=True); api.set_frame(5); api.set_frame(0)
g['build'](api); api.set_frame(1); api.set_frame(0)
print('save', api.save_scene(D + r"\tiny_chick_attack_new.fv"))
defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
api.set_frame_range(0, 30)
print('bake', api.bake_keys(defs, 0, 30, 1, 'all', True), 'export', api.export_scene(D + r"\raw_Attack.fbx", 'fbx', True, 0, 30, 30))
api.set_active_layer(0)
for L in range(len(api.layers()) - 1, 0, -1): api.delete_layer(L)
