# Director log – frolvy_ninja (rig Frolvy)

## Director – Ninja (Frolvy) bind skin v1 – mốc rig-skin – 2026-11-03
**Kết luận: Cần sửa**
Ý chính: Phần dữ liệu weight đã sạch: tổng bằng 1, tối đa 4 ảnh hưởng, đối xứng tuyệt đối, cross-side 0, far 0, đầu–cổ và khăn cổ gán đúng, mông đã đỡ vỡ (×2.73 → ×1.88). Còn hai việc chưa xong. (1) Khuỷu 90° vẫn có cạnh bị nén dưới ngưỡng đã chốt ở bản pháp sư cùng thân. (2) Ảnh duyệt vẫn là một pose tổng hợp, chồng đầy gizmo, mỗi ô ~400 px, nên không nhìn được mặt trong khuỷu, khoeo và đáy háng.

### Lỗi (nặng → nhẹ)
| # | Mức | Khớp | Bộ phận | Lỗi | Loại | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | A | Elbow_R/L 90° | khuỷu, mặt trong | 4 cạnh bad, min 0.20. Ngưỡng chốt ở bản pháp sư (cùng thân) là min ≥ 0.3 ở góc 90°. Đây là loại lỗi người dùng đã bắt ở SDR01 (lặp lại từ mage v3) | giữ thể tích | In vị trí và độ dài thật của cạnh 0.20. Cạnh < 1 cm và nằm ở mặt ngoài thì hạ xuống C. Nằm ở mặt trong thì dời dải chuyển lệch về phía cẳng tay, hoặc đặt cố định một vòng đỉnh 50/50 ở mặt trong | [đo] 0.20 |
| 2 | A | khuỷu 90, gối 90/110, háng | ảnh kiểm | Chỉ có 1 pose tổng hợp, có overlay joint/control, cỡ ~400 px mỗi ô. Không thấy mặt trong khuỷu, khoeo, đáy háng, nắm tay cầm dao (lặp lại từ mage v3 #3) | thiếu ảnh | Render cận từng khớp, ẩn joint/gizmo, ≥ 512 px, 3 góc (trước, bên, trên). Gồm: khuỷu 90, gối 90 và 110, hip_fwd80, hip_side45, tay phải handPose 2 cầm dao | thiếu ảnh |
| 3 | B | Knee 90° / 110° | gối | Có số cạnh (90: 6 bad, min 0.29; 110: 11 bad, min 0.17) nhưng chưa có độ dày gối. Bản pháp sư chốt độ dày ≥ 0.75. Khớp gối vừa dời về 0.386 nên phải đo lại | giữ thể tích | Báo độ dày gối và độ gãy ở 90°. Độ dày < 0.75 thì nâng lên A | [đo] thiếu độ dày |
| 4 | B | Hip X 60/80° | bẹn / mông | 80°: max 2.24, 11 bad. 60°: 1.80. Tệ hơn bản pháp sư (1.73 ở 80°), có thể do sửa mông. Ninja đá và nhảy nên đây là góc hay dùng | giữ thể tích | Ghi vị trí các cạnh bad (bẹn trước hay mông sau). Nếu ở mông thì nới dải Root→Hip mặt sau (−5/+20) rộng thêm về phía dưới, nhưng vẫn giữ trần Root ở 0.45 | [đo] 2.24 |
| 5 | B | Hip Z 45° | đáy háng | Cạnh 1.5 cm giãn ×3.12, tức hở thêm khoảng 3.2 cm, nhìn thấy được khi dạng chân. Đỉnh giữa háng Root 50 / Hip 25/25 | giữ thể tích | Đo khoảng cách thật. Nếu > 2 cm thì làm mềm hàng đỉnh kề đáy háng (Root 30–40) | [đo] ×3.12 |
| 6 | B | Finger/Thumb_R | tay cầm dao | Chưa test nắm tay: dao 100% Weapon_R nhưng ngón có ôm cán không? (lặp lại từ mage v2 #2) | rò weight | Chạy handPose 2 và `thumb_into_palm`. Cán nằm trong lòng tay, không có cạnh bad ở đốt ngón | thiếu số đo |
| 7 | C | Knee trên giày | cổ chân | Knee 7–27% ở y 0.04–0.08 là có chủ đích, đo thấy ankle40 tốt hơn, nên chấp nhận. Chưa thử kết hợp gối 90 + cổ chân 30 | chuyển weight | Thử pose kết hợp. Mu giày không vênh thì giữ nguyên | [đo] |
| 8 | C | Head cúi 30 / Neck | đầu và khăn cổ | Dải nối giãn 1.52 thì skill chấp nhận. Đầu chibi to, cúi có thể xuyên khăn cổ (khăn 100% Chest). shoulder_down70 còn 3 bad | xuyên | Kiểm cúi đầu 30°. Xuyên ít thì để tới khi làm clip | [mắt] |

### Giữ nguyên
- Tổng weight = 1, tối đa 4 ảnh hưởng, nhỏ nhất ≥ 1%. Đối xứng 435 cặp lệch 0. Cross-side 0, far 0.
- Head/Neck không xuống dưới y 1.19. Khăn cổ 100% Chest. Đuôi khăn nội suy Chest→Scarf theo z (xoay/hất 0 bad). Dao 100% Weapon_R.
- Trần Root ở 0.45 (nếp mông), đỉnh khe mông Root 50 / Hip 25/25. Ankle 0 bad, hip_back30 0, spine30 1. Bụng chỉ kéo 0.7 cm khi nhấc đùi 80.
- Ảnh tổng hợp nhìn tổng thể không thấy vỡ hình rõ ở mông (sau), gối nhấc (bên), khuỷu trái 80 (chéo) [mắt, ảnh nhỏ có overlay]

### Định hướng vòng sau
- Duyệt khi: khuỷu 90 có min ≥ 0.3 (hoặc chứng minh cạnh đó ngắn và nằm ngoài), gối 90 có độ dày ≥ 0.75, và có ảnh cận sạch 3 góc cho khuỷu, gối, háng, nắm dao. Hip 80 và hip_side45: chỉ cần chỉ ra vị trí cạnh bad và cho xem ảnh. Nếu ảnh trông ổn thì giữ, để người dùng quyết.
