#!/usr/bin/env python3
"""Procedural VFX textures for vfx-maker (needs only Pillow).

Tuned against measured library textures (see references/texture-quality.md):
shapes fill ~85-92% of the cell (4-8% margin), glows follow a Gaussian falloff, rings have a
sharp outer edge and a soft inner falloff, crisp shapes are a single anti-aliased tone, and
cartoon smoke is bright with a light lower-right shadow band plus fold marks.
Output: square, white/grayscale on pure black.

  python make_texture.py <preset> -o OUT.png [options]
  python make_texture.py list                      # presets and defaults

Examples
  python make_texture.py glow    -o T_Glow_Soft.png
  python make_texture.py comet   -o T_Spark_Comet.png --style anime
  python make_texture.py ring    -o T_Ring_Shockwave.png
  python make_texture.py star    -o T_Star_Sparkle.png
  python make_texture.py smoke   -o T_Smoke_Puff_2x2.png --grid 2x2
  python make_texture.py fire    -o T_Fire_Blob_3x3.png --grid 3x3 --anim
  python make_texture.py dissolve -o T_Noise_Dissolve.png --size 256
"""
import argparse
import math
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

SS = 4  # supersampling factor for drawn (polygon/ellipse) shapes

PRESETS = {
    # name: (description, tileable, defaults)
    "glow":     ("Gaussian glow, no hard core (additive light, halo)", False, dict(radius=0.9, sigma=0.3)),
    "dot":      ("flat disc with soft edge (glow dot, bokeh)", False, dict(radius=0.85, softness=0.2)),
    "ring":     ("shockwave ring: sharp outer edge, soft inner falloff", False, dict(radius=0.84, width=0.015, inner=0.2)),
    "flare":    ("symmetric anamorphic flare: hot core, thin long tails", False, dict(radius=0.92, thickness=0.12, halo=0.6)),
    "comet":    ("spark/comet: round head (left = flight direction) + tapered tail (right), for stretched billboard", False, dict(radius=0.92, thickness=0.22)),
    "star":     ("solid N-point sparkle with concave sides and sharp tips (anime twinkle)", False, dict(radius=0.9, points=4, pinch=0.5, halo=0.0)),
    "glint":    ("thin cross / N-ray glint with glow", False, dict(radius=0.92, points=4, thickness=0.05, halo=0.7)),
    "smoke":    ("cartoon smoke puff: lobes, light lower-right shadow, fold marks", False, dict(radius=0.9, lobes=6, shadow=0.78)),
    "fire":     ("anime flame: wide base + round core, 2-4 S/C tongues leaning apart, detached chunk; single tone", False,
                 dict(radius=0.9, lobes=3, style="anime")),
    "fireblob": ("anime fire blob: bean/C shape with deep bite and curl (library cfxr style)", False, dict(radius=0.9, lobes=3, style="anime")),
    "impact":   ("hit spark: 5-8 uneven spikes in a big/medium/small rhythm, round core, flying chips", False,
                 dict(radius=0.92, spikes=7, halo=0.0, style="anime")),
    "slash":    ("crescent slash: thickest near the head, long tail taper, hard outer edge, torn inner edge, streaks, chips", False,
                 dict(radius=0.9, thickness=0.38, sweep=230.0, style="anime")),
    "lightning": ("electric arc: jagged main stroke + thin secondary stroke, thick/thin, branches; horizontal (--vertical)", False,
                  dict(radius=0.92, thickness=0.022, jag=0.3, branches=2, halo=0.5)),
    "fire_element": ("MODE 1 fire element (art lead approved): one tongue for particle randomization; two concave edges "
                     "back to back ) (, arcs of 1/4..1/2 circle, sharp curled tip, Photoshop-style motion blur", False,
                     dict(radius=0.88)),
    "ember":    ("irregular ember chunk, crisp, optional halo", False, dict(radius=0.55, halo=0.45, style="anime")),
    "trail":    ("horizontal trail strip, bright head left -> fade right (fills width)", True, dict(thickness=0.45, falloff=1.4)),
    "gradient": ("linear ramp left white -> right black (fills image)", True, dict(falloff=1.0)),
    "noise":    ("tileable soft fBm noise", True, dict(scale=4.0, octaves=5)),
    "dissolve": ("tileable noise, equalised so a 0..1 threshold sweeps evenly", True, dict(scale=5.0, octaves=6)),
}

BASE_DEFAULTS = dict(look=None, blur_angle=0.0, blur_distance=0.18, sharp=False, spikes=7, sweep=230.0, jag=0.35, branches=2, vertical=False, size=512, radius=0.9, softness=0.2, falloff=1.5, width=0.03, inner=0.22, thickness=0.1, sigma=0.3,
                     halo=0.0, points=4, pinch=0.55, lobes=5, shadow=0.78, scale=4.0, octaves=5, contrast=1.0, seed=1,
                     style="soft", steps=3, grid=None, anim=False)


# ----------------------------------------------------------------------------- helpers

def clamp01(x):
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def smoothstep(e0, e1, x):
    if e1 <= e0:
        return 1.0 if x >= e1 else 0.0
    t = clamp01((x - e0) / (e1 - e0))
    return t * t * (3.0 - 2.0 * t)


def field(n, f):
    """Analytic per-pixel image at final resolution; f(u, v, px) with u, v in [-1, 1] (v up), px = pixel size."""
    px = 2.0 / n
    data = bytes(int(clamp01(f((x + 0.5) * px - 1, 1 - (y + 0.5) * px, px)) * 255 + 0.5) for y in range(n) for x in range(n))
    return Image.frombytes("L", (n, n), data)


class Canvas:
    """Supersampled canvas for drawn shapes, normalised coords u, v in [-1, 1], v up."""

    def __init__(self, n):
        self.n, self.N = n, n * SS

    def new(self):
        return Image.new("L", (self.N, self.N), 0)

    def px(self, u, v):
        return ((u + 1) * 0.5 * self.N, (1 - v) * 0.5 * self.N)

    def r(self, r):
        return r * 0.5 * self.N

    def ellipse(self, img, cx, cy, rx, ry, fill=255):
        x, y = self.px(cx, cy)
        ImageDraw.Draw(img).ellipse([x - self.r(rx), y - self.r(ry), x + self.r(rx), y + self.r(ry)], fill=fill)
        return img

    def rot_ellipse(self, img, cx, cy, rx, ry, ang, fill=255, seg=40):
        ca, sa = math.cos(ang), math.sin(ang)
        pts = []
        for k in range(seg):
            q = k * 2 * math.pi / seg
            ex, ey = rx * math.cos(q), ry * math.sin(q)
            pts.append((cx + ex * ca - ey * sa, cy + ex * sa + ey * ca))
        return self.polygon(img, pts, fill)

    def stroke(self, img, pts, widths, fill=255):
        """Polyline with per-vertex width (round joints), widths in normalised units."""
        d = ImageDraw.Draw(img)
        for i in range(len(pts) - 1):
            (u0, v0), (u1, v1) = pts[i], pts[i + 1]
            w = (widths[i] + widths[i + 1]) / 2
            d.line([self.px(u0, v0), self.px(u1, v1)], fill=fill, width=max(1, int(self.r(w) * 2)))
        for (u, v), w in zip(pts, widths):
            x, y = self.px(u, v)
            rr = self.r(w)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=fill)
        return img

    def polygon(self, img, pts, fill=255):
        ImageDraw.Draw(img).polygon([self.px(u, v) for u, v in pts], fill=fill)
        return img

    def blur(self, img, r):
        return img.filter(ImageFilter.GaussianBlur(self.r(r))) if r > 0 else img

    def down(self, img):
        return img.resize((self.n, self.n), Image.LANCZOS)


