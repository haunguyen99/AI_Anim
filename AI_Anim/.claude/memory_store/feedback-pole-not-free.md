---
name: feedback-pole-not-free
description: "IK pole vectors must never be a free solver output: parent knee poles to the foot IK, elbow poles to chest/hand, write elbow/knee direction into each key spec, run pole_audit.py before every render"
metadata:
  type: feedback
---

User 2026-10-22: "ở dự án SDR việc để pole vector của IK tự do tốn rất nhiều lần thử hãy rút kinh nghiệm từ đó".

**Why:** in SDR map06 the elbow direction came out of the solver, and each review round added one constraint (elbow out, elbow low, shoulder twist, elbow sinking into the body, twisting during spline). That cost about 9 rounds, and every fix broke an earlier one.
**How to apply:** knee pole is a child of the foot IK; elbow pole is a child of the chest, or of the hand when it holds a prop. Read the elbow/knee direction from the ref as part of the key spec. The solver only searches ±30° around that direction. Before every render, run `tools/blender/pole_audit.py` (knee vs toes ≤ 30°, elbow drop 12–20 cm, upper-arm roll jump ≤ 60°) together with elbow_gap and shoulder skin. Details: knowledge `arms_hands.md#pole-spec`. Related: [[feedback-arm-anatomy]], [[feedback-anatomy-pass]].
