# Hạt — kiến trúc, lực, và cách đưa sang Unity

## 1. `lib/particles.py`

```python
import particles as px, fxlib as fx
s = px.System(seed, [px.drag(3), px.gravity(0, 260)], ground=None, trail=0)
s.burst(16, angle=(0, 360), even=True, speed=(170, 280), life=(0.16, 0.3), size=(1.6, 2.4))
s.on_death = lambda s, idx: ...          # sub-emitter
s.update(dt)                              # mỗi bước (render gọi ở 120 Hz)
s.draw(cv, mode="streak", ramp=R, heat_curve=lambda u: u, size_curve=fx.Curve([(0, 1), (1, 0)]),
       length_scale=3, speed_scale=0.045, glow=(3, 0.35))
```

| Thành phần | Nguồn | Ghi chú |
|---|---|---|
| SoA numpy, `mem` 8 số ngẫu nhiên / hạt | three.quarks GeneratorMemory, Godot hash | "random giữa 2 curve" giữ nguyên hệ số suốt đời |
| `burst(even=True)` | pixi burst đều | hình toả cân, không thủng một phía |
| `burst(shape="circle"/"disc", radius)` | Unity Shape module | |
| `drag(k)`: `v /= 1 + k·dt` | LÖVE | ổn định mọi dt |
| `gravity(gx, gy)` | | y-xuống: gy > 0 rơi, < 0 nổi |
| `radial(a, tangential)` | LÖVE / Godot | |
| `vortex(speed, pull, k)` | Effekseer | **lái** về vận tốc đích → không nổ ở fps thấp |
| `attractor(x, y, force, R)` | Proton | suy giảm (1 − d²/R²) |
| `curl(scale, influence)` | Godot | trộn hướng về curl, giữ |v| |
| `limit_speed(vmax)` | three.quarks | vmax có thể là Curve theo tuổi |
| `wander(amount)` | | noise riêng từng hạt |
| `draw(mode="streak")` | three.quarks = Unity | đầu ở hạt, kéo ngược hướng bay, dài = size·length_scale + |v|·speed_scale |
| `draw(mode="trail")` với `System(trail=n)` | three.quarks trail | thon về đuôi |
| `loop_phase_ages` | Pixel FX Forge | hạt loop liền: đời = chu kỳ, sinh đều theo pha |

Chưa có (ý tưởng từ deepnight HParticle): ma sát riêng x/y, scale có vận tốc + ma sát, xoay theo hướng bay, squash pop, alpha nhấp nháy. Thêm khi effect cần.

`core.Particles` (6 loại có lực chỉnh sẵn: spark, grit, ember, mote, smoke, twinkle) vẫn dùng được cho effect đơn giản.

## 2. Nhịp (pixelfx / RetroImpacts / minerva)

- Hero trắng 1–2 frame → overshoot → về, mảnh lại, tụt bậc màu → toả → giữ (chi tiết trễ 0.08–0.3 s) → tắt.
- Đòn 0.3–0.8 s; khói / bụi 1–1.5 s. **Đòn một lần kết thúc trống**: tuổi thọ lớn nhất + sub-emitter < duration.
- Năng lượng đòn: `stylize.env_punch`. Vòng / mảnh bay: `stylize.drag_travel`.

## 3. Đưa sang Unity (Shuriken) — bài học từ officina-vfx-tool và three.quarks

Builder của skill: `assets/VfxCodeBuild.cs` (1 particle chạy cả flipbook). Khi mở rộng sang dựng hạt Shuriken từ recipe:

1. **Recipe hai tầng**: Python mở rộng đường tắt, đơn vị, palette, mặc định thành bản đầy đủ; C# **chỉ ánh xạ 1-1, không tự đoán mặc định**.
2. Giá trị = đúng 4 kiểu MinMaxCurve của Unity: `0.3` · `{"random": [a, b]}` · `{"curve": [[t, v]…], "mult"}` · `{"random_curve": [c1, c2]}`. Curve dựng **tangent tuyến tính** (tangent phẳng làm flipbook khựng ở đầu — lỗi dự án đã gặp).
3. Bẫy màu: gradient `Fixed` của Unity lấy key **sau** t → lệch một key (dời mỗi key sang thời điểm key kế). `startColor × colorOverLifetime` nhân nhau → màu ở startColor, gradient chỉ giữ alpha.
4. `randomSeed = seed + layerIndex`, `useAutoRandomSeed = false` → preview tái tạo được, A/B trong Review Lab có nghĩa.
5. Module không hỗ trợ → **báo lỗi to**, không lặng lẽ bỏ.
6. Sửa theo góp ý = patch theo **tên layer**, không theo chỉ số mảng; tối đa 4 vòng, vòng kém hơn thì quay lại bản tốt nhất.
7. Đo sau build (bảng triệu chứng officina): `empty / offscreen / too_dense / too_short / lingers / off_palette / lopsided / too_bright` → mỗi triệu chứng chỉ ra thông số cần xem trước. `core.check` đã có: tràn mép, chưa tắt, loop giật, không tất định.
8. Sub-emitter theo tên: `{on: birth|death|collision, child: "LayerName", inherit: [...], probability}`.

## 4. Đóng gói flipbook

- Frame 0 ở **trên-trái** (quy ước TextureSheetAnimation). Đệm 2–4 px mỗi ô nếu có mip / bilinear (VFXToolbox FixBorders).
- Loop 8 frame 4×2, một lần 16 frame 4×4 (quy ước art lead). Sheet ≤ 1024 px.
- Xám một kênh: có thể xếp 4 flipbook vào RGBA (flipbook-packer "Super / Stagger") — chưa dùng trong dự án.
