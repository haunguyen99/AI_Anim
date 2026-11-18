---
name: project-assistant-ngocvb-linux
description: Trợ lý cá nhân (/assistant) trên máy Linux của ngocvb — chủ cấu hình được, cách bật, bẫy phòng You
metadata:
  type: project
---

Trợ lý cá nhân `tro-ly` (tools/tro_ly.py) chạy trên máy Linux bằng tài khoản **ngocvb** (@ngocvb:localhost, "Vũ Bích Ngọc"), bật 2026-11-18, phiên Paseo c64245a.

- Chủ trợ lý đọc từ biến `TRO_LY_OWNER` > file `tools/.tro_ly_owner` (git-ignored, riêng từng máy) > mặc định `haunv`. Brief tự đổi tên Hậu/haunv thành chủ khi tạo phiên; bộ canh nền dùng file hậu tố `_<chủ>`.
- Khóa: `tools/horuschat_mcp/.env.<chủ>` (HORUSCHAT_API_KEY), `tools/workai/.env.<chủ>` (WORKAI_TOKEN). File tên bắt đầu dấu chấm bị ẩn trong trình quản lý file: Ctrl+H.
- `paseo_cmd.py` giờ tìm paseo ở PATH / ~/.local/bin trên Linux (trước chỉ có đường dẫn Windows).
- Phòng "You": tài khoản mới có thể có phòng nhắn-cho-chính-mình **không có tên** (member_count 1, is_direct). `tro_ly.py room` chỉ tìm theo tên nên không thấy; tìm phòng một thành viên rồi `room --set <room_id>`.

**Why:** máy mới / người mới dùng trợ lý không cần sửa code, chỉ đặt chủ + khóa.
**How to apply:** máy mới: ghi tên vào tools/.tro_ly_owner, điền 2 file .env, nhắn một tin vào phòng You, `room --set` nếu không tự tìm, rồi `/assistant_on`. Đừng quét cả ổ đĩa bằng find (treo phiên, 2026-11-18). Liên quan [[reference-horuschat-mcp]], [[reference-paseo]].
