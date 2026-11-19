"""Dựng rig Spine cho Unlock (ruy băng 3 nơ + kéo cắt). Chạy: .venv/Scripts/python.exe -I work/unlock/spine/Unlock/build_unlock.py
Nguồn: images/*.png + parts.json (từ prep_images.py). Toạ độ canvas PSD (y xuống) -> Spine (gốc root = giữa-đáy canvas, y lên).
Rig: ctrl tổng; mỗi nơ 1 xương hoa + 1 xương đuôi; dải ruy băng mỗi nửa 1 chuỗi 4 xương (mesh weight, cắt ở X_SEAM dưới nơ giữa);
kéo: sc_root (độc lập ctrl, để bay vào) -> sc_A / sc_B quay quanh ốc, ảnh region cứng."""
import json, math, os, sys
import numpy as np, cv2
from PIL import Image
from scipy.spatial import Delaunay

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "parts.json")))
W, H = P["canvas"]; PART = P["parts"]; XS = P["x_seam"]
FPS = 30
OX, OY = 882, H            # canvas (px,py) -> spine (px-OX, OY-py)


def S(px, py): return (px - OX, OY - py)


# ---------------------------------------------------------------- xương
BONES, BW = [], {}          # BW[name] = (wx, wy, wang)


def bone(name, parent, cx, cy, ang, length=40, **kw):
    """vị trí canvas (cx, cy), góc THẾ GIỚI (độ, 0 = +x, ngược chiều kim đồng hồ, -90 = chỉ xuống)"""
    wx, wy = S(cx, cy)
    if parent is None:
        x, y, rot = wx, wy, ang
    else:
        pwx, pwy, pa = BW[parent]
        dx, dy = wx - pwx, wy - pwy; c, s = math.cos(math.radians(pa)), math.sin(math.radians(pa))
        x, y, rot = dx * c + dy * s, -dx * s + dy * c, ang - pa
    BW[name] = (wx, wy, ang)
    b = {"name": name, "length": round(length, 2), "x": round(x, 3), "y": round(y, 3), "rotation": round(rot, 3)}
    if parent: b["parent"] = parent
    b.update(kw); BONES.append(b)


def to_local(name, wx, wy):
    bx, by, a = BW[name]; dx, dy = wx - bx, wy - by
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return dx * c + dy * s, -dx * s + dy * c


# ---------------------------------------------------------------- đo dải ruy băng (đường tâm theo cột)
RB = {k: np.array(Image.open(os.path.join(HERE, "images", "ribbon_%s.png" % k)))[..., 3] > 128 for k in "LR"}


def centre_y(px):
    k = "L" if px <= XS else "R"; col = RB[k][:, int(px) - PART["ribbon_" + k]["x"]]; ys = np.where(col)[0]
    return PART["ribbon_" + k]["y"] + (ys.min() + ys.max()) / 2.0


FLOWER = {"bow_L": (120, 135), "bow_R": (1644, 135), "bow_M": (882, 527)}     # tâm hoa nơ (canvas)
TAIL = {"bow_L": (120, 245, 190), "bow_R": (1646, 245, 190), "bow_M": (882, 640, 207)}   # (x, y đầu đuôi, dài)
RIB_X = [150, 330, 520, 700, 882]                       # khớp chuỗi dải (nửa trái); nửa phải đối xứng qua X = 882
SC_PIVOT = (1166, 596)                                    # ốc kéo (canvas)
SC_ANG = {"A": 157.0, "B": 106.0}                         # trục lưỡi từ ốc tới mũi (độ thế giới), đo từ ảnh


