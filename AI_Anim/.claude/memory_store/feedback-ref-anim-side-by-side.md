---
name: feedback-ref-anim-side-by-side
description: Review images show REF on one side and ANIM render on the other, never a blended overlay
metadata:
  type: feedback
---

Ảnh so sánh gửi user: ref một bên, anim (render thật, không trộn) một bên.

**Why:** user 2026-10-22 (Walk): overlay trộn đỏ lên ref "khó nhìn".
**How to apply:** dùng `work/boss_gaygor/walk/left_ov.py <dir> <frame> <view>` (REF | ANIM, 1 góc). Overlay chỉ dùng để tự đo, không gửi user. Liên quan [[feedback-one-view-at-a-time]].
