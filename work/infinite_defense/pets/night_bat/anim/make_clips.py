"""Build Idle/Attack in the open scene (Frolvy 9883), save .fv + export raw FBX. Run:
.venv/Scripts/python.exe -I tools/frolvy_port.py 9883 work/infinite_defense/pets/night_bat/anim/make_clips.py   (mode set by MODE global: idle|attack|base)"""
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_15_Night_Bat"
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\night_bat\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = {"idle_pose": ns['pose'], "api": api}; exec(open(W + r"\attack.py").read(), g)
ALL = ns['CTLS']
def clear(n=48):
    """never empty a curve (breaks rotate): only drop keys beyond frame n; the build overwrites 0..n"""
    for c in ALL:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            for f in list(api.list_keys(c + "." + a)):
                if f > n: api.delete_key(c + "." + a, int(round(f)))
def finish(name, n):
    api.set_frame(1); api.set_frame(0)
    print(name, 'save', api.save_scene(D + r"\night_bat_%s_new.fv" % name.lower()))
    defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
    api.set_frame_range(0, n)
    print('bake', api.bake_keys(defs, 0, n, 1, 'all', True), 'export', api.export_scene(D + r"\raw_%s.fbx" % name, 'fbx', True, 0, n, 30))
    api.set_active_layer(0)
    for L in range(len(api.layers()) - 1, 0, -1): api.delete_layer(L)
clear(); ns['build'](api); finish("Idle", 48)
clear(30); g['build'](api); finish("Attack", 30)
# Base: bind pose (all controls 0) held on frame 0..30 keys; fbx_strip_anim removes the clip afterwards
api.set_frame_range(0, 30)
for f in range(0, 31):
    api.set_frame(f)
    for c in ALL: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    api.select(ALL); api.set_key()
api.set_frame(1); api.set_frame(0); api.set_frame_range(0, 1)
print('base export', api.export_scene(D + r"\raw_Base.fbx", 'fbx', True, 0, 1, 30))
api.set_frame_range(0, 30)
