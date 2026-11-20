"""Sóng xung kích nằm đất, một lần 0.5 s. Toàn bộ là một "fragment shader" trên toạ độ cực
(cách của các shader shockwave / ring trên Shadertoy, Godot shaders):

  r, u = polar(x, y)                  u = góc 0..1 → noise theo u có chu kỳ → vòng không có đường nối
  band = |r - R(t)| / w(t)            R nở out_expo, w mỏng dần
  vỡ   = dissolve(band, noise(u, r))  ngưỡng tăng theo t → vòng đứt thành đoạn rồi tan
  màu  = ramp_hard(1 - band)          bậc cứng: mép trong trắng → giữa màu → ngoài sẫm

Mặt phẳng "ground" = Billboard + Render Alignment Local, quad xoay X 90°, nên vẽ vòng TRÒN (không ép dẹt).
Mẫu: không gian chỉ là ví dụ.
"""
import core as cf
import fxlib as fx
import numpy as np

META = dict(name="CFX_Shockwave_Ground", size=(128, 128), origin=(64, 64), duration=0.5, loop=False, fps=30,
            blend="add",
            space=dict(context="ground", plane="ground", camera="3/4 40", width_m=4.0,
                       anchor="world point (ground)", background="dark"),
            options=dict(seed=4, R=50, w0=12, w1=3, ramp=[(0.35, 0.12, 0.05), (1.0, 0.45, 0.1), (1.0, 0.8, 0.35), (1, 1, 0.92)]))


EQ = fx.fbm_equalizer(META["options"]["seed"], 3)


def draw(cv, t, o):
    D = META["duration"]
    p = t / D
    R = o["R"] * cf.ease.out_expo(min(p * 1.6, 1.0))      # nở nhanh, chậm dần
    w = o["w0"] + (o["w1"] - o["w0"]) * cf.ease.out_cubic(p)
    ramp = np.array(o["ramp"])
    S = o["seed"]

    def fn(X, Y):
        r, u = fx.polar(X, Y)
        band = np.abs(r - R) / max(w, 1e-3)              # 0 ở giữa dải → 1 ở mép
        inner = (r < R)                                  # phía trong dải sáng hơn (mặt sóng hướng tâm)
        heat = fx.sat(1 - band) * np.where(inner, 1.0, 0.75)
        # noise theo góc có chu kỳ (period 8 ô quanh vòng) → không đường nối ở u = 0/1
        # fbm dồn quanh 0 → Equalizer đưa về phân bố đều (bảng dựng 1 lần), nếu không ngưỡng quét qua cả vòng trong 1–2 frame
        n = EQ(fx.fbm(u * 6, r / 40, S, 3, period=(6, 1 << 10)))  # tần số thấp → vỡ thành đoạn cung lớn, không lấm tấm
        a0 = fx.cov((band - 1) * w, 1.0)                # mép dải khử răng cưa 1 px
        a, burn = fx.dissolve(a0, n, -0.15 + 1.25 * fx.smoothstep(0.15, 1.0, p) ** 1.4, soft=0.05, edge=0.12)
        rgb = fx.ramp_hard(ramp, fx.sat(heat * 0.9 + burn * 0.3))
        light = ramp[2] * (fx.sat(1 - band) ** 2 * a * 0.35 * (1 - p))[..., None]
        return rgb, a, light

    m = R + w + 2
    cv.shade(-m, -m, m, m, fn)
    cv.glow(0, 0, 40, ramp[2], 0.8 * np.exp(-t / 0.05))  # chớp lúc chạm đất
