---
name: pose-no-ctl-curves
description: "In Pose, the user wants to animate by selecting joints directly (joint dots), not Maya-style CTL curves"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 54cd37d1-1c51-427b-abd6-dc2deffeb774
  modified: 2026-10-27T16:41:49.818Z
---

Do not add Maya-style control curves (FK rings, IK foot boxes, COG circles) to the Pose workspace / Pose Lab. Keep the original interaction: pick the joint dots, rotate (E), move hip / ankle (IK foot) / wrist (IK hand), knee/elbow pole diamonds.

**Why:** 2026-10-27 the user first said "Thiếu CTL", picked FK + IK legs in Pose only, then on seeing the rings in Pose said to remove them and "dùng đối joint như ban đầu là được".

**How to apply:** if "CTL" comes up again, ask what is actually missing before drawing curves; improve joint picking/handles instead.
