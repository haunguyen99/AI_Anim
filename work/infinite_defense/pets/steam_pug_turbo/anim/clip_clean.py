# Dung lai clip, xoa key thua (simplify_keys, dung sai nho), kiem mesh khong doi, luu .fv, bake DEF + simplify, xuat raw_*.fbx.
# MODE = "attack" | "idle"  (dat o dau file chay).  Chay trong Frolvy 9888 mo rig.fv.
import math
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_22_Steam_Pug_Turbo"
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\steam_pug_turbo\anim"
TOL = dict(translate=0.0003, rotate=0.03, scale=0.001, attribute=0.01)
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = {"idle_pose": ns['pose'], "api": api}; exec(open(W + r"\attack.py").read(), g)
ALL = ns['CTLS']; O = api.ls("Object")[0]
def clear(n):
    for c in ALL:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try:
                for f in list(api.list_keys(c + "." + a)):
                    if f > n: api.delete_key(c + "." + a, int(round(f)))
            except Exception: pass
def nkeys(nodes):
    n = 0
    for c in nodes:
        for a in ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"):
            try: n += len(api.list_keys(c + "." + a))
            except Exception: pass
    return n
def snap(n):
    out = []
    for f in range(0, n + 1):
        api.set_frame(f); out.append(api.mesh_data(O, True)['positions'])
    api.set_frame(1); api.set_frame(0); return out
if MODE == "attack": N = 30; clear(30); g['build'](api); tag = "Attack"
else: N = 48; ns['build'](api); tag = "Idle"
api.set_frame_range(0, N)
before = snap(N); k0 = nkeys(ALL)
removed = api.simplify_keys(ALL, 0, N, **TOL)
after = snap(N); k1 = nkeys(ALL)
dev = max(max(abs(a - b) for a, b in zip(p, q)) for p, q in zip(before, after))
print(tag, "keys", k0, "->", k1, "removed", removed, "| max mesh deviation %.4f m (%.2f cm)" % (dev, dev * 100))
if dev > 0.002: print("!! LECH LON, khong luu"); raise SystemExit
api.set_frame(1); api.set_frame(0)
print("save", api.save_scene(D + r"\steam_pug_turbo_%s_c1.fv" % tag.lower()))
defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
print("bake", api.bake_keys(defs, 0, N, 1, 'all', True), "DEF keys", nkeys(defs), end=" -> ")
print(api.simplify_keys(defs, 0, N, **TOL), nkeys(defs))
print("export", api.export_scene(D + r"\raw_%s.fbx" % tag, 'fbx', True, 0, N, 30))
api.set_active_layer(0)
for L in range(len(api.layers()) - 1, 0, -1): api.delete_layer(L)
