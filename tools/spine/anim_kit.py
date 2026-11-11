"""Bộ hàm dựng anim Spine 4.2 bằng script, rút từ Cừu cầm ô (SheepUmbrella) và Cừu Sakura (CuuSakura), 2026-11-02.

Dùng bởi `tools/spine/idle_engine.py`, `tools/spine/active_engine.py` (skill /skillidle, /skillactive).
Mọi hàm ở đây đã chạy thật trong hai anim được duyệt; đổi hành vi thì kiểm lại bằng ví dụ CuuSakura của skill.

Quy ước: frame ở 30 fps; góc là độ, cộng thêm vào góc setup (giá trị timeline rotate của Spine); y hướng lên.
"""
import copy, json, math, os, sys

FPS = 30
try:
    sys.stdout.reconfigure(encoding="utf-8")   # chạy -I trên Windows: in tiếng Việt không lỗi
except Exception:
    pass
TOOLS = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------- toán nhỏ
def ss(a, b, x):
    """smoothstep 0 -> 1 khi x đi từ a tới b."""
    if b == a:
        return 1.0 if x >= b else 0.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def wave(amp, freq, ph, T):
    """sóng tuần hoàn theo loop T giây: amp * sin(2π (freq t / T - ph)); ph tính theo vòng của chính sóng."""
    return lambda t: amp * math.sin(2 * math.pi * (freq * t / T - ph))


def add(*fs):
    return lambda t: sum(f(t) for f in fs)


def spl(keys, amp=1.0, K=1.0):
    """mốc [(frame, giá trị)] -> g(frame), kiểu pose-to-pose: key đỉnh / đáy có tiếp tuyến 0 (không vượt key,
    ease ở pose chính), key nằm giữa dốc dùng tiếp tuyến Catmull-Rom; hai đầu vận tốc 0. Ngoài khoảng = mốc đầu / cuối.
    K giãn trục frame (độ dài anim đổi thì mốc giãn theo)."""
    ks = [(f * K, v * amp) for f, v in keys]
    n = len(ks)
    m = [0.0] * n
    for i in range(1, n - 1):
        if (ks[i][1] - ks[i - 1][1]) * (ks[i + 1][1] - ks[i][1]) > 0:
            m[i] = (ks[i + 1][1] - ks[i - 1][1]) / (ks[i + 1][0] - ks[i - 1][0])

    def g(f):
        if f <= ks[0][0]:
            return ks[0][1]
        if f >= ks[-1][0]:
            return ks[-1][1]
        for i in range(n - 1):
            f0, v0 = ks[i]; f1, v1 = ks[i + 1]
            if f <= f1:
                h = f1 - f0; t = (f - f0) / h
                return ((2 * t**3 - 3 * t**2 + 1) * v0 + (t**3 - 2 * t**2 + t) * h * m[i]
                        + (-2 * t**3 + 3 * t**2) * v1 + (t**3 - t**2) * h * m[i + 1])
    return g


def lag(g, d, a=1.0):
    """đốt sau = đốt trước trễ d frame, nhân biên độ a (overlap chuỗi: cùng một nhịp, không mỗi đốt một nhịp)."""
    return lambda f: a * g(f - d)


def blur(v, sig):
    r = int(3 * sig) + 1
    w = [math.exp(-0.5 * (i / sig) ** 2) for i in range(-r, r + 1)]
    out = []
    for i in range(len(v)):
        t = sw = 0.0
        for j, wj in zip(range(i - r, i + r + 1), w):
            t += v[min(max(j, 0), len(v) - 1)] * wj; sw += wj
        out.append(t / sw)
    return out


def arr_fn(a, pad):
    """mảng mẫu theo frame (bắt đầu ở frame -pad) -> hàm nội suy tuyến tính."""
    def g(f):
        x = min(max(f + pad, 0.0), len(a) - 1.0); i = min(int(x), len(a) - 2); u = x - i
        return a[i] * (1 - u) + a[i + 1] * u
    return g


