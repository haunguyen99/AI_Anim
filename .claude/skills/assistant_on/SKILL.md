---
name: assistant_on
description: Bật Agent trợ lý cá nhân của Hậu (phiên Paseo "tro-ly" + bộ canh HorusChat / WorkAI của haunv, nhắn chủ qua phòng You). Dùng khi người dùng gõ /assistant_on, hoặc nói "bật trợ lý", "chạy trợ lý", "mở trợ lý", "bật agent cá nhân", "trợ lý dậy đi".
---

# /assistant_on: bật trợ lý cá nhân

Công cụ: `.venv/Scripts/python.exe -I tools/assistant.py` (Linux: `python3 -I`). Giới thiệu và cách tạo lần đầu: skill `/assistant`. Trả lời tiếng Việt, ngắn. Người dùng đã ra lệnh thì làm luôn, không hỏi lại.

## Làm
1. `tro_ly.py on` (một lệnh làm đủ: kiểm khóa haunv, xóa cờ tắt, bật 2 bộ canh nền haunv nếu chưa chạy, tạo phiên Paseo `tro-ly` hoặc đánh thức phiên cũ, nhắn "Trợ lý đã bật" vào You).
2. `tro_ly.py status` để kiểm; báo một đoạn: phiên (id, trạng thái), bộ canh, phòng You, số việc mở.
3. Cuối câu: trợ lý nhắn qua phòng **You (yourself)** trên HorusChat; vào app Paseo (phiên `tro-ly`) nếu muốn gõ trực tiếp.

## Lỗi hay gặp (kể bằng lời, không dán log)
- "Thiếu khóa của haunv": chưa điền `tools/horuschat_mcp/.env.haunv` (HORUSCHAT_API_KEY) hoặc `tools/workai/.env.haunv` (WORKAI_TOKEN). Nhắc người dùng tự điền, không dán vào chat; xong chạy lại `/assistant_on`.
- "Chưa tìm thấy phòng You": nhờ người dùng nhắn một tin vào "You (yourself)" trên HorusChat, hoặc `tro_ly.py room --set <room_id>`. Chạy `on` lại. (Phòng có người khác hoặc mã hóa thì không dùng được.)
- "Paseo chưa chạy": mở app Paseo hoặc `paseo start`, rồi chạy lại.
- `on` chỉ nhắn vào You khi tìm được phòng; không thấy phòng thì trợ lý vẫn chạy nhưng chưa nhắn chủ được: nói rõ cho người dùng.
