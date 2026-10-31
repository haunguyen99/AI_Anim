# QA & anatomy pass (mọi loại anim)

## pre-send-checklist
**Kiểm tra bắt buộc trước khi gửi** (gộp từ _common và checklist Attack):
- `joint_limits.py` = 0 vi phạm; close-up từng tay/chân ở 2 góc; độ căng da vai/khuỷu/cổ tay (`arm_strain`) không vượt P0 đã
  duyệt; khiên/giáp theo xoắn cánh tay trên, không xoay độc lập; khuỷu/gối không gập ngược, không duỗi quá thẳng; khuỷu ngoài thân.
- Prop xuyên thân = 0 ở mọi key có prop (`props_weapons.md#prop-penetration`).
- Dữ liệu: scale = 1, không quaternion 0, không f-curve rỗng; pose sau khi Blender tính lại = pose đã dựng; hàm dựng chạy lại
  (`from_p0`) ra đúng pose đã key.
- Tự đo nhịp/tốc độ/trượt chân/loop: `review_process.md#self-measure`.

## anatomy-check
- "check lại Anatomy toàn thân của từng key chính đã key" (Blender Attack blocking v4): sau mỗi đợt key chạy
  `work/blender/anatomy_check.py` trên mọi key (đo hình học so P0: độ dài đùi/ống chân/cẳng tay = khớp còn liền, gập gối/khuỷu,
  hướng gối so mũi chân, xoắn/gập thân-đầu-cổ tay so P0, căng da so cả bind lẫn P0, xuyên mesh, dưới đất) rồi nhìn cận chỗ bị
  đánh dấu; sửa bằng `anatomy_fix.py`. Nguyên lý: Solid Drawing.
- Bộ đo căng da so bind vô dụng ở rig Gaygor (P0 đã giãn 3x ở hông): so cạnh với min(bind, P0). Ngưỡng phụ thuộc mesh:
  `arms_hands.md#shoulder-compression`.
- Thêm vào anatomy pass: cột sống không zigzag, nghiêng tăng dần (`torso_head.md#spine-chain`); da vai ≥ 0,30.
- SDR (sdr_lib.anatomy): da váy giữa hai đùi giãn x4-6 ở lunge là bình thường với low-poly, xem close-up thay vì tin ngưỡng.
- Cascadeur: `cascadeur.md#quick-anatomy`.

## Skin khuỷu lệch trên rig team (SDR01, 2026-10-29)
- Mesh thấp đa giác, khuỷu gập ~110°: mặt trong thắt, mặt ngoài nhô góc. Đo trước khi đổ cho pose: `sdr01/elbow_check.py` (góc gập,
  xoắn cẳng tay, hồ sơ trọng số dọc tay). Lỗi gặp: đoạn cẳng tay 0–10 cm sau khuỷu còn 18–54 % Shoulder (vùng chuyển lệch về cẳng tay).
- Sửa: chia lại Shoulder+Elbow theo smoothstep ±6 cm quanh tâm khớp (`elbow_reskin.py`), ghi chỉ 4 cluster vào bản FBX trong job
  (`apply_skin_s3.py`, giữ byte phần còn lại). Chọn dải bằng mắt (ảnh cận 3 góc): đếm tam giác lật không phân biệt được các dải.
