---
name: feedback-export-only-on-approval
description: Pet (và nhánh con): chỉ xuất FBX khi user bảo "chốt"; các vòng sửa/feedback chỉ sửa trong Frolvy, không xuất
metadata:
  type: feedback
---

Nhánh con (phiên Pet) KHÔNG xuất FBX sau mỗi vòng sửa hoặc feedback. Chỉ xuất khi user nói "chốt" (rồi mới chạy quy trình xuất + kiểm).

**Why:** user 2026-11-13: xuất sau mỗi vòng tốn thời gian, sinh file cũ/rác trong thư mục, và bản chưa duyệt không cần vào Unity.
**How to apply:** vòng sửa/feedback: sửa trong Frolvy, lưu .fv, tự kiểm bằng viewport/số đo, báo user. Nhận lệnh chốt thì xuất theo [[feedback-fbx-base-vs-anim]] (Base + _Idle + _Attack, tên gạch dưới). Brief Pet mới ghi sẵn luật này (work/infinite_defense/pets/make_brief.py).