def path_drive(y_fn, L, max_rot=14.0, max_acc=14.0, ramp=8, pad=40, sign=-1.0):
    """từ đường bay y(frame) của ctrl: trả (rot, acc) theo frame.
    rot = góc ngóc / chúi tỉ lệ vận tốc bay (lớn nhất = max_rot), dấu `sign` (mũi về -x: bay lên = xoay âm);
    acc = gia tốc bay đã chuẩn hoá (lớn nhất = max_acc) -> dùng cho quán tính đuôi / thân (bị chặn ở đáy thì văng xuống).
    Đã làm mượt (blur) và tăng dần từ 0 trong `ramp` frame đầu để F0 trùng idle. (Cừu Sakura active v3)"""
    F = list(range(-pad, L + pad + 1))
    y = [y_fn(f) for f in F]
    vy = blur([(y[min(i + 1, len(y) - 1)] - y[max(i - 1, 0)]) / 2 for i in range(len(y))], 1.5)
    ay = blur([(vy[min(i + 1, len(vy) - 1)] - vy[max(i - 1, 0)]) / 2 for i in range(len(vy))], 2.0)
    cr = max_rot / (max(abs(v) for v in vy) or 1)
    ca = max_acc / (max(abs(v) for v in ay) or 1)
    rmp = [ss(0, ramp, f) for f in F]
    rot = [sign * cr * v * r for v, r in zip(vy, rmp)]
    acc = [ca * a for a in ay]                         # chưa nhân ramp: nhân ở chỗ dùng (cùng ramp với cả tín hiệu)
    return arr_fn(rot, pad), arr_fn(acc, pad), arr_fn(rmp, pad)


# ---------------------------------------------------------------- curve / key Spine
def spine_curve(keys, field="value"):
    """giá trị timeline Spine 4.2 tại frame f (curve bezier / linear / stepped). Dùng đọc key người dùng sửa tay."""
    ks = [(k.get("time", 0) * FPS, k[field], k.get("curve")) for k in keys]
    fi = {"value": 0, "x": 0, "y": 1}.get(field, 0)

    def g(f):
        if f <= ks[0][0]:
            return ks[0][1]
        for (t0, v0, c), (t1, v1, _) in zip(ks, ks[1:]):
            if f <= t1:
                if c == "stepped":
                    return v0
                if not c:
                    return v0 + (v1 - v0) * (f - t0) / (t1 - t0)
                c = c[4 * fi: 4 * fi + 4]
                x1, y1, x2, y2 = c[0] * FPS, c[1], c[2] * FPS, c[3]
                lo, hi = 0.0, 1.0
                for _ in range(40):
                    u = (lo + hi) / 2
                    x = (1 - u) ** 3 * t0 + 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u * u * x2 + u ** 3 * t1
                    lo, hi = (u, hi) if x < f else (lo, u)
                u = (lo + hi) / 2
                return (1 - u) ** 3 * v0 + 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u * u * y2 + u ** 3 * v1
        return ks[-1][1]
    return g


def periodic_keys(f, fields, T, n_keys=12, end=None):
    """kênh tuần hoàn f(t giây) -> tuple: key đều n_keys / loop, tay cầm bezier theo đạo hàm (khớp sóng, ít key)."""
    end = end if end is not None else round(T * FPS)
    times = [round(i * end / n_keys) / FPS for i in range(n_keys + 1)]
    h = 1e-3
    ks = []
    for i, t in enumerate(times):
        v = f(t % T)
        k = {"time": round(t, 4)} if t else {}
        k.update({n: round(x, 3) for n, x in zip(fields, v)})
        if i < len(times) - 1:
            t2 = times[i + 1]; dt = (t2 - t) / 3
            v2 = f(t2 % T)
            d1 = [(a - b) / (2 * h) for a, b in zip(f((t + h) % T), f((t - h) % T))]
            d2 = [(a - b) / (2 * h) for a, b in zip(f((t2 + h) % T), f((t2 - h) % T))]
            c = []
            for j in range(len(fields)):
                c += [round(t + dt, 4), round(v[j] + d1[j] * dt, 3), round(t2 - dt, 4), round(v2[j] - d2[j] * dt, 3)]
            k["curve"] = c
        ks.append(k)
    return ks


