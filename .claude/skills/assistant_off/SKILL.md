---
name: assistant_off
description: Tắt Agent trợ lý cá nhân của Hậu (dừng phiên Paseo "tro-ly", đặt cờ tắt để không tự bật lại). Dùng khi người dùng gõ /assistant_off, hoặc nói "tắt trợ lý", "dừng trợ lý", "cho trợ lý nghỉ", "tắt agent cá nhân".
---

# /assistant_off: tắt trợ lý cá nhân

Công cụ: `.venv/Scripts/python.exe -I tools/assistant.py` (Linux: `python3 -I`). Trả lời tiếng Việt, ngắn. Người dùng đã ra lệnh thì làm luôn, không hỏi lại.

## Làm
1. `tro_ly.py off` (nhắn "Trợ lý sắp tắt" vào You, đặt cờ `work/store/_sys/watch/tro_ly_off`, dừng phiên Paseo `tro-ly`). Cờ tắt giữ nguyên qua khởi động lại máy: trợ lý chỉ bật lại khi `/assistant_on`.
2. Người dùng nói **tắt hẳn** / "tắt cả bộ canh" / "đỡ tốn tài nguyên": thêm `--daemons` (dừng luôn 2 bộ canh nền HorusChat / WorkAI của haunv; bộ canh chỉ đọc và hiện thông báo trên máy, nên mặc định giữ chạy để người dùng vẫn nhận thông báo).
3. `tro_ly.py status` để kiểm; báo: đã tắt chưa, phiên còn không, bộ canh còn chạy không.
4. Nhắc một dòng: sổ việc (`work/assistant/todo.json`) và nhật ký trợ lý vẫn giữ nguyên; bật lại bằng `/assistant_on` thì trợ lý đọc sổ và tiếp tục.

## Lưu ý
- Tin chủ nhắn vào You lúc trợ lý tắt vẫn được giữ: bật lại thì trợ lý đọc và xử lý chúng (trừ lần chạy đầu tiên trên máy, khi mọi tin có sẵn coi là đã đọc).
- Phiên Paseo bị đóng thì `/assistant_on` tạo phiên mới (mất ngữ cảnh hội thoại cũ, không mất sổ việc).
