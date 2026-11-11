---
name: feedback-work-fast
description: "User 2026-11-11 'tối ưu cách làm việc để đạt tốc độ nhanh nhất': ít lượt hơn — việc đã giao thì 1 lượt xem + 1 lượt làm/kiểm, gom lệnh, dùng lệnh một bước frolvy_port.py scene|keys|clear|reset, mở đầu việc Frolvy bằng scene"
metadata:
  node_type: memory
  type: feedback
  originSessionId: a8cbd450-9037-4cef-96fb-75d211bcc8b8
  modified: 2026-11-11T04:10:10.683Z
---

User 2026-11-11, after "xóa key của khăn và đưa về pose mặc định" (Ninja) took ~12 tool calls: "sao lâu thế", then "tôi cần bạn tối ưu cách làm việc để đạt tốc độ nhanh nhất".

**Why:** the Frolvy work itself is quick; the time went into many small sequential probe calls (API docs, node lists, key counts, "other nodes", memory re-reads, knowledge edits) and long deliberation.

**How to apply:**
- Explicit order = do it. One look call (what will be touched, counts), then ONE call that does + verifies (the tool's summary line is the check). Skip probes the task does not need; do not re-read memory/docs/skills already read in the session.
- Batch: independent calls in the same message; dependent shell steps joined with `;` in one Bash call; read-only checks in one script.
- Frolvy: start with `tools/frolvy_port.py scene` (open file, `*` unsaved, layers, keys). The user restarts / switches Frolvy between turns: 2026-11-11 11:03 the Ninja scene vanished, port 9877 became an empty scene, 9878 belongs to another session (my earlier "xong" no longer held, the file on disk was still the 10:40 version). Then `keys|clear|reset <name>` ([[reference-frolvy-mcp]]). Use the direct `frolvy` MCP tools when connected, else the CLI.
- Anything done twice becomes a one-step command ([[feedback-propose-tools]]).
- Write knowledge once, at the end of the task, in one batch ([[feedback-update-knowledge]] still applies).
- Say up front what takes long ([[feedback-report-slow-steps]]). `/fast` (faster output, same model) is the user's own lever.
