---
name: feedback-arm-anatomy
description: User rejected Attack f13 v1 arms ("bẻ quá giới hạn và xoắn vặn hỏng anatomy") - never force hand orientation on a prop; solve arms anatomically and check close-ups
metadata:
  type: feedback
---

User (2026-10-20, Attack f13 v1): "xem lại hai cánh tay bị bẻ quá giới hạn và xoắn vặn hỏng anatomy."

**Why:** I placed both hands on the mace with a fixed palm/finger orientation, so the wrists absorbed 70-75 deg twist/bend (hand hooked over the shaft, palm-up hand bent back with straight fingers, forearm armour twisted, elbow/armpit pinched). Silhouette IoU looked fine, which hid it.
**How to apply:** For every hand-on-prop pose use `work/blender/attack_pose.py` `solve_grip` (grip slides on the shaft, pure-hinge elbow, wrist near its P0 grip relation, elbows outside the torso, skin strain re-score), move the shoulder/chest when an arm would be straight, and look at ortho close-ups of each arm (`closeup`) before showing a pose. Rest-relative twist numbers can be 180 deg off on this rig - trust close-ups and `arm_strain`. See [[feedback-pose-accuracy]], [[feedback-eye-first]].
