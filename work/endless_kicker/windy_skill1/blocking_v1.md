# Windy Skill 1 — blocking v1 (2026-11-10, theo yêu cầu mới của user)

Scene: `C:\Users\Admin\Documents\Ngoc\Hoctap\Anim\Windy_Skill1.fv` (user tự lưu). Layer mới `skill1_p10` (override, stepped); 3 layer cũ của Attack (Base, fix_r5, fix_r7) đang MUTE, chưa xoá.
Range 0–44 @ 30 fps.

## Yêu cầu user (thay bản 36F phóng F24)
- Lấy đà → đẩy ra trước: trượng có xoay nhưng **chậm và ít**.
- Tới pose đẩy ra trước mới xoay **nhanh, 2 vòng**.
- **Hold 10F**, rồi hồi về Idle. **Không còn pose phóng.**

## Key đã dựng (stepped)
| F | Pose |
|---|---|
| 0 | Idle F0 |
| 8 | Lấy đà: ngả sau ~9°, ngực xoay phải, trọng tâm chân trái, trượng chĩa lên-ra sau, tay trái giang trước |
| 12 | Giữa chuyển: trượng đã quét nửa đường (xoay chậm) |
| 16 | Đẩy ra trước: đổ người trước ~15°, hông hạ 4,5 cm, trọng tâm chân phải, trượng ngang chĩa +Z |
| 17–24 | Xoay 2 vòng trong mặt phẳng dọc bên phải, mỗi frame 90° (đầu trượng: lên → sau → xuống → trước). F20 = trước, F24 = trước |
| 34 | Hold (= F24) |
| 44 | = Idle F0 |

## Cách dựng
- Tay phải dùng IK (`ArmSwitch_R.fkIk = 1` từ F0, khớp Idle sai < 0,5 cm), trượng xoay bằng `Weapon_R` quanh tay (tay đứng yên).
- Tay trái vẫn FK (IK trái không khớp Idle, lệch 6 cm).
- Chân IK giữ nguyên, chỉ hạ hông.
- Thư viện giải: `skill1_lib.py` (chạy trong Frolvy, không numpy).

## Số đo
- Tay phải tầm với vai→tay cầm: F8 0,27 · F12 0,33 · F16–F34 0,44 m (hơi quá 0,42).
- Đuôi trượng cao nhất thấp: F17 0,13 m, F19 tip 0,24 m (không cắm đất).
- Trượng cách đầu ≥ 17 cm mọi key.

## Chưa làm / cần user xem
- Vải (áo choàng, vạt), thân phụ (vai lên khi tay giơ), key breakdown F9–F11, F13–F15, về F34→F44.
- Xoay 2 vòng 8F là 90°/frame: Euler `Weapon_R` sát gimbal (ry ±88°) — khi làm spline phải key từng frame, đừng nội suy.
- Hiểu "xoay chậm và ít" F8→F16 là trượng quét cung (đầu trượng từ lên-sau về trước); nếu ý user là trượng quay quanh tay thêm ~1/4 vòng thì sửa F12.
- Điểm sinh lốc cho dev: chưa chốt (đề xuất F24 = hết xoay).

## Cập nhật 2026-11-10 (sau khi user đưa ref `lux.mp4`, ảnh trích trong `ref/`)
Ref Lux (0,98 s @ 60 fps, cam chéo từ trên): f0–f4 trượng thấp rồi nhấc lên cao sau đầu → f10–f12 vung rộng sang bên phải nhân vật (trượng ngang, tay duỗi) → f14–f18 trượng hạ xuống trước người → f20–f44 trượng xoay ~2 vòng trong mặt phẳng trước ngực, tay trái giơ cao cạnh đầu cân bằng → f46–f58 hạ trượng chéo thấp bên người, về dáng đứng.
Đã áp vào scene:
- F12: trượng quét ngang sang phải (tay duỗi, đầu trượng ra ngoài vai phải), tay trái giang ra trái.
- F16–F34: trượng dựng trước ngực (xoay trong mặt phẳng trước mặt, như ref), tay trái giơ lên cạnh đầu.
- F8, F44 giữ nguyên.
Khác ref: ref cầm gần đuôi trượng, trượng 2,15 m của Windy cầm giữa nên tay phải phải ở cao ngực (≥ 1,2 m) để đuôi không cắm đất khi xoay.

## Pose lại theo ref Lux (2026-11-10, user: "trượng ở trên tay, xoay thì bàn tay ngửa, tay không xoay theo")
Key: F0 Idle · F8 lấy đà (trượng dựng trên tay, tay cạnh vai/mặt) · F12 giữa đường (trượng vẫn dựng, tay hạ về trước) · F16 bàn tay phải NGỬA (mở, curl 0), trượng dựng trên lòng tay · F17–F24 trượng xoay 2 vòng quanh điểm tay trong mặt phẳng trước ngực (chỉ Weapon_R.rz đổi: −122 → −842, tay đứng yên) · F34 hold (= F24) · F39 hạ trượng chéo thấp, nắm lại · F44 Idle.
Đo: đầu/đuôi trượng thấp nhất 0,08–0,19 m; trượng cách đầu ≥ 9,5 cm (F19), còn lại ≥ 14 cm; tầm với tay phải ≤ 0,40 m. Tay trái giữ duỗi ra bên (khuỷu gập nhẹ).
Bài học: đặt giá trị ở frame đã có key = sửa luôn key (làm hỏng F0 lần trước) → giải ở frame trống (F50). Camera kiểm: tạo camera tạm ở (−0,1; 1,2; 4,0) nhìn thẳng mặt, tz đổi bằng set_attr; xoay ry thì phải reset rx/rz về 0.

## Sửa pose xoay theo ảnh user gửi (Lux, 2026-11-10)
Ảnh user: tay phải duỗi ra TRƯỚC ngang vai, lòng bàn tay mở hướng ra trước, ngón hướng lên; trượng tựa chéo qua bàn tay (đầu trượng lên-trước, đuôi xuống sát hông), trượng xoay quanh bàn tay như kim đồng hồ trước lòng tay.
F16–F34 đã đổi: tay duỗi ra trước (tầm với cổ tay 0,46 m = tối đa), bàn tay phải hướng trước, trượng chéo ~25° từ phương đứng, F17–F24 xoay 2 vòng quanh trục Z (Weapon_R). Trượng cách đầu thấp nhất 5 cm ở F18 (đuôi trượng đi qua trên-sau đầu), ≥ 14 cm các frame còn lại.

## Đường tay F8 → F12 → F16 (user: "tay cầm trượng đưa thẳng ra sau, vòng tay thoáng ra rồi đưa thẳng về trước; trượng quay trước tay, không xoay sau đâm vào tay")
- F8: tay phải duỗi ra SAU (cổ tay sau mặt phẳng vai ~28 cm, khuỷu gập ~44°), trượng gần dựng, nghiêng sau nhẹ (đầu trượng sau vai, đuôi xuống cạnh chân phải, cách chân ≥ 30 cm).
- F12: tay vòng ra bên phải, duỗi sang ngang (cách vai 37 cm), trượng nghiêng TRƯỚC (đầu trượng ra trước tay, đuôi kéo sau lưng) — trượng dẫn trước tay, không đâm vào tay.
- F16: tay duỗi ra trước, trượng chéo lên-trước.
- Bản F8/F12 cũ lưu ở %TEMP%\s1_old_f8_f12.json.
