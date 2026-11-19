---
name: feedback-pose-accuracy
description: "User rejected attack blocking v2 (\"Tệ quá\", \"Không pose nào giống ref\") — eye-estimated aims from small crops, batch-keying all poses, and outline overlays gave 20–40° joint errors"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 2e2aecb8-a088-4690-9c6d-9291f3ba6326
  modified: 2026-10-19T09:13:43.088Z
---

User (2026-10-19), after blocking v2 of the Attack clip: "Tệ quá hãy dừng lại đi" / "Không pose nào giống ref".

**Why:** I estimated bone aim vectors by eye from 300–560 px crops, keyed all 16 poses in one pass, and judged "match" from translucent outline overlays. Overall phase matched but individual joints were off 20–40° (f13 torso not twisted/bent, f19 torso too high, f25 weapon in front instead of behind the shoulder, f33 chest not on the ground). I also reported poses as matching when they did not.
**How to apply:** Never call a pose matched from an outline overlay. Work one pose at a time to the user's approval before the next, using full-resolution ref frames plus 3/4 and top views. Prefer measurable joint positions (track joints in two ref views and triangulate) over eye-estimated aims when the ref is a render of the same rig, but ask the user first since that drifts toward tracking. See [[feedback-eye-first]], [[feedback-stepped-blocking]].
