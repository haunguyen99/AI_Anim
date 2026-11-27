"""core: lõi vẽ của skill vfx-code — Canvas toon (thân alpha-over + sáng cộng), xuất flipbook Unity, check.

Method adapted from pixelfx (https://github.com/patch-gg/pixelfx, MIT; analysis in
Docs/VFX/_ArtDirection/components/PIXELFX_ANALYSIS.md), re-done for smooth toon instead of pixel art:
  - every pixel comes from code: shapes are signed-distance fields with 1 px anti-aliased edges
  - two layers per frame: BODY (hard toon colour steps, alpha-over) and LIGHT (soft additive glow)
  - colour = one ramp dark -> bright, picked by a single "heat" value (hard steps for body, smooth for light)
  - typed particles with tuned forces (spark, grit, ember, smoke...), drag = fast burst, slow drift
  - timing as step keys on 30 fps frames (white hero frame, overshoot, settle), deterministic seeds
  - checks: one-shot ends empty, nothing spills out of the cell, same seed = same image, loop seam

Effect module contract (see fx/*/*.py):
  META = dict(name=..., size=(w, h), origin=(x, y), duration=s, loop=False, fps=30, blend="add"|"alpha",
              space=dict(context="air"|"ground"|"dir", plane="billboard"|"ground"|"stretch", camera="3/4 40",
                         width_m=3.0, anchor="world point"|"character"|..., background="dark"|"light"|"mixed"),
              options=dict(palette=[...] or None, seed=1, ...))
  `space` is REQUIRED (art lead 2026-11-02): settle it with the user first, ask when the brief does not say (SKILL.md §0).
  def create(o): return obj with update(dt) and draw(cv)       # simulated (one-shots)
  def draw(cv, t, o): ...                                      # pure function of t (loops)
Local space: x right, y DOWN, 1 unit = 1 px at res 1, (0, 0) = META origin (hit point / feet).
"""
import colorsys
import math

import numpy as np

TAU = math.pi * 2
GRAVITY = 950.0          # units/s^2 (a 128-unit cell ~ 3 m -> ~ 9.8 m/s^2 x 40 units/m x 2.4 "game" gravity)

# ---------------------------------------------------------------- math


def clamp(v, a=0.0, b=1.0):
    return np.minimum(np.maximum(v, a), b)


def seg(a, b, t):
    """0 before a, 1 after b, linear between."""
    return clamp((t - a) / (b - a))


def smooth(a, b, t):
    x = seg(a, b, t)
    return x * x * (3 - 2 * x)


def bump(a, b, t):
    return np.sin(math.pi * seg(a, b, t))


class ease:
    @staticmethod
    def out_expo(t):
        t = clamp(t)
        return np.where(t >= 1, 1.0, 1 - np.power(2.0, -10 * t))

    @staticmethod
    def out_cubic(t):
        t = clamp(t)
        return 1 - (1 - t) ** 3

    @staticmethod
    def out_quart(t):
        t = clamp(t)
        return 1 - (1 - t) ** 4

    @staticmethod
    def out_back(t, s=1.70158):
        t = clamp(t) - 1
        return t * t * ((s + 1) * t + s) + 1

    @staticmethod
    def in_quad(t):
        t = clamp(t)
        return t * t


def hash01(*ints):
    """Deterministic 0..1 from integers (same particle -> same number every frame)."""
    h = 2166136261
    for v in ints:
        h ^= int(v) & 0xFFFFFFFF
        h = (h * 16777619) & 0xFFFFFFFF
        h ^= h >> 13
        h = (h * 1274126177) & 0xFFFFFFFF
    h ^= h >> 16
    return h / 4294967296.0


class Rng:
    def __init__(self, seed):
        self.r = np.random.default_rng(int(seed))

    def random(self):
        return float(self.r.random())

    def range(self, a, b):
        return a + (b - a) * float(self.r.random())

    def int(self, a, b):
        return int(self.r.integers(a, b + 1))

    def sign(self):
        return 1 if self.r.random() < 0.5 else -1