def build():
    BONES.clear(); BW.clear()
    bone("root", None, OX, OY, 0, 60)
    bone("ctrl", "root", 882, 450, 0, 60)
    for nm, k in (("bowL", "bow_L"), ("bowR", "bow_R"), ("bowM", "bow_M")):
        fx, fy = FLOWER[k]; tx, ty, tl = TAIL[k]
        bone(nm, "ctrl", fx, fy, 0, 60)
        bone(nm + "_t", nm, tx, ty, -90, tl)
    # chuỗi dải
    for side, sgn in (("L", 1), ("R", -1)):
        xs = [RIB_X[i] if sgn == 1 else 2 * XS - RIB_X[i] for i in range(5)]
        pts = [(x, centre_y(x)) for x in xs]
        prev = "ctrl"
        for i in range(4):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            ang = math.degrees(math.atan2(-(y1 - y0), x1 - x0))
            bone("rib%s%d" % (side, i), prev, x0, y0, ang, math.hypot(x1 - x0, y1 - y0))
            prev = "rib%s%d" % (side, i)
    # kéo
    bone("sc_root", "root", SC_PIVOT[0], SC_PIVOT[1], 0, 40)
    bone("sc_B", "sc_root", SC_PIVOT[0], SC_PIVOT[1], SC_ANG["B"], 200)
    bone("sc_A", "sc_root", SC_PIVOT[0], SC_PIVOT[1], SC_ANG["A"], 200)


