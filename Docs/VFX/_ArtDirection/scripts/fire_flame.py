"""Fire spec v2: random-curvature tongues (from the art lead's sketch) composed into a flame column
like the art lead's reference: tongues shrinking upward, nested brighter inner layers, detached pieces."""
import importlib.util
import math
import random
import sys

from PIL import Image, ImageChops, ImageDraw

spec = importlib.util.spec_from_file_location("mt", r"D:/Game_prj/VFX_LIb/.claude/skills/vfx-maker/scripts/make_texture.py")
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)

# Sketch tips (normalised, y up) and how far each edge's controls sit off its chord (+ = left of travel)
CX, CY, SC = 105.0, 128.0, 1 / 110.0
def n_(x, y): return ((x - CX) * SC, -(y - CY) * SC)
TIPS = {"A": n_(60, 42), "C": n_(160, 106), "D": n_(178, 180), "B": n_(34, 158)}
SKETCH_CTRL = {"AC": [n_(110, 40), n_(152, 70)], "CD": [n_(132, 128), n_(138, 166)],
               "DB": [n_(140, 228), n_(60, 215)], "BA": [n_(70, 120), n_(82, 70)]}


def bez(p0, p1, p2, p3, n=36):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def edge_offsets(p, q, ctrls):
    """Express sketch controls as (along, off) relative to chord p->q."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy)
    ux, uy, nx, ny = dx / L, dy / L, -dy / L, dx / L
    return [(((cx - p[0]) * ux + (cy - p[1]) * uy) / L, ((cx - p[0]) * nx + (cy - p[1]) * ny) / L) for cx, cy in ctrls]


BASE = {k: edge_offsets(TIPS[k[0]], TIPS[k[1]], SKETCH_CTRL[k]) for k in SKETCH_CTRL}


def random_tongue(rnd, notch=True):
    return upright(_random_tongue(rnd, notch))


def _random_tongue(rnd, notch=True):
    """Same structure as the sketch, but every edge gets its own random curvature:
    more, less, or flipped (the notch CD stays a bite but its depth varies). Tips wander too."""
    tips = {k: (x + rnd.uniform(-0.07, 0.07), y + rnd.uniform(-0.07, 0.07)) for k, (x, y) in TIPS.items()}
    pts = []
    for k in ("AC", "CD", "DB", "BA"):
        p, q = tips[k[0]], tips[k[1]]
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        ux, uy, nx, ny = dx / L, dy / L, -dy / L, dx / L
        amp = rnd.uniform(0.5, 1.4)                  # bend more or less than the sketch
        if k != "CD" and rnd.random() < 0.15:
            amp = -rnd.uniform(0.3, 0.6)            # flip the bend direction
        if k == "CD" and not notch:
            amp = -rnd.uniform(0.2, 0.5)            # no bite on this tongue: the notch edge bulges out gently
        skew = rnd.uniform(-0.08, 0.08)              # move the bulge along the edge
        ctrl = [(p[0] + ux * (a + skew) * L + nx * o * amp * L, p[1] + uy * (a + skew) * L + ny * o * amp * L) for a, o in BASE[k]]
        seg = bez(p, ctrl[0], ctrl[1], q)
        pts += seg if not pts else seg[1:]
    return pts


def upright(pts):
    """Rotate a tongue so its tip (first point = tip A) points straight up from the shape's centroid."""
    cx = sum(x for x, _ in pts) / len(pts)
    cy = sum(y for _, y in pts) / len(pts)
    ax, ay = pts[0]
    rot = math.pi / 2 - math.atan2(ay - cy, ax - cx)
    ca, sa = math.cos(rot), math.sin(rot)
    return [((x - cx) * ca - (y - cy) * sa, (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def place(pts, sx, sy, rot, tx, ty, flip):
    ca, sa = math.cos(rot), math.sin(rot)
    out = []
    for x, y in pts:
        x = -x if flip else x
        x, y = x * sx, y * sy
        out.append((x * ca - y * sa + tx, x * sa + y * ca + ty))
    return out


def fill_holes(mask):
    """Remove every enclosed hole/splinter inside the silhouette (art lead: no holes inside the body)."""
    w, h = mask.size
    pad = Image.new("L", (w + 2, h + 2), 0)
    pad.paste(mask.point(lambda q: 255 if q >= 128 else 0), (1, 1))
    ImageDraw.floodfill(pad, (0, 0), 128)
    return pad.crop((1, 1, w + 1, h + 1)).point(lambda q: 0 if q == 128 else 255)


def flame(seed, n=512, tones=3):
    """Few big sections: a base bowl, one big upper tongue, one medium side tongue, optional small top tongue,
    and one detached piece. Each section has its own value so overlaps read as clean region lines."""
    rnd = random.Random(seed)
    c = mt.Canvas(n)
    side = rnd.choice((-1, 1))
    plan = [  # (value, scale x, scale y, y, x, lean, notch)
        (0.6, 0.62, 0.66, -0.34, 0.0, 0.0, True),                                                    # base bowl
        (0.72, rnd.uniform(0.42, 0.48), rnd.uniform(0.66, 0.74), 0.08, side * rnd.uniform(0.08, 0.14), side * rnd.uniform(0.1, 0.2), False),
        (0.66, rnd.uniform(0.3, 0.35), rnd.uniform(0.48, 0.56), 0.0, -side * rnd.uniform(0.18, 0.24), -side * rnd.uniform(0.15, 0.3), True),
    ]
    if rnd.random() < 0.6:
        plan.append((0.78, rnd.uniform(0.17, 0.21), rnd.uniform(0.32, 0.38), 0.42, side * rnd.uniform(0.0, 0.1), rnd.uniform(-0.2, 0.2), False))
    layers = []
    for val, sx, sy, ty, tx, lean, notch in plan:
        rot = -lean + rnd.uniform(-0.08, 0.08)
        layers.append((val, place(random_tongue(rnd, notch=notch), sx, sy, rot, tx, ty, rnd.random() < 0.5)))
    layers.append((0.9, place(random_tongue(rnd, notch=False), 0.34, 0.4, rnd.uniform(-0.1, 0.1), 0.0, -0.42, rnd.random() < 0.5)))  # bright inner tongue
    s = rnd.uniform(0.1, 0.13)                                                                       # one detached piece
    detached = place(random_tongue(rnd, notch=False), s, s * 1.35, rnd.uniform(-0.4, 0.4), -side * rnd.uniform(0.05, 0.2), rnd.uniform(0.62, 0.72), rnd.random() < 0.5)

    def smooth(m):
        return c.blur(m, 0.006).point(lambda q: 255 if q >= 128 else 0)

    silhouette = c.new()
    for _, poly in layers:
        c.polygon(silhouette, mt.clamp_pts(poly, 0.97))
    silhouette = fill_holes(smooth(silhouette))
    det = smooth(c.polygon(c.new(), mt.clamp_pts(detached, 0.97)))
    if tones == 1:
        img = ImageChops.lighter(silhouette, det)
    else:
        img = Image.new("L", (c.N, c.N), 0)
        for val, poly in layers:          # paint sections in plan order: later sections overlap earlier ones
            m = ImageChops.multiply(fill_holes(smooth(c.polygon(c.new(), mt.clamp_pts(poly, 0.97)))), silhouette)
            img.paste(int(255 * val), mask=m)
        img.paste(int(255 * 0.66), mask=det)
        core = c.blur(c.ellipse(c.new(), 0, -0.5, 0.18, 0.16), 0.08)
        img = ImageChops.lighter(img, core)
    return c.down(img)


if __name__ == "__main__":
    out = sys.argv[1]
    tiles = [flame(s, 384, 3) for s in (1, 2, 3)] + [flame(s, 384, 1) for s in (1, 2, 3)]
    sheet = Image.new("RGB", (384 * 3 + 16, 384 * 2 + 8), (40, 40, 48))
    for i, t in enumerate(tiles):
        sheet.paste(t.convert("RGB"), ((i % 3) * 392, (i // 3) * 392))
    sheet.save(out + "_flames.png")
    rnd = random.Random(11)
    c = mt.Canvas(192)
    tsheet = Image.new("RGB", (192 * 6 + 40, 192), (40, 40, 48))
    for i in range(6):
        tsheet.paste(c.down(c.polygon(c.new(), place(random_tongue(rnd), 0.75, 0.75, 0, 0, 0, False))).convert("RGB"), (i * 200, 0))
    tsheet.save(out + "_tongues.png")
    print("ok")
