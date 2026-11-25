"""Dựng rig Spine cho PeaceGirl từ 22 layer đã tách (layers.json + images/).
Chạy: .venv/Scripts/python.exe -I work/peace_girl/spine/PeaceGirl/build_peacegirl.py [out.json]
Toạ độ ảnh gốc (px, py; y xuống) -> Spine (px - 368, 1075 - py), gốc root = giữa đáy ảnh. L / R theo màn hình.
CHÚ Ý: dựng lại sẽ đè lưới / weight người dùng sửa trên Spine Live -> chỉ chạy khi chưa có sửa tay (kiểm `notes --all`, `history`).

Rig: root > hip > spine > chest > neck (noScale) > head > eye_L / eye_R (chớp: scaleX), hair_F, hair_B, hairL1 > hairL2, hairR1 > hairR2
     chest > upper_arm_L > forearm_L > hand_L  và  upper_arm_R > forearm_R > hand_R (noScale: ngực nở không làm phình tay)
     thân áo (torso) = mesh weight hip / spine / chest; tóc bên = mesh weight chuỗi 2 xương; chân (đùi / tất) đứng yên theo root.
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
OX, OY = 368, 1075

L = json.load(open(os.path.join(HERE, "layers.json"), encoding="utf-8"))
LAYER = {m["name"]: m for m in L["layers"]}
ORDER = [m["name"] for m in sorted(L["layers"], key=lambda m: m["z"])]


def S(px, py): return (px - OX, OY - py)


BONES, BW = [], {}


def bone(name, parent, cx, cy, ang=None, length=40, to=None, **kw):
    """vị trí ảnh (cx, cy); góc THẾ GIỚI `ang` (độ, 0 = +x, ngược chiều kim đồng hồ) hoặc `to` = điểm ảnh bone chỉ tới"""
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


def build():
    BONES.clear(); BW.clear()
    bone("root", None, 368, 1075, 90, 20)
    bone("hip", "root", 362, 905, to=(362, 860))
    bone("spine", "hip", 362, 860, to=(362, 700))
    bone("chest", "spine", 362, 700, to=(362, 400))
    bone("neck", "chest", 368, 372, to=(374, 316), inherit="noScale")
    bone("head", "neck", 374, 316, to=(398, 70))
    bone("eye_L", "head", 360, 186, 90, 14)                 # trục X xương = dọc mắt: scaleX = chớp (neo ở mí dưới, mí trên hạ xuống)
    bone("eye_R", "head", 437, 220, 90, 14)
    bone("hair_F", "head", 400, 70, to=(400, 170))
    bone("hair_B", "head", 390, 120, to=(390, 300))
    bone("hairL1", "head", 302, 125, to=(300, 215))
    bone("hairL2", "hairL1", 300, 215, to=(298, 305))
    bone("hairR1", "head", 482, 140, to=(480, 240))
    bone("hairR2", "hairR1", 480, 240, to=(462, 336))
    # tay: vai -> khuỷu (cánh tay trên đi xuống) -> cổ tay (cẳng tay gập lên) -> bàn tay (ngón chữ V)
    bone("upper_arm_L", "chest", 215, 395, to=(258, 640), inherit="noScale")
    bone("forearm_L", "upper_arm_L", 258, 640, to=(290, 425))
    bone("hand_L", "forearm_L", 290, 425, to=(262, 330))
    bone("upper_arm_R", "chest", 505, 395, to=(432, 640), inherit="noScale")
    bone("forearm_R", "upper_arm_R", 432, 640, to=(425, 425))
    bone("hand_R", "forearm_R", 425, 425, to=(455, 340))


# ---------------------------------------------------------------- lưới
def ss(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def mesh_points(mask, eps=1.3, max_edge=30, step=40, extra=()):
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
    inner = cv2.erode(mask.astype(np.uint8), np.ones((11, 11), np.uint8))
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
    h, w = img.shape[:2]; px0, py0 = LAYER[name]["x"], LAYER[name]["y"]
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
    edges = []
    for i in range(nh): edges += [i * 2, ((i + 1) % nh) * 2]
    return {"type": "mesh", "uvs": uvs, "triangles": [i for t in tris for i in t], "vertices": verts, "hull": nh,
            "edges": edges, "width": w, "height": h}, len(allp), len(tris)


def region(name, bone_name):
    """ảnh layer = region đứng thẳng ở setup: tâm ảnh -> toạ độ xương, xoay ngược góc thế giới của xương"""
    m = LAYER[name]
    lx, ly = to_local(bone_name, *S(m["x"] + m["w"] / 2.0, m["y"] + m["h"] / 2.0))
    return {"type": "region", "x": round(lx, 3), "y": round(ly, 3), "rotation": round(-BW[bone_name][2], 3),
            "width": m["w"], "height": m["h"]}


SLOT_BONE = {"hair_back": "hair_B", "neck": "neck", "choker": "neck", "thigh_L": "root", "thigh_R": "root",
             "sock_L": "root", "sock_R": "root", "torso": "chest",
             "upper_arm_L": "upper_arm_L", "upper_arm_R": "upper_arm_R", "sleeve_L": "upper_arm_L",
             "sleeve_R": "upper_arm_R", "forearm_L": "forearm_L", "forearm_R": "forearm_R", "hand_L": "hand_L",
             "hand_R": "hand_R", "face": "head", "eye_L": "eye_L", "eye_R": "eye_R", "hair_side_L": "hairL1",
             "hair_side_R": "hairR1", "hair_front": "hair_F"}


# ---------------------------------------------------------------- weight
def w_torso(cx, cy):
    """hông (gấu áo) -> hip, bụng -> spine, ngực / vai -> chest; chuyển mượt theo độ cao"""
    p = min(2.0, max(0.0, (870 - cy) / 250 * 2))
    return [("hip", max(1e-6, 1 - p)), ("spine", max(1e-6, 1 - abs(p - 1))), ("chest", max(1e-6, p - 1))]


def w_hair(b1, b2, y0, y1):
    def f(cx, cy):
        t = ss((cy - y0) / float(y1 - y0))
        return [(b1, 1 - t + 1e-6), (b2, t + 1e-6)]
    return f


def build_all():
    build()
    global BIDX
    BIDX = {b["name"]: i for i, b in enumerate(BONES)}
    spec = {
        "torso": (w_torso, dict(step=36)),
        "hair_side_L": (w_hair("hairL1", "hairL2", 150, 260), dict(step=26)),
        "hair_side_R": (w_hair("hairR1", "hairR2", 170, 290), dict(step=26)),
    }
    atts, info = {}, {}
    for nm in ORDER:
        if nm in spec:
            fn, kw = spec[nm]
            atts[nm], nv, nt = make_mesh(nm, fn, **kw); info[nm] = (nv, nt)
        else:
            atts[nm] = region(nm, SLOT_BONE[nm])
    slots = [{"name": n, "bone": SLOT_BONE[n], "attachment": n} for n in ORDER]
    sk = {"skeleton": {"spine": "4.2.43", "fps": FPS, "images": "./images/"}, "bones": BONES, "slots": slots,
          "skins": [{"name": "default", "attachments": {n: {n: atts[n]} for n in ORDER}}], "animations": {}}
    return sk, info


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "peacegirl.json")
    prev = json.load(open(out, encoding="utf8")) if os.path.exists(out) else None
    sk, info = build_all()
    if prev and prev.get("animations"):
        sk["animations"] = {k: v for k, v in prev["animations"].items() if k != "setup"}      # giữ anim đã có (bỏ anim setup trống)
    if not os.environ.get("ANIM_KIT_DRY"):
        try:
            import spine_live_cmd
            spine_live_cmd.claude_backup(out, "Claude dựng rig PeaceGirl")
        except Exception as e:
            print("(không ghi được backup Spine Live:", e, ")")
    json.dump(sk, open(out, "w", encoding="utf8"), indent=1)
    print("Đã ghi", out, "|", len(sk["bones"]), "xương,", len(sk["slots"]), "slot |",
          {k: "%d đỉnh / %d tam giác" % v for k, v in info.items()})
