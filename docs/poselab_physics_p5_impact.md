# Pose Lab: lực tác động và ragdoll

Đã duyệt 2026-10-25 ("duyệt đề xuất": cả 5 đề xuất, mục 2 đổi thành tự bước có công tắc, mặc định bật). Người dùng: "làm luôn cả 3 bước" (đặt điểm va chạm vào bộ phận bất kỳ, vật lý tính lực đẩy cả người, các bộ phận tự dao động theo quán tính; như trúng đạn, bị xe tông).
Các giai đoạn trước: lò xo (`poselab_physics_p1.md`), va chạm thân (`p2`), cân bằng (`p3`), ngã/chết (`p4_fall`). Gói ngã/chết đã để ragdoll ra ngoài; bản này mở lại phần đó.

## 1. Mục tiêu

- Đặt một **cú tác động** lên điểm bất kỳ trên người: điểm, hướng, độ mạnh, thời gian tác động.
- Vật lý truyền lực qua các khớp. Điểm trúng bật đi trước, rồi tới thân, đầu, hông. Tay, đầu và chùy văng theo quán tính rồi lắng.
- Kết quả **Bake thành key**, chỉnh tiếp như mọi anim khác.
- Ba mức, từ ít tới nhiều vật lý:

| Bước | Dùng cho | Anim gốc | Chân |
|---|---|---|---|
| 1. Lực cộng lên anim | Hit, giật mình, trúng đạn nhẹ | Giữ nguyên, lực cộng thêm rồi lò xo kéo về | Bám sàn; tự bước khi phải bước (tắt được: chỉ báo + dấu chân gợi ý) |
| 2. Ragdoll | Bị hất văng, xe tông, chết | Mất dần theo đường "sức" (100 % → 0 %) | Tự do: bay, đổ, đập sàn, lắng |
| 3. Ragdoll có cơ | Ngã có chủ ý: đưa tay đỡ, gồng, co người | Cơ thể cố theo pose của animator trong lúc bị đẩy | Như bước 2, hông cố giữ trọng tâm khi còn sức |

**Ngoài bản này:** ngón tay, mặt, vải mô phỏng đầy đủ, tự nhấc chùy đang chống sàn.

## 2. Mốc của Gaygor (đo 2026-10-25)

Khối lượng lấy từ thể tích lõi thân (giai đoạn 2), khối lượng riêng 1000 kg/m³:
- **Tổng ~1140 kg.** Chùy cộng 15 %, tổng ~1310 kg.
- **Thân:** hông 172 kg, bụng 190 kg, ngực 223 kg, đầu 58 kg.
- **Tay:** vai 71–76 kg, khuỷu 59 kg, cổ tay 19–30 kg.
- **Chân:** đùi 41 kg, cẳng 28 kg, bàn chân 21 kg.

Tổng khối lượng là một thanh chỉnh được. Phản ứng chỉ phụ thuộc tỉ lệ giữa các khúc và tỉ lệ lực trên tổng khối lượng.

**Lực thật rất nhỏ so với Gaygor:**

| Tác động | Động lượng thật | Gaygor nhận (cả người) |
|---|---|---|
| Đạn súng ngắn | ~3 N·s | 0,002 m/s (không thấy) |
| Cú đấm người | ~20 N·s | 0,015 m/s |
| Xe 1,5 t tông ở 30 km/h | ~5800 N·s | ~4,5 m/s (hất văng) |

Game và phim luôn phóng đại. Vì vậy **mức lực đặt theo kết quả nhìn thấy**, tức tốc độ trọng tâm bị đẩy đi, và ghi kèm số tương đương ngoài đời:

| Mức | Trọng tâm bị đẩy | Thời gian tác động | Gợi ý dùng |
|---|---|---|---|
| Nhẹ | 0,3 m/s | 1 frame | trúng đạn kiểu game, giật mình |
| Vừa | 1 m/s | 2 frame | đấm, chém |
| Mạnh | 2,5 m/s | 3 frame | chùy, nổ gần |
| Hất văng | 5 m/s | 4–6 frame (đẩy liên tục) | xe tông, bị quật |

Cùng một mức, đánh vào đầu thì đầu quay mạnh, ít dời người. Đánh vào hông thì cả người dời, ít quay. Phần này do vật lý tính, không đặt tay.

## 3. Cách đặt tác động (chung cho 3 bước)

- Nút **"+ Tác động"**, rồi bấm lên người. Điểm bám vào điểm bề mặt gần nhất của khúc thân (đã có ~160 điểm mỗi khúc).
- **Hướng:** mũi tên kéo trên màn hình. Mặc định vuông góc bề mặt, đâm vào trong.
- **Bảng tác động:** frame bắt đầu, mức lực (4 mức hoặc số m/s), thời gian, hệ số phóng đại.
- Một clip có thể có **nhiều tác động**, ví dụ hai phát đạn liên tiếp. Mỗi tác động hiện thành một chấm trên dải "Tác động" (dải mới trên timeline) và mũi tên trên model ở frame của nó.
- Lưu trong cấu hình vật lý của version (db `anims`, trường `phys.impacts`), như các thiết lập lò xo.

## 4. Bước 1: lực cộng lên anim

- **Truyền lực:** coi cả người là cây khối cứng nối khớp: 17 khúc + chùy, gốc tự do 6 bậc. Xung lực tại điểm trúng cho ra **vận tốc tức thời của mọi khớp và của gốc**, giải một hệ ~57 ẩn mỗi tác động. Khúc nhẹ ở xa (đầu, cổ tay) quay nhanh; khúc nặng (hông, ngực) dời chậm.
- **Sau tác động:** mỗi khớp là lò xo của giai đoạn 1, nhận vận tốc ban đầu đó và dao động quanh anim gốc. Thêm lò xo cho **cột sống, cổ, đầu, hông**; giai đoạn 1 mới có tay và chùy.
  - Mức có sẵn: thân "Nặng", đầu "Vừa", tay "Nhẹ".
  - Va chạm thân và sàn vẫn chạy như giai đoạn 2 và gói ngã.
