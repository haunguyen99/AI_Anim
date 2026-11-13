---
name: polish-keeps-blocking-poses
description: "Khi polish/spline anim, không tự đổi pose chính đã duyệt ở blocking; muốn đổi thì hỏi trước"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e7f5846c-b962-471d-8737-e620fc931e10
  modified: 2026-11-05T04:25:15.890Z
---

Polish chỉ thêm overlap, khăn, spacing, chi tiết lên các pose blocking đã duyệt — không tự ý dời / đổi pose chính (vd kéo tay ném
về điểm khác lúc thả). Nếu thấy pose blocking cần đổi (vd điểm thả shuriken lệch vì overlap ngực), nêu vấn đề + đề xuất và hỏi trước.

**Why:** Ninja Attack polish_v7 (2026-10-30) mình tự kéo cổ tay ném về trước mặt ở F9–F12 để shuriken "bay ra trước mặt" →
user: "sao lại tự ý chỉnh sửa bản polish khác với blocking vậy", "v7 loại bỏ, xấu quá", bắt quay về polish_v6.

Lần 2 (Windy Idle, Frolvy, 2026-11-05): user tự chỉnh pose (trượng cầm chéo ngang thân), Director góp ý, user nói "chỉnh sửa
lại đi" → mình tự đổi tay cầm trượng (dựng trượng, trượt trượng trong tay, xoay cổ tay) → user: "sao lại tự ý sửa tay cầm vũ
khí vậy", bắt về lại pose của user. "Sửa theo Director" KHÔNG phải là cho phép đổi phần user đã tự chỉnh: lỗi chạm tới pose user
chỉnh (tay cầm vũ khí, hướng prop...) thì đưa phương án + hỏi; chỉ tự sửa phần user chưa đụng tới.

**How to apply:** trước khi chạy một bản polish mới, đối chiếu các key chính với blocking đã duyệt; mọi thay đổi pose (không chỉ
overlap/secondary) phải được user đồng ý trước. Xem thêm [[studio-script-single-writer]].
