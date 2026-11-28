"""Dựng rig Spine cho rương battle pass (Ruong_battle_pass_anim.psd, canvas 1198x1024). Ảnh: images/ (extract_layers.py).
Chạy: .venv/Scripts/python.exe -I work/battle_pass/spine/RuongBattlePass/build_ruong.py [out.json]
Toạ độ canvas PSD (y xuống) -> Spine (gốc root = giữa đáy rương, y lên). Giữ anim đã có trong file khi dựng lại.
CẢNH BÁO: từ lần dựng thứ hai KHÔNG chạy đè khi người dùng đã sửa lưới / weight trên Spine Live (đọc `spine_live_cmd.py history`
trước; script từ chối nếu file đã có và không đặt RUONG_REBUILD=1).

PSD = bảng tham chiếu 5 trạng thái (không cửa / đóng / đóng + vòng / mở vừa / mở hẳn) -> mỗi trạng thái cửa là một nhóm slot riêng
(đổi bằng attachment), setup = cửa đóng + núm + vòng. Xương (mọi xương ngang, góc 0 trừ chồng xu = 90 chỉ lên):
  root > chest (thân rương: squash / nghiêng cả rương + xu bên trong + cửa)
           > in_stack5 / in_stack4 / in_stack3 (chồng xu trong rương, gốc ở đáy chồng) / in_c1..c4 (xu lẻ xếp cột) / in_tilt
           > door_c (cửa đóng, bản lề trái) > door_c_tip (mép tự do) / dial (núm xoay) / ring (vòng tròn)
           > door_h (cửa mở vừa, bản lề trái) > door_h_tip > bolt_h1..3 ; door_h > knob_h (núm lồi)
           > door_o (cửa mở hẳn, bản lề PHẢI, xương hướng sang trái) > door_o_tip > bolt_o1..3
  root > fg_stack3 / fg_tilt1 / fg_c1 / fg_c2 / fg_c3 / fg_tilt2 / fg_tilt3 (xu ngoài, đứng yên theo đất khi rương squash)
Slot `cavity_clip` (clipping attachment, polygon = viền alpha của cavity) cắt các xu TRONG rương đúng như layer clip của PSD.
Cửa = lưới 2 xương bản lề -> mép tự do (smoothstep dọc ngang cửa): scaleX bản lề giả "quay cánh cửa", xoay tip = cửa rung.
"""
import json, math, os, sys
import numpy as np, cv2
from PIL import Image
from scipy.spatial import Delaunay

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
FPS = 30
OX, OY = 700, 905           # canvas (px, py) -> spine (px - OX, OY - py): gốc = giữa đáy chân rương
LJ = json.load(open(os.path.join(HERE, "layers.json"), encoding="utf8"))
LAY = LJ["layers"]


def S(px, py): return (px - OX, OY - py)


# ---------------------------------------------------------------- xương
BONES, BW = [], {}
COV = {}      # tên mesh -> tỉ lệ pixel đục được lưới phủ


def bone(name, parent, cx, cy, ang=0.0, length=40, to=None, **kw):
    """vị trí canvas (cx, cy); góc THẾ GIỚI `ang` (độ, 0 = +x, ngược chiều kim đồng hồ, 90 = lên) hoặc `to` = điểm canvas bone chỉ tới"""
    wx, wy = S(cx, cy)
    if to is not None:
        tx, ty = S(*to); ang = math.degrees(math.atan2(ty - wy, tx - wx)); length = math.hypot(tx - wx, ty - wy)
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


# điểm neo (canvas PSD), đo từ ảnh
HINGE_C = (366, 515)       # cửa đóng: mép hồng trái x 366, phải 767 (alpha), tâm dọc 515
HINGE_H = (363, 497)       # cửa mở vừa: mép hồng trái 363, mép tự do 549, dọc 272-720
HINGE_O = (378, 507)       # cửa mở hẳn: bản lề bên PHẢI (x 378), mép tự do bên trái (x 135), dọc 275-739
DIAL_C = (597, 528)        # tâm mặt núm (centroid vùng xanh đậm của layer 24)
RING_C = (648, 513)        # tâm vòng tròn (centroid alpha)
KNOB_H = (371, 523)        # núm lồi của cửa mở vừa (centroid vùng xanh)