- **Gốc (hông):** dời và xoay theo vận tốc gốc, lò xo kéo về. Bàn chân **khóa sàn**, gối và hông chân giải IK theo hông mới.
- **Tự bước** (công tắc trong bảng tác động, mặc định bật):
  1. Cú đẩy đưa điểm bắt (giai đoạn 3) ra ngoài chân quá 5 cm thì phải bước.
  2. Chọn chân đang ít đỡ người hơn, về phía bị đẩy, không bắt chéo qua chân kia.
  3. Chỗ đặt chân: điểm bắt + một khoảng nhỏ, giới hạn độ dài bước của Gaygor (đo từ Walk và Hit).
  4. Thời gian bước theo con lắc của Gaygor (trọng tâm ~1 m): 8–12 frame; bị đẩy mạnh thì nhanh và dài hơn.
  5. Chân nhấc theo cung (cao 5–8 cm), đặt xuống, khóa sàn; vùng đỡ cập nhật.
  6. Điểm bắt vẫn ra ngoài thì bước thêm, tối đa 3 bước. Vẫn không giữ được thì báo **"ngã"** (bước 2 dùng ragdoll từ đó).
  7. Bước ghi thành key chân và dải chạm sàn thật, sửa tay được. Chùy đang chống sàn tính như một điểm đỡ.
  - Hai chân không được va nhau (va chạm thân giai đoạn 2); ca khó (bị đẩy ngang từ phía chân trụ) cho bước xấu thì báo để sửa tay.
  - Tắt công tắc: chỉ báo **"cần bước"** và vẽ dấu chân gợi ý tại điểm bắt.
- **Xem trực tiếp như lò xo:** đổi mức lực là thấy ngay. Bake ra key mỗi frame; "Hoàn tác bake" như cũ.

## 5. Bước 2: ragdoll

- **Mô phỏng cả người:** mỗi khúc là khối cứng hình con nhộng (lõi thân giai đoạn 2), nối bằng khớp cầu.
  - Giải theo kiểu ràng buộc vị trí (XPBD): bền, không nổ số, dễ thêm giới hạn.
  - 20 bước con mỗi frame.
- **Giới hạn khớp:** mỗi khớp có góc gập, góc dang, góc xoắn tối đa.
  - Lấy từ góc lớn nhất Gaygor từng có trong các clip đã duyệt (Idle, Idle_Front, Walk, Attack, Hit), cộng biên 20 %, rồi chỉnh theo giải phẫu khỉ đột.
  - Bảng giới hạn hiện trên trang để bạn kiểm bằng mắt (vẽ nón giới hạn ở khớp đang chọn).
- **Va chạm:** khúc với sàn (nảy 15 %, ma sát), khúc với khúc không kề nhau, chùy với thân và sàn. Dùng lại lõi và điểm bề mặt giai đoạn 2.
- **Đường "Sức" (dải mới, 0–100 %):** độ cứng kéo mỗi khớp về pose của anim.
  - 100 %: theo đúng anim (cộng lực như bước 1, nhưng không khóa chân).
  - 0 %: mềm hoàn toàn.
  - Ví dụ chết: 100 % tới frame trúng, tụt về 20 % trong 6 frame, về 0 % lúc chạm đất.
  - Vẽ đường bằng vài điểm, nội suy mượt. Có thể đặt riêng cho thân, tay, chân.
- **Chùy:** mặc định vẫn trong tay (khớp cổ tay–cán). Nút **"Buông chùy từ frame…"**: chùy thành vật rời, rơi, nảy, nằm.
- **Kết quả:** chạy từ frame tác động tới cuối clip (hoặc tới khi nằm yên). Thêm frame nếu clip ngắn hơn thời gian lắng. Bake ra key mỗi frame; trước đó các frame giữ anim gốc.
- **Kiểm sau Bake:** chạy lại quét xuyên, lún sàn, cân bằng và cú ngã của gói ngã/chết.

## 6. Bước 3: ragdoll có cơ

- **Pose đích theo frame:** không chỉ anim gốc. Animator đặt **pose phản xạ**, ví dụ tay đưa ra đỡ, co người, đầu ngẩng tránh đập sàn. Cơ thể cố đạt pose đó với sức ở dải "Sức", trong khi vẫn bị lực và trọng lực kéo. Kết quả là cú ngã "có ý" mà vẫn đúng trọng lượng.
- **Giữ thăng bằng khi còn sức:** hông và thân tạo mô-men đưa trọng tâm về trên chân, tỉ lệ với sức.
  - Sức cao, cú đẩy vừa: loạng choạng rồi đứng lại.
  - Sức thấp hoặc cú đẩy mạnh: ngã.
  - Khi điểm bắt ra ngoài chân thì vẫn báo "cần bước" như bước 1.
- **Sức riêng từng phần:** thân, đầu, mỗi tay, mỗi chân. Ví dụ tay phải còn gồng đỡ khi chân đã mềm.

## 7. Bản Python

`tools/physics_sim.py` có cùng ba phần (truyền xung lực, ragdoll XPBD, cơ), chạy trên dump của trang, để kiểm chéo như các giai đoạn trước.

## 8. Nghiệm thu

**Bước 1**
- **Khối cứng:** khóa mọi khớp thì vận tốc sau tác động phải bằng công thức một khối cứng (v = J/M, ω = I⁻¹ (r × J)), lệch dưới 2 %.
- **Năng lượng:** không tăng sau tác động.
- **Điểm đánh:** cùng mức lực, đánh đầu thì đầu quay nhiều hơn ngực; đánh hông thì hông dời nhiều hơn đầu.
- **Hồi về:** về lại anim gốc trong thời gian chu kỳ lò xo; không rung, không xuyên thân, không lún sàn.
- **Bước chân:** "Hất văng" vào ngực Hit F10 phải bước (tắt tự bước thì báo "cần bước"); "Nhẹ" thì không.
- **Tự bước:** sau khi bước, điểm bắt về lại trong chân; chân đã đặt không trượt (dưới 0,5 cm); hai chân không bắt chéo, không xuyên nhau.

**Bước 2**
- **Rơi tự do:** sức 0 %, trọng tâm rơi đúng g, lệch dưới 1 %.
- **Hai đầu của "Sức":** 100 % giữ đúng pose; 0 % đổ và nằm.
- **Giới hạn và sàn:** không khớp nào vượt giới hạn quá 2°, không lún sàn quá 2 cm.
- **Lắng:** nằm yên (mọi khúc < 1 cm/frame) trong 1,5 s sau chạm đất, không rung.
- **Đổ cứng:** khóa cứng toàn thân thì cú đổ khớp đường tham chiếu của gói ngã/chết, lệch dưới 1 frame.
- **Thời gian:** 68 frame mô phỏng dưới 2 s. Đo và báo.