def sample_keys(v, step=4):
    """mẫu góc theo frame (0..N, tuần hoàn) -> key rotate mỗi `step` frame, tay cầm bezier theo đạo hàm."""
    n = len(v) - 1
    d = [(v[(i + 1) % n] - v[(i - 1) % n]) / 2 * FPS for i in range(n)]
    d.append(d[0])
    fr = list(range(0, n, step)) + [n]
    ks = []
    for j, f in enumerate(fr):
        k = {"time": round(f / FPS, 4)} if f else {}
        k["value"] = round(v[f], 3)
        if j + 1 < len(fr):
            f1 = fr[j + 1]; h = (f1 - f) / FPS / 3
            k["curve"] = [round(f / FPS + h, 4), round(v[f] + d[f] * h, 3), round(f1 / FPS - h, 4), round(v[f1] - d[f1] * h, 3)]
        ks.append(k)
    return ks


def _cr(vals):
    n = len(vals) - 1

    def g(x):
        x = min(max(x, 0.0), float(n)); i = min(int(x), n - 1) if n else 0; t = x - i
        p0, p1, p2, p3 = vals[max(0, i - 1)], vals[i], vals[min(n, i + 1)], vals[min(n, i + 2)]
        return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
    return g


def _d(g, x, n, e=0.01):
    a, b = max(0.0, x - e), min(float(n), x + e)
    return (g(b) - g(a)) / (b - a)


def _herm(g, f0, f1, x, n):
    h = f1 - f0; t = (x - f0) / h
    return ((2*t**3 - 3*t**2 + 1) * g(f0) + (t**3 - 2*t**2 + t) * h * _d(g, f0, n)
            + (-2*t**3 + 3*t**2) * g(f1) + (t**3 - t**2) * h * _d(g, f1, n))


def curve_keys(chans, fields, tol):
    """mẫu theo frame (mỗi kênh một list 0..N) -> key Spine ít nhất: giữ F0 / F cuối / đỉnh, thêm key ở chỗ lệch
    nhất tới khi sai số Hermite <= tol (độ: 0.08, px: 0.25, scale: 0.003)."""
    n = len(chans[0]) - 1
    gs = [_cr(v) for v in chans]
    ks = {0, n}
    for v in chans:
        for x in range(1, n):
            if (v[x] - v[x - 1]) * (v[x + 1] - v[x]) < 0:
                ks.add(x)
    while True:
        k = sorted(ks); worst, at = 0.0, None
        for f0, f1 in zip(k, k[1:]):
            for i in range(1, 2 * (f1 - f0)):
                x = f0 + i / 2
                for g in gs:
                    e = abs(_herm(g, f0, f1, x, n) - g(x))
                    if e > worst:
                        worst, at = e, round(x)
        if worst <= tol or at is None or at in ks:
            break
        ks.add(at)
    fr = sorted(ks)
    if all(max(v) - min(v) < 1e-9 for v in chans):
        fr = [0]
    out = []
    for i, f in enumerate(fr):
        k = {} if f == 0 else {"time": round(f / FPS, 4)}
        for fld, g in zip(fields, gs):
            k[fld] = round(g(f), 4)
        if i + 1 < len(fr):
            f1 = fr[i + 1]; h = (f1 - f) / FPS / 3; c = []
            for g in gs:
                c += [round(f / FPS + h, 4), round(g(f) + _d(g, f, n) * FPS * h, 4),
                      round(f1 / FPS - h, 4), round(g(f1) - _d(g, f1, n) * FPS * h, 4)]
            k["curve"] = c
        out.append(k)
    return out


def tfloor(f):
    """giây của frame f, làm tròn xuống: key slot / stepped rơi đúng frame (làm tròn lên trễ 1 frame)."""
    return math.floor(f / FPS * 1e4) / 1e4


