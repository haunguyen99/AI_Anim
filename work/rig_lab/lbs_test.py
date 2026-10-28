# Xoay từng khớp (skin tuyến tính như Rig / Pose) và đo biến dạng skin: % cạnh giãn/co quá 25%, tam giác lật mặt (so với pháp tuyến
# xoay theo khớp), xương sở hữu các cạnh hỏng. Dòng BAD = >1,5% cạnh hỏng hoặc >5 tam giác lật.
# Mỗi khớp quét HẾT dải góc trên từng trục (bước 15°, cả hai chiều, theo bảng ROM dưới); lưới tốt = cạnh giãn / co đều trên cả vùng gập:
# "đỉnh" = cạnh giãn / co tệ nhất (cạnh ≥ 0,8 cm), "hỏng" = % cạnh giãn / co quá 25 %, "dồn" = p99 / trung bình trong vùng gập.
# python work/rig_lab/lbs_test.py <id> [skin.json]                       -> bảng mỗi khớp × trục: góc tệ nhất, đỉnh giãn/co, độ dồn, tam giác lật
# python work/rig_lab/lbs_test.py <id> --wire KHỚP TRỤC ĐỘ out.png        -> ảnh lưới (trước + bên, quanh khớp) tô màu: đỏ giãn, xanh co
# python work/rig_lab/lbs_test.py <id> --render KHỚP TRỤC ĐỘ out.json     -> mesh đã xoay
# Đọc work/store/<id>_rig_lab/rig/{skin,landmarks}.json và mesh đã sửa work/store/<id>_mesh_lab/mesh/edit.json (không có thì mesh gốc).
import json, os, sys
import numpy as np
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CID = sys.argv[1]
ST = os.path.join(ROOT, "work", "store", CID + "_rig_lab", "rig") + os.sep
SKIN = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else ST + "skin.json"
CF = json.load(open(os.path.join(ROOT, "work", "rig_lab", "chars", CID + ".json"), encoding="utf-8"))
_me = os.path.join(ROOT, "work", "store", CID + "_mesh_lab", "mesh", "edit.json")
_ms = json.load(open(_me, encoding="utf-8"))["meshes"] if os.path.isfile(_me) else json.load(open(os.path.join(ROOT, "work", "rig_lab", "chars", CID, "mesh_cm.json")))
mesh = next(m for m in _ms if m["name"] == CF["body"])
V = np.array(mesh["verts"]).reshape(-1, 3); T = np.array(mesh["tris"]).reshape(-1, 3); NV = len(V)
sk = json.load(open(SKIN, encoding="utf-8")); names = sk["names"]
I4 = np.array(sk["I"]).reshape(-1, 4); W4 = np.array(sk["W"]).reshape(-1, 4)
L = json.load(open(ST + "landmarks.json", encoding="utf-8"))["lm"]
auto = json.load(open(os.path.join(ROOT, "work", "rig_lab", "chars", CID, "landmarks_auto.json")))["landmarks"]
P = {k: np.array(v, float) for k, v in {**auto, **L}.items()}

PAR = {"Root_M": None, "Spine1_M": "Root_M", "Chest_M": "Spine1_M", "Neck_M": "Chest_M", "Head_M": "Neck_M"}
for s in "RL":
    PAR.update({f"Scapula_{s}": "Chest_M", f"Shoulder_{s}": f"Scapula_{s}", f"Elbow_{s}": f"Shoulder_{s}", f"Wrist_{s}": f"Elbow_{s}",
                f"Hip_{s}": "Root_M", f"Knee_{s}": f"Hip_{s}", f"Ankle_{s}": f"Knee_{s}", f"Toes_{s}": f"Ankle_{s}"})
    for f in ["Middle", "Thumb", "Index", "Ring", "Pinky"]:
        PAR[f"{f}Finger1_{s}"] = f"Wrist_{s}"; PAR[f"{f}Finger2_{s}"] = f"{f}Finger1_{s}"

for e in CF.get("cfg", {}).get("extra", []): PAR[e["name"]] = e["parent"]   # joint phụ (giáp vai, túi…)

def desc(j):
    out = {j}; ch = True
    while ch:
        ch = False
        for b, p in PAR.items():
            if p in out and b not in out: out.add(b); ch = True
    return out

def rot(axis, deg):
    a = np.radians(deg); c, s = np.cos(a), np.sin(a)
    return {"x": np.array([[1, 0, 0], [0, c, -s], [0, s, c]]), "y": np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]), "z": np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])}[axis]

