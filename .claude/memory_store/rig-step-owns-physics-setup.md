---
name: rig-step-owns-physics-setup
description: "User wants control-joint choice, joint limits, colliders and per-part mass authored in the Rig workspace, not hardcoded in Pose"
metadata:
  node_type: memory
  type: project
  originSessionId: 54cd37d1-1c51-427b-abd6-dc2deffeb774
  modified: 2026-10-27T16:52:31.929Z
---

Direction set by the user 2026-10-27: the Rig step (Studio workspace Rig) must own the character setup that Pose uses — which joints are controllable in Pose (markers, rotate / move), joint rotation limits, collision shapes (colliders) and the mass of each body part for physics. Today Pose Lab keeps these per character in code (`CHAR_PHYS` in `work/pose_lab/index.html`: Gaygor springs, colliders, `limits` [bend lo/hi, spread lo/hi, twist lo/hi], rest pose; body capsules and mass = capsule volume × 1000 kg/m³ computed in Pose).

**Why:** a character rigged in Studio (e.g. Boss_Gragas) gets no limits / colliders / masses, and the controllable-joint list is hardcoded in Pose.

**How to apply:** build these as a Rig step that saves to the character's rig store and is read by Pose (fallback to `CHAR_PHYS` for old characters). Related: [[pose-no-ctl-curves]] (Pose selection stays joint dots, no curve controls).
