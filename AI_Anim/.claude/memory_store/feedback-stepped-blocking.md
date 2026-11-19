---
name: feedback-stepped-blocking
description: "Blocking must be reviewed stepped (CONSTANT curves) in a Blender playblast; work in the live Blender scene, not the headless keys.json path"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 2e2aecb8-a088-4690-9c6d-9291f3ba6326
  modified: 2026-10-19T08:55:17.331Z
---

User (2026-10-19, attack clip): asked why I keyed through keys.json/headless instead of Blender live, then: "ở bước Blocking, khi playblast bạn nên để curve là step by step".

**Why:** Stepped playblast shows each pose and its timing without spline hiding errors; the live scene (work/boss_gaygor/blender/boss_idle.blend, CTRL rig) is where the user can watch and hand-tweak. Headless keys.json is at best a scratch pass to get pose numbers.
**How to apply:** Key blocking on the CTRL rig in the live scene with interpolation CONSTANT (`set_interp(obj, "CONSTANT")`), playblast via tools/blender/live_render.py + tools/playblast_compose.py, send review_blocking.mp4, then wait for review before splining. Poses can be transferred from a headless build with work/blender/key_attack_blocking.py (world matrices → FK bones + CTRL targets). See [[feedback-iterate-in-house]], [[feedback-eye-first]].
