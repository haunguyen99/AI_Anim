"""Tách layer PeaceGirl từ ảnh phẳng src/source.jpg (nền xám 240).
Chạy: .venv/Scripts/python.exe -I work/peace_girl/spine/PeaceGirl/split_layers.py work/peace_girl/spine/PeaceGirl
Ra: images/<layer>.png (cắt theo bbox), layers.json (x, y, w, h = góc trên-trái trong ảnh gốc, y xuống; z tăng dần = ra trước),
    preview/labels.png (bản đồ vùng), preview/composite.png, preview/sheet.png.
L / R theo MÀN HÌNH (L = bên trái người xem).
"""
import cv2, json, os, sys
import numpy as np

D = sys.argv[1]
im = cv2.imread(f"{D}/src/source.jpg")
H_, W_ = im.shape[:2]
fg = cv2.imread(f"{D}/src/fg_mask.png", 0) > 0

hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
Hh, Ss, Vv = [hsv[..., i].astype(int) for i in range(3)]
skin = ((Hh <= 25) | (Hh >= 170)) & (Ss >= 25) & (Vv >= 125)
hair = (Hh >= 118) & (Hh <= 152) & (Ss >= 70) & (Vv >= 55)
hair_core = hair
hair = hair_core | ((Vv < 80) & (cv2.dilate(hair_core.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=4) > 0))
white = (Ss < 40) & (Vv > 170)
FLT = {
    "any": np.ones((H_, W_), bool),
    "skin": skin,
    "nonskin": ~skin,
    "hair": hair,
    "eye": (~skin) | white,
    "dark": Vv < 90,
}


def poly(pts):
    m = np.zeros((H_, W_), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 1)
    return m > 0


# ---- polygon (toạ độ ảnh gốc, y xuống) ----
P_HEAD_BOX = [(270, 30), (530, 30), (530, 345), (270, 345)]
HAIR_EXT = [(285, 150), (300, 95), (345, 55), (400, 42), (460, 50), (500, 90), (512, 150), (500, 260),
            (480, 335), (430, 340), (425, 300), (400, 285), (345, 290), (320, 300), (290, 300), (280, 230)]
P_FACE = [(298, 150), (330, 105), (400, 85), (470, 90), (505, 140), (512, 235), (468, 250), (462, 242),
          (445, 262), (425, 278), (405, 292), (383, 299), (360, 285), (342, 262), (318, 255), (304, 230), (298, 190)]
P_NECK = [(318, 262), (432, 262), (445, 380), (305, 380)]
P_NECK_EXT = [(322, 255), (430, 255), (440, 385), (312, 385)]
P_CHOKER = [(316, 290), (345, 298), (385, 305), (410, 315), (412, 326), (395, 322), (350, 315), (325, 312), (316, 302)]
P_EYE_L = [(338, 160), (362, 160), (383, 171), (383, 192), (360, 197), (340, 188)]
P_EYE_R = [(412, 205), (428, 195), (447, 197), (463, 206), (461, 224), (440, 229), (418, 224)]

P_THIGH_L = [(185, 880), (358, 880), (358, 1050), (185, 1050)]
P_THIGH_R = [(362, 880), (530, 880), (530, 1050), (362, 1050)]
P_SOCK_L = [(185, 1015), (358, 1015), (358, 1075), (185, 1075)]
P_SOCK_R = [(362, 1015), (530, 1015), (530, 1075), (362, 1075)]
P_TORSO = [(150, 325), (548, 325), (548, 950), (180, 950)]

P_SLEEVE_L = [(146, 326), (258, 326), (258, 516), (246, 524), (222, 536), (200, 553), (146, 553)]
P_SLEEVE_R = [(436, 324), (548, 324), (548, 568), (500, 558), (470, 542), (436, 522)]
P_UARM_L = [(190, 498), (262, 498), (256, 516), (246, 535), (233, 560), (226, 582), (228, 598), (241, 622),
            (257, 648), (257, 660), (190, 660)]
P_FARM_L = [(250, 424), (258, 500), (256, 516), (246, 535), (233, 560), (226, 582), (228, 598), (241, 622),
            (257, 648), (275, 660), (300, 640), (318, 500), (326, 424)]
P_UARM_R = [(441, 498), (500, 498), (500, 640), (448, 652), (445, 648), (474, 600), (473, 590), (466, 570),
            (455, 545), (447, 522)]
P_FARM_R = [(392, 424), (445, 424), (441, 498), (447, 522), (455, 545), (466, 570), (473, 590), (474, 600),
            (445, 648), (440, 660), (392, 660)]
