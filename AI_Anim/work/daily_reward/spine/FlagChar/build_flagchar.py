"""Dựng rig Spine cho nhân vật cầm cờ (daily_reward_char_flag_anim.psd, 7 layer smart object, canvas 461x719).
Chạy: .venv/Scripts/python.exe -I work/daily_reward/spine/FlagChar/build_flagchar.py [out.json]
Toạ độ canvas PSD (y xuống) -> Spine (gốc root = giữa-đáy chân, y lên). Giữ anim đã có trong file khi dựng lại.

Rig:
  root > hip > spine > chest (thở: dời + scale nhẹ) > head (noScale) > prop (cánh quạt, lắc nhẹ)
  chest > grip (ctrl tay + cờ, noScale) > hand_R / hand_L (găng) và flag1 > flag2 (vải cờ, physics)
  chest > arm_R (tay gần, tay áo) / arm_L (tay xa, dải cam sau cờ): mỗi tay một IK 1 xương, target = cổ tay (wrist_*, con của grip); găng hand_* là con của cổ tay.
  => dời `grip` là hai tay + cờ đi cùng nhau, hai cẳng tay tự xoay theo (người dùng chỉ key grip / head / chest).
Thứ tự slot = thứ tự layer PSD (dưới -> trên): L_hand3, L_hand2, Group_3, flag, L_hand1, Head, R_hand.
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
OX, OY = 200, 690          # canvas (px, py) -> spine (px - OX, OY - py)

# bbox layer trong canvas PSD (x, y) = góc trên trái; w, h lấy từ ảnh
PARTS = {"L_hand3": (187, 399), "L_hand2": (324, 376), "Group_3": (87, 389), "flag": (232, 411),
         "L_hand1": (376, 379), "Head": (0, 20), "R_hand": (118, 399)}
SLOT_BONE = {"L_hand3": "arm_L", "L_hand2": "hand_L", "Group_3": "hip", "flag": "pole", "L_hand1": "hand_L",
             "Head": "head", "R_hand": "hand_R"}
ORDER = ["L_hand3", "L_hand2", "Group_3", "flag", "L_hand1", "Head", "R_hand"]
EYES = json.load(open(os.path.join(HERE, "eyes.json")))      # prep_eyes.py: mắt tách khỏi Head để chớp
SLOT_ORDER = ORDER[:6] + ["eye_L", "eye_R"] + ORDER[6:]
SLOT_BONE.update({"eye_L": "eye_L", "eye_R": "eye_R"})


def S(px, py): return (px - OX, OY - py)


# ---------------------------------------------------------------- xương
BONES, BW = [], {}


def bone(name, parent, cx, cy, ang=None, length=40, to=None, **kw):
    """vị trí canvas (cx, cy); góc THẾ GIỚI `ang` (độ, 0 = +x, ngược chiều kim đồng hồ) hoặc `to` = điểm canvas bone chỉ tới"""
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


# điểm neo (canvas), đo từ ảnh PSD
HAND_R = (215, 447)        # tâm găng gần (viewer trái)
HAND_L = (379, 425)        # tâm nắm đấm xa (viewer phải)
FLAG_TOP = (322, 424)      # mép trên cờ giữa hai tay
MOUTH = (278, 327)         # tâm mỏ (ống cam, đo từ ảnh Head: head-local (278, 307) + offset y 20); bán kính ống ~62 px
MOUTH_R = (60.0, 90.0)     # weight mỏ = 1 trong bán kính 60, về 0 ở 90 (da đầu quanh ống bị kéo theo mềm)
HUB = (137.7, 43.5)        # tâm cánh quạt (quả cầu trắng, đo từ ảnh Head: head-local (137.7, 23.5) + offset y 20)


def build():
    BONES.clear(); BW.clear()
    bone("root", None, 200, 690, 90, 20)
    bone("hip", "root", 205, 575, 90, 35)
    # chân (mỗi chân: đùi/cẳng từ hông tới cổ chân + bàn chân tới mũi giày); chân trước = viewer trái, chân sau = viewer phải
    bone("leg_F", "hip", 143, 560, to=(150, 628))
    bone("foot_F", "leg_F", 150, 628, to=(100, 656))
    bone("leg_B", "hip", 240, 560, to=(242, 616))
    bone("foot_B", "leg_B", 242, 616, to=(306, 650))
    bone("spine", "hip", 205, 540, 90, 80)
    bone("chest", "spine", 205, 460, 90, 60)
    bone("head", "chest", 185, 405, to=(170, 250), inherit="noScale")
    bone("prop", "head", HUB[0], HUB[1], 0, 120)
    bone("mouth", "head", MOUTH[0], MOUTH[1], -8, 45)       # mỏ: scale đều = phồng / xẹp (thở)
    for nm in ("eye_L", "eye_R"):                       # trục X xương = dọc mắt (hướng lên): scaleX = chớp
        e = EYES[nm]; a = math.radians(e["angle"]); h = e["core_h"]
        if nm == "eye_L":                               # neo ở 1/4 dưới: mí trên hạ xuống
            px, py = e["center"][0] - 0.25 * h * math.cos(a), e["center"][1] + 0.25 * h * math.sin(a)
        else:                                           # mắt phải bị ống che: neo ở mép ống (đáy phần thấy)
            cb = e["core_bbox"]; px, py = (cb[0] + cb[2]) / 2.0, float(cb[3])
        e["pivot"] = (px, py)
        bone(nm, "head", px, py, e["angle"], h * 0.6)
    bone("arm_R", "chest", 135, 430, to=HAND_R, inherit="noScale")
    bone("arm_L", "chest", 190, 424, to=HAND_L, inherit="noScale")
    bone("grip", "chest", 300, 436, 0, 40, inherit="noScale")
    # cổ tay (wrist_*) là đích IK của cẳng tay: đi theo grip (cánh tay dẫn); găng (hand_*) là con của cổ tay, trễ thêm sau cánh tay
    bone("wrist_R", "grip", HAND_R[0], HAND_R[1], 0, 20)
    bone("wrist_L", "grip", HAND_L[0], HAND_L[1], 0, 20)
    bone("hand_R", "wrist_R", HAND_R[0], HAND_R[1], 0, 50)
    bone("hand_L", "wrist_L", HAND_L[0], HAND_L[1], 0, 50)
    # pole = cán cờ (mép cuộn trên cùng): CÙNG gốc với grip, bám theo bàn tay (trung bình trễ của hai găng), không vung; vải cờ là con của pole
    bone("pole", "grip", 300, 436, 0, 40)
    bone("flag1", "pole", FLAG_TOP[0], FLAG_TOP[1], -90, 130)
    bone("flag2", "flag1", FLAG_TOP[0], FLAG_TOP[1] + 130, -90, 130)


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
    h, w = img.shape[:2]; px0, py0 = PARTS[name]
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


# ---------------------------------------------------------------- weight từng layer (cx, cy = canvas)
def w_body(cx, cy):
    """thân: hip -> spine -> chest dần lên (thở co giãn phần ngực); từ y 520 xuống: chia dần cho hai chân (trái / phải theo khe
    giữa hai chân), giày (y > ~605) = bàn chân"""
    p = min(2.0, max(0.0, (565 - cy) / 150 * 2))
    up = [("hip", max(1e-6, 1 - p)), ("spine", max(1e-6, 1 - abs(p - 1))), ("chest", max(1e-6, p - 1))]
    lw = ss((cy - 520) / 65.0)
    if lw <= 0: return up
    t = ss((cy - 575) / 30.0)                                       # đùi: chia trái/phải mềm; dưới đó: theo khe giữa hai giày
    sF = (1 - t) * (1 - ss((cx - 160) / 60.0)) + t * (1 - ss((cx - 195) / 16.0))
    ff = ss((cy - 604) / 22.0) * (1 if cx < 205 else 0.0)           # giày trước (chỉ phía trái khe)
    fb = ss((cy - 598) / 22.0) * (1 if cx > 185 else 0.0)           # giày sau
    leg = [("leg_F", sF * (1 - ff)), ("foot_F", sF * ff), ("leg_B", (1 - sF) * (1 - fb)), ("foot_B", (1 - sF) * fb)]
    return [(b, w * (1 - lw)) for b, w in up] + [(b, w * lw + 1e-6) for b, w in leg]


def w_head(cx, cy):
    """đầu = head; cánh quạt (+ cọng) = prop: trên đường biên cong quanh mũ"""
    x, y = cx - PARTS["Head"][0], cy - PARTS["Head"][1]
    yb = min(66.0, 48 + 0.01 * (x - 140) ** 2)
    wp = 1 - ss((y - (yb - 8)) / 10.0)
    if (x < 88 or x > 245) and y < 92: wp = 1.0
    d = math.hypot(cx - MOUTH[0], cy - MOUTH[1])
    wm = 1 - ss((d - MOUTH_R[0]) / (MOUTH_R[1] - MOUTH_R[0]))
    return [("prop", wp + 1e-6), ("mouth", (1 - wp) * wm + 1e-6), ("head", (1 - wp) * (1 - wm) + 1e-6)]


def w_flag(cx, cy):
    """cán cờ (mép cuộn, y < ~446) cố định 100% xương pole (theo tay); vải cờ: flag1 rồi flag2 (đầu nhọn) vung overlap"""
    u = (cy - FLAG_TOP[1]) / 130.0                           # 0 = mép trên, 1 = khớp giữa, 2 = đầu nhọn
    g = 1 - ss((cy - 446) / 56.0)
    f1 = max(0.0, 1 - abs(u - 0.5)); f2 = max(0.0, 1 - abs(u - 1.5))
    return [("pole", g + 1e-6), ("flag1", (1 - g) * f1 + 1e-6), ("flag2", (1 - g) * f2 + 1e-6)]


def w_hand_R(cx, cy):
    t = ss((cx - 150) / 45.0)                                # tay áo (cẳng tay) -> găng
    return [("arm_R", 1 - t + 1e-6), ("hand_R", t + 1e-6)]


def build_all():
    build()
    global BIDX
    BIDX = {b["name"]: i for i, b in enumerate(BONES)}
    # điểm thêm dọc biên cánh quạt / mũ để weight chuyển gọn
    head_extra = [(x, min(66.0, 48 + 0.01 * (x - 140) ** 2) - 4) for x in range(90, 246, 14)]
    head_extra += [(x, min(66.0, 48 + 0.01 * (x - 140) ** 2) + 6) for x in range(90, 246, 14)]
    for r in (28, 48, 62, 76, 90):                       # vòng điểm quanh mỏ cho weight / scale mượt
        n = max(8, int(2 * math.pi * r / 20))
        head_extra += [(MOUTH[0] + r * math.cos(2 * math.pi * k / n), MOUTH[1] - 20 + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    body_extra = [(x - 87, y - 389) for y in (572, 598, 614) for x in range(95, 312, 20)]     # hàng điểm dọc hông / mép giày
    spec = {
        "L_hand3": (lambda cx, cy: [("arm_L", 1.0)], dict(step=60)),
        "L_hand2": (lambda cx, cy: [("hand_L", 1.0)], dict(step=40)),
        "Group_3": (w_body, dict(step=36, extra=body_extra)),
        "flag": (w_flag, dict(step=34)),
        "L_hand1": (lambda cx, cy: [("hand_L", 1.0)], dict(step=40)),
        "Head": (w_head, dict(step=40, extra=head_extra)),
        "R_hand": (w_hand_R, dict(step=34)),
    }
    atts, info = {}, {}
    for nm in ORDER:
        fn, kw = spec[nm]
        atts[nm], nv, nt = make_mesh(nm, fn, **kw); info[nm] = (nv, nt)
    for nm in ("eye_L", "eye_R"):                       # ảnh mắt = region, tâm ảnh -> toạ độ xương mắt, đứng thẳng ở setup
        bx, by, bw_, bh_ = EYES[nm]["bbox"]
        lx, ly = to_local(nm, *S(bx + bw_ / 2.0, by + bh_ / 2.0))
        atts[nm] = {"type": "region", "x": round(lx, 3), "y": round(ly, 3), "rotation": round(-BW[nm][2], 3),
                    "width": bw_, "height": bh_}
    slots = [{"name": n, "bone": SLOT_BONE[n], "attachment": n} for n in SLOT_ORDER]
    sk = {"skeleton": {"spine": "4.2.43", "fps": FPS, "images": "./images/"}, "bones": BONES, "slots": slots,
          "ik": [{"name": "ik_arm_R", "order": 0, "bones": ["arm_R"], "target": "wrist_R"},
                 {"name": "ik_arm_L", "order": 1, "bones": ["arm_L"], "target": "wrist_L"}],
          "skins": [{"name": "default", "attachments": {n: {n: atts[n]} for n in SLOT_ORDER}}], "animations": {}}
    return sk, info


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "flagchar.json")
    prev = json.load(open(out, encoding="utf8")) if os.path.exists(out) else None
    sk, info = build_all()
    if prev and prev.get("animations"): sk["animations"] = prev["animations"]      # giữ anim đã có
    if not os.environ.get("ANIM_KIT_DRY"):
        try:
            import spine_live_cmd
            spine_live_cmd.claude_backup(out, "Claude dựng rig FlagChar")
        except Exception as e:
            print("(không ghi được backup Spine Live:", e, ")")
    json.dump(sk, open(out, "w", encoding="utf8"), indent=1)
    print("Đã ghi", out, "|", len(sk["bones"]), "xương,", len(sk["slots"]), "slot |",
          {k: "%d đỉnh / %d tam giác" % v for k, v in info.items()})
