# 12 nguyên lý diễn hoạt - áp dụng thực tế (3D game, rig Blender)

Tài liệu sống: mỗi lần một nguyên lý được dùng/được người duyệt góp ý, thêm ví dụ thật (nhân vật, clip, frame, số đo).
Ký hiệu trạng thái: **[đã kiểm chứng]** có ví dụ được duyệt · **[đã thử]** có làm nhưng chưa chốt · **[chưa]** chưa áp dụng.

---

## A. Từng nguyên lý

### 1. Squash & Stretch (co giãn) - [chưa, gián tiếp]
- **Ý nghĩa:** khối có trọng lượng biến dạng khi chịu lực nhưng giữ thể tích.
- **3D game:** xương deform không được scale (Unity/rig game cấm scale khớp; file Idle từng bị Wrist_R scale 1.03/0.94 -
  là lỗi). Co giãn thể hiện qua **tư thế**: thân co lại (gù, hạ trọng tâm, gối gập) rồi giãn ra (ưỡn, vươn).
- **Đã làm:** nhịp thở Gaygor = gù-co ở đáy, ưỡn-giãn ở đỉnh (ngực -2..+3.5°, vai nhún 6-9 cm).
- **Cách làm:** pose co/giãn ở các key cực trị; nếu rig có xương cơ/bụng phụ mới cân nhắc scale nhẹ, phải hỏi trước.
- **Kiểm tra:** scale mọi xương = 1 (QA); khối "thở" có thấy co/giãn ở góc nghiêng không.

### 2. Anticipation (chuẩn bị) - [chưa]
- **Ý nghĩa:** động tác ngược hướng trước động tác chính để người xem đoán trước.
- **3D game:** quan trọng nhất ở Attack/Skill/Jump; ngắn để game phản hồi nhanh (thường 4-10F tùy độ nặng).
- **Gợi ý cho Gaygor Attack:** chùy kéo ra sau/lên, thân xoắn ngược, trọng tâm hạ trước cú đập.
- **Kiểm tra:** từ camera game có đọc được pha chuẩn bị trước impact không; tổng thời gian đến impact phù hợp gameplay.

### 3. Staging (dàn dựng) - [đã thử]
- **Ý nghĩa:** tư thế/silhouette truyền đạt rõ ý đồ.
- **3D game:** đọc từ camera game (góc trên/xiên), không chỉ front/side. Silhouette rõ ở frame quan trọng.
- **Đã làm:** P0 dựng từ chân lên, so 5 góc + top; brief GD "chỉ nhìn phía trước" -> khóa hướng đầu (staging cho người
  chơi). Bài học: silhouette mù với xoắn thân (Attack) - đọc bằng mắt.
- **Kiểm tra:** playblast có camera game; frame then chốt có silhouette đọc được không.

### 4. Straight Ahead & Pose to Pose - [đã kiểm chứng]
- **Ý nghĩa:** dựng theo các pose chính rồi điền giữa (pose to pose) hoặc làm liền mạch (straight ahead).
- **3D game:** pose to pose cho thân chính (blocking stepped CONSTANT -> spline); "straight ahead" kiểu mô phỏng cho chi
  tiết phụ (vải, tóc) - con lắc tính frame nối frame.
- **Đã làm:** P0 -> blocking stepped -> spline (Idle 133F); vạt khố mô phỏng con lắc (`cloth_flaps`).
- **Kiểm tra:** blocking được duyệt trước khi spline; chi tiết phụ không key tay từng frame.

### 5. Follow Through & Overlapping Action (theo đà & chồng lấn) - [đã kiểm chứng]
- **Ý nghĩa:** các phần không dừng cùng lúc; phần bị kéo trễ và tiếp đà sau khi phần dẫn dừng.
- **3D game:** chuỗi trễ dẫn -> bị kéo; đo bằng cực trị góc xoay.
- **Đã làm (Idle_Front v10-v14):** hông F28 -> Spine1 F28 -> ngực F31 -> vai F34 -> khuỷu/cổ tay F37; cổ F31 -> đầu F38;
  đầu nặng chùy trễ vai 5F (đỉnh) / 10F (đáy); vạt khố đung đưa rồi lắng.
- **Bẫy:** đổi lag thì chỉ đổi thời điểm, không đổi tư thế lấy mẫu; đạo cụ nặng bị cha kéo -> trễ key không đủ, phải
  điều khiển đường đi đầu nặng (`mace_delay`).
- **Kiểm tra:** bảng cực trị từng bộ phận tăng dần theo chuỗi.
- **Đã làm (Gaygor Walk b13, Pose Lab):** user chê "cứng nhắc". Trước hết quét tầm xoay + bước/frame từng xương: đầu, cổ, khố
  đứng im, khuỷu tay khiên bị khóa, và có giật 1 frame ở root (F21). Lớp overlap theo hông, tính trên trục thế giới:
  thân trễ 2F, đầu giảm còn 50% và trễ 2F, khố trễ 3F + bị đùi đẩy, khuỷu trễ vai 3–5F.
