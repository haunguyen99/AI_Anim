# Công thức shader realtime (Unity Built-in + URP, mobile)

Trước khi viết shader: đọc `Docs/VFX/SHADERS.md` (sổ đăng ký) và `Assets/VFX/_Shared/Shaders/VfxShaderLib.cginc`.
Thư viện dự án **đã có**: `vfxCentered`, `vfxRotate`, `vfxPolar`, `vfxSdCircle/Ring/Box/Segment`, `vfxFill`, `vfxBand`, `vfxDissolve`, `vfxEaseOut`, `vfxLifeFade`. Đừng viết lại.
Dưới đây là phần **mới** rút từ NovaShader, GDQuest, aki-null, Cyanilux. Thêm vào `VfxShaderLib.cginc` thì chỉ **thêm hàm mới**, không đổi hàm cũ, rồi ghi vào `SHADERS.md`.

Nguyên tắc chung cho mọi công thức: **thời gian nằm ở particle** (Custom1.x, vertex alpha, curve), shader chỉ giữ thông số hình (art lead 2026-11-03, xem shader `VFX/FX/Smoke Mesh`).

## 1. Alpha erosion có remap (NovaShader, MIT)

Vấn đề của `clip(noise - p)` thường: p = 0 vẫn mất pixel noise = 0, p = 1 vẫn còn pixel noise = 1 khi có dải mềm.

```hlsl
// p: 0 nguyên vẹn → 1 mất hết. Lấy từ Custom1.x, hoặc 1 - vertexColor.a (Color over Lifetime alpha thành ăn mòn).
inline half vfxErosion(half noise, half p, half sharp)   // sharp 0..1
{
    half w  = lerp(0.5h, 1e-4h, sharp);
    half pp = lerp(-w, 1.0h + w, p);
    return smoothstep(pp - w, pp + w, noise);
}
// Mép cháy: dải ngay trong ngưỡng
inline half vfxBurnEdge(half noise, half p, half width)
{
    return step(noise, p + width) - step(noise, p);
}
```
Python cùng công thức: `fxlib.erosion` → flipbook nướng và shader realtime cho kết quả giống nhau.
Noise mặc định dự án: `T_Noise_Smooth|Cells|Streaks` (R + G), linear, Repeat.

## 2. Ramp toon bằng texture (Nova emission color map)

```hlsl
// _RampTex: 256×1 (hoặc 64×1), Filter = Point → bậc cứng. Clamp.
half3 col = tex2D(_RampTex, float2(v, 0.5)).rgb;
// Nova chừa biên ~1/256: chỉ cộng ramp khi a > 0.004 — nén texture làm lệch giá trị.
```
Lợi: **một flipbook xám** đổi được mọi bảng màu (đổi nguyên tố chỉ đổi ramp). Python xuất ramp: `fxlib.ramp_hard` trên `np.linspace(0, 1, 256)`.

## 3. Quét gradient (GDQuest blast, MIT)

Texture 2 kênh: R = hình, G = gradient quét (0 → 1 theo hướng hiện). Một progress điều khiển vệt chém hiện dần, vòng nở, quét theo hướng.
```hlsl
half g    = (2.0h * _W + 1.0h) * p - _W;
half mask = smoothstep(0.0h, 1.0h, saturate(abs(t.g - g) / _W * 2.0h));
half a    = saturate(t.r - mask);
```
Python: `fxlib.wipe(shape, grad, p, width)`. Dự án: vệt chém dùng mesh + UV — kênh G = U của mesh.

## 4. UV cuộn + méo / flowmap (Nova)

```hlsl
float2 flow = (tex2D(_FlowTex, uv * _FlowScale + _Time.y * _FlowSpeed).rg * 2.0 - 1.0) * _FlowStrength;
half4 c = tex2D(_MainTex, uv + flow);
// 2 lớp noise cuộn ngược chiều nhân nhau → giấu lặp. Độ méo theo Custom1.y nếu cần riêng từng hạt.
```
Rẻ (1 sample thêm). Không dùng `atan2` mỗi pixel trên mobile: vòng thì dùng **mesh vòng có UV.x = góc** hoặc texture UV cực nướng sẵn.

## 5. Flipbook blend bằng motion vector (aki-null UnityFlipbookMotionBlending, MIT)

Ít frame (16) mà chuyển động mượt như 64. Texture MV: `rg = mv / strength * 0.5 + 0.5`, import **Linear (không sRGB)**, không nén mạnh.
```hlsl
float  f  = frac(frameTime);                       // frameTime = Frame over Time × số frame
float2 mA = (tex2D(_MV, uvA).rg * 2 - 1) * _MVStrength;
float2 mB = (tex2D(_MV, uvB).rg * 2 - 1) * _MVStrength;
half4  A  = tex2D(_MainTex, uvA - mA * f);
half4  B  = tex2D(_MainTex, uvB + mB * (1 - f));
half4  c  = lerp(A, B, f);
```
- uvA/uvB = ô frame hiện tại / kế tiếp. Unity: Texture Sheet Animation + Custom Vertex Streams `UV2` + `AnimBlend`.
- MV từ mô phỏng: `fluid.motion_vectors` (chính xác, khỏi optical flow). Từ hình vẽ code: tự tính (vận tốc hạt / đạo hàm theo t của hình). Từ ảnh bất kỳ: Farneback (MotionFrame).
- Dãn MV ra ngoài mép hình vài px, nếu không mép bị kéo rách.
- **Chưa dựng trong dự án** — cần shader mới + kiểm tra trên máy.

## 6. Quả nổ trên mesh cầu (GDQuest explosion, MIT)

- Vertex: phóng theo `curve(time)`, đẩy theo pháp tuyến bằng noise.
- Fragment: `fire = noise·fresnel + 0.2·fresnel`; màu `lerp(smoke, emission, smoothstep(fv − s, fv + s, fire))` với `fv = 1 − fireCurve(t)`; alpha = `smoothstep(ev − s, ev + s, erosionNoise·fresnel)`.
- Lệch pha từng hạt: vertex color R/G dời time và UV noise.
- Hợp **mesh particle, Render Alignment View** như `VFX/FX/Smoke Mesh`.

## 7. Sét bằng shader (Unity3D-Lightning-Shader)

Chia đoạn N = 8–10, lệch khớp theo `hash(i, floor(time·fps/2))` (đổi hình mỗi 2 frame), khoảng cách = min các `vfxSdSegment`.
Toon: lõi `step(d, w)`, quầng `step(d, 3w)`. Rẻ khi N nhỏ; sét phức tạp thì nướng flipbook (`fxlib.bolt`).

Bản đã dùng trong project (rẻ hơn, không cần min nhiều đoạn): value noise tuyến tính từ hash = đường gấp khúc, khoảng cách `|y − off|·rsqrt(1 + slope²)`, ghim đầu bằng `u(1−u)`. Xem [electric-bolt.md](electric-bolt.md) và `assets/shaders/SH_VFX_ElectricBolt.shader`.

## 8. Mobile — chi phí

- `half` cho màu / mask; `shader_feature_local` cho tính năng tuỳ chọn.
- Additive + ZWrite Off → ít overdraw nhất. Soft particle cần depth texture: tắt trên máy yếu.
- Noise nướng thành texture; tránh `atan2/pow/sin` mỗi pixel. Đắt quá thì nướng cả shader ra flipbook bằng **Cyanilux/BakeShader** (MIT, `_Slice` 0 → 1).
- Palette cosine `a + b·cos(2π(c·t + d))` thay ramp texture khi bottleneck là sample.
