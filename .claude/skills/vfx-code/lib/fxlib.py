"""fxlib: kỹ thuật VFX bằng code, rút từ các thư viện mã nguồn mở (xem references/sources.md).

Mọi hàm làm việc trên mảng numpy (X, Y) theo toạ độ local của core.Canvas:
x sang phải, y hướng xuống, (0, 0) = origin. Dùng trong `cv.shade(x0, y0, x1, y1, fn)`
hoặc tự tạo lưới bằng `grid()`.

Nhóm:
  noise     perlin2/perlin3 (có chu kỳ → tile / loop liền), fbm, ridged, voronoi, curl2, warp
  sdf       sd_circle, sd_box, sd_segment, sd_ring, sd_arc, sd_star, sd_tri, sd_vesica,
            op_union/sub/inter, op_smin/smax, op_onion, op_round, rep_polar
  polar     polar(), từ (r, góc 0..1) → vòng, sóng xung kích, vệt chém, cổng
  toon      posterize, bands, ramp_hard, ramp_soft, outline
  dissolve  dissolve() (ngưỡng + mép cháy), erosion() (NovaShader), wipe() (quét gradient), Equalizer
  màu       palette_cos (IQ), doom_fire (lửa automaton)
  shape     fire_mask (gradient × noise rồi cắt ngưỡng), fireball (ramp theo ngưỡng)
  lightning bolt() (chia đôi đoạn + lệch vuông góc + nhánh)
  curves    Curve (key, tuyến tính / mượt), Gradient (key màu), MinMax (giữa 2 hằng / 2 curve)
"""
import math

import numpy as np

TAU = math.tau


# ---------------------------------------------------------------- tiện ích


def grid(w, h, origin, res=1.0):
    """Lưới tâm pixel (toạ độ local) cho ô w×h, origin (ox, oy)."""
    ox, oy = origin
    xs = (np.arange(int(round(w * res))) + 0.5) / res - ox
    ys = (np.arange(int(round(h * res))) + 0.5) / res - oy
    return np.meshgrid(xs, ys)


def sat(v):
    return np.clip(v, 0.0, 1.0)


def smoothstep(a, b, x):
    t = sat((np.asarray(x, dtype=np.float64) - a) / (b - a + 1e-12))
    return t * t * (3 - 2 * t)


def remap(x, a0, a1, b0=0.0, b1=1.0):
    return b0 + (np.asarray(x) - a0) * (b1 - b0) / (a1 - a0 + 1e-12)


def cov(d, px=1.0):
    """SDF (<0 trong) → độ phủ, mép khử răng cưa rộng `px` đơn vị."""
    return sat(0.5 - np.asarray(d) / max(px, 1e-6))


def cov_field(f):
    """Trường bất kỳ (<0 trong) → độ phủ mép 1 px theo gradient của chính nó (core.Canvas._cov_field)."""
    gy, gx = np.gradient(f)
    return sat(0.5 - f / (np.sqrt(gx * gx + gy * gy) + 1e-6))


# ---------------------------------------------------------------- noise (Perlin gradient, có chu kỳ)


def _perm(seed):
    r = np.random.RandomState(seed & 0x7FFFFFFF)
    p = r.permutation(256)
    return np.concatenate([p, p]).astype(np.int64)


_PERM = {}


def _P(seed):
    if seed not in _PERM:
        _PERM[seed] = _perm(seed)
    return _PERM[seed]


def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


_G2 = np.array([[math.cos(a), math.sin(a)] for a in np.arange(16) * TAU / 16])