**Bước 3**
- **Đứng vững:** sức 100 %, cú "Vừa" vào ngực thì loạng choạng rồi đứng lại, không ngã.
- **Pose phản xạ:** pose tay đỡ đạt tới (lệch dưới 10°) trước khi chạm đất khi sức tay ≥ 60 %.

**Chung**
- Python và trang cho cùng kết quả.
- Clip đã duyệt không đổi khi không có tác động nào.

**Thử trên clip thật:** sau khi xong cả 3 bước, làm **Gaygor Die** theo quy trình C (clip riêng, các cổng duyệt riêng). Ghi số vòng duyệt và thời gian từng bước để so với Hit.

## 9. Ước lượng

| Phần | Thời gian |
|---|---|
| Đặt tác động, dải, lưu (chung) | nửa buổi |
| Bước 1: truyền xung lực, lò xo thân/đầu/hông | 1 buổi |
| Bước 1: tự bước | 1–1,5 buổi |
| Bước 2: XPBD, giới hạn khớp (đo từ clip đã duyệt), va chạm, Sức, buông chùy | 2 buổi |
| Bước 3: pose phản xạ, giữ thăng bằng, sức từng phần | 1–1,5 buổi |
| Python, nghiệm thu, tài liệu | 1 buổi |

Mỗi bước xong là đăng lên trang để bạn thử, rồi mới sang bước sau.

## 10. Đã quyết (2026-10-25)

1. **Mức lực theo kết quả nhìn thấy** (tốc độ đẩy trọng tâm, có ghi số tương đương ngoài đời), hay theo lực thật? Đề xuất: **theo kết quả nhìn thấy**, vì lực thật gần như không làm Gaygor nhúc nhích.
2. **Bước chân khi bị đẩy:** đã chọn **tự bước**, có công tắc, mặc định bật (tắt thì chỉ gợi ý).
3. **Chùy khi ragdoll:** đề xuất **mặc định giữ trong tay**, có nút buông chùy từ một frame.
4. **Giới hạn khớp:** đề xuất **đo từ các clip đã duyệt + 20 %**, chỉnh theo giải phẫu, bạn kiểm bằng mắt trên trang trước khi dùng cho bước 2.
5. **Thứ tự:** làm 1 → 2 → 3, mỗi bước bạn thử trên trang rồi mới sang bước sau. Bản thiết kế duyệt một lần cho cả ba.

## 11. Đã làm: bước 1 (2026-10-25)

Có trên trang Pose Lab của Hit, Attack 50 và Walk, trong bảng Vật lý, mục **Tác động**. Walk là clip lặp nên chỉ hiện ghi chú, không đặt tác động được.

**Cách dùng**
- **Đặt tác động:** bấm **+ Tác động** rồi bấm lên người. Điểm bám vào điểm bề mặt gần nhất, phía trước nhất trong vòng 14 px.
- **Hướng lực:** chọn trong bảng (vuông góc bề mặt, từ trước, từ sau, từ trái, từ phải, từ trên xuống), hoặc bấm **Kéo hướng lực** rồi bấm hay kéo trên màn hình ở chỗ lực đến.
- **Mức lực:** 4 mức, hoặc chỉnh tay Frame, Đẩy (m/s), Thời gian (frame), Phóng đại.
- **Hiển thị:** dải cam "Tác động" trên timeline (nhạt là đang tự bước), mũi tên cam trên model, vòng trên sàn ở chỗ đặt chân. Vòng đỏ là chỗ cần bước khi tắt tự bước.
- **Thông tin:** dòng báo khối lượng (~1309 kg), động lượng tương đương ngoài đời, các bước, "cần bước", "ngã".
- **Lưu:** trong `phys.impacts`, `phys.autoStep` và `phys.tone`. Bake như các lò xo.

**Khác với bản thiết kế (do đo được khi làm)**
- **Độ gồng 0,6.** Phản ứng là trộn 60 % "cả người như một khối cứng" với 40 % "khớp thả lỏng". Cả hai đầu đều giữ đúng tổng động lượng. Khớp thả lỏng hoàn toàn làm ngực văng khoảng 10 m/s trong khi hông gần như đứng yên.
- **Hông dùng mô hình con lắc ngược, không dùng lò xo.**
  - Chân chỉ đẩy được tâm áp lực trong phạm vi bàn chân, cộng 8 cm khi gập hông hoặc vung tay.
  - Lò xo hông nuốt mất cú đẩy 5 m/s nên không bao giờ phải bước.
  - Trọng tâm nhận đúng tốc độ j/M, còn thân xoay quanh trọng tâm.
- **Chỉ bước vì phần cú đánh thêm vào.** Trang chỉ bước khi điểm bắt ra ngoài chân hơn chính anim gốc quá 5 cm, vì Hit tự bước lùi trong anim.
- **Chọn chân theo dự đoán.** Với mỗi chân, tính chỗ điểm bắt sẽ tới lúc chân đó đặt xuống (chỉ còn chân kia đỡ, điểm bắt chạy xa theo e^(ω t)), rồi chọn chân bước ngắn nhất.
  - Bản đầu nhấc nhầm chân đang chịu sức nặng của tư thế so le, nên người đổ về phía đó.
  - Bước dài hơn 2 lần sải tối đa (1,6 m) thì báo **ngã** ngay.
  - Thời gian bước là 8–10 frame.
- **Giới hạn tốc độ ban đầu của mỗi khớp,** để biên độ dao động vừa bằng giới hạn góc (thân 20°, đầu 30°, tay 35°, xoay hông 18°). Giới hạn theo góc thì đầu bị kẹp cứng ở 30° vì nhận tới 56 rad/s.
- **Lò xo giai đoạn 1** (tay phải, chùy) nhận tốc độ xoay của khúc chứa nó, cũng bị giới hạn như trên. Tay trái đang cầm chùy theo vai thì đi theo chùy.

