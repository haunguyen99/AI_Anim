# Slash360: biến thể Lửa và Nước (2026-11-09)

Cùng hiệu ứng với `Slash360_Earth`: một vệt chém xoay 360° quanh nhân vật, mesh + UV, bộ shader Coloso, texture xám, màu từ ramp / Color over Lifetime, `_MaskTex` = `T_VFX_Gradient_01`, stream `Custom1XYZW`. Không gian: dir, camera topdown 60° (preview), neo nhân vật, nền tối. Art lead để mình chọn nguyên tố + chất liệu.

Builder: `Assets/VFX/Slash360/Editor/Slash360FireBuild.cs`, `Slash360WaterBuild.cs`, dùng chung `Slash360VariantKit.cs` (bản sao helper của `Slash360Build.cs`, không sửa file gốc). Menu `VFX/Slash360/Build Fire` và `Build Water`; `BuildBatch` có ở cả hai. Prefab: `VFX_Slash360_Fire`, `VFX_Slash360_Water`.

| | Earth (gốc) | Fire | Water |
|---|---|---|---|
| Mesh | `Slash_Circle_Thin` (vành mảnh) | **`Slash_Circle`** (đĩa rộng, lỗ nhỏ) | **`Curve_Wave`** (vành lượn sóng) |
| Bố cục | nghiêng X 25°, cao 1 m, R 2 m | **nghiêng X −20° + roll 15°, cao 1,2 m, R 2,2 m** | **nghiêng 8° (gần ngang), cao 0,8 m, R 2,3 m** |
| Timing | 0,35 s, đầu chạy đều | **0,42 s, đầu chậm rồi quất nhanh (ease-in)** | **0,5 s, đầu lao nhanh rồi chậm (sóng đập)** |
| Lớp phụ | mảnh đá, chớp đầu | **tàn lửa bay lên cả vòng, khói nóng sẫm, chớp đầu** | **giọt nước văng rồi rơi, sương thấp, bọt mép trắng (không chớp)** |
| Shader | Cutout | Additive + ramp lửa | Alpha (méo noise) + Additive cho mép / vệt |

Mỗi biến thể đổi cả 4 trục; mesh thì cả hai khác Earth.

Texture (từ `Assets/Library/Slash/Main_tex(Uvmesh)/`, builder tự copy file, không copy `.meta`, vào `Assets/VFX/Slash360/Textures/`):
- Fire: `Slash_Main_tex_Uvmesh_005.png` (lưỡi lửa, đầu bên trái, đuôi răng cưa) → `T_Slash360_Fire_Main.png`.
- Water: `Slash_Main_tex_Uvmesh_016.png` (đầu tròn, đuôi sọc) → `T_Slash360_Water_Main.png`.
- Import `alphaFromGray` chỉ để qua kiểm tra alpha-blend của kit; shader đọc kênh R (`_MainRIsAlpha` = 1).
- Ramp lửa `T_Slash360_Fire_Ramp.png` do builder sinh (đối xứng theo bề rộng nên không phụ thuộc chiều v của mesh): ngoài #660D00, giữa #FF6100, lõi #FFE073.
- Dùng lại file chung của Earth (chỉ đọc): `T_VFX_Gradient_01`, `T_Slash360_Detail_Trail`, `T_Slash360_EdgeCrescent_Earth`, `T_Slash360_Glow`, noise `T_Noise_Smooth`; khói `fx_t_smoke_02`.

Màu Nước (Color over Lifetime): lõi #E0FAFF, giữa #33A6FF, ngoài #0A38B3.

Chưa kiểm tra bằng Unity (Editor đang mở, không batch được):
- Chiều chạy và vị trí đường nối u của `Slash_Circle` / `Curve_Wave` (đoán từ ảnh `Mesh_candidates.png`). Chớp đầu của Fire đặt ở +z; Nước không có chớp để khỏi lệch. Tàn lửa / giọt nước rải ngẫu nhiên cả vòng, không bám đầu, nên không phụ thuộc chiều.
- Bán kính ngoài: builder tự đo `mesh.bounds` rồi scale về R, và log bounds ra Console (kiểm tra mesh phẳng XZ).
- Hình lưỡi liềm trên đĩa rộng (Fire) và vành sóng (Water): xem preview sau Build rồi chỉnh `Window`, `Radius`.
