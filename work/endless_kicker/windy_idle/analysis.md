# Windy Idle — phân tích (G1–G3, nhánh C: không có ref video)

Nguồn: FDD "Hero: Windy" (Vũ Việt Tiến, 14/10/2026, bản Prototype) + rig Frolvy `Windy_rig.fv` (2026-11-05).
Nhãn: [GDD] trích FDD · [rig] đo trên rig · [suy luận] · [?] cần hỏi.

## A. FDD nói gì về Idle

FDD **không có mục Idle** và không có link ref Idle. Có 4 anim: Attack, Skill 1, Skill 2, Skill 3. Idle phải suy ra từ:

| # | Câu gốc | Hệ quả cho Idle |
|---|---|---|
| 1 | [GDD] "Mage là Hero duy nhất tồn tại trong toàn bộ màn chơi, đứng cố định tại tâm khu vực phòng thủ và tự động tấn công enemy đi vào phạm vi." | Idle đứng tại chỗ, không root motion. Đây là anim chạy nhiều nhất (mọi lúc không đánh), nên phải nhìn lâu không chán và không mỏi mắt. Nhân vật ở tâm màn, mọi hướng đều có thể có địch → [suy luận] tư thế mở, nhìn thẳng, không quay hẳn sang một bên. |
| 2 | [GDD] Attack: "Windy đưa đầu trượng về phía trước" | Idle phải giữ trượng ở tư thế **sẵn sàng**: tay phải cầm, đầu trượng ở trên, để chuyển sang Attack ngắn (đưa đầu trượng ra trước). |
| 3 | [GDD] Skill 1: "Windy đưa cả trượng về phía trước -> trượng xoay tròn" | Idle → Skill 1 cũng bắt đầu từ trượng trong tay phải. |
| 4 | [GDD] Skill 2: "Windy bay nhẹ lên cầm trượng quay một vòng" | Chữ "bay **lên**" cho thấy bình thường Windy **đứng trên đất** → Idle chân chạm đất, không lơ lửng. |
| 5 | [GDD] Skill 3 Burst: "hai tay đang dang ra nắm vào vũ khí ở phía trước rồi hạ xuống đất **chuyển về idle**" | Câu duy nhất nhắc Idle: Idle là tư thế đáp đất sau Skill 3, hai chân trên đất, trượng đã về tay. |
| 6 | [GDD] Chủ đề: hero gió (Wind Cyclone, Hunting Tornado, Wind Collapse) | [suy luận] Chuyển động phụ nên mang chất gió: áo choàng và hai vạt sau bay nhẹ theo gió. Thân chỉ thở, giữ yên. |

## B. Rig đo được [rig]

| Mục | Số đo | Ghi chú cho Idle |
|---|---|---|
| Cao | 1,85 m; đầu 1,32–1,85 m (0,53 m, rộng 0,50 m) | Chibi khoảng 3,5 đầu. Đầu to nên cúi/gật chỉ cần vài độ là đã thấy rõ (≤ 3–4°). |
| Chân | Hông 0,66 m, gối 0,37, cổ chân 0,10 | Chân ngắn: tấn rộng sẽ trông như ngồi xổm (bài học Ninja) → đứng thẳng, hai chân rộng bằng hông. |
| Tay | Vai y 1,17; cánh tay trên 0,23 m, cẳng tay 0,225 m; bàn tay găng (chỉ ngón giữa + ngón cái) | Không có ngón trỏ: "nắm trượng" = khép găng (handPose/curl), không tạo dáng từng ngón. |
| Trượng | Dài 2,15 m (dài hơn người), cầm ở điểm cách đuôi 1,13 m, cách đầu 1,02 m; chỉ tay phải (`DEF_Weapon_R`) | **Nếu dựng đuôi chạm đất, tay cầm sẽ ở cao 1,13 m, gần ngang vai (1,17).** Tay phải phải nâng ngang vai, khuỷu gập. Đây là ràng buộc lớn nhất của dáng Idle (xem C). |
| Áo choàng | Một chuỗi 4 đốt ở giữa lưng (Cape1–4), mép giữa ở 0,46 m, hai mỏm kim cương tới 0,12 m theo Cape4 | Lắc theo gió kiểu đuôi: gốc ít, ngọn nhiều, trễ dần. |
| Hai vạt dài sau lưng | Mỗi vạt 4 đốt (BackFlap1–4), dựng mẫu chìa thẳng ra sau tới z −1,4 m | [suy luận] Mẫu dựng sẵn ở dáng bay ngang ra sau, nên ý đồ là **vạt bay trong gió**, không rủ xuống. [?] cần GD xác nhận. |
| Rig đang tham chiếu trong cảnh anim | `Windy_rig:` **không có chuỗi Cape** | Cần tham chiếu lại bản `Windy_rig.fv` mới nhất (có Cape + skin + picker) trước khi key. |