P_HAND_L = [(190, 282), (205, 280), (240, 318), (245, 268), (262, 266), (270, 300), (280, 326), (300, 340),
            (318, 352), (324, 380), (324, 424), (250, 424), (244, 395), (240, 375), (246, 350), (236, 338),
            (215, 325), (195, 300)]
P_HAND_R = [(392, 380), (400, 368), (420, 362), (440, 352), (460, 330), (480, 300), (494, 290), (506, 296),
            (496, 318), (515, 318), (535, 318), (540, 326), (528, 334), (500, 345), (478, 362), (482, 384),
            (476, 412), (462, 424), (405, 424), (392, 404)]

# vùng chữ nhật cho tóc (x0, y0, x1, y1) -> polygon
def box(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


SIDE_L = [(262, 128), (300, 116), (338, 156), (338, 262), (262, 262)]
SIDE_R = [(428, 150), (470, 128), (530, 128), (530, 345), (428, 345)]
BACK_T = box(270, 262, 338, 345)

# (tên, polygon nhìn thấy, bộ lọc màu, polygon mở rộng khi bị che)  -- thứ tự = z từ sau ra trước
LAYERS = [
    ("hair_back", BACK_T, "hair", HAIR_EXT),
    ("neck", P_NECK, "skin", P_NECK_EXT),
    ("thigh_L", P_THIGH_L, "skin", box(188, 880, 358, 1048)),
    ("thigh_R", P_THIGH_R, "skin", box(364, 880, 528, 1048)),
    ("sock_L", P_SOCK_L, "nonskin", box(186, 1015, 358, 1075)),
    ("sock_R", P_SOCK_R, "nonskin", box(364, 1015, 530, 1075)),
    ("torso", P_TORSO, "nonskin", P_TORSO),
    ("upper_arm_L", P_UARM_L, "skin", box(190, 480, 262, 655)),
    ("upper_arm_R", P_UARM_R, "skin", box(441, 480, 500, 655)),
    ("sleeve_L", P_SLEEVE_L, "nonskin", None),
    ("sleeve_R", P_SLEEVE_R, "nonskin", None),
    ("forearm_L", P_FARM_L, "skin", box(240, 395, 330, 660)),
    ("forearm_R", P_FARM_R, "skin", box(390, 395, 450, 660)),
    ("hand_L", P_HAND_L, "skin", None),
    ("hand_R", P_HAND_R, "skin", None),
    ("choker", P_CHOKER, "dark", None),
    ("face", P_FACE, "skin", P_FACE),
    ("eye_L", P_EYE_L, "eye", None),
    ("eye_R", P_EYE_R, "eye", None),
    ("hair_side_L", SIDE_L, "hair", box(270, 110, 352, 276)),
    ("hair_side_R", SIDE_R, "hair", box(414, 120, 530, 345)),
    ("hair_front", P_HEAD_BOX, "hair", None),
]
# tóc: hair_front lấy mọi tóc còn lại trong hộp đầu (vẽ trước hair_side_* nên bị chúng đè)
ORDER_PAINT = ["hair_back", "neck", "thigh_L", "thigh_R", "sock_L", "sock_R", "torso", "upper_arm_L", "upper_arm_R",
               "sleeve_L", "sleeve_R", "forearm_L", "forearm_R", "hand_L", "hand_R", "choker", "face", "eye_L",
               "eye_R", "hair_side_L", "hair_side_R", "hair_front"]
spec = {n: (p, f, e) for n, p, f, e in LAYERS}
names = ORDER_PAINT
Z = {n: i + 1 for i, n in enumerate(names)}

# hair_back nhìn thấy: tóc ở phần thấp (đuôi tóc sau cổ) + mọi tóc ngoài hộp đầu thấp
lab = np.zeros((H_, W_), np.int16)
for n in names:
    p, f, _ = spec[n]
    m = poly(p) & FLT[f] & fg
    if f == "skin":
        k = 9 if n.startswith("hand") else 5
        mc = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
        if n.startswith("hand"):
            cs, _ = cv2.findContours(mc, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            mc = np.zeros_like(mc)
            cv2.drawContours(mc, cs, -1, 1, cv2.FILLED)
        m = (mc > 0) & poly(p) & fg
    if n == "hair_front":
        m &= ~(poly(SIDE_L) | poly(SIDE_R) | poly(BACK_T))
    if n == "eye_L" or n == "eye_R":
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0
        m &= poly(p) & fg
    lab[m] = Z[n]
# viền tối quanh bàn tay / cẳng tay thuộc về tay (ăn 3 px vào điểm tối của layer đứng sau)
for n_ in ("forearm_L", "forearm_R", "hand_L", "hand_R"):
    g_ = cv2.dilate((lab == Z[n_]).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    lab[g_ & fg & (Vv < 110) & (lab < Z[n_]) & (lab > 0)] = Z[n_]
n_unl = int(((lab == 0) & fg).sum())
print("fg chưa gán trước khi nội suy:", n_unl)

# điểm fg chưa gán -> layer gần nhất
src = np.ones((H_, W_), np.uint8)
src[lab > 0] = 0
dist, labels = cv2.distanceTransformWithLabels(src, cv2.DIST_L2, 3, labelType=cv2.DIST_LABEL_PIXEL)
idx = np.flatnonzero((src == 0).ravel())
labmap = lab.ravel()[idx]
near = labmap[np.clip(labels - 1, 0, len(labmap) - 1)]
lab_full = lab.copy()
unl = (lab == 0) & fg
lab_full[unl] = near[unl]

# nét tối còn sót trên mặt sát tóc -> tóc gần nhất
hair_ids = [Z["hair_side_L"], Z["hair_side_R"], Z["hair_front"]]
is_hair = np.isin(lab_full, hair_ids)
sd = np.ones((H_, W_), np.uint8)
sd[is_hair] = 0
_, hl = cv2.distanceTransformWithLabels(sd, cv2.DIST_L2, 3, labelType=cv2.DIST_LABEL_PIXEL)
hidx = np.flatnonzero((sd == 0).ravel())
hnear = lab_full.ravel()[hidx][np.clip(hl - 1, 0, len(hidx) - 1)]
near_h = cv2.dilate(is_hair.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0
fix = (lab_full == Z["face"]) & (Vv < 115) & near_h
lab_full[fix] = hnear[fix]
print("nét tối trên mặt chuyển sang tóc:", int(fix.sum()))

# ---- alpha mềm: màu thuần lấy từ điểm lõi gần nhất, alpha = tỉ lệ pha trộn với nền ----
K3 = np.ones((3, 3), np.uint8)
fgu = fg.astype(np.uint8)
core = cv2.erode(fgu, K3, iterations=1) > 0
fg2 = cv2.dilate(fgu, K3, iterations=1) > 0
Zb = fg2 & ~core
sd0 = np.ones((H_, W_), np.uint8)
sd0[core] = 0
_, lb0 = cv2.distanceTransformWithLabels(sd0, cv2.DIST_L2, 3, labelType=cv2.DIST_LABEL_PIXEL)
idx0 = np.flatnonzero((sd0 == 0).ravel())
pure = im.reshape(-1, 3)[idx0[np.clip(lb0 - 1, 0, len(idx0) - 1)]].astype(np.float32).reshape(H_, W_, 3)
a_soft = cv2.GaussianBlur(core.astype(np.float32), (0, 0), 0.8)
a_soft[a_soft < 0.15] = 0
a_soft[core] = 1.0
a_soft[~fg2] = 0
clean = im.astype(np.float32).copy()
clean[Zb] = pure[Zb]
need = fg2 & (lab_full == 0)
lab_full[need] = near[need]


def extend_hidden(color, vis, hidden, extra_src=None, only=None):
    """tô vùng `hidden` bằng màu điểm gần nhất của layer (bỏ 2 px sát biên vì dính viền layer kề), rồi làm mượt."""
    out = color.astype(np.float32).copy()
    if not hidden.any():
        return out
    srcm = vis if extra_src is None else (vis | (extra_src & fg))
    if only is not None and (srcm & only).sum() > 40:
        srcm = srcm & only
    er = cv2.erode(srcm.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=2) > 0
    if er.sum() < 40:
        er = srcm
    sd = np.ones(vis.shape, np.uint8)
    sd[er] = 0
    dist, labels = cv2.distanceTransformWithLabels(sd, cv2.DIST_L2, 3, labelType=cv2.DIST_LABEL_PIXEL)
    idx = np.flatnonzero((sd == 0).ravel())
    pos = idx[np.clip(labels - 1, 0, len(idx) - 1)]
    near_col = color.reshape(-1, 3)[pos].astype(np.float32)
    base = np.zeros_like(out)
    base[hidden] = near_col[hidden]
    wm = (er | hidden).astype(np.float32)
    outs = []
    for sg in (2.5, 9.0):
        num = cv2.GaussianBlur(np.where((er | hidden)[..., None], np.where(hidden[..., None], base, color.astype(np.float32)), 0), (0, 0), sg)
        den_ = cv2.GaussianBlur(wm, (0, 0), sg)
        outs.append(num / np.maximum(den_, 1e-4)[..., None])
    t = np.clip(dist / 30.0, 0, 1)[..., None]
    sm = outs[0] * (1 - t) + outs[1] * t
    out[hidden] = sm[hidden]
    return out


os.makedirs(f"{D}/images", exist_ok=True)
for f in os.listdir(f"{D}/images"):
    if f.endswith(".png"):
        os.remove(f"{D}/images/{f}")
meta = []
report = []
canvas = np.full((H_, W_, 3), 240, np.float32)
for n in names:
    i = Z[n]
    vis = lab_full == i
    if not vis.any():
        report.append((n, 0, 0))
        continue
    ext = spec[n][2]
    hidden = np.zeros_like(vis)
    if ext is not None:
        hidden = poly(ext) & (lab_full > i) & ~vis & (a_soft >= 0.999)
    col = extend_hidden(clean, vis, hidden, extra_src=(hair_core if n == "hair_back" else None),
                      only=(skin if spec[n][1] == "skin" else None))
    alpha = np.where(vis, a_soft, 0.0)
    alpha[hidden] = 1.0
    ys, xs = np.nonzero(alpha > 0.01)
    x0, x1, y0, y1 = max(xs.min() - 1, 0), min(xs.max() + 2, W_), max(ys.min() - 1, 0), min(ys.max() + 2, H_)
    rgba = np.dstack([np.clip(col, 0, 255), alpha * 255]).astype(np.uint8)[y0:y1, x0:x1]
    rgba[..., :3][rgba[..., 3] == 0] = 0
    cv2.imwrite(f"{D}/images/{n}.png", rgba[..., [0, 1, 2, 3]])
    meta.append({"name": n, "file": f"images/{n}.png", "x": int(x0), "y": int(y0), "w": int(x1 - x0),
                 "h": int(y1 - y0), "z": i})
    report.append((n, int(vis.sum()), int(hidden.sum())))
    a = alpha[..., None]
    canvas = canvas * (1 - a) + col * a

json.dump({"canvas": [W_, H_], "note": "x,y = góc trên-trái trong ảnh gốc (y xuống); z tăng dần = ra trước; L/R theo màn hình",
           "layers": meta}, open(f"{D}/layers.json", "w"), ensure_ascii=False, indent=1)
for n, v, hd in report:
    print(f"{n:12s} nhìn thấy {v:7d} px   tô phần bị che {hd:6d} px")

comp = np.clip(canvas, 0, 255).astype(np.uint8)
os.makedirs(f"{D}/preview", exist_ok=True)
cv2.imwrite(f"{D}/preview/composite.png", comp)
diff = np.abs(comp.astype(int) - im.astype(int)).max(axis=2)
print("ghép lại vs gốc (trong lõi fg): lệch TB %.2f, >40: %d px" % (diff[core].mean(), (diff[core] > 40).sum()))

# bản đồ vùng để soi
rng = np.random.RandomState(3)
pal = rng.randint(40, 255, (len(names) + 2, 3))
vis_map = np.full((H_, W_, 3), 255, np.uint8)
for n in names:
    vis_map[lab_full == Z[n]] = pal[Z[n]]
for n in names:
    ys, xs = np.nonzero(lab_full == Z[n])
    if len(xs):
        cv2.putText(vis_map, n, (int(xs.mean()) - 30, int(ys.mean())), cv2.FONT_HERSHEY_SIMPLEX, .38, (0, 0, 0), 1)
cv2.imwrite(f"{D}/preview/labels.png", vis_map)

# contact sheet: mỗi layer trên nền ca-rô
tiles = []
TH = 260
for m_ in meta:
    img = cv2.imread(f"{D}/{m_['file']}", cv2.IMREAD_UNCHANGED)
    sc = min(TH / img.shape[0], TH / img.shape[1], 2.0)
    img = cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_CUBIC)
    t = np.zeros((TH + 18, TH, 3), np.uint8)
    yy, xx = np.mgrid[0:TH + 18, 0:TH]
    t[:] = np.where(((yy // 12 + xx // 12) % 2 == 0)[..., None], 200, 150)
    hh, ww = img.shape[:2]
    a = img[..., 3:4].astype(np.float32) / 255
    roi = t[18:18 + hh, 0:ww].astype(np.float32)
    t[18:18 + hh, 0:ww] = (roi * (1 - a) + img[..., :3] * a).astype(np.uint8)
    cv2.putText(t, f"{m_['z']} {m_['name']} {m_['w']}x{m_['h']}", (2, 12), cv2.FONT_HERSHEY_SIMPLEX, .4, (0, 0, 0), 1)
    tiles.append(t)
cols = 6
while len(tiles) % cols:
    tiles.append(np.full_like(tiles[0], 255))
rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
cv2.imwrite(f"{D}/preview/sheet.png", np.vstack(rows))