def perlin2(x, y, seed=0, period=None):
    """Perlin 2D, giá trị ~[-1, 1]. period=(px, py) số ô nguyên → tile liền."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    P = _P(seed)
    xi, yi = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    xf, yf = x - xi, y - yi
    px, py = period if period else (256, 256)

    def g(ix, iy, dx, dy):
        h = P[(P[(ix % px) & 255] + (iy % py)) & 255] & 15
        G = _G2[h]
        return G[..., 0] * dx + G[..., 1] * dy

    u, v = _fade(xf), _fade(yf)
    n00 = g(xi, yi, xf, yf)
    n10 = g(xi + 1, yi, xf - 1, yf)
    n01 = g(xi, yi + 1, xf, yf - 1)
    n11 = g(xi + 1, yi + 1, xf - 1, yf - 1)
    return (n00 + u * (n10 - n00)) + v * ((n01 + u * (n11 - n01)) - (n00 + u * (n10 - n00)))


_G3 = np.array([[1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0], [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],
                [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1], [1, 1, 0], [-1, 1, 0], [0, -1, 1], [0, -1, -1]], float)


def perlin3(x, y, z, seed=0, period=None):
    """Perlin 3D ~[-1, 1]. period=(px, py, pz). Loop liền theo thời gian: z = t/T * pz với pz nguyên."""
    x, y, z = (np.asarray(v, dtype=np.float64) for v in (x, y, z))
    x, y, z = np.broadcast_arrays(x, y, z)
    P = _P(seed)
    xi, yi, zi = (np.floor(v).astype(np.int64) for v in (x, y, z))
    xf, yf, zf = x - xi, y - yi, z - zi
    px, py, pz = period if period else (256, 256, 256)

    def g(ix, iy, iz, dx, dy, dz):
        h = P[(P[(P[(ix % px) & 255] + (iy % py)) & 255] + (iz % pz)) & 255] & 15
        G = _G3[h]
        return G[..., 0] * dx + G[..., 1] * dy + G[..., 2] * dz

    u, v, w = _fade(xf), _fade(yf), _fade(zf)
    L = lambda a, b, t: a + t * (b - a)  # noqa: E731
    c = {}
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                c[i, j, k] = g(xi + i, yi + j, zi + k, xf - i, yf - j, zf - k)
    x00, x10 = L(c[0, 0, 0], c[1, 0, 0], u), L(c[0, 1, 0], c[1, 1, 0], u)
    x01, x11 = L(c[0, 0, 1], c[1, 0, 1], u), L(c[0, 1, 1], c[1, 1, 1], u)
    return L(L(x00, x10, v), L(x01, x11, v), w)


def fbm(x, y, seed=0, octaves=4, lacunarity=2.0, gain=0.5, z=None, period=None):
    """Tổng nhiều tầng noise, chuẩn hoá ~[-1, 1]. Có z → 3D (dùng cho loop thời gian).
    period: chu kỳ ở tầng 1, các tầng sau nhân theo lacunarity (lacunarity nên là số nguyên để vẫn tile)."""
    s, a, f, norm = 0.0, 1.0, 1.0, 0.0
    for o in range(octaves):
        per = None
        if period:
            per = tuple(int(round(p * f)) for p in period)
        if z is None:
            s = s + a * perlin2(x * f, y * f, seed + o * 31, per)
        else:
            s = s + a * perlin3(x * f, y * f, z * (f if period else 1.0), seed + o * 31, per)
        norm += a
        a *= gain
        f *= lacunarity
    return s / norm


def ridged(x, y, seed=0, octaves=4, z=None, period=None):
    """Ridged fbm (1 - |n|)², 0..1: gân sắc — điện, vết nứt, vân nước. KHÔNG dùng cho khối khói (ra đá)."""
    s, a, f, norm = 0.0, 1.0, 1.0, 0.0
    for o in range(octaves):
        per = tuple(int(round(p * f)) for p in period) if period else None
        n = perlin2(x * f, y * f, seed + o * 31, per) if z is None else perlin3(x * f, y * f, z, seed + o * 31, per)
        s = s + a * (1 - np.abs(n)) ** 2
        norm += a
        a *= 0.5
        f *= 2.0
    return s / norm


def voronoi(x, y, seed=0, jitter=1.0, period=None):
    """Worley/Voronoi: trả (F1, F2, id ô). F2-F1 = viền ô (vết nứt, vảy, tia nước); F1 = chấm tròn."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    xi, yi = np.floor(x), np.floor(y)
    f1 = np.full(x.shape, 9.0)
    f2 = np.full(x.shape, 9.0)
    cid = np.zeros(x.shape)
    px, py = period if period else (1 << 20, 1 << 20)
    for j in (-1, 0, 1):
        for i in (-1, 0, 1):
            cx, cy = xi + i, yi + j
            hx = _hashf(np.mod(cx, px), np.mod(cy, py), seed)
            hy = _hashf(np.mod(cx, px), np.mod(cy, py), seed + 17)
            dx = cx + 0.5 + (hx - 0.5) * jitter - x
            dy = cy + 0.5 + (hy - 0.5) * jitter - y
            d = np.sqrt(dx * dx + dy * dy)
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d))
            cid = np.where(closer, hx, cid)
            f1 = np.where(closer, d, f1)
    return f1, f2, cid


