"""Impact nằm đất của tia sét: chớp trắng, vòng xung kích, tia điện nổ ra toả quanh. Glow mềm, xanh điện lõi trắng.
Ground = Billboard + Local, xoay X 90 -> vẽ vòng TRÒN."""
import math
import numpy as np
import core as cf
import fxlib as fx

META = dict(name="CFX_Lightning_Impact", size=(128, 128), origin=(64, 64), duration=0.4, loop=False, fps=30,
            blend="add",
            space=dict(context="ground", plane="ground", camera="3/4 40", width_m=4.0,
                       anchor="world point (ground)", background="dark"),
            options=dict(seed=5, n=9, core=(1, 1, 1), mid=(0.6, 0.88, 1.0), outer=(0.2, 0.45, 1.0)))

_r = np.random.RandomState(3)
ARMS = [(2 * math.pi * (i + _r.uniform(-0.3, 0.3)) / 9, _r.uniform(40, 58), _r.uniform(0, 0.03)) for i in range(9)]


def draw(cv, t, o):
    t = t * 1.5
    core, mid, outer = o["core"], o["mid"], o["outer"]
    start = 0.035                      # chạm đất cùng lúc flare của thân sét
    T = t - start
    if T < 0:
        return
    f = math.exp(-T / 0.1) * min(T / 0.012, 1.0)
    cv.glow(0, 0, 52, outer, 0.8 * f)
    cv.glow(0, 0, 40, mid, 0.5 * f)
    cv.glow(0, 0, 24, mid, 1.0 * f)
    cv.glow(0, 0, 14, core, f)
    # vòng xung kích mềm
    R = 56 * cf.ease.out_expo(min(T / 0.25, 1.0))
    ra = (1 - fx.smoothstep(0.15, 0.45, T)) * 1.0
    if ra > 0.01 and R > 2:
        def fn(X, Y):
            r = np.hypot(X, Y)
            b = np.abs(r - R) / (5 + 7 * (T / 0.4))
            R2 = R * 0.62
            b2 = np.abs(r - R2) / (3 + 4 * (T / 0.4))
            a = np.maximum(fx.sat(1 - b) ** 1.5 * ra, fx.sat(1 - b2) ** 2 * ra * 0.6)
            return np.ones(X.shape + (3,)) * np.array(mid), a, np.array(outer) * (a * 0.4)[..., None]
        cv.shade(-60, -60, 60, 60, fn)
    # tia điện toả: mọc nhanh 0.1 s, đổi hình mỗi 3 frame, tắt dần
    shape = int(T * 30 / 3)
    for i, (ang, L, d) in enumerate(ARMS):
        g = T - d
        if g < 0:
            continue
        grow = cf.ease.out_expo(min(g / 0.1, 1.0))
        fade = 1 - fx.smoothstep(0.2, 0.5, g)
        k = fade * (1.0 if (int(T * 30) % 3 == 0) else 0.75)
        if k < 0.02:
            continue
        ex, ey = math.cos(ang) * L * grow, math.sin(ang) * L * grow
        segs = fx.bolt(0, 0, ex, ey, seed=o["seed"] * 977 + i * 13 + shape, depth=5, offset=0.2, branch_p=0.35)
        for x0, y0, x1, y1, lv in segs:
            cv.glow_line(x0, y0, x1, y1, 5 if lv == 0 else 3, outer, (0.35 if lv == 0 else 0.18) * k)
        for x0, y0, x1, y1, lv in segs:
            w = (1.3 if lv == 0 else 0.7 / lv)
            cv.streak(x0, y0, x1, y1, w, w, mid, k)
        for x0, y0, x1, y1, lv in segs:
            if lv == 0:
                cv.streak(x0, y0, x1, y1, 0.5, 0.5, core, k)
        cv.glow(ex, ey, 4, mid, 0.4 * k)
