---
name: reference-joint-rules
description: "tools/joint_rules.py — joint limits + coupling (scapula follows arm, spine/neck share, hip lead); audit+apply every key, rules JSON per job"
metadata:
  node_type: memory
  type: reference
  originSessionId: 2db84807-3565-4ae3-be18-19c96cd257e1
  modified: 2026-10-31T01:54:05.931Z
---

User asked 2026-10-31 that AI use ALL joints together (raise arm → clavicle/scapula follows), not single joints.
Built `tools/joint_rules.py` + `tools/joint_rules/biped.json` (job override `work/<proj>/<job>/joint_rules.json`).
Measured vs approved P0; `apply(..., keep="hand")` keeps the hand world via `keep_hand` (rigpose `ik_arm` flips bent elbows).
Details + v1 curves: `.claude/skills/animation/knowledge/details/qa_anatomy.md#joint-coupling`.
Studio since 2026-10-31: modules/joint_rules.js (button 'Liên động', runs after each gizmo drag / AI rot-pos), bridge `anim rules on|off|status|audit|apply`. No joint-limit check in Studio yet.
Related: [[feedback-arm-anatomy]], [[feedback-anatomy-pass]], [[reference-studio-bridge]].
