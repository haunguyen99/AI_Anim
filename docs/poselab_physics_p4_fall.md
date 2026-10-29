# Pose Lab: gói ngã/chết

Đã duyệt 2026-10-25 ("duyệt": dựng cú đổ thử để nghiệm thu, nảy 15 %, lún sàn 2 cm). Các giai đoạn trước: lò xo (`poselab_physics_p1.md`), va chạm thân (`p2`), cân bằng (`p3`).

## 1. Mục tiêu

Giúp làm anim ngã và chết của nhân vật nặng như Gaygor cho đúng cân nặng:
- **Timing đổ người:** so cú đổ trong anim với cú đổ theo vật lý, để biết đang đổ quá chậm (nhẹ như bông) hay quá nhanh.
- **Nằm trên sàn:** lưng, vai, đầu, tay, khiên, chùy không lún xuống sàn. Lớp vật lý cũng không đẩy chúng xuyên sàn.
- **Đập xuống sàn rồi lắng:** khi người chạm đất, tay, chân, chùy còn văng và nảy nhẹ rồi mới nằm yên. Phần này dùng lò xo của giai đoạn 1, nay biết sàn.

**Ngoài gói này:** ragdoll tự tạo cú ngã, tự sinh anim chết. Ragdoll dễ cho cú ngã nhẽo, mất chất diễn; người làm anim vẫn đặt pose kể chuyện, công cụ chỉ đo và thêm chuyển động phụ.

## 2. Mốc vật lý của Gaygor (tính trước, 2026-10-25)

Coi thân như một khối cứng đổ quanh mép bàn chân. Trọng tâm cao 0,98 m (không chùy) hoặc 1,19 m (có chùy 15 %), bán kính quán tính 0,3 m.

| Kiểu ngã | Từ lúc bắt đầu đổ tới lúc chạm đất |
|---|---|
| Tự đổ từ đứng yên, nghiêng sẵn 3° | 40–43 frame (1,3–1,4 s) |
| Tự đổ, nghiêng sẵn 10° | 28–30 frame |
| Bị đánh bật, đà 60°/s | 19–20 frame |
| Bị đánh bật, đà 120°/s | 13–14 frame |
| Khuỵu sụp thẳng xuống (trọng tâm rơi 0,4–0,7 m) | 9–12 frame |

**Hai ý quan trọng:**
- **Đà ban đầu quyết định gần hết thời gian đổ.** Cùng là ngã ngửa, bị đánh mạnh thì nhanh gấp 3 lần tự đổ. Vì vậy công cụ không đưa ra một con số cố định, mà lấy đà ngay trong anim (tốc độ nghiêng của thân ở frame bắt đầu đổ) để tính đường đổ tham chiếu.
- **Lỗi thường gặp nhất là đổ chậm đều.** Cú đổ thật chậm ở đầu rồi nhanh dần, chạm đất nhanh nhất. Anim thường đổ đều rồi chậm lại trước khi chạm đất (ease-out). Đó chính là cảm giác "nhẹ".

## 3. Các phần

### 3.1 Đường đổ tham chiếu

- **Tự tìm frame bắt đầu đổ:** trọng tâm ra khỏi vùng đỡ và không có bước nào đỡ (lỗi "nghiêng quá" của giai đoạn 3), kéo tới khi thân chạm đất. Người dùng chỉnh lại được bằng cách chọn khoảng frame.
- **Đường tham chiếu:** từ góc nghiêng và tốc độ nghiêng của thân ở frame bắt đầu, tính đường đổ của khối cứng quanh mép chân (như bảng trên). Với kiểu sụp xuống, dùng rơi tự do của trọng tâm.
- **Đồ thị:** chiều cao trọng tâm theo frame, gồm đường anim và đường vật lý. Có dòng tóm tắt kiểu "chạm đất ở F24, vật lý là F19: chậm hơn 5 frame", "chậm dần lúc sắp chạm đất (ease-out)".
- **Bóng mờ "theo vật lý":** hiện tư thế cả người đổ cứng theo đường tham chiếu ở frame đang xem, để so mắt.

