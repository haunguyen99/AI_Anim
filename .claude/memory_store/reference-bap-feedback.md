---
name: reference-bap-feedback
description: "BAP (bap.horusjsc.com) feedback API client tools/bap/bap.py; key wap_… in tools/bap/.env (gitignored), Bearer auth"
metadata:
  node_type: memory
  type: reference
  originSessionId: a855520e-8795-414b-8992-79aec5f3e713
  modified: 2026-11-06T02:55:31.135Z
---

BAP = Bug And Plan, https://bap.horusjsc.com (feedback page /feedback). API base /api/v1, `Authorization: Bearer wap_…` (key made in BAP → API tokens).
Client: `tools/bap/bap.py` — `me`, `projects`, `list`, `show <id>`, `send --project ID --title … --content/--content-file --place … --file …`; `send_feedback()` importable.
Feedback body = project_id, title, content, place; files go multipart field `files` to /feedback/{id}/attachments.
2026-11-06: the key in tools/bap/.env got 401 — user must make a new key before first send. Ask before sending (it posts to the team).
