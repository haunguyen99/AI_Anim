---
name: viet-brief-anim
description: Viết bản phân tích (brief) một clip anim game 3D trước khi dựng: chia pha, thời lượng, chuyển động từng bộ phận, key chính. Dùng khi soạn hoặc sửa brief Idle, Attack, Skill.
---
# Viết brief anim
## Khi nào dùng / không dùng
Dùng: clip mới, cần người duyệt trước khi dựng. Không dùng: sửa pose đã duyệt, rig, xuất file.
## Cần hỏi người dùng (nếu thiếu)
Nhân vật + prop; loop hay một lần; số frame hoặc giây; góc camera game; có video ref không.
## Các bước
1. Ghi bối cảnh và ràng buộc (loop, camera, prop, chỗ nhân vật đứng).
2. Bảng pha: tên | frame | easing | ý định diễn xuất.
3. Mô tả từng bộ phận theo thứ tự hông/chân, thân/đầu, prop, tay: góc xoay, frame, độ trễ.
4. Liệt kê bộ phận phụ (vải, tóc, đuôi, phụ kiện) kèm độ trễ so với thân.
5. Lập key plan (frame nào là key chính) và gắn nhãn nguồn: [ref] [concept] [thiết kế].
## Định dạng đầu ra + ví dụ
Markdown 5 mục theo bước 1–5. Ví dụ đầy đủ: mau_brief.md. Dòng pha tốt: `Anticipation | 0–8 | ease-in | hạ hông 6 cm, ngả đầu ra sau 10°`.
## Tự kiểm trước khi trả kết quả
Tổng frame các pha khớp độ dài clip; loop thì frame cuối = frame đầu; không bỏ bộ phận phụ; chưa dựng pose, chỉ gửi brief chờ duyệt.
