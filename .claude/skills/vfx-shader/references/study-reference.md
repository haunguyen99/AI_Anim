# Học từ prefab tham chiếu (rpg-game hoặc nguồn khác) — làm đủ bước

Art lead (2026-11-04, 2026-11-06) đã từ chối hai lần cách "đọc số trong prefab rồi tự dựng": WindTornado v1 / v2 sai hướng vì chưa chạy bản gốc, rồi art lead dặn "đọc thật kĩ cách setup, mesh, texture". Khi brief nói "học theo / làm giống prefab X" hoặc chỉ tên một prefab:

## 1. Tìm và copy bản gốc
- Tìm prefab trong `D:\Projects\rpg-game\Assets` (Glob theo tên). Tìm cả prefab họ hàng (`VFX_Book_Tornado`, `Stupid_Tornado_Projectile`…): đọc hết, hỏi art lead cái nào là chuẩn nếu chưa nói.
- Copy prefab + mọi thứ nó dùng (material, shader, texture, mesh, prefab lồng) **giữ GUID**: `python -I scripts/copy_closure.py <src Assets> <dst> <đường dẫn prefab> [...]`. Script bỏ `.cs`. Bản copy vào project chính để ở `Assets/VFX/_Imported/<Tên>/` (đường dẫn con giữ nguyên). Cẩn thận trùng GUID với bản đã nhập (ví dụ `Fx_dissolve_particle_apb.shadergraph` đã có ở `_Imported/RpgGame/ShaderGraph`): xoá bản trùng.
- Render ở **project tạm** khi Unity đang mở project chính (SKILL mục 7).

## 2. Render + dump đủ
- Chép `assets/RefRender.example.cs` vào `Assets/<...>/Editor/RefRender.cs` của project tạm (cần `_Kit` vì dùng `VfxBuildKit.CaptureSheet`). Đặt biến môi trường `REF_PREFAB` (đường dẫn Assets/...), `REF_OUT` (đường dẫn file không đuôi), `REF_TIMES` (ví dụ `0.2,0.5,1,2`), `REF_CAM` (`x,y,z,lookX,lookY,lookZ`), `REF_SIZE`, rồi chạy `Unity -batchmode -quit -projectPath <tạm> -executeMethod VfxEffects.RefRender.Run`. Ra `.png` (sheet các mốc thời gian) và `.txt` (dump). Mỗi lệnh Bash mới phải đặt lại biến môi trường.
- Dump có: main (life, speed, size 3D, rotation 3D, **màu start thật**, space, scaling, max), emission (rate curve, burst), shape, mọi module (velocity gồm orbital / radial, rotation, size, color, noise, force), **Custom Data 1/2 (cả màu)**, **TSA (grid / sprites, số ô, dải frame, start frame, danh sách sprite)**, **vertex stream**, renderer (mode, alignment, mesh, pivot, sorting), material (shader, queue, thuộc tính, texture, keyword).
- Chụp một lần camera gần, một lần camera rộng, nhiều mốc thời gian (kể cả cuối). Lưu ảnh + dump vào `Docs/VFX/<Effect>/ref_*`.

## 3. Hồng ≠ bỏ qua
- Material hồng / `Hidden/InternalErrorShader` = chưa biên dịch được shader, **không phải** lý do bỏ lớp đó. Shader viết tay (CG) thường chạy ngay (ví dụ `Thrust`). **Shader Graph** có `BuiltInTarget` (đọc `m_ActiveTargets` trong `.shadergraph`) chạy được ở Built-in nếu project có `com.unity.shadergraph`: thêm `"com.unity.shadergraph": "14.0.12"` vào `Packages/manifest.json` của project tạm (project chính đã có). Chỉ Shader Graph URP-only / OmniShade mới thật sự không dùng được.
- Sheet texture của họ có thể **đóng gói kênh** (R / G / B / A mỗi kênh một vai trò) nên ảnh không nói gì về hình hiển thị. Đọc đồ thị: parse `.shadergraph` (nhiều đối tượng JSON nối nhau; `m_Edges` nối slot; SampleTexture2D slot 4 / 5 / 6 / 7 = R / G / B / A; UV channel 1 = Custom1, channel 2 = Custom2), hoặc chỉ cần render. Vẽ lưới có số ô (PIL) để biết frame nào là ô nào (frame = floor(f × số ô)).

## 4. Đọc mesh và texture
- Mesh: đo bán kính / cung / cao / UV bằng Blender nền (`bpy`: `me.vertices`, `uv_layers.active.data`) hoặc `mesh.bounds` trong Unity. Không đoán từ tên (`tornado_mesh` là phễu đồng hồ cát cao 2,42 m; `fbx_fx_cylinder_03` là vành hở 340° cao 0,27 m).
- **Hướng mesh:** log `mesh.bounds` + trục xoay trong Unity (`Describe()` ở `assets/TornadoFireBuild.example.cs`); đối chiếu với Start Rotation của bản tham chiếu (X ≈ 90° / 270° nghĩa là trục mesh không phải Y). Không giả định trục là Y.
- Texture: xem từng ô; kiểm tra có sẵn trong `Assets/Library/` không (`Docs/VFX/_Library/library_index.csv` có tên cũ / tên gốc → đường dẫn hiện tại; so md5). Dùng bản Library, thiếu mới dùng bản nhập.

## 5. Dựng
- Dùng **mesh + shader của họ trước**, số của họ (đánh dấu `// [ref]` trong build script), nhân một hệ số K theo quy mô đã chốt. Chỉ tự làm mesh / shader khi họ không có.
- So preview của mình với ảnh bản gốc. Khác có chủ ý (ví dụ đạn → đứng yên) ghi trong Plan.
- Mọi trục của Velocity / Rotation / Size over Lifetime phải cùng kiểu curve (Constant / TwoConstants / Curve / TwoCurves): lệch thì Unity bỏ qua module mà không báo lỗi.
