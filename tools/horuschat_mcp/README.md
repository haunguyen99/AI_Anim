# horuschat_mcp

Cầu nối MCP `horuschat` tới HorusChat (https://chat.horusjsc.com). HorusChat là Matrix chạy sau một Gateway
có Developer API; tài liệu nằm ngay trong app (Settings → API Keys / tài liệu Developer).

## Cài
1. HorusChat → **Settings → API Keys** → tạo key, chọn scope `messages:read`, `messages:send`,
   `rooms:read`, `users:read` (thêm `rooms:write` nếu muốn join/rời phòng). Token chỉ hiện một lần.
2. Chép `.env.example` thành `.env` trong thư mục này rồi dán key vào `HORUSCHAT_API_KEY=`.
   `.env` đã nằm trong `.gitignore`, không lên git.
3. Khởi động lại phiên Claude Code để nạp server (khai báo trong `.mcp.json` gốc), gọi `hc_me` để kiểm.

## Lệnh
| Lệnh | Việc |
|---|---|
| `hc_me` | key đang đóng vai ai, scope |
| `hc_rooms`, `hc_room` | danh sách phòng đã tham gia, thông tin + thành viên |
| `hc_history` | tin gần nhất của phòng hoặc một thread |
| `hc_events` | sự kiện mới theo cursor (`after=now`, long-poll `wait` ≤ 30 s) |
| `hc_users` | tìm user → Matrix id `@ten:host` |
| `hc_send` | gửi tin vào phòng, trả lời trong thread (`thread_root_event_id`), mention, markdown |
| `hc_dm` | nhắn riêng một người |
| `hc_edit`, `hc_react`, `hc_delete` | sửa / thả reaction / thu hồi tin của chính mình |
| `hc_download` | tải file đính kèm (`mxc://…`) |

Phòng ghi bằng room id `!…`, alias `#…:host` hoặc một phần tên phòng.

## Lưu ý
- Tin gửi đi mang tên chủ key. Claude hỏi người dùng trong chat trước mỗi lần gửi / nhắn riêng / sửa / thu hồi.
- Phòng mã hoá E2EE không đọc/gửi được qua API (`409 room_encrypted`).
- `m.notice` không tạo thông báo; mặc định dùng `m.text`.
- Giới hạn tốc độ: `429 rate_limited` + `Retry-After`.

## Bộ canh (tools/horuschat_watch.py)
Claude chạy nền `tools/horuschat_mcp/.venv/Scripts/python.exe -I tools/horuschat_watch.py`: ai **tag**, **nhắn riêng**,
**trả lời tin** hoặc **mời phòng** chủ key thì in ra rồi thoát → Claude báo người dùng trong chat, rồi chạy lại để canh tiếp.
Long-poll `/v1/developer/events?addressed_only=true` (30 s/lần, không tốn lượt AI), tối đa 8 giờ mỗi lần chạy.
Mốc ở `work/store/_sys/watch/horuschat.json`; `--once` kiểm một lần, `--reset` bỏ tin cũ.
