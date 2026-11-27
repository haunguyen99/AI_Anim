# Bảng kỹ thuật — chọn công cụ theo loại effect

Toạ độ: x phải, **y xuống**, (0, 0) = `origin`, đơn vị local (1 = 1 px ở `--res 1`).
Mọi hàm nhận mảng numpy `X, Y` (lấy từ `cv.shade(...)` hoặc `fxlib.grid`).

## 1. Chọn theo loại effect

| Effect | Kỹ thuật chính | Hàm | Mẫu |
|---|---|---|---|
| Vòng / sóng xung kích | toạ độ cực + dải `|r − R(t)|` + noise theo góc **có chu kỳ** + ngưỡng tan | `polar`, `fbm(period=)`, `Equalizer`, `dissolve`, `drag_travel` | `shockwave_ground.py` |
| Tia lửa / mảnh văng | hạt burst đều + drag + trọng lực, stretched billboard, sub-emitter | `particles.System`, `drag`, `gravity`, `draw(mode="streak")` | `spark_burst.py` |
| Sét / điện | chia đôi đoạn + nhánh, đổi hình mỗi 2 frame (`stepped`) | `bolt` | `lightning_arc.py` |
| Cột khói / hơi / bụi cuộn | mô phỏng chất lỏng → làm mờ → cắt ngưỡng → 2 tông theo gradient | `fluid.Fluid`, `box_blur`, `cov_field` | `fluid_plume.py` |
| Nổ / quả cầu lửa | cụm metaball có nhiệt lồng trong viền, ngưỡng tăng muộn; hoặc `fireball` | `stylize.puff_cluster`, `field_bands`, `carve` | — |
| Ngọn lửa loop | gradient dọc × noise 3D có chu kỳ thời gian → ngưỡng → ramp bậc cứng | `fire_mask(period_t=)`, `ramp_hard` | — |
| Lửa pixel / retro | automaton Doom | `doom_fire` | — |
| Vệt chém (texture) | cực: đầu out_cubic, đuôi smoothstep, mũi thon | `stylize.slash_arc` | — (dự án: vệt chém = mesh + UV) |
| Sao / tia toả | SDF sao, `rep_polar` lặp 1 tia thành n tia | `sd_star`, `rep_polar`, `sd_segment` | — |
| Phép / cổng / xoáy | domain warp, curl noise cho hạt, vortex lái | `warp`, `curl2`, `particles.vortex/curl` | — |
| Vết nứt / vảy / tế bào | voronoi F2 − F1 | `voronoi` | — |
| Biến mất kiểu retro | bayer / block / scan / circles | `stylize.dissolve_mask` | — |

## 2. Noise

| Hàm | Dùng khi | Lưu ý |
|---|---|---|
| `perlin2(x, y, seed, period=(px, py))` | mọi thứ; `period` số ô nguyên → **tile liền** | ~[-1, 1] |
| `perlin3(x, y, z, period=(…, pz))` | **loop theo thời gian**: `z = t/T·pz` (pz nguyên) | cách của keijiro periodic Perlin / psrdnoise |
| `fbm(..., octaves, z=, period=)` | mảng lớn + chi tiết | phân bố dồn quanh 0 → dùng `Equalizer` trước khi làm ngưỡng |
| `ridged` | gân sắc: điện, nứt, nước | **không** dùng cho thân khói (ra mặt đá — art lead đã loại) |
| `voronoi` → (F1, F2, id) | F2−F1 viền ô; F1 chấm tròn; id màu từng ô | |
| `curl2` | trường vận tốc không phân kỳ cho hạt | hạt cuộn, không tụ cục |
| `warp(x, y, amp, freq)` | lửa phép, khói hoa văn, chảy | IQ: q → r → f; đắt, chỉ offline |
| `Equalizer(sample)` / `fbm_equalizer(seed)` | đưa noise về phân bố đều 0..1 | **dựng một lần**, không tính lại mỗi frame |

