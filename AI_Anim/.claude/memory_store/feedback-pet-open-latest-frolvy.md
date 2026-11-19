---
name: feedback-pet-open-latest-frolvy
description: Khi user đang làm Pet nào: tự đóng cửa sổ Frolvy bản cũ và mở file .fv mới đã sửa cho user (tools/pet_frolvy_tidy.py)
metadata:
  type: feedback
---

User 2026-11-13: khi đang làm một dự án/con Pet, Claude tự **tắt các file Frolvy cũ không dùng và mở luôn file mới** của Pet vừa sửa, để user khỏi tắt/bật tay để check.

- Công cụ: `tools/pet_frolvy_tidy.py` (`--loop 60` chạy nền, `--once`, `--dry`). Pet đang làm = có phiên Paseo "Pet NN" chạy hoặc file .fv của Pet đang mở trong một cửa sổ Frolvy ([[feedback-workai-auto-status]]).
- Mỗi clip (idle/attack/rig) gom theo họ phiên bản (`_new`, `_v2`...): cửa sổ đang mở bản cũ của một clip → mở bản mới nhất, đóng bản cũ. File lưu trong 10 phút gần nhất cũng được mở. Cổng Frolvy mới từ 9900.
- **An toàn:** không đóng cửa sổ có dấu `*` (chưa lưu) hoặc cửa sổ của Pet có phiên đang chạy; không đóng cửa sổ không phải file Pet.

**Why:** user tốn công tắt/bật Frolvy để xem bản mới sau mỗi vòng sửa.
**How to apply:** khi làm Pet, bật chạy nền `pet_frolvy_tidy.py --loop 60` cùng `workai_pet_sync.py --loop 120`.
