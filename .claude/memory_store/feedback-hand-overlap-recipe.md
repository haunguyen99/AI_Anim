---
name: feedback-hand-overlap-recipe
description: "Cách làm tay/vai trễ (overlap) trong Idle cho người dùng duyệt nhanh: tín hiệu, độ trễ, biên độ, chiều xoay, lỗi đã mắc (chững, giựt, mất trễ)"
metadata:
  node_type: memory
  type: feedback
---

Người dùng chỉnh Idle bằng lệnh ngắn kiểu "giảm 20%", "làm ngược lại", "trễ hơn", "giữ nhịp hiện tại"; họ nhìn trên viewport, không đọc số. Làm đúng một việc được nói, báo bằng số đo + 1 dòng cần họ xem.

**Why:** 2026-11-16 chỉnh tay phải / vai Nova IdleShop mất ~10 vòng vì hiểu sai chiều, trễ, trục.
**How to apply:**
- "Trễ so với thân" = chuyển động CÙNG chiều, đến chậm; đảo chiều (hông hạ → tay nhấc) bị đọc là "mất trễ". Đừng dùng hiệu hông(t−L)−hông(t) (hông trôi đều thì ra đường phẳng → "chững"). Dùng bản sao trễ L frame của nhịp hông, khuếch đại ×G, rồi trừ giá trị F0 để F0 giữ pose gốc.
- Key thưa (mỗi 6F; xoay mỗi 3F) + tiếp tuyến Catmull-Rom vòng tròn (`set_key_tangent(path,f,slope,slope,False)`, slope = (vn−vp)/(2·bước)·fps) → hết giựt; key dày + hai đầu loop một phía = giựt. Đo gia tốc max < ~0,03.
- Khi chỉnh rotate mà "giữ nguyên translate": đọc đường cong tịnh tiến từng frame, tính xoay từ nó, ghi chỉ kênh xoay, xoá key tịnh tiến thừa do `set_key()` (nó key cả node), rồi so lại từng frame với bản cũ (sai số 0).
- Quan hệ chiều xoay↔tịnh tiến: kiểm bằng dấu vận tốc từng frame (`checks/anti.py`), chỉ ra đỉnh/đáy từng đường (`seg.py`); "tiếp tục rotate lên khi tay đi xuống ở F6-12" = dời đỉnh xoay sau đỉnh tịnh tiến (tăng độ trễ).
- Biên độ lớn bị tay trái duỗi thẳng (42,1 cm): hạ biên độ nòng, hoặc vai trái bù (`nova_shop_leftshoulder_assist.py`, làm mượt, đừng nhảy 8° trong 6F).
- Mỗi lần: nói rõ giả định về trục / chiều; chưa nhìn viewport thì nói thật; hỏi lưu bản mới (v1.3) chứ không lưu đè.
Nối: [[project-nova-idle-workflow]], [[feedback-stepped-blocking]].
