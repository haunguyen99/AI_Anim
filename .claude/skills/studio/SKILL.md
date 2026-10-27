---
name: studio
description: Mở AI Anim Studio, ứng dụng tổng hợp chạy trên máy (http://127.0.0.1:8780): một viewport chung, Mesh / Rig / Pose là các workspace. Dùng khi người dùng gõ /studio, nói "mở Studio", "mở app", "mở viewport", hoặc muốn mở một nhân vật / workspace cụ thể (vd "/studio zom1", "/studio pose").
---

# /studio: mở Studio

Studio là tool chính: mở `http://127.0.0.1:8780` là vào thẳng viewport với **cảnh trống** (ô giữa viewport: Nhập FBX, Mở nhân vật, mở nhanh nhân vật đã có). Home (dự án → anim) ở `/home`. Mã ở `tools/studio/`, thiết kế và lộ trình ở `docs/studio_design.md`. Trả lời bằng tiếng Việt, ngắn.

## Khi gõ /studio [nhân vật] [workspace]

1. **Bật server:** `preview_start` với `{name: "home"}` (`.claude/launch.json`, cổng 8780; đã chạy thì dùng lại). Ngoài Claude người dùng bấm đúp `tools/home/start.bat`.
2. **Chọn trang:**
   - Không có tham số → `http://localhost:8780/` (cảnh trống; bước 3 chỉ kiểm ô Cảnh trống hiện, không đợi mesh).
   - Có nhân vật → lấy id từ `curl -s http://127.0.0.1:8780/api/chars` (khớp id hoặc tên, không phân biệt hoa thường, khớp một phần được: "zom1" → `zom1_map1`) → `http://localhost:8780/studio/<id>`. Không khớp thì liệt kê các nhân vật đang có.
   - Có workspace (`mesh`, `rig`, `pose`) → thêm `?ws=<workspace>`.
   - Có tên anim (id trong `work/clips.json`) → mở nhân vật của anim đó, thêm `&clip=<anim>`.
   `navigate` tới trang đó trong tab preview.
3. **Kiểm nhanh:** `javascript_tool` đọc `ST.char.name`, `ST.ws`, số mesh `ST.mods.mesh.objects().length` (đợi tới khi > 0, tối đa ~5 s); lỗi thì xem `read_console_messages` và `preview_logs`.
4. **Báo:** một dòng: đã mở nhân vật nào, workspace nào, link `http://127.0.0.1:8780` (người dùng mở được trong trình duyệt của họ khi server còn chạy). Nhắc ngắn những gì chưa có nếu người dùng hỏi tới: workspace Rig / Pose còn trỏ sang Lab cũ (bước S3–S5).

## Quy tắc

- Chỉ mở và xem: không bấm lệnh sửa mesh trên kho thật (`<nhân vật>_mesh_lab`, Rig Lab đọc kho này). Cần thử thao tác thì dùng `?ns=studio_test_<x>` rồi xoá `work/store/studio_test_*`.
- Sửa Studio: thêm lệnh bằng `ST.cmd` trong module, cấu hình workspace ở `tools/studio/workspaces.js`; cập nhật `docs/studio_design.md` và `MAP.md`.
- Chỉ chụp màn hình khi người dùng yêu cầu: họ xem trang trực tiếp. Kiểm bằng `javascript_tool` / `read_page`, báo bằng chữ (xem `CLAUDE.md`).
