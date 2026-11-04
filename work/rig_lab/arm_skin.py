"""Trọng số tay dạng dải chuyển mềm dọc trục xương (Ninja 2026-10-29, user: "sửa lại phần paint chỗ khớp tay").
Skin tự động để chỗ chuyển vai→cánh tay trên→cẳng tay quá gắt: gập khuỷu 135° giãn đỉnh ~400 %, giơ tay 90° giãn ~230 %.

    .venv/Scripts/python.exe -I -X utf8 work/rig_lab/arm_skin.py <id> [--out file.json] [--write] [--bands a,b,a,b,a,b]
Không --write: chỉ ghi ra --out (để lbs_test.py so). --write: ghi vào kho (sao lưu bản cũ vào chars/<id>/).

Chỉ đụng phần trọng số đang thuộc chuỗi tay của mỗi đỉnh (Scapula + Shoulder + Elbow + Wrist cùng bên); phần của ngực, ngón tay
giữ nguyên. Phần chuỗi tay chia lại theo smoothstep dọc trục xương, s = khoảng cách có dấu tính từ khớp (cm):
  Scapula|Shoulder a..b (dọc trục cánh tay trên, tính từ khớp vai), Shoulder|Elbow a..b, Elbow|Wrist a..b (dọc trục cẳng tay).
Đỉnh ở phía thân của khớp vai (s < a của dải đầu) giữ nguyên tỉ lệ Scapula / Shoulder cũ.
"""
import collections, json, os, sys, time
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CID = sys.argv[1]
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
WRITE = "--write" in sys.argv
B = [float(x) for x in sys.argv[sys.argv.index("--bands") + 1].split(",")] if "--bands" in sys.argv else [-6, 4, -6, 6, -4, 4]
ST = os.path.join(ROOT, "work", "store", CID + "_rig_lab", "rig")
CF = json.load(open(os.path.join(ROOT, "work", "rig_lab", "chars", CID + ".json"), encoding="utf8"))
sk = json.load(open(os.path.join(ST, "skin.json")))
L = {k: np.array(v, float) for k, v in json.load(open(os.path.join(ST, "landmarks.json")))["lm"].items()}
auto = json.load(open(os.path.join(ROOT, "work", "rig_lab", "chars", CID, "landmarks_auto.json")))["landmarks"]
L = {**{k: np.array(v, float) for k, v in auto.items()}, **L}
me = os.path.join(ROOT, "work", "store", CID + "_mesh_lab", "mesh", "edit.json")
meshes = json.load(open(me))["meshes"] if os.path.isfile(me) else json.load(open(os.path.join(ROOT, "work", "rig_lab", "chars", CID, "mesh_cm.json")))
body = next(m for m in meshes if m["name"] == CF["body"])
V = np.array(body["verts"], float).reshape(-1, 3); NV = len(V)
names = list(sk["names"]); I = np.array(sk["I"]).reshape(-1, 4); W = np.array(sk["W"], float).reshape(-1, 4)


def ss(a, b, x):
    t = float(np.clip((x - a) / (b - a), 0, 1)); return t * t * (3 - 2 * t)


