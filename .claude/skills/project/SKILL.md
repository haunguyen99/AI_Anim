---
name: project
description: Mở Home, trang quản lý dự án chạy trên máy (tools/home, http://127.0.0.1:8780), và báo trạng thái công việc. Dùng khi người dùng gõ /project, muốn "mở Home", "mở trang quản lý", xem dự án nào đang có anim gì, anim nào đang làm hoặc chờ góp ý, hoặc vừa sửa trạng thái/tạo dự án/anim trên Home và muốn Claude nắm lại.
---

# /project: mở Home và báo trạng thái

Home là cửa vào của người dùng: Home → dự án (theo game) → anim → **Tiếp tục** mở Rig Lab / Pose Lab / Review Lab. Chạy trên máy này (một người dùng, dữ liệu nằm trên máy), không phải artifact. Dữ liệu là sổ `work/clips.json` (khóa `projects`, `characters`, `clips`). Trả lời bằng tiếng Việt.

## Khi gõ /project [tên dự án hoặc anim]

1. **Bật server và mở trang:** `preview_start` với `{name: "home"}` (cấu hình trong `.claude/launch.json`, cổng 8780). Nếu server đã chạy thì preview dùng lại. Người dùng tự mở ngoài Claude bằng cách bấm đúp `tools/home/start.bat`.
   Có tên dự án thì `navigate` tới `http://localhost:8780/#/p/<id dự án>` (id trong `projects` của sổ, vd `boss_gaygor`, `shoot_die_repeat`).
2. **Đọc trạng thái:** `curl -s http://127.0.0.1:8780/api/state` (hoặc đọc `work/clips.json` nếu server không lên). Mỗi clip có `status` (working / waiting / done / paused = tạm dừng), `status_manual` (người dùng chọn tay), `stage`, `note`, `review_latest`/`pose_latest`, `continue` (trang mở khi bấm Tiếp tục).
3. **Báo ngắn gọn theo dự án:** số anim, xong / chờ góp ý / đang làm / tạm dừng; liệt kê anim chưa xong với giai đoạn, bản mới nhất, việc tiếp theo (chờ góp ý → `/check_fb <clip>`; chưa có trang → `/new_clip <id>`; nhân vật chưa có rig → `/rig`).
4. **Thay đổi người dùng vừa làm trên Home:** `git diff work/clips.json`. Có thay đổi thì nêu lại (anim nào, đổi gì) và commit kèm lý do (`Home: user set ...`). Clip mới tạo từ Home (note "Mới tạo từ Home", có `work/<id>/brief.md`) → nhắc gõ `/new_clip <id>`.
5. **So với MAP:** nếu sổ lệch với bảng "Đang làm gì" của `MAP.md` (vd bản mới nhất trên Review Lab cũ hơn bản MAP ghi) thì nói ra, không tự sửa trang Lab.

## Quy tắc

- Không ghi đè thay đổi người dùng làm trên Home: luôn xem `git diff work/clips.json` trước khi sửa sổ.
- `status` người dùng chọn tay thì giữ nguyên; chỉ đổi `stage`/`note` bằng `clip_registry.py` khi công việc thực sự qua giai đoạn.
- Giữ `note` ngắn, có chữ "chờ" khi đợi góp ý, để Home đoán đúng trạng thái.
- Sửa giao diện hoặc server Home: `tools/home/index.html`, `tools/home/server.py`; kiểm bằng preview `home`, cập nhật `review_process.md#home-app` và MAP.
