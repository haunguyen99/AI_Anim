"""Bomb fireball, TOTK reference (video gQ_1K61VTvo, 14.8-17.0 s). Alpha Body + Light. 1.6 s.

Observed: flash fills the ball, then ANGULAR FACETED lumps (lava-rock look, flat 3-tone shading, hard edges); lumps cool
yellow -> orange -> dark red -> dark brown and break up into black angular smoke; a few long thin light streaks shoot
diagonally at the peak. No purple, no round spheres, no soft gradients on the body.
"""
import math

import codefx as cf

# heat ramp, dark -> bright (flat tones, picked as shadow / mid / light)
RAMP = ["#2E1A16", "#6A2A1A", "#A82A14", "#E8561A", "#FF8F1F", "#FFC93C", "#FFF1A8"]

META = dict(
    name="CFX_BombFire", size=(256, 208), origin=(128, 196), duration=1.6, loop=False, fps=30, blend="alpha",
    space=dict(context="ground", plane="billboard", camera="3/4 40", width_m=6.0, anchor="world point (ground)", background="mixed"),
    options=dict(palette=None, seed=7, scale=1.0, lumps=11),
)


def create(o):
    R = cf.Rng(o["seed"])
    S = o["scale"]
    ramp = cf.ramp(RAMP)
    n = len(ramp)
    D = META["duration"]

    # lumps: position (ellipse), radius, shape, own delay / heat lag / break-up time
    lumps = []
    for i in range(o["lumps"]):
        big = i == 0
        a = cf.TAU * i / o["lumps"] * 1.0 + R.range(-0.25, 0.25)
        rad = 0.0 if big else R.range(0.55, 1.0)
        verts = []
        k = R.int(6, 8)
        for j in range(k):
            ang = cf.TAU * j / k + R.range(-0.28, 0.28)
            verts.append((math.cos(ang), math.sin(ang) * 0.92, R.range(0.74, 1.1)))
        lumps.append(dict(
            ax=math.cos(a) * rad * 92 * S, ay=-62 * S + math.sin(a) * rad * 58 * S,
            r=(56 if big else R.range(24, 40)) * S, verts=verts, rot=R.range(-0.5, 0.5),
            delay=0.0 if big else R.range(0.0, 0.09), lag=R.range(-0.06, 0.1), brk=R.range(1.0, 1.35), rise=R.range(14, 34)))
    rays = [(R.range(-0.5, -0.15) + (0 if i % 2 == 0 else math.pi), R.range(70, 90), R.range(0.0, 0.05)) for i in range(4)]

    def tone(u):
        """u 0 (cold) .. 1 (white hot) -> (shadow, mid, light), three flat steps of the ramp."""
        i = int(round(cf.clamp(u, 0, 1) * (n - 1)))
        return ramp[max(i - 1, 0)], ramp[i], ramp[min(i + 1, n - 1)]

    class St:
        t = 0.0

        def update(self, dt):
            self.t += dt

        def draw(self, cv):
            t = self.t
            if t >= D:
                return
            # flash: white spiky star while the ball is tiny, then the lumps take over
            if t < 0.14:
                k = 1 - t / 0.14
                L = 70 * S * (0.4 + 0.6 * float(cf.ease.out_expo(cf.seg(0, 0.08, t)))) * (0.4 + 0.6 * k)
                cv.star(0, -58 * S, [L, L * 0.55, L * 0.9, L * 0.5, L * 0.75, L * 0.6, L * 0.95, L * 0.5, L * 0.8, L * 0.55],
                        L * 0.28, rot=0.3, c=ramp[n - 1])
                cv.glow(0, -58 * S, 56 * S, ramp[n - 1], 0.9 * k)
            # lumps, big one in front (drawn last)
            for lp in sorted(lumps, key=lambda q: -q["r"]):
                tl = t - lp["delay"]
                if tl <= 0:
                    continue
                grow = float(cf.ease.out_expo(cf.seg(0, 0.16, tl))) * (1 + 0.14 * math.sin(cf.clamp(tl / 0.3, 0, 1) * math.pi))
                shrink = 1 - float(cf.smooth(lp["brk"] - 0.35, lp["brk"] + 0.2, t))                  # break up into nothing at the end
                heat = 1 - float(cf.smooth(0.12 + lp["lag"], 0.95 + lp["lag"], t))                  # cools: yellow -> dark brown
                r = lp["r"] * grow * (0.35 + 0.65 * shrink) * (1 if shrink > 0.02 else 0)
                if r < 1:
                    continue
                x = lp["ax"] * float(cf.ease.out_cubic(cf.seg(0, 0.4, tl)))
                y = lp["ay"] - lp["rise"] * S * float(cf.smooth(0.5, D, t)) * (0.4 + 0.6 * (1 - heat))
                y = min(y, -r * 0.85)                                                    # lumps sit on the ground, never under it
                sh, mid, lt = tone(heat)
                V = []
                for vx, vy, rr in lp["verts"]:
                    a = math.atan2(vy, vx) + lp["rot"]
                    V.append((math.cos(a) * math.hypot(vx, vy) * rr * r, math.sin(a) * math.hypot(vx, vy) * rr * r))
                cv.poly(x, y, V, sh)                                                     # shadow tone: whole lump
                V2 = [(vx * 0.78 - r * 0.1, vy * 0.78 - r * 0.14) for vx, vy in V]
                cv.poly(x, y, V2, mid)                                                   # body tone, shifted up-left
                V3 = [(vx * 0.4 - r * 0.22, vy * 0.4 - r * 0.3) for vx, vy in V]
                cv.poly(x, y, V3, lt, a=0.95 if heat > 0.15 else 0.0)                    # lit facet (only while warm)
                if heat > 0.25:
                    cv.glow(x, y, r * 1.5, ramp[n - 2], 0.28 * heat)
            # light streaks (thin, diagonal), only around the peak
            for ang, ln, dl in rays:
                tr = t - dl
                if 0 < tr < 0.4:
                    f = float(cf.ease.out_expo(cf.seg(0, 0.16, tr))) * (1 - float(cf.smooth(0.16, 0.4, tr)))
                    x0, y0 = math.cos(ang) * 30 * S, -58 * S + math.sin(ang) * 18 * S
                    x1, y1 = math.cos(ang) * ln * S * f * 1.15, -58 * S + math.sin(ang) * ln * S * f * 0.6
                    cv.streak(x0, y0, x1, y1, 2.2 * f, 0.3, ramp[n - 2], 0.9)
                    cv.glow_line(x0, y0, x1, y1, 7 * S, ramp[n - 3], 0.5 * f)

    return St()
