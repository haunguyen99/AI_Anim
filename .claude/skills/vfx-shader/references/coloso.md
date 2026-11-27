# Bộ shader Coloso (VFXLib) — cách dùng chuẩn

Ba shader nhập từ rpg-game (`RPG_VFX/Duong/Shader`), bản đã sửa chạy cả URP và Built-in:

| Menu shader | File (`Assets/VFX/_Imported/RpgGame/Particle_Basic/`) | Dùng khi |
|---|---|---|
| `VFXLib/ColosoShaderAdditive_Optimized` | `VFXShaderAdditive.shader` | Sáng, năng lượng, lửa, sét, băng. Blend `One One`. Có `_ColorTex` (ramp màu) và tách kênh RGB |
| `VFXLib/ColosoShaderAlpha_Optimized` | `VFXShaderAlpha.shader` | Khói, độc, đất, thứ cần che nền. Blend alpha. Có méo UV bằng noise |
| `VFXLib/ColosoShaderAlphaCutOut_Optimized` | `VFXShaderAlphaCutout.shader` | Mép cứng kiểu cel / đá. `clip(alpha - _AlphaCutOut)` |

Tên trong ô chọn Shader của material là tên menu (dưới mục **VFXLib**), không phải tên file.

**Art lead, 2026-11-03: slash chỉ làm bằng bộ này.** Các effect khác dùng khi hợp (trail, vệt, đòn đánh có mesh + UV).

## Nguyên tắc dùng (học từ material slash của rpg-game: Katana, Scythe, Skarnfrost)

1. **`_MainTex` là hình xám.** Dạng của effect nằm ở texture (R hoặc alpha). Không bake màu vào texture.
2. **Màu từ hạt hoặc ramp:**
   - Particle: Start Color + Color over Lifetime (core → mid → outer theo thời gian).
   - Additive: `_ColorTex` là ramp màu theo bề rộng. Bật `_Color90degreeUVFlip` = 1 để trục x của ramp = v của mesh; `_ColorIntensity` = 0, `_ColorPower` = 1, `_Desaturate` = 0.
   - Độ sáng chung: `_MainColor` (HDR), `_TextureIntensity` (Additive bình phương nó).
3. **`_MaskTex` nhân vào alpha:** dùng `T_VFX_Gradient_01` (trắng ở giữa, đen mờ hai đầu) để làm mờ hai đầu mesh. Có thể cuộn (`_MaskFlowX/Y`) cho sọc chuyển động.
4. **Dissolve:** `_DissolveTex` (noise, cuộn bằng `_DissolveFlowX/Y`), `_SmoothDissolve` ≈ 7 theo material mẫu, `_UseManual_DebugDissolve` = 0 để đọc từ particle. `_MainTexRDissolve` = 1 thì dùng chính hình làm ngưỡng (phần mỏng tan trước).
5. **Custom Vertex Streams (mỗi layer mesh):** `Position, Color, UV, Custom1XYZW`.
   - Custom1.x → dissolve: 1 hiện, 0 tan. Với `_SmoothDissolve` 7 vùng tan nằm dưới ≈ 0.5–0.65, nên giữ ≥ 0.65 cho tới lúc muốn tan.
   - Custom1.y → hệ số méo (`_UseCustom1YDistortion` = 1; chỉ Alpha / Cutout).
   - Custom1.zw → offset UV chính khi `_UseMainUVCustom1ZW` = 1 (tên "Custom1ZW" nghĩa là zw của Custom1). **Dùng cái này để quét / trượt texture theo tuổi hạt**, không dùng `_MainFlowX/Y` (đó là thời gian tuyệt đối, mỗi lần phát lệch pha).
6. **Cố định:** `_MainClampX/Y` = 1 (texture 1 bản), `_MainRBGOffset` = 0 (tách kênh tốn 3 sample), `_FD` = 0, `_CDF` = 0, `_CameraOffset` = 0 nếu không cần soft particle / fade camera. `_MainRIsAlpha` = 1 khi hình ở kênh R (texture RGB xám), = 0 khi hình ở alpha.
7. **Cull:** mesh phẳng một mặt thì `_CullMode` = 0 (Off) như material mẫu. Mesh có tiết diện hai mặt chồng nhau (ví dụ `SM_VFX_Slash_Circle_Thin`) dùng `_CullMode` = 2 để Additive không cộng đôi.
8. **Alpha / Cutout:** `_UseNoise` + `NoiseTex` + `_MainTexDistortion` (0.5 theo mẫu) cho mép gợn; Cutout chỉnh `_AlphaCutOut` (0.35–0.45 cho đá).

## Thuộc tính tham chiếu nhanh

| Nhóm | Thuộc tính |
|---|---|
| Chung | `_MainColor` (HDR, alpha không dùng), `_OpacityStrength`, `_OpacityPower`, `_TextureIntensity`, `_CullMode`, `_ZwriteMode` (Alpha) |
| Main | `_MainTex` + ST (tiling x âm = lật), `_MainFlowX/Y`, `_MainClampX/Y`, `_Main90degreeUVFlip`, `_MainUVSwitch` (UV1), `_UseMainUVCustom1ZW`, `_MainRIsAlpha` |
| Mask | `_MaskTex`, `_MaskFlowX/Y` (đọc kênh R) |
| Màu (Additive) | `_ColorTex`, `_ColorFlowX/Y`, `_ColorClampX/Y`, `_Color90degreeUVFlip`, `_Desaturate`, `_ColorPower`, `_ColorIntensity` |
| Dissolve | `_DissolveTex`, `_DissolveFlowX/Y`, `_MainTexRDissolve`, `_UseManual_DebugDissolve`, `_ManualDissolve`, `_SmoothDissolve` |
| Méo (Alpha / Cutout) | `_NoiseTex`, `_UseNoise`, `_UseCustom1YDistortion`, `_MainTexDistortion`, `_NoiseFlowX/Y`, `_NoiseAffectsXAxis/YAxis` |
| Fade | `_FD` (độ sâu), `_CDF` + `_CDFOffset` (khoảng cách camera), `_CameraOffset` |

