# Trong Frolvy: doc anim cua scene dang mo -> /tmp/wc_<TAG>_vals.json (gia tri moi kenh co key, moi frame) + save_anim vao thu vien (ten wcv2_<TAG>). Dat TAG, SRC truoc.
import json
import time; api.save_scene("/tmp/wc_scratch_%d.fv" % int(time.time()*1000))
print("open", api.open_scene(SRC))
f0, f1 = api.frame_range()
ATT = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")
keyed = {}
for n in api.ls("Curve"):
    for a in ATT:
        k = api.list_keys(n + "." + a)
        if k: keyed.setdefault(n, {})[a] = [float(x) for x in k]
vals = {}
for f in range(int(f0), int(f1) + 1):
    api.set_frame(f)
    vals[f] = {n + "." + a: api.get_attr(n + "." + a) for n in keyed for a in keyed[n]}
json.dump(dict(range=[f0, f1], keyed=keyed, vals=vals, inf={n + "." + a: list(api.infinity(n + "." + a)) for n in keyed for a in keyed[n]}), open("/tmp/wc_%s_vals.json" % TAG, "w"))
api.set_frame(int(f0))
api.select(list(keyed.keys()))
print(api.save_anim("wcv2_" + TAG, int(f0), int(f1)), "nodes", len(keyed), "range", f0, f1, "layers", api.layers(), "inf", sorted(set(map(str, [tuple(api.infinity(n + "." + a)) for n in keyed for a in keyed[n]]))))
api.select([])
