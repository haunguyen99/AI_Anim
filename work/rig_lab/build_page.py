# Dựng trang Rig Lab: nhúng mesh + gợi ý khớp + xương khách (đáp án) + mẫu ngón vào template.html
# python work/rig_lab/build_page.py  -> work/rig_lab/pages/gaygor/index.html
import json, os
R = os.path.dirname(os.path.abspath(__file__))
mesh = sorted(json.load(open(f"{R}/ref_gaygor/ref_mesh.json")), key=lambda m: -len(m["verts"]))
skel = json.load(open(f"{R}/ref_gaygor/ref_skeleton.json"))
auto = json.load(open(f"{R}/landmarks_auto.json"))
pos = {s["name"]: s["bind_pos"] for s in skel}
w, t = pos["Wrist_R"], pos["MiddleFinger3_R"]
ln = abs(t[0] - w[0])
fingers = {}   # [dọc tay (cm/len), dy/len, dz/len] cho tay R (x âm)
for f in ["Middle", "Thumb", "Index", "Ring", "Pinky"]:
    fingers[f] = [[round(abs(pos[f"{f}Finger{i}_R"][0] - w[0]) / ln, 4), round((pos[f"{f}Finger{i}_R"][1] - w[1]) / ln, 4),
                   round((pos[f"{f}Finger{i}_R"][2] - w[2]) / ln, 4)] for i in (1, 2, 3)]
r2 = lambda a: [round(x, 3) for x in a]
data = dict(body=dict(verts=mesh[0]["verts"], tris=mesh[0]["tris"]),
            props=[dict(name=m["name"], verts=m["verts"], tris=m["tris"]) for m in mesh[1:]],
            auto=auto, fingers=fingers,
            ref=[dict(name=s["name"], parent=s["parent"], pos=r2(s["bind_pos"] or [0, 0, 0])) for s in skel],
            refW={k: [v[0], [round(x, 3) for x in v[1]]] for k, v in mesh[0]["weights"].items()})
html = open(f"{R}/template.html", encoding="utf8").read().replace("/*DATA*/null", json.dumps(data, separators=(",", ":")))
os.makedirs(f"{R}/pages/gaygor", exist_ok=True)
open(f"{R}/pages/gaygor/index.html", "w", encoding="utf8").write(html)
print(len(html) // 1024, "KB")
