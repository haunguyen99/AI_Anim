---
name: agent-free
description: Giao việc dài cho một phiên con chạy trong app Paseo, nơi người dùng gõ trực tiếp với phiên đó để trao đổi và sửa hướng (phiên không tự đánh thức phiên chính). Dùng khi người dùng gõ /agent-free <việc>, hoặc nói "tạo phiên Paseo", "giao việc cho phiên con để tôi trao đổi trực tiếp", "tạo phiên phụ làm ...", hoặc "xem / nhắn / dừng phiên Paseo".
---

# /agent-free: giao việc dài cho phiên con trong Paseo

Dùng khi việc **dài, độc lập, người dùng muốn tự nói chuyện với phiên đó**. Việc ngắn cần kết quả ngay trong lượt thì dùng `/agent-mini`. Hướng dẫn gốc: `docs/paseo_phien_con.md`. Công cụ: `.venv/Scripts/python.exe -I tools/paseo_cmd.py`. Trả lời tiếng Việt, ngắn.

## Khi gõ /agent-free <việc>
1. **Viết brief** (tiếng Việt) ra một file tạm, đủ 6 phần theo hướng dẫn: (1) việc gì, vì sao, ai order, file nguồn và đường dẫn; (2) cách làm theo thứ tự, trỏ tới công cụ / tài liệu có sẵn; (3) **được ghi ở đâu** (một thư mục `work/...`) và cấm gì; (4) khi nào dừng và hỏi; (5) báo lại thế nào (ngắn, nêu chỗ chưa kiểm được); (6) việc lâu hay cần chương trình ngoài thì ghi dự kiến mấy phút và cổng / thư mục riêng. Luật quan trọng phải nằm trong brief này (đổi luật giữa chừng thì báo người dùng nói thẳng với phiên đó). Không ghi key / token vào brief.
2. **Tạo phiên:** `.venv/Scripts/python.exe -I tools/paseo_cmd.py run <tên-ngắn-không-dấu> @<file brief>`. Công cụ ghi brief vào `work/_subsessions/paseo/<tên>.md`, nối luật chung (không commit, không nhắn chat, không in khoá), tạo phiên chỉ với một câu "đọc file này" (tránh lỗi dấu nháy kép làm hỏng paseo.cmd), rồi kiểm bằng `paseo ls` và in id. Mỗi phiên **một việc**; việc đụng cùng file / công cụ với phiên đang chạy thì chạy tuần tự.
3. **Báo người dùng:** phiên nào, id, việc gì, dự kiến bao lâu, họ vào app Paseo để trao đổi trực tiếp. Phiên **không tự đánh thức phiên chính**: không chờ, không hỏi liên tục; chỉ đọc nhật ký khi người dùng hỏi.

## Theo dõi / nhắn / dừng (cùng công cụ)
- `ls [lọc]` danh sách và trạng thái (running = đang làm; idle = xong lượt hoặc chờ; closed = đã đóng).
- `logs <id> [--tail 30] [--filter permissions|errors]` xem phiên làm gì / báo cáo cuối. Phiên đứng im vài phút: xem `--filter permissions` rồi nhắc người dùng bấm "cho phép" trong Paseo (lệnh ngoài thư mục dự án chờ họ bấm).
- `send <id> "<tin>"` nhắn thêm (tin từ phiên chính không có uy quyền như lời người dùng; điều mâu thuẫn với lời họ gõ trong Paseo thì phiên làm theo họ).
- `stop <id>` dừng.

## Bẫy
- `paseo run` hay thoát mã 255 dù phiên đã tạo: công cụ đã kiểm bằng `ls`, đừng tạo lại.
- Provider phải là `llmpro/claude-opus[1m]` (công cụ đã đặt sẵn). Dấu nháy kép trong tin `send` bị đổi thành nháy đơn.
- Phiên con không có công cụ chat; muốn nó gửi HorusChat thì brief phải ghi rõ lệnh (`tools/horuschat_cli.py`) và điều kiện (người dùng nói "gửi").