def build():
    BONES.clear(); BW.clear()
    bone("root", None, 700, 905, 90, 20)
    bone("chest", "root", 700, 905, 0, 300)
    # --- xu trong rương (gốc ở đáy chồng, chỉ lên)
    bone("in_stack5", "chest", 651, 676, 90, 330)
    bone("in_stack4", "chest", 789, 722, 90, 275)
    bone("in_stack3", "chest", 638, 730, 90, 215)
    for i, cy in enumerate((634.5, 581.5, 529.5, 475.5), 1):          # c1 (thấp nhất) .. c4 (cao nhất), tâm ảnh
        bone(f"in_c{i}", "chest", 489, cy, 0, 70)
    bone("in_tilt", "chest", 473, 372, 0, 70)
    # --- cửa đóng
    bone("door_c", "chest", *HINGE_C, 0, 200)
    bone("door_c_tip", "door_c", 566, HINGE_C[1], 0, 200)
    bone("dial", "door_c", *DIAL_C, 0, 60)
    bone("ring", "door_c", *RING_C, 0, 100)
    # --- cửa mở vừa
    bone("door_h", "chest", *HINGE_H, 0, 93)
    bone("door_h_tip", "door_h", 456, HINGE_H[1], 0, 93)
    bone("knob_h", "door_h", *KNOB_H, 0, 70)
    for i, (cx, cy) in enumerate(((530, 424), (530, 529.5), (533.5, 627.5)), 1):
        bone(f"bolt_h{i}", "door_h_tip", cx, cy, 0, 40)
    # --- cửa mở hẳn (xương hướng sang trái, scaleX = co về bản lề phải)
    bone("door_o", "chest", *HINGE_O, 180, 120)
    bone("door_o_tip", "door_o", 258, HINGE_O[1], 180, 120)
    for i, (cx, cy) in enumerate(((179, 424), (179, 529.5), (176.5, 627.5)), 1):
        bone(f"bolt_o{i}", "door_o_tip", cx, cy, 0, 40)
    # --- xu ngoài (cha = root: đứng yên theo đất khi rương squash)
    bone("fg_stack3", "root", 705, 922, 90, 225)
    bone("fg_tilt1", "root", 714.5, 646.5, 0, 70)
    bone("fg_c1", "root", 409, 818.5, 0, 70)
    bone("fg_c2", "root", 438, 757.5, 0, 70)
    bone("fg_c3", "root", 1069, 786.5, 0, 70)
    bone("fg_tilt2", "root", 1030, 681.5, 0, 70)
    bone("fg_tilt3", "root", 889, 825.5, 0, 70)