## 3. SDF 2D (IQ / hg_sdf viết lại) — âm = bên trong

`sd_circle`, `sd_box(r=bo góc)`, `sd_segment` (capsule thon r0 → r1, trả cả h 0..1), `sd_ring`, `sd_arc`, `sd_star(n, m)`, `sd_tri`, `sd_vesica` (lá / lưỡi lửa).
Phép: `op_union` min · `op_sub` max(a, −b) · `op_inter` max · **`op_smin(a, b, k)`** hợp mềm (thuỳ khói dính thân) · `op_onion` thành viền · `op_round` · `rep_polar(n)` lặp góc.
Phủ: `cov(d, px)` mép 1 px · `cov_field(f)` mép 1 px theo gradient (trường bất kỳ).

## 4. Màu toon

| Hàm | Ý |
|---|---|
| `ramp_hard(ramp, v)` | **thân**: bậc cứng (`core.at`) |
| `ramp_soft(ramp, v)` | chỉ lớp sáng |
| `posterize(v, n)`, `bands(v, edges, soft)` | lượng tử hoá / toon band |
| `stylize.field_bands(E, heat, n)` | một trường → độ phủ + chỉ số bậc (viền và tông đi cùng nhau) |
| `outline(alpha, px)`, `stylize.id_edges(ids)` | viền ngoài; nét giữa các khối chồng nhau |
| `palette_cos` | palette cosine IQ — nháp nhanh / lớp sáng |

## 5. Tan / ăn mòn

| Hàm | Kiểu |
|---|---|
| `dissolve(alpha, noise, t, soft, edge)` | ngưỡng + dải mềm theo **đơn vị noise** + mặt nạ mép cháy |
| `erosion(alpha, noise, p, sharp)` | **công thức NovaShader** — trùng với shader realtime (shaders.md §1), p 0 → 1 luôn đi từ nguyên tới mất hết |
| `wipe(shape, grad, p, width)` | quét dải theo kênh gradient (GDQuest blast) |
| `stylize.dissolve_mask(kind, …)` | bayer / block / scan / edge / circles |
| `stylize.keep_components(mask, n, root_row)` | dọn chấm lẻ sau khi tan |

Luật (rút từ các thư viện + góp ý art lead):
- noise **đứng yên** trên bề mặt; chỉ ngưỡng thay đổi → chỗ đã tan không đặc lại;
- ngưỡng phải đi tới > 1 + soft ở cuối, nếu không `--check` báo "chưa tắt hẳn";
- tần số noise thấp → vỡ thành mảng lớn (toon); cao → lấm tấm (thường sai).

## 6. Thời gian

`core.ease.*`, `seg`, `smooth`, `bump`; thêm:
- `fxlib.Curve(keys, mode)` — key tuyến tính / Catmull-Rom; `Gradient(keys, hard)`; `MinMax(a, b)` giữa 2 hằng / 2 curve theo số ngẫu nhiên riêng của hạt;
- `stylize.drag_travel(age, K)` — bắn nhanh rồi phanh, chuẩn hoá về 1;
- `stylize.env_punch(t)` — năng lượng đòn fighting game;
- `stepped=True` trong META + `floor(t·30) // hold` — nhịp anime "on 2s".

## 7. Loop liền

1. Noise có chu kỳ: `perlin3(..., z=t/T·P, period=(…, P))`.
2. Tần số thời gian nguyên: `sin(2π·k·t/T)` với k nguyên.
3. Hạt: `particles.loop_phase_ages` (sinh đều theo pha, đời hạt = chu kỳ).
4. Mô phỏng: chạy ổn định ≥ 2n frame rồi `fluid.loop_sync` (VFXToolbox) — đường lui, mất tương phản ở giữa.
5. `--check` đo chỗ nối; effect kiểu nhịp (sét) thì đặt `stepped=True`.
