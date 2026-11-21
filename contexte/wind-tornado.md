# WindTornado: bài học (2026-11-06)

- **Bản chốt hiện tại (v3)** = prefab `Stupid_Tornado_Projectile` của rpg-game làm lại layer theo layer (xem `Docs/VFX/WindTornado/Plan.md`). Art lead chỉ định prefab này và dặn "đọc thật kĩ từ cách setup và mesh, texture".
- **Prefab rpg-game dùng Shader Graph vẫn render được ở Built-in** nếu graph có BuiltInTarget (kiểm tra `m_ActiveTargets`) và project có `com.unity.shadergraph`. Hồng ≠ không dùng được: thêm package vào project tạm rồi render lại. Sheet texture của họ **đóng gói kênh** (R tone, G tan / highlight, B méo UV, A alpha) nên nhìn ảnh gốc không ra hình hiển thị; phải giải đồ thị (script đọc `.shadergraph`, nối slot theo `m_Edges`) hoặc render.
- Đọc một prefab tham chiếu cho đủ: số module (dump), **màu start thật**, Custom1 / Custom2, vertex stream, TSA (kể cả chế độ Sprites: texture nằm ở danh sách sprite, material không có), ô nào của sheet (frame = floor(f × số ô)), mesh (bán kính / cung / UV), queue material, ảnh render.

- **SAI ở bản đầu, đã sửa (2026-11-06):** ghi "rpg-game không có mesh phễu" là nhầm. `VFX_Book_Tornado` dùng `RPG_VFX/Mesh/tornado_mesh.fbx` (phễu đồng hồ cát 2 × 2 × 2,42 m): thân lốc là **một hạt** mesh này (sống 10 s, xoay 1 vòng/s) + shader `Thrust` cuộn noise `wind_tex`; chuyển động mềm do shader (noise cuộn), không do mesh cứng. Mình đã đọc tham số rồi tự làm mesh Blender mà không chạy / không xem bản gốc nên đi sai hướng. **Bài học: học từ tham chiếu = copy prefab + dependency (`tools/py/copy_closure.py`), render + dump (`tools/py/RefRender.cs.txt`), xem ảnh, dùng mesh / shader của họ trước; chỉ tự làm khi họ không có.**
- Mảnh tường tự làm (`tools/blender/tornado_bands.py`) và cách nhiều mảnh ngắn (`fbx_fx_cylinder_03`, `Tornado_vertical`) vẫn là phụ: `Tornado_vertical` thành lớp Rings.
- **Spin giảm dần + size "bật ra" nhanh** (curve, không phải hằng số) là thứ làm chuyển động mềm (rpg-game: rot speed 1→0, size 0→0.38 ở 14% đời →1).
- **Velocity / Rotation over Lifetime: mọi trục phải cùng kiểu curve** (Constant / TwoConstants / Curve / TwoCurves). Lệch kiểu thì Unity bỏ qua module, hạt không bay và không báo lỗi (WindTornado từng thành đĩa đồng tâm vì x,z hằng số còn y là khoảng).
- **Hướng mesh phụ thuộc file, không mặc định là Y** (cập nhật 2026-11-06). Mesh tự xuất từ Blender đúng setting thì Blender Z → Unity Y (`SM_VFX_Wind*` nằm ngang trong XZ), nhưng mesh nhập của rpg-game (`fbx_fx_cylinder_03`, `Tornado_vertical`, `tornado_mesh`) có trục vành / phễu trên **Z**: vành nằm ngang quanh cột phải Start Rotation X 90°. Luôn đọc `mesh.bounds` + trục xoay trước khi đặt rotation (xem `vfx-shader/references/tornado.md` mục "Hướng mesh").
- **Không dùng Start Size 3D để kéo cao mesh** (méo): đưa tỉ lệ thật vào mesh, Start Size đều.
- Blender 4.3 chạy nền: `bpy.ops.object.shade_smooth` và `read_factory_settings` lặp lại sau khi xuất FBX có thể crash; dùng `poly.use_smooth` và tạo color attribute sau khi gán UV + `me.update()`.
- Unity đang mở project thì không chạy batchmode được: nhờ art lead bấm menu **VFX → WindTornado → Build**.

## Công thức làm tornado lần sau (2026-11-06)
Chi tiết ở memory `tornado-recipe`; tóm tắt:
1. Học từ prefab tham chiếu **đủ bước**: `tools/py/copy_closure.py` (copy theo GUID) → render + dump bằng `tools/py/RefRender.cs.txt` trong project tạm (thêm `com.unity.shadergraph` 14.0.12 nếu tham chiếu dùng Shader Graph) → xem ảnh + từng ô texture + UV mesh → dựng.
2. Mẫu chuẩn = `Stupid_Tornado_Projectile`: vành gió `fbx_fx_cylinder_03` (Graph shader, sheet đóng gói kênh, Custom1 = tan / độ gắt / méo, Custom2 = màu lóe) + vành sáng + ống `Tornado_vertical` Additive nở rộng + cột sương + sương chân (Billboard + Local, không Horizontal) + khói + vụn. Số của họ × K (K = 0,5 → cao ~3,6 m). Builder chạy được: `Assets/VFX/WindTornado/Editor/WindTornadoBuild.cs` (dòng `[ref]` = lấy thẳng từ dump).
3. Tornado đứng yên (không phải đạn): emission lên 0,3 s, giữ, giảm; đạn thì 1 → 0.
4. Biến thể (lửa, băng, độc…): vẫn là cùng hiệu ứng; đổi ≥ 2 trong mesh / bố cục / timing / lớp phụ, không chỉ đổi màu.
