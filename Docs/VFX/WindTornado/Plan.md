# VFX_WindTornado — kế hoạch v3 (2026-11-06, theo prefab Stupid_Tornado_Projectile của rpg-game)

**Vì sao v3:** art lead chỉ định học `Stupid_Tornado_Projectile` ("đọc thật kĩ cách setup, mesh, texture"). Đã copy prefab + phụ thuộc (`Assets/VFX/_Imported/RpgTornado/`), render bản gốc (`ref_Stupid_Tornado_Projectile.png`), dump mọi module (`ref_Stupid_Tornado_Projectile_params.txt`), giải đồ thị Shader Graph, xem từng ô texture (`ref_sheet_*_cells.png`) và UV mesh. v1 (mảnh Blender) và v2 (phễu `tornado_mesh`, từ `VFX_Book_Tornado`) đã bỏ.

Không gian: ground · quanh trục Y, các vành nghiêng quay + cột sương dựng đứng · camera 3/4 nhìn xuống 40° · cao ~3,6 m · neo điểm đất, đứng yên · một lần ~3,9 s (lên 0,3 s, giữ, tan) · stylized. Màu: lấy đúng của họ (teal `06FFDF` cho vành gió, xanh nhạt cho ống, trắng cho sương, xanh dương cho vụn).

## Cách bản gốc hoạt động (đã đọc)
- **Mesh** `fbx_fx_cylinder_03`: vành hở ~340°, bán kính 0,59 m, cao 0,27 m, UV 0..1 vòng quanh và theo chiều cao. `Tornado_vertical`: ống r 0,32 / cao 0,29 m, UV 0..1.
- **Shader** Shader Graph `Fx_dissolve_particle_apb` (có BuiltInTarget; Built-in chạy được khi có package shadergraph). Sheet **đóng gói kênh**: R = độ sáng màu, G = trường tan / highlight, B = méo UV, A = alpha. Custom1 = (tan 0→1, độ gắt mép ~20, độ méo, –). Custom2 = màu highlight (trắng). Màu thân = Start Color × R. Highlight (Min −10, Max −2) sáng ở chỗ G còn cao khi đang tan, nên mép tan lóe trắng. UV0 = ô sheet, UV1 = Custom1, UV2 = Custom2: stream `Position, Normal, Color, UV, UV2, Custom1XYZW, Custom2XYZW`.
- Vành tan dần bằng chính ô sheet (G làm trường tan), nên từ ô "đốm lửa" 14–15 ra các sợi xanh có lõi trắng.

| # | Layer | Vai trò (số của họ × K = 0,5) | Mesh | Shader | Texture |
|---|---|---|---|---|---|
| L1 | Wind (root) | Vành gió: sống 0,35–0,5 s, bay lên 4–6, size 5–7, nghiêng 70–110°, quay 3 vòng/s giảm dần, tan theo Custom1; 25/s | `fbx_fx_cylinder_03` | Graph | `Tex_fx_elements_set_01` ô 14–15 (4×4); sheet này không có trong Library nên dùng bản nhập `_Imported/RpgTornado` |
| L2 | SharpRing | Vành sáng hơn, lên cao ngắn | cùng mesh | Graph (soft particles) | `Library/impact/impact_071` (= splash set) ô 8 (3×6) |
| L3 | Tubes | Ống mảnh bay lên và nở r 0,27→2,9 m (×K), Additive | `Tornado_vertical` | Mobile Additive | `Library/wave/wave_070` (= Wind01) |
| L4 | MistUp | Cột sương trắng dựng đứng | Billboard | Mobile Alpha Blended | `Library/smoke/smoke_010` (= Dust01) |
| L5 | MistFoot | Sương lan sát đất (của họ là Horizontal Billboard: đổi sang Billboard + Local, xoay X 90° theo luật art lead) | Billboard | Mobile Additive | smoke_010 |
| L6 | Smoke | Khói xám (world space) | Billboard | Graph | `Tex_fx_elements_set_01` ô 10 |
| L7 | Bits | Vụn xanh nhỏ quay quanh chân | Billboard | Graph | `Tex_fx_elements_set_01` 8×8 ô 19 |

