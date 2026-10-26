# Dựng trang Rig Lab cho một nhân vật theo cấu hình chars/<id>.json (Gaygor vẫn dùng build_page.py)
# python work/rig_lab/build_char.py <id>  -> chars/<id>/mesh_cm.json, landmarks_auto.json, pages/<id>/index.html
import json, os, subprocess, sys
R = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(f"{R}/chars/{sys.argv[1]}.json", encoding="utf8"))
out = f"{R}/chars/{C['id']}"; os.makedirs(out, exist_ok=True)
sc = C.get("scale", 1)
meshes = json.load(open(f"{R}/{C['ref_dir']}/ref_mesh.json"))
for m in meshes: m["verts"] = [round(v * sc, 3) for v in m["verts"]]
json.dump(meshes, open(f"{out}/mesh_cm.json", "w"), separators=(",", ":"))
env = dict(os.environ, RIG_BODY=C["body"])
subprocess.check_call([sys.executable, f"{R}/propose.py", f"{out}/mesh_cm.json", f"{out}/landmarks_auto.json"], env=env)
auto = json.load(open(f"{out}/landmarks_auto.json"))
byn = {m["name"]: m for m in meshes}; body = byn[C["body"]]
cfg = C["cfg"]
# mẫu ngón: lấy từ rig khách của clip cũ (tỉ lệ cổ tay → ngón / cổ tay → đầu ngón), tên xương cũng từ đó
sk = json.load(open(f"{R}/{C['names_from']}/ref_skeleton.json")); pos = {s["name"]: s["bind_pos"] for s in sk}
oldmesh = json.load(open(f"{R}/{C['names_from']}/ref_mesh.json")); oldL = max(abs(v) for m in oldmesh for v in m["verts"][0::3])
w = pos["Wrist_R"]; tip = -oldL * .995; fingers = {}
for f in cfg["fingers"]:
    fingers[f] = [[round(abs(pos[f"{f}Finger{i}_R"][0] - w[0]) / abs(tip - w[0]), 4), round((pos[f"{f}Finger{i}_R"][1] - w[1]) / abs(tip - w[0]), 4),
                   round((pos[f"{f}Finger{i}_R"][2] - w[2]) / abs(tip - w[0]), 4)] for i in range(1, cfg.get("fseg", 3) + 1)]
data = dict(body=dict(verts=body["verts"], tris=body["tris"]), props=[],
            clothes=[dict(name=byn[n]["name"], verts=byn[n]["verts"], tris=byn[n]["tris"]) for n in C.get("clothes", [])],
            auto=auto, fingers=fingers, cfg=cfg, ref=[dict(name=s["name"], parent=s["parent"], pos=None) for s in sk], refW={})
html = open(f"{R}/template.html", encoding="utf8").read().replace("/*DATA*/null", json.dumps(data, separators=(",", ":"))).replace("__NAME__", C["name"])
os.makedirs(f"{R}/pages/{C['id']}", exist_ok=True)
open(f"{R}/pages/{C['id']}/index.html", "w", encoding="utf8").write(html)
print(len(html) // 1024, "KB", {k: v for k, v in auto["landmarks"].items() if k in cfg or True} if False else "")
