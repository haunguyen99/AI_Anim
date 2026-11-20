"""particles: hệ hạt vector hoá (numpy) cho flipbook vfx-code, theo mẫu kiến trúc của
three.quarks / bevy_hanabi / Godot / Effekseer / LÖVE / pixi-particle-emitter (xem references/particles.md).

  spawn (burst / rate)  →  init (MinMax lấy 1 số ngẫu nhiên / hạt, nhớ suốt đời)
                        →  update (danh sách behavior theo thứ tự)  →  draw (disc / streak / glow / trail)

Khác core.Particles (6 loại hạt có lực chỉnh sẵn): ở đây lực ghép tự do, giá trị theo đời hạt
(Curve / Gradient), sub-emitter khi chết, stretched billboard đúng công thức Unity.
Tất định: mọi ngẫu nhiên lấy từ RandomState(seed + emitter).

Toạ độ: x phải, y XUỐNG, (0,0) = origin. Trọng lực dương = rơi xuống.
"""
import math

import numpy as np

import fxlib as fx


def _val(v, r, t=0.0):
    """Giá trị: số · (a, b) ngẫu nhiên giữa 2 số theo r · Curve/callable theo t · fx.MinMax."""
    if isinstance(v, fx.MinMax):
        return v(r, t)
    if isinstance(v, (tuple, list)) and len(v) == 2 and not callable(v[0]):
        return v[0] + (v[1] - v[0]) * r
    if callable(v):
        return v(t)
    return np.full(np.shape(r), float(v)) if np.ndim(r) else float(v)


