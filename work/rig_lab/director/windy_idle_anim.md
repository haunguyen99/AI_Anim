# Director log – windy_idle (Windy_Idle.fv, anim Idle loop 40F)

## Director – Windy Idle (Windy_Idle.fv, key F0/F17/F40) – mốc blocking – 2026-11-05
**Kết luận: Cần sửa** (chỉ 1 lỗi A về biên độ; khung nhịp đúng, sửa xong là sang spline được)
Ý chính: một nhịp thở 40F, hít 17F, thở ra 23F (~43/57, đúng analysis C), loop khít (seam 0,000 cm), chân khóa (trượt 0). Khung đúng. Nhưng thân chỉ nhún 1–2 cm còn ngọn áo choàng đi 24 cm. Ở camera game ta chỉ thấy áo choàng lắc trên một thân đứng im, chưa thấy nhân vật thở.

### Lỗi (nặng → nhẹ)
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | A | F17 (đỉnh) | ngực / vai / đầu | Biên độ thở gần như không thấy ở cam game. Ước tính nhân vật cao ~1,65 m (theo ảnh front), ở camera2 cao ~110 px, tức ~0,7 px/cm. Vai đi lên 1,8–2,0 cm ≈ 1,4 px, đầu 1,45 cm ≈ 1 px, tay phải và đầu trượng 0,8 cm ≈ 0,5 px. Ảnh side F0 và F17 để cạnh nhau gần như trùng nhau. Bản Gaygor đã duyệt (cam top-down) có vai nhún 6–9 cm. | Readability / Exaggeration | Tăng biên độ thân trên, KHÔNG hạ hông: vai (Scapula R/L ty) lên 3,5–4 cm; Chest rx −2,5 → −3,5°; Spine1 −1,5 → −2°; Neck giữ nguyên; Head rx bù +2 → +3° để mặt vẫn nhìn thẳng; Root ty giữ +1 cm. Không vượt Chest −4° (bài học: uốn quá tay thì đầu gật). Render cam game F0 và F17 ≥ 512 px, đặt riêng cạnh nhau để xác nhận vai và quả cầu thấy được dịch chuyển. | [đo] measure.txt + ước tính px |
| 2 | B | F0–F40 | áo choàng Cape1–4 | (a) Cả 4 đốt key cùng frame (F10/F30) nên áo đung đưa như một tấm ván cứng. (b) Biên độ áo (ngọn 24 cm) gấp 12 lần thân: mắt bị kéo hết vào áo. (c) Pha −A ở F30 đưa ngọn áo ra trước: chưa có ảnh nên chưa biết có xuyên bắp chân, gót hay đuôi trượng không. | Overlap / Hierarchy of motion | Để trễ cho bước spline: 0/+3/+6/+9 F gốc → ngọn (analysis: 3F/đốt). Sau khi tăng biên độ thân (#1) thì giữ A ngọn ≤ 10°. Render side F10 và F30 để kiểm xuyên. | [đo] CapeEnd 24,2 cm; [mắt] xuyên chưa xem |
| 3 | B | F0–F40 | tay trái (FK) | Tay đi cứng theo ngực: cổ tay trái dịch 4,47 cm, nhiều hơn vai (2,3 cm), cùng pha F17. Khi ngực ưỡn, tay buông dưới tâm xoay ngực bị đẩy ra trước/sau như một thanh cứng: tay bị lắc chứ không treo. | Follow-through / Gravity | FK Shoulder_L xoay bù để bàn tay vẫn treo gần thẳng xuống, chỉ nhấc 1–2 cm. Elbow_L trễ +2 F sau vai. Trễ thêm khi sang spline (vai +4, khuỷu +6, cổ tay +7). Khuỷu giữ gập > 40°. | [đo] Wrist_L 4,47 cm |
| 4 | B | F0–F40 | trượng / đầu trượng | Trượng chỉ tịnh tiến 0,8 cm theo tay phải, không xoay. Quả cầu là khối dễ thấy nhất ở cam game mà đứng im nên đọc là "đóng băng". | Overlap / Secondary | Ở spline: xoay nhẹ CTL_Weapon_R (hoặc xoay IK tay R) để quả cầu đi lên/xuống 1,5–2 cm, trễ 3–4 F sau cổ tay phải. Đòn bẩy ~1,2 m: 1° ≈ 2 cm, nên giữ ≤ 1°. Điều khiển đường đi của quả cầu, không khuếch đại xoay vai (props_weapons#heavy-prop-lever, #long-prop-flick). Đo khoảng hở mũi nhọn đuôi trượng với sàn ở mọi frame: ảnh front cho thấy mũi đã sát sàn (~5 px), xoay sai chiều sẽ cắm xuống đất. | [đo] WeaponEnd 0,8 cm; [mắt] mũi sát sàn |
| 5 | C | F0–F40 | hai vạt BackFlap | Gió đã tắt theo ý người dùng (không tính là lỗi). Dù vậy, ngọn vạt vẫn đi lên/xuống 7,3 cm cứng theo ngực (đỉnh F0, đáy F17), như một cái cánh cứng gắn vào lưng. Đây là trễ quán tính, không phải gió. | Follow-through | Để người dùng quyết định: thêm trễ 2–3 F/đốt cho BackFlap1–4, xoay ngược một phần chuyển động từ ngực, không thêm gợn gió. Đưa người dùng 2 bản (cứng / có trễ) để chọn. | [đo] BackFlapEnd 7,3 cm |
| 6 | C | — | trượng chéo / tay cầm | Pose gốc do người dùng chọn. Đầu trượng nặng ở cao bên trái chỉ có một tay đỡ, nên thở mạnh hơn (#1) sẽ làm lộ đòn bẩy. Ghi chú, không phải lỗi. | — | Để người dùng quyết định. | [mắt] |
| 7 | C | toàn clip | quy ước frame | Frolvy F0..F39 (F0 = F40), còn analysis và Studio dùng F1 = đáy, đỉnh ở F18. Hai cách đếm khớp nhau (F17 Frolvy = F18), nhưng mọi ghi chú gửi người dùng phải ghi rõ đang đếm theo cách nào. | — | Ghi "F17 (Frolvy, 0-based)". | — |

### Giữ nguyên
- Tỉ lệ hít/thở 17/23. Đỉnh ở F17 đều trên mọi xương thân, không vọt lố (biên độ đo = giá trị key). Seam F40–F0 = 0.
- Chân IK khóa, trượt 0. Hông chỉ nâng khi hít, không hạ hông.
- Đầu bù rx để mặt nhìn thẳng, yaw khóa.
- Chu kỳ áo 40F, biên độ tăng dần gốc→ngọn (2/4/7/10°): cấu trúc đúng, chỉ thiếu trễ.
- Pose gốc của người dùng (trượng chéo, chân phải trước): không đụng.

### Định hướng vòng sau
- Trước khi spline: sửa #1, rồi render cam game F0|F17 ≥ 512 px để cạnh nhau, cùng side F10/F30 (kiểm áo xuyên chân) và một playblast cam game 2 vòng loop.
- Bảng trễ cho spline (40F, rút từ công thức 60F × 2/3): hông 0, Spine1 +1, Chest +3, Scapula/Neck +4, Head +6, vai trái +4 / khuỷu +6 / cổ tay +7, IK tay R +4, quả cầu trượng +7, Cape +0/+3/+6/+9. Dời cả đường cong (giữ tỉ lệ 17/23), đừng nắn lại hình dạng. Với infinity cycle, sau khi dời phải key lại F0 và F40 bằng giá trị nội suy để seam vẫn = 0. Đo lại frame đỉnh từng xương sau khi dời.
- Mục tiêu cảm giác: ngực dẫn, vai và đầu trễ theo, tay và trượng treo, áo gợn từ gốc ra ngọn. Nhân vật thở trước, áo đi sau.