def _hashf(ix, iy, seed):
    """Hash số nguyên → 0..1 (vector hoá, tất định)."""
    h = (np.asarray(ix, dtype=np.int64) * 374761393 + np.asarray(iy, dtype=np.int64) * 668265263
         + seed * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFF) / float(0xFFFFFF)


def curl2(x, y, seed=0, eps=0.01, z=None):
    """Trường curl của noise ψ: v = (∂ψ/∂y, -∂ψ/∂x). Không phân kỳ → hạt cuộn xoáy, không tụ cục.
    Dùng cho hạt khói / tàn lửa / bụi phép (three.quarks, Bridson 2007)."""
    f = (lambda a, b: perlin2(a, b, seed)) if z is None else (lambda a, b: perlin3(a, b, z, seed))
    dpdy = (f(x, y + eps) - f(x, y - eps)) / (2 * eps)
    dpdx = (f(x + eps, y) - f(x - eps, y)) / (2 * eps)
    return dpdy, -dpdx


def warp(x, y, amp=1.0, freq=1.0, seed=0, octaves=3, z=None):
    """Domain warping (Inigo Quilez): lệch toạ độ bằng noise rồi mới lấy mẫu → hình chảy, xoắn, lửa phép."""
    qx = fbm(x * freq, y * freq, seed, octaves, z=z)
    qy = fbm(x * freq + 5.2, y * freq + 1.3, seed + 7, octaves, z=z)
    return x + amp * qx, y + amp * qy


# ---------------------------------------------------------------- SDF 2D (Inigo Quilez, hg_sdf)


def sd_circle(x, y, r):
    return np.hypot(x, y) - r


def sd_box(x, y, hw, hh, r=0.0):
    qx, qy = np.abs(x) - hw + r, np.abs(y) - hh + r
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def sd_segment(x, y, ax, ay, bx, by, r0, r1=None):
    """Capsule thon từ a (bán kính r0) tới b (r1). Trả (d, h) với h = 0 ở a → 1 ở b."""
    r1 = r0 if r1 is None else r1
    pax, pay, bax, bay = x - ax, y - ay, bx - ax, by - ay
    h = sat((pax * bax + pay * bay) / (bax * bax + bay * bay + 1e-12))
    d = np.hypot(pax - bax * h, pay - bay * h) - (r0 + (r1 - r0) * h)
    return d, h


def sd_ring(x, y, r, w):
    return np.abs(np.hypot(x, y) - r) - w * 0.5


def sd_arc(x, y, r, w, a0, a1):
    """Cung tròn từ góc a0 → a1 (radian, ngược chiều kim đồng hồ trên màn hình y-xuống là chiều dương của atan2)."""
    ang = np.arctan2(y, x)
    mid, half = (a0 + a1) / 2, abs(a1 - a0) / 2
    da = np.abs((ang - mid + math.pi) % TAU - math.pi)
    rho = np.hypot(x, y)
    inside = da <= half
    d_band = np.abs(rho - r) - w / 2
    e0 = (r * math.cos(mid - half), r * math.sin(mid - half))
    e1 = (r * math.cos(mid + half), r * math.sin(mid + half))
    d_cap = np.minimum(np.hypot(x - e0[0], y - e0[1]), np.hypot(x - e1[0], y - e1[1])) - w / 2
    return np.where(inside, d_band, d_cap)