# ---------------------------------------------------------------- mặt: chớp mắt, nhắm cười
def blink(B0, eyes, brows=(), brow_dx=-6.0, squash=0.6):
    """chớp mắt kiểu Cừu cầm ô (đã duyệt 2 lần): mắt mở scaleX 100 -> squash trong 2 frame, đổi ảnh mắt nhắm (100%)
    giữ 2 frame, đổi lại mắt mở squash -> 100% trong 2 frame; lông mày dời brow_dx theo trục X của head (dọc mặt).
    eyes = [(slot, ảnh nhắm, ảnh mở, xương mắt)], brows = [xương mày]. Trả (bones, slots).
    Yêu cầu rig: xương mắt / mày rotation local 0 theo head, head dọc đường giữa mặt (X = dọc mặt)."""
    T = tfloor
    sc = [{"time": T(B0), "x": 1, "y": 1}, {"time": T(B0 + 2), "x": squash, "y": 1, "curve": "stepped"},
          {"time": T(B0 + 3), "x": 1, "y": 1, "curve": "stepped"}, {"time": T(B0 + 5), "x": squash, "y": 1},
          {"time": T(B0 + 7), "x": 1, "y": 1}]
    bones = {bone: {"scale": copy.deepcopy(sc)} for _, _, _, bone in eyes}
    slots = {s: {"attachment": [{"time": T(B0 + 3), "name": c}, {"time": T(B0 + 5), "name": o}]} for s, c, o, _ in eyes}
    dx = brow_dx
    br = [{"time": T(B0 - 1), "x": 0, "y": 0, "curve": [T(B0 - 1) + 0.0333, 0, T(B0 + 3) - 0.0333, dx,
                                                      T(B0 - 1) + 0.0333, 0, T(B0 + 3) - 0.0333, 0]},
          {"time": T(B0 + 3), "x": dx, "y": 0, "curve": "stepped"},
          {"time": T(B0 + 4), "x": dx, "y": 0, "curve": [T(B0 + 4) + 0.06, dx, T(B0 + 11) - 0.08, 0,
                                                        T(B0 + 4) + 0.06, 0, T(B0 + 11) - 0.08, 0]},
          {"time": T(B0 + 11), "x": 0, "y": 0}]
    for b in brows:
        bones[b] = {"translate": copy.deepcopy(br)}
    return bones, slots


def eyes_closed(e0, e1, eyes, brows=(), brow_dx=-6.0, squash=0.6):
    """nhắm mắt cười từ e0 tới e1 (active): bóp squash 2 frame -> mắt nhắm giữ -> mở squash -> 100% trong 2 frame."""
    T = tfloor
    sc = [{"time": T(e0 - 2), "x": 1, "y": 1}, {"time": T(e0), "x": squash, "y": 1, "curve": "stepped"},
          {"time": T(e0 + 1), "x": 1, "y": 1, "curve": "stepped"}, {"time": T(e1), "x": squash, "y": 1},
          {"time": T(e1 + 2), "x": 1, "y": 1}]
    bones = {bone: {"scale": copy.deepcopy(sc)} for _, _, _, bone in eyes}
    slots = {s: {"attachment": [{"time": T(e0 + 1), "name": c}, {"time": T(e1), "name": o}]} for s, c, o, _ in eyes}
    dx = brow_dx
    br = [{"time": T(e0 - 3), "x": 0, "y": 0, "curve": [T(e0 - 3) + 0.0333, 0, T(e0 + 1) - 0.0333, dx,
                                                      T(e0 - 3) + 0.0333, 0, T(e0 + 1) - 0.0333, 0]},
          {"time": T(e0 + 1), "x": dx, "y": 0, "curve": "stepped"},
          {"time": T(e1), "x": dx, "y": 0, "curve": [T(e1) + 0.06, dx, T(e1 + 7) - 0.08, 0, T(e1) + 0.06, 0, T(e1 + 7) - 0.08, 0]},
          {"time": T(e1 + 7), "x": 0, "y": 0}]
    for b in brows:
        bones[b] = {"translate": copy.deepcopy(br)}
    return bones, slots


