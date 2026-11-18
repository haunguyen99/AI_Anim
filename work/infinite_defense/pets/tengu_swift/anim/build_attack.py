W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\tengu_swift\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = {"api": api}; exec(open(W + r"\attack.py").read(), g)
for c in ns['CTLS']:
    for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
        try: api.set_infinity(c + "." + a, "constant", "constant")
        except Exception: pass
        for f in list(api.list_keys(c + "." + a)):
            if f > 30: api.delete_key(c + "." + a, int(round(f)))
g['build'](api, ns['pose'], ns['CTLS'], ns['apply']); print("attack built")
ns['hold_fix'](api, 30); print("hold fixed")
