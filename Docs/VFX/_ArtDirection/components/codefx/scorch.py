"""Component 06 Scorch: burn mark / cracks on the ground after a hit (codefx, /vfx-maker mode C). Alpha body + heat light.

Space (component standard, no question needed): ground only, lies flat (Billboard + Render Alignment Local),
camera 3/4 40 deg (the mark reads squashed ~0.64), ~2.6 m, under every other layer (sorting -2).
Drawn TOP-DOWN on the canvas (the flat quad), so no perspective in the texture.

v2 (art lead 2026-11-02: "shape hơi đơn giản quá") - layered detail, still toon (2-3 hard tones):
  burn   - soft outer soot halo; ragged rim (2 noise octaves) with mixed spikes + a few long thin rays; 3 tone rings;
           crater core with a lit lip (top-left) and a shadow lip; splatter droplets (radial teardrops) and ash specks
  cracks - main cracks with a pale lip under a dark core (depth); secondary branches; short cross cracks linking
           neighbours (a web ring around the crater); rubble chunks with 2 tones in the centre
  both   - lighter burn + cracks
Timing: pops in 0 -> 0.08 s, heat cools by ~0.7 s (hard steps white -> yellow -> orange -> red -> dark, pixelfx
drawCracks), the mark holds, then fades + erodes rim-first (small bits first) to empty at the end.
"""
import math

import numpy as np

import codefx as cf

META = dict(
    name="CFX_Scorch", size=(128, 128), origin=(64, 64), duration=2.0, loop=False, fps=30, blend="alpha",
    space=dict(context="ground", plane="ground", camera="3/4 40", width_m=2.6, anchor="world point (ground)", background="mixed"),
    options=dict(palette=None, seed=4, style="burn", cracks=9, scale=1.0),
)

SOOT = [cf.hexc("#100b09"), cf.hexc("#24190f"), cf.hexc("#3c2b20"), cf.hexc("#5a4433")]   # darkest -> lip highlight
LIGHT = np.array([-0.6, -0.8])                                                              # top-left (flat quad)


def _jag(a, length, n, rough, seed, x0=0.0, y0=0.0):
    """Mostly straight crack polyline with small kinks along angle a."""
    pts = [(x0, y0)]
    for i in range(1, n + 1):
        u = i / n
        off = (cf.hash01(seed, i, 5) - 0.5) * rough * length * (0.4 + u)
        d = length * u
        pts.append((x0 + math.cos(a) * d - math.sin(a) * off, y0 + math.sin(a) * d + math.cos(a) * off))
    return pts


