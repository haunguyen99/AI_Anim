# Chay trong Frolvy 9888 khi nguoi dung noi "chot": dung lai Attack / Idle / Base tu script, bake DEF, xuat raw_*.fbx (chua xu ly).
# MODE = "attack" | "idle" | "base"  (dat o dau file chay)
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_22_Steam_Pug_Turbo"
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\steam_pug_turbo\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = {"idle_pose": ns['pose'], "api": api}; exec(open(W + r"\attack.py").read(), g)
ALL = ns['CTLS']
def clear(n):
    for c in ALL:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try:
                for f in list(api.list_keys(c + "." + a)):
                    if f > n: api.delete_key(c + "." + a, int(round(f)))
            except Exception: pass
def finish(name, n):
    api.set_frame(1); api.set_frame(0)
    defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
    api.set_frame_range(0, n)
    print(name, 'bake', api.bake_keys(defs, 0, n, 1, 'all', True), 'export', api.export_scene(D + r"\raw_%s.fbx" % name, 'fbx', True, 0, n, 30))
    api.set_active_layer(0)
    for L in range(len(api.layers()) - 1, 0, -1): api.delete_layer(L)
if MODE == "attack":
    clear(30); g['build'](api); finish("Attack", 30)
elif MODE == "idle":
    ns['build'](api); finish("Idle", 48)
else:
    # Base: bind pose (moi control = 0) giu key 0 tren frame 0..30; fbx_strip_anim bo clip sau
    api.set_frame_range(0, 30)
    for f in range(0, 31):
        api.set_frame(f)
        for c in ALL: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
        api.select(ALL); api.set_key()
    api.set_frame(1); api.set_frame(0); api.set_frame_range(0, 1)
    print('base export', api.export_scene(D + r"\raw_Base.fbx", 'fbx', True, 0, 1, 30))
    api.set_frame_range(0, 30)