**Nghiệm thu (Hit polish_v7, Attack polish_v3, chỉ trên máy, đã xóa)**
- **Khối cứng:** khóa mọi khớp thì tốc độ xoay và tốc độ hông trùng công thức khối cứng, sai số 0 %. Tổng động lượng sau tác động bằng j, sai số 0 % ở mọi độ gồng.
- **Điểm đánh:** cùng mức Vừa, đánh hông thì hông dời 2,0 m/s, đầu quay 0,6 rad/s. Đánh đầu thì đầu quay mạnh nhất, hông chỉ dời 0,24 m/s.
- **Hồi về:** góc đầu so với anim gốc là 0 → 15 → 16 → 5 → 3 → 5 → 2 → 0 (mỗi 2 frame), về 0 trước cuối clip, không rung.
- **Bước chân** (đánh ngực Hit F10 từ phía trước):

  | Mức | Kết quả |
  |---|---|
  | Nhẹ | không bước |
  | Vừa | một bước 48 cm (F20–30) rồi đứng lại |
  | Mạnh | một bước rồi báo ngã (F19) |
  | Hất văng | 3 bước, chưa giữ được |

  Đánh Vừa từ bên phải hoặc ở F4 cũng một bước rồi đứng lại. Tắt tự bước thì báo "cần bước F20, chân phải".
- **Không lỗi mới:** không lún sàn, không xuyên thân, không lỗi cân bằng mới (lỗi cổ tay phải–gối F13 có sẵn từ lò xo cũ). Chân đã đặt không trượt (0,00 cm).
- **Python:** `tools/physics_sim.py --impact` cho cùng kết quả với trang.
  - Lời giải: lệch dưới 2e-6 m/s.
  - Hông và chân từng frame: lệch dưới 0,001 cm.
  - Các bước, "cần bước", ngã: giống hệt.
  - Tư thế thân: lệch 0,0002°.
  - `--compare` với lò xo nhận tốc độ: lệch dưới 0,001°.
  - Mẫu kiểm: `phys_check/hit_imp_two.json` (2 tác động, 3 bước), `hit_imp_parts.json`.
- **Thời gian:** 100–150 ms (Hit 32 frame), 243 ms (Attack 68 frame, có lò xo).

**Chưa làm ở bước 1**
- Mũi tên kéo trực tiếp trong không gian 3D. Hiện đặt hướng bằng cách bấm hoặc kéo trên màn hình.
- Tự bước không xét va chạm giữa hai chân trong lúc bước, chỉ giữ khoảng cách ngang tối thiểu 20 cm. Quét va chạm sau đó vẫn báo nếu có xuyên.

## 12. Đã làm: bước 2, ragdoll (2026-10-25)

Có trên trang Pose Lab của Hit, Attack 50 và Walk: bảng Vật lý, mục **Ragdoll**. Walk là clip lặp nên không bật được.

**Cách dùng**
- Bấm **Ragdoll: bật**. Ragdoll bắt đầu ở frame đang xem, hoặc ở frame của tác động gần đó; sửa được ở ô "từ F".
- **Đồ thị Sức:** kéo điểm, bấm chỗ trống để thêm, bấm đúp để xóa. Mặc định 100 % → 20 % sau 6 frame → 0 % sau 20 frame.
- **Dải "Sức" trên timeline:** cam càng đậm càng nhiều sức.
- **Hệ số theo nhóm:** Thân, Tay, Chân (0–150 %).
- **Buông chùy ở F đang xem**, bấm lại để bỏ.
- **Kéo dài clip tới lúc nằm yên:** chạy thử thêm 90 frame rồi đặt độ dài clip bằng frame nằm yên + 4. Phần thêm giữ key cuối và được lưu trong `phys.rag.len`.
- **Hiện giới hạn khớp:** khung cam là vùng cho phép (gập × dang) của khớp đang chọn, đường xanh là hướng hiện tại, kèm dòng chữ ghi các khoảng góc.
- **Dòng thông tin:** frame nằm yên, lún sàn tối đa, vượt giới hạn tối đa ở khớp nào.
- Bake như các lớp vật lý khác. Tác động ở frame ragdoll trở đi đẩy thẳng vào ragdoll; tác động trước đó vẫn đi qua bước 1.

**Bộ giải**
- XPBD, 20 bước con mỗi frame. Mỗi khúc là lõi con nhộng của giai đoạn 2.
- **Khối lượng:** tối thiểu 4 kg, quán tính tối thiểu 0,02 kg·m². Lõi cổ chỉ 0,3 kg từng làm cổ quay loạn.
- **Cổ** đi theo ngực; đầu nối thẳng vào ngực, giới hạn bằng cổ cộng đầu.
- **Chùy trong tay** là một phần của khối bàn tay (gộp khối lượng và quán tính). Buông thì tách ra, giữ đúng vận tốc lúc đó.
- **Cơ:** kéo mỗi khớp về góc của pose key, độ mềm = 1e-6 / sức³. Sức 100 % giữ pose, lệch 2–4° vì trọng lực; sức 20 % sụp một nửa.
- **Giới hạn khớp:**
  - Đo trên Hit (polish_v7, b75_v2, k10_v1) và Walk anim_v1, nới 20 %, gộp với giải phẫu.
  - Khuỷu gập 0–145°, gối 0–150° tính từ thẳng.
  - Mỗi bước con giải 2 vòng (giới hạn trước, vị trí khớp sau).
  - Tư thế lúc bắt đầu luôn được cho phép.
  - Khớp nào lúc bắt đầu đã lệch quá 90° so với tư thế nghỉ thì đo giới hạn quanh tư thế bắt đầu.
- **Sàn:** điểm bề mặt; nảy 15 %; ma sát trượt 0,6 và ma sát tĩnh.
- **Va chạm giữa các khúc** (và chùy đã buông với thân): chỉ ở mức vận tốc, có khoảng lún cho phép 5 mm.
- **Hãm:** ma sát khớp 8/s, hãm lăn khi chạm sàn 12/s, khớp chạm giới hạn bị hãm mạnh (100/s).
- **Ngủ:** thân mềm chậm hơn 2,5 cm/frame liên tục 6 frame thì đứng hẳn; có lực mới hoặc sức tăng thì tỉnh lại.

**Những lỗi đã gặp và cách sửa (để không lặp lại)**