## C. Thiết kế đề xuất

**Loại:** idle thở + chuyển động phụ theo gió (công thức `knowledge/details/idle.md#breath-recipe`). Không có diễn xuất liếc/đổi trọng tâm vì FDD không yêu cầu.

**Độ dài (chốt, người dùng 2026-11-05): 40 F @ 30 fps (1,33 s)**, một nhịp thở, F1 = đáy hơi thở (chỗ nối loop). Hít vào ~17 F, thở ra ~23 F (thở ra dài hơn, ~43/57). Gió cho vải: áo choàng chu kỳ 40 F, hai vạt chu kỳ 20 F (chia hết 40 để loop khít, và khác nhịp thở để không lặp cùng lúc).

**Tư thế gốc (k1_idle), 3 phương án cho tay cầm trượng:**

| PA | Mô tả | Số đo | Ưu | Nhược |
|---|---|---|---|---|
| **A (đề xuất)** | Trượng dựng chéo nhẹ ra ngoài bên phải, nghiêng ~18° (đầu trượng chụm về phía người), đuôi chạm đất cách tâm người ~0,7 m | Tay cầm ở x −0,35 m (ngoài vai 15 cm), cao ~1,07 m (1,13 × cos 18°), hơi ra trước 10 cm; vai → tay cầm chỉ ~0,21 m nên khuỷu gập sâu ~100°, khuỷu chĩa xuống-ra ngoài | Đứng chắc, đúng dáng pháp sư; Attack chỉ cần nhấc đuôi lên và đưa đầu trượng ra trước | Tay phải hơi cao vì trượng dài |
| B | Trượng dựng thẳng đứng sát người bên phải | Tay ở 1,13 m, ngang vai | Gọn, nhìn từ trên xuống ít che | Tay nâng ngang vai trông gồng, khó thở thả lỏng |
| C | Cầm trượng chéo trước người, không chạm đất (đầu trượng chếch lên trái) | Tay ngang bụng ~0,95 m | Sẵn sàng nhất cho Attack/Skill 1 | Trượng 2,15 m chéo trước người che thân; tay phải giữ cả cây nặng → phải có trễ đầu trượng |

Các bộ phận khác (cả 3 phương án):
- **Chân:** đứng thẳng, rộng bằng hông, gối gập nhẹ ≤ 10°, khoá đất (trượt 0).
- **Thân:** thẳng, ngực hơi ưỡn. Thở: hông nhún 1–1,5 cm, uốn Spine1 −1..+2°, Chest −2..+3°; trễ dọc cột sống 1/3/4F (rút từ 2/4/6F của loop 60F; bài học Ninja: "body thở hơi cứng" nếu không trễ).
- **Đầu:** nhìn thẳng, yaw khoá, gật ≤ 3° trễ cổ ~4 F.
- **Tay trái (tay tự do):** thả lỏng cạnh hông, khuỷu gập > 40° (luật không duỗi thẳng), găng khép hờ; nhấc 2–3 cm khi hít, trễ vai ~4 F.
- **Tay phải + trượng:** bàn tay khoá trên trượng; PA A/B thì đuôi trượng khoá đất, tay chỉ nhún theo vai ≤ 1 cm.
- **Áo choàng (Cape1–4):** lắc ra sau theo gió, gốc ±2°, ngọn ±10°, trễ 3 F mỗi đốt, chu kỳ 40 F.
- **Hai vạt (BackFlap1–4):** nếu bay ngang (theo mẫu): gợn sóng lên xuống ±6–8°, trễ 2 F mỗi đốt, chu kỳ 20 F, hai vạt lệch pha 5 F.

**Bảng pha (một pha một key, theo `gdd_stage0.md`):**

| F | Pha | Mô tả | Key pose |
|---|---|---|---|
| 1 | Đáy thở | Tư thế gốc k1, vai thấp nhất | `k1_idle` |
| 1→18 | Hít vào | Vai/ngực lên, tay trái nhấc nhẹ | — (chuyển tiếp) |
| 18 | Đỉnh hít | Vai cao nhất, ngực ưỡn nhất | — (nhích nhỏ, AI dựng ở blocking) |
| 18→40 | Thở ra (dài hơn) | Về đáy, F41 = F1 | `k1_idle` |
| suốt | Gió | Áo choàng chu kỳ 40 F, vạt 20 F | — |

