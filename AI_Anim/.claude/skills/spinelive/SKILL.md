---
name: spinelive
description: Mở Spine Live (trang xem / sửa skeleton Spine 2D chạy trên máy, http://127.0.0.1:8781/spine) ngay trong khung trình duyệt của Claude, với file Spine sửa gần nhất (hoặc file khớp từ khoá). Dùng khi người dùng gõ /spinelive, nói "mở spine live", "mở spinelive trong claude", "mở file spine gần nhất", hoặc /spinelive <tên game / anim / file>.
---

# /spinelive: mở Spine Live trong Claude, file gần nhất

Trả lời bằng tiếng Việt, ngắn. Spine Live: `tools/spine_live/` (trang), `tools/home/spine_live.py` + `spine_edit.py` + `spine_bridge.py` (xử lý), server riêng `tools/spine_live/server.py` cổng 8781 (tách khỏi Home 2026-11-05; Home `/spine` chỉ chuyển sang). Luật làm Spine ở skill `spine2d`.

## Khi gõ /spinelive [từ khoá | list]

1. **Server Spine Live:** `curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:8781/api/spine/list`.
   - Ra `200`: dùng server đang chạy (có thể do người dùng bật bằng `tools/spine_live/start.bat, tools/home/start.bat` hoặc phiên khác). Không khởi động lại.
   - Không ra `200`: `.venv/Scripts/python.exe -I tools/spine_live/ensure_server.py` (Bash thường, không nền): bật server
     **chạy riêng** (tách hẳn khỏi app, không cửa sổ), đợi tới khi `/api/spine/ping` trả lời rồi thoát.
     2026-11-10: trước đây `preview_start {name: "spine-live"}` chạy server như tiến trình con của khung xem trước nên đóng
     khung là tắt server; giờ mục `spine-live` trong `.claude/launch.json` chỉ có `url` (gắn vào server đang chạy).
     Kiểm sống: `curl http://127.0.0.1:8781/api/spine/ping`; log: `work/store/_sys/spine_live/server.log` (+ `server_stdout.log`).
2. **Chọn file:** `.venv/Scripts/python.exe -I tools/spine_live_recent.py [từ khoá]`.
   - In một dòng JSON `{json, label, kind, sửa lúc, url}`: file skeleton có lần sửa gần nhất (Claude gen, người dùng Key / sửa lưới trên Spine Live đều tính), lọc theo từ khoá nếu có.
   - Người dùng gõ `list` / "chọn file": `... spine_live_recent.py --list 8`, đưa danh sách và hỏi file nào (AskUserQuestion, tối đa 4 lựa chọn gần nhất).
   - `{"error": ...}`: báo đúng câu đó; không khớp từ khoá thì chạy `--list 8` để gợi ý.
3. **Mở trong Claude:**
   - Đã có tab Spine Live trong khung trình duyệt (`tabs_context`, origin `http://127.0.0.1:8781`): `navigate` tab đó tới `url`.
   - Chưa có: `preview_start` với `{url: <url>}` (hoặc `{name: "spine-live"}` rồi `navigate`).
4. **Kiểm đã chạy** (không chụp màn hình, `CLAUDE.md`): `javascript_tool` đợi tối đa ~5 s tới khi `player?.skeleton` có, đọc tên anim `player.skeleton.data.animations.map(a => a.name)` và `document.getElementById("status").textContent`.
   `player` khai báo bằng `let` ở script trang: đọc thẳng `player`, **không** dùng `window.player` (luôn `undefined`).
   - `tabs_context` báo **pane hidden** (khung trình duyệt đang thu lại): player không chạy được (không có requestAnimationFrame, trang báo "player không khởi động sau 10 s"). Tự hiện khung bằng `mcp__ccd_view__show_pane {pane: "preview"}` rồi chạy lại bước 3–4.
   - **Chỉ mở trong Claude** (người dùng 2026-11-05: "mở spinelive ngay trong claude ... chỉ mở trong claude, không đẩy ra ngoài chrome"): không mở Spine Live ở Chrome / trình duyệt thường (`Start-Process`, Claude in Chrome), không đưa link để người dùng tự mở ngoài.
   - Lỗi nạp file: đọc `#msg` của trang + `read_console_messages`; thử đọc JSON / atlas bằng `spine.SkeletonJson` trong trang để biết lỗi do file hay do trang.
5. **Báo một dòng:** đã mở file nào (label + sửa lúc), các anim có trong file (không gửi link để mở ngoài Claude).

## Khi chạy trong VS Code (không có `preview_start`)

Extension Claude Code trong VS Code không có khung trình duyệt của app Claude (`ToolSearch` không ra `preview_start` / `mcp__ccd_view__show_pane`). Đừng dừng lại báo "không mở được" (lỗi 2026-11-06), làm thế này:
1. **Server chưa chạy** (bước 1 không ra `200`): tự bật, cửa sổ thu nhỏ, chạy tiếp sau khi lệnh xong:
   `Start-Process -WindowStyle Minimized -WorkingDirectory "G:\Claude2Danim\AI_Anim" -FilePath ".venv\Scripts\python.exe" -ArgumentList "-I","tools\spine_live\server.py"` (PowerShell), rồi đợi `curl` ra `200`.
   **Không** dùng `tools/spine_live/start.bat` / `tools/home/start.bat`: hai file đó tự mở Chrome.
2. **Mở trang:** chọn file như bước 2, rồi đưa link `http://127.0.0.1:8781/spine?json=...` (đúng `url` của `spine_live_recent.py`) thành một dòng riêng trong câu trả lời và nói người dùng bấm vào. Dự án đặt `workbench.browser.openLocalhostLinks: true` (`.vscode/settings.json`) nên link `127.0.0.1` bấm trong chat mở ngay trong trình duyệt tích hợp của VS Code, không ra Chrome. Đây là ngoại lệ của "không đưa link" ở bước 4: trong VS Code, đó là cách mở trong cửa sổ đang làm.
3. **Kiểm đã mở:** không có `javascript_tool`; đợi người dùng bấm rồi `tools/spine_live_cmd.py status` (thấy trang đang mở + file) thay cho bước 4.

## Sau khi mở
- Đẩy bước đang làm lên trang: `tools/spine_live_cmd.py show <json> --anim <a> [--frame N] [--say "..."]` (trang ở chế độ Theo Claude tự nhảy theo); `status` để xem trang nào đang mở.
- Ghi chú / pose người dùng gửi từ trang: `tools/spine_live_cmd.py notes --bones`.

## Sau khi dựng / sửa rig (2026-11-19)
- Trang đang mở thì **tự cập nhật**: ghi file xong chạy `spine_live_cmd.py show <json> --anim <a> --bones --say "..."`, người dùng không phải tải lại (họ đã hỏi "không cập nhật live à?" khi mình chỉ ghi file). Kiểm bằng `status` (có dòng "đã thấy bước N").
- Mỗi lần xong một lệnh rig: dựng lại anim `rig_demo` (`tools/spine/rig_demo.py` hoặc demo riêng) rồi `show --anim rig_demo`.
- Máy Linux không có `.venv/Scripts/python.exe` thật: `bash tools/setup.sh` (cần `sudo apt install python3-venv python3-pip` trước) tạo `.venv` + lối tắt. Server Spine Live: `.venv/Scripts/python.exe -I tools/spine_live/ensure_server.py`. Đừng `pkill -f server.py` trong cùng lệnh Bash (giết luôn shell, mã 144).
- **Giao diện ban đêm (người dùng 2026-11-19)**: Spine Live mặc định tối (nếu trình duyệt chưa lưu lựa chọn); đổi tức thì trên trang đang mở: `spine_live_cmd.py theme dark|light` (trang hỏi focus.json mỗi 0,5 s, lưu `spinelive:theme`). Sửa `index.html` thì trang đang mở phải tải lại một lần (trang chỉ tự nạp lại khi JSON / atlas / ảnh đổi).

## Playblast (2026-11-27)
- Menu **Công cụ ▾ > Playblast (🎬)**: quay anim đang xem thành mp4 (`preview/<anim>_playblast.mp4`), chọn Từ / Đến F, Lặp ×, Rộng, FPS, Nền, Số frame. Vẽ bằng runtime Spine thật qua cầu nối `snap`, khung cố định, không ghi file skeleton. Mã: `tools/spine_live/playblast.js` (trang), `tools/home/spine_playblast.py` (server: cắt ô, đánh số, ffmpeg; `POST /api/spine/playblast {op: start|frames|finish|cancel}`). Sửa Python phải khởi động lại server. Gọi từ script / Chrome ẩn: `window.spinePlayblast.record()` sau khi đặt ô `#pbFrom #pbTo #pbW`.