- **Bẫy (walk vác vật nặng):** đặt vai xoay ngược hông 35% với đích là hằng số thì mất 1,5–2 điểm IoU, vì ref để vai đi cùng
  hông. Đích phải là chính chuyển động cũ dời trễ (`sy(f-2)`) cộng một phần nhỏ xoay ngược (~20%). Không bao giờ đích = trung bình.
  Đo IoU từng lớp riêng trước khi gộp.
- **Chuyển overlap dựng tay sang lò xo Pose Lab (Gaygor Walk phys_v1, 2026-10-26, user: "áp dụng vật lý cho walk"):**
  - Không đưa key về pose tĩnh. Thử với vạt khố tĩnh: lò xo chỉ cho 7° (bản dựng tay 35°), vì cái đẩy chính là đùi; va chạm thân
    không bắt được vì vạt khố chạm đùi quá nông.
  - Cách làm: giữ chuyển động chính trong key nhưng dời sớm đúng bằng độ trễ của lò xo (vạt khố +2F với mức "Vừa"), để lò xo trả lại
    độ trễ và thêm vượt + lắng. Kết quả: cùng nhịp với bản tay, biên độ +13%.
  - Đo độ trễ bằng tương quan chéo trên trục xoay chính (`work/walk/phys_v1/make_keys.py` ghi số đo). Không dùng tổng góc lệch theo
    từng mức dời, vì sai do biên độ lấn át.
  - Đầu là lò xo giữ hướng trong thế giới, nên nhịp gần như không theo key. Chỉ dời 1F, biên độ ~3° như cũ.

### 6. Slow In & Slow Out (chậm vào, chậm ra) - [đã kiểm chứng]
- **Ý nghĩa:** chuyển động tăng tốc rồi giảm tốc ở hai đầu.
- **3D game:** easing sine mềm; tránh hai đầu phẳng quá lâu (smootherstep -> "đứng luôn", Idle v10 F20).
- **Đã làm:** đường cong nhịp thở sine; bỏ key giữa pha thở ra để khỏi "đập đáy" (đầu giật F22/F53).
- **Kiểm tra:** biểu đồ tốc độ từng bộ phận: không có đoạn ~0 kéo dài giữa pha, không có cú hãm 1-2 frame.

### 7. Arcs (đường cong) - [đã thử]
- **Ý nghĩa:** chuyển động tự nhiên đi theo cung, không theo đường thẳng.
- **3D game:** quỹ đạo của đầu, cổ tay, đầu vũ khí; IK dễ cho đường thẳng - kiểm tra quỹ đạo.
- **Đã làm:** chùy xoay quanh điểm tì vai (đầu nặng vẽ cung); vạt khố xoay quanh mép thắt lưng.
- **Còn thiếu:** công cụ vẽ quỹ đạo (motion trail) ra ảnh để soát arc - nên làm khi vào Attack/Walk.
- **Kiểm tra:** quỹ đạo đầu/cổ tay/đầu vũ khí ở góc front và top không gãy góc.

### 8. Secondary Action (hành động phụ) - [đã kiểm chứng]
- **Ý nghĩa:** hành động phụ làm giàu hành động chính mà không lấn át.
- **3D game:** nhịp thở trong lúc đứng; vải, tóc, phụ kiện; ngón tay; mắt (nếu có).
- **Đã làm:** vạt khố bay trong gió (26°, gió theo đợt), khuỷu tay gập theo nhịp thở (IK).
- **Kiểm tra rig sớm** (`rig_inventory.py`) để không bỏ sót xương phụ (DressFront_M/DressBack_M bị bỏ quên tới v12).

### 9. Timing (thời lượng) - [đã kiểm chứng]
- **Ý nghĩa:** số frame quyết định trọng lượng và cảm xúc.
- **3D game:** độ dài clip theo gameplay (idle 2 s = 60F @30fps); nhịp phải hợp tính cách (boss nặng thở chậm).
- **Đã làm:** 2 nhịp/60F bị chê "gấp" -> 1 nhịp/60F; thở ra 33F > hít vào 26F.
- **Kiểm tra:** bảng hít vào/thở ra (F) từng bộ phận; tỉ lệ tốc độ hai pha.

### 10. Exaggeration (cường điệu) - [đã thử]
- **Ý nghĩa:** đẩy chuyển động vượt thực tế để đọc rõ, giữ tính tin được.
- **3D game:** camera xa + model nhỏ -> cần biên độ lớn hơn ref (vải 10° -> 26° theo yêu cầu "bay trong gió").
- **Giới hạn:** vượt giới hạn khớp / làm hỏng giải phẫu là sai (Attack f13 "xoắn vặn hỏng anatomy"); quá tay cũng hỏng
  (ngực -4..+6° làm đầu gật 18°).
- **Kiểm tra:** joint limits = 0 vi phạm; nhìn ở camera game xem có đọc được không.

### 11. Solid Drawing -> Solid Posing (khối & tư thế vững) - [đã kiểm chứng]
- **Ý nghĩa:** khối, trọng lượng, cân bằng, giải phẫu đúng.
- **3D game:** trọng tâm trên chân trụ, chân cắm đất (trượt = 0), giải phẫu khớp đúng (khuỷu bản lề, xoắn chia vai/cổ tay),
  không twin (hai bên đối xứng y hệt).
