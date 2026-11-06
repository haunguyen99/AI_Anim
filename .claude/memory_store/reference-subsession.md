---
name: reference-subsession
description: Phiên con trong VS Code — tools/subsession/subsession.py + skill subsession (claude --bg), làm xong 2026-11-05
metadata:
  type: reference
---

Lớp 1 của docs/vscode_subsessions_design.md đã làm và thử thật (start/wait/send/stop). Tên skill và script đều là `subsession` (user 2026-11-05: tên skill tiếng Anh). Lớp 2 (extension, cần Node.js) chưa quyết.

**Why:** phiên điều phối (HorusChat, WorkAI) trước chỉ chạy được trong app desktop.
**How to apply:** giao việc dài/độc lập qua skill subsession, `wait` bằng run_in_background (đã xác nhận đánh thức phiên VS Code). Bẫy đã gặp (bgIsolation, MCP, allowedTools nuốt prompt, send tạo bản sao) ghi trong SKILL.md. Xem [[reference-vscode-pilot]].
