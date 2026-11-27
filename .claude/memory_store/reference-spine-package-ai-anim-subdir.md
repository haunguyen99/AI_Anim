---
name: reference-spine-package-ai-anim-subdir
description: "Thư mục con AI_Anim/AI_Anim = gói kiến thức Spine 2D (skill, memory_store, tools/spine*, MAP.md) không kèm dữ liệu; máy Linux này chưa có file Spine / venv Linux"
metadata:
  node_type: memory
  type: reference
  originSessionId: 28d1723c-2f5a-42e3-be8e-3d5f9772a888
  modified: 2026-11-20T02:56:20.143Z
---

`/home/huongbtx/Desktop/DataHDD/Project/AI_Anim/AI_Anim` (người dùng chỉ vào 2026-11-20, "nạp toàn bộ kiến thức từ dữ liệu này") là gói gọn của dự án, dùng cho việc Spine 2D: 6 skill (spine2d, skillidle, skillactive, exportspine, skillreport, spinelive), `.claude/memory_store/` (~120 memory, bản cũ hơn bản trong repo cha ở vài file; repo cha có thêm Nova / Frolvy), `tools/spine*`, `tools/spine_live/`, `MAP.md`, `HUONG_DAN.txt`. Không có `work/` dữ liệu (chỉ README: chép Spine / PSD vào `work/<game>/spine/<anim>/`).

**Why:** máy Linux này chưa có file Spine nào; `/spinelive` báo danh sách rỗng.
**How to apply:**
- `.venv/Scripts/python.exe` là venv Windows (Exec format error trên Linux). `tools/setup.sh` sẽ `rm -rf .venv` rồi dựng lại: không chạy khi chưa hỏi, vì `.venv` nằm trên ổ dùng chung với Windows. Muốn có numpy / PIL: tạo venv riêng (`~/.venvs/ai_anim`).
- Python hệ thống (3.12.3, không numpy) đủ để bật `tools/spine_live/server.py` (cổng 8781) và chạy `spine_live_recent.py`, nhưng snap / mesh / weight sẽ lỗi 500 (cần numpy). Xem thêm quy tắc Spine Live trong skill `spinelive`.
- Khôi phục memory của gói: `claude_memory.py restore` ghi vào thư mục memory của đúng thư mục chạy lệnh, không đụng memory của repo cha.
