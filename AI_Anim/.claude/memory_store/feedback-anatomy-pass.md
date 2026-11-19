---
name: feedback-anatomy-pass
description: After keying, run anatomy check on every key AND every code-generated inbetween (twist/jump scan per frame) before sending
metadata:
  type: feedback
---
After blocking keys, reviewer asked (2026-10-20): "check lại Anatomy toàn thân của từng key chính đã key". The silhouette fit had torn feet off the shins in 9 keys, a backward knee, and limbs under the floor, none visible in IoU.
**Why:** silhouette/IoU fitting ignores joint integrity; IK targets out of reach silently detach copy-location bones.
**How to apply:** run work/blender/anatomy_check.py on every key (segment lengths = joints intact, flex, knee vs toes, twists vs P0, skin strain vs min(bind,P0), BVH penetration vs P0, floor), close-up flagged spots, fix with anatomy_fix.py, before any playblast is sent. See [[feedback-arm-anatomy]], [[feedback-coarse-to-fine]].

Extended 2026-10-22 (SDR06 Reload lhand_b4, user found twisted inbetweens by eye; "AI tự sửa khá khó, người dùng phải vào sửa keypose"): the check ran only on keys, so frames made by code (IK holds, layers, interpolation) were never looked at. **How to apply:** run the anatomy check and a per-frame rotation-jump/twist scan (local twist about bone Y and frame-to-frame angle per bone) on EVERY frame, not just keys, plus a close-up strip of the generated frames, before sending.
