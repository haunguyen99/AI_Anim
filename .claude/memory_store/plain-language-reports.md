---
name: plain-language-reports
description: "Báo nhận xét Director / kết quả anim cho user bằng lời thường, không thuật ngữ, không tên control trong phần chính"
metadata:
  node_type: memory
  type: feedback
  originSessionId: a61cace9-ee15-4c45-b223-033f8a4d06a8
  modified: 2026-11-05T04:32:38.164Z
---

Khi báo nhận xét Director (hoặc kết quả kiểm anim) cho user: nói người xem đang thấy gì → nên thấy gì → sửa hướng nào, câu ngắn,
tiếng Việt thường. Không thuật ngữ Anh trần (Overlap, Readability...), không tên control/kênh, tối đa 1 con số làm tròn mỗi ý.
Chi tiết kỹ thuật để ở cuối hoặc bỏ.

**Why:** Windy Idle 2026-11-05, sau báo cáo Director blocking dày bảng + số px/cm + tên control, user: "bảo director nói ngôn
ngữ người, nói dễ hiểu 1 chút". Đã thêm mục "Cách nói" vào `.claude/agents/animation-director.md`.

**How to apply:** mọi lần chuyển lời Director cho user, và báo cáo QA anim. Liên quan [[polish-keeps-blocking-poses]].
