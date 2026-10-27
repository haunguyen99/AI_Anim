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
# model tĩnh (không có xương khách): mẫu bàn tay mặc định 5 ngón × 3 đốt, chỉnh lại ở bước Khớp
DEFAULT_FINGERS = {"Middle": [[0.408, -0.052, 0.136], [0.644, -0.027, 0.138], [0.825, -0.1, 0.135]], "Thumb": [[0.089, -0.186, 0.315], [0.144, -0.273, 0.395], [0.304, -0.405, 0.448]],
                   "Index": [[0.397, -0.079, 0.312], [0.616, -0.043, 0.355], [0.785, -0.104, 0.384]], "Ring": [[0.443, -0.085, -0.073], [0.59, -0.025, -0.087], [0.729, -0.123, -0.085]],
                   "Pinky": [[0.307, -0.076, -0.271], [0.558, -0.076, -0.299], [0.664, -0.111, -0.317]]}
skp = f"{R}/{C.get('names_from')}/ref_skeleton.json" if C.get("names_from") else ""
sk = json.load(open(skp)) if skp and os.path.isfile(skp) else []; pos = {s["name"]: s["bind_pos"] for s in sk}
fingers = {}
if pos.get("Wrist_R") and all(pos.get(f"{f}Finger{i}_R") for f in cfg["fingers"] for i in range(1, cfg.get("fseg", 3) + 1)):
    oldmesh = json.load(open(f"{R}/{C['names_from']}/ref_mesh.json")); oldL = max(abs(v) for m in oldmesh for v in m["verts"][0::3])
    w = pos["Wrist_R"]; tip = -oldL * .995
    for f in cfg["fingers"]:
        fingers[f] = [[round(abs(pos[f"{f}Finger{i}_R"][0] - w[0]) / abs(tip - w[0]), 4), round((pos[f"{f}Finger{i}_R"][1] - w[1]) / abs(tip - w[0]), 4),
                       round((pos[f"{f}Finger{i}_R"][2] - w[2]) / abs(tip - w[0]), 4)] for i in range(1, cfg.get("fseg", 3) + 1)]
else:
    for f in cfg["fingers"]:
        d = DEFAULT_FINGERS.get(f, DEFAULT_FINGERS["Middle"]); n = cfg.get("fseg", 3)
        fingers[f] = [d[min(round(i * (len(d) - 1) / max(n - 1, 1)), len(d) - 1)] for i in range(n)]
# xương khách dựng lại từ skin (skel_from_weights.py): dùng luôn làm gợi ý khớp, thay cho tỉ lệ khung chung của propose.py
if C.get("auto_from_ref"):
    sc = C.get("scale", 1); L = auto["landmarks"]
    for k in L:
        if pos.get(k): L[k] = [round(v * sc, 2) for v in pos[k]]
    json.dump(auto, open(f"{out}/landmarks_auto.json", "w"), indent=1)
data = dict(body=dict(name=body["name"], verts=body["verts"], tris=body["tris"]), props=[],
            clothes=[dict(name=byn[n]["name"], verts=byn[n]["verts"], tris=byn[n]["tris"]) for n in C.get("clothes", [])],
            auto=auto, fingers=fingers, cfg=cfg, ref=[dict(name=s["name"], parent=s["parent"], pos=None) for s in sk], refW={})
html = open(f"{R}/template.html", encoding="utf8").read().replace("/*DATA*/null", json.dumps(data, separators=(",", ":"))).replace("__NAME__", C["name"])
os.makedirs(f"{R}/pages/{C['id']}", exist_ok=True)
open(f"{R}/pages/{C['id']}/index.html", "w", encoding="utf8").write(html)
print(len(html) // 1024, "KB", {k: v for k, v in auto["landmarks"].items() if k in cfg or True} if False else "")
