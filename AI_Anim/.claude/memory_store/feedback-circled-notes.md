---
name: feedback-circled-notes
description: Reviewer often sends notes as circles only (no text) - overlay the strokes on the webm frame to read them; a circle on a hold frame means add a key there
metadata:
  node_type: memory
  type: feedback
  originSessionId: f3f1c765-8a3f-48e3-abcd-48032cd1e922
  modified: 2026-10-20T10:02:33.961Z
---

Attack blocking_v5 got 8 notes with only red circles, part "Toàn thân / timing" (2026-10-20). Read them by drawing the
note strokes (normalized x,y × webm w,h) onto the extracted frame; compare REF|ANIM in the circled panels.

**Why:** the reviewer marks what is wrong, not why; circles on hold frames (f26/44/53/60) meant the ref had moved on, and
circles on the mace/hands meant the IoU fit had put the prop and the grips on the wrong side.

**How to apply:** for circle-only notes, diagnose each circle per view yourself (prop position, grip side, head, timing),
measure the prop from the ref (mace_measure.py) instead of trusting silhouette IoU, add keys on circled holds.
Related: [[feedback-eye-first]], [[feedback-pose-accuracy]], [[reference-review-page]].
