"""Fire spec v3 (art lead line art fire_lineart_v1.png): outer silhouette from big C / hook / quarter-bite,
middle tongue with a scalloped (chain of small C) bottom edge, 3-lobe cloud core at the base,
a lens-shaped detached sliver on top and a small notched tongue upper-right."""
import importlib.util
import math
import random
import sys

from PIL import Image, ImageChops

base = r"C:/Users/Manh/AppData/Local/Temp/claude/D--Game-prj-VFX-LIb/9d8d4544-4411-4651-a2b4-a626cb5e261d/scratchpad/tools/"
spec = importlib.util.spec_from_file_location("ff", base + "fire_flame.py")
ff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ff)
mt = ff.mt


def lens(c, cx, cy, w, h, tilt):
    """Pointed both ends: intersection of two big circles (a thin vertical leaf)."""
    r = (h * h / 4 + w * w / 4) / w
    ca, sa = math.cos(tilt), math.sin(tilt)
    off = r - w / 2
    a = c.ellipse(c.new(), cx + ca * off, cy + sa * off, r, r)
    b = c.ellipse(c.new(), cx - ca * off, cy - sa * off, r, r)
    return ImageChops.multiply(a, b)


def scallop_below(c, x0, x1, y, bumps, depth):
    """Mask of everything BELOW a scalloped line: a chain of `bumps` small C-arcs hanging down."""
    pts = []
    for i in range(bumps):
        a0, a1 = x0 + (x1 - x0) * i / bumps, x0 + (x1 - x0) * (i + 1) / bumps
        cx, r = (a0 + a1) / 2, (a1 - a0) / 2
        for k in range(21):
            ang = math.pi + math.pi * k / 20            # lower half circle: a U hanging down
            pts.append((cx + math.cos(ang) * r, y + math.sin(ang) * r * depth))
    pts = [(-1.2, pts[0][1]), *pts, (1.2, pts[-1][1]), (1.2, -1.2), (-1.2, -1.2)]
    return c.polygon(c.new(), pts)


def flame_v7(seed, n=460, tones=3, jitter=1.0):
    rnd = random.Random(seed)
    J = lambda v: v * (1 + rnd.uniform(-0.15, 0.15) * jitter)
    j = lambda: rnd.uniform(-0.05, 0.05) * jitter
    c = mt.Canvas(n)
    # ---- outer silhouette
    sil = c.new()
    c.ellipse(sil, -0.03 + j(), -0.36 + j(), J(0.46), J(0.46))                          # bottom C bowl
    left = ff.place(ff.random_tongue(rnd, notch=False), J(0.34), J(0.62), 0.35, -0.24 + j(), -0.02 + j(), False)
    c.polygon(sil, left)                                                                   # left lobe, hook tip up-left
    right = c.ellipse(c.new(), 0.22 + j(), 0.05 + j(), J(0.22), J(0.27))                  # right bulge
    bite = c.ellipse(c.new(), 0.36 + j(), -0.26 + j(), J(0.13), J(0.15))                   # quarter-circle bite on the right flank
    upper = ff.place(ff.random_tongue(rnd, notch=False), J(0.42), J(0.62), -0.1, 0.03 + j(), 0.2 + j(), True)
    c.polygon(sil, upper)
    sil = ImageChops.lighter(sil, right)
    sil = mt.sub(sil, bite)
    smooth = lambda m: c.blur(m, 0.006).point(lambda q: 255 if q >= 128 else 0)
    sil = ff.fill_holes(smooth(sil))
    # ---- middle tongue region with a scalloped bottom edge
    mid = ImageChops.multiply(smooth(c.polygon(c.new(), upper)), sil)
    mid = mt.sub(mid, scallop_below(c, -0.08 + j(), 0.3 + j(), 0.02 + j(), rnd.choice((2, 3)), J(0.8)))
    # ---- 3-lobe cloud core at the base
    core = c.new()
    c.ellipse(core, -0.03 + j(), -0.43 + j(), J(0.2), J(0.2))
    c.ellipse(core, -0.23 + j(), -0.57 + j(), J(0.14), J(0.15))
    c.ellipse(core, 0.17 + j(), -0.56 + j(), J(0.14), J(0.15))
    core = ImageChops.multiply(smooth(core), sil)
    # ---- detached pieces
    det = lens(c, -0.06 + j(), 0.8 + j(), J(0.07), J(0.24), math.pi / 2 + rnd.uniform(-0.2, 0.2))
    small = ff.place(ff.random_tongue(rnd, notch=True), J(0.14), J(0.17), -0.4, 0.22 + j(), 0.56 + j(), True)
    det = ImageChops.lighter(det, smooth(c.polygon(c.new(), small)))
    if tones == 1:
        img = ImageChops.lighter(sil, det)
    else:
        img = Image.new("L", (c.N, c.N), 0)
        img.paste(int(255 * 0.55), mask=sil)
        img.paste(int(255 * 0.75), mask=mid)
        img.paste(int(255 * 0.95), mask=core)
        img.paste(int(255 * 0.6), mask=det)
    if rnd.random() < 0.5 and jitter > 0:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return c.down(img)


if __name__ == "__main__":
    out, lineart = sys.argv[1], sys.argv[2]
    # 1) unjittered build with the art lead's lines on top (same frame: x_px = line_x + 93, y_px = line_y)
    ref = flame_v7(0, 460, 3, jitter=0.0).convert("RGB")
    la = Image.open(lineart).convert("RGB")
    mask = la.convert("L").point(lambda q: 255 if q > 60 else 0)
    ref.paste((255, 60, 40), (93, 0), mask)
    ref.save(out + "_overlay.png")
    # 2) random variants
    tiles = [flame_v7(s, 384, 3) for s in (1, 2, 3)] + [flame_v7(s, 384, 1) for s in (1, 2, 3)]
    sheet = Image.new("RGB", (384 * 3 + 16, 384 * 2 + 8), (40, 40, 48))
    for i, t in enumerate(tiles):
        sheet.paste(t.convert("RGB"), ((i % 3) * 392, (i // 3) * 392))
    sheet.save(out + "_flames.png")
    print("ok")
