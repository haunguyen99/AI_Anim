# Trong Frolvy: mo rig_v2, ap anim cu (thu vien wcv2_<TAG>) len cac control, dat range/infinity, so gia tri moi frame voi ban cu, luu <tag>_v2.fv. Dat TAG, OUT truoc.
import json, time
D = "/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_16_Wind_Chameleon/v2_mesh_moi/"
old = json.load(open("/tmp/wc_%s_vals.json" % TAG))
api.save_scene("/tmp/wc_scratch_%d.fv" % int(time.time() * 1000))
print("open", api.open_scene(D + "wind_chameleon_rig_v2.fv"))
f0, f1 = old["range"]
api.set_frame_range(int(f0), int(f1))
nodes = list(old["keyed"].keys())
api.select(nodes)
print("apply", api.apply_anim("wcv2_" + TAG, int(f0), "replace", nodes))
api.select([])
for p, inf in old["inf"].items():
    api.set_infinity(p, inf[0], inf[1])
bad = 0; worst = 0.0; wpath = ""
for f in range(int(f0), int(f1) + 1):
    api.set_frame(f)
    for p, v in old["vals"][str(f)].items():
        nv = api.get_attr(p); d = abs(nv - v)
        if d > 1e-3: bad += 1
        if d > worst: worst, wpath = d, "%s f%d" % (p, f)
print("so voi ban cu: kenh lech >1e-3:", bad, "lech max", round(worst, 5), wpath)
api.set_frame(int(f0))
for c in api.ls("Curve"): pass
api.select(list(api.ls("Curve")) + list(api.ls("Joint"))); api.hide(False); api.select([])
print(api.save_scene(D + OUT))
