# Tornado / cột gió — làm theo `Stupid_Tornado_Projectile` (rpg-game)

Art lead chọn prefab này làm chuẩn (2026-11-06). Ví dụ làm xong: `Assets/VFX/WindTornado/` (builder mẫu `assets/TornadoBuild.example.cs`, plan `Docs/VFX/WindTornado/Plan.md`, ảnh + dump bản gốc `Docs/VFX/WindTornado/ref_*`). **Không** tự làm mảnh tường bằng Blender, **không** dùng một mesh phễu cao (`tornado_mesh`) làm thân: cả hai đã thử và bị bỏ (v1, v2).

Trước khi làm: đọc [study-reference.md](study-reference.md) (copy + render + dump bản gốc). Prefab gốc: `D:\Projects\rpg-game\Assets\_Game\Resources_moved\Prefabs\Projectile\Stupid_Tornado_Projectile.prefab`. Họ hàng: `VFX_Book_Tornado` (thân = một hạt phễu `tornado_mesh` + shader `Thrust`, đã thử, kém hơn), `VFX_Tornado_Blade`.

## Cách bản gốc hoạt động
- **Mesh**: `fbx_fx_cylinder_03` = vành hở ~340°, bán kính 0,59 m, cao 0,27 m, UV 0..1 vòng quanh / theo chiều cao. `Tornado_vertical` = ống r 0,32, cao 0,29 m.
- **Shader** `Shader Graphs/Fx_dissolve_particle_apb` (có BuiltInTarget; ở `Assets/VFX/_Imported/RpgGame/ShaderGraph/`). Sheet **đóng gói kênh**: R = độ sáng màu, G = trường tan / highlight, B = méo UV, A = alpha.
  - Custom1 = (tan 0→1, độ gắt mép ~20, độ méo UV, –); Custom2 = màu highlight (trắng); màu thân = Start Color × R.
  - Highlight_Min −10, Highlight_Max −2 (mép tan lóe trắng), Emission_Power 1, soft particles tắt (bật cho lớp sáng).
  - Stream: `Position, Normal, Color, UV, UV2, Custom1XYZW, Custom2XYZW`. Material queue 3025 (3027 cho lớp splash).
  - Tên thuộc tính (reference name): `Main_tex`, `Vector1_930B327D` (Highlight_Min), `Vector1_270105AC` (Highlight_Max), `Boolean_9C0948F4` (soft particles), `Vector1_2C5A3101` (Emission_Power).

## Các lớp (số của họ; × K, K = 0,5 cho cột cao ~3,6 m)
| Layer | Số chính | Mesh / texture |
|---|---|---|
| Wind (root) | life 0,35–0,5 s; speed 4–6 (Cone angle 0, rot −90° X → lên); size 5–7; start rot 3D X 70–110°, Y 0..360°; Rotation over Lifetime Z 18,85 rad/s × curve 1→0 (x, y là curve 0); Size over Lifetime tách trục: x,y (0,0)(0,14;0,38)(1,1), z ×1,5 (0,0)(0,15;0,61)(1,1); alpha 1→0; rate 25/s; Start Color `06FFDF`; TSA 4×4 frame 0,875–1 (ô 14–15) | `fbx_fx_cylinder_03`; `Tex_fx_elements_set_01.tga` (không có trong Library: dùng bản nhập `_Imported/RpgTornado`) |
| SharpRing | life 0,2–0,35; Box scale (0,01; 1; 0,01) pos y 0,5; velocity y 1–5; size 3–5; Size over Lifetime x,y 0,5→1, z ×0,5 (0,67→0); TSA 3×6 frame 0,444 (ô 8); soft particles bật | cùng mesh; `Library/impact/impact_071.tga` (= splash set) |
| Tubes | GameObject rot X 270°; speed 8; size 3D (3, 3, 15); life 1; rate 10; rotation z 6,98 rad/s; Size over Lifetime x,y ×3 (0,09→1), z (0,18→0,74); alpha (0,0)(0,14;0,59)(0,49;0,24)(1,0); màu `69B4FF`..`DCF2FF`; Mobile/Particles/Additive | `Tornado_vertical`; `Library/wave/wave_070` (= Wind01) |
| MistUp | y 0,35; rot (0,270,90); Circle arc 7,5° bán kính ~0; speed 5; size 5 × curve ×1,5 (0,11→0,52→1); life 1,3; rate 10; màu trắng A 0,65; alpha (0,0)(0,11;1)(0,52;0,49)(1,0); Alpha Blended | Billboard; `Library/smoke/smoke_010` (= Dust01) |
| MistFoot | Billboard + Local, GameObject xoay X 90° (không Horizontal Billboard); size 8–10; life 0,7; Additive; size 1→0; màu `AAB2FD`..`ACF9FF` alpha ~0,4–0,6 | smoke_010 |
| Smoke | world space; Cone r 2,2 angle 45; speed 3–5; size 3,5–5; gravity −1..−0,5; màu `BABABA`→trắng, alpha 0,08→0; Custom1 (0→1, 0→20, 0→−0,1); TSA 4×4 ô 10 | Billboard, Graph |
| Bits | 8×8 ô 19; size 0,3–0,5; speed 1–13; Cone r 2 angle 45; orbital Y ×20 (−0,5→0); Size over Lifetime nhấp nháy; Start Color `0080FF`; Custom2 trắng | Billboard, Graph |