| Hiện tượng | Nguyên nhân | Cách sửa |
|---|---|---|
| Thân nằm mềm tự bật lên 1,45 m (Attack) | Các ràng buộc đẩy vị trí (va chạm thân, giới hạn khớp) giằng co trong vòng khớp kín, cú đẩy biến thành vận tốc | Mỗi ràng buộc một chiều có bước vận tốc riêng: tốc độ tách ra không lớn hơn trước khi chạm |
| Năng lượng tăng 11–29 kJ khi rơi tự do | Khuỷu trái của Attack lúc bắt đầu đã lệch gần 180° so với nghỉ (tay xoắn 180°, gập ngược); ở đó phép tách gập/dang/xoắn suy biến | Đo góc liên tục theo thời gian; khớp lệch quá 90° thì đo giới hạn quanh tư thế bắt đầu |
| Tăng số bước con làm tệ hơn (tới 105 kJ) | Dấu hiệu chỗ sinh năng lượng tính theo bước con, không theo thời gian | Dùng để khoanh vùng lỗi |
| Chùy 170 kg hàn vào tay 19 kg làm bộ giải bơm năng lượng | Chênh lệch khối lượng quá lớn | Gộp chùy vào khối bàn tay khi còn cầm |
| Thân nằm rung 2–9 cm/frame mãi | Khớp tì sát giới hạn kẹp đi kẹp lại ở mép | Hãm khớp ở giới hạn + cơ chế ngủ |

**Nghiệm thu (Hit polish_v7, Attack polish_v3, chỉ trên máy, đã xóa)**
- **Rơi tự do** (sức 0 %, nâng 20 m): trọng tâm rơi đúng 9,81 m/s², sai số 0 %.
- **Sức 100 %** giữ pose (lệch 2–4°); **0 %** đổ và nằm.
- **Không sinh năng lượng:** 0 kJ ở mọi ca không có cơ. Có cơ thì cơ tự làm công, ví dụ 3,8 kJ khi đứng lên theo key.
- **Giới hạn khớp:** vượt tối đa 0,4–2,7°. Có 2 ca nhỉnh hơn 2° một chút: Attack F20 (2,7°) và Hit buông chùy (2,1°).
- **Lún sàn:** tối đa 0,3 cm.
- **Lắng sau khi chạm đất:**

  | Ca | Thời gian |
  |---|---|
  | Hit từ F10 | 0,87 s |
  | Hit từ F16 | 0,80 s |
  | Hit từ F4 | 1,17 s |
  | Hit, đường Sức mặc định | 1,00 s |
  | Hit, buông chùy | 1,13 s |
  | Attack từ F6 | 0,73 s |
  | Attack từ F20 | 0,63 s |
  | Attack từ F45 | 1,07 s |

  Riêng Attack bắt đầu từ F30 thì đang giữa cú lao (trọng tâm 6–7 m/s ngay trong anim), nên trượt xa và chưa nằm yên trong 90 frame. Đây là đúng vật lý.
- **Đổ cứng so với gói ngã/chết:**
  - Khóa cứng mọi khớp, đánh ngực Hit F3 từ trước.
  - Kết quả: Vừa ×1,5: 15 / 14,8 frame (đạt). Vừa: 11 / 12 (lệch 1). Nhẹ: 11 / 13,3 (không đạt).
  - Nguyên nhân: gót chân trượt 5–7 cm và nhấc lên, trong khi đường tham chiếu giả định gót đứng yên làm trục.
  - Bán kính quán tính thật của Gaygor là 0,61 m (chùy trên lưng), không phải 0,3 m như gói ngã/chết đang dùng.
- **Thời gian tính:** 0,2–0,45 s cho 90 frame (Hit, Attack).
- **Python:** `tools/physics_sim.py --ragdoll` chạy cùng bộ giải trên trạng thái ban đầu và đầu vào từng frame do trang ghi lại (`window.__ragRec`).
  - Trùng tuyệt đối mọi frame, kể cả lúc va chạm (0,00000 cm, 0,00000°).
  - Đổi số bước con 20 → 19 thì lệch 43 cm, nên phép so là thật.
  - Mẫu: `phys_check/rag_hit_death.json`, `rag_hit_release.json`.

**Chưa làm ở bước 2**
- Bản Python chưa dựng lại ragdoll từ pose; nó nhận trạng thái ban đầu từ trang.
- Va chạm chùy–thân khi chùy còn trong tay bị tắt (chùy tì vai là cố ý).
- Chưa có giới hạn riêng cho Attack: blocking của team có tay trái xoắn 180°.

## 13. Đã làm: bước 3, ragdoll có cơ (2026-10-25)

Có trên trang Hit, Attack 50, Walk, cùng mục **Ragdoll** của bước 2.

**Mới thêm**
- **Pose phản xạ:** cơ kéo mỗi khớp về pose key của từng frame (đã có từ bước 2). Muốn tay đưa ra đỡ, co người, ngẩng đầu thì key tư thế đó trong anim; ragdoll cố đạt nó theo sức.
- **Sức riêng 6 phần:** Thân, Đầu, Tay trái, Tay phải, Chân trái, Chân phải (0–150 %), nhân với đường Sức. Cấu hình cũ (Tay, Chân) vẫn đọc được.
- **Giữ thăng bằng:**
  - Điều kiện: còn sức ở chân, có bàn chân chạm sàn, và điểm bắt của cả người còn trong vùng bàn chân (cộng 8 cm gập hông).
  - Khi đủ điều kiện, hông được kéo về hông của pose key (cả hướng xoay và vị trí trên mặt sàn), mạnh theo sức chân. Tốc độ đẩy bị giới hạn ở mức ma sát chân đẩy được cả người (μg).
  - Ra ngoài vùng chân thì không có gì giữ, và thân ngã.
- **Dòng "Còn sức nhưng chân không giữ nổi từ F… (cần bước)":** chỉ hiện khi điểm bắt ra ngoài 3 frame liền và sau đó trọng tâm hạ quá 25 cm. Khi đứng yên, vùng đỡ dao động nhẹ không gây báo nhầm.
- **Vùng đỡ:** mọi điểm đế chân cách sàn dưới 2 cm. Bản đầu chỉ lấy 1–3 điểm vừa lún, nên thân đứng yên vẫn bị coi là ra ngoài 30–40 cm.

**Nghiệm thu (Hit polish_v7, ragdoll từ F30 = tư thế Idle, clip kéo dài; chỉ trên máy, đã xóa)**

| Trường hợp | Kết quả |
|---|---|
| Sức 100 %, không đẩy | đứng vững suốt 60 frame, không báo nhầm |
| Sức 100 %, đẩy Nhẹ vào ngực | đứng vững |
| Sức 100 %, đẩy **Vừa** từ **bên hông** | loạng choạng (điểm bắt ra mép vài frame) rồi đứng lại, không chạm đất |
| Sức 100 %, đẩy **Vừa** vào ngực từ **phía trước** (ngửa ra sau) | điểm bắt ra ngoài gót 30 cm trở lên, ngã, báo cần bước F36 |

