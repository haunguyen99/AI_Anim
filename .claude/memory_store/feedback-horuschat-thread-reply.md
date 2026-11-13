---
name: feedback-horuschat-thread-reply
description: Trả lời tin HorusChat vào thread của chính tin đó (kèm --thread) để phòng chat đỡ loạn; xưng hô gọi tên hoặc "bạn"
metadata:
  type: feedback
---

User 2026-11-13: "sau này hãy trả lời vào thread của mỗi tin nhắn để đỡ loạn nhé".

**Why:** phòng như ArtAnimVFX nhiều người nhắn cùng lúc; tin trả lời lẻ ở dòng chính làm loạn.
**How to apply:** mọi nháp/tin đáp một tin cụ thể dùng `horuschat_cli.py draft ... --thread <id>`: tin đã trong thread thì dùng id gốc thread, chưa thì dùng event_id của chính tin đó. Chỉ tin nói chung cho cả phòng mới để dòng chính. Vẫn `--mention` người được đáp, gọi tên hoặc "bạn" (không "anh/chị"). Đã ghi vào tools/subsession/briefs/horuschat_intake.md. Liên quan [[project-ai-employee]], [[feedback-chat-dispatcher]].
