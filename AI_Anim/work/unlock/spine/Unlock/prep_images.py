"""Tách PSD unlock.psd thành PNG từng bộ phận (images/) + parts.json (bbox trên canvas PSD, y xuống).
Chạy: .venv/Scripts/python.exe -I work/unlock/spine/Unlock/prep_images.py
PSD gốc: 4 layer = L0 dải ruy băng (RGB nền xanh lá, alpha thật), L1 3 cái nơ (1 layer), L2 / L3 hai nửa kéo.
Việc làm: (1) khử viền xanh lá, (2) tách nơ theo thành phần liên thông, (3) cắt dải ruy băng ở X_SEAM (dưới nơ giữa),
hai nửa chồng nhau SEAM_OV px để không hở mép."""
import json, os, numpy as np, cv2
from PIL import Image
from psd_tools import PSDImage

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images")
X_SEAM, SEAM_OV = 882, 4

psd = PSDImage.open(os.path.join(HERE, "unlock.psd"))
W, H = psd.size
canvas = []
for l in psd:
    im = l.topil().convert("RGBA")
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); c.paste(im, (l.left, l.top)); canvas.append(np.array(c))


def despill(a):
    """viền xanh lá (g > max(r,b)) -> lấy màu từ điểm sạch lân cận (tích chập chuẩn hoá)"""
    a = a.copy(); r, g, b, al = [a[..., i].astype(np.float32) for i in range(4)]
    bad = (g > np.maximum(r, b) + 4) & (al > 0)
    good = ((~bad) & (al > 200)).astype(np.float32)
    for _ in range(3):
        k = 5
        num = cv2.blur(a[..., :3].astype(np.float32) * good[..., None], (k, k))
        den = cv2.blur(good, (k, k))[..., None]
        fill = num / np.maximum(den, 1e-4)
        m = bad & (den[..., 0] > 0.02)
        a[..., :3][m] = fill[m]
        good = np.where(m, 1.0, good).astype(np.float32); bad = bad & ~m
    a[..., 3][bad] = 0
    return a


parts = {}


def save(name, arr, box=None):
    al = arr[..., 3] > 8
    if box is None:
        ys, xs = np.where(al); box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    x0, y0, x1, y1 = [int(v) for v in box]
    Image.fromarray(arr[y0:y1, x0:x1]).save(os.path.join(OUT, name + ".png"))
    parts[name] = {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}


L0, L1, L2, L3 = [despill(c) for c in canvas]
# dải ruy băng: hai nửa quanh X_SEAM
left = L0.copy(); left[:, X_SEAM + SEAM_OV:, 3] = 0
right = L0.copy(); right[:, :X_SEAM - SEAM_OV, 3] = 0
save("ribbon_L", left); save("ribbon_R", right)
# nơ: thành phần liên thông của L1 (sắp theo x)
k, lab, st, cen = cv2.connectedComponentsWithStats((L1[..., 3] > 8).astype(np.uint8), 8)
big = sorted([i for i in range(1, k) if st[i, 4] > 2000], key=lambda i: cen[i][0])
assert len(big) == 3, big
for nm, i in zip(["bow_L", "bow_M", "bow_R"], big):
    m = (lab == i)
    arr = L1.copy(); arr[~m, 3] = 0
    save(nm, arr)
# kéo: L2 = nửa dưới-trái, L3 = nửa có ốc (trên)
save("scissor_B", L2); save("scissor_A", L3)
json.dump({"canvas": [W, H], "x_seam": X_SEAM, "parts": parts}, open(os.path.join(HERE, "parts.json"), "w"), indent=1)
print(json.dumps(parts))
