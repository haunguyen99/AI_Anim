"""Tách mắt khỏi layer Head (mắt vẽ liền trong ảnh) để chớp mắt: src/Head.png -> images/Head.png (mắt đã vá bằng da) +
images/eye_L.png, eye_R.png (con ngươi tối, alpha mềm) + eyes.json (tâm, góc trục dọc mắt, kích thước; toạ độ canvas PSD).
Chạy: .venv/Scripts/python.exe -I work/daily_reward/spine/FlagChar/prep_eyes.py
Mắt phải (viewer phải) bị ống miệng che phần dưới: chỉ lấy phần thấy được, điểm neo ở đáy (mép ống) để chớp = hạ mí từ trên xuống."""
import json, math, os, sys
import numpy as np, cv2
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
HEAD_XY = (0, 20)                                   # góc trên trái layer Head trong canvas PSD
im = np.array(Image.open(os.path.join(HERE, "src", "Head.png")).convert("RGBA"))
rgb = im[..., :3].astype(np.float32); alpha = im[..., 3]
L = rgb.mean(2)
dark = ((L < 100) & (alpha > 200)).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(dark)
PICK = {"eye_L": 12, "eye_R": 11}                   # id thành phần (xem phân tích): bbox (173,227,34,60) và (259,219,28,28)
# chọn lại theo bbox cho chắc (id có thể đổi nếu ảnh đổi)
want = {"eye_L": (173, 227, 34, 60), "eye_R": (259, 219, 28, 28)}
ids = {}
for k, (x, y, w, h) in want.items():
    for i in range(1, n):
        if abs(st[i, 0] - x) <= 3 and abs(st[i, 1] - y) <= 3 and abs(st[i, 2] - w) <= 4 and abs(st[i, 3] - h) <= 4: ids[k] = i
assert len(ids) == 2, ids
head = im.copy(); out = {}
allmask = np.zeros(alpha.shape, np.uint8)
for k, i in ids.items():
    core = (lab == i).astype(np.uint8)
    cs, _ = cv2.findContours(core, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros_like(core); cv2.drawContours(filled, cs, -1, 1, -1)
    band = cv2.dilate(filled, np.ones((5, 5), np.uint8))                                   # dải mép 2 px
    soft = np.clip((200.0 - L) / (200.0 - 45.0), 0, 1) * band
    a = np.where(filled > 0, 1.0, soft).astype(np.float32)
    a = cv2.GaussianBlur(a, (0, 0), 0.6)
    ys, xs = np.nonzero(a > 0.02); x0, x1, y0, y1 = xs.min() - 1, xs.max() + 2, ys.min() - 1, ys.max() + 2
    # màu: trong lõi lấy gốc, ngoài lõi kéo màu lõi ra (không lẫn da cam vào viền)
    miss = ((filled == 0)).astype(np.uint8) * 255
    col = cv2.inpaint(np.clip(rgb, 0, 255).astype(np.uint8), miss, 3, cv2.INPAINT_TELEA)
    patch = np.dstack([col, (a * 255).astype(np.uint8)])[y0:y1, x0:x1]
    Image.fromarray(patch, "RGBA").save(os.path.join(HERE, "images", k + ".png"))
    allmask |= cv2.dilate(filled, np.ones((7, 7), np.uint8))
    pts = np.argwhere(filled > 0)[:, ::-1].astype(np.float64)                                # (x, y)
    c = pts.mean(0); u, s, vt = np.linalg.svd(pts - c, full_matrices=False)
    ax = vt[0] if vt[0][1] < 0 else -vt[0]                                                   # hướng lên (y ảnh giảm)
    ang = math.degrees(math.atan2(-ax[1], ax[0]))                                            # độ, y lên
    bb = tuple(int(v) for v in (x0 + HEAD_XY[0], y0 + HEAD_XY[1], x1 - x0, y1 - y0))
    out[k] = {"bbox": bb, "center": [round(float(c[0]) + HEAD_XY[0], 2), round(float(c[1]) + HEAD_XY[1], 2)], "angle": round(float(ang), 2),
              "core_h": int(filled.sum(0).max()), "core_bbox": [int(pts[:, 0].min()) + HEAD_XY[0], int(pts[:, 1].min()) + HEAD_XY[1],
                                                               int(pts[:, 0].max()) + HEAD_XY[0], int(pts[:, 1].max()) + HEAD_XY[1]]}
    print(k, out[k])
fill = cv2.inpaint(np.clip(rgb, 0, 255).astype(np.uint8), allmask * 255, 5, cv2.INPAINT_TELEA)
head[..., :3] = np.where(allmask[..., None] > 0, fill, head[..., :3])
Image.fromarray(head, "RGBA").save(os.path.join(HERE, "images", "Head.png"))
out["eye_R"]["angle"] = out["eye_L"]["angle"]      # mắt phải bị ống che nên PCA sai: dùng góc mắt trái
json.dump(out, open(os.path.join(HERE, "eyes.json"), "w"), indent=1)
