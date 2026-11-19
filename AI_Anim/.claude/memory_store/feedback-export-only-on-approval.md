---
name: feedback-export-only-on-approval
description: Pet (và nhánh con): chỉ xuất FBX khi user bảo "chốt"; các vòng sửa/feedback chỉ sửa trong Frolvy, không xuất
metadata:
  type: feedback
---

Nhánh con (phiên Pet) KHÔNG xuất FBX sau mỗi vòng sửa hoặc feedback. Chỉ xuất khi user nói "chốt" (rồi mới chạy quy trình xuất + kiểm).

**Why:** user 2026-11-13: xuất sau mỗi vòng tốn thời gian, sinh file cũ/rác trong thư mục, và bản chưa duyệt không cần vào Unity.
**How to apply:** vòng sửa/feedback: sửa trong Frolvy, lưu .fv, tự kiểm bằng viewport/số đo, báo user. Nhận lệnh chốt thì xuất theo [[feedback-fbx-base-vs-anim]] (Base + _Idle + _Attack, tên gạch dưới). Brief Pet mới ghi sẵn luật này (work/infinite_defense/pets/make_brief.py).

## Quy trình khi user nói "chốt <Pet>" (user 2026-11-13: "chốt thì tự tối ưu: file mới giữ, ver cũ xoá hết, xuất fbx đã chốt")
1. `tools/pet_chot.py clean <ID>`: giữ .fv MỚI NHẤT của mỗi clip (rig / idle / attack), xóa bản cũ cùng clip, raw_*.fbx, _tmp. Giữ _src, _orig, report.
2. Xuất FBX chốt (Base + _Idle + _Attack, tên gạch dưới) từ các file vừa giữ: bảo phiên Pet đó (Paseo) chạy quy trình xuất trong brief, hoặc chạy finalize của con đó (`work/infinite_defense/pets/<pet>/finalize.sh`).
3. `tools/pet_chot.py check <ID>`: Base có mesh + deformer + BindPose, 0 AnimationStack; file anim 0 mesh, có Dummy. Đạt thì `mark <ID>` ghi CHOT.txt (`all <ID>` làm clean + check + mark) → bộ canh tích Done trên WorkAI ([[feedback-workai-auto-status]]).
4. Không chép vào Unity trừ khi user bảo ([[reference-pets-unity-folder]]). Báo user ngắn: đã xóa gì, xuất gì, kết quả kiểm.

**Thống nhất thư mục sau chốt (user 2026-11-13, sau khi thấy các thư mục Pet không đồng nhất):** mỗi Pet đã chốt chỉ còn ĐÚNG 3 FBX trong `New_PET\Pet_NN_*` (Base, _Idle, _Attack) + .fv mới nhất mỗi clip. Mọi FBX khác bị xóa: raw_*, _src, _orig, _old_fbx, và bản sao mesh + `fbx_backup` bên `work/infinite_defense/pets/<tên>/`. `pet_chot.py clean` làm đủ việc này (đã mở rộng). Phải chạy `clean` cho MỌI Pet chốt, không chỉ vài con.
**"Xóa" khi chốt = bỏ vào Thùng rác Windows (user chọn 2026-11-13)**, không xóa hẳn: lệnh xóa hàng loạt bị hệ thống chặn, `pet_chot.py clean` đã đổi sang `recycle()` (khôi phục được). Đã dọn Pet 11, 12, 13, 15, 16, 17.
