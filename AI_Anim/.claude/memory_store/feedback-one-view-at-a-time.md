---
name: feedback-one-view-at-a-time
description: "Match/key the pose one camera view at a time and review each view before moving to the next, for fast review"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b0850603-fd00-4d14-bf10-59aec256f552
  modified: 2026-10-22T10:22:43.995Z
---

Khi khớp pose với ref, làm từng góc camera một (front, left, back, right, top), gửi user duyệt 1 góc xong mới sang góc kế; không key/đo cả 5 góc cùng lúc.

**Why:** user nói 2026-10-22 (Gaygor Walk): "key từng góc một thôi, để có review nhanh, 1 góc đơn mới qua key các góc khác".
**How to apply:** mỗi vòng chỉ render + overlay 1 góc (rẻ hơn, xem nhanh), chốt góc đó rồi mới sang góc sau. Kết hợp [[feedback-quick-render]] và [[feedback-report-slow-steps]].
