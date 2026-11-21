---
name: agent-dashboard
description: Mở Agent Dashboard của repo hiện tại, trang trực quan hoá agent, skill, hook, kiến thức và các luồng đang chạy trực tiếp. Dùng khi người dùng nói mở dashboard, xem hệ thống agent, xem sơ đồ agent, xem các luồng agent, kiểm tra liên kết agent hoặc skill.
---

# Mở Agent Dashboard

Dùng được ở mọi repo. `<thư-mục-skill>` là base directory của skill này. Các lệnh chạy từ thư mục đang làm việc, script tự tìm gốc repo git. Không phải repo git thì xem thư mục hiện tại. Không tạo file nào trong repo được xem.

1. Sinh lại trang:

   ```bash
   node "<thư-mục-skill>/scripts/agent-dashboard.mjs"
   ```

   Nếu lệnh lỗi, báo nguyên văn dòng lỗi và dừng. Không mở bản cũ như thể đó là bản mới.
2. Bật chế độ trực tiếp. Lệnh này dùng lại server của repo này nếu đang chạy, và in ra URL:

   ```bash
   node "<thư-mục-skill>/scripts/agent-dashboard-live.mjs" --detach
   ```

   Mỗi repo có server riêng, chỉ nghe trên 127.0.0.1 và tự tắt sau 30 phút không có trang nào mở.
3. Mở đúng URL vừa in:
   - Trong app Claude có Browser pane: gọi `preview_start` với URL đó.
   - Nếu không có Browser pane: chạy lại lệnh ở bước 2 và thêm `--open` để mở bằng trình duyệt mặc định.
   - Nếu server live lỗi: báo lỗi, rồi mở file HTML mà bước 1 đã in, và nói rõ đó là bản không trực tiếp.
4. Báo ngắn gọn tên repo và số agent, skill, liên kết, cảnh báo mà script in ra. Nếu có cảnh báo, liệt kê từng cảnh báo. Không tự sửa khi người dùng chưa yêu cầu.
