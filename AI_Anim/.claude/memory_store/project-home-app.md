---
name: project-home-app
description: "Home = local project manager app (tools/home, port 8780) — the user's entry point; projects by game; data per machine"
metadata:
  node_type: memory
  type: project
  originSessionId: c990f45c-fe77-4202-bb0e-b693e293125c
  modified: 2026-10-23T09:49:21.792Z
---

Since 2026-10-23 the user starts work from **Home** (`tools/home/start.bat` or preview `home`, http://127.0.0.1:8780): Home → project (by game; SDR = map2 + map06) → anim → Continue opens Rig/Pose/Review Lab. Single user, data stays on the machine (not an artifact). Stores projects in `work/clips.json` key `projects`; "+ Animation mới" registers the clip + writes `work/<dự án>/<id>/brief.md`, then user types `/new_clip <id>`.

**Why:** user wants one app-like place to manage work per project and check status.
**How to apply:** keep clips.json stage/note accurate (note with "chờ" when waiting for review) so Home shows the right status; new characters go into the right project. Details: knowledge `review_process.md#home-app`. Related: [[reference-review-page]], [[project-map]].


2026-10-27: root http://127.0.0.1:8780 now opens Studio straight into the viewport with an empty scene (user: "sao không mở một file trống"; start card: Nhập FBX / Mở nhân vật / quick list); Home moved to /home (user: "bây giờ là tool tổng hợp… mở phát ra viewport luôn"). See [[project-studio]].
