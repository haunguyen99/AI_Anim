"""Mode 1 (single image randomized by a particle system): fire element candidates + particle preview.

Element = one fire tongue from the art lead's sketch (C edge, hook tip, quarter-circle bite), random curvature,
tip pointing up, filling ~88% of the square. The preview fakes a Unity particle system: particles rise,
shrink, rotate a little, flip randomly and go white-yellow -> orange -> red -> fade.

  python fire_particle_element.py OUT_DIR
"""
import importlib.util
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ff", os.path.join(HERE, "fire_flame.py"))
ff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ff)
mt = ff.mt


def self_intersects(pts):
    """True if the closed outline crosses itself (those give hairlines and crossed tips)."""
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    segs = list(zip(pts, pts[1:] + pts[:1]))
    for i in range(len(segs)):
        for j in range(i + 2, len(segs)):
            if i == 0 and j == len(segs) - 1:
                continue
            (a, b), (c, d) = segs[i], segs[j]
            if ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d):
                return True
    return False


def arc_edge(p, q, theta, side, steps=36):
    """Circular arc from p to q spanning `theta` radians, bulging to the left of p->q if side > 0."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    c = math.hypot(dx, dy) or 1e-9
    nx, ny = -dy / c * side, dx / c * side                 # bulge direction
    R = c / (2 * math.sin(theta / 2))
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    cx, cy = mx - nx * R * math.cos(theta / 2), my - ny * R * math.cos(theta / 2)
    a0 = math.atan2(p[1] - cy, p[0] - cx)
    best = None
    for sgn in (1, -1):                                    # pick the sweep that passes through the bulge
        am = a0 + sgn * theta / 2
        d = math.hypot(cx + math.cos(am) * R - (mx + nx * R * (1 - math.cos(theta / 2))),
                       cy + math.sin(am) * R - (my + ny * R * (1 - math.cos(theta / 2))))
        if best is None or d < best[0]:
            best = (d, sgn)
    sgn = best[1]
    return [(cx + math.cos(a0 + sgn * theta * i / steps) * R, cy + math.sin(a0 + sgn * theta * i / steps) * R) for i in range(steps + 1)]


# Frame rule (art lead): every element has TWO CONCAVE EDGES BACK TO BACK  ) (  on opposite sides of the body:
# the back edge B->A bows in, and the side bite C->D bows in from the other side. The leading edge A->C is
# convex, the bottom D->B convex. No extra bites beyond the  ) (  pair (art lead: an extra bottom bite is wrong). Variety comes from how deep each
# concave edge is (1/4..1/2 circle), proportions, tip height, curl direction and bottom detail - never from
# dropping or flipping one of the two concave edges.


def arc_tongue(rnd, look):
    T = {k: (x + rnd.uniform(-0.07, 0.07), y + rnd.uniform(-0.07, 0.07)) for k, (x, y) in ff.TIPS.items()}
    mx, my = (T["B"][0] + T["C"][0]) / 2, (T["B"][1] + T["C"][1]) / 2
    k = rnd.uniform(*look["k"])                          # tip height (chords at A must open ~60-80 deg)
    T["A"] = (mx + (T["A"][0] - mx) * k, my + (T["A"][1] - my) * k)
    side = {e: (1 if sum(o for _, o in ff.BASE[e]) > 0 else -1) for e in ff.BASE}
    deg = lambda r: math.radians(rnd.uniform(*r))
    edges = [(T["A"], T["C"], side["AC"], deg(look["ac"])),           # convex leading edge
             (T["C"], T["D"], side["CD"], deg(look["cd"]))]           # concave side bite  "("
    if look.get("bottom_bite"):                                       # bottom: two small convex lobes split by a bite
        E = ((T["D"][0] + T["B"][0]) / 2 + rnd.uniform(-0.05, 0.05), (T["D"][1] + T["B"][1]) / 2 - 0.12)
        edges += [(T["D"], E, side["DB"], deg((90, 130))), (E, T["B"], side["DB"], deg((90, 130)))]
    else:
        edges.append((T["D"], T["B"], side["DB"], deg(look["db"])))     # convex bottom
    edges.append((T["B"], T["A"], side["BA"], deg(look["ba"])))        # concave back edge ")"
    # sharp top tip: the back edge must bow in more than the leading edge bows out
    p0, q0, s0, th0 = edges[0]
    th0 = min(th0, math.radians(150))
    pl, ql, sl, thl = edges[-1]
    thl = min(math.radians(180), max(thl, th0 + math.radians(25)))
    edges[0], edges[-1] = (p0, q0, s0, th0), (pl, ql, sl, thl)
    pts = []
    for p, q, sd, th in edges:
        seg = arc_edge(p, q, th, sd)
        pts += seg if not pts else seg[1:]
    return ff.upright(pts)


def curl_tip(pts, amount):
    """Bend the upper part sideways (quadratic falloff) so the tip is a curve that hooks to one side."""
    ys = [y for _, y in pts]
    y0, y1 = min(ys) + 0.4 * (max(ys) - min(ys)), max(ys)
    h = max(ys) - min(ys)
    return [(x + amount * h * max(0.0, (y - y0) / (y1 - y0)) ** 2.2, y) for x, y in pts]


def fill_ratio(pts):
    """Polygon area / bounding-box area: low = thin, sliver-like element."""
    area = abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2
    xs, ys = [x for x, _ in pts], [y for _, y in pts]
    return area / ((max(xs) - min(xs)) * (max(ys) - min(ys)) or 1e-9)


def element(seed, n=512, look=None, aspect=1.0, curl=0.16):
    rnd = random.Random(seed)
    def tip_angle(q):
        (ax, ay), (bx, by), (cx_, cy_) = q[0], q[3], q[-4]
        a1, a2 = math.atan2(by - ay, bx - ax), math.atan2(cy_ - ay, cx_ - ax)
        d = abs(a1 - a2) % math.tau
        return math.degrees(min(d, math.tau - d))

    best = None
    for _ in range(400):   # draw until the outline is clean and the (curled) top tip is sharp; else keep the best
        cand = arc_tongue(rnd, look)
        cand = [(x * aspect, y) for x, y in cand]   # slim or wide body
        cand = curl_tip(cand, curl)
        score = max(0.0, tip_angle(cand) - 70) * 3 + (1000 if self_intersects(cand[::3]) else 0) + (300 if fill_ratio(cand) < 0.6 else 0) - fill_ratio(cand) * 20
        if best is None or score < best[0]:
            best = (score, cand)
        if tip_angle(cand) <= 70 and fill_ratio(cand) >= 0.64 and not self_intersects(cand[::3]):
            break
    pts = best[1]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    k = 1.76 / max(max(xs) - min(xs), max(ys) - min(ys))      # longest side -> 88% of the cell
    pts = [((x - cx) * k, (y - cy) * k) for x, y in pts]
    c = mt.Canvas(n)
    m = c.polygon(c.new(), pts)
    m = c.blur(m, 0.004).point(lambda q: 255 if q >= 128 else 0)
    return c.down(m), pts


EDGE_LEN = 36   # random_tongue = 4 Bezier edges of 36 steps each (tip A, C, D, B in order)


def concave_edge_weights(pts):
    """Per-point softness: 0 on convex edges; on edges that bow INTO the shape, a bump peaking at the
    apex of the curve (scaled by how deep it bows) and falling to 0 (sharp) at the junctions."""
    gx = sum(x for x, _ in pts) / len(pts)
    gy = sum(y for _, y in pts) / len(pts)
    w = [0.0] * len(pts)
    for e in range(4):
        i0, i1 = e * EDGE_LEN, min((e + 1) * EDGE_LEN, len(pts) - 1)
        p0, p1, pm = pts[i0], pts[i1], pts[(i0 + i1) // 2]
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        chord = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1e-9
        inward = math.hypot(pm[0] - gx, pm[1] - gy) < math.hypot(mx - gx, my - gy)
        if not inward:
            continue
        amp = max(0.7, min(1.0, math.hypot(pm[0] - mx, pm[1] - my) / chord * 9))   # every concave apex gets soft
        for i in range(i0, i1 + 1):
            t = (i - i0) / (i1 - i0)
            w[i] = max(w[i], amp * math.sin(math.pi * t) ** 1.3)
    return w


def edge_mix_concave(mask, pts, blur=0.05, motion=0.26, direction=90.0):
    """Soft at the apex of inward-bowing curves, sharpening toward the junctions; convex edges and tips sharp.
    The soft part is a MOTION blur along the motion direction (fire rises: 90 deg = up), not a uniform blur."""
    n = mask.size[0]
    soft = mt.motion_blur(mask, direction, motion * n, back=0.6).filter(ImageFilter.GaussianBlur(n * 0.025))   # motion first, light blur so edges parallel to the motion soften too
    w = concave_edge_weights(pts)
    W = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(W)
    to_px = lambda q: ((q[0] + 1) / 2 * n, (1 - q[1]) / 2 * n)
    width = max(2, int(motion * n * 1.3))
    for i in range(len(pts) - 1):
        v = int(255 * (w[i] + w[i + 1]) / 2)
        if v > 0:
            d.line([to_px(pts[i]), to_px(pts[i + 1])], fill=v, width=width)
    W = W.filter(ImageFilter.GaussianBlur(motion * n * 0.3))
    hi = W.getextrema()[1] or 1
    W = W.point(lambda q: min(255, int(q * 255 / hi * 1.15)))       # the apex reaches full softness
    return Image.composite(soft, mask, W)


def soft_body(mask, blur=0.07, lo=0.12, hi=0.85, motion=0.08, direction=90.0):
    """Art lead's reference look: blur the WHOLE shape, then levels so the core (far from edges) stays white
    while edges fall off broadly; concave apexes end up softest, tips keep their pointed outline but dim
    toward the point. A light motion blur along the motion direction adds the trailing streak."""
    n = mask.size[0]
    b = mask.filter(ImageFilter.GaussianBlur(blur * n))
    if motion > 0:
        b = Image.blend(b, mt.motion_blur(b, direction, motion * n, back=1.0), 0.5)
    lut = [int(255 * mt.smoothstep(lo, hi, q / 255) ** 0.9) for q in range(256)]
    return b.point(lut)


def soft_shaded(mask, pts, inner=0.09, lo=0.15, hi=0.8, motion=0.2):
    """Art lead's reference look, take 2: keep the silhouette (tips stay pointed), shade the inside with a
    core-to-edge falloff (white core, darker near the edges and in narrow tips), and only let the edge
    blur OUTWARD at the apex of concave curves (motion blur along the motion direction)."""
    n = mask.size[0]
    outline = edge_mix_concave(mask, pts, motion=motion)                      # sharp, soft only at concave apexes
    g = mask.filter(ImageFilter.GaussianBlur(inner * n))                       # distance-from-edge proxy
    lut = [int(255 * mt.smoothstep(lo, hi, q / 255) ** 0.8) for q in range(256)]
    g = g.point(lut)
    g = Image.blend(g, mt.motion_blur(g, 90.0, n * 0.06, back=1.0), 0.4)       # a hint of streak along the motion
    return ImageChops.multiply(outline, ImageChops.lighter(g, outline.point(lambda q: int(q * 0.18))))


def ps_motion_blur(mask, angle=90.0, rel_distance=0.18):
    """Same as Photoshop Filter > Blur > Motion Blur on the whole shape: symmetric box blur along `angle`.
    The art lead used Angle 0, Distance 33 px on a shape ~180 px long -> distance ~18% of the shape's size."""
    bbox = mask.getbbox()
    size = max(bbox[2] - bbox[0], bbox[3] - bbox[1]) if bbox else mask.size[0]
    dist = rel_distance * size
    return mt.motion_blur(mask, angle, dist / 2, back=1.0)


