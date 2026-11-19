---
name: frolvy-additive-layer-euler-coupling
description: "Frolvy additive layer does not add rotation per channel on shoulder FK; FL.key totals drift, fix by re-key loop and key every frame of the span"
metadata:
  node_type: memory
  type: reference
  originSessionId: 0783b7cd-def6-482e-9470-d185e0c611df
  modified: 2026-11-09T04:26:05.774Z
---

On Windy (Frolvy 0.9.36), a big rotation change on an additive layer (shoulder/scapula) shows up coupled in the other Euler channels: asking ry -30 gave ry -20 and moved rz/rx too (FL.key err 8-13 deg). Small changes (<= ~10 deg) and elbow/wrist/weapon converge fine.

**Why:** the layer composes rotations, not per-channel sums, so frolvy_layers.key's per-channel write-back is not exact.

**How to apply:**
- Key ALL channels of the touched nodes on every frame of the edited span (target = base total elsewhere), otherwise a lone key makes the layer a constant offset before/after it (leaked into F0-F7 once).
- After FL.key, read the shown value and re-key with cmd += (target - shown), up to ~8 loops; stop when < 0.3 deg. If it diverges (gimbal-like shoulder), reduce the move or use scapula + fewer joints.
- Measure hand/staff world position (world_matrix cols 12-14) to judge the result, not the channel numbers.
- Compare layer muted vs on over all controls to prove only the intended frames changed.

Related: [[edit-on-layer]] (feedback-edit-on-layer.md), [[reference-frolvy-mcp]].