### 3.2 Sàn cho cả thân

- Mọi điểm bề mặt của các khúc thân (đã có từ giai đoạn 2) không được thấp hơn sàn quá 2 cm. Thêm dòng **"lún sàn"** vào danh sách va chạm, tô đỏ trên dải "xuyên".
- **Khi nằm:** các khúc chạm sàn trở thành vùng đỡ của giai đoạn 3. Nhờ vậy nằm yên không bị báo "rời đất".
- **Lớp vật lý:** mọi phần lò xo tránh sàn bằng cách chạm không nảy, như với thân. Mức sàn bằng min(0, chính pose key), nên không bao giờ thấp hơn key.

### 3.3 Đập xuống sàn rồi lắng

- Các phần lò xo (tay, khiên, chùy, vạt khố) giữ đà khi thân chạm đất, chạm sàn, rồi lắng. Với tay và chùy, thêm một cú **nảy nhỏ** (mặc định nảy lại 15 % tốc độ lao vào) để có chất "đồ nặng rơi xuống". Chạm thân giữa các khúc vẫn không nảy.
- **Mức có sẵn** cho anim chết: tay và đầu "Nhẹ", khiên và chùy "Nặng", và một nút gợi ý chọn các phần nên mềm.

## 4. Nghiệm thu

Hiện chưa có anim chết của Gaygor (xem mục 6, câu 1).
- **Đường đổ:** dựng thử cú đổ cứng quanh gót chân trên Pose Lab, với nhiều góc và đà khác nhau. Đường đổ trong anim phải trùng đường tham chiếu (lệch dưới 1 frame lúc chạm đất). Làm chậm cú đổ đi 30 % thì phải báo "chậm hơn".
- **Sàn:** cho người nằm, hạ thấp 5 cm. Phải báo "lún sàn" đúng khúc, đúng frame.
- **Vật lý:** khi chạm sàn, tay và chùy văng ra rồi lắng, không xuyên sàn, không rung.
- **Clip đã duyệt** (Hit, Attack, Walk): không có báo mới.
- **Python và trang:** cùng kết quả.

## 5. Ước lượng

- Đường đổ tham chiếu, đồ thị, bóng mờ: 1 buổi.
- Sàn cho cả thân (báo và vật lý), vùng đỡ khi nằm: nửa buổi.
- Đập sàn, nảy nhỏ, mức có sẵn: nửa buổi.
- Bản Python, nghiệm thu, tài liệu: nửa buổi.

## 6. Cần bạn quyết

1. **Clip để thử:** chỉ dựng cú đổ thử trên Pose Lab, hay làm luôn **Gaygor Die** thật bằng quy trình C (bản thiết kế, pose kể chuyện, blocking…) và dùng gói này trong lúc làm? Đề xuất: **dựng cú đổ thử để nghiệm thu công cụ**, còn Gaygor Die làm thành clip riêng khi bạn cần, vì nó cần các cổng duyệt riêng.
2. **Nảy khi chạm sàn** cho tay và chùy: 15 % tốc độ, hay không nảy (chỉ lắng)? Đề xuất: **15 %**.
3. **Ngưỡng "lún sàn":** đề xuất **2 cm**, giống ngưỡng xuyên thân.

## 7. Đã làm (2026-10-25)

Có trên trang Pose Lab của Hit, Attack 50 và Walk (bảng Cân bằng và bảng Va chạm thân).

