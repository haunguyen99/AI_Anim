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
# mọi mesh trong cảnh đều vào lõi Rig: mesh phụ (chars/<id>.json "extra": tóc, phụ kiện, vũ khí) không phải prop thì là lớp mặc thêm
propn = {p["name"] for p in C.get("props", [])}
C["clothes"] = list(C.get("clothes", [])) + [n for n in C.get("extra", []) if n in byn and n not in propn and n not in C.get("clothes", [])]
# xương khách chỉ mesh phụ dùng (nỏ slingshot_*, bím tóc joint*): thêm thành joint phụ noBody (không nhận đỉnh thân khi skin tự động)
if sk:
    par = {s["name"]: s["parent"] for s in sk}; bw = set(body.get("weights", {}))
    used = {b for n in C["clothes"] for b in byn[n].get("weights", {}) if b not in bw}
    have = {e["name"] for e in cfg.get("extra", [])}; add = []
    def need(b):
        if b in have or b in bw or not pos.get(b) or not par.get(b): return
        need(par[b]); have.add(b); add.append({"name": b, "parent": par[b], "label": b, "noBody": True})
    for b in sorted(used): need(b)
    if add: cfg["extra"] = list(cfg.get("extra", [])) + add
# joint phụ (cfg.extra): vị trí ghi sẵn trong cấu hình, không có thì lấy theo xương khách
for e in cfg.get("extra", []):
    p = e.get("pos") or pos.get(e["name"])
    if p: auto["landmarks"][e["name"]] = [round(v, 2) for v in p]
if cfg.get("extra"): json.dump(auto, open(f"{out}/landmarks_auto.json", "w"), indent=1)
# khớp đo tay trên mesh (chars/<id>.json "landmarks"): đè gợi ý của propose.py (tỉ lệ Gaygor lệch với thân khác)
for k, p in C.get("landmarks", {}).items(): auto["landmarks"][k] = [round(v, 2) for v in p]
if C.get("landmarks"): json.dump(auto, open(f"{out}/landmarks_auto.json", "w"), indent=1)
# prop rời gắn cứng vào xương Weapon (chars/<id>.json "props": [{name, xf}]); xf = 3 cột trục (x, y, z của prop
# trong thế giới) + điểm đặt gốc prop, 12 số. Mesh FBX để prop ở gốc (Ninja: kunai đứng ở 0,0,0) nên xf đặt nó vào tay;
# gốc prop = điểm cầm = vị trí khớp Weapon
props = []
for p in C.get("props", []):
    v, m = byn[p["name"]]["verts"], p.get("xf")
    if m:
        v = [round(m[k] * v[i] + m[3 + k] * v[i + 1] + m[6 + k] * v[i + 2] + m[9 + k], 3) for i in range(0, len(v), 3) for k in range(3)]
        if cfg.get("weapon"): auto["landmarks"]["Weapon"] = [round(x, 2) for x in m[9:12]]
    props.append(dict(name=p["name"], verts=v, tris=byn[p["name"]]["tris"], **({"xf": m} if m else {})))
if props: json.dump(auto, open(f"{out}/landmarks_auto.json", "w"), indent=1)
data = dict(body=dict(name=body["name"], verts=body["verts"], tris=body["tris"]), props=props,
            clothes=[dict(name=byn[n]["name"], verts=byn[n]["verts"], tris=byn[n]["tris"]) for n in C.get("clothes", [])],
            auto=auto, fingers=fingers, cfg=cfg, ref=[dict(name=s["name"], parent=s["parent"], pos=None) for s in sk], refW={})
html = open(f"{R}/template.html", encoding="utf8").read().replace("/*DATA*/null", json.dumps(data, separators=(",", ":"))).replace("__NAME__", C["name"])
os.makedirs(f"{R}/pages/{C['id']}", exist_ok=True)
open(f"{R}/pages/{C['id']}/index.html", "w", encoding="utf8").write(html)
print(len(html) // 1024, "KB", {k: v for k, v in auto["landmarks"].items() if k in cfg or True} if False else "")
