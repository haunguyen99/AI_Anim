---
name: feedback-ref-video-cut-segment
description: Ref video đưa vào quy trình anim phải cắt thành đoạn cụ thể, không đưa video thừa thông tin
metadata:
  type: feedback
---

Ref video phải cắt thành đoạn cụ thể (đúng pha / hành động cần làm), không đưa cả video có thông tin thừa (intro, chữ, cảnh khác).

**Why:** người dùng 2026-11-26, khi dựng slide quy trình Animation với AI, bước intake: "lưu ý cắt thành video đoạn cụ thể, không đưa video có thông tin thừa".

**How to apply:** trước khi phân tích ref, cắt bằng ffmpeg (yt-dlp tải nếu là link), ghi link gốc + mốc giờ + lý do; ref cũng phải hợp concept animation. Luật đã vào `CORE.md` và `review_process.md#ref-cut`. Slide: `docs/slides/quy_trinh_animation_ai.html`. Liên quan [[project-nova-attack-analysis]].
