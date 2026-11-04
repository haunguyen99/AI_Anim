---
name: feedback-report-slow-steps
description: "While working, tell the user which steps are time-consuming (user asked 2026-10-22)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: cecf265b-fb48-47d0-ac4a-9a158c1bbe6b
  modified: 2026-10-22T10:21:05.302Z
---

User (2026-10-22, Gaygor Attack v10): "Trong quá trình làm, nếu thấy bước nào tốn thời gian nhớ báo lại cho tôi biết".

**Why:** the user wants to see where time goes so the pipeline can be sped up.
**How to apply:** in progress updates and the final report, name the slow steps (with rough time, e.g. trial render rounds, state recovery, playblast/publish) and suggest how to cut them. Write trial parameters to a file (e.g. work/<dự án>/<job>/vNN/fixes.py) so the next session doesn't re-discover them.

2026-11-03 (Ropeway Crank, user: "Sao những vòng sửa sau này mất thời gian vậy"): a Frolvy full-clip rebuild with per-frame arm solving = ~5–6 min (3 chunks, 180 s MCP limit), dump+render ~1.5 min, director ~3 min. Say the minutes BEFORE starting; probe ALL affected frames (not 4–5 samples) before a full rebuild; rebuild only the changed range; for small layout tweaks send to the user while the director checks in parallel.