def pose(joint, axis, deg):
    R = rot(axis, deg); p = P[joint]; D = desc(joint)
    mov = np.array([names[i] in D for i in range(len(names))])
    X = V.copy(); Y = (V - p) @ R.T + p
    w = np.zeros(NV)
    for k in range(4): w += W4[:, k] * mov[I4[:, k]]
    pose.last = (R, w)
    return X * (1 - w)[:, None] + Y * w[:, None]

E = np.unique(np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), axis=1), axis=0)
L0 = np.linalg.norm(V[E[:, 0]] - V[E[:, 1]], axis=1)
N0 = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
dom = np.array([names[I4[i, np.argmax(W4[i])]] for i in range(NV)])

def measure(X):
    l = np.linalg.norm(X[E[:, 0]] - X[E[:, 1]], axis=1); r = l / np.maximum(L0, 1e-6) - 1
    R, w = pose.last; wt = w[T].mean(1)   # pháp tuyến mong đợi: xoay theo khớp nếu tam giác chủ yếu đi theo khớp
    Ne = np.where((wt > 0.5)[:, None], N0 @ R.T, N0)
    n = np.cross(X[T[:, 1]] - X[T[:, 0]], X[T[:, 2]] - X[T[:, 0]]); flip = (np.einsum("ij,ij->i", n, Ne) < 0) & (np.linalg.norm(N0, axis=1) > 1e-3)
    a = np.abs(np.log1p(np.clip(r, -0.95, None)))
    band = a > 0.005                                    # cạnh có biến dạng (vùng gập)
    peak = float(a[L0 > 0.8].max()) if len(a) else 0   # cạnh giãn / co tệ nhất (bỏ cạnh < 0,8 cm: suy biến, không thấy)
    conc = float(np.percentile(a[band], 99) / max(a[band].mean(), 1e-6)) if band.sum() > 20 else 0
    bv = defaultdict(int)
    for e in np.where(a > np.log(1.25))[0]: bv[dom[E[e, 0]]] += 1
    worst = sorted(bv.items(), key=lambda x: -x[1])[:2]
    return dict(bad=float((np.abs(r) > 0.25).mean() * 100), flip=int(flip.sum()), peak=np.expm1(peak) * 100, conc=conc,
                st=float(r.max() * 100), co=float(-r.min() * 100), worst=[(str(b), c) for b, c in worst], r=r)

# dải góc (độ) mỗi trục; dấu theo bên: R = tay/chân phía x âm. Vai ở tư thế chữ T: z âm (R) = hạ tay, y = đưa trước / sau, x = xoắn
ROM = {"Root_M": dict(x=(-30, 30), y=(-45, 45), z=(-25, 25)), "Spine1_M": dict(x=(-30, 45), y=(-40, 40), z=(-30, 30)), "Chest_M": dict(x=(-30, 45), y=(-40, 40), z=(-30, 30)),
       "Neck_M": dict(x=(-40, 50), y=(-60, 60), z=(-35, 35)), "Head_M": dict(x=(-40, 40), y=(-70, 70), z=(-30, 30))}
for s, sg in (("R", -1), ("L", 1)):
    ROM.update({f"Scapula_{s}": dict(y=(-25, 25), z=(-25, 25)), f"Shoulder_{s}": dict(x=(-80, 80), y=(-90, 90), z=(-90, 80) if s == "L" else (-80, 90)),
                f"Elbow_{s}": dict(y=(0, 140) if s == "R" else (-140, 0), x=(-60, 60)), f"Wrist_{s}": dict(x=(-60, 60), y=(-45, 45), z=(-70, 70)),
                f"Hip_{s}": dict(x=(-110, 40), y=(-40, 40), z=(-45, 45)), f"Knee_{s}": dict(x=(0, 140)), f"Ankle_{s}": dict(x=(-40, 40), z=(-20, 20)), f"Toes_{s}": dict(x=(-40, 40))})
    for fn in ["Middle", "Index", "Ring", "Pinky"]:
        ROM[f"{fn}Finger1_{s}"] = dict(z=(0, 90) if s == "L" else (-90, 0), y=(-20, 20)); ROM[f"{fn}Finger2_{s}"] = dict(z=(0, 100) if s == "L" else (-100, 0))
    ROM[f"ThumbFinger1_{s}"] = dict(y=(-45, 45), z=(-30, 30)); ROM[f"ThumbFinger2_{s}"] = dict(y=(-60, 60))

