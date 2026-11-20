"""Bomb ground fire, TOTK reference (video gQ_1K61VTvo 15.5-17.0 s): after the blast, a ragged line of small orange flame
tongues keeps burning on the grass, longer than the fireball. Alpha body + small light. 2.0 s.
"""
import math

import codefx as cf

RAMP = ["#5A1A12", "#C8381A", "#FF7A1F", "#FFB830", "#FFE070"]

META = dict(
    name="CFX_BombGroundFire", size=(256, 64), origin=(128, 60), duration=2.0, loop=False, fps=30, blend="alpha",
    space=dict(context="ground", plane="billboard", camera="3/4 40", width_m=6.0, anchor="world point (ground)", background="mixed"),
    options=dict(palette=None, seed=3, scale=1.0, flames=13),
)


def create(o):
    R = cf.Rng(o["seed"])
    S = o["scale"]
    ramp = cf.ramp(RAMP)
    D = META["duration"]
    fl = []
    for i in range(o["flames"]):
        fl.append(dict(x=(i / (o["flames"] - 1) - 0.5) * 190 * S + R.range(-6, 6), w=R.range(7, 12) * S, h=R.range(16, 34) * S,
                       t0=R.range(0.15, 0.55), life=R.range(1.0, 1.7), ph=R.range(0, 6.28), lean=R.range(-0.5, 0.5)))

    class St:
        t = 0.0

        def update(self, dt):
            self.t += dt

        def draw(self, cv):
            t = self.t
            for f in fl:
                tl = t - f["t0"]
                if tl <= 0 or tl >= f["life"]:
                    continue
                u = tl / f["life"]
                env = float(cf.ease.out_cubic(cf.seg(0, 0.18, u))) * (1 - float(cf.smooth(0.55, 1.0, u)))   # grows fast, dies slowly
                h = f["h"] * env * (0.85 + 0.15 * math.sin(t * 22 + f["ph"]))
                w = f["w"] * (0.6 + 0.4 * env)
                if h < 2:
                    continue
                sway = f["lean"] * 5 + math.sin(t * 14 + f["ph"]) * 3 * env
                # ragged tongue: wide at the base, bent tip, one small side lick
                V = [(-w, 0), (-w * 0.9, -h * 0.35), (-w * 0.35, -h * 0.65), (sway, -h), (w * 0.4, -h * 0.55), (w * 0.95, -h * 0.3), (w, 0)]
                cv.poly(f["x"], 0, V, ramp[1] if u < 0.75 else ramp[0])
                V2 = [(vx * 0.72, vy * 0.82) for vx, vy in V]
                cv.poly(f["x"], 0, V2, ramp[2])
                V3 = [(vx * 0.4, vy * 0.55) for vx, vy in V]
                cv.poly(f["x"], 0, V3, ramp[3] if u < 0.6 else ramp[2])
                cv.glow(f["x"], -h * 0.4, min(w * 1.7, h * 0.6), ramp[3], 0.18 * env)

    return St()