Bỏ so với bản gốc: `particle_dark` (vụn trắng), `smoke_spread`, `leaf` (họ cũng tắt sẵn).
**Khác bản gốc có chủ ý:** bản gốc là đạn (phun 1,5 s rồi tàn, tốc độ 1 → 0); ở đây emission lên 0,3 s, giữ, rồi giảm (chiếm `Emit` = 2,6 s) để đứng yên ~3,9 s.
Khác bản nào: effect gió đầu tiên; khác Slash360 (cung dài), IceSpike (khối đứng cố định) ở mesh, bố cục, timing.
Shader: không viết mới (dùng Shader Graph nhập). Ngân sách: 7 layer, 200 hạt tối đa.

## Ghi chú kỹ thuật
- Material Graph: tên thuộc tính là reference name (`Main_tex`, `Vector1_930B327D` = Highlight_Min, `Vector1_270105AC` = Highlight_Max, `Boolean_9C0948F4` = soft particles, `Vector1_2C5A3101` = Emission_Power); queue 3025 / 3027.
- Shader Graph hiện hồng ở project tạm nếu thiếu package: thêm `com.unity.shadergraph` 14.0.12 vào `Packages/manifest.json` của project tạm (project chính đã có).
- Mọi trục của Velocity / Rotation / Size over Lifetime phải cùng kiểu curve (Unity bỏ qua module nếu lệch kiểu).
- Chưa vào `Included` của Showcase (chờ art lead duyệt). Project chính đang mở thì bấm **VFX → WindTornado → Build**.

---
## Lịch sử v1 (đã bỏ)
### v1 (đã duyệt 2026-11-06)

Không gian: ground · cột dựng đứng quanh trục Y, mesh nằm ngang xoay quanh trục · camera 3/4 nhìn xuống 40° · cao ~3,6 m, bán kính đáy ~0,6 m → đỉnh ~1,5 m · neo điểm đất, đứng yên · nền lẫn.
(đã chốt: lốc xoáy dựng đứng, ~3–4 m, quanh một điểm trên đất, mesh SM_VFX_Wind / SM_VFX_Wind_Wave; đề xuất: timing, màu, lớp, art style)
Thời lượng: một lần 3,6 s (lên 0,4 s → giữ ~2 s → tan ~0,7 s) · Art Style: stylized / cel · màu Core F2FFF6, Mid 9FE0C8, Outer 4FA39A, bụi cát CCB58F.

| # | Layer | Vai trò & timing | Carrier | Shader | Texture (Library) | Kết thúc |
|---|---|---|---|---|---|---|
| L1 | Spiral (root PS) | Thân lốc: ~40 mảnh tường cong/s, sống 0,65–0,9 s, bay lên 3,8–5,6 m/s (hết 3,6 m), nở 0,45→1,3 lần, nghiêng ±17°, xoay quanh Y 9–16 rad/s, lật nhẹ X/Z, noise | `SM_VFX_WindBand_A/B/C` (Blender: mảnh tường cong 105–230°, cao 0,45–0,95 m, loe lên, alpha mờ hai đầu); ngẫu nhiên 1 trong 3 | Coloso Alpha | `trail/trail_033.png` (dải ruy-băng sóng, thân đặc, R = hình; cuộn nhanh theo u); méo `noise/noise_028.png`; dissolve `noise/noise_062.png` | Dissolve Custom1.x + alpha |
| L2 | Inner | Mảnh nhỏ hơn (×0,5), sống 0,4–0,6 s, xoay ngược 14–24 rad/s | cùng 3 mesh | Coloso Alpha (OpacityPower 0,6) | `trail/trail_009.png` (sợi gió mảnh, alpha ≤ 0,77) | Dissolve + alpha |
| L3 | Dust | Bụi cát liền một vành ở chân | Billboard | `Mobile/Particles/Alpha Blended` (khói mặc định) | `Assets/VFX/fx_t_smoke_02.png` | Fade |
| L4 | Streaks | Vệt gió mảnh quét quanh thân | Stretched Billboard, pivot (0,1,0) | Coloso Alpha (`_MainRIsAlpha` = 1) | `trail/trail_004.png` | Fade |

