---
name: frolvy-head-aim-keep-roll
description: "Turning the head toward a target in Frolvy: never key ry alone or aim only the forward vector (head tilts sideways = \"gãy cổ\"); solve rx+ry+rz to hit target yaw while keeping pitch and roll of the base pose"
metadata:
  node_type: memory
  type: feedback
  originSessionId: a81c2cb7-d80d-4705-a6fd-a5851ab16438
  modified: 2026-11-06T06:47:11.570Z
---

User 2026-11-06 (Hero_Blade_Attack_01, head looks at pCylinder1): head tilted to one side "như bị gãy cổ", twice ("lỗi này bị lặp lại"). Once from aiming the forward vector with rx+ry only (roll came out −20°), once from keying ry alone (ctrl ry yaws about the head's tilted local Y, so world roll changes).

**Why:** the head control sits under a chest/neck that is already pitched and twisted, so one Euler channel is not a world yaw.

**How to apply:**
- Measure world yaw/pitch/roll of DEF_Head from its matrix (yaw=atan2(m8,m10), pitch=asin(-m9), roll=asin(m1)); target = aim yaw, base pitch, base roll. Solve rx,ry,rz together (3x3 Jacobian by finite differences, a few Gauss-Newton steps) and check roll/pitch within ~0.5° of base before reporting.
- Put it on a new additive layer, rotate channels only, explicit keys at the user's key frames (f0/f8/f12) equal to their base values; `FL.key(…, {}, f)` does not create those keys. Delete keyed custom attrs (`space`) from the layer: additive layers add enums (space 1→2 moved the arm poles).
- Always compare layer on/off at the user's key frames (joints moved = 0) and report roll numbers, not just yaw error.

Related: [[keep-existing-keys-when-editing]], [[feedback-edit-on-layer]].
