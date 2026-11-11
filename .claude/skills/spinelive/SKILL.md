---
name: spinelive
description: Mở Spine Live (trang xem / sửa skeleton Spine 2D chạy trên máy, http://127.0.0.1:8781/spine) ngay trong khung trình duyệt của Claude, với file Spine sửa gần nhất (hoặc file khớp từ khoá). Dùng khi người dùng gõ /spinelive, nói "mở spine live", "mở spinelive trong claude", "mở file spine gần nhất", hoặc /spinelive <tên game / anim / file>.
---

# /spinelive: mở Spine Live trong Claude, file gần nhất

Trả lời bằng tiếng Việt, ngắn. Spine Live: `tools/spine_live/` (trang), `tools/home/spine_live.py` + `spine_edit.py` + `spine_bridge.py` (xử lý), server riêng `tools/spine_live/server.py` cổng 8781 (tách khỏi Home 2026-11-05; Home `/spine` chỉ chuyển sang). Luật làm Spine ở skill `spine2d`.

## Khi gõ /spinelive [từ khoá | list]

1. **Server Spine Live:** `curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:8781/api/spine/list`.
   - Ra `200`: dùng server đang chạy (có thể do người dùng bật bằng `tools/spine_live/start.bat, tools/home/start.bat` hoặc phiên khác). Không khởi động lại.
   - Không ra `200`: `preview_start` với `{name: "spine-live"}` (`.claude/launch.json`), đợi tới khi `curl` ra `200`.
     Không dùng `run_in_background` của Bash để chạy server (bị dừng khi lệnh nền kết thúc, lỗi 2026-11-03).
2. **Chọn file:** `.venv/Scripts/python.exe -I tools/spine_live_recent.py [từ khoá]`.
   - In một dòng JSON `{json, label, kind, sửa lúc, url}`: file skeleton có lần sửa gần nhất (Claude gen, người dùng Key / sửa lưới trên Spine Live đều tính), lọc theo từ khoá nếu có.
   - Người dùng gõ `list` / "chọn file": `... spine_live_recent.py --list 8`, đưa danh sách và hỏi file nào (AskUserQuestion, tối đa 4 lựa chọn gần nhất).
   - `{"error": ...}`: báo đúng câu đó; không khớp từ khoá thì chạy `--list 8` để gợi ý.
3. **Mở trong Claude:**
   - Đã có tab Spine Live trong khung trình duyệt (`tabs_context`, origin `http://127.0.0.1:8781`): `navigate` tab đó tới `url`.
   - Chưa có: `preview_start` với `{url: <url>}`.
4. **Kiểm đã chạy** (không chụp màn hình, `CLAUDE.md`): `javascript_tool` đợi tối đa ~5 s tới khi `player?.skeleton` có, đọc tên anim `player.skeleton.data.animations.map(a => a.name)` và `document.getElementById("status").textContent`.
   `player` khai báo bằng `let` ở script trang: đọc thẳng `player`, **không** dùng `window.player` (luôn `undefined`).
   - `tabs_context` báo **pane hidden** (khung trình duyệt đang thu lại): player không chạy được (không có requestAnimationFrame, trang báo "player không khởi động sau 10 s"). Nhờ người dùng mở khung trình duyệt của Claude rồi chạy lại bước 3–4; hoặc mở ở trình duyệt thường bằng `Start-Process "<url>"` (PowerShell) nếu họ muốn.
   - Lỗi nạp file: đọc `#msg` của trang + `read_console_messages`; thử đọc JSON / atlas bằng `spine.SkeletonJson` trong trang để biết lỗi do file hay do trang.
5. **Báo một dòng:** đã mở file nào (label + sửa lúc), các anim có trong file, link `url` (mở được ở trình duyệt thường khi server còn chạy).

## Sau khi mở
- Đẩy bước đang làm lên trang: `tools/spine_live_cmd.py show <json> --anim <a> [--frame N] [--say "..."]` (trang ở chế độ Theo Claude tự nhảy theo); `status` để xem trang nào đang mở.
- Ghi chú / pose người dùng gửi từ trang: `tools/spine_live_cmd.py notes --bones`.
