---
name: feedback-chat-dispatcher
description: "The HorusChat-watcher session also receives and dispatches work (user 2026-11-03): triage each order, propose owner/session, open one session per job"
metadata:
  node_type: memory
  type: feedback
  originSessionId: c9131ccf-2a0c-4863-8817-37fd7cfc823b
  modified: 2026-11-03T09:20:57.368Z
---

User 2026-11-03: "section này có thêm nhiệm vụ nhận và điều phối công việc" — the session that runs the HorusChat watcher ([[reference-horuschat-mcp]]) is also the job intake + dispatcher.

For each job that arrives (order, feedback, bug, request in DM/tag):
1. Read it fully: open the GDD/sheet row, download images, read thread root; summarize what/who/deadline/missing info.
2. Propose: do it ourselves (one separate Claude session per job, brief with files + done criteria) or forward to a teammate (e.g. Trần Quang Tùng took Harvest Ring Investor).
3. On the user's yes: start the session / forward / reply. Track each job's session; when a session reports, relay outcome in 1–2 lines.
4. Sessions never post to HorusChat themselves without the user's OK; replies to requesters go through the user's approval.

**Why:** user handles many requesters (Khải, Anh, Thịnh, Tùng…) at once; one hub keeps intake and status in one place.
**How to apply:** keep watcher running; announce each new job with a proposal (do / forward / ask for info) instead of only relaying the message.
