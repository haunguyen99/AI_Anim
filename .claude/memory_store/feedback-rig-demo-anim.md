---
name: feedback-rig-demo-anim
description: "Spine: sau MỖI lệnh rig tự dựng anim `rig_demo` + đẩy lên Spine Live (trang tự cập nhật, không bắt người dùng tải lại)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5606ebcf-7008-4ec1-bd2b-7d9d183cb23f
  modified: 2026-11-19T08:42:46.688Z
---

Người dùng 2026-11-19: "sau mỗi lệnh rig hãy auto làm 1 anim setup demo rig để demo rig trực quan" và "không cập nhật live à? tôi cần cập nhật liên tục auto không cần thủ công load lại".

**Why:** người dùng xem rig trên Spine Live bên cạnh khung chat; ảnh tĩnh setup khó thấy xương / weight đúng hay sai, và ghi file mà không `show` thì trang không nhảy theo.

**How to apply:** xong bước rig (xương / mesh / weight / slot) → `tools/spine/rig_demo.py <json>` (hoặc `build_demo()` riêng của nhân vật) → `spine_live_cmd.py show <json> --anim rig_demo --bones --say ...`; mỗi bước làm việc đều `show`/`say` lên trang. Mẫu: Unlock `work/unlock/spine/Unlock/build_anims.py`. Ghi trong skill spine2d (mục Rig) và spinelive. Liên quan [[reference-spine-live]], [[spine-live-in-paseo]].