def edge_mix(mask, sign, blur=0.05):
    """Sharp edges on the leading side (tip + the side the tip curls toward), soft edges on the base and
    the opposite side, blending smoothly along the contour."""
    n = mask.size[0]
    soft = mask.filter(ImageFilter.GaussianBlur(blur * n))
    dx, dy = sign * 0.45, 1.0
    L = math.hypot(dx, dy)
    dx, dy = dx / L, dy / L

    def w(u, v, px):
        s_ = u * dx + v * dy                                    # high = leading (sharp) side
        soft_w = 1 - mt.smoothstep(-0.55, 0.25, s_)
        return soft_w * (1 - mt.smoothstep(0.35, 0.75, v))      # the tip always stays crisp
    W = mt.field(n, w)
    return Image.composite(soft, mask, W)


def iou(a, b):
    a = a.resize((64, 64)).point(lambda q: 1 if q > 127 else 0)
    b = b.resize((64, 64)).point(lambda q: 1 if q > 127 else 0)
    pa, pb = list(a.getdata()), list(b.getdata())
    inter = sum(1 for x, y in zip(pa, pb) if x and y)
    union = sum(1 for x, y in zip(pa, pb) if x or y)
    return inter / union if union else 0.0


# six looks, all with the  ) (  pair of concave edges; they differ in depth of each concave, proportions, tip
# height, curl and bottom detail.  arc ranges in degrees (90 = 1/4 circle, 180 = 1/2 circle)
LOOKS = [
    dict(name="balanced",    aspect=1.4,  curl=-1, k=(1.15, 1.3),   ac=(100, 130), cd=(100, 130), db=(110, 150), ba=(115, 145)),
    dict(name="deep_bite",   aspect=1.2,  curl=1,  k=(1.25, 1.4), ac=(90, 110),  cd=(140, 160), db=(100, 140), ba=(110, 135)),
    dict(name="deep_back",   aspect=1.3,  curl=-1, k=(1.2, 1.35), ac=(95, 120),  cd=(95, 115),  db=(110, 150), ba=(145, 160)),
    dict(name="waisted",     aspect=1.1,  curl=1,  k=(1.1, 1.25),   ac=(90, 105),  cd=(130, 150), db=(120, 160), ba=(135, 155)),
    dict(name="even_pair",   aspect=1.3,  curl=1,  k=(1.2, 1.35), ac=(95, 120),  cd=(125, 145), db=(110, 150), ba=(125, 145)),
    dict(name="low_wide",    aspect=1.6,  curl=1,  k=(1.3, 1.45),  ac=(90, 115),  cd=(110, 145), db=(130, 170), ba=(115, 145)),
]