unit = lambda v: v / np.linalg.norm(v)
changed = 0
for s in "LR":
    C = ["Scapula_" + s, "Shoulder_" + s, "Elbow_" + s, "Wrist_" + s]
    Sh, El, Wr = L[C[1]], L[C[2]], L[C[3]]
    du, df = unit(El - Sh), unit(Wr - El)
    for i in range(NV):
        old = collections.Counter()
        for k in range(4):
            if W[i, k] > 0: old[names[I[i, k]]] += W[i, k]
        CC = C if len(B) >= 6 else C[:3]          # 4 số --bands: cổ tay giữ nguyên trọng số cũ
        m = sum(old[b] for b in CC)
        if m <= 0.01 or sum(old[b] for b in CC[1:]) <= 0.01: continue
        p = V[i]
        w1 = ss(B[0], B[1], np.dot(p - Sh, du))      # 0 = scapula, 1 = cánh tay trên trở ra
        w2 = ss(B[2], B[3], np.dot(p - El, du))      # 0 = cánh tay trên, 1 = cẳng tay
        w3 = ss(B[4], B[5], np.dot(p - Wr, df)) if len(B) >= 6 else 0.0   # 0 = cẳng tay, 1 = bàn tay
        if w1 <= 0:      # phía thân của vai: giữ nguyên
            continue
        new = {C[0]: 1 - w1, C[1]: w1 * (1 - w2), C[2]: w1 * w2 * (1 - w3), C[3]: w1 * w2 * w3}
        if CC is not C:
            if np.dot(p - Wr, df) > 0: continue   # bàn tay: giữ nguyên
            new.pop(C[3])
        # phía thân: trộn với tỉ lệ scapula/shoulder cũ để nối êm
        mix = collections.Counter({b: w for b, w in old.items() if b not in CC})
        oldarm = {b: old[b] / m for b in CC}
        for b in CC: mix[b] += m * (w1 * new[b] + (1 - w1) * oldarm[b])
        top = [(b, w) for b, w in mix.most_common(4) if w > 0.01]
        tot = sum(w for _, w in top)
        for b, _ in top:
            if b not in names: names.append(b)
        I[i] = [names.index(b) for b, _ in top] + [0] * (4 - len(top))
        W[i] = [w / tot for _, w in top] + [0] * (4 - len(top))
        changed += 1

# Dọn xương lạ trên tay (user 2026-10-29: "vẫn bị ảnh hưởng tới cánh tay quá, cánh tay vẫn bị méo"):
#  - cẳng tay (trước khớp cổ tay): bỏ trọng số ngón tay, phần Elbow + Wrist + ngón chia lại Elbow→Wrist theo smoothstep(-10, +6) quanh cổ tay;
#  (đã thử chuyển Spine1_M / Neck_M ở vòng vai về Chest_M: ngực xoay z 30° giãn 57 → 211 %, bỏ.)
SMALL = lambda b, s: b.endswith("_" + s) and "Finger" in b
cleaned = 0
for s in "LR":
    El, Wr = L["Elbow_" + s], L["Wrist_" + s]
    df = unit(Wr - El); lf = float(np.linalg.norm(Wr - El))
    for i in range(NV):
        cur = collections.Counter()
        for k in range(4):
            if W[i, k] > 0: cur[names[I[i, k]]] += W[i, k]
        p = V[i]; t2 = float(np.dot(p - El, df))
        new = collections.Counter(cur)
        if cur["Elbow_" + s] + cur["Wrist_" + s] > 0.05 and -2 <= t2 < lf:
            mm = cur["Elbow_" + s] + cur["Wrist_" + s] + sum(w for b, w in cur.items() if SMALL(b, s))
            for b in list(new):
                if SMALL(b, s): del new[b]
            ww = ss(-10, 6, t2 - lf)
            new["Wrist_" + s] = mm * ww; new["Elbow_" + s] = mm * (1 - ww)
        if new == cur: continue
        top = [(b, w) for b, w in new.most_common(4) if w > 0.01]
        tot = sum(w for _, w in top)
        for b, _ in top:
            if b not in names: names.append(b)
        I[i] = [names.index(b) for b, _ in top] + [0] * (4 - len(top))
        W[i] = [w / tot for _, w in top] + [0] * (4 - len(top))
        cleaned += 1
print("đỉnh dọn xương lạ:", cleaned)

sk["names"] = names; sk["I"] = I.flatten().tolist(); sk["W"] = [round(float(x), 4) for x in W.flatten()]; sk["at"] = int(time.time() * 1000)
print("đỉnh tay viết lại:", changed)
if OUT:
    json.dump(sk, open(OUT, "w"), separators=(",", ":")); print("ra", OUT)
if WRITE:
    bak = os.path.join(ROOT, "work", "rig_lab", "chars", CID, "skin_before_armskin_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    json.dump(json.load(open(os.path.join(ST, "skin.json"))), open(bak, "w"), separators=(",", ":"))
    json.dump(sk, open(os.path.join(ST, "skin.json"), "w"), separators=(",", ":"))
    print("đã ghi kho, sao lưu:", os.path.relpath(bak, ROOT))