## Texture slash: lấy từ `Assets/Library/Slash/` (art lead 2026-11-04)

Texture chạy UV (`_MainTex`) của mọi slash lấy trong `Assets/Library/Slash/Main_tex(Uvmesh)/` (`Slash_Main_tex_Uvmesh_NNN`; vệt trúng đòn ở `Slash/Onhit/`; tên cũ ở `Docs/VFX/_Library/library_index.csv`).
1. Xem ảnh các ứng viên (Read PNG) và chọn theo dáng vệt trong brief (lưỡi mảnh, vệt dày, mép rách, vệt kiếm…).
2. Chỉ chọn ảnh **xám** (màu đến từ ramp / Color over Lifetime). Bỏ qua ảnh có màu sẵn.
3. Giữ nguyên khung UV và tỉ lệ gốc. Hướng vệt không khớp trục u của mesh thì xoay bằng `_Main90degreeUVFlip` hoặc tiling âm; không sửa file trong Library.
4. Build script chỉ `LoadAssetAtPath`, không `ImportTexture` lên file Library (dùng chung). Cần wrap / import khác thì copy ảnh (không copy `.meta`) sang `Assets/VFX/<Effect>/Textures/`.
5. Ghi đường dẫn texture đã chọn vào `Plan.md`. Chỉ bake bằng `scripts/bake_slash_textures.py` khi Slash không có dáng hợp, và nói lý do trong kế hoạch.
6. `_MaskTex` vẫn là `T_VFX_Gradient_01`. Ramp màu (`_ColorTex`) có thể bake bằng script.

## Công thức lưỡi liềm quét quanh mesh vòng (ví dụ Slash360)

Mesh có u chạy dọc đường quét (0→1) và v theo bề rộng. Muốn lưỡi liềm dài `W` (phần vòng) chạy hết vòng:
- MainTex là hình lưỡi liềm trong không gian (l, v): x = l (0 đầu … 1 mũi đuôi), y = v. Lấy từ `Assets/Library/Slash/` (mục trên); Slash360 cũ bake bằng `scripts/bake_slash_textures.py` (đầu nhọn, đuôi mờ, ramp màu) trước khi có Library.
- `_MainTex` tiling.x = **−1/W**. Offset từ particle: Custom1.z = `(1+W)/W × tiến độ` (đường thẳng từ 0 đến `(1+W)/W` trong 80% tuổi hạt rồi giữ).
- Đầu ở l = 0, vị trí đầu theo u = Custom1.z × W.
- Mảnh vụn bay theo đầu: Circle shape, Arc Mode = Loop, một vòng trong thời gian đầu đi hết vòng.
- Ví dụ đầy đủ: `assets/ColosoMeshFxBuild.example.cs` (bản 5 nguyên tố, từ `Slash360Build.cs`; project hiện chỉ giữ Đất, bản đầy đủ lưu ở `Docs/VFX/_ArtDirection/_archive/Slash360_5elements_2026-11-03/`).

## Lỗi thường gặp

- Bake màu vào texture chính rồi dùng `_MainColor` trắng: mất khả năng đổi màu bằng hạt. Dùng ramp / Color over Lifetime.
- Dùng `_MainFlowX` để quét một lần: lệch pha giữa các lần phát. Dùng Custom1.zw.
- Quên stream: effect đứng yên / không tan. Kiểm tra `SetActiveVertexStreams` có `Custom1XYZW`.
- Đặt `_ColorIntensity` = 1 (mặc định) khi có ramp: màu bị cộng 1 nên trắng. Phải 0.
- Đổi import của texture noise dùng chung (`Assets/VFX/_Shared/Textures/Noise/`): build script chỉ `LoadAssetAtPath`, không `ImportTexture` lên chúng (từng làm hỏng wrap Repeat của Meteor / Blast).
- Bộ Coloso nhiều sample (Main 1–3, Color, Dissolve, Mask, Noise): không vượt ~6 layer hạt mesh cùng lúc trên mobile.

## Shader nhập khác đáng dùng (xem `Assets/VFX/_Imported/RpgGame/README.md`)

- `Custom/VFX/UltimateGradient_MultiplyNoiseDissolve_Sweep` (`DissolveBasic`): gradient 3 màu theo độ xám, quét UV một lần, dissolve noise cuộn, nguội dần.
- `Custom/UVNoise_DoubleSided_PureDissolve` (`UVNoise`): UV cuộn theo tuổi hạt (OneShot), màu mặt trước / sau khác nhau.
- `Slash/BlendDistortionCutout` (`SlashShader`), `ThrustEffect…` (đâm trên mesh trụ), `Trail`, `SwordBeam` (Shader Graph/Amplify).
- `Cartoon FX/Remaster/*`: glow, ring, distortion, ubershader procedural.