def diverse_candidates(n=512, max_iou=0.8):
    """Returns [(hard_mask, curl_sign)] with clearly different looks."""
    rnd = random.Random(7)
    out = []
    seed = 1
    for look in LOOKS:
        best = None
        for _ in range(12):
            seed += 1
            e, pts = element(seed, n, look, look["aspect"], look["curl"] * rnd.uniform(0.08, 0.24))
            mirrored = e.transpose(Image.FLIP_LEFT_RIGHT)
            worst = max([max(iou(e, o), iou(mirrored, o)) for o, _ in out] or [0.0])
            if best is None or worst < best[0]:
                best = (worst, e, pts)
            if worst < max_iou:
                break
        out.append((best[1], best[2]))
    return out


GRAD = [(0.0, (255, 246, 200)), (0.25, (255, 205, 80)), (0.5, (255, 120, 30)), (0.78, (190, 35, 20)), (1.0, (90, 10, 10))]


def grad(u):
    for (a, ca), (b, cb) in zip(GRAD, GRAD[1:]):
        if u <= b:
            t = (u - a) / (b - a)
            return tuple(int(ca[i] + (cb[i] - ca[i]) * t) for i in range(3))
    return GRAD[-1][1]


def particle_preview(elem, seed, n=512, count=55, additive=False):
    rnd = random.Random(seed)
    bg = (24, 22, 30)
    img = Image.new("RGB", (n, n), bg)
    parts = []
    for _ in range(count):
        u = rnd.random()                                    # normalised age
        x = rnd.gauss(0, 0.11) * (1 - 0.4 * u) + math.sin(u * 4 + rnd.random()) * 0.04 * u
        y = -0.72 + u * 1.35 + rnd.uniform(-0.05, 0.05)
        size = (0.46 - 0.32 * u ** 0.8) * rnd.uniform(0.8, 1.2)
        rot = rnd.uniform(-14, 14)
        flip = rnd.random() < 0.5
        alpha = 1.0 if u < 0.65 else max(0.0, 1 - (u - 0.65) / 0.35)
        parts.append((u, x, y, size, rot, flip, alpha))
    parts.sort(key=lambda p: -p[0])                          # old (top) first, young (bright, bottom) on top
    for u, x, y, size, rot, flip, alpha in parts:
        px = max(4, int(size * n / 2))
        m = elem.resize((px, px), Image.LANCZOS)
        if flip:
            m = m.transpose(Image.FLIP_LEFT_RIGHT)
        m = m.rotate(rot, resample=Image.BICUBIC, expand=True)
        m = m.point(lambda q, a=alpha: int(q * a))
        col = Image.new("RGB", m.size, grad(u))
        ox, oy = int((x + 1) / 2 * n - m.size[0] / 2), int((1 - y) / 2 * n - m.size[1] / 2)
        if additive:
            layer = Image.new("RGB", (n, n), (0, 0, 0))
            layer.paste(col, (ox, oy), m)
            img = ImageChops.add(img, layer)
        else:
            img.paste(col, (ox, oy), m)
    return img


