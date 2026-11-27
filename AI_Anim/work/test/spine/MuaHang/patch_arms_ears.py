"""Rig 2 tay + 2 tai của mèo (vá lên file hiện có, không đụng layer khác): mỗi cái = chuỗi 2 xương + mesh có weight.
Chạy: .venv/Scripts/python.exe -I work/test/spine/MuaHang/patch_arms_ears.py [json]   (chạy lại an toàn: dựng lại 4 chuỗi từ đầu)
Weight dọc chuỗi: sát gốc (~8-45 px) = xương `mascot` (dính thân, không hở), rồi xương 1, uốn mượt sang xương 2 quanh khớp giữa.
Toạ độ ảnh (px, py; y xuống) -> Spine (px - W/2, H - py)."""
import json, math, os, sys
import numpy as np, cv2
from PIL import Image
from scipy.spatial import Delaunay
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
L = json.load(open(f"{HERE}/layers.json", encoding="utf-8"))
W, H = L["canvas"]
LAY = {r["name"]: r for r in L["layers"]}
S = lambda px, py: (px - W / 2.0, H - py)

# slot: (xương gốc, xương 2, (gốc, khớp, đầu) theo toạ độ ảnh, (a0, a1) vùng dính thân)
CHAINS = {
    "tai1": ("ear_L", "ear_L2", [(340, 272), (333, 236), (325, 198)], (8, 40)),
    "tai2": ("ear_R", "ear_R2", [(615, 360), (600, 290), (478, 238)], (8, 40)),
    "tay2": ("paw_L", "paw_L2", [(195, 445), (140, 470), (95, 500)], (10, 55)),
    "tay1": ("paw_R", "paw_R2", [(505, 498), (555, 455), (612, 410)], (10, 55)),
}