def sd_star(x, y, r, n=5, m=2.5):
    """Sao n cánh (IQ sdStar). m ∈ [2, n]: 2 = cánh béo, n = cánh rất mảnh."""
    an, en = math.pi / n, math.pi / m
    acs = (math.cos(an), math.sin(an))
    ecs = (math.cos(en), math.sin(en))
    ang = np.arctan2(x, -y)  # cánh đầu tiên hướng lên
    bn = np.mod(ang, 2 * an) - an
    l = np.hypot(x, y)
    px, py = l * np.cos(bn), l * np.abs(np.sin(bn))
    px, py = px - r * acs[0], py - r * acs[1]
    t = np.clip(-(px * ecs[0] + py * ecs[1]), 0, r * acs[1] / ecs[1])
    px, py = px + ecs[0] * t, py + ecs[1] * t
    return np.hypot(px, py) * np.sign(px)


def sd_tri(x, y, r):
    """Tam giác đều cạnh hướng lên (y-xuống: đỉnh ở trên)."""
    k = math.sqrt(3.0)
    y = -y
    x = np.abs(x) - r
    y = y + r / k
    cond = x + k * y > 0
    nx, ny = (x - k * y) / 2, (-k * x - y) / 2
    x, y = np.where(cond, nx, x), np.where(cond, ny, y)
    x = x - np.clip(x, -2 * r, 0)
    return -np.hypot(x, y) * np.sign(y)


def sd_vesica(x, y, r, d):
    """Hình lá / mắt (giao 2 đường tròn): lưỡi lửa, lá chém, mắt phép. Trục dọc."""
    x, y = np.abs(x), np.abs(y)
    b = math.sqrt(max(r * r - d * d, 0))
    return np.where((y - b) * d > x * b, np.hypot(x, y - b), np.hypot(x + d, y) - r)


def op_union(a, b):
    return np.minimum(a, b)


def op_sub(a, b):
    """a trừ b."""
    return np.maximum(a, -b)


def op_inter(a, b):
    return np.maximum(a, b)


def op_smin(a, b, k):
    """Hợp mềm (polynomial smin, IQ): k = độ rộng vùng dính (đơn vị). Khối khói/thuỳ dính nhau."""
    h = sat(0.5 + 0.5 * (b - a) / k)
    return b + (a - b) * h - k * h * (1 - h)


def op_smax(a, b, k):
    return -op_smin(-a, -b, k)


def op_onion(d, w):
    """Biến hình đặc thành viền dày w."""
    return np.abs(d) - w / 2


def op_round(d, r):
    return d - r


def rep_polar(x, y, n):
    """Lặp góc n lần (hg_sdf pModPolar): vẽ 1 tia → được n tia. Trả (x', y', chỉ số)."""
    ang = np.arctan2(y, x) + math.pi / n
    rho = np.hypot(x, y)
    idx = np.floor(ang / (TAU / n))
    a = np.mod(ang, TAU / n) - math.pi / n
    return rho * np.cos(a), rho * np.sin(a), idx


# ---------------------------------------------------------------- polar


def polar(x, y, sy=1.0, rot=0.0):
    """(r, u) với u = góc 0..1 bắt đầu từ `rot` (radian). sy < 1 → vòng nằm đất dưới camera 3/4 (sy ≈ sin 40° = 0.64)."""
    yy = y / max(sy, 1e-6)
    r = np.hypot(x, yy)
    u = np.mod((np.arctan2(yy, x) - rot) / TAU, 1.0)
    return r, u


# ---------------------------------------------------------------- toon


def posterize(v, steps):
    """Bậc cứng: v 0..1 → floor(v·n)/(n-1)."""
    n = max(int(steps), 2)
    return np.clip(np.floor(np.asarray(v) * n), 0, n - 1) / (n - 1)


def bands(v, edges, soft=0.0):
    """Toon band: trả chỉ số bậc 0..len(edges) theo các ngưỡng tăng dần. soft > 0 → mép mềm (trả số thực)."""
    v = np.asarray(v, dtype=np.float64)
    out = np.zeros(v.shape)
    for e in edges:
        out = out + (smoothstep(e - soft, e + soft, v) if soft > 0 else (v >= e))
    return out


def ramp_hard(ramp, v):
    """Tra ramp bậc cứng (thân toon). ramp: mảng (n, 3)."""
    ramp = np.asarray(ramp, dtype=np.float64)
    n = len(ramp)
    return ramp[np.clip(np.floor(np.asarray(v) * n), 0, n - 1).astype(int)]


