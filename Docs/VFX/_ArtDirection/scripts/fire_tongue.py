"""Fire tongue from the art lead's sketch (fire spec v2): 4 tips joined by 4 smooth curves.

Tips (sketch coords, 216x256): A top-left (60,42), C right above the notch (160,106),
D right-bottom (178,180), B left (34,158).
Edges: A->C long convex arc (C / quarter-ellipse), C->D concave quarter-circle notch,
D->B big convex C (bottom), B->A gently concave edge bowing inward.
"""
import importlib.util
import math
import random
import sys

from PIL import Image, ImageDraw

spec = importlib.util.spec_from_file_location("mt", r"D:/Game_prj/VFX_LIb/.claude/skills/vfx-maker/scripts/make_texture.py")
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)

CX, CY, SC = 105.0, 128.0, 1 / 110.0


def norm(x, y):
    return ((x - CX) * SC, -(y - CY) * SC)


def bez(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


# control points traced from the sketch (sketch pixel coords)
SKETCH = {
    "A": (60, 42), "C": (160, 106), "D": (178, 180), "B": (34, 158),
    "AC": [(110, 40), (152, 70)],        # top edge bulges up-right
    "CD": [(132, 128), (138, 166)],      # notch: dips inward to x~136
    "DB": [(140, 228), (60, 215)],       # bottom C bulges down
    "BA": [(70, 120), (82, 70)],         # left edge bows inward (to x~76)
}


def tongue_outline(rnd=None, jitter=0.0, flip=False):
    def j(p):
        x, y = norm(*p)
        if rnd and jitter:
            x += rnd.uniform(-jitter, jitter)
            y += rnd.uniform(-jitter, jitter)
        return (-x, y) if flip else (x, y)
    A, B, C, D = (j(SKETCH[k]) for k in "ABCD")
    pts = []
    pts += bez(A, j(SKETCH["AC"][0]), j(SKETCH["AC"][1]), C)
    pts += bez(C, j(SKETCH["CD"][0]), j(SKETCH["CD"][1]), D)[1:]
    pts += bez(D, j(SKETCH["DB"][0]), j(SKETCH["DB"][1]), B)[1:]
    pts += bez(B, j(SKETCH["BA"][0]), j(SKETCH["BA"][1]), A)[1:]
    return pts


def render(outline, n=256, ss=4):
    c = mt.Canvas(n)
    img = c.polygon(c.new(), outline)
    return c.down(img)


if __name__ == "__main__":
    out = sys.argv[1]
    sketch = Image.open(sys.argv[2]).convert("L")
    exact = render(tongue_outline(), 256)
    # overlay: rebuilt fill (dim) with the art lead's sketch lines on top, in the sketch's own frame
    W, H = sketch.size
    ov = Image.new("RGB", (W, H))
    fill = Image.new("L", (W, H), 0)
    ImageDraw.Draw(fill).polygon([(x / SC + CX, -y / SC + CY) for x, y in tongue_outline()], fill=110)
    ov.paste((110, 70, 40), mask=fill)
    ov.paste((255, 255, 255), mask=sketch.point(lambda p: 255 if p > 60 else 0))
    ov.resize((W * 2, H * 2), Image.LANCZOS).save(out + "_overlay.png")
    rnd = random.Random(3)
    tiles = [exact] + [render(tongue_outline(rnd, 0.09, flip=(i % 2 == 1)), 256) for i in range(5)]
    sheet = Image.new("RGB", (256 * 3 + 16, 256 * 2 + 8), (40, 40, 48))
    for i, t in enumerate(tiles):
        sheet.paste(t.convert("RGB"), ((i % 3) * 264, (i // 3) * 264))
    sheet.save(out + "_variants.png")
    print("ok")
