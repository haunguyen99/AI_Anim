---
name: studio-script-single-writer
description: "Script dựng pose qua cầu nối Studio phải là tiến trình ghi duy nhất, kiểm frame trước mỗi lần key (Auto key bật)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e7f5846c-b962-471d-8737-e620fc931e10
  modified: 2026-10-30T09:55:59.400Z
---

Studio bật Auto key: mọi lệnh sửa khớp ghi key ngay vào frame trang đang ở. Nếu frame đổi giữa chừng (người dùng bấm trang, lệnh
trễ quá 15 s rồi chạy muộn, hoặc 2 script cùng chạy) thì pose bị ghi vào frame sai, sinh key thừa (Ninja Attack b_v1 2026-10-30:
key thừa F2, 3, 6, 13, 14, 16, 20, 28; polish_v5 lần 1 hỏng F1 vì 2 tiến trình cùng ghi).

**Why:** user phải báo "timing đang bị loạn, xuất hiện các key bị thừa".

**How to apply:** chạy script bằng đúng một tiến trình nền (run_in_background, không dùng `&`), kiểm `wmic` không còn script
khác; script gọi `anim info` kiểm frame + version trước khi sửa và trước khi key, sai thì dừng; dặn user không bấm trang lúc chạy;
chạy xong đối chiếu danh sách key. Mẫu: work/infinite_defense/ninja_ninja_attack/polish_v3.py `at_frame`.

Chốt frame chưa đủ: polish_v14 (2026-10-30, trang Studio đang ẩn/tab nền) vẫn có F1 nhận góc của F15 và F16–F29 không được
ghi, script không báo. Luôn đọc lại MỌI frame và so với số tính ra sau khi ghi (ghi lại frame lệch, tối đa 3 lần).

Chụp tự kiểm (`snap`) xong phải trả viewport về `view 1 persp all az=30 el=15`: `view 1 top` / `el=88` để camera thẳng đỉnh
đầu, Studio nhớ camera theo workspace nên người dùng "không xoay được viewpoint" (2026-10-30).
