"""Build + save + export both clips in the open scene (Frolvy 9884). Run:
.venv/Scripts/python.exe -I tools/frolvy_port.py 9884 work/infinite_defense/pets/wind_chameleon/anim/make_clips.py
Variable MODE (set before exec by the wrapper) = "build" (keys only, keep scene) or "export"."""
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_16_Wind_Chameleon"
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\wind_chameleon\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = {"idle_pose": ns['pose'], "api": api}; exec(open(W + r"\attack.py").read(), g)
ALL = ns['CTLS']
def clear():
    for c in ALL:
        for a in ns['CH']:
            for f in list(api.list_keys(c + "." + a)): api.delete_key(c + "." + a, int(round(f)))
    for c in ALL:
        [api.set_attr(c + "." + a, 0.0) for a in ("rx","ry","rz","tx","ty","tz")]
        try: [api.set_attr(c + "." + a, 1.0) for a in ("sx","sy","sz")]
        except Exception: pass
def unkey_defs():
    for j in [j for j in api.ls("Joint") if j.startswith("DEF_")]:
        for a in ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"):
            for f in list(api.list_keys(j + "." + a)): api.delete_key(j + "." + a, int(round(f)))
def finish(name, n):
    api.set_frame(1); api.set_frame(0)
    print(name, 'save', api.save_scene(D + r"\wind_chameleon_%s_v3.fv" % name.lower()))
    defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
    api.set_frame_range(0, n)
    print('bake', api.bake_keys(defs, 0, n, 1, 'all', True), 'export', api.export_scene(D + r"\raw_%s.fbx" % name, 'fbx', True, 0, n, 30))
    api.set_active_layer(0)
    unkey_defs()
    for L in range(len(api.layers()) - 1, 0, -1): api.delete_layer(L)
if MODE == "idle": clear(); ns['build'](api)
elif MODE == "attack": clear(); g['build'](api)
elif MODE == "export_idle": clear(); ns['build'](api); finish("Idle", 48)
elif MODE == "export_attack": clear(); g['build'](api); finish("Attack", 30)
elif MODE == "base":
    clear(); api.set_frame(1); api.set_frame(0); api.set_frame_range(0, 1)
    print('base export', api.export_scene(D + r"\raw_Base.fbx", 'fbx', True, 0, 1, 30)); api.set_frame_range(0, 30)
