"""fluid: mô phỏng khói / lửa 2D bằng numpy (Jos Stam "Stable Fluids" 1999, cách làm của
PavelDoGreat/WebGL-Fluid-Simulation và GregTJ/stable-fluids), dùng để NƯỚNG flipbook.

Một bước:  thêm lực (nổi nhiệt, nguồn) → xoáy (vorticity confinement) → advect vận tốc
           → chiếu áp suất (Jacobi) → advect mật độ / nhiệt → tiêu tán.

Lưới mặc định 128×128, ~3–6 ms/bước trên CPU. Hướng y của lưới: hàng 0 ở TRÊN (giống ảnh),
nên "bay lên" = vy âm.

Để ra toon: KHÔNG xuất mật độ thô. Đem density / temperature qua fxlib.posterize / ramp_hard,
hoặc dùng làm `noise` đứng yên cho dissolve. Muốn loop: chạy mô phỏng dài, cắt 1 đoạn rồi
crossfade đầu–cuối (loop_crossfade).
"""
import numpy as np


def _bilerp(f, x, y):
    """Lấy mẫu song tuyến f tại toạ độ pixel thực (x cột, y hàng), kẹp biên."""
    H, W = f.shape
    x = np.clip(x, 0, W - 1.001)
    y = np.clip(y, 0, H - 1.001)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    a = f[y0, x0] * (1 - fx) + f[y0, x0 + 1] * fx
    b = f[y0 + 1, x0] * (1 - fx) + f[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


class Fluid:
    # Thông số đã thử (lưới 128, dt 1): buoy 0.08–0.12, vort 0.2–0.8. vort > ~2 hoặc nguồn tmp > 0.2/bước
    # → nổ số (vận tốc tăng vô hạn). Nguồn: splat den 0.1–0.15, tmp 0.1–0.15 mỗi bước trong ~20 bước.
    def __init__(self, w=128, h=128, iters=24, vort=0.5, buoy=0.1, cool=0.6, vel_diss=0.15, den_diss=0.25, vmax=6.0):
        self.W, self.H = w, h
        self.vx = np.zeros((h, w))
        self.vy = np.zeros((h, w))
        self.den = np.zeros((h, w))
        self.tmp = np.zeros((h, w))
        self.iters, self.vort, self.buoy, self.cool = iters, vort, buoy, cool
        self.vel_diss, self.den_diss, self.vmax = vel_diss, den_diss, vmax
        self.gx, self.gy = np.meshgrid(np.arange(w, dtype=float), np.arange(h, dtype=float))

    # -- nguồn: splat Gauss (cách WebGL-Fluid-Simulation)
    def splat(self, cx, cy, r, den=0.0, tmp=0.0, vx=0.0, vy=0.0):
        g = np.exp(-((self.gx - cx) ** 2 + (self.gy - cy) ** 2) / (r * r))
        self.den += den * g
        self.tmp += tmp * g
        self.vx += vx * g
        self.vy += vy * g

    def advect(self, f, dt):
        """Semi-Lagrangian: lần ngược theo vận tốc rồi lấy mẫu. Ổn định với mọi dt."""
        return _bilerp(f, self.gx - self.vx * dt, self.gy - self.vy * dt)

    def _curl(self):
        dvy_dx = (np.roll(self.vy, -1, 1) - np.roll(self.vy, 1, 1)) * 0.5
        dvx_dy = (np.roll(self.vx, -1, 0) - np.roll(self.vx, 1, 0)) * 0.5
        return dvy_dx - dvx_dy

    def vorticity(self, dt):
        """Vorticity confinement (Fedkiw 2001): đẩy lại xoáy nhỏ mà advection làm mất → khói có cuộn."""
        w = self._curl()
        aw = np.abs(w)
        nx = (np.roll(aw, -1, 1) - np.roll(aw, 1, 1)) * 0.5
        ny = (np.roll(aw, -1, 0) - np.roll(aw, 1, 0)) * 0.5
        l = np.sqrt(nx * nx + ny * ny) + 1e-5
        nx, ny = nx / l, ny / l
        self.vx += self.vort * (ny * w) * dt
        self.vy += self.vort * (-nx * w) * dt

    def project(self):
        """Chiếu áp suất: giải ∇²p = ∇·v bằng Jacobi rồi v -= ∇p → không nén (khói cuộn, không phình loang)."""
        div = 0.5 * (np.roll(self.vx, -1, 1) - np.roll(self.vx, 1, 1) + np.roll(self.vy, -1, 0) - np.roll(self.vy, 1, 0))
        p = np.zeros_like(div)
        for _ in range(self.iters):
            p = (np.roll(p, 1, 0) + np.roll(p, -1, 0) + np.roll(p, 1, 1) + np.roll(p, -1, 1) - div) * 0.25
        self.vx -= 0.5 * (np.roll(p, -1, 1) - np.roll(p, 1, 1))
        self.vy -= 0.5 * (np.roll(p, -1, 0) - np.roll(p, 1, 0))
        # biên kín: vận tốc 0 ở 1 px ngoài cùng (np.roll là tuần hoàn → chặn khói vòng sang mép kia)
        for f in (self.vx, self.vy):
            f[0, :] = f[-1, :] = 0
            f[:, 0] = f[:, -1] = 0

    def step(self, dt=1.0):
        self.vy -= self.buoy * self.tmp * dt              # nổi: nóng bay lên (y âm)
        if self.vort:
            self.vorticity(dt)
        self.project()
        vx, vy = self.advect(self.vx, dt), self.advect(self.vy, dt)
        self.vx, self.vy = np.clip(vx, -self.vmax, self.vmax), np.clip(vy, -self.vmax, self.vmax)  # chặn nổ số
        self.project()
        self.den = self.advect(self.den, dt)
        self.tmp = self.advect(self.tmp, dt)
        self.vx *= 1 - self.vel_diss * dt * 0.05
        self.vy *= 1 - self.vel_diss * dt * 0.05
        self.den *= 1 - self.den_diss * dt * 0.05
        self.tmp *= 1 - self.cool * dt * 0.05


def loop_crossfade(frames, overlap):
    """Biến chuỗi frame thành loop liền: trộn `overlap` frame cuối vào đầu (cách Houdini/EmberGen loop).
    frames: list mảng cùng kích thước. Trả list mới dài len - overlap."""
    n = len(frames)
    out = [f.copy() for f in frames[: n - overlap]]
    for i in range(overlap):
        k = (i + 1) / (overlap + 1)
        out[i] = frames[n - overlap + i] * (1 - k) + frames[i] * k
    return out


def loop_sync(frames, n, sync=None):
    """Loop kiểu VFXToolbox LoopingProcessor (Unity): chọn frame đồng bộ S, xuất n frame,
    out[i] = lerp(in[S+i], in[S-(n-i)], cong_S(i/n)), cong_S đi từ (0.25, 0) tới (0.75, 1).
    Cần mô phỏng đã ổn định (nguồn liên tục) và len(frames) >= 2n."""
    S = len(frames) - n if sync is None else sync
    assert S - n >= 0 and S + n <= len(frames), "cần ít nhất 2n frame quanh frame đồng bộ"
    out = []
    for i in range(n):
        x = i / n
        k = min(max((x - 0.25) / 0.5, 0.0), 1.0)
        k = k * k * (3 - 2 * k)
        out.append(frames[S + i] * (1 - k) + frames[S - (n - i)] * k)
    return out


def motion_vectors(F, dt_between, steps_per_frame=1):
    """Motion vector CHÍNH XÁC từ vận tốc mô phỏng (không cần optical flow như MotionFrame / Farneback):
    độ dời pixel giữa 2 frame nướng ≈ v · số bước. Trả (mx, my) theo pixel lưới; mã hoá cho Unity:
    rg = mv / strength * 0.5 + 0.5, texture LINEAR (không sRGB). Shader blend: references/shaders.md §MV."""
    return F.vx * dt_between * steps_per_frame, F.vy * dt_between * steps_per_frame
