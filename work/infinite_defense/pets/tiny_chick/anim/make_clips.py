"""Build + save + export both clips in the open scene (Frolvy 9882). Run:
.venv/Scripts/python.exe -I tools/frolvy_port.py 9882 work/infinite_defense/pets/tiny_chick/anim/make_clips.py"""
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_13_Tiny_Chick"
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\tiny_chick\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = {"idle_pose": ns['pose'], "api": api}; exec(open(W + r"\attack.py").read(), g)
ALL = ns['CTLS']
def clear():
    for c in ALL:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            for f in list(api.list_keys(c + "." + a)): api.delete_key(c + "." + a, int(round(f)))
    for c in ALL:
        api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
def finish(name, n):
    api.set_frame(1); api.set_frame(0)
    print(name, 'save', api.save_scene(D + r"\tiny_chick_%s_new.fv" % name.lower()))
    defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
    api.set_frame_range(0, n)
    print('bake', api.bake_keys(defs, 0, n, 1, 'all', True), 'export', api.export_scene(D + r"\raw_%s.fbx" % name, 'fbx', True, 0, n, 30))
    api.set_active_layer(0)
    for L in range(len(api.layers()) - 1, 0, -1): api.delete_layer(L)
clear(); ns['build'](api); finish("Idle", 48)
clear(); g['build'](api); finish("Attack", 30)
# Base: bind pose, no keys
clear(); api.set_frame(1); api.set_frame(0); api.set_frame_range(0, 1)
print('base export', api.export_scene(D + r"\raw_Base.fbx", 'fbx', True, 0, 1, 30))
api.set_frame_range(0, 30)
