---
name: feedback-workai-auto-status
description: Khi user đang làm dự án Pet: tự cập nhật In Progress/Done subtask GEK-2355..2369 trên WorkAI bằng tools/workai_pet_sync.py
metadata:
  type: feedback
---

User 2026-11-13: khi đang làm dự án Pet (Infinite Defense, việc cha GEK-2273) thì Claude tự tích trạng thái trên WorkAI, không hỏi lại.

- Công cụ: `tools/workai_pet_sync.py` (chạy nền `--loop 120`, `--once`, `--dry`). Token Ngọc (id 435) trong tools/workai/.env.
- To Do → **In Progress** khi có agent Paseo "Pet NN" chạy, hoặc file .fv của Pet đang mở trong một cửa sổ Frolvy (kể cả cửa sổ user tự mở, user 2026-11-13: "đang làm con nào thì đánh In Progress"), hoặc thư mục `New_PET\Pet_NN_*` có file .fv. → **Done** chỉ khi thư mục có file `CHOT.txt` + đủ 3 FBX; Claude tạo `CHOT.txt` khi user nói "chốt <Pet>" (xuất FBX xong, kiểm xong). Không bao giờ lùi trạng thái.
- GEK-2370 (xuất FBX + đẩy Unity) và việc cha GEK-2273: làm tay, không do công cụ.

**Why:** phiên con có thể xuất FBX sớm trước khi user chốt, nên FBX không chứng minh đã duyệt ([[feedback-export-only-on-approval]]).
**How to apply:** mỗi phiên mới làm Pet, bật lại bộ chạy nền nếu chưa chạy; nhớ tạo CHOT.txt khi user chốt. Xem [[reference-workai]].