- **Đã làm:** P0 từ chân lên; giới hạn khớp theo rig; khuỷu luôn gập >40°; khiên theo xoắn cánh tay trên.
- **Vi phạm đã bị nhắc 2 lần:** bẻ/xoắn khớp quá đà phá giải phẫu (Idle 133F khuỷu trái xoắn 169°; Attack f13 hai tay) -
  quy tắc ở `arms_hands.md#no-overbend`, checklist ở `qa_anatomy.md#pre-send-checklist`.
- **Kiểm tra:** QA trượt chân, giới hạn khớp, độ căng da (`arm_strain`), close-up từng tay.
- **Ví dụ chân (Gaygor Walk b13 → b14, 2026-10-26):** "gối xoay vặn" khi nhấc chân. Gối xoay ra và bàn chân xoắn ngược chiều
  quanh ống chân cùng lúc. Cẳng chân là một khối liền: bàn chân phải đi theo mặt phẳng gối (`legs_feet.md#knee-dir`).

### 12. Appeal (sức hút) - [đã thử]
- **Ý nghĩa:** nhân vật hấp dẫn, có cá tính.
- **3D game:** tính cách qua tư thế và nhịp: Gaygor = boss vũ phu, tự tin -> đứng chắc, vai nhún nặng, nhìn thẳng người chơi,
  chùy nặng trễ; tránh đều như máy (mỗi bộ phận/chi tiết một nhịp riêng).
- **Kiểm tra:** câu hỏi cuối mỗi vòng: "nhân vật có đang *sống* và *đúng tính cách* không" - đây là phần cần mắt người duyệt.

---

## B. Quy trình diễn hoạt thực tế ↔ nguyên lý

| Bước (pipeline v2) | Nguyên lý chính | Việc cụ thể |
|---|---|---|
| 2 Phân tích ref | Timing, Staging, Appeal | Tổng quan hành động + tính cách; từng bộ phận: vai trò dẫn/bị kéo, timing, độ trễ, chi tiết phụ |
| 3 Rig + camera | Solid posing | Giới hạn khớp, trục khớp, IK/FK, kiểm kê xương phụ |
| 4 P0 + Blocking | Pose to pose, Staging, Solid posing, Anticipation | Pose chính stepped, từ chân lên, đọc ở mọi góc + camera game |
| 5 Spline + Polish | Slow in/out, Arcs, Follow through/Overlap, Secondary, Exaggeration | Đường cong chung, chuỗi trễ, quỹ đạo, chi tiết phụ |
| 6 QA + Review | Tất cả, đặc biệt Appeal | Đo số liệu + trang review; mỗi feedback -> nguyên lý nào bị vi phạm |
| 7 Xuất | - | Bake, FBX, kiểm tra đọc lại |

**Khi nhận feedback:** gọi tên nguyên lý bị vi phạm trước (vd. "hông khựng" = Slow in/out; "cột sống cứng" = Overlap +
Squash/stretch tư thế; "vải ít động" = Secondary + Exaggeration), rồi mới sửa - và ghi vào mục A.

---

## C. Áp dụng theo đối tượng trên nhân vật

| Đối tượng | Nguyên lý trọng tâm | Cách làm đã dùng | Ví dụ (Gaygor) |
|---|---|---|---|
| Hông / trọng tâm | Timing, Slow in/out, Solid posing | Dẫn nhịp; sine; chân IK cắm đất | Hông nhấc 2.8 cm, đỉnh F28 |
| Cột sống / ngực | Overlap, Squash/stretch (tư thế) | Uốn hai chiều, trễ dần lên | Ngực -2..+3.5°, trễ +4F |
| Cổ / đầu | Overlap, Staging | Khóa hướng nhìn, bù sớm để đầu trễ sau cổ | Đầu trễ cổ ~6F, gật 3.6° |
| Vai / bả vai | Timing, Exaggeration | Nhún theo nhịp thở | Vai 6-9 cm |
| Tay tự do | Follow through, Solid posing | IK, tay nhấc hơn vai, khuỷu luôn gập | Khuỷu 41-54°, trễ vai 5F |
| Tay cầm đạo cụ | Solid posing | Giải bài toán cầm, không ép hướng tay | `solve_grip` (Attack) |
| Đạo cụ nặng (chùy) | Follow through, Arcs | Đòn bẩy tì vai, đầu nặng trễ | Đỉnh trễ vai 5F, biên độ 7.7 cm |
| Giáp/khiên cứng | Solid posing | Theo xoắn cánh tay trên, không biến dạng | Khiên tay phải |
| Vải / vạt / áo choàng | Secondary, Follow through, Exaggeration | Con lắc giảm chấn + gió, trục ở điểm đính | Vạt khố 26°/25°, chu kỳ 20/24F |
| Tóc / đuôi / dây | Secondary, Overlap | (chưa làm) chuỗi con lắc, mỗi đốt trễ thêm | - |
| Ngón tay | Secondary | Theo cổ tay +1F | Ngón tay phải |
| Mắt / mặt | Appeal, Anticipation | (chưa có rig mặt) | - |
