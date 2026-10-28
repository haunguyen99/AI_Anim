# Infinite Defense — Hero Ninja: danh sách anim từ FDD (giai đoạn 0, G1–G2)

Nguồn: FDD Hero Ninja v1.1 (17/10/2026), `ninja_fdd_v1.1.txt` (bản tải về 2026-10-28,
https://docs.google.com/document/d/1fQYJ82Xi7PhQJM-eow2MMzxvO0gzE9hgI1eNGJNNa2k).
Nhãn nguồn: [GDD] trích FDD, [rig] đo trên rig, [user] lời người dùng, [suy luận], [?] cần hỏi.

## Rig (2026-10-28)
- [rig] `MC_Ninja.fbx`: `body_ninja` (989 đỉnh, chibi cao 185 cm, đầu ~45 cm), `weapon` (kunai dài 75 cm, gốc = điểm cầm),
  `weapon_explode` (kunai bùa nổ, KHÔNG rig: [user] "rig model ninja và weapon thôi").
- [rig] 48 xương: thân, tay găng (ngón cái + khối 4 ngón, mỗi ngón 2 đốt + đầu), 2 chuỗi khăn `Scarf1–4 + ScarfEnd` (đuôi khăn
  nằm ngang kéo ra sau tới z −150), kunai bind cứng vào `Weapon` (con của `Wrist_L`).
- [user] **kunai ở tay TRÁI** — FDD ghi tay phải (xem câu hỏi Q1).

## Danh sách anim
| # | Anim | [GDD] mô tả | Loại | Ghi chú |
|---|---|---|---|---|
| 1 | Idle | "đứng thủ thế hơi khom người, tay phải cầm ngược kunai trước ngực, tay trái thả lỏng. Khăn quàng bay nhẹ theo nhịp thở. Khoảng mỗi 4–6 giây xoay kunai một vòng trong tay (optional). Animation loop liền mạch." Ref: tay duỗi trong ref là tay không, hơi khom người. | loop | **đang làm** (`ninja_idle`) |
| 2 | Attack (đánh thường) | "vung tay trái từ sau ra trước ném shuriken, tay phải giữ kunai thủ thế trước ngực." Shuriken bay thẳng, không homing. Phân thân dùng chung. | một lần | điểm thả shuriken = sự kiện game |
| 3 | Skill 1 Explosive Kunai | "vung tay cầm kunai (trong tư thế idle) về phía trước hướng mục tiêu" | một lần | kunai bùa nổ bay homing; `weapon_explode` có thể là bản bay (Q4) |
| 4 | Skill 2 Shadow Clone | "kết ấn hai tay trước ngực rồi trở về tư thế chiến đấu" | một lần | kunai vẫn trong tay khi kết ấn (Q5) |
| 5 | Skill 3 Vanish | "từ tư thế idle hạ thấp trọng tâm cơ thể rồi tan biến" | một lần | model ẩn suốt skill |
| 6 | Skill 3 Reappear | "hiện ra trong tư thế đáp đất và như lúc vanish, sau đó về idle" | một lần | |
| — | Hit / Die / Run | không có trong FDD | | [?] Q6 |

## Câu hỏi cấp dự án (G2)
- **Q1 Tay cầm kunai** — FDD: tay phải cầm kunai, tay trái ném shuriken. [user] kunai tay trái. → đổi toàn bộ: kunai tay trái,
  ném shuriken bằng tay phải? (Đề xuất: đúng vậy, đổi gương mọi mô tả FDD.)
- **Q2 Camera game** — FDD không nói. Tower defense thường nhìn chéo từ trên (3/4 top-down). Cần góc thật để thiết kế silhouette.
- **Q3 Xoay kunai "mỗi 4–6 giây" vs loop** — một loop 4–6 s (120–180F) có một lần xoay, hay Idle thở ngắn (60F) + clip
  `Idle_Spin` riêng để code chèn ngẫu nhiên? (Đề xuất: tách 2 clip, dễ ghép và không lặp cứng nhịp.)
- **Q4 `weapon_explode`** — kunai bùa nổ của Skill 1: anim cầm kunai thường rồi game đổi sang bản bùa nổ khi ném, hay cần hiện
  `weapon_explode` trong tay lúc vung?
- **Q5 Kết ấn (Skill 2) khi tay đang cầm kunai** — giữ kunai trong tay (kẹp giữa các ngón) hay giấu kunai?
- **Q6** Có cần Hit / Die / Run / Victory không (FDD chưa liệt kê)?
- **Mâu thuẫn nhỏ:** FDD Idle "tay trái thả lỏng" nhưng phần Signature "tay trái để trống để ném shuriken" và ref "tay duỗi kiếm là
  tay không" → tay không vừa thả lỏng vừa vươn ra trước? (Đề xuất cho Idle: tay không hơi đưa ra trước, khuỷu chùng, như ref.)