**Đường đổ tham chiếu**
- Cú ngã được tìm tự động. Điểm kết thúc là frame một khúc thân (không tính bàn chân và vũ khí) chạm sàn (≤ 2 cm). Điểm bắt đầu là frame trọng tâm bắt đầu đi xuống liên tục, bỏ qua các frame còn đứng vững trong chân. Trọng tâm phải hạ hơn 25 cm.
- Đổ người (topple): khối cứng đổ quanh điểm của **bàn chân** xa nhất theo hướng ngã. Góc nghiêng tính trong mặt phẳng ngã, có dấu. Góc và đà ban đầu lấy từ chính anim. Sụp xuống (collapse, trọng tâm đi ngang < 30 % độ rơi): rơi tự do từ tốc độ rơi của anim.
- Dòng báo trong danh sách Cân bằng: "đổ người chạm đất sau 20 frame, vật lý 17 frame: chậm hơn 3 frame, chậm dần trước khi chạm đất". Cú ngã đúng vật lý vẫn hiện một dòng "khớp". Báo khi lệch ≥ 2 frame, hoặc khi tốc độ rơi lúc chạm đất < 60 % tốc độ lớn nhất (ease-out). Lỗi cân bằng nằm trong cú ngã thì không báo lặp.
- Đồ thị chiều cao trọng tâm (xanh: anim, nét đứt: vật lý), theo frame đang xem.
- Nút **Bóng đổ theo vật lý**: bóng mờ là pose ở frame bắt đầu đổ, đổ cứng theo đường vật lý.

**Sàn cho cả thân**
- Khúc thân hoặc vũ khí thấp hơn sàn quá 2 cm: dòng "… lún sàn, sâu X cm" trong danh sách va chạm và trên dải đỏ.
- Khúc thân chạm sàn (< 5 cm) là vùng đỡ ("T:<khúc>"), nên nằm yên không bị báo rời đất.
- Lò xo: sàn là một vật chắn của mọi phần (khớp, bản lề, đung đưa khuỷu), không thấp hơn pose key. Chạm sàn nảy lại 15 %, cả khớp lẫn vũ khí. Chạm thân giữa các khúc vẫn không nảy.

**Nghiệm thu**
- Cú đổ cứng dựng thử trên Attack polish_v3 và Hit (chỉ trên máy, đã xóa):
  - Đổ đúng vật lý khớp dưới 1 frame: Hit, đà 100°/s: 18 / 17,9 frame. Hit, 150°/s: 13 / 12,9. Attack: 17 / 16,9.
  - Làm chậm 30 % thì báo chậm hơn 3,6 frame; chậm 50 % thì 6,9 frame.
  - Thay 6 frame cuối bằng ease-out: báo "chậm hơn 3,4 frame, chậm dần trước khi chạm đất". Bóng mờ đã chạm đất ở F21 trong khi anim còn cao.
- Hạ người nằm 5 cm: báo lún sàn đúng ở Root, Spine, hai vai, khuỷu, F40–45.
- Vật lý không tạo lỗi lún sàn mới. Rung nhẹ khi nảy ở chỗ chạm sàn không bị tính là lỗi.
- Hit, Attack, Walk đã duyệt không có báo mới, trừ một lỗi có thật: **Attack F23–50, móng tay trái lún 15 cm dưới sàn** (đã nhìn từ dưới sàn để xác nhận).
- Python `tools/physics_sim.py` cho cùng kết quả với trang:
  - Lò xo có sàn và nảy: lệch tối đa 0,006° (`phys_check/hit_v2_body.json`, `attack_v3_body.json`).
  - Cú ngã, vùng đỡ khi nằm, lún sàn: `--balance` trên `phys_check/attack_fall_bal.json` cho cùng cú ngã (F5–25, 20 / 16,6 frame, ease-out), cùng lỗi, và 91 frame lún sàn như trang.
- Thời gian: quét cân bằng có cú ngã trên Attack (68 frame) mất khoảng 0,23 s.

**Chưa làm:** "Mức có sẵn cho anim chết" và nút gợi ý phần nên mềm (mục 3.3). Hiện dùng nút preset Gaygor và chỉnh từng phần.