Họ có thêm `particle_dark`, `smoke_spread`, `leaf` (tắt sẵn / phụ): bỏ.

## Hướng mesh (đọc trước khi đặt Start Rotation)
- Trong Unity, ba mesh của rpg-game đều có **trục vành / phễu trên Z** (log của `Describe()`: "revolution axis ~ Z"): `fbx_fx_cylinder_03` (bounds 0,70 × 1,17 × 0,27: trục là chiều nhỏ nhất), `Tornado_vertical` (0,64 × 0,64 × 0,29), `tornado_mesh` (2,01 × 2,00 × 2,42: phễu cao theo Z).
- Vì vậy: vành **nằm ngang quanh cột đứng (trục vành thẳng đứng) = Start Rotation X 90°** (±~20° nghiêng; bản gốc dùng X 70–110°, chính là tín hiệu này). Phễu `tornado_mesh` dựng đứng = X −90° + Y 90°. Ống `Tornado_vertical`: GameObject xoay X 270°. Start Rotation X ≈ 0 làm trục vành chĩa dọc hướng nhìn.
- **Lỗi đã gặp (FireTornado, art lead sửa tay 2026-11-06):** đặt Whips X ±11° với giả định "trục là Y" nên sai hướng; đúng là X = 90°, Z = 0, Start Size 3D (2, 2, 3). Với mesh chưa từng dùng: đọc bounds, đặt thử 0° / 90° rồi **xem** preview trước khi chốt.
- Mesh tự làm trong Blender xuất đúng trục Y (Blender Z → Unity Y) khi dùng đúng setting xuất; mesh nhập từ nguồn khác thì phải đo, không đoán.

## Khác bản gốc (có chủ ý)
- Bản gốc là **đạn** (phun 1,5 s với rate 1→0 rồi tàn). Tornado **đứng yên**: rate lên 0,3 s, giữ, giảm về 0 (`Rate()` trong builder); `Emit` = 2,6 s, cả effect ~3,9 s.
- Horizontal Billboard → Billboard + Local (luật art lead).
- Muốn bay như đạn: `VfxPathMover` / `focusOffset` của Showcase.

## Biến thể
**Đã làm: `FireTornado`** (`Assets/VFX/FireTornado/`, `Docs/VFX/FireTornado/Plan.md`): thân = một phễu `tornado_mesh` + Thrust (không phải vành rời), dải lửa dựng đứng leo lên, sụp + đợt tàn lửa, khói nhiệt, quầng cháy đất. Cho thấy cách khác cả bốn thứ mà không cần prefab tham chiếu riêng: dùng lại mesh / shader nhập của họ làm "linh kiện" (xem `assets/TornadoBuild.example.cs` cho kiểu vành + Graph, `assets/TornadoFireBuild.example.cs` cho kiểu phễu + Thrust).

Lửa / băng / độc / sét… vẫn là cùng hiệu ứng nhưng đổi ≥ 2 trong mesh / bố cục / timing / lớp phụ (không chỉ đổi màu). Màu: đổi Start Color của Wind / Tubes / Mist, giữ nguyên số. Gợi ý: lửa = thêm lớp tia lửa + Custom2 vàng; băng = rate thấp hơn, thêm mảnh pha lê, vành quay chậm hơn.

## Lỗi đã gặp
- Thân dựng bằng mảnh Blender hoặc một phễu cao: không ra cột xoáy (v1, v2).
- Hồng trong project tạm = thiếu `com.unity.shadergraph` (thêm vào manifest).
- Rotation / Size / Velocity over Lifetime lệch kiểu curve giữa các trục: Unity bỏ qua module. Builder mẫu dùng `Spin()` / `SizeXYZ()` để ép mọi trục cùng kiểu curve.
- Trùng GUID `Fx_dissolve_particle_apb.shadergraph` giữa `_Imported/RpgGame/ShaderGraph` và bản copy: xoá bản copy.
- Unity đang mở project chính: build ở project tạm (`D:/tmp_w/scratch_wind`, cần các texture Library ở bảng trên và `_Imported/RpgTornado`), rồi art lead bấm **VFX → WindTornado → Build**.
