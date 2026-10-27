# Quy tắc chung cho mọi phiên Claude trong dự án AI Animation

Đọc `MAP.md` trước khi tạo file mới. Luật làm anim nằm ở `.claude/skills/animation/knowledge/CORE.md`.

## Trình duyệt (Studio, Home, các Lab, trang review)
- **Chỉ chụp màn hình khi người dùng yêu cầu** (người dùng, 2026-10-27). Người dùng xem trực tiếp trên trang nên thấy ngay mọi thay đổi.
- Kiểm tra kết quả bằng `javascript_tool`, `read_page` hoặc `find` (tên object, ẩn/hiện, đang chọn gì, lỗi console), rồi báo ngắn bằng chữ.
- Bấm theo `ref` (từ `find` / `read_page`) hoặc gọi lệnh trên trang bằng JS, không đọc tọa độ từ ảnh chụp.
- Việc nhỏ (xóa, ẩn, đổi tên): đọc đủ tên object trước, làm trong một lượt, không chờ từng bước.
- Không thuộc quy tắc này: các bản render / playblast trong quy trình anim (quick render, so REF|ANIM, kiểm giải phẫu). Đó là bước tự kiểm tra pose, không phải chụp màn hình để báo cáo.

## Trả lời
- Mọi câu trả lời bằng tiếng Việt.
