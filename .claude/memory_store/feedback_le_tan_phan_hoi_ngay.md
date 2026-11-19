---
name: feedback-le-tan-phan-hoi-ngay
description: "Lễ tân HorusChat phải phản hồi người nhắn ngay lập tức, không để khách chờ lâu"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f671f962-39d6-4a7e-a750-73cf3ab87f99
  modified: 2026-11-18T04:45:13.090Z
---

Hậu (2026-11-18): khi nhiều người order, khách phải chờ khá lâu agent mới phản hồi; cần agent phản hồi ngay sau khi người dùng gửi tin.

**Why:** lễ tân là mặt tiền chăm sóc khách; chậm làm khách nghĩ AI không nghe.

**How to apply:** chạy `horuschat_cli.py wait` một mình; có tin thì xử lý/đáp ngay, KHÔNG chạy kèm `workai_watch.py` trước khi đáp (chỉ chạy workai_watch khi `wait` hết hạn). Tin gửi cho AI: đáp xác nhận một câu trước, việc nặng giao subagent chạy nền (mỗi order một subagent, lễ tân chỉ làm rõ yêu cầu với khách). Xem [[le-tan-vai-tro]] nếu có.