class System:
    """SoA: mỗi thuộc tính là một mảng. Hạt chết được giữ lại (alive=False) để chỉ số ổn định."""

    ATTR = ("x", "y", "vx", "vy", "age", "life", "size", "rot", "spin", "delay", "kind")

    def __init__(self, seed=1, behaviors=None, ground=None, trail=0):
        self.rng = np.random.RandomState(seed & 0x7FFFFFFF)
        self.b = list(behaviors or [])
        self.ground = ground                      # None hoặc y của mặt đất (thường 0)
        self.trail = trail                        # số điểm lịch sử cho ribbon / trail
        for a in self.ATTR:
            setattr(self, a, np.zeros(0))
        self.alive = np.zeros(0, bool)
        self.mem = np.zeros((0, 8))               # 8 số ngẫu nhiên / hạt (GeneratorMemory của three.quarks)
        self.hist = np.zeros((0, max(trail, 1), 2))
        self.on_death = None                      # fn(system, idx_array) — sub-emitter
        self.t = 0.0

    # ------------------------------------------------------------ spawn
    def burst(self, n, x=0.0, y=0.0, shape="point", radius=0.0, angle=(0, 360), speed=(100, 200),
              life=(0.3, 0.6), size=(1.0, 1.0), delay=(0.0, 0.0), spin=(0.0, 0.0), kind=0, even=False,
              inherit=None):
        """shape: point | circle (trên viền) | disc (trong lòng). angle (độ, 0 = phải, 90 = XUỐNG theo y-xuống;
        dùng -90 cho hướng lên). even=True: chia góc đều + lệch nhỏ (pixi burst đều → hình toả cân)."""
        n = int(n)
        if n <= 0:
            return np.zeros(0, int)
        R = self.rng
        m = R.rand(n, 8)
        a0, a1 = math.radians(angle[0]), math.radians(angle[1])
        if even:
            ang = a0 + (a1 - a0) * (np.arange(n) + 0.5 + (m[:, 0] - 0.5) * 0.6) / n
        else:
            ang = a0 + (a1 - a0) * m[:, 0]
        if shape == "circle":
            px, py = x + np.cos(ang) * radius, y + np.sin(ang) * radius
        elif shape == "disc":
            rr = radius * np.sqrt(m[:, 7])
            px, py = x + np.cos(ang) * rr, y + np.sin(ang) * rr
        else:
            px, py = np.full(n, float(x)), np.full(n, float(y))
        sp = _val(speed, m[:, 1])
        vx, vy = np.cos(ang) * sp, np.sin(ang) * sp
        if inherit is not None:
            vx, vy = vx + inherit[0], vy + inherit[1]
        new = dict(x=px, y=py, vx=vx, vy=vy, age=np.zeros(n), life=_val(life, m[:, 2]),
                   size=_val(size, m[:, 3]), rot=ang.copy(), spin=np.radians(_val(spin, m[:, 4])),
                   delay=_val(delay, m[:, 5]), kind=np.full(n, float(kind)))
        i0 = len(self.x)
        for k, v in new.items():
            setattr(self, k, np.concatenate([getattr(self, k), v]))
        self.alive = np.concatenate([self.alive, np.ones(n, bool)])
        self.mem = np.vstack([self.mem, m])
        h = np.repeat(np.stack([px, py], 1)[:, None, :], max(self.trail, 1), 1)
        self.hist = np.concatenate([self.hist, h])
        return np.arange(i0, i0 + n)

    # ------------------------------------------------------------ update
    def update(self, dt):
        self.t += dt
        if not len(self.x):
            return
        wait = self.delay > 0
        self.delay = np.where(wait, self.delay - dt, self.delay)
        act = self.alive & ~wait
        self.age = np.where(act, self.age + dt, self.age)
        dead = act & (self.age >= self.life)
        if dead.any():
            self.alive &= ~dead
            if self.on_death:
                self.on_death(self, np.nonzero(dead)[0])
            act = self.alive & (self.delay <= 0)     # hạt mới sinh từ on_death chạy từ bước sau
        if not act.any():
            return
        for bh in self.b:
            bh(self, act, dt)
        self.x = np.where(act, self.x + self.vx * dt, self.x)
        self.y = np.where(act, self.y + self.vy * dt, self.y)
        self.rot = np.where(act, self.rot + self.spin * dt, self.rot)
        if self.ground is not None:
            hit = act & (self.y > self.ground)
            self.y = np.where(hit, self.ground, self.y)
            self.vy = np.where(hit, -self.vy * 0.35, self.vy)
            self.vx = np.where(hit, self.vx * 0.7, self.vx)
        if self.trail > 1:
            self.hist[act, 1:] = self.hist[act, :-1]
            self.hist[act, 0, 0], self.hist[act, 0, 1] = self.x[act], self.y[act]

    def nlife(self):
        """Tuổi chuẩn hoá 0..1 (cho Curve / Gradient over lifetime)."""
        return np.clip(self.age / np.maximum(self.life, 1e-6), 0, 1)

    def live(self):
        return np.nonzero(self.alive & (self.delay <= 0))[0]

    # ------------------------------------------------------------ draw vào core.Canvas
    def draw(self, cv, mode="disc", color=(1, 1, 1), size_curve=None, alpha_curve=None, glow=None,
             length_scale=1.0, speed_scale=0.0, ramp=None, heat_curve=None, idx=None):
        """mode:
          disc    thân toon (alpha-over), bán kính = size · size_curve(tuổi)
          streak  stretched billboard kiểu Unity: đầu ở hạt, kéo NGƯỢC hướng bay,
                  dài = size·length_scale + |v|·speed_scale, đầu dày → đuôi nhọn
          glow    chỉ lớp sáng cộng
          trail   ribbon từ lịch sử vị trí (trail > 1), thon dần về đuôi
        color: rgb · Gradient theo tuổi · None + ramp/heat_curve (tra ramp bậc cứng theo nhiệt(tuổi))
        glow: (bán kính × size, cường độ) → thêm lớp sáng ở đầu hạt."""
        ids = self.live() if idx is None else idx
        if not len(ids):
            return
        u = self.nlife()[ids]
        sz = self.size[ids] * (size_curve(u) if size_curve else 1.0)
        al = alpha_curve(u) if alpha_curve else np.ones(len(ids))
        if ramp is not None:
            cols = fx.ramp_hard(ramp, heat_curve(u) if heat_curve else 1 - u)
        elif callable(color):
            cols = np.asarray(color(u))
        else:
            cols = np.tile(np.asarray(color, float), (len(ids), 1))
        for j, i in enumerate(ids):
            r, c, a = float(sz[j]), cols[j], float(al[j])
            if r <= 0.05 or a <= 0.01:
                continue
            x, y = float(self.x[i]), float(self.y[i])
            if mode == "disc":
                cv.disc(x, y, r, c, a)
            elif mode == "streak":
                v = math.hypot(self.vx[i], self.vy[i])
                L = r * length_scale + v * speed_scale
                dx, dy = (self.vx[i] / v, self.vy[i] / v) if v > 1e-6 else (1.0, 0.0)
                cv.streak(x, y, x - dx * L, y - dy * L, r, r * 0.15, c, a)
            elif mode == "trail" and self.trail > 1:
                h = self.hist[i]
                for k in range(len(h) - 1):
                    f0, f1 = 1 - k / (len(h) - 1), 1 - (k + 1) / (len(h) - 1)
                    cv.streak(h[k, 0], h[k, 1], h[k + 1, 0], h[k + 1, 1], r * f0, max(r * f1, 0.05), c, a * f0 ** 0.5)
            if glow or mode == "glow":
                gr, gk = glow if glow else (3.0, 0.6)
                cv.glow(x, y, r * gr, c, gk * a)


# ---------------------------------------------------------------- behaviors (gọi theo thứ tự trong list)


def drag(k):
    """v /= (1 + k·dt) — ổn định mọi dt (LÖVE). k 2–4: bắn nhanh trôi chậm."""
    def f(s, m, dt):
        d = 1.0 / (1.0 + k * dt)
        s.vx = np.where(m, s.vx * d, s.vx)
        s.vy = np.where(m, s.vy * d, s.vy)
    return f


def gravity(gx=0.0, gy=600.0):
    """Gia tốc hằng (đơn vị/s²). y-xuống: gy > 0 = rơi; gy < 0 = nổi (khói, tàn lửa)."""
    def f(s, m, dt):
        s.vx = np.where(m, s.vx + gx * dt, s.vx)
        s.vy = np.where(m, s.vy + gy * dt, s.vy)
    return f


