---
name: reference-paseo-subagent
description: "Cách giao việc cho phiên con bằng `paseo run` (CLI, brief, theo dõi bằng logs, bẫy quyền kẹt); hướng dẫn đầy đủ ở docs/paseo_phien_con.md"
metadata:
  node_type: memory
  type: reference
  originSessionId: 9d3f18ee-ed13-4e59-8e7c-cfdce2cfd4c4
  modified: 2026-11-13T03:14:42.727Z
---

User 2026-11-13: tạo hướng dẫn nhỏ cho các phiên khác làm theo cách tạo subagent đã dùng (rebind-mayah-pirate, airport-order-anim-vfx, goat-*).

**How to apply:** đọc `docs/paseo_phien_con.md` trước khi giao việc nền. Tóm tắt: `& "C:\Program Files\Paseo\resources\bin\paseo.cmd" run --no-wait --provider "llmpro/claude-opus[1m]" --title <tên> --cwd "E:\AI Animation" $brief` (bắt buộc --provider; mã thoát 255 vẫn là đã tạo, kiểm `paseo ls`); theo dõi `paseo logs <id> --tail N`, nhắn `paseo send --no-wait <id> "..."`, dừng `paseo stop <id>`. Phiên con không tự đánh thức phiên chính. Bẫy: lệnh cần quyền (đọc ngoài thư mục dự án, Unity.exe) chờ người dùng bấm "cho phép" trong Paseo, không bấm thì đứng im; luật quan trọng ghi trong brief đầu tiên vì phiên con làm theo người dùng hơn tin `paseo send`; mỗi phiên một việc; việc chung công cụ chạy tuần tự. Liên quan [[reference-paseo]], [[reference-subsession]], [[feedback-chat-dispatcher]].