def ramp_soft(ramp, v):
    """Tra ramp mượt (chỉ cho lớp sáng)."""
    ramp = np.asarray(ramp, dtype=np.float64)
    n = len(ramp)
    xx = sat(v) * (n - 1)
    i = np.clip(np.floor(xx).astype(int), 0, n - 2)
    f = (xx - i)[..., None]
    return ramp[i] * (1 - f) + ramp[i + 1] * f


def outline(alpha, width_px=1.5):
    """Viền ngoài từ alpha (dãn bằng max filter tách trục, không cần scipy). Trả mặt nạ viền 0..1."""
    a = np.asarray(alpha, dtype=np.float64)
    k = max(1, int(math.ceil(width_px)))
    d = a.copy()
    for ax in (0, 1):
        acc = d.copy()
        for s in range(1, k + 1):
            acc = np.maximum(acc, np.roll(d, s, ax))
            acc = np.maximum(acc, np.roll(d, -s, ax))
        d = acc
    return sat(d - a)


def box_blur(f, r, axes=(0, 1)):
    """Làm mờ hộp bán kính r pixel (tách trục, cumsum). Lặp 2–3 lần ≈ Gauss."""
    f = np.asarray(f, dtype=np.float64)
    r = int(r)
    if r <= 0:
        return f
    for ax in axes:
        pad = [(0, 0)] * f.ndim
        pad[ax] = (r + 1, r)
        c = np.cumsum(np.pad(f, pad, mode="edge"), axis=ax)
        n = f.shape[ax]
        f = (np.take(c, range(2 * r + 1, 2 * r + 1 + n), axis=ax) - np.take(c, range(0, n), axis=ax)) / (2 * r + 1)
    return f


# ---------------------------------------------------------------- dissolve (ngưỡng alpha theo noise)


class Equalizer:
    """Đưa noise về phân bố đều 0..1 bằng bảng phân vị dựng MỘT LẦN từ mẫu tham chiếu.
    Lý do: fbm dồn quanh 0 → ngưỡng dissolve tuyến tính quét qua phần lớn diện tích trong 1–2 frame.
    Dựng bảng một lần (không tính lại mỗi frame) → chỗ đã tan không đặc lại (luật liên tục khung hình)."""

    def __init__(self, sample, n=257):
        s = np.sort(np.asarray(sample, dtype=np.float64).ravel())
        self.q = s[np.linspace(0, len(s) - 1, n).astype(int)]
        self.p = np.linspace(0, 1, n)

    def __call__(self, v):
        return np.interp(v, self.q, self.p)


def fbm_equalizer(seed=0, octaves=3, n=20000):
    """Equalizer cho fbm(seed, octaves) — lấy mẫu ngẫu nhiên trên mặt phẳng noise."""
    r = np.random.RandomState(seed + 999)
    xs, ys = r.uniform(0, 64, n), r.uniform(0, 64, n)
    return Equalizer(fbm(xs, ys, seed, octaves))


def dissolve(alpha, noise, t, soft=0.06, edge=0.08):
    """Ăn mòn: pixel còn khi noise > t. Trả (alpha_mới, mặt nạ mép cháy 0..1).
    - noise 0..1, đứng yên theo thời gian (bám bề mặt) → chỗ đã tan không đặc lại;
    - soft: dải mờ theo đơn vị noise (không theo pixel → mép không rung);
    - edge: độ rộng dải mép cháy phía trong (tô màu lửa / sáng cộng).
    t chạy -soft..1+soft là tan hết. Trong Unity: t = Custom1.x hoặc 1 - vertex alpha (Uber particle shader)."""
    n = np.asarray(noise, dtype=np.float64)
    keep = smoothstep(t - soft, t + soft, n)
    burn = (1 - smoothstep(t, t + edge, n)) * keep if edge > 0 else np.zeros_like(n)
    return np.asarray(alpha) * keep, burn


def erosion(alpha, noise, p, sharp=0.6):
    """Alpha erosion kiểu NovaShader (MIT): p 0..1 (Unity: 1 - vertex alpha hoặc Custom1.x).
    w = lerp(0.5, 1e-4, sharp); p' = lerp(-w, 1 + w, p) → p = 0 nguyên vẹn, p = 1 mất hết, bất kể sharp.
    Cùng công thức với shader realtime (references/shaders.md) → flipbook và shader cho kết quả giống nhau."""
    w = 0.5 + (1e-4 - 0.5) * sharp
    pp = -w + (1 + 2 * w) * p
    return np.asarray(alpha) * smoothstep(pp - w, pp + w, noise)


