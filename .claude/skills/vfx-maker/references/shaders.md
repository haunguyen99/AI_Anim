# Shader

**Ưu tiên shader có sẵn.** Chỉ viết shader mới khi cần tính năng shader chuẩn không có (dissolve, UV scroll, màu viền, dùng kênh R làm alpha...). Nêu lý do trong kế hoạch.

## Shader có sẵn theo pipeline

`VfxBuildKit.Material(path, blend, texture)` tự chọn shader và cấu hình blend:

| Blend | Built-in | URP |
|---|---|---|
| Additive | `Mobile/Particles/Additive` | `Universal Render Pipeline/Particles/Unlit` (Blend = Additive) |
| Alpha | `Mobile/Particles/Alpha Blended` | `Universal Render Pipeline/Particles/Unlit` (Blend = Alpha) |
| Multiply | `Mobile/Particles/Multiply` | `Universal Render Pipeline/Particles/Unlit` (Blend = Multiply) |

Shader Mobile không có màu tint trên material — màu đến từ vertex color (Start Color / Color over Lifetime của particle). Đây là cách nên dùng: một material phục vụ nhiều màu.

Cần shader lit cho mesh debris: Built-in `Mobile/Diffuse` hoặc `Standard`; URP `Universal Render Pipeline/Simple Lit`. Truyền tên shader qua tham số `shaderName`.

## Shader tự viết: `SH_VFX_Particle.shader`

Template trong `assets/` của skill, path menu `VFX/Particle Basic`. **Một shader chạy cả Built-in và URP**: dùng `CGPROGRAM` + `UnityCG.cginc` và một Pass không có `LightMode` (URP vẫn vẽ nó như SRPDefaultUnlit). Không tương thích SRP Batcher — chấp nhận được cho particle.

Tính năng:
- `_MainTex`, `_TintColor` (HDR), nhân vertex color.
- `_UseR` (keyword `_GRAYSCALE_R`): dùng kênh R làm alpha cho texture grayscale nền đen.
- `_Dissolve` (keyword `_DISSOLVE`): dissolve theo noise, ngưỡng lấy từ **Custom1.x** của particle (Custom Data module), viền màu `_EdgeColor`.
- `_SrcBlend`/`_DstBlend`: Additive = SrcAlpha/One, Alpha = SrcAlpha/OneMinusSrcAlpha. `VfxBuildKit.Material(..., shaderName: "VFX/Particle Basic")` tự đặt theo blend (multiply không hỗ trợ trong shader này).

Dùng dissolve: bật Custom Data và vertex streams trong build script:

```csharp
var cd = ps.customData; cd.enabled = true; cd.SetMode(ParticleSystemCustomData.Custom1, ParticleSystemCustomDataMode.Vector);
cd.SetVectorComponentCount(ParticleSystemCustomData.Custom1, 1);
cd.SetVector(ParticleSystemCustomData.Custom1, 0, VfxBuildKit.Curve(0, 0, 0.6f, 0, 1, 1)); // giữ nguyên rồi tan dần
VfxBuildKit.UseCustom1Stream(ps); // Position, Color, UV, Custom1.x → TEXCOORD0.xyz
mat.EnableKeyword("_DISSOLVE"); mat.SetFloat("_Dissolve", 1);
```

## Viết shader mới

Bắt đầu từ template, giữ các nguyên tắc:
- Hướng mobile: `#pragma target 2.0` nếu đủ, `half`/`fixed` cho màu, ít texture sample (≤ 2–3), không vòng lặp, không `discard` khi blend được (alpha test tốn trên GPU tile-based).
- Tính năng tùy chọn dùng `shader_feature_local` để material không dùng không phải trả chi phí.
- Không include file của URP (`Packages/com.unity.render-pipelines.universal/...`) để shader vẫn compile được trong project Built-in.
- Đặt file trong `Assets/VFX/_Shared/Shaders/SH_<Name>.shader`, path `VFX/<Name>`.
- Build report sẽ báo lỗi compile (`ShaderUtil.ShaderHasError`); đọc log Unity để lấy dòng lỗi cụ thể.
