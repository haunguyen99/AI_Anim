---
name: reference-subsession
description: Phiên con trong VS Code — tools/subsession/subsession.py + skill subsession (claude --bg), làm xong 2026-11-05
metadata:
  type: reference
---

Lớp 1 của docs/vscode_subsessions_design.md đã làm và thử thật (start/wait/send/stop). Tên skill và script đều là `subsession` (user 2026-11-05: tên skill tiếng Anh). Lớp 2 (extension, cần Node.js) chưa quyết.

**Why:** phiên điều phối (HorusChat, WorkAI) trước chỉ chạy được trong app desktop.
**How to apply:** giao việc dài/độc lập qua skill subsession, `wait` bằng run_in_background (đã xác nhận đánh thức phiên VS Code). Bẫy đã gặp (bgIsolation, MCP, allowedTools nuốt prompt, send tạo bản sao) ghi trong SKILL.md. Xem [[reference-vscode-pilot]].

**Xác nhận 2026-11-06:** phiên con nền hiện trong danh sách phiên của extension VS Code, nên lớp 2 (cây phiên) không cần; chỉ còn thông báo + tab Anim nếu team muốn.

**Giao diện (2026-11-06):** trang /sessions trong Home (tools/home/sessions.py) và extension VS Code horus-anim.horus-sessions (tools/vscode_ext, JS thuần, build_vsix.py đóng gói không cần Node). User muốn UI nằm trong VS Code; Claude không sửa được giao diện extension Claude chính thức nên làm thanh bên riêng.

**Đồng bộ (2026-11-06, ext 0.2.0):** danh sách phiên lấy từ Claude Code (agents + nhật ký projects + chỉ mục app); bấm phiên = claude-vscode.primaryEditor.open(session, prompt). Chỉ mục app ở %LOCALAPPDATA%/Claude-Data/*/claude-code-sessions là nội bộ, có thể đổi.