def radial(a=0.0, tangential=0.0, cx=0.0, cy=0.0):
    """Gia tốc theo hướng tâm (a > 0 đẩy ra) + tiếp tuyến (xoáy) — LÖVE / Godot."""
    def f(s, m, dt):
        dx, dy = s.x - cx, s.y - cy
        d = np.hypot(dx, dy) + 1e-6
        rx, ry = dx / d, dy / d
        s.vx = np.where(m, s.vx + (rx * a - ry * tangential) * dt, s.vx)
        s.vy = np.where(m, s.vy + (ry * a + rx * tangential) * dt, s.vy)
    return f


def vortex(speed=200.0, pull=0.0, cx=0.0, cy=0.0, k=8.0):
    """Xoáy kiểu Effekseer: LÁI vận tốc về (tiếp tuyến·speed + hướng tâm·pull) thay vì cộng thêm
    → không nổ tốc độ ở fps thấp. k = độ bám (1/s). Hạt phép cuộn quanh tâm, cổng dịch chuyển."""
    def f(s, m, dt):
        dx, dy = s.x - cx, s.y - cy
        d = np.hypot(dx, dy) + 1e-6
        tx, ty = -dy / d, dx / d
        txv, tyv = tx * speed - dx / d * pull, ty * speed - dy / d * pull
        w = 1 - math.exp(-k * dt)
        s.vx = np.where(m, s.vx + (txv - s.vx) * w, s.vx)
        s.vy = np.where(m, s.vy + (tyv - s.vy) * w, s.vy)
    return f


def attractor(x, y, force=800.0, radius=100.0):
    """Hút về điểm, suy giảm (1 - d²/R²) trong bán kính R (Proton). force < 0 = đẩy."""
    def f(s, m, dt):
        dx, dy = x - s.x, y - s.y
        d2 = dx * dx + dy * dy
        d = np.sqrt(d2) + 1e-6
        fall = np.clip(1 - d2 / (radius * radius), 0, 1)
        s.vx = np.where(m, s.vx + dx / d * force * fall * dt, s.vx)
        s.vy = np.where(m, s.vy + dy / d * force * fall * dt, s.vy)
    return f


def curl(scale=40.0, influence=0.5, time_speed=0.5, seed=0):
    """Curl noise kiểu Godot: TRỘN hướng vận tốc về trường curl, giữ độ lớn |v|:
    v = mix(v, curl̂·|v|, influence·dt·10). Hạt cuộn mềm, không tụ cục, không tăng tốc."""
    def f(s, m, dt):
        cx, cy = fx.curl2(s.x / scale, s.y / scale, seed, z=s.t * time_speed)
        l = np.hypot(cx, cy) + 1e-6
        sp = np.hypot(s.vx, s.vy)
        w = min(influence * dt * 10, 1.0)
        s.vx = np.where(m, s.vx + (cx / l * sp - s.vx) * w, s.vx)
        s.vy = np.where(m, s.vy + (cy / l * sp - s.vy) * w, s.vy)
    return f


def limit_speed(vmax, dampen=0.5):
    """Giới hạn tốc độ (three.quarks LimitSpeedOverLife). vmax: số hoặc Curve theo tuổi."""
    def f(s, m, dt):
        L = vmax(s.nlife()) if callable(vmax) else vmax
        sp = np.hypot(s.vx, s.vy) + 1e-6
        over = m & (sp > L)
        k = np.clip(1 - ((sp - L) / sp) * dampen * dt * 20, 0, 1)
        s.vx = np.where(over, s.vx * k, s.vx)
        s.vy = np.where(over, s.vy * k, s.vy)
    return f


def loop_phase_ages(n, phase, life=1.0, seed=0, jitter=0.8):
    """Hạt loop không đường nối (Pixel FX Forge LoopFrames): đời hạt = chu kỳ loop, thời điểm sinh chia đều
    birth_i = (i + jitter·r)/n, tuổi tại pha φ = ((φ - birth) mod 1)·life.
    Trả (tuổi giây, chỉ số vòng đời k) — trộn k vào seed để mỗi vòng đời khác nhau. Pha 0 và 1 cho cùng tuổi,
    nhưng k lệch 1 → muốn loop tuyệt đối thì KHÔNG dùng k (mỗi hạt lặp đúng một quỹ đạo)."""
    r = np.random.RandomState(seed).rand(n)
    birth = (np.arange(n) + jitter * r) / n
    x = phase - birth
    return np.mod(x, 1.0) * life, np.floor(x).astype(int)


def wander(amount=60.0, freq=6.0):
    """Lắc ngang theo noise riêng từng hạt (tàn lửa, bụi phép)."""
    def f(s, m, dt):
        n = fx.perlin2(s.age * freq, s.mem[:, 6] * 97.0, 11)
        s.vx = np.where(m, s.vx + n * amount * dt * 10, s.vx)
    return f