def create(o):
    R = cf.Rng(o["seed"])
    S = o["scale"]
    fire = cf.ramp(o["palette"])
    style = o["style"]
    sd = R.int(1, 9999)

    # ---- burn layout
    spikes = [(R.range(0, cf.TAU), R.range(0.12, 0.35), R.range(0.08, 0.2)) for _ in range(R.int(7, 10))]
    ray0 = R.range(0, cf.TAU)                              # long thin rays, spread around (never bunched like scratches)
    spikes += [(ray0 + cf.TAU * j / 3 + R.range(-0.4, 0.4), R.range(0.45, 0.65), R.range(0.035, 0.06)) for j in range(3)]
    drops = []
    for _ in range(R.int(12, 16)):
        a = R.range(0, cf.TAU)
        drops.append((a, R.range(1.0, 1.55), R.range(1.0, 3.2) * S, R.range(1.2, 2.6), R.range(0.0, 1.0)))
    ash = [(R.range(0, cf.TAU), R.range(0.2, 1.45), R.range(0.45, 1.1) * S, R.range(0, 1)) for _ in range(28)]

    # ---- cracks layout
    cracks, ends = [], []
    n = o["cracks"]
    for i in range(n):
        a = cf.TAU * i / n + R.range(-0.25, 0.25)
        L = R.range(26, 42) * S
        main = _jag(a, L, 5, 0.12, sd + i)
        brs = []
        for j in range(R.int(0, 2)):                      # 0-2 branches per crack, leaving at 40-80 %
            k = R.int(2, 4)
            bx, by = main[k]
            brs.append((_jag(a + R.sign() * R.range(0.35, 0.8), L * R.range(0.18, 0.35), 3, 0.15, sd + 50 + i * 3 + j, bx, by), k / 5))
        cracks.append((main, brs))
        ends.append(main)
    web = []                                             # short cross cracks between neighbours (web ring)
    for i in range(n):
        if R.random() < 0.65:
            k = R.int(1, 2)
            (x0, y0), (x1, y1) = ends[i][k], ends[(i + 1) % n][k]
            mx, my = (x0 + x1) / 2 + R.range(-3, 3) * S, (y0 + y1) / 2 + R.range(-3, 3) * S
            web.append(([(x0, y0), (mx, my), (x1, y1)], k / 5 + 0.15))
    chunks = []
    for _ in range(R.int(5, 8)):
        a, d, r = R.range(0, cf.TAU), R.range(3, 13) * S, R.range(1.8, 4.2) * S
        m = R.int(5, 7)
        verts = [(math.cos(cf.TAU * j / m + R.range(-0.3, 0.3)) * r * R.range(0.7, 1.0),
                  math.sin(cf.TAU * j / m + R.range(-0.3, 0.3)) * r * R.range(0.7, 1.0)) for j in range(m)]
        chunks.append((math.cos(a) * d, math.sin(a) * d, verts, r))

    class St:
        t = 0.0

        def update(self, dt):
            self.t += dt

        def draw(self, cv):
            t, D = self.t, META["duration"]
            if t >= D:
                return
            grow = float(cf.ease.out_expo(cf.seg(0, 0.08, t)))
            if grow <= 0:
                return
            heat = float(max(0.0, 1 - t / 0.7) ** 1.4)
            fade = 1 - float(cf.smooth(0.55, 1.0, t / D))
            erode = float(cf.smooth(0.6, 1.0, t / D))
            if style in ("burn", "both"):
                self.burn(cv, grow, heat, fade, erode, 0.6 if style == "both" else 0.85)
            if style in ("cracks", "both"):
                self.cracks(cv, t, heat, fade, erode)
            if heat > 0:
                cv.glow(0, 0, 40 * S * grow, cf.blend(fire, 0.7), 0.6 * heat)

        # ------------------------------------------------------------------ burn
        def burn(self, cv, grow, heat, fade, erode, alpha):
            Rb = 33 * S * grow

            def rim(ang):
                rr = Rb * (0.74 + 0.16 * cf.noise1((ang + math.pi) / cf.TAU * 7, sd) + 0.1 * cf.noise1((ang + math.pi) / cf.TAU * 23, sd + 9))
                for a0, ln, w in spikes:
                    da = np.abs((ang - a0 + math.pi) % cf.TAU - math.pi)
                    rr = rr + Rb * ln * np.clip(1 - da / w, 0, 1) ** 1.6
                return rr

            def erosion(X, Y, q, a):
                if erode <= 0:
                    return a
                n = cf.fbm2(X / (10 * S) + sd, Y / (10 * S), sd)
                return a * cf.smooth(0, 1, (n - (erode * 1.2 - (1 - q) * 0.5)) / 0.12 + 0.5)

            # 1) soft outer soot halo
            def halo(X, Y):
                r, ang = np.hypot(X, Y), np.arctan2(Y, X)
                rr = Rb * 1.3 * (0.8 + 0.2 * cf.noise1((ang + math.pi) / cf.TAU * 5, sd + 3))
                q = r / rr
                a = np.clip(1 - q, 0, 1) ** 0.7 * 0.32 * alpha
                return np.broadcast_to(SOOT[2], X.shape + (3,)), erosion(X, Y, np.clip(q, 0, 1), a) * fade, None
            m = Rb * 1.45
            cv.shade(-m, -m, m, m, halo)

            # 2) main mark: 3 tone rings + crater lips + hot embers
            def mark(X, Y):
                r, ang = np.hypot(X, Y), np.arctan2(Y, X)
                rr = rim(ang)
                q = r / np.maximum(rr, 1e-3)
                cov = np.clip(0.5 - (r - rr) * cv.res, 0, 1)
                col = np.where((q < 0.38)[..., None], SOOT[0], np.where((q < 0.72)[..., None], SOOT[1], SOOT[2]))
                # crater lip: just outside the core, lit on the light side, darker on the far side
                lip = (q > 0.38) & (q < 0.47)
                facing = (X * LIGHT[0] + Y * LIGHT[1]) / np.maximum(r, 1e-3)
                col = np.where((lip & (facing > 0.25))[..., None], SOOT[3], col)
                col = np.where((lip & (facing < -0.25))[..., None], SOOT[0], col)
                a = cov * alpha * np.where(q < 0.72, 1.0, 0.75)
                a = erosion(X, Y, np.clip(q, 0, 1), a)
                lt = None
                if heat > 0:
                    h = heat * np.clip(1 - q / 0.62, 0, 1)
                    col = np.where((h > 0.05)[..., None], cf.at(fire, 0.25 + 0.75 * h), col)
                    lt = cf.blend(fire, 0.8) * (h * 0.6)[..., None]
                return col, a * fade, lt
            m = Rb * 1.9
            cv.shade(-m, -m, m, m, mark)

            # 3) splatter droplets (radial teardrops) + ash specks; small bits go first when eroding
            fsmall = fade * (1 - float(cf.smooth(0.0, 0.6, erode)))
            if fsmall > 0.02:
                for a0, dist, size, elong, k in drops:
                    d = dist * Rb
                    x, y = math.cos(a0) * d, math.sin(a0) * d
                    tx, ty = x - math.cos(a0) * size * elong, y - math.sin(a0) * size * elong
                    cv.streak(x, y, tx, ty, size, size * 0.35, SOOT[1] if k > 0.3 else SOOT[0], alpha * fsmall)
                for a0, dist, size, k in ash:
                    d = dist * Rb
                    cv.disc(math.cos(a0) * d, math.sin(a0) * d, size, SOOT[0] if k > 0.4 else SOOT[2], 0.7 * alpha * fsmall)

        # ------------------------------------------------------------------ cracks
        def cracks(self, cv, t, heat, fade, erode):
            g = float(cf.ease.out_cubic(cf.seg(0.0, 0.1, t)))

            def line(pts, gg, wmax, lip_a, layer):
                """layer 0 = pale lips, 1 = dark cores. All lips are drawn before any core, so joints don't bead."""
                if gg <= 0:
                    return
                n = len(pts) - 1
                shown = n * gg
                for i in range(n):
                    if i >= shown:
                        break
                    u, u1 = i / n, (i + 1) / n
                    (x0, y0), (x1, y1) = pts[i], pts[i + 1]
                    if i + 1 > shown:
                        f = shown - i
                        x1, y1 = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
                    w0 = (wmax * (1 - u) ** 1.3 + 0.35 * S)
                    w1 = (wmax * (1 - u1) ** 1.3 + 0.35 * S)
                    a = fade * (1 - erode * (0.4 + u))
                    if a <= 0.02:
                        continue
                    h = heat * (1 - u * 0.8)
                    if layer == 0:                                  # pale lip under the dark core reads as depth
                        cv.streak(x0, y0, x1, y1, w0 * 1.9, w1 * 1.9, SOOT[3], min(1.0, a * lip_a))
                        continue
                    col = cf.at(fire, h) if h > 0.12 else SOOT[0]
                    cv.streak(x0, y0, x1, y1, w0, w1, col, min(1.0, a))
                    if h > 0.12:
                        cv.glow_line(x0, y0, x1, y1, w0 * 3, cf.blend(fire, 0.75), 0.35 * h)

            for layer in (0, 1):
                for main, brs in cracks:
                    line(main, g, 1.7 * S, 0.55, layer)
                    for pts, bk in brs:
                        line(pts, float(cf.clamp((g - bk) / max(1e-3, 1 - bk))), 1.0 * S, 0.45, layer)
                for pts, wk in web:
                    line(pts, float(cf.clamp((g - wk) / max(1e-3, 1 - wk))), 0.7 * S, 0.4, layer)

            # crater pit + rubble chunks (2 tones: lit top-left face, dark body)
            cv.disc(0, 0, 6 * S * g, SOOT[0], 0.9 * fade)
            fch = fade * (1 - float(cf.smooth(0.0, 0.7, erode)))
            if fch > 0.02 and g > 0.3:
                for x, y, verts, r in chunks:
                    cv.poly(x, y, verts, SOOT[1], fch)
                    lit = [(vx * 0.62 + LIGHT[0] * r * 0.22, vy * 0.62 + LIGHT[1] * r * 0.22) for vx, vy in verts]
                    cv.poly(x, y, lit, SOOT[3], fch)
                    if heat > 0.2:
                        cv.disc(x, y, r * 0.35, cf.at(fire, heat * 0.8), fch)

    return St()
