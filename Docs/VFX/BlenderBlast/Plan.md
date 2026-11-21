# BlenderBlast — thử vụ nổ dựng bằng Blender MCP (2026-11-11)

Không gian (đã chốt, art lead chọn mặc định): ground · ~3 m (vòm cao ~2,5 m, sóng tới r 3,8 m) · camera 3/4 nhìn xuống 40° · neo điểm nổ · ~1,5 s một phát · lửa cam + khói xám · nền tối.
Cách làm (art lead chọn): **mesh hoạt hình** dựng bằng Python trong Blender 4.3 qua MCP (`mcp__blender__execute_blender_code`), 30 fps, frame 1–50.
Tạo hình: `Docs/VFX/_Anatomy/explosion.md` (tạo mới hôm nay).

Bất biến (chép từ anatomy): một chớp, một ngữ cảnh · thân là cụm khối sần đáy rộng có chiều cao, lửa trong lòng khói · nở nhanh – nguội – tan chậm · màu nóng → nguội.

| # | Lớp | Timing (frame @30) | Dựng |
|---|---|---|---|
| 1 | Flash | 1–6 | cầu sần r 1,7 m, emission vàng trắng, scale lên 2 frame rồi co |
| 2 | Thân (21 cụm × 3 trạng thái) | Hot 1–15 → Ember 6–22 → Smoke 10–50 | icosphere 4 + noise fractal (sần 0,22–0,3); bố cục: 10 cụm vành đáy r 1,1–1,6 · 7 giữa cao 1 m · 4 đỉnh 1,75 m; chuyển trạng thái bằng **đổi scale chéo** giữa 3 object cùng vị trí (vì màu vật liệu không xuất qua FBX); cụm trên bốc nhanh hơn; khói tan bằng co nhỏ |
| 3 | Shockwave | 1–12 | torus mảnh nằm đất, r 0,4 → 3,8 ease-out, dẹt dần |
| 4 | Đá văng | 1–34 | 12 viên sần, đạn đạo g 9,8, xoay, chạm đất dừng, co ở cuối |
| 5 | Tia lửa | 1–17 | 18 khối hộp kéo dài theo vận tốc (quaternion theo hướng bay), drag + trọng lực nhẹ |

File:
- `Assets/VFX/BlenderBlast/Mesh/SM_VFX_BlenderBlast.fbx` (animation baked, cho Unity; Unity chưa có glTFast)
- `Assets/VFX/BlenderBlast/Mesh/SM_VFX_BlenderBlast.glb` (bản tham khảo, giữ emission)
- `Assets/VFX/BlenderBlast/Source~/BlenderBlast.blend` (nguồn; `~` để Unity bỏ qua)
- Preview: `Docs/VFX/BlenderBlast/Preview_sheet.png` (frame 2, 4, 7, 10, 14, 20, 30, 42; EEVEE, camera 3/4 40°)

Chưa làm:
- Prefab `VFX_BlenderBlast` trong Unity: lúc làm, Unity MCP đang nối vào project khác nên chưa import. Cần: Animation Type Legacy (hoặc Generic + Animator), vật liệu Unity (Hot/Core/Ember/Flash/Ring/Spark = Additive hoặc Unlit emission, Smoke/Rock = Lit), Scaling Mode không áp dụng (không phải particle).
- Chưa vào `Included` (chờ art lead duyệt).

Bài học Blender MCP:
- Xoá object không xoá collection đang link vào scene → collection mới bị đặt tên `.001`; xoá collection rỗng trước khi dựng lại.
- `select_set` / `hide_set` trong ngữ cảnh addon không ăn khi xuất; gỡ collection preview khỏi scene rồi xuất cả scene.
- AgX làm lửa cháy trắng → view transform `Standard`, emission thấp (1,5–3).

Nhận xét tự review: đạt 4 bất biến. Yếu: lửa phẳng màu (chưa có gradient sâu), khói tan bằng co nhỏ chứ chưa ăn mòn thành sợi như GroundBlast, viền vòng sóng hơi dày.

---

## Thử 2 + 3 (2026-11-11): mô phỏng → flipbook

Cùng không gian (ground, 3/4 40°, nền tối). Sheet 8×8, ô 256 px, RGBA, 64 frame trải đều thời lượng nguồn. Camera **ortho** 3/4 40°, khung cố định bao trọn vụ nổ lúc lớn nhất.

| Sheet | Nguồn | Kết quả |
|---|---|---|
| `Textures/T_BlenderBlast_Sim_8x8.png` | Mantaflow tự bake (`Source~/BlenderBlast_Sim.blend`, `blast_sim.py`) | **hỏng**: cầu lửa nhỏ, khói tan sau ~20 frame, màu ngả xanh. Giữ để so, không dùng. |
| `Textures/T_VDB_GroundExplosion_8x8.png` | JangaFX Ground Explosion (frame 1–185) | nổ đất, cột khói nghiêng; lửa còn cháy trắng frame 5–12 |
| `Textures/T_VDB_GasolineExplosion_8x8.png` | JangaFX Gasoline Explosion (4–130) | cầu lửa → nấm khói tròn, hợp brief nhất |
| `Textures/T_VDB_MidairExplosion_8x8.png` | JangaFX Mid-Air Explosion (1–125) | lưỡi lửa phụt ngang rồi cuộn khói |

Preview trên nền tối: `Docs/VFX/BlenderBlast/VDB_*_preview.png`, `Sim_sheet_preview.png`. Nguồn VDB: `D:\Game_prj\_VDB\` (CC0). Lệnh render lại:
`blender -b --factory-startup -P Source~/vdb_render.py -- <thư mục VDB> <thư mục ra> 64 <frame đầu> <frame cuối> <độ đặc 15> <lửa 0.6–12> full <ngưỡng lửa>` rồi `python -I Source~/make_sheet.py`.

Còn yếu / việc tiếp:
- Vụ nổ chỉ chiếm ~40% ô (khung tính theo hộp lưới VDB, rộng hơn khói thật) → crop sát để tăng độ nét.
- Khói xám phẳng, thiếu khối sáng tối; lửa Gasoline / Mid-Air hơi nhạt; Ground cháy trắng.
- Chưa phân loại hướng (luật Library): Ground / Mid-Air **có hướng** (nghiêng / phụt một phía) → không spam, không xoay ngẫu nhiên; Gasoline gần như không hướng.
- Chưa dựng prefab particle (Frame over Time tuyến tính) và chưa vào Review Lab.
