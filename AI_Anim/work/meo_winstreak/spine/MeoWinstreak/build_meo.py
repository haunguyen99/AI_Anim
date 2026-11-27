"""Dựng rig Spine cho mèo thạch bị máy gắp (meo_winstreak_anim.psd, canvas 1695x4899). Ảnh: images/ (extract_layers.py).
Chạy: .venv/Scripts/python.exe -I work/meo_winstreak/spine/MeoWinstreak/build_meo.py [out.json]
Toạ độ canvas PSD (y xuống) -> Spine (gốc root = giữa đáy mèo, y lên). Giữ anim đã có trong file khi dựng lại.
CẢNH BÁO: từ lần dựng thứ hai KHÔNG chạy đè khi người dùng đã sửa lưới / weight trên Spine Live (đọc `spine_live_cmd.py history`
trước; script từ chối nếu file đã có và không đặt MEO_REBUILD=1).

Rig:
  root > cat (ctrl mèo) > hip > spine > head > ear_L1 > ear_L2 / ear_R1 > ear_R2 / eye_L / eye_R / mouth
  hip > foot_L / paw_F (bàn chân trước, weight cục bộ trong thân) / bump_R (cục nhô bên phải)
  root > hang (cán, 1 xương, xoay = đu đưa) > claw (thân + vòng đệm) > knob_L / knob_R (chốt, đứng yên) / arm_L / arm_R (càng, gốc ở tâm chốt)
Thứ tự slot = thứ tự layer PSD (dưới -> trên). Mặt: mắt / miệng có 2 attachment (keo = mặc định đúng ảnh PSD, nam = mắt oval mở).
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
OX, OY = 819, 4612          # canvas (px, py) -> spine (px - OX, OY - py)
LAY = json.load(open(os.path.join(HERE, "layers.json"), encoding="utf8"))["layers"]


def S(px, py): return (px - OX, OY - py)


# ---------------------------------------------------------------- xương
BONES, BW = [], {}


def bone(name, parent, cx, cy, ang=None, length=40, to=None, **kw):
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
KNOB_L = (203.5, 4025.4)     # tâm đĩa tím chốt trái (centroid vùng màu đĩa)
KNOB_R = (1182.5, 4097.4)    # chốt phải
ARM_L_TIP = (384, 4438)      # mũi càng trái (xa chốt nhất)
ARM_R_TIP = (1114, 4471)
POLE_X = 819
JOINTS = [("hang", 280), ("claw", 3450)]     # y PSD gốc xương cán (1 xương) và xương thân máy gắp
EYE_C = {"eye_L": (454.0, 4206.0), "eye_R": (613.5, 4222.5), "mouth": (533.5, 4247.5)}     # tâm ảnh bản `nam`


def build():
    BONES.clear(); BW.clear()
    bone("root", None, 819, 4612, 90, 20)
    # mèo (ctrl tách khỏi máy gắp: thả / nhấc riêng)
    bone("cat", "root", 819, 4600, 90, 60)
    bone("hip", "cat", 819, 4540, 90, 150)
    bone("spine", "hip", 819, 4390, 90, 150)
    bone("head", "spine", 819, 4240, to=(819, 3800))
    bone("ear_L1", "head", 470, 3920, to=(455, 3835))
    bone("ear_L2", "ear_L1", 455, 3835, to=(448, 3768))
    bone("ear_R1", "head", 805, 3935, to=(808, 3850))
    bone("ear_R2", "ear_R1", 808, 3850, to=(812, 3772))
    for nm in ("eye_L", "eye_R", "mouth"):                       # mặt gần chính diện: local rotation 0 theo head
        bone(nm, "head", *EYE_C[nm], 90, 60)
    bone("foot_L", "hip", 340, 4400, to=(295, 4500))
    bone("paw_F", "hip", 746, 4420, to=(746, 4560))
    bone("bump_R", "hip", 1290, 4350, to=(1370, 4350))
    # máy gắp: treo từ đỉnh cần
    prev = "root"
    ys = [j[1] for j in JOINTS]
    for i, (nm, y) in enumerate(JOINTS[:-1]):
        bone(nm, prev, POLE_X, y, -90, ys[i + 1] - y); prev = nm
    bone("claw", prev, POLE_X, 3450, -90, 350)
    bone("knob_L", "claw", *KNOB_L, 0, 60)
    bone("knob_R", "claw", *KNOB_R, 0, 60)
    bone("arm_L", "claw", *KNOB_L, to=ARM_L_TIP)
    bone("arm_R", "claw", *KNOB_R, to=ARM_R_TIP)


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
    hull, inner, m = mesh_points(mask, **kw)
    allp = np.vstack([hull, inner]) if len(inner) else hull
    tris = tri_filter(allp, m)
    used = sorted(set(i for t in tris for i in t))
    remap = {o: n for n, o in enumerate([i for i in range(len(hull)) if i in used] + [i for i in used if i >= len(hull)])}
    order = sorted(remap, key=lambda o: remap[o]); allp = allp[order]
    nh = sum(1 for o in order if o < len(hull)); tris = [[remap[i] for i in t] for t in tris]
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
def tent(y, joints):
    """joints = [(bone, y)] y tăng dần; trả [(bone, w)] nội suy tuyến tính, ngoài đầu / cuối = 1 bone đó"""
    if y <= joints[0][1]: return [(joints[0][0], 1.0)]
    if y >= joints[-1][1]: return [(joints[-1][0], 1.0)]
    for (a, ya), (b, yb) in zip(joints, joints[1:]):
        if ya <= y <= yb:
            t = (y - ya) / (yb - ya); return [(a, 1 - t), (b, t)]


def w_claw(cx, cy):
    """cán = 1 xương `hang` cứng (100%) tới sát vòng đệm (y ~3270); vòng đệm + thân trên = `claw`; chuyển trong 70 px ngay dưới mép vòng đệm"""
    c = ss((cy - 3270) / 70.0)
    return [("hang", 1 - c + 1e-6), ("claw", c + 1e-6)]


def vband(cy):
    """thân mèo: head (trên) -> spine -> hip (dưới), nội suy tuyến tính giữa gốc từng đốt"""
    return tent(cy, [("head", 4240), ("spine", 4390), ("hip", 4540)])


def mix(local, base):
    """local = [(bone, w)] tổng <= 1, phần còn lại chia theo base"""
    t = sum(w for _, w in local)
    return [(b, w) for b, w in local if w > 0] + [(b, w * max(0.0, 1 - t)) for b, w in base]


def w_body(cx, cy):
    loc = []
    # tai trái nằm trong thân: vùng x 340-640, từ y 3945 lên đỉnh
    ew = ss((3945 - cy) / 60.0) * ss((cx - 340) / 40.0) * (1 - ss((cx - 620) / 40.0))
    f2 = ss((3885 - cy) / 70.0)
    loc += [("ear_L1", ew * (1 - f2)), ("ear_L2", ew * f2)]
    d = math.hypot(cx - 746, cy - 4500)                          # bàn chân trước (bump đáy)
    loc.append(("paw_F", 1 - ss((d - 55) / 65.0)))
    d = math.hypot(cx - 1336, cy - 4345)                         # cục nhô bên phải
    loc.append(("bump_R", 1 - ss((d - 45) / 65.0)))
    t = sum(w for _, w in loc)
    if t > 1: loc = [(b, w / t) for b, w in loc]
    return mix(loc, vband(cy))


def w_belly(cx, cy): return vband(cy)


def w_foot(cx, cy):
    """chân trái nằm SAU thân: phần trên / đuôi mảnh theo đúng weight thân (head -> spine -> hip) để mép chân luôn nằm dưới mép thân,
    không hở khe khi thân nghiêng (lỗi 2026-11-27: đuôi chỉ theo hip, mép thân theo spine / head); phần giọt nước (y > 4410) theo foot_L"""
    f = 0.5 * ss((cy - 4330) / 80.0)       # foot_L tối đa 50%: phần còn lại theo thân (mép thân quanh y 4400-4500 theo spine ~60%, nếu chân chỉ theo hip sẽ hở khe)
    return [("foot_L", f + 1e-6)] + [(b, w * (1 - f) + 1e-6) for b, w in vband(cy)]


def w_ear_R(cx, cy):
    return tent(cy, [("ear_R2", 3850), ("ear_R1", 3935), ("head", 3995)])


def one(b): return lambda cx, cy: [(b, 1.0)]


def build_all():
    build()
    global BIDX
    BIDX = {b["name"]: i for i, b in enumerate(BONES)}
    # hàng điểm trong dọc cần ở đúng cao độ khớp (để tent uốn mượt) + quanh tai trái / bàn chân của thân
    pole_extra = [(POLE_X - 167, y - 264) for y in (3200, 3300, 3400)]
    body_extra = [(x - 246, y - 3755) for x, y in
                  [(470, 3900), (455, 3835), (448, 3790), (746, 4500), (746, 4440), (1336, 4345), (1290, 4320), (400, 3960), (560, 3960)]]
    spec = [
        ("claw_arm_L", one("arm_L"), dict(max_edge=140, step=170)),
        ("claw_knob_L", one("knob_L"), dict(max_edge=140, step=170)),
        ("cat_foot_L", w_foot, dict(max_edge=45, step=70)),
        ("cat_body", w_body, dict(max_edge=70, step=95, extra=body_extra)),
        ("cat_belly", w_belly, dict(max_edge=110, step=130)),
        ("cat_ear_R", w_ear_R, dict(max_edge=40, step=60)),
        ("claw_arm_R", one("arm_R"), dict(max_edge=140, step=170)),
        ("claw_knob_R", one("knob_R"), dict(max_edge=140, step=170)),
        ("claw_body", w_claw, dict(eps=1.5, max_edge=170, step=230, extra=pole_extra)),
    ]
    SLOT_BONE = {"claw_arm_L": "arm_L", "claw_knob_L": "knob_L", "cat_foot_L": "foot_L", "cat_body": "hip", "cat_belly": "hip",
                 "mouth": "mouth", "eye_L": "eye_L", "eye_R": "eye_R", "cat_ear_R": "ear_R1", "claw_arm_R": "arm_R",
                 "claw_knob_R": "knob_R", "claw_body": "claw", "cat_head": "head"}
    SLOT_ORDER = ["claw_arm_L", "claw_knob_L", "cat_foot_L", "cat_body", "claw_arm_R", "claw_knob_R", "claw_body",
                  "cat_head", "cat_belly", "mouth", "eye_L", "eye_R", "cat_ear_R"]
    skin, info = {}, {}
    for nm, fn, kw in spec:
        att, nv, nt, ws = make_mesh(nm, fn, **kw); skin[nm] = {nm: att}; info[nm] = (nv, nt, ws)
    import copy
    skin["cat_head"] = {"cat_head": copy.deepcopy(skin["cat_body"]["cat_body"])}      # cùng lưới + weight với cat_body: hai mảnh biến dạng giống hệt
    info["cat_head"] = info["cat_body"]
    for slot in ("mouth", "eye_L", "eye_R"):         # 2 biến thể (region, tâm ảnh -> toạ độ xương, đứng thẳng ở setup)
        skin[slot] = {}
        for var in ("keo", "nam"):
            nm = {"mouth": "mouth_", "eye_L": "eye_L_", "eye_R": "eye_R_"}[slot] + var
            x0, y0, x1, y1 = LAY[nm]["bbox"]
            lx, ly = to_local(slot, *S((x0 + x1) / 2.0, (y0 + y1) / 2.0))
            skin[slot][nm] = {"type": "region", "x": round(lx, 3), "y": round(ly, 3), "rotation": round(-BW[slot][2], 3),
                              "width": x1 - x0, "height": y1 - y0}
    slots = []
    for n in SLOT_ORDER:
        s = {"name": n, "bone": SLOT_BONE[n], "attachment": n if n not in ("mouth", "eye_L", "eye_R") else
             {"mouth": "mouth_keo", "eye_L": "eye_L_keo", "eye_R": "eye_R_keo"}[n]}
        # cat_belly: PSD là multiply 16%, nhưng multiply của runtime Spine với PNG không PMA làm SÁNG vùng bóng (đã thấy trên Spine Live).
        # Ảnh đã nướng alpha 16% nên blend normal cho kết quả gần như y hệt (lệch < 2/255).
        slots.append(s)
    sk = {"skeleton": {"spine": "4.2.43", "fps": FPS, "images": "./images/"}, "bones": BONES, "slots": slots,
          "skins": [{"name": "default", "attachments": {n: skin[n] for n in SLOT_ORDER}}], "animations": {}}
    return sk, info


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "meo.json")
    prev = json.load(open(out, encoding="utf8")) if os.path.exists(out) else None
    if prev and not os.environ.get("MEO_REBUILD"):
        sys.exit("File %s đã có: người dùng có thể đã sửa lưới / weight. Đọc spine_live_cmd.py history rồi mới đặt MEO_REBUILD=1." % out)
    sk, info = build_all()
    if prev and prev.get("animations"): sk["animations"] = prev["animations"]      # giữ anim đã có
    if not os.environ.get("ANIM_KIT_DRY"):
        try:
            import spine_live_cmd
            spine_live_cmd.claude_backup(out, "Claude dựng rig MeoWinstreak")
        except Exception as e:
            print("(không ghi được backup Spine Live:", e, ")")
    json.dump(sk, open(out, "w", encoding="utf8"), indent=1)
    print("Đã ghi", out, "|", len(sk["bones"]), "xương,", len(sk["slots"]), "slot")
    for k, (nv, nt, ws) in info.items():
        tot = sum(ws.values())
        print(f"  {k:12s} {nv:3d} đỉnh / {nt:3d} tam giác | weight theo xương:", {b: round(v, 1) for b, v in sorted(ws.items(), key=lambda t: -t[1])})
