"""Mode 2 fire: whole flame per frame, 4x4 = 16-frame LOOP, multi-tone grayscale.

Art lead's construction (3 sketches, 2026-10-21):
  * skeleton = 4 circles stacked bottom -> top, zig-zag left/right, shrinking upward (1 biggest at the base);
  * the flame outline wraps the circles: one bulging lobe per circle, joined by necks; at the necks concave
    bites alternate sides (the  ) (  pair) and leave small hooks;
  * fire rises: the circles drift up and shrink; the top one leaves through the top and comes back at the
    base as the biggest -> the order repeats -> seamless loop.

  python fire_sheet.py OUT_DIR
"""
import math
import os
import sys
import importlib.util

from PIL import Image, ImageChops, ImageDraw, ImageFilter

spec = importlib.util.spec_from_file_location("mt", r"D:/Game_prj/VFX_LIb/.claude/skills/vfx-maker/scripts/make_texture.py")
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)

N_CIRCLES = 4
Y_BOTTOM, Y_TOP = -0.55, 0.62          # where a circle is born and where it leaves
R_BOTTOM, R_TOP = 0.2, 0.075           # radius at the base and at the top
X_SWAY = 0.2                           # zig-zag offset
LOBE = 1.75                            # lobe radius = circle radius * LOBE (outline wraps well around the circle)


def smoothstep(e0, e1, x):
    return mt.smoothstep(e0, e1, x)


import random as _random

# Loop rule: frame(t=1) must equal frame(t=0). Every circle climbs exactly one slot per sheet, so circle k ends
# where circle k+1 started; that holds as long as position and size depend on (height, t) with t-periodic terms.

def spine_x(y, t):
    """Swaying S-shaped spine (art lead's yellow/blue/green curves): x of the flame's backbone at height y.
    Only whole-number time frequencies -> spine at t=1 is identical to t=0."""
    return (0.24 * math.sin(3.0 * y + math.tau * t)
            + 0.07 * math.sin(5.6 * y - 2 * math.tau * t + 1.0)
            + 0.04 * math.sin(math.tau * t + 2.0))


_SIZE_KNOTS = [_random.Random(5).uniform(0.7, 1.3) for _ in range(9)]


def size_mult(u):
    """Random but smooth size factor along the climb (sizes need not shrink monotonically)."""
    f = u * (len(_SIZE_KNOTS) - 1)
    i = min(int(f), len(_SIZE_KNOTS) - 2)
    k = f - i
    k = k * k * (3 - 2 * k)
    return _SIZE_KNOTS[i] + (_SIZE_KNOTS[i + 1] - _SIZE_KNOTS[i]) * k


def circles_at(t):
    """t in [0,1) over the whole sheet = every circle climbs exactly ONE slot along the swaying spine."""
    out = []
    for idx in range(N_CIRCLES):
        u = ((idx + t) / N_CIRCLES) % 1.0                         # 0 = slot 1 at the base, 1 = leaving the top
        y = Y_BOTTOM + (Y_TOP - Y_BOTTOM) * (u ** 0.9)
        r = (R_BOTTOM + (R_TOP - R_BOTTOM) * u) * size_mult(u) * (1 + 0.08 * math.sin(math.tau * t + 3 * u))
        r *= smoothstep(0.0, 0.08, u) * 0.35 + 0.65 if u < 0.08 else 1.0     # swell in at the base, no pop
        r *= 1 - smoothstep(0.86, 1.0, u)                                     # shrink to nothing at the top
        out.append((spine_x(y, t), y, r, u, idx))
    return sorted(out, key=lambda c: c[1])


def neck(c, a, b, w):
    """Capsule joining two lobes (width w x the smaller lobe radius)."""
    (x0, y0, r0), (x1, y1, r1) = a, b
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1e-9
    nx, ny = -dy / L, dx / L
    h0, h1 = r0 * w, r1 * w
    return c.polygon(c.new(), [(x0 + nx * h0, y0 + ny * h0), (x1 + nx * h1, y1 + ny * h1),
                               (x1 - nx * h1, y1 - ny * h1), (x0 - nx * h0, y0 - ny * h0)])


def fill_holes(mask):
    """No enclosed holes or specks inside the body."""
    w, h = mask.size
    pad = Image.new("L", (w + 2, h + 2), 0)
    pad.paste(mask.point(lambda q: 255 if q >= 128 else 0), (1, 1))
    ImageDraw.floodfill(pad, (0, 0), 128)
    return pad.crop((1, 1, w + 1, h + 1)).point(lambda q: 0 if q == 128 else 255)


