---
name: reference-spine-live
description: Spine Live page (Home /spine) shows Spine 2D skeleton JSON live; tools/spine_live_cmd.py pushes each work step so the user watches Claude work
metadata:
  node_type: memory
  type: reference
  originSessionId: 1ddcc19b-ae7c-4ab6-995f-358713a15247
  modified: 2026-10-28T09:31:02.880Z
---

Spine Live = `http://127.0.0.1:8780/spine?json=work/<game>/spine/<anim>/<x>.json` (tools/spine_live + tools/home/spine_live.py), added 2026-10-28 because the Spine editor has no remote API. Auto-reloads on file change, keeps anim + time; rig overlay (bones, mesh, weight heatmap, red + at origin).

User 2026-10-28: "tôi không thấy được quá trình bạn làm việc trên Spine Live" → during Spine work push every meaningful step with `tools/spine_live_cmd.py show <json> --anim --frame --bones --weight --say "..."` / `say "..."`; the page's "Theo Claude" mode follows. Put temp test skeletons in `<anim>/_live/`, not the scratchpad. Related: [[reference-spine-mcp]].
