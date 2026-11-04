---
name: feedback-keypose-flipbook
description: "key pose images of one anim must be consistent like 2D flipbook frames; generate as a chain, check playback"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 607f2297-0f5f-461f-a014-fc25b29527a9
  modified: 2026-10-31T04:53:25.337Z
---

User 2026-10-31: tạo ảnh key pose là "sự đồng nhất", giống diễn hoạt 2D: vẽ các hình rồi chạy liên tiếp thành anim.

**Why:** ảnh rời đẹp nhưng phát lên giật, đổi cỡ, trượt chân thì không dùng được làm blocking demo (▶ Chạy ảnh).

**How to apply:** luật đầy đủ ở knowledge/details/gdd_stage0.md mục "Đồng nhất chuỗi ảnh". Khoá camera/khung/đường đất/chân trụ/tạo hình; key chủ duyệt trước; sinh theo thứ tự với key trước làm ref, chỉ đổi phần ghi; kiểm cả chuỗi bằng số trước khi gửi; sửa thì ref key trước + sau. Liên quan [[reference-codex-img]], [[feedback-pose-accuracy]].

User 2026-10-31 (thêm): mọi lần tạo ảnh mới nhất định gửi concept gốc làm ref + nêu trong prompt, để không ra nhân vật/đồ vật khác. keypose_gen.py tự thêm (keypose.concept_for/concept_text), thiếu concept thì dừng.

User 2026-10-31 (thêm): key sau viết prompt + lấy ref từ ảnh key trước (keypose_gen.py tự làm qua tools/keypose_chain.py); đo độ lệch NGAY sau mỗi ảnh (không đợi đủ chuỗi vì tốn tài nguyên), căn khung tự động, key trước lệch thì chặn key sau.
