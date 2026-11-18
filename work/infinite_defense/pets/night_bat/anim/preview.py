# preview.py <idle|attack>: build the clip in the open scene (no save/export) for contact sheets
import sys
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\night_bat\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = {"idle_pose": ns['pose'], "api": api}; exec(open(W + r"\attack.py").read(), g)
MODE = globals().get("MODE", "attack")
n = 48 if MODE == "idle" else 30
for c in ns['CTLS']:
    for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
        for f in list(api.list_keys(c + "." + a)):
            if f > n: api.delete_key(c + "." + a, int(round(f)))
(ns if MODE == "idle" else g)['build'](api)