def compare_f(out, ref_path):
    cands = diverse_candidates(512)
    f = cands[5][0]
    ref = Image.open(ref_path).convert("RGB")
    tiles = [ref.resize((256, int(256 * ref.size[1] / ref.size[0])), Image.LANCZOS)]
    for angle in (0.0, 90.0):
        tiles.append(ps_motion_blur(f, angle).resize((256, 256), Image.LANCZOS).convert("RGB"))
    sheet = Image.new("RGB", (264 * len(tiles), 256), (40, 40, 48))
    for i, t in enumerate(tiles):
        sheet.paste(t, (i * 264, (256 - t.size[1]) // 2))
    sheet.save(os.path.join(out, "_compare_F.png"))


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    if len(sys.argv) > 2:
        compare_f(out, sys.argv[2])
        sys.exit(0)
    cands = diverse_candidates(512)
    hard = [e for e, _ in cands]
    mixed = [ps_motion_blur(e, 0.0) for e, pts in cands]
    sheet = Image.new("RGB", (256 * 6 + 40, 256 * 2 + 8), (40, 40, 48))
    for i, (h, m) in enumerate(zip(hard, mixed)):
        h.save(os.path.join(out, f"T_Fire_Tongue_{chr(65 + i)}.png"))
        m.save(os.path.join(out, f"T_Fire_Tongue_{chr(65 + i)}_edges.png"))
        sheet.paste(h.resize((256, 256), Image.LANCZOS).convert("RGB"), (i * 264, 0))
        sheet.paste(m.resize((256, 256), Image.LANCZOS).convert("RGB"), (i * 264, 264))
    sheet.save(os.path.join(out, "_candidates.png"))
    prev = Image.new("RGB", (384 * 3 + 16, 384 * 2 + 8), (40, 40, 48))
    for i in range(3):
        prev.paste(particle_preview(hard[i], 100 + i, 384).convert("RGB"), (i * 392, 0))
        prev.paste(particle_preview(mixed[i], 100 + i, 384).convert("RGB"), (i * 392, 392))
    prev.save(os.path.join(out, "_particle_preview.png"))
    print("ok")
