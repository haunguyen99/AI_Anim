"""Tia lửa văng giữa không + tàn lửa, một lần 0.55 s. Dùng particles.System (references/particles.md):
  - burst chia góc đều (pixi) → hình toả cân, không thủng một phía;
  - tia = stretched billboard đúng công thức Unity (dài = size·length_scale + |v|·speed_scale), đầu có sáng;
  - drag v/(1+k·dt) (LÖVE) + trọng lực nhẹ → bắn nhanh, trôi chậm, cong xuống;
  - tia chết → sub-emitter sinh 1 tàn lửa (three.quarks EmitSubParticleSystem on Death);
  - tàn lửa lái theo curl noise (Godot) + bay lên, màu tra ramp bậc cứng theo tuổi.
Mẫu: không gian chỉ là ví dụ.
"""
import core as cf
import fxlib as fx
import numpy as np
import particles as px

META = dict(name="CFX_Spark_Burst", size=(128, 128), origin=(64, 64), duration=0.55, loop=False, fps=30,
            blend="add",
            space=dict(context="air", plane="billboard", camera="3/4 40", width_m=1.5,
                       anchor="world point (điểm trúng)", background="dark"),
            options=dict(seed=7, n=16,
                         ramp=[(1, 1, 0.9), (1, 0.85, 0.4), (1, 0.55, 0.15), (0.85, 0.25, 0.08)]))


def create(o):
    ramp = np.array(o["ramp"])
    sparks = px.System(o["seed"], [px.drag(3.0), px.gravity(0, 260)])
    sparks.burst(o["n"], angle=(0, 360), even=True, speed=(170, 280), life=(0.16, 0.3), size=(1.6, 2.4))
    embers = px.System(o["seed"] + 1, [px.drag(4.0), px.gravity(0, -60), px.curl(scale=18, influence=0.6, seed=3)])

    def on_death(s, idx):                          # mỗi tia chết → 1 tàn lửa ở đúng chỗ, thừa hưởng 15% vận tốc
        for i in idx:
            embers.burst(1, x=s.x[i], y=s.y[i], speed=(10, 30), life=(0.1, 0.2), size=(0.9, 1.4),
                         inherit=(s.vx[i] * 0.15, s.vy[i] * 0.15))

    sparks.on_death = on_death
    size_shrink = fx.Curve([(0, 1), (0.7, 0.8), (1, 0)])

    class St:
        t = 0.0

        def update(self, dt):
            self.t += dt
            sparks.update(dt)
            embers.update(dt)

        def draw(self, cv):
            t = self.t
            # hero: lóe trắng 2 frame đầu rồi tắt nhanh (references/techniques.md §6)
            cv.glow(0, 0, 34, ramp[1], 0.9 * np.exp(-t / 0.05))
            if t < 0.07:
                cv.disc(0, 0, 9 * (1 - t / 0.07) + 2, ramp[0])
            sparks.draw(cv, mode="streak", ramp=ramp, heat_curve=lambda u: u * 0.9,
                        size_curve=size_shrink, length_scale=3.0, speed_scale=0.045, glow=(3.0, 0.35))
            embers.draw(cv, mode="disc", ramp=ramp, heat_curve=lambda u: 0.4 + u * 0.6,
                        size_curve=fx.Curve([(0, 1), (1, 0)]), glow=(2.5, 0.25))

    return St()
