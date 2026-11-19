---
name: feedback-ai-does-user-approves
description: "Studio rig (and similar step gates): AI does every step, user only approves / gives FB; Duyệt → AI does next step, Cần sửa → AI fixes"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9e5958ee-2e98-46b1-a039-a2010ed17cb1
  modified: 2026-10-28T09:11:00.732Z
---

User 2026-10-28: "AI sẽ làm mọi việc người dùng chỉ duyệt và fb thôi" — on Studio Rig step gates, pressing Duyệt or Cần sửa must wake Claude to continue.

**Why:** the user wants to be reviewer only, not operator; waiting for them to type in chat breaks the flow.

**How to apply:** keep `tools/notes_watch.py` running in background (it now also picks `kind: rig_gate`). On ok → do the next Rig step yourself, `rig step <n>`, self-check, stop for approval (one step at a time). On fix → fix that step per note. Then `studio_cmd.py gate-done <id> <step> "msg"` and restart the watcher. See [[reference-studio-bridge]], [[feedback-review-listening]].
