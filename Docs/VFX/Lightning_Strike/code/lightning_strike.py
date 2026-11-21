"""Tia sét đánh xuống đất (đứng, billboard): thân sét rơi xuống -> chớp flare ở chân -> tia tắt, tàn lửa bắn ra.
Glow mềm, xanh điện lõi trắng. Chân tia = origin."""
import math
import numpy as np
import core as cf
import fxlib as fx

H = 185
META = dict(name="CFX_Lightning_Strike", size=(160, 256), origin=(80, 214), duration=0.4, loop=False, fps=30,
            blend="add",
            space=dict(context="ground", plane="billboard", camera="3/4 40", width_m=4.0,
                       anchor="world point (ground) - chan tia set", background="dark"),
            options=dict(seed=7, core=(1, 1, 1), mid=(0.6, 0.88, 1.0), outer=(0.2, 0.45, 1.0)))

_rng = np.random.RandomState(11)
SP = [(_rng.uniform(-2.9, -0.25), _rng.uniform(110, 210), _rng.uniform(0.25, 0.42), _rng.uniform(0, 0.03)) for _ in range(16)]
SP = [(a if i % 2 else -math.pi - a, v, l, d) for i, (a, v, l, d) in enumerate(SP)]


def draw(cv, t, o):
    t = t * 1.5                      # co thời gian: 0.6 s -> 0.4 s, nhanh hơn
    core, mid, outer = o["core"], o["mid"], o["outer"]
    # --- thân sét: rơi 0..0.07, giữ + chớp lại, tắt nhanh 0.2..0.36
    prog = cf.ease.out_expo(min(t / 0.04, 1.0))
    head = -H + H * prog
    fade = 1.0 - fx.smoothstep(0.17, 0.36, t)
    flick = 1.0 if t < 0.1 else (0.75 + 0.25 * (math.sin(t * 150) > 0)) if t < 0.2 else 1.0
    k = fade * flick
    if k > 0.01:
        segs = fx.bolt(0, -H, 0, 0, seed=o["seed"] * 31 + (1 if t > 0.14 else 0), depth=6, offset=0.14, branch_p=0.5)
        vis = [s for s in segs if min(s[1], s[3]) <= head]
        for x0, y0, x1, y1, lv in vis:
            cv.glow_line(x0, y0, x1, y1, 9 if lv == 0 else 4, outer, (0.4 if lv == 0 else 0.2) * k)
        for x0, y0, x1, y1, lv in vis:
            w = (2.0 if lv == 0 else 1.0 / lv) * (0.5 + 0.5 * k)
            cv.streak(x0, y0, x1, y1, w, w, mid, k)
        for x0, y0, x1, y1, lv in vis:
            if lv == 0:
                cv.streak(x0, y0, x1, y1, 0.8, 0.8, core, k)
        if prog < 1:
            cv.glow(0, head, 10, mid, 0.7)
    # --- flare ở chân: bùng ngay khi chạm (t~0.06), tắt chậm
    if t >= 0.035:
        ft = t - 0.035
        f = math.exp(-ft / 0.09) * min(ft / 0.015, 1.0)
        cv.glow(0, 0, 34 + 22 * cf.ease.out_expo(min(ft / 0.1, 1)), outer, 0.7 * f)
        cv.glow(0, 0, 20 + 8 * f, mid, 0.9 * f)
        cv.glow(0, 0, 9, core, 1.0 * f)
        # vệt flare ngang (anamorphic) + sao 4 cánh mảnh
        L = 62 * cf.ease.out_expo(min(ft / 0.08, 1)) * (0.4 + 0.6 * f)
        cv.streak(-L, 0, L, 0, 0.3, 0.3, core, 0.5 * f)
        cv.glow_line(-L, 0, L, 0, 4, mid, 0.18 * f)
        Lv = 36 * f
        cv.streak(0, -Lv, 0, Lv * 0.2, 0.4, 0.4, core, 0.7 * f)
    # --- tàn lửa bắn ra từ chân
    for a, v, life, d in SP:
        age = t - 0.045 - d
        if age < 0 or age > life:
            continue
        kd = 4.0
        def pos(s):
            r = v * (1 - math.exp(-kd * s)) / kd
            return r * math.cos(a), r * math.sin(a) + 190 * s * s
        x1, y1 = pos(age); x0, y0 = pos(max(age - 0.04, 0))
        a_ = (1 - age / life) ** 1.3
        cv.streak(x0, y0, x1, y1, 0.3, 1.1, mid, a_)
        cv.glow(x1, y1, 3, outer, 0.3 * a_)
