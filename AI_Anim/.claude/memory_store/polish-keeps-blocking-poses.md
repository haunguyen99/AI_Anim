---
name: polish-keeps-blocking-poses
description: "Khi polish/spline anim, không tự đổi pose chính đã duyệt ở blocking; muốn đổi thì hỏi trước"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e7f5846c-b962-471d-8737-e620fc931e10
  modified: 2026-10-30T05:03:58.434Z
---

Polish chỉ thêm overlap, khăn, spacing, chi tiết lên các pose blocking đã duyệt — không tự ý dời / đổi pose chính (vd kéo tay ném
về điểm khác lúc thả). Nếu thấy pose blocking cần đổi (vd điểm thả shuriken lệch vì overlap ngực), nêu vấn đề + đề xuất và hỏi trước.

**Why:** Ninja Attack polish_v7 (2026-10-30) mình tự kéo cổ tay ném về trước mặt ở F9–F12 để shuriken "bay ra trước mặt" →
user: "sao lại tự ý chỉnh sửa bản polish khác với blocking vậy", "v7 loại bỏ, xấu quá", bắt quay về polish_v6.

**How to apply:** trước khi chạy một bản polish mới, đối chiếu các key chính với blocking đã duyệt; mọi thay đổi pose (không chỉ
overlap/secondary) phải được user đồng ý trước. Xem thêm [[studio-script-single-writer]].