def scale(img, k):
    return img.point(lambda p: min(255, int(p * k + 0.5)))


def add(*imgs):
    out = imgs[0]
    for im in imgs[1:]:
        out = ImageChops.add(out, im)
    return out


def sub(a, b):
    return ImageChops.multiply(a, ImageOps.invert(b))


def normalize(img):
    hi = img.getextrema()[1]
    return img if hi == 0 else img.point(lambda p: int(p * 255 / hi + 0.5))


def anim_scale(a, t, start):
    """Ease-out growth from `start` to 1 over the flipbook."""
    return start + (1 - start) * (1 - (1 - t) ** 2) if a.anim else 1.0


# ----------------------------------------------------------------------------- analytic presets (final resolution)

def p_glow(n, a, rnd, t):
    R = a.radius * anim_scale(a, t, 0.5)
    s = a.sigma * R / 0.9

    def f(u, v, px):
        r = math.hypot(u, v)
        return math.exp(-0.5 * (r / s) ** 2) * (1 - smoothstep(R * 0.85, R, r))
    return field(n, f)


def p_dot(n, a, rnd, t):
    R = a.radius * anim_scale(a, t, 0.5)
    e = max(R * a.softness, 0)

    def f(u, v, px):
        return 1 - smoothstep(R - e - px, R + px, math.hypot(u, v))
    return field(n, f)


def p_ring(n, a, rnd, t):
    R = a.radius * anim_scale(a, t, 0.3)
    w, iw = a.width, a.inner * (1 - 0.5 * t if a.anim else 1)

    def f(u, v, px):
        d = math.hypot(u, v) - R
        if d > 0:                                   # sharp outer edge
            return 1 - smoothstep(0, px * 1.5, d)
        if d > -w:                                  # bright rim line
            return 0.9
        return (1 - smoothstep(0, iw, -d - w)) ** 1.8 * 0.6    # soft inner falloff toward the centre
    return field(n, f)


def p_star(n, a, rnd, t):
    R = a.radius * anim_scale(a, t, 0.4)
    m, e = a.points, a.pinch

    def rmax(th):  # superformula: concave sides, sharp tips for e < 1
        k = m * th / 4
        return R * (abs(math.cos(k)) ** e + abs(math.sin(k)) ** e) ** (-1 / e)

    peak = max(rmax(0), rmax(math.pi / m))
    norm = R / peak  # make the tips reach exactly R
    rot = math.pi / 2 - (0 if rmax(0) >= rmax(math.pi / m) else math.pi / m)  # put one tip straight up

    def f(u, v, px):
        r = math.hypot(u, v)
        if r < 1e-9:
            return 1.0
        lim = rmax(math.atan2(v, u) - rot) * norm
        body = 1 - smoothstep(lim - px * 1.2, lim + px * 0.8, r)
        if a.halo > 0:
            body = max(body, a.halo * 0.6 * math.exp(-0.5 * (r / (0.28 * R)) ** 2))
        return body
    return field(n, f)


def p_comet(n, a, rnd, t):
    L = a.radius
    T = a.thickness * 0.5
    hx = L - T * (1.0 if a.style == "anime" else 2.6)  # head centre (right); room for the glow in soft style

    def f(u, v, px):
        if u >= hx:   # round head
            return 1 - smoothstep(T - px, T + px, math.hypot(u - hx, v))
        k = (u + L) / (hx + L)               # 0 at tail tip, 1 at head
        if k <= 0:
            return 0.0
        half = T * k ** 0.6
        body = 1 - smoothstep(half - px, half + px * 1.5, abs(v))
        return body * (0.25 + 0.75 * k ** 1.5)   # tail dims toward its tip
    img = field(n, f)
    if a.style != "anime":                   # soft glow around the head for the soft style
        c = Canvas(n)
        glow = c.down(scale(c.blur(c.ellipse(c.new(), hx, 0, T * 1.3, T * 1.1), T * 0.7), 0.5))
        img = ImageChops.lighter(img, glow)
    # Unity Stretched Billboard: flight direction = LEFT edge of the texture (verified 2026-10-31), so the head goes left
    return ImageOps.mirror(img)


# ----------------------------------------------------------------------------- drawn presets (supersampled)

def glow_layer(c, cx, cy, rx, ry, blur, weight):
    return scale(c.blur(c.ellipse(c.new(), cx, cy, rx, ry), blur), weight)


def p_flare(n, a, rnd, t):
    c = Canvas(n)
    L, T = a.radius, a.thickness
    img = add(glow_layer(c, 0, 0, L * 0.38, T * 0.55, T * 0.18, 1.0),
              glow_layer(c, 0, 0, L * 0.94, T * 0.16, T * 0.08, 0.9),
              glow_layer(c, 0, 0, L * 0.55, T * 1.0, T * 0.6, a.halo * 0.6))
    return c.down(normalize(img))


def p_glint(n, a, rnd, t):
    c = Canvas(n)
    R, T = a.radius, a.thickness
    lines = a.points // 2 if a.points % 2 == 0 else a.points
    ray = add(glow_layer(c, 0, 0, R * 0.97, T * 0.18, T * 0.1, 1.0),
              glow_layer(c, 0, 0, R * 0.6, T * 0.8, T * 0.6, a.halo * 0.45))
    img = c.new()
    for k in range(lines):
        img = ImageChops.lighter(img, ray.rotate(k * 180.0 / lines, resample=Image.BICUBIC))
    img = add(img, glow_layer(c, 0, 0, R * 0.1, R * 0.1, R * 0.08, 0.9), glow_layer(c, 0, 0, R * 0.3, R * 0.3, R * 0.2, a.halo * 0.35))
    return c.down(normalize(img))


def lobes(rnd, R, count, spread=0.42, rmin=0.32, rmax=0.48):
    """Cluster of circles that fits inside radius R."""
    out = []
    for i in range(count):
        ang = 2 * math.pi * i / count + rnd.uniform(-0.4, 0.4)
        rr = R * rnd.uniform(rmin, rmax)
        d = min(R * spread * rnd.uniform(0.6, 1.0), R - rr)
        out.append((math.cos(ang) * d, math.sin(ang) * d, rr))
    out.append((0, 0, R * rmax))
    return out


