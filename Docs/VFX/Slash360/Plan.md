# Slash360 (hiện chỉ còn Đất; bản 5 nguyên tố đã lưu ở `Docs/VFX/_ArtDirection/_archive/Slash360_5elements_2026-11-03/`) — kế hoạch v1 (đã duyệt 2026-11-03, "dựng cả 5")

Không gian: dir · mesh vòng 360° nghiêng 25° theo tay kiếm (Swing xoay X 25°, nâng 1 m) · camera topdown 60° · neo nhân vật · bán kính 2 m · nền tối (giả định).
Chốt: xoay 360°, nghiêng theo tay kiếm, ~2 m neo nhân vật, Stylized/anime ~0.35 s. Đề xuất: nghiêng 25°, nền tối.

| # | Layer | Vai trò | Kỹ thuật | Shader |
|---|---|---|---|---|
| L1 | Body | thân vệt 0–0.35 s | mesh `SM_VFX_Slash_Circle_Thin` (vành phẳng, scale 1.56 → bán kính ngoài 2 m), UV chạy theo tuổi hạt (Custom1.x) | `VFX/FX/Slash Sweep` |
| L2 | Edge | mép sáng | cùng mesh, mảnh hơn, Additive | `VFX/FX/Slash Sweep` |
| L3 | Debris | mảnh nguyên tố theo đầu vệt | circle shape arc Loop 1 vòng / 0.19 s | Spark / mesh tinh thể–gai / bong bóng |
| L4 | StartFlash | 1 chớp ở điểm bắt đầu | billboard glow 0.1 s | Additive |

Khác kế hoạch ban đầu: Element detail gộp vào shader Body (noise cuộn ngược chiều) thay vì mesh thứ 3; Mesh đổi (2026-11-03, art lead): `SM_VFX_Slash_360` là vòng dây mỏng dựng đứng, không hợp làm vệt chém → dùng `SM_VFX_Slash_Circle_Thin`: vành phẳng, u chạy quanh vành (bắt đầu ở +z, chiều kim đồng hồ nhìn từ trên), v = bề rộng với mép ngoài sắc ở v = 0.5. Edge dùng chính mesh này. Ảnh so sánh các mesh: `Mesh_candidates.png`.

Nguyên tố (Core / Mid / Outer; Blend; texture Body; detail): Lửa (trắng vàng/cam/đỏ sẫm; Add; S_03; Streaks) · Băng (trắng/xanh nhạt/xanh lam; Add; S_02; Cells cứng) · Sét (trắng/vàng/tím; Add; S_01; Streaks nhanh) · Độc (vàng chanh/xanh lá/tím đen; Alpha; B_02; Smooth) · Đất (vàng nâu/nâu/nâu sẫm; Alpha; Blunt_Slash; Cells thô).

Nguồn asset: mesh `Assets/VFX/_Imported/Mesh/SM_VFX_Slash_Circle_Thin.fbx`, `SM_VFX_Debris_Crystal_01/02`, `SM_VFX_Spike`; texture slash copy từ rpg-game `RPG_VFX/Duong/Texture/Slash` (T_VFX_Slash_S_01/02/03, B_02, Blunt_Slash); noise `_Shared/Textures/Noise`; glow từ `Explosion/Textures/T_Glow_Soft.png`.
Shader mới: `SH_VFX_SlashSweep.shader` (ghi trong `Docs/VFX/SHADERS.md`).
Ngân sách: ≤ 210 particle tối đa mỗi prefab (thực tế ~30), 4 material, texture ≤ 512.
Build: menu `VFX → Slash360 → Build` (5 prefab `VFX_Slash360_<Element>`).

## v1.1 (2026-11-03, phản hồi art lead: đầu vệt bị cắt sắc, quá cứng)
- Shader: đầu vệt thu nhọn về mép ngoài (`_HeadPoint`), đuôi mờ dần (`_TailSoft`), dải màu mềm hơn (`_BandSoft`).
- Thêm lớp `L0_Trail`: màn vệt mờ dài kéo theo sau, sọc noise cuộn dọc hướng chém (cảm giác chuyển động).
- Edge chỉ còn ngắn sát đầu (mép sáng sát lưỡi), không viền trắng suốt vệt.