def wipe(shape, grad, p, width=0.15):
    """Gradient sweep (GDQuest blast, MIT): kênh `grad` 0..1 quét một dải mềm qua `shape`.
    Dùng cho vệt chém hiện dần, vòng nở, quét theo hướng. Trả alpha."""
    g = (2 * width + 1) * p - width
    mask = smoothstep(0, 1, sat(np.abs(np.asarray(grad) - g) / width * 2))
    return sat(np.asarray(shape) - mask)


def palette_cos(t, a=(0.5, 0.5, 0.5), b=(0.5, 0.5, 0.5), c=(1, 1, 1), d=(0.0, 0.33, 0.67)):
    """Palette cosine (Inigo Quilez): col = a + b·cos(2π(c·t + d)). Thay ramp bằng 4 vector — chỉ hợp lớp sáng / nháp."""
    t = np.asarray(t, dtype=np.float64)[..., None]
    return np.clip(np.asarray(a) + np.asarray(b) * np.cos(TAU * (np.asarray(c) * t + np.asarray(d))), 0, 1)


def doom_fire(w, h, steps, seed=0, wind=1, source=None):
    """Lửa automaton kiểu Doom (filipedeschamps/doom-fire-algorithm, MIT): hàng đáy nóng tối đa,
    mỗi bước mỗi ô lấy nhiệt ô dưới trừ 0–1, dịch ngang ngẫu nhiên. Vector hoá theo hàng.
    Trả list `steps` mảng nhiệt 0..1 (đem tra ramp bậc cứng → lửa pixel/toon gần như miễn phí)."""
    r = np.random.RandomState(seed)
    H = np.zeros((h, w))
    H[-1, :] = 1.0 if source is None else source
    out = []
    for _ in range(steps):
        for y in range(h - 1):
            rnd = r.randint(0, 4, w)
            src = H[y + 1]
            dec = (rnd & 1) * (1.0 / 36)
            xs = np.clip(np.arange(w) - rnd + wind, 0, w - 1)
            H[y, xs] = np.maximum(src - dec, 0)
        out.append(H.copy())
    return out


# ---------------------------------------------------------------- hình lửa / quả cầu lửa


def fire_mask(x, y, h, w, t, seed=0, speed=1.0, period_t=None, detail=3):
    """Ngọn lửa (cách Shadertoy / Godot shader): gradient dọc × noise cuộn lên rồi cắt ngưỡng.
    x, y local (origin = chân lửa, y hướng xuống). h = chiều cao, w = nửa bề ngang.
    Trả trường 'nhiệt' 0..1 (>0 là có lửa): đem cắt ngưỡng / tra ramp bậc cứng.
    period_t: chu kỳ loop (s) → noise 3D có chu kỳ, lửa loop liền."""
    u = x / max(w, 1e-6)
    v = sat(-y / max(h, 1e-6))                      # 0 ở chân → 1 ở đỉnh
    shape = (1 - v) * sat(1 - np.abs(u) / (1.0 - 0.65 * v + 1e-6))  # tam giác thon lên
    if period_t:
        z = (t / period_t) * 4.0
        n = fbm(x / w * 1.2, (y / h) * 2.0, seed, detail, z=z, period=(64, 64, 4))
    else:
        n = fbm(x / w * 1.2, (y / h) * 2.0 + t * speed * 2.0, seed, detail)
    return shape + 0.55 * n * (0.35 + v) - 0.25


def fireball(r_norm, noise, heat):
    """Quả cầu lửa stylized: nhiệt = heat(t) - r_norm + noise → tra ramp bậc cứng.
    r_norm 0 ở tâm → 1 ở viền. heat giảm theo thời gian: trắng → vàng → cam → đỏ → khói."""
    return np.asarray(heat) - np.asarray(r_norm) + 0.35 * np.asarray(noise)


# ---------------------------------------------------------------- tia sét


