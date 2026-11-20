# Điện (lightning) – học từ rpg-game (2026-11-04)

> **Công thức chính xác của line_impact (cột sáng vàng), wave, flare: xem `thunder-core.md`.** Chỗ nào dưới đây mô tả line_impact là "tia zig-zag" thì SAI: art lead xác nhận nó là cột sáng vàng ban đầu (Stretched, 3D size 35×50×5, pivot (0,1,0)).

Nguồn đã đọc: `VFX_BossRaid_Knight_Thunder` (+`_InUse`), `..._Thunder Spear` (+`_InUse`), `..._Lightning_Trail`, `..._Landing`, `VFX_Aura_Gauntlet_Prismatic`. Bản InUse chỉ là prefab thường (gom lại dưới một `root` scale 0.07), nội dung giống bản gốc.

## Cách rpg-game dựng điện
| Lớp | Renderer | Shader / vật liệu | Ghi chú |
|---|---|---|---|
| Tia sét (cung điện) | **Mesh** `thunder_mesh2.fbx` / `Guardian_Lighting.fbx`, render alignment **Local** (cả Trail lẫn Aura) | `Particles/Lightning_CustomBlend` (đã nhập: `Particle_Basic/Lightning.shader`), `_MainTex` = `Guardian_Lightning3.png`, `_Gradient` = `Gradient_lightning.png`, `_TintColor` HDR (9.45, 2.66, 0) | Vertex streams `000103041f27` = Position, Color, UV, **Custom1.x (UV2.z)** = lifetime/cutoff, **random offset (w)**. Custom Data 1 = curve -0.47→1 (hoặc -0.31→1): cutoff quét dọc thân sét → tia “bắn ra” rồi tắt. Đời 0.4–0.7 s, size 0.3–0.6, `sizeOverLife` 0.71→1 |
| Tia ngắn bắn ra (Thunder Spear) | **Stretched Billboard**, lengthScale 2, velScale 1 | Additive built-in 10720, sheet `cfxr electric arcs fade x4.png` **1×4**, startFrame ngẫu nhiên | Đời 0.1–0.3 s, 5/s, shape cone cao 15 → hồ quang bắn dọc theo mũi giáo; có thêm lớp `Tx_electricity_08_rot.png` |
| Chớp vạch (line_impact) | Stretched Billboard + mesh `ME_Curve_06`, `lightning_texture_sheet1.png` **5×1**, 2 burst (t=0, 0.1), life 0.15 s, size 35 | vật liệu `M_lightning_bossraid` | Tia dài chớp 2 lần |
| Tàn điện (electric_remain) | Stretched Billboard, sheet 3×3 `HandPaintedLightning2.png` | `ERB/Particles/Add_CenterGlow` (đã nhập `Hovl_ERB/`) | burst 10 hạt ×2 (t=0, 1), cone 70°, randomDir 1, đời 0.2–0.5 s, màu vàng |
| Flare / impact / wave | Billboard align World(2) (nằm đất), additive | `TX_VFX_Mask16`, `flashLarge`, `wave 1` | Chớp 0.15–0.3 s, màu vàng (1,0.85,0.25); sóng phình 0.38→1 trong 0.5 s |
| Vết nứt đất | Mesh `ME_Tornado_03` | `VFX/Master` (Shader_VFX) + `T_VFX_Ground_Crack.png` | alpha 0→1 (0.18) →1 (0.71) →0 |
| Khói aura | Billboard sheet 2×2 `SmokeHarsh.png` | UberFXSG (URP only) | không cần: dùng khói mặc định của art lead |

Màu: vàng (1, 0.85, 0.25) lõi, cam đậm (0.98,0.88,0) → đỏ tím (0.44,0.01,0.12) ở cuối đời; TintColor HDR cam (9.45, 2.66, 0).

## Rút ra khi làm điện
1. Sét = **mesh dải (strip) dài + UV dọc thân**; hình do texture quyết định, thời gian bằng `Custom1.z` quét cutoff (shader `Lightning_CustomBlend` có sẵn).
2. Tia chớp rất ngắn: đời 0.1–0.3 s, nhiều tia chồng, mỗi tia một frame sheet khác nhau (startFrame random).
3. Luôn có: chớp lõi (flare) + sóng nền + tàn điện bắn ra, màu vàng → cam.
4. Texture dùng được đã copy: `Assets/VFX/_Imported/RpgGame/Lightning/Textures` (Guardian_Lightning3, Gradient_lightning, cfxr electric arcs x4, Tx_electricity_08_rot, lightning_texture_sheet1, HandPaintedLightning2, Lightning_light), mesh `Lightning/Mesh` (thunder_mesh2, Guardian_Lighting).
5. Shader dùng được (đã nhập, chạy cả hai pipeline): `Particle_Basic/Lightning.shader`, `Particle_Basic/Electric.shader`, `Hovl_ERB/Add_CenterGlow.shader`, `Hovl_ERB/Electricity.shader`. `LightningParticles.shadergraph` chỉ URP – bỏ.

## Sửa lại sau khi render mẫu (2026-11-04) – quan trọng hơn bảng ở trên
Đã render `VFX_BossRaid_Knight_Thunder` / Spear / Trail bằng project tạm (ảnh: `Docs/VFX/_Reference/rpg-game_Thunder/`). Thấy ra:
- Thunder **không phải cột sét 8 m**: là **vết nứt đất toả tròn** (T_VFX_Ground_Crack, vàng, nằm đất, hiện dần rồi tắt ~1.4 s) + **tia dài chớp 2 lần** (sheet `lightning_texture_sheet1` 5 frame, Stretched Billboard, frame tuyến tính trong 0.15 s) + **cung điện trắng nhọn** bắn ra mọi hướng (`HandPaintedLightning2` 3x3, Stretched, speed nhỏ, randomDirection 1) + chớp tròn + sóng.
- Thunder Spear chỉ là một tia sáng hình thoi, Trail chỉ vài đốm: không có gì để học thêm về hình dạng tia.
- Slash và Aura chưa render được (Slash lỗi null, Aura dùng ShaderGraph URP).
- Stretched Billboard kéo đuôi **ra sau** hướng bay: muốn tia treo phía trên điểm đánh thì cho hạt bay xuống (shape Cone xoay X +90).
- Tia dạng sheet mỏng: xếp chồng 2–3 hạt mỗi burst cho đủ sáng.
- **Sheet cắt bằng Texture Sheet Animation thì Tiling/Offset của material phải để 1×1, 0.** Material tái sử dụng giữa các lần build giữ tiling cũ (bản 1 để 5×1) → UV bị bóp, tia mỏng và sai; builder phải reset tiling/offset mỗi lần build.

## Đã làm: Assets/VFX/LightningStrike (sét đánh xuống), bản 2 theo mẫu
Bản 1 (mesh dải tự vẽ + `Lightning_CustomBlend`) bỏ vì nhìn như dải cam uốn lượn. Bản 2 dùng đúng texture của rpg-game (nứt đất, sheet tia, sheet cung điện) + impact mix. Ghi chú: `Docs/VFX/LightningStrike/Plan.md`. MixRecipeBuild phải gọi TRƯỚC khi tạo root (nó mở scene riêng).
