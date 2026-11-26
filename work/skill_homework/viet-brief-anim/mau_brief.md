# Mẫu brief: Idle pháp sư cầm gậy (ví dụ giả định)
## 1. Bối cảnh, ràng buộc
Loop 60 frame, 24 fps. Camera game nhìn từ trên xuống, chếch 45°. Gậy cầm tay phải, đầu gậy phát sáng. [thiết kế]
## 2. Bảng pha
| Pha | Frame | Easing | Ý định |
|---|---|---|---|
| Thở vào | 0–24 | ease-in-out | ngực nở, vai nhích lên 1 cm, đầu ngẩng 3° |
| Giữ | 24–30 | giữ | gần như đứng yên, chỉ mắt và áo choàng còn động |
| Thở ra | 30–54 | ease-in-out | ngực xẹp, vai hạ, đầu về vị trí gốc |
| Nối loop | 54–60 | ease-out | khớp pose frame 0, không giật |
## 3. Từng bộ phận
- Hông/chân: trọng tâm dồn nhẹ sang chân trái ở frame 12, về giữa frame 48. Chân giữ nguyên chỗ.
- Thân/đầu: cột sống nghiêng tăng dần, mỗi đốt ≤ 10°; đầu trễ thân 3 frame.
- Prop (gậy): đầu gậy lắc ±2 cm theo nhịp thở, trễ tay 2 frame.
- Tay: tay phải siết gậy, cổ tay không xoay; tay trái buông, khuỷu gập ~45°.
## 4. Bộ phận phụ
Áo choàng: trễ thân 4 frame, biên độ lớn dần về gấu. Dây đeo: trễ 3 frame. Đầu gậy phát sáng: nhịp 30 frame.
## 5. Key plan
Key chính: 0, 24, 30, 54, 60 (60 = 0). Điểm kiểm: góc cột sống, không xuyên gậy vào thân, vòng loop.
