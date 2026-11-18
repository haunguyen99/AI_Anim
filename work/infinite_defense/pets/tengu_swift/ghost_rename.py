"""Frolvy still writes joints deleted/replaced earlier (ghost sets, lower ids, names DEF_*). Rename every DEF_ LimbNode whose id is below the LAST DEF_Root_M id to GHOST_*,
so fbx_ascii_keep --root DEF_Root_M finds one root. Also snaps numeric noise on joint Lcl Rotation/Scaling (Muzzle scale 1.000002) that trips fbx_add_bindpose.
usage: ghost_rename.py in.fbx out.fbx"""
import os, re, sys
TOL = float(os.environ.get("SNAP_DEG", "1e-4"))
t = open(sys.argv[1], encoding="utf-8").read()
root_ids = [int(x) for x in re.findall(r'\tModel: (\d+), "Model::DEF_Root_M", "LimbNode"', t)]
cut = max(root_ids)


def f(m):
    return m.group(0).replace("Model::DEF_", "Model::GHOST_") if int(m.group(1)) < cut else m.group(0)


t, n = re.subn(r'\tModel: (\d+), "Model::DEF_[^"]*", "LimbNode"', f, t)


def snap(m):
    v = [float(x) for x in m.group(2).split(",")]
    v = [0.0 if (m.group(1) == "Rotation" and abs(x) < TOL) else (1.0 if (m.group(1) == "Scaling" and abs(x - 1) < 1e-5) else x) for x in v]
    return 'P: "Lcl %s", "Lcl %s", "", "A",%s' % (m.group(1), m.group(1), ",".join("%.6f" % x for x in v))


t = re.sub(r'P: "Lcl (Rotation|Scaling)", "Lcl (?:Rotation|Scaling)", "", "A",([^\n]*)', snap, t)
print("models seen", n, "ghost", len(re.findall(r"Model::GHOST_", t)), "root ids", root_ids)
open(sys.argv[2], "w", encoding="utf-8", newline="").write(t)