Chỉ có **một key pose** (k1_idle); các pha còn lại là chuyển động nhỏ.

### k1_idle v2 (theo concept + 3 ref người dùng gửi, 2026-11-05)
v1 (trượng chéo 8°, tay ngang vai, tay trái buông) bị chê "xấu quá". v2 dựng ở F0 trên `Windy_rig:`:
- Trụ chân trái (contrapposto): hông dời trái 4 cm, hông phải hạ 1,6 cm (Root rz 4°, ry −6°); chân trái thẳng (gối 2°), chân phải
  chùng gối 26°, bàn chân ra trước 9 cm, nhón gót 1,2 cm, mũi chân xoay ngoài 14°. Ngực nghiêng ngược (IKChest rz −8°) → vai phải
  cao hơn vai trái 2,8 cm. Đầu ngẩng 3°, quay 4°.
- Trượng gần thẳng đứng, ngả ra ngoài 8°, đuôi chạm đất (x −0,29, z 0,10); trượt trượng trong tay 13 cm (`CTL_Weapon_R` tx 0,13)
  để tay nắm ở ngang ngực (0,99 m) thay vì ngang vai; xoay trượng 90° quanh trục để mặt trăng + quả cầu quay ra trước như concept.
  Cách đầu 8,3 cm. Cẳng tay phải gần ngang, khuỷu sát sườn (gập 66°), găng khép 0,65.
- Tay trái chống nạnh (ref phác thảo): cổ tay ở hông (0,30; 0,82), khuỷu chĩa ra ngoài (gập 84°), găng khép 0,55.
- Hai vạt: chữ S rủ xuống và xoè ra hai bên sau lưng (Flap1 xuống 28°/ra ngoài 30°, Flap2 −12°, Flap3–4 cong lên 22°/18°), ngọn
  cách đất ≥ 0,33 m.

### k1_idle v3 (chân theo ảnh người dùng gửi, 2026-11-05)
Thay thế trụ một chân của v2 bằng tấn rộng: hai cổ chân cách 36 cm (rộng ngang vai), chân phải trước chân trái 9 cm, mũi chân xoay
ngoài 18°/16°, cả hai bàn chân phẳng; hông hạ 1,8 cm, dời trái 2 cm, nghiêng 2°; hai gối chùng đều 23°, pole gối dời ra ngoài 8 cm
cho gối chĩa theo mũi chân. Ngực nghiêng ngược 5°. Trượng dời ra ngoài (tay nắm x −0,49, đuôi x −0,35) để cách bàn chân phải ~10 cm;
tay phải gập 49°. Tay trái chống nạnh theo hông mới. Phần trên khác giữ như v2.

## D. Nối với anim khác [suy luận]

| Từ → tới | Điều kiện |
|---|---|
| Idle → Attack | Attack F1 = Idle F1 (cùng pose k1) hoặc dùng crossfade ngắn ~4–6 F của Unity. Trượng không đổi tay. |
| Idle → Skill 1 / 2 / 3 | Như trên. Skill 2 và 3 bay lên từ tư thế đứng đất của Idle. |
| Skill 3 Burst → Idle | [GDD] "hạ xuống đất chuyển về idle": khung cuối Burst = Idle F1. |

## E. Câu hỏi cho GD (kèm phương án đề xuất)

1. **Camera ingame** là góc nào (top-down, 3/4 từ trên, hay ngang)? Quyết định độ lớn chuyển động đọc được và PA cầm trượng. *Đề xuất:* 3/4 từ trên (thủ thành ở tâm).
2. ~~**Cách cầm trượng khi Idle**~~ → **Chốt PA A** (người dùng 2026-11-05): trượng dựng chéo ~18°, đuôi chạm đất bên phải, tay cầm cao ~1,07 m.
3. **Hai vạt dài sau lưng** bay ngang theo gió (đúng dáng model) hay rủ xuống? *Đề xuất:* bay ngang, gợn nhẹ.
4. **Có lơ lửng không?** FDD chỉ nói "bay lên" ở Skill 2/3, nên đề xuất Idle đứng đất.
5. ~~Độ dài loop~~ → **Chốt 40 F** (người dùng 2026-11-05). Còn mở: có cần biến thể Idle dài (liếc, xoay trượng) để chèn ngẫu nhiên không?
6. ~~Clip cũ "trượng dựng đuôi chạm đất bên phải"~~ → thay bằng PA A (vẫn chạm đất bên phải, nhưng chéo).
</content>
</invoke>