- **Ca đẩy Vừa từ phía trước không đạt** điều kiện "loạng choạng rồi đứng lại" của bản thiết kế. Đây là đúng vật lý: 1 m/s ra sau vượt sức giữ của mắt cá và hông với thế đứng này. Bước 1 cũng cho kết quả là phải bước một bước. Ngưỡng tự đứng lại khi bị đẩy ra sau nằm giữa Nhẹ (0,3 m/s) và Vừa (1 m/s).
- **Phản xạ:** chỉ tay có sức (thân và chân 0 %), bị đẩy ngã. Trước khi chạm đất, tay lệch khỏi pose key tối đa:

  | Sức tay | Lệch tối đa | Đạt (< 10°)? |
  |---|---|---|
  | 100 % | 2,1° | đạt |
  | 60 % | 4,9° | đạt |
  | 30 % | 15,1° | không |
  | 0 % | 97° | không |

- **Python:** `tools/physics_sim.py --ragdoll` có thêm phần giữ thăng bằng. Trùng tuyệt đối với trang ở cả 4 ca: giữ thăng bằng, phản xạ, cú chết, buông chùy. Mẫu: `phys_check/rag_hit_balance.json`, `rag_hit_reflex.json`, `rag_hit_death.json`, `rag_hit_release.json`.

**Chưa làm**
- Tự bước khi ragdoll còn sức. Tự bước hiện chỉ có ở bước 1 (lớp cộng lên anim).
- Lực giữ thăng bằng tác động lên hông như một lực tổng (giới hạn theo μg), chưa phân ra mô-men ở từng cổ chân.

## 14. Sửa sau khi dùng thật (Gaygor Die, 2026-10-25)

- **Điểm chạm sàn của ragdoll:** dùng **mọi điểm bề mặt** của từng khúc (60–290 điểm), thay cho 22 điểm lấy đều.
  - Với 22 điểm lấy đều, Gaygor nằm ngửa bị lún 7–10 cm giữa các điểm (giáp, hông).
  - Lấy 40 hay 80 điểm theo kiểu "xa nhau nhất" vẫn còn lún 3–4 cm.
  - Dùng mọi điểm: lún 0 cm, chùy 0 cm. Thời gian tính khoảng 0,67 s cho 52 frame.

## 15. Ma sát sàn tính theo xung (2026-10-26, Die b50)

- **Lỗi:** ma sát cũ được tính như một thay đổi vận tốc, rồi chia cho khối lượng hiệu dụng của điểm chạm. Ở xa trọng tâm, ma sát yếu đi 3–5 lần, nên Gaygor nằm ngửa vẫn trượt tới 2 m.
- **Sửa:** tách làm hai bước.
  - Pháp tuyến: nảy 15 %, không bật lên.
  - Ma sát trượt: một xung dọc hướng trượt, không vượt quá μ_d × xung pháp tuyến (fn·h). Xung chỉ đủ để dừng vận tốc trượt, không đảo chiều.
  - Sửa ở cả trang lẫn bản Python `rag_frame`.
- **Kiểm:**
  - `phys_check/rag_die_b50.json` (Die b50: ragdoll từ F20, buông chùy F23, đẩy gối F42) trùng trang tuyệt đối, tối đa 0,0001 cm.
  - Bốn mẫu `rag_hit_*.json` ghi trước khi sửa nên lệch 16–55 cm từ F11–34. Cần ghi lại khi mở trang Hit lần tới.

## 16. Nút × không xóa được tác động (2026-10-26, user "không xóa được tác động")

- **Nguyên nhân:**
  - Bấm × thì tác động được xóa trên máy và hẹn lưu sau 0,7 s.
  - Trong lúc đó, bản lưu trước (lúc kéo thanh trượt) từ db quay về muộn, khác `animAt`, nên `applyRemote` chép đè `ANIM.phys` bằng bản cũ: tác động hiện lại và được lưu lại.
  - Nút × còn xóa trên mảng đã chụp lúc vẽ dòng (`L`). Khi `ANIM.phys` bị thay bằng bản db, nút xóa nhầm mảng.
- **Sửa:**
  - `applyRemote` bỏ qua bản db cũ hơn `animAt` trên máy, và không nhận bản db khi đang lưu (`flushing`).
  - Nút × của tác động, khớp lò xo và vùng chắn xóa trên `ANIM.phys` hiện tại: theo đối tượng, nếu không có thì theo frame + bộ phận, hoặc theo xương.
- **Kiểm (trang trên máy):**
  - bấm × thì xóa ngay;
  - bản db cũ tới muộn không đưa tác động quay lại;
  - thay đổi mới hơn của người khác vẫn được nhận;
  - bấm × lần nữa vẫn xóa được.

## 17. Ragdoll "Về đích" (2026-10-26, user: 2 key Idle + nằm, vật lý phải kết thúc đúng pose người dùng)

Bật ở bảng Ragdoll: **Về đích: bật** (đích = key cuối) và **Tìm cú đổ**. Cài đặt nằm ở `ANIM.phys.rag.goal`:

| Trường | Ý nghĩa |
|---|---|
| `on` | bật chế độ Về đích |
| `gs` | sức kéo về đích, 0,6 |
| `ramp` | số frame tăng sức sau khi chạm sàn, 12 |
| `rate` | tốc độ tối đa mục tiêu đi về pose cuối, 4°/F |
| `blend` | số frame trộn cuối, 10 |
| `push` | cú đẩy tìm được: {vx, vz, wy} |
| `f` | frame đích; mặc định là key cuối |

1. **Cú đẩy ban đầu (bước 1).**
   - Ở frame bắt đầu ragdoll, mọi khối nhận thêm vận tốc v + ω × (x − trọng tâm). Có ba số: vx, vz (m/s) và wy (rad/s quanh trục đứng).
   - "Tìm cú đổ" chạy ragdoll nhiều lần. Mỗi lần đo chỗ nằm lệch so với key cuối: dx, dz và xoay dyaw của hông.
   - Trước tiên chỉnh cú đẩy ngược theo phần lệch đo được (lệch / thời gian tới lúc chạm sàn), hệ số tự tăng khi tốt hơn, tự giảm khi tệ hơn. Sau đó dò tinh từng bước nhỏ. Tối đa 60 lần chạy.
   - Chỉ dò từng bước nhỏ từ cú đẩy 0 thì kẹt ở cú ngã sấp: lệch 141 cm, 149°.