def ss(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def world(bones):
    BW = {}
    for b in bones:
        b.setdefault("x", 0.0); b.setdefault("y", 0.0); b.setdefault("rotation", 0.0)
        p = b.get("parent")
        if p:
            px, py, pa = BW[p]; c, s = math.cos(math.radians(pa)), math.sin(math.radians(pa))
            BW[b["name"]] = (px + c * b["x"] - s * b["y"], py + s * b["x"] + c * b["y"], pa + b["rotation"])
        else:
            BW[b["name"]] = (b["x"], b["y"], b["rotation"])
    return BW


def to_local(BW, name, wx, wy):
    bx, by, a = BW[name]; dx, dy = wx - bx, wy - by
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return dx * c + dy * s, -dx * s + dy * c


def mesh_points(mask, eps=1.2, max_edge=16, step=18):
    m = cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    ap = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
    hull = []
    for i in range(len(ap)):
        a, b = ap[i], ap[(i + 1) % len(ap)]
        n = max(1, int(math.ceil(np.linalg.norm(b - a) / max_edge)))
        for k in range(n): hull.append(a + (b - a) * k / n)
    hull = np.array(hull)
    inner = cv2.erode(mask.astype(np.uint8), np.ones((9, 9), np.uint8))
    ys, xs = np.mgrid[0:mask.shape[0]:step, 0:mask.shape[1]:step]
    pts = [(x + (y // step % 2) * step / 2, y) for y, x in zip(ys.ravel(), xs.ravel())]
    pts = [p for p in pts if 0 <= p[0] < mask.shape[1] and 0 <= p[1] < mask.shape[0] and inner[int(p[1]), int(p[0])]]
    return hull, np.array(pts, float).reshape(-1, 2), cv2.dilate(m, np.ones((7, 7), np.uint8))


def tri_filter(allp, m):
    tri = Delaunay(allp).simplices; keep = []
    h, w = m.shape
    inside = lambda p: 0 <= int(p[0]) < w and 0 <= int(p[1]) < h and m[int(p[1]), int(p[0])] > 0
    for t in tri:
        a, b, c = allp[t]
        if all(inside(q) for q in ((a + b + c) / 3, (a + b) / 2, (b + c) / 2, (a + c) / 2)): keep.append([int(i) for i in t])
    return keep


def arclen(pts, v):
    """vị trí dọc đường gấp khúc (khoảng cách từ gốc theo trục), chiếu điểm v lên đoạn gần nhất"""
    best, acc = None, 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        a, b = np.array(a, float), np.array(b, float); ab = b - a; ln = np.linalg.norm(ab)
        t = float(np.clip(np.dot(v - a, ab) / ln ** 2, 0, 1)); d = np.linalg.norm(a + ab * t - v)
        if best is None or d < best[0]: best = (d, acc + t * ln)
        acc += ln
    return best[1]


def make_mesh(slot, bones_idx, BW, chain):
    b1, b2, pts, (a0, a1) = chain
    img = np.array(Image.open(f"{HERE}/images/{slot}.png"))
    h, w = img.shape[:2]; px0, py0 = LAY[slot]["x"], LAY[slot]["y"]
    hull, inner, m = mesh_points(img[..., 3] > 8)
    allp = np.vstack([hull, inner]) if len(inner) else hull
    tris = tri_filter(allp, m)
    used = sorted(set(i for t in tris for i in t))
    remap = {o: n for n, o in enumerate([i for i in range(len(hull)) if i in used] + [i for i in used if i >= len(hull)])}
    order = sorted(remap, key=lambda o: remap[o]); allp = allp[order]
    nh = sum(1 for o in order if o < len(hull)); tris = [[remap[i] for i in t] for t in tris]
    L1 = math.dist(pts[0], pts[1]); L2 = math.dist(pts[1], pts[2]); bz = 0.3 * min(L1, L2)
    uvs, verts = [], []
    for (x, y) in allp:
        uvs += [round(x / w, 5), round(y / h, 5)]
        cx, cy = px0 + x, py0 + y
        a = arclen(pts, np.array([cx, cy], float))
        wm = 1 - ss((a - a0) / float(a1 - a0))                       # dính thân mèo ở gốc
        w2 = ss((a - (L1 - bz)) / (2 * bz))                          # uốn sang xương 2 quanh khớp
        ws = [("mascot", wm), (b1, (1 - wm) * (1 - w2)), (b2, (1 - wm) * w2)]
        ws = [(b, v) for b, v in ws if v > 0.01]; tot = sum(v for _, v in ws); ws = [(b, v / tot) for b, v in ws]
        wx, wy = S(cx, cy)
        verts.append(len(ws))
        for b, v in ws:
            lx, ly = to_local(BW, b, wx, wy)
            verts += [bones_idx[b], round(lx, 3), round(ly, 3), round(v, 4)]
    edges = []
    for i in range(nh): edges += [i * 2, ((i + 1) % nh) * 2]
    return {"type": "mesh", "uvs": uvs, "triangles": [i for t in tris for i in t], "vertices": verts, "hull": nh,
            "edges": edges, "width": w, "height": h}, len(allp), len(tris)


def apply(path):
    sk = json.load(open(path, encoding="utf-8"))
    names2 = {c[1] for c in CHAINS.values()}
    sk["bones"] = [b for b in sk["bones"] if b["name"] not in names2]
    bones = {b["name"]: b for b in sk["bones"]}
    BW = world(sk["bones"])
    # đặt lại gốc xương cơ sở (ear_L, ear_R, paw_L, paw_R) và thêm xương 2
    for slot, (b1, b2, pts, _) in CHAINS.items():
        (x0, y0), (x1, y1), (x2, y2) = [S(*p) for p in pts]
        a1 = math.degrees(math.atan2(y1 - y0, x1 - x0)); a2 = math.degrees(math.atan2(y2 - y1, x2 - x1))
        par = bones[b1]["parent"]; px, py, pa = BW[par]
        c, s = math.cos(math.radians(pa)), math.sin(math.radians(pa)); dx, dy = x0 - px, y0 - py
        bones[b1].update({"x": round(dx * c + dy * s, 3), "y": round(-dx * s + dy * c, 3), "rotation": round(a1 - pa, 3),
                          "length": round(math.hypot(x1 - x0, y1 - y0), 2)})
        BW[b1] = (x0, y0, a1)
        nb = {"name": b2, "parent": b1, "length": round(math.hypot(x2 - x1, y2 - y1), 2), "x": round(math.hypot(x1 - x0, y1 - y0), 3), "y": 0.0,
              "rotation": round(a2 - a1, 3)}
        sk["bones"].append(nb); BW[b2] = (x1, y1, a2)
    BW = world(sk["bones"])
    bidx = {b["name"]: i for i, b in enumerate(sk["bones"])}
    info = {}
    for slot, ch in CHAINS.items():
        att, nv, nt = make_mesh(slot, bidx, BW, ch)
        sk["skins"][0]["attachments"][slot] = {slot: att}; info[slot] = (nv, nt)
        for sl in sk["slots"]:
            if sl["name"] == slot: sl["bone"] = ch[0]
    try:
        import spine_live_cmd
        spine_live_cmd.claude_backup(path, "Claude rig 2 tay + 2 tai mèo (mesh + weight)")
    except Exception as e:
        print("(không ghi được backup Spine Live:", e, ")")
    json.dump(sk, open(path, "w", encoding="utf-8"), indent=1)
    print("Đã ghi", path, "|", len(sk["bones"]), "xương |", {k: "%d đỉnh / %d tam giác" % v for k, v in info.items()})


if __name__ == "__main__":
    apply(sys.argv[1] if len(sys.argv) > 1 else f"{HERE}/muahang.json")