# ---------------------------------------------------------------- rig: FK + quán tính
class Rig:
    def __init__(self, skel):
        self.B = {b["name"]: b for b in skel["bones"]}
        self.parent = {b["name"]: b.get("parent") for b in skel["bones"]}

    def fk(self, rot, tr):
        """FK 2D (xoay + dời, bỏ scale). rot(name, f) = độ thêm local; tr(name, f) = (dx, dy) local."""
        B = self.B

        def fk(name, f, cache):
            if name in cache:
                return cache[name]
            b = B[name]
            dx, dy = tr(name, f)
            lx, ly = b.get("x", 0) + dx, b.get("y", 0) + dy
            lr = b.get("rotation", 0) + rot(name, f)
            if b.get("parent"):
                px, py, pr = fk(b["parent"], f, cache)
                c, s_ = math.cos(math.radians(pr)), math.sin(math.radians(pr))
                w = (px + c * lx - s_ * ly, py + s_ * lx + c * ly, pr + lr)
            else:
                w = (lx, ly, lr)
            cache[name] = w
            return w
        return fk


class Inertia:
    """góc local idle theo giây (tuần hoàn T): sóng riêng OWN[b](t) + quán tính:
    gain * (góc thế giới của cha lúc t - trễ  -  lúc t) — xương con muốn giữ hướng cũ rồi đuổi theo cha."""
    def __init__(self, parent, own, inertia, T, lag_scale=1.0):
        self.parent, self.own, self.inertia, self.T, self.ls = parent, own, inertia, T, lag_scale
        self.memo = {}

    def local(self, b, t):
        key = (b, round(t % self.T, 6))
        if key in self.memo:
            return self.memo[key]
        v = self.own[b](t) if b in self.own else 0.0
        if b in self.inertia:
            g, lg = self.inertia[b]
            p = self.parent[b]
            v += g * (self.world(p, t - lg * self.ls / FPS) - self.world(p, t))
        self.memo[key] = v
        return v

    def world(self, b, t):
        tot = 0.0
        while b:
            tot += self.local(b, t)
            b = self.parent[b]
        return tot


# ---------------------------------------------------------------- physics chuỗi
class Chain:
    """chuỗi physics: mỗi đầu xương là chất điểm; lò xo (hz, zeta) kéo về dáng nghỉ (chuỗi cứng theo xương cha /
    đốt trước đã mô phỏng), lực gió / nước tuần hoàn theo loop (amp px/s², pha ph, hướng wdir), giữ chiều dài xương.
    Active: hz_act / zeta_act lúc nhảy (cứng hơn chống lật), lim = góc lệch tối đa so với dáng nghỉ (chặn mềm tanh).
    Giá trị đã duyệt (CuuSakura): khăn 0.9 Hz / 0.22 / gió 320; tai 1.3 / 0.3 / 60; chuông 1.3-1.5 / 0.22;
    vây 1.2 / 0.3 / nước 500; thân cừu (active) spine1 3.2 / 0.7, spine2 3.2 / 0.65, head 3.2 / 0.7."""
    def __init__(self, bones, hz, zeta, amp=0.0, ph=0.0, wdir=(1.0, 0.0), hz_act=None, zeta_act=None, lim=None):
        self.bones, self.hz, self.zeta, self.amp, self.ph, self.wdir = list(bones), hz, zeta, amp, ph, wdir
        self.hz_act = hz if hz_act is None else hz_act
        self.zeta_act = zeta if zeta_act is None else zeta_act
        self.lim = lim