2. **Cơ kéo về pose cuối (bước 2).**
   - "Chạm sàn" là khi ngực xuống thấp hơn độ cao ngực của key cuối + 15 cm.
   - Từ lúc đó, mục tiêu của cơ đi từ góc khớp hiện tại tới góc khớp của key cuối, mỗi frame tối đa `rate`. Sức tăng thêm `gs` theo smoothstep trong `ramp` frame.
   - Đổi mục tiêu ngay một lúc thì bàn chân bị quất 65–120°/F.
   - Thân vẫn chịu sàn, giới hạn khớp và va chạm. Người không "ngủ" khi cơ còn sức.
3. **Trộn phần dư (bước 3, `ragGoalFinish`).**
   - Đo phần lệch còn lại ở frame đích: hông (cm), thân xoay (°), khớp lệch nhiều nhất. Số này hiện trên trang.
   - Sau đó trộn local mọi xương về key cuối trong `blend` frame, theo smoothstep. Thân, rồi riêng từng prop (chùy là xương riêng), được nâng lên nếu lún sàn. Frame đích và sau đó = key cuối.
- **Kết quả thử** (Die 2 key: F1 Idle, F72 pose nằm đã duyệt; ragdoll từ F4, buông chùy F10):

  | | Không có Về đích | Có Về đích, chưa tìm cú đổ | Sau Tìm cú đổ |
  |---|---|---|---|
  | Hông lệch | — | 225 cm | 0,3 cm |
  | Thân xoay lệch | — | 18° | 2,1° |
  | Tay chân lệch | — | 0,3° | 0,2° |

  - Tìm cú đổ: 36 lần chạy, 29 giây.
  - Chạm sàn F20, nằm yên F47. Hông đứng yên ở F60–72, không lún sàn.
  - Trang báo "lệch lớn" khi hông lệch quá 30 cm hoặc thân xoay quá 30°.
- **Bản Python** (`phys_check/rag_die_goal.json`): cùng logic với trang.
  - F1–30 lệch dưới 1e-4 cm.
  - Sau đó lệch lớn dần tới 0,35 cm ở F72. Lúc nằm mà cơ vẫn đang kéo, sai số làm tròn bị khuếch đại.
- **Còn lại:** chân nảy tới 49°/F lúc lưng đập sàn (vật lý). Tay khiên lấn chân phải 4–9 cm ở F17–32, vì va chạm giữa các khối chỉ chặn vận tốc (giống ragdoll thường).

### 17b. Về đích v2 (user "hơi cứng và thiếu tự nhiên" trên goal_v1)

**Lỗi đo được trên goal_v1:**
- F4–F12 người đứng im, rồi đổ như một khối. Khuỷu phải giữ 146° suốt, đầu và vai chỉ 1–3°/2F.
- Sau khi chạm sàn, người tự "tạo dáng" đều một tốc độ: gối phải 121 → 164°, lưng 20 → 59° trong F26–36, hông bị đẩy lên 10 cm.
- Từ F38 đứng im hẳn.

**Sửa:**
- Khi bật Về đích, đầu (0,4), tay trái và tay phải (0,6) lỏng hơn thân, nên trễ và văng theo khi đổ.
- Trong lúc rơi, mục tiêu của cơ nghiêng dần về key cuối (`pre` 0,5 trong `preF` 16 F, sức thêm `preS` 0,12).
- Sau khi chạm sàn, từng khớp đi tới key cuối theo smoothstep:
  - thời gian = góc / 3°, trong khoảng 6–22 F;
  - trễ theo nhóm: thân 0, chân 2, tay 3, đầu 5 frame;
  - sức `gs` 0,35, không nhân với độ lỏng của nhóm.
- Xong thì buông trong `letGo` 10 F, giữ trương lực `hold` 0,25. Buông về 0 thì đầu ngoẹo lệch key cuối 80°.
- Phần dư trộn trong lúc lắng (chạm sàn + 4 → lúc nằm yên), sau đó giữ đúng key cuối. Trộn ở 10 frame cuối thì người đang nằm yên 20 frame lại nhúc nhích 4–7°/F.
- Điểm khi dò có thêm độ lệch của prop đã buông (0,2 × độ). Nếu prop lệch quá 15°, "Tìm cú đổ" thử thêm frame buông ±2 và ±4 quanh frame người dùng đặt.
  - Die: chỉ dò cú đẩy thì chùy vẫn lệch 48°. Thử thêm frame buông thì ra F6 (sớm hơn 4 frame), chùy lệch 11,7°.

**Kết quả** (63 lần chạy, 53 giây):
- Hông lệch 2,2 cm, thân xoay lệch 1,5°.
- Tốc độ khớp lớn nhất 22°/F (v1: 49).
- Sau khi chạm sàn chuyển động giảm dần 22 → 11 → 6 → 2 → 0,3°/F, nằm yên F41.
- Bản Python khớp trang tuyệt đối (0,00001 cm). Có trương lực giữ lại nên sai số làm tròn không còn bị khuếch đại.
- Còn lại: tay khiên lấn cổ chân phải tới 9 cm ở F26 (va chạm thân chỉ chặn vận tốc).

### 17c. Về đích v3: lỏng, khớp theo % (user "không nhất thiết phải giữ đúng pose cuối 100%... như một bức tượng đá đổ xuống")

- **Key cuối giờ chỉ là hướng nhắm.**
  - Lực kéo yếu: `gs` 0,15, `pre` 0,3, `preS` 0,04, `hold` 0 (không giữ trương lực).
  - Khi bật Về đích, nhóm mặc định: đầu 0,15, tay 0,3, chân 0,5. Gối khuỵu, đầu và tay buông.
  - Thanh **Khớp pose cuối** (`match`, mặc định 50 %): phần dư chỉ trộn theo tỉ lệ đó. 0 % = để nguyên vật lý, 100 % = đúng key cuối.
