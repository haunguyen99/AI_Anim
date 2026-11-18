# Weight map: each vertex coloured by its joints' blend; 3 views. py -I plotw.py [mesh] [out.png]
import json, sys, colorsys
from PIL import Image, ImageDraw
mesh = sys.argv[1] if len(sys.argv) > 1 else "Pet_lucky_neko"
out = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\Admin\AppData\Local\Temp\wplot.png"
d = json.load(open(r"C:\Users\Admin\AppData\Local\Temp\_lucky_w_now.json"))[mesh]
P = d["P"]; W = d["W"]
names = sorted({j for w in W for j, _ in w})
col = {j: tuple(int(255 * c) for c in colorsys.hsv_to_rgb((i * 0.618) % 1, 0.85, 0.95)) for i, j in enumerate(names)}
def color(w):
    r = [0, 0, 0]
    for j, v in w:
        for k in range(3): r[k] += col[j][k] * v
    return tuple(int(c) for c in r)
C = [color(w) for w in W]
S = 1700; H = 1000
views = [(0, 1, 1, "front"), (2, 1, -1, "side(face left)"), (0, 2, 1, "top")]
xs = [p[0] for p in P]; ys = [p[1] for p in P]; zs = [p[2] for p in P]
img = Image.new("RGB", (S, H + 80), (30, 30, 30)); dr = ImageDraw.Draw(img)
for vi, (ix, iy, sg, t) in enumerate(views):
    a = [p[ix] * sg for p in P]; b = [p[iy] for p in P]
    x0, x1, y0, y1 = min(a), max(a), min(b), max(b)
    sc = min((S / 3 - 40) / (x1 - x0 + 1e-9), (H - 60) / (y1 - y0 + 1e-9))
    ox = vi * S / 3 + 20
    for p, c in zip(P, C):
        u = ox + (p[ix] * sg - x0) * sc; v = H - 30 - (p[iy] - y0) * sc
        dr.ellipse([u - 4, v - 4, u + 4, v + 4], fill=c)
    dr.text((ox, 5), t, fill=(255, 255, 255))
x = 10
for j in names:
    dr.rectangle([x, H + 20, x + 12, H + 32], fill=col[j]); dr.text((x + 15, H + 20), j[4:], fill=(255, 255, 255)); x += 15 + 7 * len(j[4:]) + 14
img.save(out)