def p_smoke(n, a, rnd, t):
    """Cartoon smoke: an asymmetric overall outline split into lobes in a big/medium/small rhythm
    (no two neighbours alike), drawn back to front; each lobe carries a lower-right shadow crescent, so
    overlaps read as volumes rolling over each other. Never a round puff."""
    c = Canvas(n)
    R = a.radius * anim_scale(a, t, 0.65)
    k = max(5, a.lobes + 1)
    ax, ay = R * rnd.uniform(0.5, 0.62), R * rnd.uniform(0.36, 0.48)    # elongated base outline
    rot = rnd.uniform(-0.6, 0.6)
    sizes = rhythm_sizes(rnd, k, big=0.5, mid=(0.3, 0.36), small=(0.18, 0.24))
    lobes_ = []
    for i, (cls, rr) in enumerate(sizes):
        ang = math.tau * i / k + rnd.uniform(-0.25, 0.25)
        ex, ey = math.cos(ang) * ax, math.sin(ang) * ay
        x, y = ex * math.cos(rot) - ey * math.sin(rot), ex * math.sin(rot) + ey * math.cos(rot)
        r = R * rr
        scale_fit = min(1.0, (R * 0.97 - r) / (math.hypot(x, y) or 1e-9))
        lobes_.append((x * scale_fit, y * scale_fit, r))
    lobes_.append((rnd.uniform(-0.1, 0.1) * R, rnd.uniform(-0.05, 0.1) * R, R * 0.42))   # big inner mass
    lobes_.sort(key=lambda l: -l[1])                                      # top (back) first, lower lobes in front
    img = Image.new("L", (c.N, c.N), 0)
    shade = int(255 * a.shadow)
    for x, y, r in lobes_:
        m = c.ellipse(c.new(), x, y, r, r)
        img.paste(255, mask=m)
        lit = c.ellipse(c.new(), x - r * 0.12, y + r * 0.14, r * 0.97, r * 0.97)
        img.paste(shade, mask=sub(m, lit))                                # shadow crescent, lower-right
    if a.style != "anime":
        img = c.blur(img, R * (0.025 + a.softness * 0.05))
    return c.down(img)


def p_fireblob(n, a, rnd, t):
    c = Canvas(n)
    R = a.radius * anim_scale(a, t, 0.95)
    # body: 2-3 overlapping ellipses with random aspect -> asymmetric, elongated mass (not a round cloud)
    lb = []
    body = c.new()
    for i in range(a.lobes):
        ang = rnd.uniform(0, 2 * math.pi)
        d = R * rnd.uniform(0.0, 0.3)
        rx, ry = R * rnd.uniform(0.6, 0.8), R * rnd.uniform(0.5, 0.72)
        x, y = math.cos(ang) * d, math.sin(ang) * d
        rx, ry = min(rx, R - abs(x)), min(ry, R - abs(y))
        lb.append((x, y, (rx + ry) / 2))
        c.ellipse(body, x, y, rx, ry)
    # one deep bite (bean / C shape) + one small bite, always on the edge, never in the middle.
    # Flipbook break-up comes from the shared hole dissolve (see dissolve_mask).
    g, inward = 1.0, 1.0
    ang = rnd.uniform(0, 2 * math.pi)
    big = R * rnd.uniform(0.55, 0.68) * g
    cut = c.ellipse(c.new(), math.cos(ang) * R * 0.75 * inward, math.sin(ang) * R * 0.75 * inward, big, big)
    ang2 = ang + math.pi + rnd.uniform(-1.2, 1.2)
    small = R * rnd.uniform(0.2, 0.3) * g
    c.ellipse(cut, math.cos(ang2) * R * 0.8 * inward, math.sin(ang2) * R * 0.8 * inward, small, small)
    body = sub(body, cut)
    # optional curl: a thick hook overlapping the body edge next to the deep bite
    if rnd.random() < 0.6:
        hr = R * rnd.uniform(0.28, 0.36)
        ha = ang + rnd.choice((-1, 1)) * rnd.uniform(0.9, 1.3)
        hx, hy = math.cos(ha) * R * 0.55, math.sin(ha) * R * 0.55
        o = hr * 0.4
        hook = sub(c.ellipse(c.new(), hx, hy, hr, hr), c.ellipse(c.new(), hx + math.cos(ang) * o, hy + math.sin(ang) * o, hr * 0.85, hr * 0.85))
        body = ImageChops.lighter(body, hook)
    img = body
    if a.halo > 0:          # optional hot core as a second tone
        core = c.new()
        for x, y, r in lb:
            c.ellipse(core, x * 0.7 - R * 0.06, y * 0.7 + R * 0.05, r * 0.5, r * 0.5)
        img = ImageChops.lighter(scale(img, 1 - a.halo * 0.4), ImageChops.multiply(core, img))
    if a.style != "anime":
        img = c.blur(img, R * 0.025)
    return c.down(img)


def ribbon(pts, widths):
    """Polygon outline of a stroke with per-point half-widths (normalised units)."""
    left, right = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        L = math.hypot(dx, dy) or 1e-9
        nx, ny = -dy / L, dx / L
        left.append((x + nx * widths[i], y + ny * widths[i]))
        right.append((x - nx * widths[i], y - ny * widths[i]))
    return left + right[::-1]


def rhythm_sizes(rnd, count, big=1.0, mid=(0.5, 0.7), small=(0.22, 0.35), n_big=(1, 2)):
    """Big/medium/small sizes ordered so that no two neighbours (cyclic) share a size class."""
    nb = min(count, rnd.randint(*n_big))
    rest = count - nb
    nm = (rest + 1) // 2
    classes = ["B"] * nb + ["M"] * nm + ["S"] * (rest - nm)
    for _ in range(200):
        rnd.shuffle(classes)
        if all(classes[i] != classes[(i + 1) % count] for i in range(count)) or count < 3:
            break
    val = {"B": lambda: big * rnd.uniform(0.92, 1.0), "M": lambda: rnd.uniform(*mid), "S": lambda: rnd.uniform(*small)}
    return [(c, val[c]()) for c in classes]


