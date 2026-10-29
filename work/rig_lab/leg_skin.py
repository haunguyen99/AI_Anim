"""Trọng số chân dạng dải chuyển mềm dọc trục xương (Ninja 2026-10-29, ghi chú: "phần này paint vẫn chưa được xử lí đẹp"
khoanh hông–đùi–gối lúc gập chân). Skin tự động + clean_skin.py để chỗ chuyển chậu→đùi và đùi→ống chân quá gắt:
gập đùi 110° giãn đỉnh 557 %, gập gối 140° hỏng 2 % cạnh.

    .venv/Scripts/python.exe -I -X utf8 work/rig_lab/leg_skin.py <id> [--out file.json] [--write] [--bands a,b,a,b,a,b,a,b]
Không --write: chỉ ghi ra --out (để lbs_test.py so). --write: ghi vào kho (sao lưu bản cũ vào chars/<id>/).

Mỗi đỉnh của mảnh thân chính thấp hơn khớp hông + 14 cm:
  s = khoảng cách có dấu dọc trục xương tính từ khớp; trọng số chia theo smoothstep qua từng khớp
  (mặc định Root|Hip -8..+10, Hip|Knee -8..+8, Knee|Ankle -8..+6, Ankle|Toes -5..+4 cm, chọn bằng dò lbs_test);
  đỉnh gần đường giữa (|x| < 4) chia hai chân theo smoothstep(-4, 4, x);
  dải hông + 6..+14 cm trộn dần với skin cũ để nối êm lên bụng.
"""
import collections, json, os, sys, time
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CID = sys.argv[1]
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
WRITE = "--write" in sys.argv
B = [float(x) for x in sys.argv[sys.argv.index("--bands") + 1].split(",")] if "--bands" in sys.argv else [-8, 10, -8, 8, -8, 6, -5, 4]   # đã dò 2026-10-29 (sweep lbs_test): Root|Hip, Hip|Knee, Knee|Ankle, Ankle|Toes (cm)
ST = os.path.join(ROOT, "work", "store", CID + "_rig_lab", "rig")
CF = json.load(open(os.path.join(ROOT, "work", "rig_lab", "chars", CID + ".json"), encoding="utf8"))
sk = json.load(open(os.path.join(ST, "skin.json")))
L = {k: np.array(v, float) for k, v in json.load(open(os.path.join(ST, "landmarks.json")))["lm"].items()}
me = os.path.join(ROOT, "work", "store", CID + "_mesh_lab", "mesh", "edit.json")
meshes = json.load(open(me))["meshes"] if os.path.isfile(me) else json.load(open(os.path.join(ROOT, "work", "rig_lab", "chars", CID, "mesh_cm.json")))
body = next(m for m in meshes if m["name"] == CF["body"])
V = np.array(body["verts"], float).reshape(-1, 3); T = np.array(body["tris"]).reshape(-1, 3); NV = len(V)
names = list(sk["names"]); I = np.array(sk["I"]).reshape(-1, 4); W = np.array(sk["W"], float).reshape(-1, 4)

par = list(range(NV))
def f(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
for a, b, c in T:
    for u, v in ((a, b), (b, c)): par[f(u)] = f(v)
mr = collections.Counter(f(i) for i in range(NV)).most_common(1)[0][0]

ss = lambda a, b, x: float(np.clip((x - a) / (b - a), 0, 1)) ** 2 * (3 - 2 * float(np.clip((x - a) / (b - a), 0, 1)))
unit = lambda v: v / np.linalg.norm(v)
hipY = (L["Hip_L"][1] + L["Hip_R"][1]) / 2


def chain(p, s):
    H, K, A, To = L["Hip_" + s], L["Knee_" + s], L["Ankle_" + s], L["Toes_" + s]
    dt, ds, df = unit(K - H), unit(A - K), unit(To - A)
    wh = ss(B[0], B[1], np.dot(p - H, dt)); wk = ss(B[2], B[3], np.dot(p - K, dt)); wa = ss(B[4], B[5], np.dot(p - A, ds)); wt = ss(B[6], B[7], np.dot(p - To, df))
    return {"Root_M": 1 - wh, "Hip_" + s: wh * (1 - wk), "Knee_" + s: wh * wk * (1 - wa), "Ankle_" + s: wh * wk * wa * (1 - wt), "Toes_" + s: wh * wk * wa * wt}


changed = 0
for i in range(NV):
    if f(i) != mr: continue
    p = V[i]
    if p[1] > hipY + 14: continue
    sL = ss(-4, 4, p[0])
    new = collections.Counter()
    for s, k in (("L", sL), ("R", 1 - sL)):
        if k <= 0: continue
        for b, w in chain(p, s).items(): new[b] += k * w
    a = 1 - ss(hipY + 6, hipY + 14, p[1])   # 1 dưới hông+6, 0 trên hông+14
    old = collections.Counter({names[I[i, k]]: W[i, k] for k in range(4) if W[i, k] > 0})
    mix = collections.Counter()
    for b, w in new.items(): mix[b] += a * w
    for b, w in old.items(): mix[b] += (1 - a) * w
    top = [(b, w) for b, w in mix.most_common(4) if w > 0.01]
    tot = sum(w for _, w in top)
    for b, _ in top:
        if b not in names: names.append(b)
    I[i] = [names.index(b) for b, _ in top] + [0] * (4 - len(top))
    W[i] = [w / tot for _, w in top] + [0] * (4 - len(top))
    changed += 1

sk["names"] = names; sk["I"] = I.flatten().tolist(); sk["W"] = [round(float(x), 4) for x in W.flatten()]; sk["at"] = int(time.time() * 1000)
print("đỉnh chân viết lại:", changed)
if OUT:
    json.dump(sk, open(OUT, "w"), separators=(",", ":")); print("ra", OUT)
if WRITE:
    bak = os.path.join(ROOT, "work", "rig_lab", "chars", CID, "skin_before_legskin_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    json.dump(json.load(open(os.path.join(ST, "skin.json"))), open(bak, "w"), separators=(",", ":"))
    json.dump(sk, open(os.path.join(ST, "skin.json"), "w"), separators=(",", ":"))
    print("đã ghi kho, sao lưu:", os.path.relpath(bak, ROOT))