def frame(t, n=256):
    c = mt.Canvas(n)
    cs = circles_at(t)
    live = [(x, y, r, u, i) for x, y, r, u, i in cs if r > 0.012]
    body = c.new()
    for x, y, r, u, i in live:
        c.ellipse(body, x, y, r * LOBE, r * LOBE * 1.08)           # lobe around each circle, slightly tall
    for a, b in zip(live, live[1:]):
        body = ImageChops.lighter(body, neck(c, (a[0], a[1], a[2] * LOBE), (b[0], b[1], b[2] * LOBE), 0.55))
    body = c.blur(body, 0.03).point(lambda q: 255 if q >= 110 else 0)   # fuse lobes and necks organically
    # one concave bite per neck, on the side away from the upper lobe, alternating up the column ( ) ( ).
    # The bite circle sits mostly OUTSIDE the body so it only takes a 1/4..1/2-circle arc out of the edge.
    bites = c.new()
    bpx = body.load()
    for a, b in zip(live, live[1:]):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        side = 1 if b[0] > a[0] else -1                              # the upper lobe leans to `side`
        row = int((1 - my) / 2 * c.N)
        if not 0 <= row < c.N:
            continue
        xs = [x for x in range(c.N) if bpx[x, row]]
        if not xs:
            continue
        edge_px = xs[0] if side > 0 else xs[-1]                      # real silhouette edge on the bite side
        ex = edge_px / c.N * 2 - 1
        rb = min(a[2], b[2]) * LOBE * 0.7
        c.ellipse(bites, ex - side * rb * 0.15, my, rb, rb)          # centre just outside the edge: ~150-deg arc bite
    body = mt.sub(body, bites)
    # flame tips: each circle grows an approved mode-1 tongue as it climbs past u=0.55 (continuous in time)
    import random as _r
    base_tongue = mt.fire_element_outline(_r.Random(11), "waisted")
    ys0 = [y for _, y in base_tongue]
    xs0 = [x for x, _ in base_tongue]
    h0, cx0 = max(ys0) - min(ys0), sum(xs0) / len(xs0)
    for x, y, r, u, i in live:
        g = smoothstep(0.55, 0.75, u)
        if g <= 0.01:
            continue
        sc = r * LOBE * 2.2 * g / h0
        side = 1 if x < 0 else -1                                    # curl toward the column centre
        tongue = [((tx - cx0) * sc * side + x, (ty - min(ys0)) * sc + y - r * LOBE * 0.5) for tx, ty in base_tongue]
        c.polygon(body, mt.clamp_pts(tongue, 0.97))
    body = fill_holes(c.blur(body, 0.006).point(lambda q: 255 if q >= 128 else 0))
    # tones: outer flame, brighter zone around the circles, brightest core at the base
    # brighter nested layer: the silhouette shrunk inward (an inner flame parallel to the outline), lifted a bit
    inner = c.blur(body, 0.07).point(lambda q: 255 if q >= 225 else 0)
    inner = ImageChops.offset(inner, 0, int(c.N * 0.015))
    inner = ImageChops.multiply(inner, body)
    core = c.new()
    bx, by, br, bu, bi = live[0]
    c.ellipse(core, bx, by - br * 0.1, br * 0.85, br * 0.8)
    core = ImageChops.multiply(c.blur(core, 0.04), body)
    img = Image.new("L", (c.N, c.N), 0)
    img.paste(int(255 * 0.55), mask=body)
    img.paste(int(255 * 0.78), mask=inner)
    img = ImageChops.lighter(img, core.point(lambda q: int(q * 0.97)))
    return c.down(img)


GRAD = [(0.0, (0, 0, 0)), (0.5, (150, 20, 25)), (0.6, (230, 70, 20)), (0.8, (255, 165, 40)), (1.0, (255, 245, 200))]


def colorize(gray):
    lut = []
    for v in range(256):
        u = v / 255
        for (a, ca), (b, cb) in zip(GRAD, GRAD[1:]):
            if u <= b:
                k = (u - a) / (b - a)
                lut.append(tuple(int(ca[i] + (cb[i] - ca[i]) * k) for i in range(3)))
                break
    r = gray.point([c[0] for c in lut]); g = gray.point([c[1] for c in lut]); b = gray.point([c[2] for c in lut])
    return Image.merge("RGB", (r, g, b))


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    cell = 256
    frames = [frame(i / 16, cell) for i in range(16)]
    sheet = Image.new("L", (cell * 4, cell * 4), 0)
    for i, f in enumerate(frames):
        sheet.paste(f, ((i % 4) * cell, (i // 4) * cell))
    sheet.convert("RGB").save(os.path.join(out, "T_Fire_Loop_4x4.png"))
    colorize(sheet).save(os.path.join(out, "_loop_sheet_colored.png"))
    colored = [colorize(f) for f in frames]
    colored[0].save(os.path.join(out, "_loop_preview.gif"), save_all=True, append_images=colored[1:], duration=1000 // 12, loop=0)
    # skeleton debug: circles drawn over the first 4 frames
    dbg = Image.new("RGB", (cell * 4, cell), (0, 0, 0))
    for i in range(4):
        f = colorize(frames[i * 4]).copy()
        d = ImageDraw.Draw(f)
        tt = i * 4 / 16
        d.line([((spine_x(y, tt) + 1) / 2 * cell, (1 - y) / 2 * cell) for y in [Y_BOTTOM - 0.1 + k * 0.02 for k in range(70)]],
               fill=(120, 230, 120), width=2)
        for x, y, r, u, idx in circles_at(tt):
            if r > 0.012:
                px, py, pr = (x + 1) / 2 * cell, (1 - y) / 2 * cell, r / 2 * cell
                d.ellipse([px - pr, py - pr, px + pr, py + pr], outline=(80, 160, 255), width=2)
                d.text((px - 3, py - 6), str(idx + 1), fill=(80, 160, 255))
        dbg.paste(f, (i * cell, 0))
    dbg.save(os.path.join(out, "_loop_skeleton.png"))
    print("ok")
