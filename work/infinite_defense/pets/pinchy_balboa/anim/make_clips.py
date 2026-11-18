"""Build Idle/Attack in the open scene (Frolvy 9885), save .fv + export raw FBX. Mode: MODE global (idle|attack|base) set by caller via prefix line."""
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa"
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\pinchy_balboa\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = {"idle_pose": ns['pose'], "api": api}; exec(open(W + r"\attack.py").read(), g)
ALL = ns['CTLS']
def clear(n):
    for c in ALL:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            for f in list(api.list_keys(c + "." + a)):
                if f > n: api.delete_key(c + "." + a, int(round(f)))
def finish(name, n):
    api.set_frame(1); api.set_frame(0)
    print(name, 'save', api.save_scene(D + r"\pinchy_%s_new.fv" % name.lower()))
    defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
    api.set_frame_range(0, n)
    print('bake', api.bake_keys(defs, 0, n, 1, 'all', True), 'export', api.export_scene(D + r"\raw_%s.fbx" % name, 'fbx', True, 0, n, 30))
    api.set_active_layer(0)
    for L in range(len(api.layers()) - 1, 0, -1): api.delete_layer(L)
