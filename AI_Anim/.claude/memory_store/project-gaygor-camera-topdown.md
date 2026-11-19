---
name: project-gaygor-camera-topdown
description: "Gaygor's game camera is TOP-DOWN (user 2026-10-25), not the right-side view the Hit/Die designs assumed"
metadata:
  node_type: memory
  type: project
  originSessionId: 20043592-be79-4e6b-b2ba-600a995b91bb
  modified: 2026-10-25T12:34:25.088Z
---

User 2026-10-25 (reviewing Gaygor Die F72): "Game nay góc camera in game là topdown".

**Why:** Hit and Die designs (work/boss_gaygor/gaygor_hit/analysis.md, work/boss_gaygor/gaygor_die/analysis.md) said the game camera is the
character's right side ("Right (ingame)" on Pose Lab) — that was an assumption, never confirmed. Readability decisions
(head turned to the camera, silhouettes, which side props fall) must be judged from above.

**How to apply:** check every Gaygor pose/still from the top (Pose Lab "Top", stills view 1) first; ask whether the
top-down camera is straight down or tilted when a decision depends on it. Related: [[project-workflow-c-text-brief]].