**Đổi theo review 2026-11-06:** bỏ lớp Gust (quạt đất, #3); mesh thân: `SM_VFX_Wind` (cung nằm, giống vệt chém) → `SM_VFX_Curve_Wave` (dải vòng) → phễu cao một khối (méo + chuyển động cứng) → **mảnh tường cong ngắn dựng đứng tự làm bằng Blender, spawn dày ngẫu nhiên** (#5; cách làm học từ rpg-game); dissolve ban đầu `noise_037` rồi đổi `noise_062`; texture chính `trail_001` → `trail_009`, noise méo `T_Noise_Smooth` → `noise_028` (art lead yêu cầu đổi); mép mềm + lắc noise (#1); bụi liền (#2).

**Học từ rpg-game** (`VFX_Book_Tornado`, `VFX_Tornado_Blade`, `Stupid_Tornado_Projectile`): không có mesh phễu cao nào. Lớp thân là `fbx_fx_cylinder_03` (mảnh tường cong ~200°) + `Tornado_vertical` (dải vòng ngắn r 0,32 / cao 0,29 m), spawn rate 25–30/s, sống 0,35–0,6 s, Start Rotation 3D X 70–110° + Y ngẫu nhiên, xoay quanh trục 50 rad/s, Size over Lifetime tách trục, Custom Data; thêm khói billboard lớn (fog_up / fog_down) và lá / hạt bay theo orbital velocity.

Khác với bản nào: effect gió đầu tiên của dự án; khác Slash360 (một cung dài) và IceSpike (khối đứng cố định) ở cả mesh, bố cục (cột xoáy nhiều cung) và timing (liên tục, tăng-giữ-tan).
Shader: không viết mới. Ngân sách: 4 material, 2 layer mesh Coloso, tối đa ~80 + 80 mảnh nhưng thực tế ~25 mỗi lớp cùng lúc. Mesh tự làm: `Assets/VFX/WindTornado/Meshes/SM_VFX_WindBand_A/B/C.fbx` (script `tools/blender/tornado_bands.py`).

## Ghi chú kỹ thuật
- Mesh `SM_VFX_Wind*` / `Curve_Wave` có sẵn nằm ngang (mặt XZ), mesh WindBand tự làm dựng đứng sẵn (trục Y). Luôn dùng Start Size đều (kéo không đều làm méo mesh).
- Quay quanh Y: Start Rotation 3D (Y ngẫu nhiên, X/Z nghiêng ±7°) + Rotation over Lifetime tách trục (Y). Mesh renderer alignment Local.
- Mảnh WindBand: u chạy dọc cung, v lên tường; texture cuộn nhanh theo u (`_MainFlowX`), alpha đỉnh làm mờ hai đầu và mép nên không dùng mask.
- Chưa vào `Included` của Showcase (chờ art lead duyệt).

## Tự review 2026-11-06 (project tạm `D:/tmp_w/scratch_wind`, build batch được khi Unity đang mở project chính)
- Bản dùng `trail_009` làm texture chính gần như vô hình (alpha ≤ 0,77, sợi mảnh, lại bị noise méo + dissolve cắt): đã đổi thân lốc sang `trail_033` (thân đặc).
- Mảnh tường quá thấp (0,25–0,55 m) nên cột mảnh: làm lại cao 0,45–0,95 m, tăng mật độ 34 → 40/s.
- Mới học từ rpg-game: spin giảm dần + size bật nhanh (chỉ tinh chỉnh). Chưa làm: lớp lá / hạt sáng bay quanh theo orbital giảm dần, vòng flare đất, khói billboard lớn; chưa thấy bản gốc chạy.
- UV của WindBand (2026-11-06): đo bằng Blender thấy tỉ lệ cung : cao lệch nhau (A 3,7 : 1, B 8,3 : 1, C 1,8 : 1) trong khi texture là 4 : 1, nên texture bị giãn / ép khác nhau giữa 3 mảnh. Đã sửa trong `tools/blender/tornado_bands.py`: u của mỗi mảnh = chiều dài cung / (4 × chiều cao) (A 0–1,0 · B 0–2,2 · C 0–0,48), nên cần Repeat theo u (`_MainClampX` = 0, texture Library import Repeat).
