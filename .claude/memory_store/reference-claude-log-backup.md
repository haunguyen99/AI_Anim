---
name: reference-claude-log-backup
description: "Log phiên Claude + agent Paseo được sao lưu mỗi giờ sang DataHDD/claude_log_backup (systemd user timer, từ 2026-11-18)"
metadata:
  node_type: memory
  type: reference
  originSessionId: dfd45043-2e91-4f7e-b458-00791fb23654
  modified: 2026-11-18T01:44:54.776Z
---

Máy Linux sao lưu log phiên Claude mỗi giờ sang `/home/ngocvb/Desktop/DataHDD/claude_log_backup/`:
- `projects/`: bản sao `~/.claude/projects`
- `paseo_agents/`: bản sao `~/.paseo/agents`
- `lan_sao_luu_cuoi.txt`: giờ sao lưu gần nhất

Script là `~/.local/bin/claude_log_backup.sh`, chạy bằng systemd user timer `claude-log-backup.timer` (hourly, Persistent). Bản sao chỉ thêm và cập nhật, không xoá, nên phiên đã xoá trong app vẫn còn ở đây.

**Why:** log Pet 11–23 (11–14/11) mất hẳn khi máy Windows không còn, nên /skillreport không đo được AI gen và người làm cho các pet đó.

**How to apply:** khi làm /skillreport mà không thấy log trong `~/.claude/projects`, tìm trong thư mục sao lưu này trước. Xem thêm [[project-ai-employee]].
