---
name: doi_danh_tinh
description: Đổi danh tính đăng nhập WorkAI / HorusChat giữa "AI Animation" (tài khoản animationa@horusvn.com, id 534, mặc định) và "haunv" (tài khoản của người dùng). Dùng khi người dùng gõ /doi_danh_tinh, hoặc nói "đổi danh tính", "chuyển sang tài khoản AI", "dùng tài khoản của tôi", "đang đăng nhập là ai", "đổi sang haunv".
---

# /doi_danh_tinh: đổi danh tính WorkAI / HorusChat

Hai danh tính (`tools/identity.py`): **ai** = AI Animation (mặc định), **haunv** = tài khoản của người dùng. Khoá ở `tools/workai/.env.<tên>` và `tools/horuschat_mcp/.env.<tên>` (git-ignored, không in ra chat). Trả lời tiếng Việt, ngắn.

## Khi gõ /doi_danh_tinh [ai|haunv]

1. **Không có tham số hoặc "đang là ai":** chạy `.venv/Scripts/python.exe -I tools/identity.py`, báo danh tính mặc định + tên tài khoản thấy trên WorkAI và HorusChat.
2. **Có tham số (ai hoặc haunv):** chạy `.venv/Scripts/python.exe -I tools/identity.py <tên> --daemons` (ghi danh tính mặc định + chạy lại 2 bộ canh nền WorkAI / HorusChat theo danh tính mới). Đọc kết quả, báo tên tài khoản hiện thấy trên cả hai nơi.
3. **Báo lỗi bằng lời:**
   - "Chưa có danh tính": thiếu file `.env.<tên>`.
   - WorkAI trả 401 hoặc HorusChat báo thiếu key: file `.env.<tên>` còn trống. Nhắc người dùng điền token WorkAI và key HorusChat (Settings → API Keys) vào đó, không dán vào chat.
4. **Cuối câu trả lời nhắc một dòng:** công cụ HorusChat (MCP) trong phiên Claude chỉ đọc lại danh tính khi khởi động lại phiên. Các lệnh Python (workai.py, bộ canh) đổi ngay.

## Luật
- Đổi sang `haunv` hay `ai` đều là việc người dùng đã ra lệnh: làm luôn, không hỏi lại.
- Không bao giờ in nội dung `.env.*`, token, key hay mật khẩu.
- Sau khi đổi danh tính, mọi tin gửi lên HorusChat và thao tác WorkAI sẽ mang tên tài khoản đó: nhắc người dùng một dòng khi chuyển sang `haunv` (tin gửi dưới tên người dùng).
- Chạy một lệnh riêng bằng danh tính khác mà không đổi mặc định: thêm `--profile <tên>` vào lệnh đó.