class ChainSim:
    def __init__(self, rig, ch, n_wind, sub=8):
        self.ch, self.B, self.n, self.sub = ch, rig.B, n_wind, sub
        self.L = [self.B[b]["length"] for b in ch.bones]
        self.R = [self.B[b].get("rotation", 0) for b in ch.bones]
        self.b0 = self.B[ch.bones[0]]
        self.pts = None
        # góc nghỉ local thêm (cừu: dáng idle + đích); Chain có thể khai báo sẵn `rest(i, frame)` (vd chân đá nhẹ theo nhịp)
        self.rest = getattr(ch, "rest", None) or (lambda i, f: 0.0)

    def root(self, fk, f):
        px, py, pr = fk(self.b0["parent"], f, {})
        c, s_ = math.cos(math.radians(pr)), math.sin(math.radians(pr))
        b0 = self.b0
        return px + c * b0.get("x", 0) - s_ * b0.get("y", 0), py + s_ * b0.get("x", 0) + c * b0.get("y", 0), pr

    def init(self, fk, f=0):
        hx, hy, a = self.root(fk, f)
        self.pts = []
        for i in range(len(self.L)):
            a += self.R[i]; hx += self.L[i] * math.cos(math.radians(a)); hy += self.L[i] * math.sin(math.radians(a))
            self.pts.append([hx, hy, 0.0, 0.0])

    def force(self, f):
        amp, ph = self.ch.amp, self.ch.ph
        if not amp:
            return 0.0
        u = 2 * math.pi * f / self.n
        return amp * (math.sin(2 * u + ph) + 0.45 * math.sin(3 * u + 1.7 * ph) + 0.25 * math.sin(5 * u + 0.6 * ph))

    def step(self, fk, f, hz, zeta, dt):
        w0 = 2 * math.pi * hz
        hx, hy, pr = self.root(fk, f)
        g = self.force(f)
        wx, wy = self.ch.wdir
        prev, bse = (hx, hy), pr
        for i in range(len(self.L)):
            ta = bse + self.R[i] + self.rest(i, f)
            tx, ty = prev[0] + self.L[i] * math.cos(math.radians(ta)), prev[1] + self.L[i] * math.sin(math.radians(ta))
            p = self.pts[i]
            p[2] += (w0 * w0 * (tx - p[0]) - 2 * zeta * w0 * p[2] + g * wx) * dt
            p[3] += (w0 * w0 * (ty - p[1]) - 2 * zeta * w0 * p[3] + g * wy) * dt
            p[0] += p[2] * dt; p[1] += p[3] * dt
            dx, dy = p[0] - prev[0], p[1] - prev[1]; d = math.hypot(dx, dy) or 1.0
            p[0], p[1] = prev[0] + dx / d * self.L[i], prev[1] + dy / d * self.L[i]
            bse = math.degrees(math.atan2(dy, dx)); prev = (p[0], p[1])

    def read(self, fk, f):
        hx, hy, pr = self.root(fk, f)
        bse, prev, out = pr, (hx, hy), []
        for i in range(len(self.L)):
            wa = math.degrees(math.atan2(self.pts[i][1] - prev[1], self.pts[i][0] - prev[0]))
            out.append((wa - bse - self.R[i] + 180) % 360 - 180)
            bse, prev = wa, (self.pts[i][0], self.pts[i][1])
        return out


def simulate_loop(rig, chains, fk, N, cycles=5, sub=8):
    """idle: chạy (cycles - 1) vòng tới tuần hoàn rồi ghi vòng cuối (N + 1 frame), khép loop bằng cách chia đều phần
    lệch F0 / F N. Trả {xương: [độ thêm local theo frame]}."""
    out = {}
    dt = 1.0 / (FPS * sub)
    for ch in chains:
        s = ChainSim(rig, ch, N, sub)
        s.init(fk, 0)
        rec = {b: [] for b in ch.bones}
        for fr in range(cycles * N + 1):
            if fr:
                for k in range(sub):
                    s.step(fk, fr - 1 + (k + 1) / sub, ch.hz, ch.zeta, dt)
            if fr >= (cycles - 1) * N:
                for b, v in zip(ch.bones, s.read(fk, fr)):
                    rec[b].append(v)
        for b, v in rec.items():
            e = v[-1] - v[0]
            out[b] = [x - e * i / N for i, x in enumerate(v)]
    return out


# ---------------------------------------------------------------- file, lịch sử, mix
def load(path):
    return json.load(open(path, encoding="utf-8"))


def write_anim(path, name, anim, label=None, skel=None):
    """ghi một anim vào file skeleton, giữ mọi anim khác; cất bản trước vào lịch sử Hoàn tác của Spine Live."""
    skel = skel or load(path)
    skel.setdefault("animations", {})[name] = anim
    if not os.environ.get("ANIM_KIT_DRY"):
        try:
            sys.path.insert(0, TOOLS)
            import spine_live_cmd
            spine_live_cmd.claude_backup(path, label or f"Claude gen {name}")
        except Exception as e:
            print("(không ghi được backup Spine Live:", e, ")")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(skel, fh, indent=1, ensure_ascii=False)


