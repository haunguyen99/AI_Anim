# Blender: mô phỏng + VDB → flipbook (2026-11-11)

Học được khi làm `BlenderBlast` (Plan: `Docs/VFX/BlenderBlast/Plan.md`). Script: `Assets/VFX/BlenderBlast/Source~/` (`vdb_render.py`, `vdb_probe.py`, `make_sheet.py`, `blast_sim.py`).

## Nguồn VDB miễn phí
- JangaFX free VDB (EmberGen), **CC0**: https://jangafx.com/software/embergen/download/free-vdb-animations (15 gói, file trên MediaFire).
- Đã tải 3 gói nổ vào `D:\Game_prj\_VDB\` (ngoài project): Ground Explosion (200 frame, kênh density/flames), Gasoline Explosion (131 frame, + temperature), Mid-Air Explosion (126 frame).
- Đã Z-up, đáy chạm đất; đơn vị ~voxel → scale 0,01 cho ra ~2,5–3,5 m.
- MediaFire: link tải thật nằm trong trang (`download*.mediafire.com/...`); có gói curl lấy được, có gói phải mở trang bằng trình duyệt mới thấy link.

## Render VDB bằng EEVEE (Blender 4.3) — bẫy đã gặp
- **Alpha của khối volume luôn = 1** (film transparent không tác dụng khi có VDB). Cách làm: render mỗi frame 2 lần (nền đen / tấm emission trắng 1.0 sau vụ nổ), `alpha = 1 − mean(trắng − đen)`, `màu = đen / alpha`. Tấm nền tắt `visible_shadow`.
- **Camera ortho + clip range lớn → khói đen** (froxel quá thô, ánh sáng không vào). Đặt `clip_start/end` và `eevee.volumetric_start/end` sát quanh vụ nổ (ví dụ 44–58 m với camera cách 50 m).
- View transform `Standard` (AgX làm lửa cháy trắng).
- Emission từ `flames`: Map Range (ngưỡng 0,08–0,15 → 1) rồi mũ 1,5; không ngưỡng thì cả đám khói nguội phát cam.

## Mantaflow
- Bake trong Blender của người dùng qua MCP được (~3 phút ở res 110), nhưng **đọc `domain_settings.density_grid` / `flame_grid` làm Blender crash** (cả UI lẫn `-b`). Không đọc lưới.
- `bake_all` báo "Dependency graph update requested during evaluation" khi viewport đang Rendered → chuyển Solid trước.
- Kết quả res 110 vẫn nhỏ, khói tan sớm; không bằng VDB có sẵn. Ưu tiên VDB.

## Blender MCP
- Xoá object không xoá collection đã link → tên mới bị `.001`; xoá collection rỗng trước khi dựng lại.
- `select_set` / `hide_set` không ăn khi xuất từ addon; gỡ collection khỏi scene rồi xuất.
- Việc nặng (bake, render nhiều frame) chạy bằng Blender nền: `blender.exe -b --factory-startup -P script.py -- args`.
