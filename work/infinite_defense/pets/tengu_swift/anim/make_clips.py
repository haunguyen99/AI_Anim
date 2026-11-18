D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_18_Tengu_Swift"
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\tengu_swift\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = {"api": api}; exec(open(W + r"\attack.py").read(), g)
ALL = ns['CTLS']
def clear(n):
    for c in ALL:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            for f in list(api.list_keys(c + "." + a)):
                if f > n: api.delete_key(c + "." + a, int(round(f)))
def finish(name, n):
    api.set_frame(1); api.set_frame(0)
    print(name, 'save', api.save_scene(D + r"\tengu_swift_%s.fv" % name.lower()))
    defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
    api.set_frame_range(0, n)
    print('bake', api.bake_keys(defs, 0, n, 1, 'all', True), 'export', api.export_scene(D + r"\raw_%s.fbx" % name, 'fbx', True, 0, n, 30))
    api.set_active_layer(0)
    for L in range(len(api.layers()) - 1, 0, -1): api.delete_layer(L)
clear(48); ns['build'](api); ns['hold_fix'](api, 48); finish("Idle", 48)
clear(30); g['build'](api, ns['pose'], ns['CTLS'], ns['apply']); ns['hold_fix'](api, 30); finish("Attack", 30)
api.set_frame_range(0, 30)
for f in range(0, 31):
    api.set_frame(f)
    for c in ALL: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    api.select(ALL); api.set_key()
api.set_frame(1); api.set_frame(0); api.set_frame_range(0, 1)
print('base export', api.export_scene(D + r"\raw_Base.fbx", 'fbx', True, 0, 1, 30))
api.set_frame_range(0, 30)
