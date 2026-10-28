# Pose Lab: vật lý giai đoạn 2 (va chạm cả thân)

Đã duyệt 2026-10-25 ("oki làm như đề xuất": chưa tự sửa key, ngưỡng 2 cm, mốc nghỉ = pose Idle). Giai đoạn 1: `docs/poselab_physics_p1.md`.

## 1. Mục tiêu

Tay, khiên, vũ khí và vạt khố không xuyên vào người.
- **Báo xuyên:** khi pose, khi xem lại, và trong QA, frame nào xuyên thì hiện ngay.
- **Vật lý không gây xuyên:** lớp vật lý của giai đoạn 1 không được đẩy tay hay khiên vào thân. Hiện chỉ vật cầm tay mới có vùng chắn.

**Ngoài giai đoạn 2:**
- Tự sửa key bị xuyên (xem mục 7).
- Trọng tâm và cân bằng.
- Gợi ý phản ứng trúng đòn.

## 2. Đo thử trước khi thiết kế (2026-10-25)

Mình dựng thử hình con nhộng (capsule) cho 17 khúc của Gaygor, tự lấy từ lưới (mỗi đỉnh thuộc xương có trọng số lớn nhất, bán kính = phân vị 60 %). Sau đó quét các clip đã duyệt, chỉ tính chỗ lẹm hơn lúc nghỉ (F1) quá 2 cm:

| Clip | Cặp bị báo xuyên |
|---|---|
| Hit polish_v7 | 3 cặp: khiên/cẳng tay phải với đùi và gối phải, F10–F24, sâu tới 10 cm |
| Attack 50 polish_v3 | 11 cặp: khuỷu phải với đầu và ngực, chùy với đầu, ngực, tay phải… |

Xem tận mắt hai chỗ nặng nhất:
- **Attack F30, chùy với đầu (báo 13 cm):** không xuyên. Chùy nằm trên cẳng tay, phía sau đầu.
- **Hit F12, khiên với gối (báo 10 cm):** không xuyên. Khiên chỉ nằm cạnh gối.

**Kết luận:** con nhộng dựng thô báo sai nhiều. Nguyên nhân:
- **Giáp làm phình hình:** khiên làm con nhộng cẳng tay phải dày 27 cm; mào và sừng làm con nhộng đầu dày 23 cm.
- **Chạm cố ý bị tính là xuyên:** tay nắm chùy, chùy kê vai.

Cách dựng hình phải sửa đúng hai điểm này. Không được tin số đo khi chưa nhìn bằng mắt (bài học "Eye first").

## 3. Hình va chạm

| Loại | Dùng cho | Cách dựng |
|---|---|---|
| **Lõi con nhộng** | Thân, đầu, cổ, đùi, cẳng chân, cánh tay, cẳng tay, bàn tay | Tự dựng từ lưới, bán kính phân vị **40 %** (thon, nằm trong thịt), bỏ đỉnh của giáp |
| **Vỏ điểm** | Khiên, vũ khí, giáp lớn | Tập điểm của lưới (như chùy ở giai đoạn 1), gắn vào xương mang nó |
| **Sàn** | Chân, vật cầm tay | Đã có |

- **Dựng một lần cho mỗi nhân vật:** nút "Dựng vùng va chạm" tạo bộ hình. Bật "Hiện vùng va chạm" thì hình hiện mờ trên model. Kéo thanh trượt để chỉnh bán kính từng khúc. Bộ hình lưu theo nhân vật, giống "Mức của nhân vật".
- **Giáp được nhận riêng:** đỉnh nằm xa trục xương hơn 1,6 lần bán kính lõi thì coi là giáp. Giáp lớn (khiên) thành vỏ điểm riêng.

## 4. Cặp nào được kiểm

- **Kiểm:**
  - tay (cánh tay, cẳng tay, bàn tay, khiên) với thân, đầu, cổ, đùi, cẳng chân;
  - tay với tay; chân với chân;
  - vũ khí với mọi khúc;
  - vạt khố với đùi.
- **Bỏ qua:**
  - khúc liền nhau (vai với ngực);
  - bàn tay đang nắm vật với chính vật đó;
  - vật với vùng chắn đã khai báo (chùy kê vai).
- **Tính tương đối:** chỉ báo phần lẹm sâu hơn lúc nghỉ (F1 hoặc pose Idle). Chỗ vốn đã chạm khi đứng yên (nách, đùi trong) không bị báo.
- **Ngưỡng báo:** sâu hơn lúc nghỉ 2 cm (chỉnh được).

## 5. Dùng ở đâu

1. **Báo xuyên trên trang:**
   - một dải đỏ "xuyên" trên timeline;
   - danh sách kiểu "F25–F26 khuỷu phải vào ngực, sâu 9 cm", bấm vào là nhảy tới frame;
   - hai khúc đang xuyên tô đỏ trên model.
   Chạy cả khi vật lý tắt.
2. **Trong lớp vật lý:**
   - mọi phần lò xo (khớp mềm, bản lề, đung đưa khuỷu, vật cầm tay) đều tránh các khúc thân;
   - dùng ràng buộc không nảy của giai đoạn 1: xoay phần đó ra khỏi thân đúng phần lẹm và bỏ vận tốc lao vào;
   - mức sàn = min(lúc nghỉ, pose key), nên vật lý không bao giờ làm xuyên sâu hơn key.
3. **Python:** `tools/physics_sim.py` dùng cùng bộ hình. QA của AI (`polish_check.py` và các bản sau) thêm mục "xuyên thân".