## v1.2 (2026-11-03, art lead: dùng 3 shader Coloso đã sửa để làm slash)
- Body / Edge / Trail dùng `VFXLib/ColosoShaderAdditive_Optimized` (Lửa, Băng, Sét, Edge, Trail), `ColosoShaderAlpha_Optimized` (Độc, Trail của Đất), `ColosoShaderAlphaCutOut_Optimized` (Đất). `VFX/FX/Slash Sweep` không còn dùng trong Slash360 (vẫn giữ trong project).
- Hình lưỡi liềm (đầu nhọn, đuôi mờ, 3 dải màu) bake sẵn vào texture RGBA: `Docs/VFX/Slash360/bake_slash_textures.py` → `T_Slash360_Crescent_<El>.png`, `EdgeCrescent`, `Detail`.
- Chuyển động quét điều khiển bằng Custom Vertex Streams (Position, Color, UV, Custom1XY, Custom2XY): Custom1.x = dissolve (1 hiện, 0 tan), Custom1.y = hệ số méo, Custom2.x = vị trí đầu / cửa sổ (cộng vào UV chính, `_UseMainUVCustom1ZW`). `_MainTex` tiling x = -1/window.
- Dissolve lấy từ chính lưỡi liềm (`_MainTexRDissolve`) nên đuôi mỏng tan trước. Sọc detail = MaskTex cuộn ngược chiều (`_MaskFlowX`).
- Additive shader không có méo UV bằng noise (Alpha / Cutout có), nên Lửa / Băng / Sét không còn gợn nhẹ như bản Slash Sweep.
- Mất so với bản Slash Sweep: dải màu không còn tính theo vị trí lúc chạy (bake cố định theo hình).

## v1.2.1 (sửa lỗi visual)
- Lớp Trail nhỏ hơn thân 1.5% (trước to hơn 2% nên sọc lòi ra viền ngoài thành răng cưa); sọc thưa và nhẹ hơn.
- Tia lửa: capsule có đuôi thay vì hình nón.

## v1.3 (art lead: "xem lại cách dùng bộ shader" — học từ material slash trong rpg-game: Katana, Scythe, Skarnfrost)
Cách dùng chuẩn của bộ Coloso:
- `_MainTex` là hình xám (alpha = lưỡi liềm). Màu đến từ hạt (Color over Lifetime) hoặc `_ColorTex` (ramp) ở shader Additive, không bake màu vào texture.
- `_MaskTex` = `T_VFX_Gradient_01` làm mờ hai đầu mesh (không dùng MaskTex chứa sọc chi tiết nữa; sọc chi tiết chuyển sang `_DissolveTex` cuộn).
- Custom Vertex Streams: Position, Color, UV, **Custom1XYZW**. Custom1.x = dissolve (1 hiện … 0 tan), .y = hệ số méo, .zw = offset UV chính (`_UseMainUVCustom1ZW`): z = vị trí đầu / cửa sổ. Trước đây đặt offset ở Custom2: sai quy ước.
- `_SmoothDissolve` ≈ 7 (giá trị của material mẫu), `_UseManual_DebugDissolve` = 0, `_MainClampX/Y` = 1, `_MainRBGOffset` = 0, `_FD` = 0, Alpha/Cutout bật `_UseNoise` + `_UseCustom1YDistortion`.
- Màu Additive: ramp `T_Slash360_Ramp_<El>.png` qua `_ColorTex` + `_Color90degreeUVFlip` = 1, `_ColorIntensity` = 0. Alpha / Cutout (Độc, Đất): Color over Lifetime Core → Mid → Outer.
- `bake_slash_textures.py` giờ bake texture xám + ramp (không còn màu trong texture chính).

## v2.0 (2026-11-03, art lead: "bỏ các nguyên tố slash khác, giữ lại đất thôi")
- Slash360 chỉ còn nguyên tố **Đất** (`VFX_Slash360_Earth`; Coloso AlphaCutOut, cutoff 0,4; mảnh đá `SM_VFX_Spike` + `Debris_Crystal_01`). Lửa, Băng, Sét, Độc bị xoá khỏi project (prefab, material, texture riêng, scene demo, ảnh preview).
- Bản 5 nguyên tố (builder, script bake, kế hoạch, preview) lưu ở `_archive/Slash360_5elements_2026-11-03/` để khôi phục: chép lại `Slash360Build.cs` + `bake_slash_textures.py` và chạy bake rồi Build.
- Texture dùng chung giữ lại: `T_Slash360_Edge`, `Glow`, `White`, `Detail_Trail`, `T_VFX_Gradient_01`.