def sweep(j, ax, lo, hi, step=15):
    angs = sorted(set([a for a in range(int(lo), int(hi) + 1, step) if a] + [int(lo), int(hi)]) - {0})
    res = [(a, measure(pose(j, ax, a))) for a in angs]
    return max(res, key=lambda t: (t[1]["peak"], t[1]["flip"])), res

def wire(X, j, out, r):
    from PIL import Image, ImageDraw
    c = P[j]; box = 45; ims = []
    for view in ("front", "side"):
        iu, su = (0, 1) if view == "front" else (2, -1)
        U = X[:, iu] * su; Vv = X[:, 1]; D = X[:, 2] if view == "front" else X[:, 0]
        u0, v0 = c[iu] * su - box, c[1] - box; px = 9; Wd = int(2 * box * px)
        img = Image.new("RGB", (Wd, Wd), (24, 26, 34)); dr = ImageDraw.Draw(img); f = lambda u, v: ((u - u0) * px, (v0 + 2 * box - v) * px)
        tri = np.stack([U[T], Vv[T], D[T]], -1); nz = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])[:, 2]
        er = {}
        for k, (a, b) in enumerate(E): er[(a, b)] = r[k]
        for t in np.argsort(tri[:, :, 2].mean(1)):
            sh = int(60 + 120 * min(1, abs(nz[t]) / (np.linalg.norm(np.cross(tri[t, 1] - tri[t, 0], tri[t, 2] - tri[t, 0])) + 1e-9)))
            dr.polygon([f(*tri[t, k, :2]) for k in range(3)], fill=(sh, sh, int(sh * 1.05)))
            for k in range(3):
                a, b = sorted((T[t, k], T[t, (k + 1) % 3])); q = er.get((a, b), 0)
                col = (255, int(200 * max(0, 1 - q * 3)), int(200 * max(0, 1 - q * 3))) if q > 0.05 else (int(200 * max(0, 1 + q * 3)), int(200 * max(0, 1 + q * 3)), 255) if q < -0.05 else (40, 40, 48)
                dr.line([f(*tri[t, k, :2]), f(*tri[t, (k + 1) % 3, :2])], fill=col, width=1)
        ims.append(img)
    o = Image.new("RGB", (ims[0].width * 2 + 6, ims[0].height)); o.paste(ims[0], (0, 0)); o.paste(ims[1], (ims[0].width + 6, 0)); o.save(out)

if "--render" in sys.argv or "--wire" in sys.argv:
    k = sys.argv.index("--render" if "--render" in sys.argv else "--wire"); j, ax, dg, out = sys.argv[k + 1], sys.argv[k + 2], float(sys.argv[k + 3]), sys.argv[k + 4]
    X = pose(j, ax, dg)
    if "--render" in sys.argv: json.dump([{"name": mesh["name"], "verts": X.ravel().round(3).tolist(), "tris": mesh["tris"]}], open(out, "w"))
    else: m = measure(X); wire(X, j, out, m["r"]); print("peak %.0f%%  stretch %.0f%%  compress %.0f%%  conc %.1f  flip %d" % (m["peak"], m["st"], m["co"], m["conc"], m["flip"]))
    sys.exit()
rows = []
for j, axes in ROM.items():
    if j not in P or j not in names: continue
    for ax, (lo, hi) in axes.items():
        (a, m), _ = sweep(j, ax, lo, hi); rows.append((j, ax, lo, hi, a, m))
        bad = lambda m: m["peak"] > 80 or m["flip"] > 8 or m["bad"] > 0.5
        flag = "BAD" if bad(m) else ""
        print("%-17s %s [%4d..%4d] tệ nhất %+4d°  đỉnh %4.0f%%  hỏng %4.2f%%  dồn %4.1f  lật %3d  %s %s" % (j, ax, lo, hi, a, m["peak"], m["bad"], m["conc"], m["flip"], m["worst"], flag))
print("TB đỉnh %.0f%%  TB hỏng %.2f%%  tổng lật %d  số BAD %d" % (np.mean([r[5]["peak"] for r in rows]), np.mean([r[5]["bad"] for r in rows]), sum(r[5]["flip"] for r in rows), sum(1 for r in rows if bad(r[5]))))
