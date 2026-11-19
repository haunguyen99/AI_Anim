---
name: reference-phien-con-skills
description: "Hai skill gọi nhanh phiên con - /agent-free (Paseo, dài, gõ trực tiếp, không đánh thức phiên chính) và /agent-mini (công cụ Agent, ngắn, tự đánh thức); công cụ tools/paseo_cmd.py"
metadata:
  node_type: memory
  type: reference
  originSessionId: 43e932ab-0d11-495e-b842-e4919e67beda
  modified: 2026-11-13T04:36:03.385Z
---

User 2026-11-13: tạo skill gọi nhanh theo hai cách tạo subagent.
- `/agent-free <việc>`: việc dài, user muốn gõ trực tiếp trong app Paseo; không tự đánh thức phiên chính. Công cụ `tools/paseo_cmd.py run <tên> @brief | ls | logs <id> | send <id> | stop <id>` (brief ghi ở work/_subsessions/paseo/, prompt chỉ trỏ file để tránh lỗi dấu nháy kép).
- `/agent-mini <việc>`: việc ngắn cần kết quả ngay; Agent tool `run_in_background`, chip "subagents", tự đánh thức, user không gõ trực tiếp được (nút "Open parent"); chết khi phiên chính đóng.
- Cách thứ ba `tools/subsession/subsession.py` (`claude --bg`) chỉ khi cần tự đánh thức mà không dùng app desktop.
Hướng dẫn gốc docs/paseo_phien_con.md. Liên quan [[project-ai-employee]], [[reference-subsession]], [[reference-paseo]].