def noise1(x, seed=0):
    """Smooth value noise in 0..1 (scalar or array)."""
    x = np.asarray(x, dtype=np.float64)
    i = np.floor(x).astype(np.int64)
    f = x - i
    f = f * f * (3 - 2 * f)
    h = np.vectorize(lambda k: hash01(k, seed, 77))
    a, b = h(i), h(i + 1)
    return a + (b - a) * f


def _hash2(ix, iy, seed):
    h = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + seed * 982451653) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h ^= h >> 16
    return h / 4294967296.0


def noise2(x, y, seed=0):
    """Smooth 2D value noise in 0..1 (vectorised)."""
    x, y = np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64)
    ix, iy = np.floor(x), np.floor(y)
    fx, fy = x - ix, y - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    ix, iy = ix.astype(np.int64), iy.astype(np.int64)
    a, b = _hash2(ix, iy, seed), _hash2(ix + 1, iy, seed)
    c, d = _hash2(ix, iy + 1, seed), _hash2(ix + 1, iy + 1, seed)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def fbm2(x, y, seed=0, octaves=3):
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(octaves):
        s = s + amp * noise2(x * (2 ** o), y * (2 ** o), seed + o * 17)
        tot += amp
        amp *= 0.5
    return s / tot


def loop_noise(phase, seed=0, radius=1.0, freq=1):
    """Noise that has the same value at phase 0 and 1 (seamless loops)."""
    ang = TAU * phase * freq
    return 0.5 * (noise1(np.cos(ang) * radius * 3 + 10, seed) + noise1(np.sin(ang) * radius * 3 + 20, seed + 1))


# ---------------------------------------------------------------- colour & ramps


