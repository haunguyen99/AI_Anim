---
name: project-gaygor-idle-front
description: "Gaygor Idle_Front (60F, look forward, no glance) approved at v14 on 2026-10-20 after 9 team review rounds; exported FBX + baked blend"
metadata:
  node_type: memory
  type: project
  originSessionId: 7d2b80c9-f2b6-4906-8dd7-0a234b58ddaf
  modified: 2026-10-20T04:02:12.656Z
---

Idle_Front (Game Design request: boss only looks forward) approved at v14 on 2026-10-20 via the team review page.
Built by tools/blender/idle_front_build.py (shared sine breath curve 26F in / 33F out, overlap lags, spine bend, IK right arm, mace_delay, cloth_flaps with wind). Exported with tools/blender/export_clip.py: work/boss_gaygor/idle_front/export/EN_M11_Boss_Gaygor_Idle_Front.fbx, work/boss_gaygor/blender/boss_idle_front_baked.blend.

**Why:** reference point for the next idle/breath variants and the review workflow.
**How to apply:** rebuild variants with idle_front_build(**changes); the reviewer cares about rhythm (exhale longer than inhale), overlap chains, heavy-prop drag and lively secondary cloth. See [[reference-review-page]], [[feedback-review-listening]], [[project-gaygor-idle-approved]].
