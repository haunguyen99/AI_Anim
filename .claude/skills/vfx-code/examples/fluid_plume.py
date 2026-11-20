"""Cột khói / bụi bốc lên tại đất, một lần 1.4 s, nướng từ mô phỏng chất lỏng (fluid.Fluid).

Kỹ thuật (WebGL-Fluid-Simulation, stable-fluids + cách toon hoá của các bộ bake stylized):
  - nguồn splat Gauss có nhiệt → nổi lên; vorticity confinement → mép cuộn kiểu nấm;
  - KHÔNG xuất mật độ thô: làm mờ nhẹ (bỏ sợi vụn) → cắt ngưỡng → silhouette sắc 1 px;
  - sáng / bóng 2 tông theo pháp tuyến giả từ gradient mật độ (đèn trên-trái), bậc cứng;
  - tan bằng ngưỡng mật độ tăng dần (khói mỏng mất trước, lõi đặc giữ lâu) — không cần noise riêng.

Lưu ý dự án: hình dáng khói toon của art lead là thân + thuỳ bám sát, không cắt đáy (SKILL.md §0).
Mô phỏng hợp với cột khói / hơi nước / bụi cuộn — không thay cho khói toon hình thuỳ.
Mẫu: không gian chỉ là ví dụ.
"""
import math

import core as cf
import fluid
import fxlib as fx
import numpy as np

META = dict(name="CFX_Fluid_Plume", size=(128, 128), origin=(64, 112), duration=1.4, loop=False, fps=30,
            blend="alpha",
            space=dict(context="ground", plane="billboard", camera="3/4 40", width_m=2.0,
                       anchor="world point (ground)", background="mixed"),
            options=dict(seed=5, N=96, steps_per_s=60, thr0=0.10, thr1=1.6,
                         lit=(0.86, 0.84, 0.80), shadow=(0.50, 0.49, 0.52), rim=(1.0, 0.75, 0.45)))


def create(o):
    N = o["N"]
    F = fluid.Fluid(N, N, vort=0.6, buoy=0.1, den_diss=0.1)
    R = cf.Rng(o["seed"])
    phase = [R.range(0, 6.28) for _ in range(3)]
    D = META["duration"]
    gy0 = META["origin"][1] / META["size"][1] * N - 4   # nguồn sát mặt đất (lưới)
    F.splat(N / 2, gy0, 7, den=0.9, tmp=0.5)           # cục nổ sẵn ở t = 0 → frame đầu có hình (hero)

    class St:
        t = 0.0
        acc = 0.0
        k = 0

        def update(self, dt):
            self.t += dt
            self.acc += dt * o["steps_per_s"]
            while self.acc >= 1.0:
                self.acc -= 1.0
                if self.k < 22:                      # nguồn 22 bước đầu (~0.37 s)
                    for j in range(3):
                        F.splat(N / 2 + (j - 1) * 6, gy0, 5,
                                den=0.13, tmp=0.12, vx=0.4 * math.sin(self.k * 0.5 + phase[j]))
                F.step(1.0)
                self.k += 1

        def draw(self, cv):
            p = self.t / D
            d = fx.box_blur(fx.box_blur(F.den, 1), 1)          # bỏ sợi vụn trước khi cắt ngưỡng
            thr = o["thr0"] + (o["thr1"] - o["thr0"]) * fx.smoothstep(0.35, 1.0, p) ** 1.5
            dl = fx.box_blur(fx.box_blur(d, 3), 3)             # pháp tuyến lấy từ bản mờ hơn → mảng bóng lớn, không sọc
            gy, gx = np.gradient(dl)
            gl = np.sqrt(gx * gx + gy * gy) + 1e-6
            lit = (-gx * -0.7 + -gy * -0.7) / gl             # pháp tuyến giả = -∇d, đèn trên-trái
            S = cv.w / N                                       # đơn vị local / ô lưới

            def fn(X, Y):
                gxp = (X + cv.ox) / S - 0.5                    # toạ độ lưới
                gyp = (Y + cv.oy) / S - 0.5
                dd = fluid._bilerp(d, gxp, gyp)
                ll = fluid._bilerp(lit, gxp, gyp)
                a = fx.cov_field(thr - dd)                     # silhouette sắc theo ngưỡng
                tone = (ll + 0.25 * (dd - thr) / max(thr, 1e-3)) > 0.05
                rgb = np.where(tone[..., None], np.array(o["lit"]), np.array(o["shadow"]))
                heat = max(0.0, 1 - p / 0.3)                   # lúc đầu ửng màu lửa ở mặt bóng
                if heat > 0:
                    rgb = np.where(tone[..., None], rgb, rgb * (1 - 0.6 * heat) + np.array(o["rim"]) * 0.6 * heat)
                return rgb, a, None

            cv.shade(-cv.ox, -cv.oy, cv.w - cv.ox, cv.h - cv.oy, fn)

    return St()
