# Điện: Thunder Spear, Lightning Trail, Aura Gauntlet (học từ rpg-game, 2026-11-04)

Đọc kèm `thunder-core.md`. Số liệu lấy từ prefab (Start Color kiểu Two Colors đã đọc min..max). Kích thước trong ngoặc là bản đã nhân scale root của mẫu; mọi effect dựng lại không có scale trên transform, Scaling Mode Hierarchy, root là Particle System.

## ThunderSpear (loop 5 s, tia chạy dọc cán giáo)
| Layer | Setup mẫu |
|---|---|
| root (glow) | Stretched, pivot (0, 0.5, 0), Length Scale 2, Velocity 0, 3D size (30, 17, 1), life 1, speed 0.01, rate 2 + burst t=0, màu Two Colors (1,0.76,0.48)..(1,0.56,0.13), alpha 0 → 1 (0.21) → 1 (0.77) → 0, texture `Lightning_light.png` (vệt sáng ngang mềm), additive |
| Thunder | Stretched, pivot (0, 0.5, 0), Length 2, Velocity 1, 3D size X 1–3, Y 8–25, Z 1, life 0.1–0.2, speed 0.1, rate 5 + burst, màu (1,0.82,0.1)..trắng, sheet 1×4 tuyến tính + start frame random, texture `cfxr electric arcs fade x4.png`, additive |
| electric | Stretched, size 1–3, rot3D X ±60°, shape Sphere r 0.6 scale (1,1,15) (elip dài dọc cán), rate 5, life 0.15–0.3, speed 0.1–0.3, màu (1,0.82,0.02), sheet 1×4, `Tx_electricity_08_rot.png`, order 2 |
Root mẫu scale 0.1428. Bản dựng: cán đứng 2.6 m, độ rộng cung điện ×3 (texture chỉ lấp dải mỏng của khung).

## LightningTrail (một layer, mesh, World space)
Mesh `thunder_mesh2.fbx`, Render Alignment Local, sort Youngest In Front, order 5; **Simulation Space World**; rate 5 + 0.5 theo quãng đường; life 0.3–1.2, speed 0.2–0.5; 3D size X 0.5–0.7, Y 0.4–0.7, Z 1; rot3D X, Y 0..2π; shape Sphere r 0.3 scale (1,5,1); Size over Life 0.71 → 1 (0.05) → 0.54; màu (1,0.77,0.04); Custom Data Custom1.x = đường cong -0.47 → 1; streams Position, Color, UV, Custom1.
Shader `Particles/Lightning_CustomBlend`: `_MainTex` Guardian_Lightning3 (**Repeat**, cuộn theo U), `_Gradient` Gradient_lightning, Tint HDR (9.45, 2.66, 0), Stretch 2, Offset -0.07, Speed 0.4, **Blend Src 3 (DstColor) Dst 1 (One)**.
Bản dựng: scale thế giới ×0.8 thay vì 0.1428, rate 8 + 2/m cho dễ đọc; root mang `VfxPathMover` để showcase di chuyển.

## AuraGauntlet (loop, quanh vật thể)
| Layer | Setup mẫu |
|---|---|
| root smoke | Billboard, rate 12, life 1–2.5, speed 0–0.5, size 0.5–1, gravity -0.1, max 50, màu Two Colors (1,0,0.16)..(1,0.27,0.36), size 0.61 → 0, alpha 0 → 1 (0.48) → 0; shader UberFX ShaderGraph (URP) → thay bằng khói mặc định |
| smoke | như trên, size 1–2, màu (1,0.83,0.85), order 2, gần đất |
| electric | Mesh `Guardian_Lighting.fbx`, align Local, rate 10, life 0.4–0.7, 3D size X 0.3–0.6 Y 1 Z 0.5, sim speed 0.75, shape Sphere r 0.5 scale (1.5,1,1) alignToDirection + randomDirection 1, Custom1.x = 0 (-0.31) → 0.15 (0.56) → 0.31 (0.64) → 0.45 (0.84) → 1 (1); Lightning shader với `Guardian_Gradient` (tím → lam → trắng), Tint HDR (11.57, 0.55, 0.93), Stretch 2, Offset -0.07, Speed 0.4 |
| dot_Light | Billboard, rate 7, life 0.5–1, speed 1–2, size 1, Size over Life 1 → 0, alpha 1 → 0, Noise strength 1 freq 2, `Rectangle 1.png` (chấm sáng), additive, order 3 |
Mẫu phát từ mesh cây gậy (không có trong project): bản dựng dùng box / elip cao 1.5 m.

## Bài học chung
- Start Color `minMaxState` 2 = Two Colors; đọc `minColor..maxColor`.
- Texture Sheet 1×4 / 3×3 / 5×1 chỉ cắt bằng module Texture Sheet; Tiling của material phải 1×1.
- Stretched Billboard kéo đuôi ra sau hướng bay; pivot Y=1 đặt đáy tại điểm phát.
- Effect có vệt (World space) cần emitter di chuyển: `VfxPathMover` (play mode) và tham số `motion` của `VfxBuildKit.CaptureSheet / Finish` (preview).

## AuraGauntlet: ghi chú dựng lại (2026-11-04, lần 2)
- Mesh bolt của mẫu là `pSphere2` (42 đỉnh, mảnh cong 2 × 0.8 × 1 m) trong `Guardian_Lighting.fbx`, khớp theo local ID 4864056309639282896 (không phải `Sphere.004`). Khi cutoff < 0 (5% đầu đời) cả mảnh hiện đặc: là hành vi của mẫu, nhìn như một tấm hồng phẳng.
- Texture lấy từ `Assets/Library`: bolt = `Lightnings_Electrics_007` (= Guardian_Lightning3), chấm sáng = `glow_012` (gần nhất với Rectangle 1). Ramp tím → lam → trắng không có trong Library nên builder sinh `T_AuraGauntlet_Ramp.png`. Khói = `fx_t_smoke_02` (mặc định).
- Khói mặc định là alpha blended còn shader của mẫu thiên về cộng sáng: khói thấp để màu trắng sẽ lấn át, nên tô đỏ hồng bằng Start Color.
- Bản copy tham chiếu: `Assets/VFX/_Imported/RpgAura/` (hiện hồng, Shader Graph URP).
