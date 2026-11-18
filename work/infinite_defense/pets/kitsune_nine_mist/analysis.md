# Pet 23 Kitsune Nine-Mist - phân tích Idle + Attack (chờ duyệt, chưa dựng)

Nguồn: GDD dòng 23 + rig hiện tại (73 joint) + khuôn clip Pet cũ (Idle 0-48 lặp, Attack 0-30, 30 fps). Luật Pet: bay lơ lửng ~12 cm, chân/tai/đuôi thả và trễ theo thân.

## Việc của anim, việc của VFX/shader
- Anim: thân, đầu, tai, chân, 9 đuôi, mốc frame bắn.
- Không phải anim (không có joint): mắt lóe đỏ (emission/shader), tàn ảnh hoa bỉ ngạn, mưa móng vuốt. Anim chỉ chừa mốc frame để gắn.

## Idle (lặp, 48F = 1,6 s, F48 = F0)
Cảm giác: cáo quý phái trôi trong khói, thân lên xuống rất chậm, 9 đuôi uốn như sóng.
- Thân: hover nền 12 cm (CTL_Main nâng cố định). Hông nhấp nhô ±1,5 cm, 1 nhịp/vòng; nghiêng ngang ±3° (đối pha nhịp lên xuống).
- Đầu: ngược nhịp thân, trễ 3F, ±2° gật; quay nhìn ±5° một lần/vòng. Tai: trễ 4-5F so với đầu, ±5°, tai phải lệch 6F so với tai trái.
- Chân: thả, trễ thân 4-6F; đùi ±6°, cẳng chân trễ thêm 3F, bàn chân trễ thêm 3F (đong đưa, không đạp đất).
- 9 đuôi (nhân vật chính của clip): sóng chạy từ gốc ra ngọn, mỗi đốt trễ 4F, biên độ tăng dần gốc→ngọn 3°→5°→7°→9°→11°; mỗi đuôi lệch pha ~3F so với đuôi kề (cả quạt gợn từ trong ra ngoài). Mỗi đuôi đi vòng nhỏ (lên-xuống lệch 90° với trước-sau) để đuôi cuộn chứ không đung đưa phẳng. Đuôi giữa chậm nhất, đuôi ngoài cùng nhanh/rộng nhất. CTL_TailFan thở nhẹ -0,1…+0,15, trễ 6F.
- Lặp: mọi chu kỳ là ước của 48 (1 hoặc 2 vòng), chạy `loop_seam.smooth` sau mỗi vòng sửa. Key thưa: bước 6F cho thân, 3F cho đuôi/tai.

## Attack (31 key, 0-30, ~1,0 s)
Đọc từ xa: nén lại → bung quạt → rung dư → về idle.
| Frame | Pha | Thân/đầu/tai | Đuôi/chân |
|---|---|---|---|
| 0 | Idle F0 | đúng tư thế idle | - |
| 0-8 | Gồng (8F) | hạ hover 12→8 cm, ngả sau ~6° (Spine1 ≤10°), đầu cúi 8°, tai cụp ra sau | quạt khép (fan -0,8), ngọn đuôi cuộn vào trong, đuôi hạ thấp về sau; chân co lên |
| 8-12 | Bung (4F, nhanh) | thân bật lên/tiến 6 cm, đầu ngẩng, tai bật ra trước | đuôi bật theo sóng: gốc trước, ngọn trễ 1F; fan vượt +1,2 |
| **12** | **BẮN (gắn event)** | pose mạnh nhất, đầu ngẩng 10°, hơi hé thế thủ | fan +1,0, 9 đầu đuôi hướng ra ngoài/lên; giữ 2F (12-14) |
| 14-22 | Dư chấn | thân lún nhẹ 3 cm rồi nổi lại, tai và chân vẫy tắt dần | đuôi rung tắt dần, ngọn trễ gốc 1F mỗi đốt; fan +1,0 → +0,3 |
| 22-30 | Về idle | hover về 12 cm, đầu/tai về trung tính | fan → 0; F30 = đúng Idle F0 |
- Mắt đỏ lóe: VFX, đề xuất bật từ F8 đến F14 (event "eye_on" F8, "eye_off" F16).
- Chỗ nối Attack→Idle: Idle F0 đang chuyển động còn Attack dừng ở F30; sẽ khớp tư thế, nối chuyển động bằng ease 3F cuối.

## Cần bạn quyết / rig cần thêm
1. **Camera game** (từ trên xuống hay 3/4)? Quạt hiện xòe trong mặt phẳng đứng (nhìn trước thấy rõ, nhìn từ trên xuống ít đổi). Đề xuất: thêm vào driven key của `fan` một chút xoay ngang (ra sau/hai bên 10-15°) để từ trên nhìn cũng thấy bung. Em làm khi bạn duyệt.
2. **Socket bắn:** Unity đọc 1 socket `DEF_Muzzle_M` hay 9 đầu đuôi? (đang chờ từ lần trước.)
3. Mắt lóe và tàn ảnh hoa: xác nhận là VFX/shader, không cần joint mắt.
4. Độ dài: Idle 48F, Attack 31F ở 30 fps như các Pet trước, được không?
5. Rig vừa sửa kích cỡ control đuôi và skin; trước khi anim bạn có muốn check thêm rig không?

Quy trình tiếp theo (sau khi duyệt): blocking thân/hông/đầu → đuôi/tai/chân → spline → check xoắn + loop_seam → playblast, chưa xuất FBX đến khi bạn nói "chốt".