- **Đường Sức của bản thử goal_v1** đổi thành 70 % ở F4 → 15 % ở F8 → 0 ở F14 (trước: 100 → 30 → 0 ở F20). Sức mất chậm cũng làm người đổ như tượng.
- **Đo được** (39 lần chạy, 30 giây; hông lệch 0,8 cm, thân xoay lệch 4,8°):
  - gối trái 113 → 70° ở F12, hông tụt 68 → 38 cm (người sụp xuống rồi mới ngã ngửa);
  - đầu ngoẹo 20–40° mỗi 4 frame, chân phải hất lên khi lưng chạm sàn;
  - F48–57 đầu tự ngoẹo sang bên rồi nằm yên.
- **Còn lại:** tay khiên lấn gối và cổ chân phải 3–7 cm trong lúc khuỵu (F8–23), vì va chạm giữa các khối chỉ chặn vận tốc.

## 18. "+ Tác động" bấm trúng người mà không thêm được (2026-10-26, user "Sao tôi không thêm được tác động nhỉ")

- **Nguyên nhân:** điểm bề mặt thưa (ngực Gaygor có 182 điểm, trên màn hình cách nhau hơn 28 px). Bấm chỉ được nhận khi cách một điểm dưới 14 px, nên bấm giữa ngực (cách điểm gần nhất 14,5 px) bị báo "không trúng".
- **Sửa (`impPickAt`):** lấy điểm gần chỗ bấm nhất trong vòng 45 px. Trong các điểm gần ngang nhau (thêm tối đa 12 px), chọn điểm gần camera nhất.
- **Kiểm (bấm chuột thật trên trang):**
  - bấm ngực ở góc phải thì đặt vào cánh tay phải, vì tay khiên che trước ngực;
  - bấm đầu chùy thì đặt vào chùy;
  - bấm chỗ trống thì vẫn báo không trúng.

## 19. Dữ liệu db bị khóa trên claude.ai: thêm / xóa tác động lỗi (2026-10-26, user "Vẫn ko được")

- **Nguyên nhân thật** (đọc được nhờ bắt lỗi ở dòng trạng thái trên trang live): `Cannot add property 0, object is not extensible at Array.push at impPickAt`.
  - Trên claude.ai, dữ liệu từ db (onSnapshot) là đối tượng bị đóng băng. `applyRemote` gán thẳng `ANIM.phys = an.phys`, nên mọi push / splice lên `impacts`, `parts`, `colliders` đều ném lỗi giữa chừng.
  - Thêm tác động: nút vẫn xanh, không có gì xảy ra.
  - Xóa tác động: rất có thể cũng do lỗi này (mục 16).
  - Trang chạy trên máy không có db nên không gặp.
- **Sửa:** `applyRemote` dùng bản chép `JSON.parse(JSON.stringify(an.phys))`. Bấm "+ Tác động" mà gặp lỗi thì dòng trạng thái hiện lỗi kèm vị trí.
  - Một lần sửa trung gian lỡ tạo một xuống dòng thật trong chuỗi JS, làm cả trang Die không chạy trong vài phút; đã sửa.
- **Kiểm trên trang live claude.ai** (bấm chuột thật):
  - thêm tác động thì "Đã đặt tác động ở hông, F1" và có mũi tên trên người;
  - bấm × thì xóa được;
  - db lưu đúng, `impacts` rỗng.
- **Bài học:** dữ liệu db trên artifact luôn phải chép ra trước khi sửa. Mọi thay đổi chạm db phải thử trên trang live, không chỉ trên bản ở máy.

### 17d. Về đích "chỉ dáng" là mặc định (2026-10-26)

Bạn: "Với về đích 2 frame chỉ lấy pose chứ không lấy theo root. Khi bật tác động, lực đẩy nhân vật đi xa hơn vị trí pose cuối, khi đó cả body bị kéo ngược lại 1 đoạn".

- **Chỉ dáng (mặc định):**
  - hông giữ nguyên chỗ và hướng do vật lý (và tác động) đưa tới; vật đã buông (chùy) nằm nguyên chỗ rơi;
  - chỉ các khớp trộn về key cuối, theo thanh Khớp pose cuối;
  - cú đẩy (`vx`/`vz`/`wy`) vẫn giữ nguyên (xem 17e);
  - "Tìm cú đổ" chỉ dò hướng xoay và chùy, không dò chỗ nằm;
  - không báo "lệch xa" theo chỗ nằm.
- **Dáng + vị trí** (nút **Đích:**): như trước, cả hông kéo về chỗ của key cuối.
- Cài đặt nằm ở `ANIM.phys.rag.goal.root`, nhận `"pose"` (mặc định) hoặc `"full"`.
- **Đo trên goal_v1 có tác động vừa ở ngực F5:** trong đoạn trộn, hông bị kéo ngược 1,65 cm/F ở chế độ dáng + vị trí, còn 0,35 cm/F ở chế độ chỉ dáng (phần đó là nâng khỏi sàn). Người nằm đúng chỗ cú đánh đưa tới.
- **Lỗi gặp khi làm:** lần đầu chùy đã buông vẫn bị đặt theo hông như trong key, nên đứng thẳng lơ lửng cạnh người. Vật đã buông thì giữ kết quả vật lý.

### 17e. Chỉ dáng giữ cả cú đẩy (2026-10-26)

Bạn: "Cái bạn sửa không đúng trọng tâm lắm. nó làm mất cả lực tác động ban đầu".

- **Nguyên nhân:** bản 17d bỏ `vx`/`vz` của cú đẩy ở chế độ chỉ dáng. Cú đẩy cộng vào lực của tác động, nên bỏ nó đi thì người bay ít hơn hẳn.
- **Sửa:** cú đẩy dùng đủ ở cả hai chế độ. Chỉ dáng chỉ còn một tác dụng: đoạn trộn cuối không kéo hông về. "Tìm cú đổ" ở chế độ chỉ dáng vẫn không đổi `vx`/`vz`.
- **Đo trên goal_v1 của bạn** (tác động F1 đầu, mạnh ×0,8; thanh F4; đẩy vz −2,26):

  | Bản | Hông Z (cm) F10 / F30 / F40 / F72 |
  |---|---|
  | dáng + vị trí | −97 / −238 / −240 / −213 (kéo ngược 27 cm) |
  | chỉ dáng 17d | −46 / −87 / … / −101 (mất cú đẩy) |
  | chỉ dáng 17e | −97 / −250 / −280 / −280 (đi một chiều, không kéo ngược) |

- Đường đi của hông giống nhau tới F20 ở cả hai chế độ. Bật hay tắt AutoPhysics traj 100 không đổi kết quả này.
