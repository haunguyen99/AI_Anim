# Flamethrower (súng phun lửa) — Plan, bản HTML v1 (2026-11-18)
Order: `work/vfx_orders/20261118_phongdq_phunlua/order.md` (Phong). Anatomy: `Docs/VFX/_Anatomy/flamethrower.md`.

## Định hướng không gian (đề xuất đã gửi Phong, Phong trả lời "oke")
- Ngữ cảnh: **dir** (phun ngang trên mặt phẳng người đứng, đứng trên đất = ground cho người / bia). Súng cầm tay của nhân vật 1,8 m, đầu nòng cao 1,1 m.
- Camera 3/4 nhìn xuống 40° (canvas 2D: mét đứng × cos 40°, chiều sâu đất × sin 40°). Quy mô: tầm phun ~5 m, nón nở tới ~1,2 m ở cuối; bia cách nòng ~3,9 m.
- Kiểu bắn: liên tục khi giữ (chuột / Space), hoặc tự động (bắn 2,9 s, nghỉ 2,3 s) để xem không cần thao tác. Màu: cam đỏ viền vàng (mặc định), thêm xanh hextech, tím.
- Nền: dusk xanh tím, sàn đá tròn, trụ đá xa.

## Bất biến (chép từ Anatomy)
dòng liên tục nòng → ~5 m; nhìn ra lưỡi lửa cel nhiều lớp; hẹp ở nòng → nở, nóng → nguội, đầu cong lên + tan; có lửa đầu nòng, thả nút thì ngắt; một ngữ cảnh; stylized bậc màu cứng.

## Dựng
- `Docs/VFX/Flamethrower/index.html`, 1 file tự chứa, không thư viện, không texture / ảnh ngoài. Mô phỏng bước cố định 1/120 s, seed cố định (cùng `t` → cùng khung).
- Dòng lửa: 180 hạt/s, tốc độ 7,4–9,8 m/s, drag 1,25, buoyancy 2,3 m/s² + lắc sin, sống 0,62–1,0 s, bán kính 0,08 → 0,40–0,62 m rồi co về 0 (u > 0,68). Hạt vẽ **lưỡi lửa Bezier mũi nhọn quay theo vận tốc**, 4 lớp (1 / 0,72 / 0,48 / 0,25), lớp trong lệch lùi + lên tạo mép sáng, **5 bậc màu cứng** (không gradient), vẽ già trước, mới (sáng) sau.
- Hạt phụ: tia lửa kim cương 34/s (gravity, nảy nhẹ trên đất), khói 2 lớp tròn từ ~10% hạt lửa chết, sao nhọn lửa đầu nòng (7 cánh, nhấp nháy 20 Hz) + quầng, lửa mồi nhỏ khi nghỉ, ánh sáng hắt xuống sàn + rim lên người, bia rơm (đếm hạt trúng → nhiệt → lửa bốc + cháy xém).
- **Texture Library: không dùng** (không texture; mọi hình vẽ bằng code web, giống Disintegrate). Lửa là hình hữu cơ: thay vì tin preset ảnh, hình dựng bằng Bezier cel; hai phương án khác (flipbook Library `Flipbooks/Fire`, VFX Graph) để dành cho bản Unity nếu Phong cần. Không có builder Unity nên `check_texture_plan.py` không áp dụng.
- Âm thanh WebAudio tự tổng hợp (không file ngoài, không giấy phép): noise hồng qua bandpass 720 Hz (LFO 9 Hz) + lowpass cho tiếng phụt; rền thấp lowpass 240 Hz; xì khí highpass; "fwoomp" lúc bắt (noise lowpass quét 2200 → 220 Hz + sine 120 → 42 Hz); "psss" lúc tắt; lách tách ngẫu nhiên khi bắn; compressor trước loa. Bấm 1 lần để bật tiếng.
- Điều khiển: màu, giữ để bắn (nút / chuột trên cảnh / Space), tự động, bia, âm thanh + âm lượng, tốc độ. Tham số URL: `?t=<giây>&color=&seed=&ui=0&dummy=0&auto=0` vẽ đúng 1 khung (kiểm / xuất ảnh).

## Chưa làm / điểm yếu đã biết
- Review vfx-director vòng 1: không lỗi hình / luật; đã sửa `?t=Infinity` treo, Space kẹt khi mất focus, lệch số tài liệu, hạ gain "fwoomp". Còn **KHÔNG CHẮC**: clipping chưa đo, âm thanh chưa nghe bằng tai, luật "hình hữu cơ: đưa 2–3 phương án ảnh trước" (Phong đã "oke" đề xuất mặc định, chưa có ảnh phương án) → art lead quyết.
- Chưa có prefab Unity (brief chỉ yêu cầu HTML).
- Nhân vật + súng là hình vẽ phẳng giả lập, súng nhỏ nên khó đọc chi tiết; chưa nghe thử âm thanh bằng tai (chỉ kiểm tạo node không lỗi).
- Chưa có ảnh ref của Phong ("style LOL" hiểu là cel, bậc màu cứng, bão hòa, mép sáng).
