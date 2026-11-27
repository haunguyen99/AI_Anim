# Công cụ web của dự án

## Shape Lab (art lead tạo hình bằng tham số)
- File gốc: `Docs/VFX/_ArtDirection/tools/shape_lab.html`. Bản đăng: https://claude.ai/artifact/BAbVif8XRDWGL2Gt7Xkk9F (giữ URL này).
- Chạy local: server `shape-lab` trong `.claude/launch.json` (cổng 8765); file:// không nạp được `shape_library.js`.
- Thư viện hình: `tools/shape_library/library.json` + mask theo nguyên tố; build ra atlas `_atlas/`. Thêm hình: `python shape_library.py add <img> --element <id> --name "..."`.
- Đăng lại: page + `shape_library.js` + `_atlas/*.png`, `root` = tools, ≤ ~35 file mỗi lần.
- Art lead dán JSON "Copy thông số" vào chat: đọc như ý định hình dáng chính xác.
- Art lead sửa / xoá hình trong Lab (artifact db, collection `libEdits`). "Áp dụng chỉnh sửa" = `python shape_library.py apply-edits <json>` rồi đăng lại.

## Review Lab (xem effect không cần Unity)
- `python -I .claude/skills/vfx-maker/review-lab/build_review.py --project . [--effect Tên]` → `Docs/VFX/_Review/index.html`.
- Bản đăng: https://claude.ai/artifact/DKQDnM9vtH8iNXaLUkURoN. Bản tự chứa > 16 MB nên đăng bản `--link` + ảnh qua `files`, từng đợt ~25–35 file.
- Phản hồi art lead xuất ra từ nút "Xuất phản hồi": mỗi ghim = một yêu cầu sửa cụ thể.

## Mix Lab (xem / tinh chỉnh mix thành phần)
- `Docs/VFX/_ArtDirection/tools/mix_lab/mix_lab.html`. Bản đăng: https://claude.ai/artifact/CMFUvsBJ6YeqapsMZoNwbt.
- Dữ liệu: `MixCapture` chụp mỗi prefab CMP_* (chạy lại sau khi đổi thành phần).
- Recipe → `MixRecipeBuild.BuildBatch -recipe Docs/VFX/_Recipes/<tên>.json` → `Assets/VFX/Mixes/<tên>/`.

## Blender
- MCP `blender` trong `.mcp.json` (addon thường không chạy). Chạy headless: `blender.exe -b --factory-startup --python <script> -- <args>` (Blender 4.3 ở `D:/download/blender-4.3.0-windows-x64/`).