def bolt(ax, ay, bx, by, seed=0, depth=6, offset=0.22, branch_p=0.35, branch_len=0.6, branch_ang=0.5):
    """Tia sét kiểu chia đôi đoạn (midpoint displacement, nhiều repo 'lightning generator'):
    mỗi vòng chia đôi mọi đoạn, lệch điểm giữa vuông góc ±offset·độ dài, offset giảm một nửa mỗi vòng;
    nhánh rẽ ở điểm giữa với xác suất branch_p, lệch 20–45°.
    Trả list đoạn (x0, y0, x1, y1, cấp) — cấp 0 = thân chính (dày nhất)."""
    rng = np.random.RandomState(seed & 0x7FFFFFFF)
    segs = [(ax, ay, bx, by, 0)]
    off = offset * math.hypot(bx - ax, by - ay)
    for _ in range(depth):
        out = []
        for x0, y0, x1, y1, lv in segs:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            dx, dy = x1 - x0, y1 - y0
            L = math.hypot(dx, dy) + 1e-9
            nx, ny = -dy / L, dx / L
            k = rng.uniform(-1, 1) * off / (1 + lv)
            mx, my = mx + nx * k, my + ny * k
            out.append((x0, y0, mx, my, lv))
            out.append((mx, my, x1, y1, lv))
            if lv < 2 and rng.rand() < branch_p / (1 + lv):
                ang = math.atan2(my - y0, mx - x0) + rng.choice([-1, 1]) * rng.uniform(0.35, 0.8) * branch_ang * 1.6
                bl = math.hypot(mx - x0, my - y0) * branch_len * 1.6
                out.append((mx, my, mx + math.cos(ang) * bl, my + math.sin(ang) * bl, lv + 1))
        segs = out
        off *= 0.5
    return segs


# ---------------------------------------------------------------- curve / gradient (kiểu module "over lifetime")


class Curve:
    """Curve theo key [(t, v), ...], t 0..1. mode 'linear' hoặc 'smooth' (Catmull-Rom).
    Đánh giá được trên mảng (vector hoá). Cùng dạng với AnimationCurve / three.quarks PiecewiseBezier."""

    def __init__(self, keys, mode="linear"):
        self.k = sorted((float(a), float(b)) for a, b in keys)
        self.mode = mode

    def __call__(self, t):
        t = np.asarray(t, dtype=np.float64)
        ts = np.array([a for a, _ in self.k])
        vs = np.array([b for _, b in self.k])
        if self.mode == "linear" or len(ts) < 3:
            return np.interp(t, ts, vs)
        i = np.clip(np.searchsorted(ts, t, side="right") - 1, 0, len(ts) - 2)
        t0, t1 = ts[i], ts[i + 1]
        u = sat((t - t0) / (t1 - t0 + 1e-12))
        p0 = vs[np.maximum(i - 1, 0)]
        p1, p2 = vs[i], vs[i + 1]
        p3 = vs[np.minimum(i + 2, len(vs) - 1)]
        return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


class Gradient:
    """Gradient màu theo key [(t, (r, g, b)), ...]. hard=True → bậc cứng (toon)."""

    def __init__(self, keys, hard=False):
        self.k = sorted(keys, key=lambda kv: kv[0])
        self.hard = hard

    def __call__(self, t):
        t = np.asarray(t, dtype=np.float64)
        ts = np.array([a for a, _ in self.k])
        cs = np.array([c for _, c in self.k], dtype=np.float64)
        if self.hard:
            i = np.clip(np.searchsorted(ts, t, side="right") - 1, 0, len(ts) - 1)
            return cs[i]
        return np.stack([np.interp(t, ts, cs[:, c]) for c in range(3)], axis=-1)


class MinMax:
    """Giá trị ngẫu nhiên giữa 2 hằng / 2 curve, cố định theo hạt (Unity MinMaxCurve, Effekseer random range).
    lerp theo `r` riêng của từng hạt (0..1), không random lại mỗi frame."""

    def __init__(self, a, b=None):
        self.a, self.b = a, (a if b is None else b)

    def __call__(self, r, t=0.0):
        av = self.a(t) if callable(self.a) else self.a
        bv = self.b(t) if callable(self.b) else self.b
        return av + (bv - av) * r