def anim_len(a):
    t = 0.0
    for tl in list(a.get("bones", {}).values()) + list(a.get("slots", {}).values()):
        for keys in tl.values():
            for k in keys:
                t = max(t, k.get("time", 0.0))
    return t


def mix(skel, first, second, name, t_first=None):
    """anim `name` = `first` rồi `second` dời t_first (second phải bắt đầu đúng F0 của first, vd active sau idle).
    Kênh thiếu ở một bên = giữ tư thế setup ở phần đó. Ghi vào skel['animations'][name]."""
    A = skel["animations"]
    a, b = A[first], A[second]
    T = t_first if t_first is not None else anim_len(a)
    eps = 1e-4
    setup = {"translate": {"x": 0, "y": 0}, "scale": {"x": 1, "y": 1}, "shear": {"x": 0, "y": 0}}

    def shift(keys, dt):
        out = []
        for k in keys:
            k = copy.deepcopy(k)
            k["time"] = round(k.get("time", 0.0) + dt, 4)
            c = k.get("curve")
            if isinstance(c, list):
                k["curve"] = [round(v + dt, 4) if i % 2 == 0 else v for i, v in enumerate(c)]
            out.append(k)
        return out

    def join(ak, bk, kind):
        ak = ak or [dict(time=0.0, **setup.get(kind, {"value": 0}))]
        bk = bk or [dict(time=0.0, **setup.get(kind, {"value": 0}))]
        head = [copy.deepcopy(k) for k in ak if k.get("time", 0.0) < T - eps]
        if head and head[0].get("time") == 0:
            del head[0]["time"]
        return head + shift(bk, T)

    bones = {}
    for bn in sorted(set(a.get("bones", {})) | set(b.get("bones", {}))):
        ab, bb = a["bones"].get(bn, {}), b["bones"].get(bn, {})
        bones[bn] = {kind: join(ab.get(kind), bb.get(kind), kind) for kind in sorted(set(ab) | set(bb))}
    slots = {}
    for s in sorted(set(a.get("slots", {})) | set(b.get("slots", {}))):
        asl, bsl = a.get("slots", {}).get(s, {}), b.get("slots", {}).get(s, {})
        slots[s] = {kind: [copy.deepcopy(k) for k in asl.get(kind, []) if k.get("time", 0.0) < T - eps] + shift(bsl.get(kind, []), T)
                    for kind in set(asl) | set(bsl)}
    A[name] = {"bones": bones, "slots": slots}
    return A[name]


def user_edits(json_path, anim):
    """sổ sửa tay của người dùng trên Spine Live cho file này: keypose đã key (keyed.json) + lần ghi gần nhất trong
    lịch sử Hoàn tác. Gọi TRƯỚC khi dựng lại một anim: có sửa tay mới thì chép key đó vào file key người dùng
    (vd active_user_keys.json) rồi mới dựng, không thì sẽ đè mất (lỗi CuuSakura 2026-11-02 14:45 và 14:55)."""
    root = os.path.abspath(os.path.join(TOOLS, ".."))
    rel = os.path.relpath(os.path.abspath(json_path), root).replace("\\", "/")
    out = {"keyposes": [], "history": []}
    try:
        kd = load(os.path.join(root, "work/store/_sys/spine_live/keyed.json"))
        out["keyposes"] = [(e["frame"], e["bones"], e["t"]) for e in kd.get(rel, {}).get(anim, [])]
    except (OSError, ValueError):
        pass
    try:
        lg = load(os.path.join(root, "work/store/_sys/spine_live/backup", rel.replace("/", "__") + ".log.json"))
        out["history"] = [(e["t"], e.get("who"), e["what"]) for e in lg]
    except (OSError, ValueError):
        pass
    last_claude = max((t for t, w, _ in out["history"] if w == "claude"), default="")
    out["user_since_claude"] = [(t, x) for t, w, x in out["history"] if w == "user" and t > last_claude]
    return out