## 6. Nghiệm thu

- **Báo sai:** trên Hit polish_v7, Attack 50 polish_v3 và Walk, xem tận mắt mọi chỗ bị báo. Mục tiêu không còn báo sai; chỗ nào còn thì ghi lý do.
- **Báo đúng:** cố ý xoay khuỷu vào ngực, hoặc ép khiên vào đùi. Phải báo đúng frame, đúng cặp.
- **Vật lý:** trên Hit polish_v2, cho tay phải nặng hơn tới khi khiên quệt vào đùi. Khiên phải dừng ở đùi: không xuyên, không bật, không rung.
- **Tốc độ:** quét cả clip dưới 0,2 giây; vật lý vẫn dưới 0,2 giây.
- **Python và trang:** khớp nhau dưới 0,1°.

## 7. Cần bạn quyết

1. **Tự sửa key bị xuyên?** Ví dụ nút "Đẩy ra" xoay khớp ra khỏi thân bằng IK, cho frame đang xem. Đề xuất: **để sau**. Giai đoạn 2 chỉ báo và giữ cho vật lý không gây xuyên; sửa key vẫn do người làm, vì cách sửa đúng tùy ý diễn.
2. **Ngưỡng báo:** sâu hơn lúc nghỉ 2 cm. Đề xuất: **2 cm**.
3. **Mốc "lúc nghỉ":** F1 của clip hay pose Idle của nhân vật? Đề xuất: **pose Idle**, vì clip có thể bắt đầu ở pose khác.

## 8. Ước lượng

- Dựng hình và hiệu chỉnh trên Gaygor, gồm xem tận mắt: 1 buổi.
- Báo xuyên trên trang (dải, danh sách, tô đỏ): nửa buổi.
- Va chạm trong vật lý và bản Python: 1 buổi.
- Nghiệm thu, tài liệu: nửa buổi.

## 9. Đã làm (2026-10-25)

- **Code:** `work/pose_lab/index.html`, phần "body collision" (`buildBody`, `pairDepth`, `bodyIssues`, `scanBody`, `drawBodyViz`), phần "body collision for the springs" (`bodyLink`, `bodyPush`, `bodySafe`) và phần "body collision panel". Bản Python: lớp `Body` trong `tools/physics_sim.py`.
- **Cách đo cuối cùng (sửa qua 4 lần, mỗi lần soi tận mắt):**
  - lõi con nhộng bán kính phân vị 40 %, tính chỉ từ đỉnh của chính khúc đó;
  - khúc dày hơn khúc đối xứng quá 30 % (cẳng tay có khiên) thì lấy bán kính của bên kia;
  - đỉnh của bả vai gom vào ngực, vì khối cơ thang sát đầu là thân chứ không phải tay;
  - **độ lẹm = điểm bề mặt của khúc này lọt vào lõi của khúc kia**, không đo con nhộng với con nhộng (cách đó báo đầu lẹm vào tay 17 cm trong khi lưới chỉ chạm);
  - tay đang nắm vũ khí nhận theo khoảng cách từ vũ khí tới lõi bàn tay (6 cm).
- **Soi tận mắt trên clip đã duyệt:**

  | Chỗ báo | Kết luận |
  |---|---|
  | Attack F26–F29, khiên/cẳng tay phải vào đầu, 13–15 cm | Xuyên thật: mép khiên cắt ngang mặt |
  | Attack F58–F60, chùy vào đầu, 9 cm | Xuyên thật: đầu cán cắm vào gáy |
  | Attack F5, cẳng tay phải vào đùi phải, 6 cm | Có lẽ thật: mặt sau khiên lẹm vào đùi |
  | Hit F12–F13, bàn tay phải (khiên) vào bàn chân phải, 6 cm | Thật: mép khiên chạm mu bàn chân |
  | Attack F45–F51, cánh tay trái vào đầu, 8 cm | Giáp ranh: đầu tì sát bắp tay |
  | Walk F13–F26, chùy vào ngực, 6 cm | Giáp ranh: đầu cán sát cổ áo |

  Không còn chỗ nào báo sai rõ ràng. Hai chỗ giáp ranh chỉnh được bằng thanh bán kính lõi.
- **Báo đúng:** cố ý xoay cánh tay phải vào ngực ở Hit F16, trang báo đúng F16: cẳng tay phải vào ngực, bụng, hông, sâu 28–29 cm.
- **Vật lý:**
  - Hit polish_v2 với "Mức của nhân vật": không còn chỗ xuyên nào; Hit v7 làm tay có chỗ khiên chạm chân ở F12.
  - Cho tay phải nặng hẳn (chu kỳ 20, độ nảy 0,8, giới hạn 40°): vẫn không xuyên, lưới an toàn chỉ dùng 1 lần.
  - Attack và Walk: vật lý không thêm chỗ xuyên nào ngoài những chỗ có sẵn trong key.
- **Tốc độ:**
  - Vật lý: Hit 84 ms, Attack 194 ms, Walk 251 ms (clip lặp tính 2 vòng, 112 frame; theo frame thì tương đương).
  - Quét xuyên: 24–60 ms.
- **Python và trang:** khớp tối đa 0,0002° ở các khớp, chùy 0,006° (Hit) và 0,0004° (Attack). Dữ liệu kiểm chéo: `work/pose_lab/phys_check/*_body.json`.
- **Chưa làm (theo quyết định):** tự sửa key bị xuyên.
