---
name: spine-live-in-paseo
description: "Khi chạy trong Paseo: mở Spine Live trong trình duyệt tích hợp của Paseo (browser_* MCP) và đẩy sửa thẳng lên trang đó, không đưa link"
metadata:
  node_type: memory
  type: feedback
  originSessionId: a8e5414e-55f0-4a6f-a13b-6715d5abf821
  modified: 2026-11-06T08:35:34.633Z
---

Người dùng 2026-11-06: "từ giờ hãy link trực tiếp với những trang spine và update kéo trực tiếp sửa lên những trang spine trong ứng dụng Paseo". Với Spine Live (http://127.0.0.1:8781/spine?json=...): mở / điều hướng bằng công cụ `browser_*` của Paseo (`browser_list_tabs` → `browser_navigate` tab Spine Live có sẵn, chưa có thì `browser_new_tab`), không đưa link bảo người dùng bấm. Sau mỗi bước sửa đẩy thẳng lên trang đó: `tools/spine_live_cmd.py show <json> --anim <a> [--frame N] [--say ...]` (trang Theo Claude tự nhảy), kiểm bằng `status` / `browser_evaluate`.

**Why:** người dùng muốn thấy sửa ngay trên trang đang mở trong Paseo, không qua bước bấm link. Thay thế ngoại lệ VS Code ở [[spine-live-in-claude-only]] khi phiên chạy trong Paseo.

**How to apply:** cần Paseo bật browser automation + có app desktop làm browser host. Nếu không có tool `browser_*` (lỗi `browser_disabled` / `browser_no_host`) thì nói rõ, vẫn đẩy qua `spine_live_cmd.py show` cho trang đã mở, đừng im lặng quay lại đưa link. Không mở Chrome ngoài.
