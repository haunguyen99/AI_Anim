"""Dọn skin theo vùng cơ thể: xương chỉ giữ ảnh hưởng trong bộ phận của nó (Ninja 2026-10-29, user: "các joint đang ảnh
hưởng đến cả những vertex ở ngoài bộ phận"). Skin tự động (khoảng cách + khuếch tán) để xương đùi lấn qua đường giữa
sang đùi kia và lên bụng, xương ngực/cột sống lấn vào gốc cánh tay.

    .venv/Scripts/python.exe -I -X utf8 work/rig_lab/clean_skin.py <id> [--dry]

Luật (chỉ trên mảnh thân chính; mảnh rời như cổ khăn, đuôi khăn giữ nguyên):
  1. Xương có hậu tố _L/_R không ảnh hưởng đỉnh nằm bên kia đường giữa (quá 1 cm).
  2. Xương đùi Hip_*: không ảnh hưởng đỉnh cao hơn khớp hông + 6 cm (bụng thuộc Root/Spine).
  3. Gối/cổ chân/mũi chân: chỉ đỉnh thấp hơn khớp hông.
  4. Xương thân (Root, Spine1, Chest, Neck, Head) không ảnh hưởng phần cánh tay (|x| > khớp vai + 4 cm);
     chỉ trong dải độ cao cánh tay; xương tay (vai trở ra) không ảnh hưởng đỉnh trong thân (|x| < khớp vai - 8 cm).
  5. Bỏ trọng số < 0.02, chuẩn hoá tổng = 1; đỉnh mất hết trọng số thì gán cho xương được phép gần nhất.
Sao lưu skin cũ: work/rig_lab/chars/<id>/skin_before_clean_<giờ>.json. Đóng / tải lại trang Rig ngay sau khi chạy.
"""
import collections, json, os, sys, time
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CID = sys.argv[1]; DRY = "--dry" in sys.argv
ST = os.path.join(ROOT, "work", "store", CID + "_rig_lab", "rig")
CF = json.load(open(os.path.join(ROOT, "work", "rig_lab", "chars", CID + ".json"), encoding="utf8"))
sk = json.load(open(os.path.join(ST, "skin.json")))
L = json.load(open(os.path.join(ST, "landmarks.json")))["lm"]
me = os.path.join(ROOT, "work", "store", CID + "_mesh_lab", "mesh", "edit.json")
meshes = json.load(open(me))["meshes"] if os.path.isfile(me) else json.load(open(os.path.join(ROOT, "work", "rig_lab", "chars", CID, "mesh_cm.json")))
body = next(m for m in meshes if m["name"] == CF["body"])
V = np.array(body["verts"], float).reshape(-1, 3); T = np.array(body["tris"]).reshape(-1, 3); NV = len(V)
names = sk["names"]; I = np.array(sk["I"]).reshape(-1, 4); W = np.array(sk["W"], float).reshape(-1, 4)
assert sk.get("nv", NV) == NV, "skin và mesh khác số đỉnh"

# mảnh thân chính = thành phần liên thông lớn nhất
par = list(range(NV))
def f(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
for a, b, c in T:
    for u, v in ((a, b), (b, c)): par[f(u)] = f(v)
comp = collections.Counter(f(i) for i in range(NV)); main_root = comp.most_common(1)[0][0]
main = np.array([f(i) == main_root for i in range(NV)])

hipY = (L["Hip_L"][1] + L["Hip_R"][1]) / 2
shX = (abs(L["Shoulder_L"][0]) + abs(L["Shoulder_R"][0])) / 2
CORE = {"Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M", "HeadEnd_M"}
side = lambda b: "L" if b.endswith("_L") else "R" if b.endswith("_R") else ""
is_arm = lambda b: b.split("_")[0] in ("Shoulder", "Elbow", "Wrist") or "Finger" in b or b.startswith(("ShoulderTwist", "ElbowTwist"))
is_leg_low = lambda b: b.split("_")[0] in ("Knee", "Ankle", "Toes", "ToesEnd") or b.startswith("KneeTwist")


def allowed(b, p):
    x, y = p[0], p[1]; s = side(b)
    if s and abs(x) > 1 and (x > 0) != (s == "L"): return False
    if b.startswith("Hip_") and y > hipY + 6: return False
    if is_leg_low(b) and y > hipY: return False
    if b in CORE and abs(x) > shX + 4 and hipY + 20 < y < L["Neck_M"][1] + 4: return False   # dải cánh tay (đầu rộng hơn vai)
    if is_arm(b) and abs(x) < shX - 8: return False
    return True


def seg_dist(p, b):   # khoảng cách tới khớp (đủ để chọn xương thay thế)
    return np.linalg.norm(p - np.array(L.get(b, [0, 0, 0]), float)) if b in L else 1e9


changed, emptied, removed = 0, 0, collections.Counter()
for i in np.where(main)[0]:
    w = W[i].copy(); ok = True
    for k in range(4):
        if w[k] > 0 and not allowed(names[I[i, k]], V[i]):
            removed[names[I[i, k]]] += 1; w[k] = 0; ok = False
    w[w < 0.02] = 0
    if w.sum() <= 0:
        cands = [b for b in names if b in L and allowed(b, V[i])]
        b = min(cands, key=lambda b: seg_dist(V[i], b)); I[i] = [names.index(b), 0, 0, 0]; w = np.array([1.0, 0, 0, 0]); emptied += 1
    w = w / w.sum()
    if not ok or not np.allclose(w, W[i]): changed += 1
    W[i] = w

print(f"đỉnh thân chính {main.sum()}/{NV}, đổi {changed}, gán lại hoàn toàn {emptied}")
print("trọng số bị bỏ theo xương:", removed.most_common(12))
if DRY:
    sys.exit(0)
bak = os.path.join(ROOT, "work", "rig_lab", "chars", CID, "skin_before_clean_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
json.dump(json.load(open(os.path.join(ST, "skin.json"))), open(bak, "w"), separators=(",", ":"))
sk["I"] = I.flatten().tolist(); sk["W"] = [round(float(x), 4) for x in W.flatten()]; sk["at"] = int(time.time() * 1000)
json.dump(sk, open(os.path.join(ST, "skin.json"), "w"), separators=(",", ":"))
print("đã ghi skin, sao lưu:", os.path.relpath(bak, ROOT))