# ---------------------------------------------------------------- lưới
def ss(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def mesh_points(mask, eps=1.3, max_edge=30, step=56):
    """viền = contour (mask nới 2 px) -> approxPolyDP -> chia cạnh dài; điểm trong = lưới step px nằm trong mask co 6 px"""
    m = cv2.dilate(mask.astype(np.uint8), np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    ap = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
    hull = []
    for i in range(len(ap)):
        a, b = ap[i], ap[(i + 1) % len(ap)]
        n = max(1, int(math.ceil(np.linalg.norm(b - a) / max_edge)))
        for k in range(n): hull.append(a + (b - a) * k / n)
    hull = np.array(hull)
    inner = cv2.erode(mask.astype(np.uint8), np.ones((13, 13), np.uint8))
    ys, xs = np.mgrid[0:mask.shape[0]:step, 0:mask.shape[1]:step]
    pts = [(x + (y // step % 2) * step / 2, y) for y, x in zip(ys.ravel(), xs.ravel())]
    pts = [p for p in pts if 0 <= p[0] < mask.shape[1] and inner[int(p[1]), int(p[0])]]
    return hull, np.array(pts, float).reshape(-1, 2), cv2.dilate(m, np.ones((9, 9), np.uint8))


def tri_filter(allp, m):
    tri = Delaunay(allp).simplices; keep = []
    h, w = m.shape
    def inside(p): return 0 <= int(p[0]) < w and 0 <= int(p[1]) < h and m[int(p[1]), int(p[0])] > 0
    for t in tri:
        a, b, c = allp[t]
        if all(inside(q) for q in ((a + b + c) / 3, (a + b) / 2, (b + c) / 2, (a + c) / 2)): keep.append([int(i) for i in t])
    return keep


def make_mesh(name, weight_fn, **kw):
    part = PART[name]; img = np.array(Image.open(os.path.join(HERE, "images", name + ".png")))
    mask = img[..., 3] > 8
    hull, inner, m = mesh_points(mask, **kw)
    allp = np.vstack([hull, inner]) if len(inner) else hull
    tris = tri_filter(allp, m)
    used = sorted(set(i for t in tris for i in t))
    remap = {o: n for n, o in enumerate([i for i in range(len(hull)) if i in used] + [i for i in used if i >= len(hull)])}
    order = sorted(remap, key=lambda o: remap[o]); allp = allp[order]
    nh = sum(1 for o in order if o < len(hull)); tris = [[remap[i] for i in t] for t in tris]
    uvs, verts = [], []
    for (x, y) in allp:
        uvs += [round(x / part["w"], 5), round(y / part["h"], 5)]
        cx, cy = part["x"] + x, part["y"] + y            # canvas
        wx, wy = S(cx, cy)
        ws = weight_fn(cx, cy)
        tot = sum(w for _, w in ws); ws = [(b, w / tot) for b, w in ws if w / tot > 0.01]
        tot = sum(w for _, w in ws); ws = [(b, w / tot) for b, w in ws]
        verts.append(len(ws))
        for b, w in ws:
            lx, ly = to_local(b, wx, wy)
            verts += [BIDX[b], round(lx, 3), round(ly, 3), round(w, 4)]
    edges = []
    for i in range(nh): edges += [i * 2, ((i + 1) % nh) * 2]
    return {"type": "mesh", "uvs": uvs, "triangles": [i for t in tris for i in t], "vertices": verts, "hull": nh,
            "edges": edges, "width": part["w"], "height": part["h"]}, len(allp), len(tris)


def chain_weight(side):
    xs = [RIB_X[i] if side == "L" else 2 * XS - RIB_X[i] for i in range(5)]
    pts = [S(x, centre_y(x)) for x in xs]
    P = np.array(pts)
    def fn(cx, cy):
        v = np.array(S(cx, cy)); best = (1e18, 0.0)
        for i in range(4):
            a, b = P[i], P[i + 1]; d = b - a; t = np.clip(np.dot(v - a, d) / np.dot(d, d), 0, 1)
            dist = np.linalg.norm(v - (a + d * t))
            if dist < best[0]: best = (dist, i + t)
        u = best[1]                                  # 0..4 dọc chuỗi
        return [("rib%s%d" % (side, j), max(0.0, 1 - abs(u - (j + 0.5)))) for j in range(4)]
    return fn


def bow_weight(nm, k):
    ty = TAIL[k][1]
    def fn(cx, cy):
        t = ss((cy - (ty - 35)) / 75.0)
        return [(nm, 1 - t + 1e-6), (nm + "_t", t + 1e-6)]
    return fn


def region(slot_bone, name, rot_world):
    """region cứng: tâm ảnh -> toạ độ xương slot_bone"""
    pt = PART[name]; lx, ly = to_local(slot_bone, *S(pt["x"] + pt["w"] / 2, pt["y"] + pt["h"] / 2))
    return {"x": round(lx, 3), "y": round(ly, 3), "rotation": round(-BW[slot_bone][2], 3), "width": pt["w"], "height": pt["h"]}


def make():
    build()
    global BIDX
    BIDX = {b["name"]: i for i, b in enumerate(BONES)}
    atts, info = {}, {}
    for nm, side in (("ribbon_L", "L"), ("ribbon_R", "R")):
        atts[nm], nv, nt = make_mesh(nm, chain_weight(side)); info[nm] = (nv, nt)
    for nm, b in (("bow_L", "bowL"), ("bow_R", "bowR"), ("bow_M", "bowM")):
        atts[nm], nv, nt = make_mesh(nm, bow_weight(b, nm), step=48); info[nm] = (nv, nt)
    atts["scissor_B"] = {"type": "region", **region("sc_B", "scissor_B", None)}
    atts["scissor_A"] = {"type": "region", **region("sc_A", "scissor_A", None)}
    order = [("ribbon_L", "ctrl"), ("ribbon_R", "ctrl"), ("bow_L", "bowL"), ("bow_R", "bowR"), ("bow_M", "bowM"),
             ("scissor_B", "sc_B"), ("scissor_A", "sc_A")]
    slots = [{"name": n, "bone": b, "attachment": n} for n, b in order]
    sk = {"skeleton": {"spine": "4.2.43", "fps": FPS, "images": "./images/"}, "bones": BONES, "slots": slots,
          "skins": [{"name": "default", "attachments": {n: {n: atts[n]} for n, _ in order}}], "animations": {}}
    return sk, info


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "unlock.json")
    prev = None
    if os.path.exists(out):
        prev = json.load(open(out, encoding="utf8"))
    sk, info = make()
    if prev and prev.get("animations"): sk["animations"] = prev["animations"]      # giữ anim đã có
    json.dump(sk, open(out, "w", encoding="utf8"), indent=1)
    print("Đã ghi", out, "|", len(sk["bones"]), "xương,", len(sk["slots"]), "slot |", {k: "%d đỉnh / %d tam giác" % v for k, v in info.items()})
