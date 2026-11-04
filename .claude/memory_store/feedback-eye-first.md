---
name: feedback-eye-first
description: Look at the problem by eye (all views incl. top/game) and name it before reaching for silhouette/numeric optimisation
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7d2b80c9-f2b6-4906-8dd7-0a234b58ddaf
  modified: 2026-10-19T08:07:44.031Z
---

User (2026-10-19), after I chased a weapon/hand complaint with silhouette solvers: "Đừng quá phụ thuộc vào silhouette để giải quyết mọi vấn đề. Trước tiên cần nhìn tổng quan bằng mắt xem vấn đề thực sự là gì. Sau đó mới tìm phương án sửa chi tiết."

**Why:** Silhouette/tracking fits hid the real defect. Viewed side by side (and from the top ref view) the actual problem was obvious: the left hand floated 11 cm off a 30 cm-radius shaft and the weapon sat 15 cm too far back. The optimiser had compensated with wrong moves instead.
**How to apply:** For any feedback, first put REF next to ANIM in every view (top/game views too), describe in words what differs (which part, which direction), then fix that specific thing directly on the control rig (e.g. tools/blender/grip_set.py), and verify by eye again. Use numeric solvers only for well-defined sub-problems. See [[feedback-iterate-in-house]].
