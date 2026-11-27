---
name: feedback-spinelive-auto-update-paseo
description: "Spine Live mở trong Paseo (máy Linux này) phải tự nạp lại mỗi khi file đổi; đã thêm ô \"Tự cập nhật\" mặc định bật, poll không dừng khi pane ẩn"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 28d1723c-2f5a-42e3-be8e-3d5f9772a888
  modified: 2026-11-20T03:11:18.212Z
---

Người dùng 2026-11-20: "spinelive khi mở trên paseo máy này cần được chuyển sang chế độ auto update, mỗi lần sửa, prompt không cần tự thủ công reload lại".

**Why:** `poll()` trong `tools/spine_live/index.html` dừng khi `document.hidden`; khung trình duyệt của Paseo báo ẩn khi không đứng ở tab đó, nên file đổi mà trang không nạp.
**How to apply:** sau khi ghi file Spine chỉ báo "đã ghi", không bảo người dùng reload / F5. Nếu họ vẫn thấy không nạp: kiểm ô "Tự cập nhật" còn tích, rồi `curl /api/spine/stat?json=...` xem `t` có đổi không (server bật từ thư mục `AI_Anim/AI_Anim`, không phải thư mục cha, để thấy đúng `work/`). Chưa kiểm được trong Paseo thật (phiên này không có khung trình duyệt). Liên quan [[reference-spine-package-ai-anim-subdir]].