def bolt(rnd, p0, p1, jag, depth, decay=0.72):
    """Midpoint displacement: perpendicular offsets halve at each level. Low depth = few sharp angular segments."""
    pts = [p0, p1]
    amp = jag
    for _ in range(depth):
        out = [pts[0]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            dx, dy = x1 - x0, y1 - y0
            L = math.hypot(dx, dy) or 1e-9
            o = rnd.uniform(-1, 1) * amp * L
            out += [(mx - dy / L * o, my + dx / L * o), (x1, y1)]
        pts = out
        amp *= decay
    return pts


def weave(rnd, pts, amp):
    """Secondary stroke hugging the main one: same path, small alternating perpendicular offsets."""
    out = []
    for i, (x, y) in enumerate(pts):
        if i == 0 or i == len(pts) - 1:
            out.append((x, y))
            continue
        (xa, ya), (xb, yb) = pts[i - 1], pts[i + 1]
        dx, dy = xb - xa, yb - ya
        L = math.hypot(dx, dy) or 1e-9
        o = amp * rnd.uniform(0.3, 1.0) * rnd.choice((-1, 1))   # crosses the main stroke at random
        out.append((x - dy / L * o, y + dx / L * o))
    return out


def clamp_pts(pts, lim):
    return [(max(-lim, min(lim, x)), max(-lim, min(lim, y))) for x, y in pts]


def thick_thin(rnd, n_pts, w0, taper=0.35):
    """Width per vertex: tapers toward the end and pulses thick/thin (the thick-thin stroke rule)."""
    phase, freq = rnd.uniform(0, 6.28), rnd.uniform(1.5, 3.5)
    return [w0 * (1 - (1 - taper) * i / max(1, n_pts - 1)) * (0.7 + 0.45 * (0.5 + 0.5 * math.sin(phase + freq * 6.28 * i / n_pts)))
            for i in range(n_pts)]


def lightning_path(rnd, p0, p1, corners, sharp_prob=0.15):
    """Trunk of straight segments at random angles: lengths 0.5-1.5x the mean, turns 20-60 deg,
    occasional sharp 90-150 deg kink; no regular zig-zag. Mapped so it runs exactly from p0 to p1."""
    heading, pts = 0.0, [(0.0, 0.0)]
    for i in range(corners + 1):
        turn = math.radians(rnd.uniform(20, 60)) * rnd.choice((-1, 1))
        if rnd.random() < sharp_prob and 0 < i < corners:
            turn = math.radians(rnd.uniform(90, 150)) * (1 if turn > 0 else -1)
        heading = max(-1.2, min(1.2, heading + turn)) if abs(heading + turn) > 1.2 else heading + turn
        heading -= heading * 0.2                       # pull back toward the main direction
        L = rnd.uniform(0.5, 1.5)
        x, y = pts[-1]
        pts.append((x + math.cos(heading) * L, y + math.sin(heading) * L))
    (sx, sy), (ex, ey) = pts[0], pts[-1]
    a0 = math.atan2(ey - sy, ex - sx)
    a1 = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    k = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / (math.hypot(ex - sx, ey - sy) or 1e-9)
    ca, sa = math.cos(a1 - a0), math.sin(a1 - a0)
    return [(p0[0] + k * ((x - sx) * ca - (y - sy) * sa), p0[1] + k * ((x - sx) * sa + (y - sy) * ca)) for x, y in pts]


def pinched(pts, w0, tip_zero=True):
    """Insert a pinch just after every corner: thick at the corner, thin right after, taper to the tip."""
    out_p, out_w = [], []
    n = len(pts) - 1
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        base = w0 * (1 - 0.75 * i / n)
        nxt = w0 * (1 - 0.75 * (i + 1) / n)
        out_p += [(x0, y0), (x0 + (x1 - x0) * 0.18, y0 + (y1 - y0) * 0.18), (x0 + (x1 - x0) * 0.6, y0 + (y1 - y0) * 0.6)]
        out_w += [base, base * 0.45, (base + nxt) * 0.45]
    out_p.append(pts[-1])
    out_w.append(0.0 if tip_zero else w0 * 0.25)
    return out_p, out_w


def p_lightning(n, a, rnd, t):
    c = Canvas(n)
    R = a.radius
    anime = a.style == "anime"
    T = a.thickness * (1.3 if anime else 1.0)
    lim = R * 0.9
    p0, p1 = (-R * 0.86, rnd.uniform(-0.12, 0.12) * R), (R * 0.86, rnd.uniform(-0.12, 0.12) * R)
    trunk = clamp_pts(lightning_path(rnd, p0, p1, rnd.randint(5, 9)), lim)
    if not anime:   # realistic: fine jitter on each straight segment
        fine = [trunk[0]]
        for q0, q1 in zip(trunk, trunk[1:]):
            fine += bolt(rnd, q0, q1, 0.12, 2, decay=0.6)[1:]
        trunk = clamp_pts(fine, lim)
    trunk_len = sum(math.hypot(x1 - x0, y1 - y0) for (x0, y0), (x1, y1) in zip(trunk, trunk[1:]))
    branches, twigs = [], []
    for _ in range(a.branches):                       # 1-3 branches: 20-45 deg off the trunk, 20-50% of its length
        i = rnd.randint(1, max(1, len(trunk) * 2 // 3))
        (x, y), (xn, yn) = trunk[i], trunk[min(i + 1, len(trunk) - 1)]
        base_ang = math.atan2(yn - y, xn - x) + math.radians(rnd.uniform(20, 45)) * rnd.choice((-1, 1))
        L = trunk_len * rnd.uniform(0.2, 0.5)
        end = (x + math.cos(base_ang) * L, y + math.sin(base_ang) * L)
        br = clamp_pts(lightning_path(rnd, (x, y), end, rnd.randint(2, 4)), lim)
        branches.append(br)
        if rnd.random() < 0.6 and len(br) > 2:          # an occasional twig on the branch
            j = rnd.randint(1, len(br) - 2)
            (bx, by), (bxn, byn) = br[j], br[j + 1]
            ta = math.atan2(byn - by, bxn - bx) + math.radians(rnd.uniform(25, 45)) * rnd.choice((-1, 1))
            tl = L * rnd.uniform(0.25, 0.45)
            twigs.append(clamp_pts(lightning_path(rnd, (bx, by), (bx + math.cos(ta) * tl, by + math.sin(ta) * tl), 2), lim))
    if a.anim:   # strike in the first quarter; then twigs die first, then branches, the trunk lasts longest
        f = smoothstep(0.0, 0.25, t)
        cutn = lambda pts: pts[: max(2, int(len(pts) * f))]
        trunk = cutn(trunk)
        branches = [cutn(b) for b in branches] if 0.15 < t < 0.6 else []
        twigs = twigs if 0.2 < t < 0.42 else []
        if t > 0.25:
            jr = random.Random(int(t * 1000) + 7)
            trunk = [(x, y + jr.uniform(-1, 1) * R * 0.012) for x, y in trunk]
    trunk_img = c.new()
    tp, tw = pinched(trunk, T)
    c.polygon(trunk_img, ribbon(tp, tw))
    thin = c.new()
    for b in branches:
        bp, bw = pinched(b, T * 0.5)
        c.polygon(thin, ribbon(bp, bw))
    for tg in twigs:
        gp, gw = pinched(tg, T * 0.28)
        c.polygon(thin, ribbon(gp, gw))
    core = ImageChops.lighter(trunk_img, thin)
    if anime:   # only the main body gets the rim; fine lines stay clean
        rim = c.blur(trunk_img, T * 0.35).point(lambda q: 110 if q > 30 else 0)
        img = ImageChops.lighter(add(rim, scale(c.blur(core, T * 1.4), a.halo * 0.7)), core)
    else:
        img = add(core, scale(c.blur(core, T * 1.8), a.halo * 2.0))
    if a.vertical:
        img = img.rotate(90, resample=Image.BICUBIC)
    return c.down(img)


def p_fire(n, a, rnd, t):
    """Anime flame: wide base hugging a round core that barely moves, 2-4 tongues with S/C spines that
    lean apart and taper to sharp tips, plus a detached chunk breaking off at 60-80% height.
    In a flipbook the tongue curves cycle S -> C -> S and the chunk rises and shrinks."""
    c = Canvas(n)
    R = a.radius
    lim = R * 0.92
    body = c.new()
    c.ellipse(body, 0, -R * 0.45, R * 0.47, R * 0.44)                     # round core ball = wide bottom (~80% of the mass)
    k = rnd.randint(2, 4)
    tops = []
    order = sorted(range(k), key=lambda i: abs(i - (k - 1) / 2))           # tallest tongue in the middle
    heights = {}
    for rank, i in enumerate(order):
        heights[i] = R * (1.32 - 0.25 * rank) * rnd.uniform(0.9, 1.05)
    phase_t = t * math.tau * 1.5 if a.anim else 0.0
    for i in range(k):
        x0 = (i - (k - 1) / 2) * R * 0.2 + rnd.uniform(-0.04, 0.04) * R   # tongues overlap at the root
        y0 = -R * 0.5
        h = heights[i]
        lean = (i - (k - 1) / 2) * 0.45 + rnd.uniform(-0.2, 0.2)        # neighbours lean apart
        amp = R * rnd.uniform(0.12, 0.2)
        ph = rnd.uniform(0, math.tau) + phase_t
        W = R * rnd.uniform(0.27, 0.34) * (1.15 if i == order[0] else 1.0)
        spine, widths = [], []
        for j in range(25):
            u = j / 24
            x = x0 + lean * u * h * 0.4 + amp * math.sin(ph + u * math.pi * 1.6) * u ** 0.6   # S/C spine
            y = y0 + u * h
            spine.append((max(-lim, min(lim, x)), min(lim, y)))
            widths.append(W * (1 - u) ** 1.1 * (1 + 0.15 * math.sin(ph * 0.7 + u * 7)))
        c.polygon(body, ribbon(spine, widths))
        tops.append(spine[-1])
    # detached chunk above one tongue tip (60-80% of the flame height); rises and shrinks in a flipbook
    tx, ty = rnd.choice(tops)
    rise = R * 0.25 * t if a.anim else 0.0
    cr = R * rnd.uniform(0.09, 0.13) * (1 - 0.8 * t if a.anim else 1.0)
    tx += R * 0.08 * rnd.choice((-1, 1))
    cy = min(lim - cr * 2.0, ty + R * 0.06 + rise)
    if cr > R * 0.01:
        c.ellipse(body, tx, cy, cr * 0.8, cr)
        c.polygon(body, [(tx - cr * 0.55, cy + cr * 0.4), (tx + cr * 0.55, cy + cr * 0.4), (tx + cr * 0.2, cy + cr * 2.0)])
    img = body
    if a.halo > 0:          # optional hot core as a second tone
        core = c.ellipse(c.new(), 0, -R * 0.42, R * 0.26, R * 0.3)
        img = ImageChops.lighter(scale(img, 1 - a.halo * 0.4), ImageChops.multiply(core, img))
    if a.style != "anime":
        img = c.blur(img, R * 0.025)
    return c.down(img)


def p_impact(n, a, rnd, t):
    """Hit spark: 5-8 straight spikes with deliberately uneven angles, lengths in a big/medium/small rhythm
    (no two neighbours alike), base ~15-25% of length, a small round core and a few flying chips."""
    c = Canvas(n)
    R = a.radius
    k = max(4, a.spikes)
    sizes = rhythm_sizes(rnd, k)
    rot = rnd.uniform(0, math.tau)
    step = math.tau / k
    img = c.new()
    core_r = R * 0.2
    for i, (cls, ln) in enumerate(sizes):
        ang = rot + i * step + rnd.uniform(-0.35, 0.35) * step
        L = R * ln
        half = math.atan2(L * rnd.uniform(0.075, 0.125), core_r)          # base width ~15-25% of the length
        tip = (math.cos(ang) * L, math.sin(ang) * L)
        c.polygon(img, [(math.cos(ang - half) * core_r, math.sin(ang - half) * core_r), tip,
                        (math.cos(ang + half) * core_r, math.sin(ang + half) * core_r), (0, 0)])
    c.ellipse(img, 0, 0, core_r, core_r)
    for _ in range(rnd.randint(3, 5)):                                    # chips: small shards flying outward
        ang = rnd.uniform(0, math.tau)
        d = R * rnd.uniform(0.55, 0.85)
        sz = R * rnd.uniform(0.03, 0.06)
        cx, cy = math.cos(ang) * d, math.sin(ang) * d
        c.polygon(img, [(cx + math.cos(ang) * sz * 2.2, cy + math.sin(ang) * sz * 2.2),
                        (cx + math.cos(ang + 2.2) * sz, cy + math.sin(ang + 2.2) * sz),
                        (cx + math.cos(ang - 2.2) * sz, cy + math.sin(ang - 2.2) * sz)])
    if a.halo > 0 or a.style != "anime":
        img = add(img, scale(c.blur(c.ellipse(c.new(), 0, 0, R * 0.45, R * 0.45), R * 0.25), max(a.halo, 0.4)))
    return c.down(img)


def p_slash(n, a, rnd, t):
    """Crescent slash: hard bright outer (blade) edge, torn soft inner edge, thickest ~35% from the head,
    long taper to the tail, short taper at the head, inner streak gaps and a few chips along the inner edge."""
    c = Canvas(n)
    R = a.radius
    rc = R * 0.86
    sweep = math.radians(a.sweep)
    a_head = math.radians(rnd.uniform(-30, 10))           # head on the right, tail sweeping counter-clockwise behind
    a_tail = a_head + sweep
    W = rc * a.thickness
    samples = 90
    outer, inner, mids = [], [], []
    for i in range(samples + 1):
        u = i / samples                                   # 0 = tail, 1 = head
        ang = a_tail + (a_head - a_tail) * u
        peak = 0.65
        w = W * ((u / peak) ** 1.6 if u < peak else ((1 - u) / (1 - peak)) ** 0.6)
        tear = 1 + (0.22 * rnd.uniform(-1, 1) if i % 3 == 0 else 0.0)   # torn inner edge
        outer.append((math.cos(ang) * rc, math.sin(ang) * rc))
        inner.append((math.cos(ang) * (rc - w * tear), math.sin(ang) * (rc - w * tear)))
        mids.append((ang, w))
    img = c.polygon(c.new(), outer + inner[::-1])
    streaks = c.new()                                     # 2-3 thin dark streak gaps running along the arc
    for k in range(rnd.randint(2, 3)):
        f = rnd.uniform(0.35, 0.75)
        u0, u1 = rnd.uniform(0.05, 0.4), rnd.uniform(0.6, 0.95)
        pts, ws = [], []
        for ang, w in mids[int(u0 * samples): int(u1 * samples)]:
            pts.append((math.cos(ang) * (rc - w * f), math.sin(ang) * (rc - w * f)))
            ws.append(max(w * 0.05, R * 0.004))
        if len(pts) > 2:
            ws = [x * math.sin(math.pi * j / (len(ws) - 1)) for j, x in enumerate(ws)]
            c.polygon(streaks, ribbon(pts, ws))
    img = sub(img, streaks)
    for _ in range(rnd.randint(3, 5)):                    # chips flaking off the inner edge, trailing behind
        u = rnd.uniform(0.15, 0.7)
        ang, w = mids[int(u * samples)]
        d = rc - w - R * rnd.uniform(0.03, 0.1)
        sz = R * rnd.uniform(0.015, 0.035)
        cx, cy = math.cos(ang) * d, math.sin(ang) * d
        c.polygon(img, [(cx + math.cos(ang + 1.57) * sz * 2, cy + math.sin(ang + 1.57) * sz * 2),
                        (cx + math.cos(ang) * sz, cy + math.sin(ang) * sz), (cx - math.cos(ang) * sz, cy - math.sin(ang) * sz)])
    if a.style != "anime":
        img = ImageChops.lighter(c.blur(img, R * 0.02), scale(c.blur(img, R * 0.06), 0.6))
    return c.down(img)


# ----------------------------------------------------------------------------- fire element (mode 1, approved)
#
# Art lead spec, approved 2026-10-21 (references/shape-language.md, "Lửa — kiểu 1"):
#   * frame = TWO CONCAVE EDGES BACK TO BACK  ) (  on opposite sides of the body: the back edge bows in, a
#     quarter-circle style bite bows in from the other side; leading edge convex, bottom convex; no other bites;
#   * every edge is a circular arc of 1/4..1/2 circle (90..180 deg), random within that range;
#   * the top tip is a sharp point that curls to one side (curve, never a straight cone);
#   * full, not thin (fills >= ~64% of its bounding box); candidates differ by concave depths, proportions,
#     tip height and curl direction - never by flipping the frame;
#   * softness = Photoshop Motion Blur over the whole shape (art lead: Angle 0, Distance 33 px on a ~180 px
#     shape -> ~18% of the shape size, symmetric).

def _sk(x, y):  # sketch pixel coords (216x256 sketch) -> normalised
    return ((x - 105.0) / 110.0, -(y - 128.0) / 110.0)


FIRE_TIPS = {"A": _sk(60, 42), "C": _sk(160, 106), "D": _sk(178, 180), "B": _sk(34, 158)}
_FIRE_CTRL = {"AC": [_sk(110, 40), _sk(152, 70)], "CD": [_sk(132, 128), _sk(138, 166)],
              "DB": [_sk(140, 228), _sk(60, 215)], "BA": [_sk(70, 120), _sk(82, 70)]}


def _bulge_side(p, q, ctrls):
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    return 1 if sum((cx - p[0]) * nx + (cy - p[1]) * ny for cx, cy in ctrls) > 0 else -1


FIRE_SIDE = {e: _bulge_side(FIRE_TIPS[e[0]], FIRE_TIPS[e[1]], _FIRE_CTRL[e]) for e in _FIRE_CTRL}

# six looks (arc ranges in degrees; k = how far the top tip is pushed away from the body)
FIRE_LOOKS = {
    "balanced":  dict(aspect=1.4, curl=-1, k=(1.15, 1.3), ac=(100, 130), cd=(100, 130), db=(110, 150), ba=(115, 145)),
    "deep_bite": dict(aspect=1.2, curl=1, k=(1.25, 1.4), ac=(90, 110), cd=(140, 160), db=(100, 140), ba=(110, 135)),
    "deep_back": dict(aspect=1.3, curl=-1, k=(1.2, 1.35), ac=(95, 120), cd=(95, 115), db=(110, 150), ba=(145, 160)),
    "waisted":   dict(aspect=1.1, curl=1, k=(1.1, 1.25), ac=(90, 105), cd=(130, 150), db=(120, 160), ba=(135, 155)),
    "even_pair": dict(aspect=1.3, curl=1, k=(1.2, 1.35), ac=(95, 120), cd=(125, 145), db=(110, 150), ba=(125, 145)),
    "low_wide":  dict(aspect=1.6, curl=1, k=(1.3, 1.45), ac=(90, 115), cd=(110, 145), db=(130, 170), ba=(115, 145)),
}


def _arc_edge(p, q, theta, side, steps=36):
    dx, dy = q[0] - p[0], q[1] - p[1]
    c = math.hypot(dx, dy) or 1e-9
    nx, ny = -dy / c * side, dx / c * side
    R = c / (2 * math.sin(theta / 2))
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    cx, cy = mx - nx * R * math.cos(theta / 2), my - ny * R * math.cos(theta / 2)
    a0 = math.atan2(p[1] - cy, p[0] - cx)
    tx, ty = mx + nx * R * (1 - math.cos(theta / 2)), my + ny * R * (1 - math.cos(theta / 2))
    sgn = min((1, -1), key=lambda g: math.hypot(cx + math.cos(a0 + g * theta / 2) * R - tx, cy + math.sin(a0 + g * theta / 2) * R - ty))
    return [(cx + math.cos(a0 + sgn * theta * i / steps) * R, cy + math.sin(a0 + sgn * theta * i / steps) * R) for i in range(steps + 1)]


def _upright(pts):
    """Rotate so the top tip (first point) points straight up from the centroid."""
    cx = sum(x for x, _ in pts) / len(pts)
    cy = sum(y for _, y in pts) / len(pts)
    rot = math.pi / 2 - math.atan2(pts[0][1] - cy, pts[0][0] - cx)
    ca, sa = math.cos(rot), math.sin(rot)
    return [((x - cx) * ca - (y - cy) * sa, (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def _curl_tip(pts, amount):
    ys = [y for _, y in pts]
    y0, y1, h = min(ys) + 0.4 * (max(ys) - min(ys)), max(ys), max(ys) - min(ys)
    return [(x + amount * h * max(0.0, (y - y0) / (y1 - y0)) ** 2.2, y) for x, y in pts]


def _self_intersects(pts):
    ccw = lambda a, b, c: (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    segs = list(zip(pts, pts[1:] + pts[:1]))
    for i in range(len(segs)):
        for j in range(i + 2, len(segs)):
            if i == 0 and j == len(segs) - 1:
                continue
            (p1, p2), (p3, p4) = segs[i], segs[j]
            if ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4):
                return True
    return False


def _tip_angle(q):
    (ax, ay), (bx, by), (cx, cy) = q[0], q[3], q[-4]
    d = abs(math.atan2(by - ay, bx - ax) - math.atan2(cy - ay, cx - ax)) % math.tau
    return math.degrees(min(d, math.tau - d))


def _fill_ratio(pts):
    area = abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2
    xs, ys = [x for x, _ in pts], [y for _, y in pts]
    return area / ((max(xs) - min(xs)) * (max(ys) - min(ys)) or 1e-9)


def fire_element_outline(rnd, look):
    """One tongue outline obeying the approved rules; retries until the tip is sharp, the outline clean and
    the body full (keeps the best try after 400 attempts)."""
    L = FIRE_LOOKS[look]
    curl = L["curl"] * rnd.uniform(0.08, 0.24)
    best = None
    for _ in range(400):
        T = {k: (x + rnd.uniform(-0.07, 0.07), y + rnd.uniform(-0.07, 0.07)) for k, (x, y) in FIRE_TIPS.items()}
        mx, my = (T["B"][0] + T["C"][0]) / 2, (T["B"][1] + T["C"][1]) / 2
        k = rnd.uniform(*L["k"])
        T["A"] = (mx + (T["A"][0] - mx) * k, my + (T["A"][1] - my) * k)
        deg = lambda r: math.radians(rnd.uniform(*r))
        th_ac = min(deg(L["ac"]), math.radians(150))
        th_ba = min(math.radians(180), max(deg(L["ba"]), th_ac + math.radians(25)))   # back bows in more -> sharp tip
        edges = [(T["A"], T["C"], FIRE_SIDE["AC"], th_ac),     # convex leading edge
                 (T["C"], T["D"], FIRE_SIDE["CD"], deg(L["cd"])),  # concave side bite  (
                 (T["D"], T["B"], FIRE_SIDE["DB"], deg(L["db"])),  # convex bottom
                 (T["B"], T["A"], FIRE_SIDE["BA"], th_ba)]     # concave back edge  )
        pts = []
        for p0, q0, sd, th in edges:
            seg = _arc_edge(p0, q0, th, sd)
            pts += seg if not pts else seg[1:]
        pts = _curl_tip([(x * L["aspect"], y) for x, y in _upright(pts)], curl)
        ok = not _self_intersects(pts[::3])
        score = max(0.0, _tip_angle(pts) - 70) * 3 + (0 if ok else 1000) + (300 if _fill_ratio(pts) < 0.6 else 0) - _fill_ratio(pts) * 20
        if best is None or score < best[0]:
            best = (score, pts)
        if ok and _tip_angle(pts) <= 70 and _fill_ratio(pts) >= 0.64:
            break
    return best[1]


def p_fire_element(n, a, rnd, t):
    look = a.look or rnd.choice(sorted(FIRE_LOOKS))
    pts = fire_element_outline(rnd, look)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    k = 2 * a.radius / max(max(xs) - min(xs), max(ys) - min(ys))      # longest side -> radius*100% of the cell
    pts = [((x - cx) * k, (y - cy) * k) for x, y in pts]
    c = Canvas(n)
    m = c.down(c.blur(c.polygon(c.new(), pts), 0.004).point(lambda q: 255 if q >= 128 else 0))
    if a.sharp:
        return m
    bbox = m.getbbox()
    size = max(bbox[2] - bbox[0], bbox[3] - bbox[1]) if bbox else n
    return motion_blur(m, a.blur_angle, a.blur_distance * size / 2, back=1.0)   # == Photoshop Motion Blur


def p_ember(n, a, rnd, t):
    c = Canvas(n)
    R = a.radius
    k = rnd.randint(5, 7)
    pts = []
    for i in range(k):
        ang = 2 * math.pi * i / k + rnd.uniform(-0.3, 0.3)
        rr = R * rnd.uniform(0.6, 1.0)
        pts.append((math.cos(ang) * rr, math.sin(ang) * rr * 0.75))
    img = c.blur(c.polygon(c.new(), pts), R * 0.03 if a.style == "anime" else R * 0.08)
    if a.halo > 0:
        img = add(img, scale(c.blur(c.ellipse(c.new(), 0, 0, R * 0.9, R * 0.9), R * 0.4), a.halo))
    return c.down(normalize(img))


def p_trail(n, a, rnd, t):
    c = Canvas(n)
    N = c.N
    col = [int(255 * (1 - x / (N - 1)) ** a.falloff) for x in range(N)]
    img = Image.new("L", (N, N))
    img.putdata([col[x] for _ in range(N) for x in range(N)])
    band = add(scale(c.blur(c.ellipse(c.new(), 0, 0, 3.0, a.thickness * 0.6), a.thickness * 0.4), 0.7),
               scale(c.blur(c.ellipse(c.new(), 0, 0, 3.0, a.thickness * 0.12), a.thickness * 0.08), 0.6))
    return c.down(ImageChops.multiply(img, band))


def p_gradient(n, a, rnd, t):
    return field(n, lambda u, v, px: ((1 - u) / 2) ** a.falloff)


def tile_fbm(n, scale_, octaves, rnd):
    """Seamless fBm: random grids upscaled bicubic with wrap-around padding."""
    acc, wsum = None, 0.0
    for o in range(octaves):
        p = max(2, int(round(scale_ * 2 ** o)))
        g = Image.new("L", (p, p))
        g.putdata([rnd.randint(0, 255) for _ in range(p * p)])
        tiled = Image.new("L", (p * 3, p * 3))
        for i in range(3):
            for j in range(3):
                tiled.paste(g, (i * p, j * p))
        big = tiled.resize((n * 3, n * 3), Image.BICUBIC).crop((n, n, 2 * n, 2 * n))
        w = 0.5 ** o
        wsum += w
        acc = big if acc is None else Image.blend(acc, big, w / wsum)
    return acc


def p_noise(n, a, rnd, t):
    return ImageOps.autocontrast(tile_fbm(n, a.scale, a.octaves, rnd), cutoff=1)


def p_dissolve(n, a, rnd, t):
    return ImageOps.equalize(tile_fbm(n, a.scale, a.octaves, rnd))


# ----------------------------------------------------------------------------- hole dissolve (flipbooks)
#
# Art rules (from the art lead):
#   * three hole sizes: large / medium / small - never two holes of the SAME size next to each other;
#   * random, not uniform: irregular ellipses at random angles, staggered start times and a few thin
#     slits, so the remaining strokes mix thick and thin parts; soft style also mixes crisp and blurred edges.

HOLE_CLASSES = (("L", 0.3, (1, 2)), ("M", 0.17, (2, 3)), ("S", 0.09, (2, 4)))   # name, radius (x R), count range
HOLE_GAP = 0.16                                                     # min clearance between same-size holes (x R)


def plan_holes(seed, R, direction, center_first=False):
    """direction = dissolve vector A in degrees (0 = right, 90 = up). The side opposite A goes first."""
    rnd = random.Random(seed * 7177 + 13)
    ax, ay = math.cos(math.radians(direction)), math.sin(math.radians(direction))
    holes = []
    for name, frac, (cmin, cmax) in HOLE_CLASSES:
        count = rnd.randint(cmin, cmax)
        placed = 0
        for _ in range(600):
            if placed >= count:
                break
            r = R * frac * rnd.uniform(0.85, 1.15)
            ang, dist = rnd.uniform(0, 2 * math.pi), R * 1.05 * math.sqrt(rnd.random())
            x, y = math.cos(ang) * dist, math.sin(ang) * dist
            ok = True
            for h in holes:
                d = math.hypot(x - h["x"], y - h["y"])
                if d < 0.8 * (r + h["r"]):                                  # no heavy overlap: holes stay readable
                    ok = False
                    break
                if h["cls"] == name and d < r + h["r"] + HOLE_GAP * R:      # same size never side by side
                    ok = False
                    break
            if center_first and name == "L" and placed == 0:   # smoke: the first big hole opens in the middle
                x, y = rnd.uniform(-0.15, 0.15) * R, rnd.uniform(-0.15, 0.15) * R
            elif not ok:
                continue
            slit = name != "L" and rnd.random() < 0.3                     # thin slits -> thin strokes
            asp = rnd.uniform(0.28, 0.42) if slit else rnd.uniform(0.65, 1.35)
            proj = ((x * ax + y * ay) / R + 1) / 2                             # 0 = side opposite A (dissolves first)
            rot = rnd.uniform(0, math.pi)
            sats = []
            for _ in range(0 if slit else rnd.randint(1, 2)):        # satellites make the hole organic, not punched
                sa = rnd.uniform(0, 2 * math.pi)
                sats.append((math.cos(sa) * rnd.uniform(0.55, 0.9), math.sin(sa) * rnd.uniform(0.55, 0.9), rnd.uniform(0.5, 0.8)))
            holes.append(dict(cls=name, x=x, y=y, r=r, asp=asp, rot=rot, slit=slit, sats=sats,
                              start=0.05 if (center_first and name == "L" and placed == 0) else
                              clamp01(0.02 + 0.5 * proj * rnd.uniform(0.6, 1.0) + rnd.uniform(-0.04, 0.1)),
                              dur=rnd.uniform(0.3, 0.55), soft=rnd.choice((0.0, 0.02, 0.035, 0.05, 0.07))))   # soft style: mostly blurred edges, a few crisp ones
            placed += 1
    return holes


def same_size_neighbours(holes, R):
    bad = 0
    for i, h in enumerate(holes):
        for k in holes[i + 1:]:
            if h["cls"] == k["cls"] and math.hypot(h["x"] - k["x"], h["y"] - k["y"]) < h["r"] + k["r"] + HOLE_GAP * R:
                bad += 1
    return bad


def dissolve_mask(n, a, holes, t):
    """255 = cut away. Holes open at staggered times, grow, and finally swallow the shape."""
    c = Canvas(n)
    if t >= 1.0:
        return Image.new("L", (n, n), 255)
    cut = c.new()
    # Every open hole grows by the same global factor, so large > medium > small holds in EVERY frame.
    # Holes pop open quickly (from 75% size) at staggered times; the growth makes neighbours meet,
    # leaving a lace of thick and thin strokes before the last frames clear everything.
    grow = 0.7 + 2.1 * t ** 1.5
    for h in holes:
        k = smoothstep(h["start"], h["start"] + 0.12, t)
        if k <= 0:
            continue
        r = h["r"] * (0.75 + 0.25 * k) * grow
        one = c.rot_ellipse(c.new(), h["x"], h["y"], r, r * h["asp"], h["rot"])
        for sx, sy, sr in h["sats"]:
            c.rot_ellipse(one, h["x"] + sx * r, h["y"] + sy * r, r * sr, r * sr * h["asp"], h["rot"] + sx)
        if a.style != "anime" and h["soft"] > 0:            # soft style: mix crisp and blurred hole edges
            one = c.blur(one, h["soft"] * a.radius)
        cut = ImageChops.lighter(cut, one)
    return c.down(cut)


def motion_blur(img, direction, length_px, back=0.35, steps=None):
    """Blur along vector A only: samples from -back*L to +L along A (biased forward, so wisps lean toward A)."""
    if length_px < 1:
        return img
    steps = steps or max(12, int(length_px * (1 + back) / 1.2))   # ~1 px per step: smooth, no banding
    dx, dy = math.cos(math.radians(direction)), -math.sin(math.radians(direction))   # image y is down
    acc = None
    for i in range(steps + 1):
        d = length_px * (-back + (1 + back) * i / steps)
        shifted = img.transform(img.size, Image.AFFINE, (1, 0, -dx * d, 0, 1, -dy * d), resample=Image.BILINEAR, fillcolor=0)
        acc = shifted if acc is None else Image.blend(acc, shifted, 1.0 / (i + 1))
    return acc


def directional_soften(img, a, t, n):
    """Dissolving frames are blurred along A, more and more as t grows (frame 0 stays crisp)."""
    if t <= 0:
        return img
    smear = motion_blur(img, a.dir, n * a.blur * t ** 0.8)
    out = Image.blend(img, smear, min(1.0, 0.35 + 0.65 * t))
    if a.thin_strokes:   # thin strokes (lightning) vanish under heavy blur: keep a fading crisp core on top
        out = ImageChops.lighter(out, scale(img, 0.85 * (1 - t) ** 0.7))
    return out


BUILDERS = {k: globals()["p_" + k] for k in PRESETS}
FLIPBOOK_PRESETS = ("smoke", "fire", "fireblob", "lightning")   # art lead: flipbooks only for smoke, fire, electricity


# ----------------------------------------------------------------------------- render

def use_dissolve(a, preset):
    if not a.anim or PRESETS[preset][1]:
        return False
    return a.dissolve != "off"   # dissolve rules apply to every texture type


def render_cell(preset, a, n, seed, t, holes=None):
    img = BUILDERS[preset](n, a, random.Random(seed), t)
    if holes is not None:
        img = sub(img, dissolve_mask(n, a, holes, t))
        img = directional_soften(img, a, t, n)
    elif a.anim:
        img = scale(img, 1 - t * t)
    if a.contrast != 1.0:
        img = img.point(lambda p: max(0, min(255, int((p - 128) * a.contrast + 128))))
    if a.style == "anime" and a.steps > 1 and preset not in ("fire", "fireblob", "fire_element", "ember", "star", "comet", "smoke", "lightning", "impact", "slash"):
        s = a.steps   # flat value steps for soft-shaded presets (crisp presets are already flat)
        img = img.point(lambda p: int(round(round(p / 255 * s) / s * 255)))
    return img


def parse_grid(g):
    if not g:
        return 1, 1
    cc, rr = g.lower().split("x")
    return int(cc), int(rr)


def main(argv):
    if len(argv) > 1 and argv[1] == "list":
        for k, (desc, tile, d) in PRESETS.items():
            print(f"{k:9s} {'[tileable] ' if tile else ''}{desc}   defaults: {d}")
        return 0
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("preset", choices=sorted(PRESETS))
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--size", type=int, help="output size in px (square), default 512")
    for k in ("radius", "softness", "falloff", "width", "inner", "thickness", "sigma", "halo", "pinch", "shadow", "scale", "contrast", "jag", "sweep"):
        p.add_argument("--" + k, type=float)
    for k in ("points", "lobes", "octaves", "seed", "steps", "branches", "spikes"):
        p.add_argument("--" + k, type=int)
    p.add_argument("--vertical", action="store_true", help="lightning: vertical bolt instead of a horizontal arc")
    p.add_argument("--look", choices=sorted(FIRE_LOOKS), help="fire_element: which approved look (default: random per seed)")
    p.add_argument("--blur-angle", dest="blur_angle", type=float, help="fire_element: Photoshop-style motion blur angle in degrees (default 0)")
    p.add_argument("--blur-distance", dest="blur_distance", type=float, help="fire_element: blur distance as a fraction of the shape size (default 0.18)")
    p.add_argument("--sharp", action="store_true", help="fire_element: no blur (hard silhouette)")
    p.add_argument("--style", choices=["soft", "anime"], help="anime = crisp edges / flat value steps")
    p.add_argument("--grid", help="CxR atlas, e.g. 2x2 variants or 4x4 flipbook")
    p.add_argument("--anim", action="store_true", help="with --grid: frames animate (grow, break up, fade) instead of random variants")
    p.add_argument("--dissolve", choices=["auto", "on", "off"], default="auto",
                   help="flipbook hole dissolve (large/medium/small holes + blur along --dir); flipbooks are smoke/fire only")
    p.add_argument("--dir", type=float, default=90.0,
                   help="dissolve direction A in degrees (0 right, 90 up, 180 left, 270 down): the side opposite A goes first, blur streaks along A")
    p.add_argument("--blur", type=float, default=0.12, help="max directional blur length as a fraction of the cell (last frames)")
    args = p.parse_args(argv[1:])

    if args.anim and args.preset not in FLIPBOOK_PRESETS:
        p.error(f"flipbooks are only made for smoke, fire and electricity; '{args.preset}' should be a single "
                "texture or a variants atlas (--grid without --anim), animated by the particle system")
    _, tileable, preset_defaults = PRESETS[args.preset]
    a = argparse.Namespace(**{**BASE_DEFAULTS, **preset_defaults,
                              **{k: v for k, v in vars(args).items() if v is not None and v is not False}})
    a.anim = args.anim
    a.thin_strokes = args.preset == "lightning"
    cols, rows = parse_grid(a.grid)
    count = cols * rows
    cell = a.size // max(cols, rows)

    holes = plan_holes(a.seed, a.radius, a.dir, center_first=args.preset == "smoke") if use_dissolve(a, args.preset) and count > 1 else None
    img = Image.new("L", (cell * cols, cell * rows), 0)
    for i in range(count):
        t = i / (count - 1) if (a.anim and count > 1) else 0.0
        seed = a.seed if a.anim else a.seed + i * 7919
        img.paste(render_cell(args.preset, a, cell, seed, t, holes), ((i % cols) * cell, (i // cols) * cell))
    img.convert("RGB").save(a.out)

    w, h = img.size
    if holes is not None:
        cnt = {k: sum(1 for x in holes if x["cls"] == k) for k in "LMS"}
        print(f"holes L/M/S = {cnt['L']}/{cnt['M']}/{cnt['S']}, slits = {sum(x['slit'] for x in holes)}, "
              f"same-size neighbours = {same_size_neighbours(holes, a.radius)}")
    msg = f"{a.out}  {w}x{h}  preset={args.preset} style={a.style}" + (f" grid={cols}x{rows}{' anim' if a.anim else ''}" if count > 1 else "")
    if not tileable and count == 1:
        bbox = img.point(lambda q: 255 if q > 6 else 0).getbbox()
        if bbox:
            l, t_, r, b = bbox
            margin = min(l, t_, w - r, h - b) / w * 100
            occ = max(r - l, b - t_) / w
            msg += f"  occupancy {occ:.2f}  min margin {margin:.1f}%"
            if margin < 2:
                msg += "  WARNING: touches edge"
            elif occ < 0.75:
                msg += "  note: small in cell (library textures fill ~0.85-0.92)"
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
