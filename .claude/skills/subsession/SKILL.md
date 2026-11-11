---
name: subsession
description: Giao việc cho phiên con (phiên Claude nền) trong VS Code / terminal, theo dõi, nhắn thêm, nhận báo cáo. Dùng khi người dùng nói "giao việc cho phiên con", "chạy song song", "phiên con đang làm gì", "bảo phiên X làm thêm", "dừng phiên X", hoặc khi một việc dài, độc lập nên tách khỏi phiên chính. Công cụ tools/subsession/subsession.py (thiết kế: docs/vscode_subsessions_design.md).
---

# subsession: phiên con trong VS Code

Chạy mọi lệnh: `.venv/Scripts/python.exe -I tools/subsession/subsession.py <lệnh>`. Trả lời tiếng Việt.

## Khi nào giao
Việc dài, độc lập, có phạm vi file rõ (rig lại một con, dựng báo cáo, đọc và tóm tắt tài liệu). Không giao việc cần hỏi người dùng giữa chừng liên tục, hay việc đụng cùng file với phiên đang chạy.

## Luồng
1. Viết brief: việc gì, file nào được sửa, "xong" là gì, cách kiểm. Không ghi key/token.
   `start --name <tên-ngắn> --brief "<text>"` (hoặc `--brief @file`), kèm `--files a,b` (để cảnh báo trùng file), `--parent <id>` nếu phiên con giao tiếp, `--allow "Bash(git status*);..."` nếu việc cần thêm lệnh (mặc định chỉ Read/Glob/Grep/Edit/Write + lệnh `done`).
2. Chạy `wait <tên>` bằng `run_in_background`: khi phiên con báo cáo / kẹt / thoát / hết giờ, phiên chính được đánh thức, đọc báo cáo, **kiểm kết quả thật** rồi báo người dùng.
3. Việc thêm: `send <tên> "<tin>"` rồi `wait` lại. Phiên con đang chạy dở thì tin được xếp hàng.
4. `list`, `tree`, `log <tên>`, `stop <tên>`; người dùng muốn nói trực tiếp: `claude attach <id claude 8 ký tự>` trong terminal VS Code.

## Trạng thái
chạy · chờ (xong lượt) · **kẹt** (đang chờ duyệt quyền, xem `log`, cho thêm `--allow` hoặc `attach`) · xong · chặn (phiên con ghi `CHẶN: <câu hỏi>`: hỏi người dùng rồi `send`) · dừng · thoát (không có báo cáo: xem `log`).

## Điều đã thử (2026-11-05, claude 2.1.302)
- `--bg` tự cấp id (bỏ `--session-id`); script lưu id claude 8 ký tự trong registry.
- Phiên nền mặc định cách ly trong worktree và không ghi được report: script truyền `--settings {"worktree":{"bgIsolation":"none"}}` cho từng phiên (không sửa settings dự án).
- Không nạp MCP (`--strict-mcp-config`): tránh hộp thoại duyệt MCP làm kẹt phiên. Việc cần MCP (Frolvy, Maya...) làm ở phiên chính.
- `--allowedTools` là tham số nhiều giá trị: prompt phải đứng TRƯỚC cờ (script đã lo).
- `send` vào phiên còn mở: claude tạo bản sao id mới; script theo bản sao và dừng bản cũ.
- `claude --bg ... --help` tạo phiên rỗng: đừng chạy thử kiểu đó.

## Luật an toàn
Phiên con không commit, không đổi nhánh, không đẩy GitHub (luật gắn sẵn cuối brief). Tối đa 4 phiên cùng lúc. Không dùng `--dangerously-skip-permissions`.
- Phiên con nền (`claude --bg`) HIỆN trong danh sách phiên của extension VS Code (user xác nhận 2026-11-06): không cần làm cây phiên riêng, lớp 2 chỉ còn thông báo + tab Anim nếu muốn.
- Giao diện quản lý: trang /sessions của Home (tools/home/sessions.py + sessions.html, nút trên thanh Home). Khởi động lại Home để dùng.
- Trong VS Code: extension "Horus: Phiên Claude" (tools/vscode_ext, cài bằng `.venv/Scripts/python.exe -I tools/vscode_ext/build_vsix.py --install`, rồi Reload Window): biểu tượng ở thanh bên, cây phiên, nút giao việc / nhắn thêm / dừng / xoá, thông báo khi phiên con xong. Dữ liệu từ `subsession.py json` / `detail`.
- Danh sách phiên lấy từ chính Claude Code (subsession.py `rows()`): claude agents + nhật ký ~/.claude/projects (tên, phiên đã đóng, cache titles_cache.json) + chỉ mục app desktop (phiên cha spawnedFrom, đã lưu trữ; đọc-chỉ, best-effort, có thể đổi khi app cập nhật). Extension mở phiên bằng lệnh claude-vscode.primaryEditor.open(sessionId, prompt) của extension Claude Code.
