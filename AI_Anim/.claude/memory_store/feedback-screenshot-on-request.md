---
name: feedback-screenshot-on-request
description: Only take browser screenshots when the user asks for one; otherwise check page state via JS/read_page and report in text
metadata:
  node_type: memory
  type: feedback
  originSessionId: 98415810-dce9-4d70-8e09-d4120141ccff
  modified: 2026-10-27T11:10:46.138Z
---

User 2026-10-27: "từ giờ những gì tôi yêu cầu cần phải chụp hình thì mới chụp nhé!"

**Why:** user xem trực tiếp trên trang (Studio, Home, các Lab), nên chụp màn hình chỉ làm chậm và tốn thời gian ([[feedback-studio-quick-edits]]).
**How to apply:** khi dùng trình duyệt, không gọi screenshot/zoom trừ khi user yêu cầu chụp hình. Kiểm tra kết quả bằng javascript_tool, read_page hoặc find, rồi báo ngắn bằng chữ. Click theo ref hoặc dùng JS thay vì đọc tọa độ từ ảnh chụp. Các bản render/playblast của quy trình anim ([[feedback-quick-render]], [[feedback-eye-first]]) không thuộc quy tắc này: đó là việc kiểm tra pose, không phải chụp màn hình báo cáo.
