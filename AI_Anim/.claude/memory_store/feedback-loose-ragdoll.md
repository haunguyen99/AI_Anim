---
name: feedback-loose-ragdoll
description: "Physics falls must look limp, not like a falling statue; the user's last key is a direction, not a 100% target"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 20043592-be79-4e6b-b2ba-600a995b91bb
  modified: 2026-10-26T02:51:42.767Z
---

User 2026-10-26 on Ragdoll "Về đích": "Không nhất thiết phải giữ đúng pose cuối 100%... bạn đang kéo cứng, khiến nhân vật như một bức tượng đá đổ xuống"; approved the limp v3 ("Bản lỏng ổn rồi", tag ragdoll-goal-v3-approved).

**Why:** strong muscle drives toward the key (and slow strength loss) made the body fall as one block and pose itself after landing; the user values a natural limp collapse over exact pose matching.

**How to apply:** in ragdoll / physics deaths keep muscles weak and losing strength fast (head/arms/legs loose, knees give), no held tone; match the user's end key only partly (Pose Lab "Khớp pose cuối", default 50%) unless asked for exact. Judge by eye for "statue" signs: elbows/head fixed to the torso while falling, constant-speed self-posing after landing. Related: [[reference-pose-lab]], [[feedback-eye-first]].

Also 2026-10-26 (approved "oki rồi", tag poselab-goal-poseonly-push-approved): the end key matches the POSE only, not the place ("chỉ dáng", default) — never drag the hips back to the key's place, and never weaken the hit/push to get there ("nó làm mất cả lực tác động ban đầu"). The body lies where the impact sends it.
