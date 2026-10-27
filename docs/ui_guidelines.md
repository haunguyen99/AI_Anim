# Quy tắc giao diện cho các tool (Home, Rig Lab, Pose Lab, Review Lab)

Mục tiêu: **đơn giản, ít thông tin, thân thiện**. Người dùng là animator, nhìn một lần phải biết bấm gì.

## Luật

1. **Nút là icon, không có chữ.** Tên nút nằm trong tooltip (`title`) và `aria-label`. Chữ chỉ dùng cho nhãn dữ liệu (tên anim, tên khớp), không dùng cho nút.
2. **Mỗi màn hình có một nút chính** (màu nhấn): Home là "Dự án mới", trang dự án là "Animation mới", dòng anim là "Tiếp tục". Các nút phụ viền nhạt, nút ít dùng không viền (ghost).
3. **Ẩn cái không dùng được**, không làm xám. Chưa có link Pose thì không hiện nút Pose.
4. **Ít thông tin trên màn hình.**
   - Số liệu chỉ là icon + con số (✓ 4 · ⏱ 2).
   - Ghi chú dài cắt một dòng, xem đủ khi di chuột.
   - Nhật ký git, thống kê tổng, mô tả phụ bỏ khỏi màn hình chính.
   - Chỉ hiện hướng dẫn khi có việc phải làm; khi đó là một nút icon (vd chép lệnh).
5. **Trạng thái là icon + màu**, không là chữ: đang làm ✎, chờ góp ý ⏱, đã xong ✓, tạm dừng ⏸.
6. **Giai đoạn là thanh chấm** (chấm xanh đã qua, chấm cam đang ở) kèm tên giai đoạn hiện tại.
7. **Hộp thoại chỉ hai nút icon:** ✕ hủy, ✓ xác nhận.
8. **Bàn phím:** nút thao tác thường dùng ghi phím tắt trong tooltip, vd "Bút vẽ (D)".
9. Chạm được: nút icon tối thiểu 30 px (nút chính 38 px), có viền focus rõ khi dùng Tab.
10. Giao diện sáng và tối theo `prefers-color-scheme`.

## Bộ icon

Nét 1,8 px, bo tròn, viewBox 24×24, màu theo chữ (`stroke: currentColor`). Mỗi icon là một chuỗi `<path>` trong bảng `ICONS` ở đầu script (bản mẫu trong `tools/home/index.html`):

`home` · `refresh` · `plus` · `edit` · `play` (tô đặc) · `copy` · `rig` · `pose` · `review` · `close` · `check` · `working` · `waiting` · `done` · `paused` · `list` · `back`

Thêm icon mới cùng kiểu nét. Trang Lab là một file HTML độc lập đăng lên claude.ai, nên mỗi trang nhúng bảng `ICONS` của riêng nó (không dùng file ngoài).

## Cách áp dụng cho một tool

1. Liệt kê từng nút hiện có, ghi chữ và việc nó làm.
2. Chọn icon từ bộ trên, thiếu thì vẽ thêm. Gom nút ít dùng vào menu (⋯).
3. Đổi nút thành icon, tên cũ chuyển sang `title`.
4. Gỡ thông tin nào người dùng không đọc ở màn hình chính.
5. Thử trên trình duyệt: không lỗi console, mọi nút có tooltip, bấm Tab thấy viền focus.

## Tiến độ

| Tool | Trạng thái |
|---|---|
| Home (`tools/home/`) | Xong 2026-10-26 |
| Review Lab (`work/review_page/`) | Xong 2026-10-27: nút Gửi, Gửi cho AI, thu phóng, Sửa / Xoá / Đã sửa trên ghi chú là icon; dòng phím tắt gom vào nút ?; nút Gửi cho AI khi xác nhận (armed) hiện lại câu hỏi bằng chữ |
| Pose Lab (`work/pose_lab/`) | Xong 2026-10-26: 54 nút tĩnh + nút góc ref thành icon, mục vật lý gập lại, ghi chú version chỉ hiện ở bản đang mở, phím tắt gom vào nút ? |
| Rig Lab (`work/rig_lab/`) | Xong 2026-10-26: bước, chế độ, camera, duyệt, xuất, skin đều là icon; chip trạng thái duyệt là icon; tên pose (Giơ tay, Gập khuỷu…) giữ chữ vì là tên lựa chọn |

## Cách làm icon trong Pose Lab (không đụng logic)

Pose Lab có 60+ nút mà code JS gán `textContent` cho nhiều nút ("Vật lý: bật", "Auto key: tắt", "Dừng"…). Nên nút giữ nguyên chữ nhưng **ẩn bằng CSS** (`font-size: 0`), icon vẽ bằng `::before` với `mask-image` (biến `--ic` theo id nút), nên mọi code cũ vẫn chạy.

- Bảng id → icon nằm trong khối CSS `/*ICONS*/` và `/*ICONS2*/` ở cuối `<style>` của `work/pose_lab/index.html`; nút thêm mới chỉ cần class `ibtn` và một dòng `#id { --ic: url(...) }`.
- Đoạn script cuối file đọc chữ ẩn thành tooltip + `aria-label` (nút có trạng thái thì tooltip = "Vật lý: bật - mô tả") và đặt `data-state` (`on` khi chữ có ": bật", "world", "Dừng", "Bậc thang") để đổi icon / màu.
- Mục vật lý (AutoPhysics, Lò xo, Tác động, Ragdoll, Va chạm, Cân bằng) gập lại; lựa chọn mở / đóng nhớ trong localStorage.

## Cách làm icon trong Rig Lab

Nút Rig Lab được dựng lại bằng `innerHTML` mỗi lần đổi bước, nên `work/rig_lab/patch_ibtn.py` thêm một script cuối `template.html`: bảng bộ chọn → icon, gắn `data-ic` + class `ibtn` (chữ ẩn bằng CSS, thành tooltip) và gắn lại sau mỗi lần DOM đổi (`MutationObserver`, dùng `setTimeout` chứ không `requestAnimationFrame` vì tab ẩn không chạy rAF). Nút mới: thêm một dòng vào bảng `R` và một icon vào `I` rồi chạy lại patch trên template sạch (patch có chốt chặn `/*IBTN*/`).

## Cách làm icon trong Review Lab

Giống Pose Lab: chữ ẩn bằng CSS, icon bằng mask, script cuối trang gắn `data-ic` theo id (`aiSend`, `send`, `zOut`, `zIn`) hoặc theo chữ của nút ghi chú `.mini` (Đã sửa, Mở lại, Sửa, Xoá, Lưu, Huỷ), nên nút dựng bằng JS cũng được đổi. Riêng nút "Gửi feedback cho AI" có bước xác nhận: lúc đang chờ xác nhận (`.arm`) nó hiện lại chữ "Đã xem hết clip? Gửi N ghi chú…" thay cho icon, vì đó là câu hỏi cần đọc.

Khi thử trang Review dựng sẵn bằng `http.server`, tiếng Việt bị lỗi font vì thiếu `<meta charset>` (claude.ai thêm khi đăng); để thử, nạp bằng `fetch` rồi `document.write('<meta charset="utf-8">' + html)`.
