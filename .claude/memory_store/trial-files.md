---
name: trial-files
description: "File thử rig / anim của Claude: thử trên bản sao bằng tools/spine/trial.py, ghi kết quả vào trials.md, xoá ngay khi có kết quả"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f0bf9c9c-d257-471b-952a-718c16dd07a7
  modified: 2026-11-05T02:04:28.591Z
---

Mọi file Claude tạo ra để thử rig / anim (bản sao JSON, ảnh snap, contact sheet) phải được ghi kết quả rồi xoá ngay khi đã có kết quả. Spine: `tools/spine/trial.py new <json> <tên> --why` -> `done <tên> --result "..."` (sổ `<thư mục skeleton>/trials.md`, xoá bản sao + ảnh + kho Hoàn tác / Phiên bản của bản sao). Luật cũng nằm trong CLAUDE.md.

**Why:** người dùng 2026-11-05: "những file mà claude tạo ra để thử rig, anim hãy lưu lại kết quả thử và tự động lập tức xóa file thử sau khi đã đạt được kết quả". Trước đó `_live/` và kho versions (297 MB) / backup (117 MB) đầy ảnh và JSON thử bỏ lại.

**How to apply:** không tự tạo `_live/_xxx.json` hay ảnh thử bằng tay; dùng trial.py. Thử trong bộ nhớ (không ghi file) thì vẫn ghi kết quả vào sổ. Ảnh định gửi người dùng thì `--keep`. Đầu phiên có thể chạy `trial.py sweep` để dọn lần thử bỏ dở. Liên quan [[spine-feedback-scope]].
