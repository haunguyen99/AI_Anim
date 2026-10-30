# Dựng trang Mesh Lab cho một nhân vật: nhúng mesh gốc (cm) vào template.html
# python work/mesh_lab/build_mesh.py <gaygor|id trong rig_lab/chars>  -> work/mesh_lab/pages/<id>/index.html
import json, os, sys
R = os.path.dirname(os.path.abspath(__file__))
RL = os.path.join(R, "..", "rig_lab")
cid = sys.argv[1]
if cid == "gaygor":
    meshes, name = json.load(open(f"{RL}/ref_gaygor/ref_mesh.json")), "Gaygor"
else:
    C = json.load(open(f"{RL}/chars/{cid}.json", encoding="utf8"))
    meshes, name = json.load(open(f"{RL}/chars/{cid}/mesh_cm.json")), C["name"]
data = dict(name=name, meshes=[dict(name=m["name"], verts=[round(v, 3) for v in m["verts"]], tris=m["tris"]) for m in meshes])
html = open(f"{R}/template.html", encoding="utf8").read().replace("/*DATA*/null", json.dumps(data, separators=(",", ":"))).replace("__NAME__", name)
out = f"{R}/pages/{cid}"
os.makedirs(out, exist_ok=True)
open(f"{out}/index.html", "w", encoding="utf8").write(html)
print(len(html) // 1024, "KB ->", out)