def hexc(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def shift(c, light=1.0, hue=0.0, sat=1.0):
    hh, ll, ss = colorsys.rgb_to_hls(*np.clip(c, 0, 1))
    r = colorsys.hls_to_rgb((hh + hue) % 1, clamp(ll * light, 0, 1), clamp(ss * sat, 0, 1))
    return np.array(r)


def mix(a, b, t):
    return np.asarray(a) * (1 - t) + np.asarray(b) * t


# Standard slots (Docs/VFX/_ArtDirection/components/STANDARD.md)
CORE, MID, OUTER = "#FFF3C4", "#FF9A3C", "#C8281E"
DUST = "#CDBBA6"


def ramp_from_slots(core=CORE, mid=MID, outer=OUTER, white=True):
    """7-step ramp dark -> bright, hue-shifted: shadows lean deep/cool, highlights warm/white."""
    c, m, o = hexc(core), hexc(mid), hexc(outer)
    steps = [shift(o, 0.32, -0.03, 0.9), shift(o, 0.62, -0.015), o, m, mix(m, c, 0.5), c]
    if white:
        steps.append(np.array([1.0, 1.0, 1.0]))
    return np.array(steps)


def ramp_smoke(base=DUST):
    """Toon smoke/dust: 5 steps, cool dark underside -> warm lit top."""
    b = hexc(base)
    return np.array([shift(b, 0.35, -0.06, 0.6), shift(b, 0.58, -0.03, 0.8), shift(b, 0.8), b, shift(b, 1.12, 0.01, 0.9)])


def ramp(palette):
    """palette: None (standard fire slots) · dict of slots {"Core", "Mid", "Outer"} (Mix Lab / recipe palette)
    · list of hex colours dark -> bright (a full custom ramp)."""
    if palette is None:
        return ramp_from_slots()
    if isinstance(palette, dict):
        return ramp_from_slots(palette.get("Core", CORE), palette.get("Mid", MID), palette.get("Outer", OUTER))
    return np.array([hexc(p) for p in palette])


def at(r, t):
    """Hard step: toon picks a colour, it does not fade between two. t 0..1 (array ok) -> rgb."""
    n = len(r)
    i = np.clip(np.floor(np.asarray(t) * n), 0, n - 1).astype(int)
    return r[i]


def blend(r, t):
    """Smooth ramp lookup (light only)."""
    n = len(r)
    x = np.clip(np.asarray(t, dtype=np.float64), 0, 1) * (n - 1)
    i = np.clip(np.floor(x).astype(int), 0, n - 2)
    f = (x - i)[..., None]
    return r[i] * (1 - f) + r[i + 1] * f


# ---------------------------------------------------------------- canvas & painter


class Canvas:
    """One frame: body (premultiplied rgb + alpha) and light (additive rgb). Coordinates in local units."""

    def __init__(self, size, origin, res=2.0):
        self.w, self.h = size
        self.ox, self.oy = origin
        self.res = res
        self.W, self.H = int(round(self.w * res)), int(round(self.h * res))
        self.col = np.zeros((self.H, self.W, 3))
        self.alpha = np.zeros((self.H, self.W))
        self.light = np.zeros((self.H, self.W, 3))
        self.fade = 1.0
        self.light_k = 1.0

    # -- grid of pixel centres (local units) inside a bounding box
    def _box(self, x0, y0, x1, y1, pad=2.0):
        r = self.res
        px0 = int(math.floor((x0 - pad + self.ox) * r))
        px1 = int(math.ceil((x1 + pad + self.ox) * r))
        py0 = int(math.floor((y0 - pad + self.oy) * r))
        py1 = int(math.ceil((y1 + pad + self.oy) * r))
        px0, py0 = max(px0, 0), max(py0, 0)
        px1, py1 = min(px1, self.W), min(py1, self.H)
        if px1 <= px0 or py1 <= py0:
            return None
        xs = (np.arange(px0, px1) + 0.5) / r - self.ox
        ys = (np.arange(py0, py1) + 0.5) / r - self.oy
        X, Y = np.meshgrid(xs, ys)
        return (slice(py0, py1), slice(px0, px1)), X, Y

    def _cov(self, d):
        """Signed distance (units, <0 inside) -> coverage with a 1 px AA edge."""
        return clamp(0.5 - d * self.res)

    def _cov_field(self, f):
        """Implicit field (any scale, <0 inside) -> coverage, using its gradient for a 1 px edge."""
        gy, gx = np.gradient(f)
        g = np.sqrt(gx * gx + gy * gy) + 1e-6
        return clamp(0.5 - f / g)

    def put(self, sl, cov, rgb, a=1.0):
        a_ = np.asarray(cov * a * self.fade)
        if not np.any(a_ > 0):
            return
        rgb = np.asarray(rgb, dtype=np.float64)
        if rgb.ndim == 1:
            rgb = np.broadcast_to(rgb, a_.shape + (3,))
        self.col[sl] = rgb * a_[..., None] + self.col[sl] * (1 - a_[..., None])
        self.alpha[sl] = a_ + self.alpha[sl] * (1 - a_)

    def add(self, sl, rgb, k):
        k = np.asarray(k * self.fade * self.light_k)
        rgb = np.asarray(rgb, dtype=np.float64)
        if rgb.ndim == 1:
            rgb = np.broadcast_to(rgb, k.shape + (3,))
        self.light[sl] += rgb * k[..., None]

    # ---------------- body shapes (colour may be a function of shape coordinates)
    def disc(self, x, y, r, c, a=1.0):
        """c: rgb, or fn(u) with u = distance/r (0 centre .. 1 rim)."""
        if r <= 0:
            return
        b = self._box(x - r, y - r, x + r, y + r)
        if not b:
            return
        sl, X, Y = b
        dist = np.hypot(X - x, Y - y)
        cov = self._cov(dist - r)
        col = c(clamp(dist / r)) if callable(c) else c
        self.put(sl, cov, col, a)

    def ellipse_ring(self, x, y, r, w, c, a=1.0, sy=1.0, rot=0.0, keep=None):
        """Ring on a tilted plane (sy = squash, 1 = facing camera). c: rgb or fn(ang). keep: fn(ang)->bool mask."""
        if r <= 0 or w <= 0:
            return
        R = r + w
        b = self._box(x - R, y - R * max(sy, 0.05) - R * abs(math.sin(rot)), x + R, y + R * max(sy, 0.05) + R * abs(math.sin(rot)))
        if not b:
            return
        sl, X, Y = b
        dx, dy = X - x, Y - y
        cr, sr = math.cos(-rot), math.sin(-rot)
        u, v = dx * cr - dy * sr, (dx * sr + dy * cr) / max(sy, 1e-3)
        rho, ang = np.hypot(u, v), np.arctan2(v, u)
        f = np.abs(rho - r) - w / 2
        cov = self._cov_field(f)
        if keep is not None:
            cov = cov * keep(ang)
        col = c(ang) if callable(c) else c
        self.put(sl, cov, col, a)

    def streak(self, x0, y0, x1, y1, r0, r1, c, a=1.0):
        """Tapered capsule from head (x0, y0, radius r0) to tail (x1, y1, radius r1). c: rgb or fn(h), h 0 head .. 1 tail."""
        R = max(r0, r1)
        b = self._box(min(x0, x1) - R, min(y0, y1) - R, max(x0, x1) + R, max(y0, y1) + R)
        if not b:
            return
        sl, X, Y = b
        bx, by = x1 - x0, y1 - y0
        L2 = bx * bx + by * by + 1e-9
        h = clamp(((X - x0) * bx + (Y - y0) * by) / L2)
        rr = r0 + (r1 - r0) * h
        d = np.hypot(X - (x0 + bx * h), Y - (y0 + by * h)) - rr
        col = c(h) if callable(c) else c
        self.put(sl, self._cov(d), col, a)

    def poly(self, x, y, verts, c, a=1.0):
        """Filled polygon (verts relative to x, y). c: rgb or fn(dist_to_centre_norm)."""
        V = np.asarray(verts, dtype=np.float64) + [x, y]
        b = self._box(V[:, 0].min(), V[:, 1].min(), V[:, 0].max(), V[:, 1].max())
        if not b:
            return
        sl, X, Y = b
        d = np.full(X.shape, 1e9)
        inside = np.zeros(X.shape, bool)
        n = len(V)
        for i in range(n):
            ax, ay = V[i]
            bx, by = V[(i + 1) % n]
            ex, ey = bx - ax, by - ay
            wx, wy = X - ax, Y - ay
            t = clamp((wx * ex + wy * ey) / (ex * ex + ey * ey + 1e-12))
            d = np.minimum(d, np.hypot(wx - ex * t, wy - ey * t))
            cond = ((ay <= Y) & (by > Y)) | ((by <= Y) & (ay > Y))
            xint = ax + (Y - ay) * ex / (ey + 1e-12)
            inside ^= cond & (X < xint)
        sd = np.where(inside, -d, d)
        if callable(c):
            rmax = np.max(np.hypot(V[:, 0] - x, V[:, 1] - y))
            col = c(clamp(np.hypot(X - x, Y - y) / rmax))
        else:
            col = c
        self.put(sl, self._cov(sd), col, a)

    def star(self, x, y, lengths, inner, rot=0.0, c=(1, 1, 1), a=1.0):
        """Spiky star: one spike per entry of `lengths` (tip distances), valleys at radius `inner`."""
        n = len(lengths)
        verts = []
        for i, L in enumerate(lengths):
            ang = rot + TAU * i / n
            verts.append((math.cos(ang) * L, math.sin(ang) * L))
            ang2 = ang + math.pi / n
            verts.append((math.cos(ang2) * inner, math.sin(ang2) * inner))
        self.poly(x, y, verts, c, a)

    def arc(self, cx, cy, r, width, a0, a1, c, a=1.0, sy=1.0, rot=0.0):
        """Crescent band along an ellipse arc (slash / shock front). width: number or fn(u), u 0 at a0 .. 1 at a1.
        c: rgb or fn(u, v) with v -1 inner .. 1 outer edge."""
        R = r + (width if not callable(width) else 1) * 2 + r * 0.1
        b = self._box(cx - R - 4, cy - R - 4, cx + R + 4, cy + R + 4)
        if not b:
            return
        sl, X, Y = b
        dx, dy = X - cx, Y - cy
        cr, sr = math.cos(-rot), math.sin(-rot)
        u_, v_ = dx * cr - dy * sr, (dx * sr + dy * cr) / max(sy, 1e-3)
        rho, ang = np.hypot(u_, v_), np.arctan2(v_, u_)
        span = a1 - a0
        u = ((ang - a0) % TAU) / span
        inside_ang = u <= 1
        u = clamp(u)
        w = width(u) if callable(width) else np.full(u.shape, float(width))
        f = np.abs(rho - r) - w / 2
        f = np.where(inside_ang & (w > 0.05), f, 1e3)
        cov = self._cov_field(np.where(f > 100, 100, f))
        cov = np.where(inside_ang, cov, 0)
        col = c(u, clamp((rho - r) / np.maximum(w / 2, 1e-3), -1, 1)) if callable(c) else c
        self.put(sl, cov, col, a)

    def shade(self, x0, y0, x1, y1, fn):
        """Per-pixel 'fragment shader': fn(X, Y) -> (rgb[...,3], alpha[...], light_rgb[...,3] or None)."""
        b = self._box(x0, y0, x1, y1, pad=0)
        if not b:
            return
        sl, X, Y = b
        rgb, a, lt = fn(X, Y)
        self.put(sl, 1.0, rgb, a)
        if lt is not None:
            self.add(sl, lt, 1.0)

    # ---------------- light
    def glow(self, x, y, r, c, k):
        if r <= 0 or k <= 0:
            return
        b = self._box(x - r, y - r, x + r, y + r, pad=0)
        if not b:
            return
        sl, X, Y = b
        d = clamp(np.hypot(X - x, Y - y) / r)
        self.add(sl, c, k * (1 - d) ** 2)

    def glow_line(self, x0, y0, x1, y1, r, c, k):
        b = self._box(min(x0, x1) - r, min(y0, y1) - r, max(x0, x1) + r, max(y0, y1) + r, pad=0)
        if not b:
            return
        sl, X, Y = b
        bx, by = x1 - x0, y1 - y0
        h = clamp(((X - x0) * bx + (Y - y0) * by) / (bx * bx + by * by + 1e-9))
        d = clamp(np.hypot(X - (x0 + bx * h), Y - (y0 + by * h)) / r)
        self.add(sl, c, k * (1 - d) ** 2)

    def glow_ring(self, x, y, r, w, c, k, sy=1.0):
        R = r + w
        b = self._box(x - R, y - R * sy, x + R, y + R * sy, pad=0)
        if not b:
            return
        sl, X, Y = b
        rho = np.hypot(X - x, (Y - y) / max(sy, 1e-3))
        d = clamp(np.abs(rho - r) / w)
        self.add(sl, c, k * (1 - d) ** 2)


# ---------------------------------------------------------------- particles


KINDS = {
    # g = gravity scale, drag = 1/s, bounce = restitution on the floor (y = 0), buoy = upward accel
    "spark": dict(g=0.45, drag=2.2, bounce=0.45),
    "grit": dict(g=1.0, drag=0.6, bounce=0.35),
    "ember": dict(g=-0.03, drag=1.6, wander=40.0),
    "mote": dict(g=0.0, drag=3.0),
    "smoke": dict(g=-0.017, drag=1.6, wander=8.0),
    "twinkle": dict(g=0.0, drag=4.0),
}


class P:
    __slots__ = ("k", "x", "y", "vx", "vy", "life", "max", "size", "delay", "seed", "age", "alive", "rest", "data")


class Particles:
    """Typed particles with tuned forces (pixelfx sim.js idea). Floor at y = 0 when ground=True."""

    def __init__(self, seed=1, ground=False, scale=1.0):
        self.ps = []
        self.ground = ground
        self.scale = scale
        self.n = 0
        self.seed = seed
        self.on_death = None

    def spawn(self, kind, x, y, vx, vy, life, size=1.0, delay=0.0, data=None):
        p = P()
        p.k, p.x, p.y, p.vx, p.vy = kind, x, y, vx, vy
        p.life = p.max = life
        p.size, p.delay, p.age, p.alive, p.rest = size, delay, 0.0, True, False
        p.seed = self.n
        p.data = data or {}
        self.n += 1
        self.ps.append(p)
        return p

    def update(self, dt):
        for p in self.ps:
            if not p.alive:
                continue
            if p.delay > 0:
                p.delay -= dt
                continue
            K = KINDS[p.k]
            p.age += dt
            p.life -= dt
            if p.life <= 0:
                p.alive = False
                if self.on_death:
                    self.on_death(self, p)
                continue
            if p.rest:
                continue
            g = K.get("g", 0) * GRAVITY * self.scale
            dr = K.get("drag", 0)
            w = K.get("wander", 0)
            if w:
                p.vx += (hash01(p.seed, int(p.age * 9), 3) - 0.5) * w * 2 * dt * 9
            p.vy += g * dt
            f = math.exp(-dr * dt)
            p.vx *= f
            p.vy *= f
            p.x += p.vx * dt
            p.y += p.vy * dt
            if self.ground and p.y > 0:
                p.y = 0
                b = K.get("bounce", 0)
                if b and abs(p.vy) > 60 * self.scale:
                    p.vy = -p.vy * b
                    p.vx *= 0.7
                else:
                    p.vy = 0
                    p.vx *= 0.5
                    if p.k == "grit":
                        p.rest = True

    def live(self):
        return [p for p in self.ps if p.alive and p.delay <= 0]


# ---------------------------------------------------------------- rendering & export


def substep(obj, dt, hz=120):
    n = max(1, int(math.ceil(dt * hz)))
    for _ in range(n):
        obj.update(dt / n)


def render(mod, opts=None, times=None, res=2.0):
    """Render frames at the given times (sorted). Returns list of Canvas."""
    M = mod.META
    o = dict(M.get("options", {}))
    o.update(opts or {})
    D = M["duration"]
    frames = []
    if hasattr(mod, "create"):
        st = mod.create(o)
        t = 0.0
        for tt in times:
            if tt > t:
                substep(st, tt - t)
                t = tt
            cv = Canvas(M["size"], M["origin"], res)
            st.draw(cv)
            frames.append(cv)
    else:
        for tt in times:
            cv = Canvas(M["size"], M["origin"], res)
            mod.draw(cv, (tt % D) if M.get("loop") else min(tt, D), o)
            frames.append(cv)
    return frames


def sample_times(M, n):
    """n frames over the effect: loops = one full period, one-shots = 0 .. D (frame n-1 just before the end)."""
    D = M["duration"]
    return [D * i / n for i in range(n)]


def to_add_rgba(cv):
    """Additive material (Mobile/Particles/Additive, SrcAlpha One): body over black + light, rgb = c / a, a = max channel."""
    c = cv.col + cv.light
    c = np.clip(c, 0, 1)
    a = c.max(axis=2)
    rgb = c / np.maximum(a, 1e-6)[..., None]
    return np.dstack([rgb, a])


def to_alpha_rgba(cv):
    """Alpha-blend body (straight alpha)."""
    a = np.clip(cv.alpha, 0, 1)
    rgb = cv.col / np.maximum(a, 1e-6)[..., None]
    return np.dstack([np.clip(rgb, 0, 1), a])


def to_light_rgba(cv):
    c = np.clip(cv.light, 0, 1)
    a = c.max(axis=2)
    return np.dstack([c / np.maximum(a, 1e-6)[..., None], a])


def composite(cv, bg=(0.08, 0.085, 0.1)):
    """Preview: body over background, light added on top."""
    out = np.asarray(bg) * (1 - cv.alpha[..., None]) + cv.col
    return np.clip(out + cv.light, 0, 1)


def sheet(images, cols):
    h, w = images[0].shape[:2]
    rows = int(math.ceil(len(images) / cols))
    ch = images[0].shape[2] if images[0].ndim == 3 else 1
    out = np.zeros((h * rows, w * cols, ch))
    for i, im in enumerate(images):
        r, c = divmod(i, cols)
        out[r * h:(r + 1) * h, c * w:(c + 1) * w] = im.reshape(h, w, ch)
    return out


# ---------------------------------------------------------------- checks (pixelfx tools/check.mjs, adapted)


SPACE_KEYS = ("context", "plane", "camera", "width_m", "anchor", "background")
CONTEXTS = ("air", "ground", "dir")
PLANES = ("billboard", "ground", "stretch")      # never Horizontal / Vertical Billboard (art lead 2026-10-31)


def check_space(M):
    """Space must be decided before the effect is made (SKILL.md §0)."""
    issues = []
    sp = M.get("space")
    if not isinstance(sp, dict):
        return ["META thiếu 'space' (không gian hoạt động) — xác định / hỏi người dùng trước khi làm (SKILL.md §0)"]
    for k in SPACE_KEYS:
        if sp.get(k) in (None, "", "?"):
            issues.append(f"space.{k} chưa xác định — hỏi người dùng")
    if sp.get("context") and sp["context"] not in CONTEXTS:
        issues.append(f"space.context '{sp['context']}' không hợp lệ ({', '.join(CONTEXTS)})")
    if sp.get("plane") and sp["plane"] not in PLANES:
        issues.append(f"space.plane '{sp['plane']}' không hợp lệ ({', '.join(PLANES)}; không dùng Horizontal/Vertical Billboard)")
    w, h = M.get("size", (1, 1))
    ox, oy = M.get("origin", (w / 2, h / 2))
    if sp.get("context") == "ground" and sp.get("plane") == "billboard" and oy < h * 0.7:
        issues.append("context ground + billboard đứng: origin nên ở gần đáy ô (chân chạm đất)")
    if sp.get("context") == "dir" and ox > w * 0.45:
        issues.append("context dir: hướng đòn vẽ sang phải, origin nên lệch trái ô")
    if M.get("blend") == "add" and sp.get("background") == "light":
        issues.append("blend add trên nền sáng sẽ mất hình — cân nhắc alpha hoặc thêm viền tối")
    wm = sp.get("width_m")
    if isinstance(wm, (int, float)) and not (0.2 <= wm <= 12):
        issues.append(f"space.width_m = {wm} m bất thường (so với người 2 m)")
    return issues


def check(mod, opts=None, res=1.0):
    M = mod.META
    D = M["duration"]
    issues = check_space(M)
    for k in ("name", "size", "origin", "duration", "blend"):
        if k not in M:
            issues.append(f"META thiếu '{k}'")
    ts = [D * i / 24 for i in range(24)]
    a = render(mod, opts, ts, res)
    b = render(mod, opts, ts, res)
    if any(not np.allclose(x.col, y.col) or not np.allclose(x.light, y.light) for x, y in zip(a, b)):
        issues.append("không tất định: cùng seed nhưng 2 lần render khác nhau")
    edge = 0.0
    for cv in a:
        m = np.maximum(cv.alpha, cv.light.max(axis=2))
        e = max(m[:2].max(), m[-2:].max(), m[:, :2].max(), m[:, -2:].max())
        edge = max(edge, float(e))
    if edge > 0.06:
        issues.append(f"tràn mép ô: giá trị ở viền {edge:.2f} (> 0.06) — thu nhỏ effect hoặc tăng size")
    if not M.get("loop"):
        end = render(mod, opts, [D], res)[0]
        m = max(float(end.alpha.max()), float(end.light.max()))
        if m > 0.02:
            issues.append(f"đòn một lần chưa tắt hẳn ở t = duration (còn {m:.2f})")
    elif not M.get("stepped"):   # stepped = đổi hình theo nhịp (sét, chớp), không có chuyển động liên tục để so
        f0, fl = render(mod, opts, [0.0, D * (1 - 1 / 30)], res)
        f1 = render(mod, opts, [D / 30], res)[0]
        seam = np.abs(composite(f0) - composite(fl)).mean()
        step = np.abs(composite(f0) - composite(f1)).mean() + 1e-6
        if seam > 2.5 * step:
            issues.append(f"loop giật ở chỗ nối (chênh {seam / step:.1f}× bước thường)")
    return issues