# ---------------------------------------------------------------- lưới
def ss(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def mesh_points(mask, eps=1.5, max_edge=40, step=80, extra=()):
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
    inner = cv2.erode(mask.astype(np.uint8), np.ones((15, 15), np.uint8))
    ys, xs = np.mgrid[0:mask.shape[0]:step, 0:mask.shape[1]:step]
    pts = [(x + (y // step % 2) * step / 2, y) for y, x in zip(ys.ravel(), xs.ravel())]
    pts += [tuple(p) for p in extra]
    pts = [p for p in pts if 0 <= p[0] < mask.shape[1] and 0 <= p[1] < mask.shape[0] and inner[int(p[1]), int(p[0])]]
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
    img = np.array(Image.open(os.path.join(HERE, "images", name + ".png")))
    h, w = img.shape[:2]; px0, py0 = LAY[name]["bbox"][:2]
    mask = img[..., 3] > 8
    if kw.pop("hollow", False):    # vật rỗng (vòng): viền ngoài = hull, MỌI lỗ (giữa vòng + các ô khuyết) lấy điểm dọc viền lỗ làm đỉnh trong,
        # tam giác nằm trong lỗ bị tri_filter bỏ -> lưới (và lớp tô weight) đúng hình vòng, không phải hình chữ nhật
        me = kw.get("max_edge", 30)
        m0 = cv2.dilate(mask.astype(np.uint8), np.ones((5, 5), np.uint8))
        cs, hi = cv2.findContours(m0, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        def sub(c, eps=1.2):
            ap = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float); out = []
            for i in range(len(ap)):
                a, b = ap[i], ap[(i + 1) % len(ap)]; k = max(1, int(math.ceil(np.linalg.norm(b - a) / me)))
                out += [a + (b - a) * j / k for j in range(k)]
            return np.array(out)
        outer = max([i for i in range(len(cs)) if hi[0][i][3] < 0], key=lambda i: cv2.contourArea(cs[i]))
        hull = sub(cs[outer])
        holes = [sub(cs[i]) for i in range(len(cs)) if hi[0][i][3] == outer and cv2.contourArea(cs[i]) > 20]
        inner = np.vstack(holes) if holes else np.zeros((0, 2))
        m = cv2.dilate(m0, np.ones((9, 9), np.uint8))
    elif kw.pop("quad", False):      # lưới chữ nhật phủ cả ảnh (không dùng cho vòng nữa: lớp tô weight thành hình chữ nhật đỏ phủ cả núm)
        n = kw.get("n", 4); xs_, ys_ = np.linspace(0, w, n + 1), np.linspace(0, h, n + 1)
        hull = np.array([(x, 0) for x in xs_[:-1]] + [(w, y) for y in ys_[:-1]] + [(x, h) for x in xs_[:0:-1]] + [(0, y) for y in ys_[:0:-1]], float)
        inner = np.array([(x, y) for y in ys_[1:-1] for x in xs_[1:-1]], float).reshape(-1, 2)
        m = np.ones((h + 1, w + 1), np.uint8)
    else:
        hull, inner, m = mesh_points(mask, **kw)
    allp = np.vstack([hull, inner]) if len(inner) else hull
    tris = tri_filter(allp, m)
    used = sorted(set(i for t in tris for i in t))
    remap = {o: n for n, o in enumerate([i for i in range(len(hull)) if i in used] + [i for i in used if i >= len(hull)])}
    order = sorted(remap, key=lambda o: remap[o]); allp = allp[order]
    nh = sum(1 for o in order if o < len(hull)); tris = [[remap[i] for i in t] for t in tris]
    cov_m = np.zeros(mask.shape, np.uint8)       # kiểm phủ: phần ảnh đục (alpha > 8) nằm trong tam giác lưới
    for t in tris: cv2.fillPoly(cov_m, [np.round(allp[t]).astype(np.int32)], 1)
    COV[name] = float((cov_m.astype(bool) & mask).sum() / max(1, mask.sum()))
    uvs, verts = [], []
    wsum = {}
    for (x, y) in allp:
        uvs += [round(x / w, 5), round(y / h, 5)]
        cx, cy = px0 + x, py0 + y
        wx, wy = S(cx, cy)
        ws = weight_fn(cx, cy)
        tot = sum(v for _, v in ws); ws = [(b, v / tot) for b, v in ws if v / tot > 0.01]
        tot = sum(v for _, v in ws); ws = [(b, v / tot) for b, v in ws]
        verts.append(len(ws))
        for b, v in ws:
            lx, ly = to_local(b, wx, wy)
            verts += [BIDX[b], round(lx, 3), round(ly, 3), round(v, 4)]
            wsum[b] = wsum.get(b, 0) + v
    edges = []
    for i in range(nh): edges += [i * 2, ((i + 1) % nh) * 2]
    return {"type": "mesh", "uvs": uvs, "triangles": [i for t in tris for i in t], "vertices": verts, "hull": nh,
            "edges": edges, "width": w, "height": h}, len(allp), len(tris), wsum


# ---------------------------------------------------------------- weight (cx, cy = canvas PSD)
def one(b): return lambda cx, cy: [(b, 1.0)]


def hinge_tip(xh, xf, bh, bt):
    """cánh cửa: bản lề (100% ở mép bản lề) -> mép tự do (100% ở mép tự do), smoothstep theo trục ngang; xf < xh cũng được"""
    def f(cx, cy):
        t = ss((cx - xh) / (xf - xh)); return [(bh, 1 - t + 1e-6), (bt, t + 1e-6)]
    return f


def with_local(local, base):
    """local = [(bone, w)] tổng <= 1, phần còn lại chia theo base(cx, cy)"""
    def f(cx, cy):
        loc = [(b, w(cx, cy)) for b, w in local]; t = sum(w for _, w in loc)
        if t > 1: loc = [(b, w / t) for b, w in loc]; t = 1.0
        return [(b, w) for b, w in loc if w > 0] + [(b, w * (1 - t)) for b, w in base(cx, cy)]
    return f


def disc(center, r_full, r_zero):
    return lambda cx, cy: 1 - ss((math.hypot(cx - center[0], cy - center[1]) - r_full) / (r_zero - r_full))


def build_all():
    build()
    global BIDX
    BIDX = {b["name"]: i for i, b in enumerate(BONES)}
    spec = [   # (slot / attachment, hàm weight, tham số lưới)
        ("chest_body", one("chest"), dict(max_edge=110, step=150)),
        ("cavity", one("chest"), dict(max_edge=90, step=140)),
        ("in_stack5", one("in_stack5"), dict(max_edge=60, step=85)),
        ("in_stack4", one("in_stack4"), dict(max_edge=60, step=85)),
        ("in_c1", one("in_c1"), dict(max_edge=60, step=85)),
        ("in_c2", one("in_c2"), dict(max_edge=60, step=85)),
        ("in_c3", one("in_c3"), dict(max_edge=60, step=85)),
        ("in_c4", one("in_c4"), dict(max_edge=60, step=85)),
        ("in_tilt", one("in_tilt"), dict(max_edge=55, step=80)),
        ("in_stack3", one("in_stack3"), dict(max_edge=60, step=85)),
        ("fg_stack3", one("fg_stack3"), dict(max_edge=60, step=85)),
        ("fg_tilt1", one("fg_tilt1"), dict(max_edge=55, step=80)),
        ("fg_c1", one("fg_c1"), dict(max_edge=60, step=85)),
        ("fg_c2", one("fg_c2"), dict(max_edge=60, step=85)),
        ("fg_c3", one("fg_c3"), dict(max_edge=60, step=85)),
        ("fg_tilt2", one("fg_tilt2"), dict(max_edge=55, step=80)),
        ("fg_tilt3", one("fg_tilt3"), dict(max_edge=55, step=80)),
        ("door_o", hinge_tip(HINGE_O[0], 135, "door_o", "door_o_tip"), dict(max_edge=60, step=70)),
        ("bolt_o1", one("bolt_o1"), dict(max_edge=30, step=45)),
        ("bolt_o2", one("bolt_o2"), dict(max_edge=30, step=45)),
        ("bolt_o3", one("bolt_o3"), dict(max_edge=30, step=45)),
        ("door_c", hinge_tip(HINGE_C[0], 767, "door_c", "door_c_tip"), dict(max_edge=70, step=90)),
        ("dial", one("dial"), dict(max_edge=45, step=60)),
        ("door_h", with_local([("knob_h", disc(KNOB_H, 70, 120))], hinge_tip(HINGE_H[0], 549, "door_h", "door_h_tip")),
         dict(max_edge=45, step=65)),
        ("bolt_h1", one("bolt_h1"), dict(max_edge=30, step=45)),
        ("bolt_h2", one("bolt_h2"), dict(max_edge=30, step=45)),
        ("bolt_h3", one("bolt_h3"), dict(max_edge=30, step=45)),
        ("ring", one("ring"), dict(hollow=True, max_edge=30)),
    ]
    SLOT_BONE = {n: n for n, _, _ in spec}
    SLOT_BONE.update({"chest_body": "chest", "cavity": "chest", "cavity_clip": "chest", "door_c": "door_c", "door_h": "door_h", "door_o": "door_o"})
    # setup pose = cửa đóng: núm + vòng hiện, hai trạng thái còn lại ẩn (đổi bằng attachment, xem rig_demo)
    HIDDEN = {"door_o", "bolt_o1", "bolt_o2", "bolt_o3", "door_h", "bolt_h1", "bolt_h2", "bolt_h3"}
    SLOT_ORDER = ["chest_body", "cavity", "cavity_clip", "in_stack5", "in_stack4", "in_c1", "in_c2", "in_c3", "in_c4", "in_tilt", "in_stack3",
                  "fg_stack3", "fg_tilt1", "fg_c1", "fg_c2", "fg_c3", "fg_tilt2", "fg_tilt3",
                  "door_o", "bolt_o1", "bolt_o2", "bolt_o3", "door_c", "dial", "door_h", "bolt_h1", "bolt_h2", "bolt_h3", "ring"]
    skin, info = {}, {}
    for nm, fn, kw in spec:
        att, nv, nt, ws = make_mesh(nm, fn, **kw); skin[nm] = {nm: att}; info[nm] = (nv, nt, ws)
    # clipping: viền alpha của cavity (PSD: xu trong rương clip vào layer này), toạ độ trong xương chest
    img = np.array(Image.open(os.path.join(HERE, "images", "cavity.png")))[..., 3] > 128
    img = cv2.morphologyEx(img.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cs, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea); ap = cv2.approxPolyDP(c, 2.0, True)[:, 0, :].astype(float)
    x0, y0 = LAY["cavity"]["bbox"][:2]
    vs = []
    for (x, y) in ap:
        lx, ly = to_local("chest", *S(x0 + x, y0 + y)); vs += [round(lx, 2), round(ly, 2)]
    skin["cavity_clip"] = {"cavity_clip": {"type": "clipping", "end": "in_stack3", "vertexCount": len(ap), "vertices": vs, "color": "ce3a3aff"}}
    info["cavity_clip"] = (len(ap), 0, {})
    slots = []
    for n in SLOT_ORDER:
        s = {"name": n, "bone": SLOT_BONE[n]}
        if n not in HIDDEN: s["attachment"] = n
        slots.append(s)
    sk = {"skeleton": {"spine": "4.2.43", "fps": FPS, "images": "./images/"}, "bones": BONES, "slots": slots,
          "skins": [{"name": "default", "attachments": {n: skin[n] for n in SLOT_ORDER}}], "animations": {}}
    return sk, info


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "ruong.json")
    prev = json.load(open(out, encoding="utf8")) if os.path.exists(out) else None
    if prev and not os.environ.get("RUONG_REBUILD"):
        sys.exit("File %s đã có: người dùng có thể đã sửa lưới / weight. Đọc spine_live_cmd.py history rồi mới đặt RUONG_REBUILD=1." % out)
    sk, info = build_all()
    if prev and prev.get("animations"): sk["animations"] = prev["animations"]      # giữ anim đã có
    if not os.environ.get("ANIM_KIT_DRY"):
        try:
            import spine_live_cmd
            spine_live_cmd.claude_backup(out, "Claude dựng rig RuongBattlePass")
        except Exception as e:
            print("(không ghi được backup Spine Live:", e, ")")
    json.dump(sk, open(out, "w", encoding="utf8"), indent=1, ensure_ascii=False)
    low = {k: round(v, 4) for k, v in COV.items() if v < 0.995}
    print("Phủ lưới (pixel đục nằm trong tam giác): min %.4f | mesh < 99,5%%: %s" % (min(COV.values()), low or "không có"))
    print("Đã ghi", out, "|", len(sk["bones"]), "xương,", len(sk["slots"]), "slot")
    for k, (nv, nt, ws) in info.items():
        print(f"  {k:11s} {nv:3d} đỉnh / {nt:3d} tam giác | weight:", {b: round(v, 1) for b, v in sorted(ws.items(), key=lambda t: -t[1])})
