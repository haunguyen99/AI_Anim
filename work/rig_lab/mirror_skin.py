"""python work/rig_lab/mirror_skin.py <id>
Chép skin bên phải (x < 0, xương *_R) sang bên trái (x > 0, *_L) theo đỉnh đối xứng gần nhất. Ghi đè skin.json của kho rig."""
import json, math, sys
ROOT = r"E:\AI Animation"
cid = sys.argv[1]
sp = ROOT + rf"\work\store\{cid}_rig_lab\rig\skin.json"
raw = json.load(open(sp, encoding="utf8")); d = raw.get("data", raw)
C = json.load(open(ROOT + rf"\work\rig_lab\chars\{cid}.json", encoding="utf8"))
body = next(m for m in json.load(open(ROOT + rf"\work\rig_lab\chars\{cid}\mesh_cm.json")) if m["name"] == C["body"])
v = body["verts"]; n = len(v) // 3; assert n == d["nv"], (n, d["nv"])
names = d["names"]; idx = {b: i for i, b in enumerate(names)}
swap = lambda b: b[:-2] + "_L" if b.endswith("_R") else b[:-2] + "_R" if b.endswith("_L") else b
I, W = d["I"], d["W"]
P = [(v[3 * i], v[3 * i + 1], v[3 * i + 2]) for i in range(n)]
right = [i for i in range(n) if P[i][0] < -0.3]
done = far = 0
for i in range(n):
    x, y, z = P[i]
    if x <= 0.3: continue                      # chỉ sửa đỉnh bên trái (+x)
    best, bd = None, 1e9
    for j in right:
        dd = (P[j][0] + x) ** 2 + (P[j][1] - y) ** 2 + (P[j][2] - z) ** 2
        if dd < bd: bd, best = dd, j
    if best is None or math.sqrt(bd) > 2.0: far += 1; continue
    for k in range(4):
        w = W[4 * best + k]; b = names[I[4 * best + k]]
        I[4 * i + k] = idx[swap(b)] if w > 0 else I[4 * i + k]; W[4 * i + k] = w
    done += 1
raw.update(d) if "data" not in raw else raw["data"].update(d)
json.dump(raw, open(sp, "w", encoding="utf8"), separators=(",", ":"))
print("left verts mirrored", done, "| no mirror within 2 cm (kept)", far)
