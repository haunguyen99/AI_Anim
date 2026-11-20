# Quy tắc shader mobile (bắt buộc cho mọi shader của skill)

**Phạm vi:** áp cho shader **mới viết** (`SH_VFX_*`). Bộ Coloso và shader nhập từ rpg-game (`Assets/VFX/_Imported/`) có nhiều sample hơn; dùng chúng theo [coloso.md](coloso.md), không sửa cho khớp bảng này.

Mục tiêu: một shader nhẹ, đơn giản, đọc được; chạy cả Built-in và URP trong cùng file.

## Cấu trúc

- Một Pass unlit, **không** đặt `LightMode`. Built-in vẽ nó ở forward, URP vẽ như SRPDefaultUnlit.
- Chỉ dùng `CGPROGRAM` + `UnityCG.cginc` + `VfxShaderLib.cginc`. **Không include file của URP**, để shader vẫn compile trong project Built-in. Không tương thích SRP Batcher là chấp nhận được với VFX.
- `#pragma target 2.0` khi đủ; chỉ lên 3.0 khi cần (ví dụ nhiều interpolator, đạo hàm `ddx/ddy`).
- Blend qua `[Enum] _SrcBlend/_DstBlend`: Additive = SrcAlpha/One, Alpha = SrcAlpha/OneMinusSrcAlpha. `ZWrite Off`, `Cull Off` cho quad.
- Tính năng tuỳ chọn dùng `#pragma shader_feature_local`, không dùng `multi_compile` (tránh nổ số biến thể). Tối đa ~3 keyword mỗi shader.
- Path menu: `VFX/FX/<Name>`; file: `Assets/VFX/_Shared/Shaders/SH_VFX_<Name>.shader`.

## Ngân sách mỗi pixel (mặc định)

| Hạng mục | Giới hạn |
|---|---|
| Texture sample | ≤ 3 (noise dùng chung, gói 2 noise vào R và G để 1 sample lấy 2 giá trị) |
| Hàm đắt (`atan2`, `pow`, `sin/cos`, `exp`, `log`) | 0 trong fragment nếu tránh được; tối đa 1 khi hình bắt buộc cần (ví dụ góc xoáy dùng `atan2`) |
| Vòng lặp, `if` phụ thuộc dữ liệu | Không. Dùng `lerp/step/smoothstep` |
| `discard` / `clip` | Không, trừ khi cần ghi depth. Alpha test tốn trên GPU tile-based |
| Interpolator | ≤ 4 `float4` |

Đưa mọi thứ không đổi theo pixel lên **vertex shader**: UV cuộn theo thời gian, sin/cos của góc xoay theo particle, seed.

## Kiểu dữ liệu

- `half` cho màu, alpha, giá trị 0..1; `float` cho UV, vị trí, thời gian (`_Time.y` lớn dần, `half` sẽ mất chính xác sau vài phút).
- Không dựng noise bằng toán (value/perlin/simplex) trong fragment: **đọc texture noise dùng chung** rẻ hơn trên mobile.

## Overdraw (chi phí lớn nhất của VFX mobile)

- Quad càng sát hình càng tốt: chỉnh size particle và `_Radius` để ít pixel trong suốt.
- Ít lớp chồng; một shader làm nhiều việc trong một quad rẻ hơn ba quad chồng nhau.
- Additive không cần sort; alpha blend chồng nhiều lớp to là đắt nhất.

## Màu và texture (project Linear color space)

- Thuộc tính `Color` thường được Unity tự chuyển sang linear. Màu `[HDR]` thì không được chuyển, nên nếu thấy sai sáng thì áp `GammaToLinearSpace` như shader lửa cũ.
- Texture noise/mask là **dữ liệu**: tắt sRGB, wrap Repeat (`ImportNoise` trong build template làm việc này).
- Màu HDR bị cắt về 1 khi bake ra PNG.

## Dữ liệu từ particle

- Vertex color = tint × alpha (Start Color, Color over Lifetime).
- Custom1.x = progress 0..1 theo tuổi particle, Custom1.y = seed ngẫu nhiên → TEXCOORD0.zw. Bật bằng `FxProgress()` trong build template.
- Không giả định Custom1 luôn là dissolve: đọc lại shader có sẵn xem nó đọc stream nào.

## Kiểm tra trước khi giao

- Không lỗi compile (BuildReport / Console). Material không hồng.
- Đếm lại sample và hàm đắt trong fragment; ghi vào header shader dòng `// Cost:`.
- Preview sheet đúng hình ở các mốc thời gian, kết thúc sạch (progress = 1 không còn pixel sáng).
