---
name: spine-feedback-scope
description: Góp ý anim Spine chỉ sửa anim đang mở trên Spine Live; góp ý rig / weight thì sửa cho toàn bộ anim
metadata:
  node_type: memory
  type: feedback
  originSessionId: f0bf9c9c-d257-471b-952a-718c16dd07a7
  modified: 2026-11-05T01:58:25.628Z
---

Góp ý về ANIM (nhịp, overlap, curve, pose...) chỉ sửa đúng anim đang mở trên Spine Live (xem `player.animationState.getCurrent(0)` hoặc focus của trang); không đổi tham số / hàm dùng chung làm các anim khác đổi theo. Góp ý về RIG / WEIGHT / mesh thì sửa ở rig, áp cho mọi anim.

**Why:** người dùng 2026-11-05 (Gentleman): xin sửa overlap hai tay, Claude sửa luôn walk / idle; người dùng: "sửa ở anim spawn L ... chỉ sửa feedback về anim ở anim đang mở ở spinelive hiện tại, còn về rig, weight thì mới sửa ở toàn bộ anim".

**How to apply:** trước khi sửa anim, đọc anim đang mở trên trang. Script dựng nhiều anim (vd `build_walk.py`) thì thêm nhánh riêng cho anim đó (tham số riêng, `if side < 0`...) và ghi riêng bằng `--anim <tên>`; kiểm sau khi ghi chỉ anim đó đổi. Không rõ góp ý thuộc anim nào thì hỏi. Liên quan [[spine-live-push-branch]].
