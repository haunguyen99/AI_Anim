# Director log – windy_attack

## Director – windy_attack analysis.md (bản 2026-11-05) – mốc analysis – 2026-11-05
**Kết luận: Cần sửa** (không Chặn: hướng đòn đúng FDD và ref, nhịp 24F/bắn F9 đúng quyết định đã chốt)
Ý chính: Ý đồ rõ: vung trượng qua đầu rồi chĩa ngang ra trước như cầm giáo, bắn ở F9. Nhưng bảng pha vẫn tính theo dáng Idle cũ (trượng dựng đứng). Từ dáng chéo 45° user chỉnh, chưa có đường đi của trượng lúc lấy đà và lúc về. Vài pose then chốt cũng chưa tính được với tay và chân chibi: tay phải không với ra sau gáy được, tay trái không với tới cán, thế tấn không tới được nếu không bước.

### Cần sửa (nặng → nhẹ)
| # | Mức | Ở đâu (frame) | Đang thấy | Nên thấy / sửa thế nào |
|---|---|---|---|---|
| 1 | A | Trượng, F0→F5 và F13→F24 | Bảng chỉ ghi "nhấc trượng lên, kéo ra sau đầu" và "kéo về dáng chéo 45°". Không nói đầu trượng đi đường nào từ dáng chéo (đầu trượng đang ở trước-trái-trên, đuôi gần chạm đất bên phải, cách ~1 m) | Vẽ rõ đường đầu trượng và đuôi trượng ở từng key. Lúc đi: đuôi nhấc khỏi đất trước, đầu trượng vòng qua đâu, bên trái hay bên phải đầu. Lúc về: đuôi hạ xuống bên phải mà không quét qua chân phải, không cắm đất |
| 2 | A | Tay phải, F5 (đỉnh lấy đà) | Thiết kế muốn tay phải cao ~1,5 m, ở sau vai, trượng dựng sau gáy như ref. Tay chibi dài ~46 cm, đầu rộng 50 cm, nên tay phải duỗi thẳng và vặn vai ra sau mới tới. Tay sẽ xuyên đầu hoặc mũ. Nhìn từ trên, trượng dựng đứng chỉ còn một chấm bị đầu che | Bỏ kiểu "dựng sau gáy". Cho tay phải lên cạnh tai phải (~1,3 m), trượng ngả ra sau ~45°, đầu trượng chĩa lên và ngược hướng mục tiêu. Từ trên nhìn xuống, trượng thành một vạch chĩa ra sau, đối nghịch với lúc bắn |
| 3 | A | Tay trái + thân, F7–F13 (cầm hai tay) | Trượng phải nằm ngoài sườn phải để đuôi không đâm thân. Khi đó vai trái tới chỗ đỡ giữa cán xa ~58 cm, dài hơn cả cánh tay. Bảng chưa nói thân phải xoay | Ghi rõ thân trên xoay sang phải bao nhiêu để vai trái đưa lên trước, sao cho tay trái tới cán còn gập khuỷu. Đầu vẫn nhìn thẳng mục tiêu. Tính lại tầm với cho cả F7 (đón cán) |
| 4 | A | Chân + hông, F9 | Muốn hạ hông 8–10 cm, gối trước gập sâu, chân sau duỗi, mà không bước. Hai bàn chân chỉ cách nhau trước-sau ~28 cm. Muốn chân sau duỗi thì hông phải đổ ra trước cả bàn chân trước, nhìn như sắp ngã hoặc ngồi xổm (bài học Ninja: chân ngắn tấn rộng thành ngồi xổm) | Chọn một trong hai. (a) Không bước: hạ hông chỉ ~4–5 cm, gối sau hơi chùng, độ "đổ người" lấy từ thân nghiêng trước. (b) Bàn chân phải trượt lên ~15–20 cm ở F7–F9 rồi về chỗ cũ trong pha về |
| 5 | B | Tay trái, F0 và F24 | Bảng ghi Idle F0 tay trái "thả, FK", nhưng Idle v2/v3 là tay trái chống nạnh. Trượng chéo 45° có đầu ở trước-trái nên có khi tay trái còn đỡ trượng. Chưa đo từ file Idle user chỉnh | Đo lại tay trái ở Idle F0 trong file Windy_Idle.fv, ghi vào mục C. Pha về phải trả tay trái về đúng chỗ đó (chống nạnh thì cần chạm hông chuẩn) |
| 6 | B | Trượng + đầu/mũ, F6–F8 (vung) | "Cung qua bên phải đầu" là ý đúng. Nhưng tay cầm chỉ ở ngoài mép đầu ~5 cm, nên lúc trượng chéo xuống trước, cán sẽ quẹt sát đầu hoặc vành mũ | Ghi khoảng hở tối thiểu giữa cán và khối đầu/mũ (~10 cm) cho cả 3 frame vung, tay cầm đẩy ra ngoài thêm |
| 7 | B | Đầu, cả clip | Không có cột đầu. Đầu chibi là khối to nhất nhìn từ trên | Thêm cột đầu: đầu khoá về mục tiêu suốt đòn, chỉ ngửa nhẹ lúc lấy đà, cúi nhẹ theo cú vung, trễ thân 1–2F |
| 8 | B | Frame bắn cho dev | Bảng đếm từ F0 nên "bắn F9" ở đây là frame thứ 10 trên Studio. Clip ghi F0→F24 là 25 frame, có frame cuối trùng Idle | Ghi một quy ước duy nhất: số frame xuất, và frame bắn theo cả hai cách đếm. Đưa thêm mốc theo tỉ lệ đòn (~0,375) để game co giãn tốc độ vẫn bắn đúng lúc |

Còn vài điểm nhỏ ở mức C (xem ghi chú kỹ thuật).

### Giữ nguyên
- Ý đồ đòn: lấy đà ngắn, vung một cung lớn, đỉnh đòn là trượng nằm ngang chĩa thẳng mục tiêu. Đúng câu FDD "đưa đầu trượng về phía trước", đúng ref GD, từ trên cao đọc bằng một vạch dài.
- Nhịp 5 · 4 · 4 · 11 với bắn F9 hợp với đòn lặp 0,8 s. Bỏ đoạn giữ 14F của ref là đúng. Pha về dài nhất, chậm dần về Idle.
- Vào/ra đúng Idle F0, không trôi chỗ, không đổi dáng cầm của user.
- Ý vải: bị hất ra sau lúc vung, quật về trước sau khi bắn, trễ dần từng đốt.
- Ba câu hỏi mục E đặt đúng chỗ.

### Vòng sau
- Mục D cần có đường đi của trượng từ dáng chéo của user, và 3 pose then chốt (F5, F7, F9) đã tính được với tay và chân chibi. Đọc xong phải hình dung được ngay cái vạch trượng: chĩa ra sau → quét qua bên phải đầu → chĩa thẳng mục tiêu → về chéo.

### Ghi chú kỹ thuật cho animator
- [đo, từ số trong analysis] Trượng Idle F0: tay (−0,20; 0,76; 0,23) → đầu (0,62; 1,56; 0,57), vector dài ~1,20 m. Kéo dài về phía đuôi 1,13 m: đuôi ≈ (−0,98; ~0,00; −0,09), tức đuôi gần chạm đất cách ~1 m bên phải. Pha lấy đà phải nhấc đuôi trước; pha về phải hạ đuôi êm, không cắm đất (khoá y đuôi ≥ 0 mọi frame).
- [đo] #2 tầm với: vai y 1,14, tay 0,23 + 0,225 = 0,455 m. Tay ở y 1,5 và sau vai 0,3 m (để trượng ra khỏi đầu rộng 0,5 m) → cách vai ~0,47 m > 0,455 m: duỗi hết cỡ cộng gập vai ~150° là quá giới hạn khớp. Gợi ý: cổ tay ~(−0,35; 1,30; −0,10), trượng nghiêng sau ~45°. Kiểm `joint_rules` vai/khuỷu.
- [đo] #3: trượng ở x ≈ −0,30 (ngoài sườn phải), điểm đỡ cán ~0,3 m trước tay phải. Vai trái (≈ +0,17; ~1,04; 0) tới (−0,30; 1,00; +0,35): ~0,58 m > 0,455 m. Cần ngực + hông xoay phải ~30–40° (đo lại khi P0). Hệ quả: chân phải trước + tay trái trước là thế vặn ngược (chéo). Xem lại ref xem chân nào trước, tay nào trước, rồi ghi lại.
- [đo] #4: chân hông→cổ chân ~0,56 m. Hông hạ 9 cm → chiều dọc ~0,44 m; chân sau duỗi thì hông phải ở trước cổ chân sau ~0,34 m → z hông ≈ +0,19, trước cổ chân phải (+0,13). Trọng tâm lọt ra ngoài chân đỡ.
- [mắt] Độ cao trượng lúc bắn: bảng ghi ~1,0 m (ngang ngực, khi đã hạ hông là sát vai), trong khi ref "tay sau giữ đuôi sát hông" là ~0,7 m. Chọn một số và ghi rõ, vì nó quyết định khoảng hở với cằm/đầu và với vạt sau lưng.
- [mắt] Đuôi trượng lúc bắn ở ~z −1,0 phía sau, ngang sườn phải: kiểm xuyên hai vạt sau lưng (Idle v2/v3 vạt xoè ra hai bên sau lưng) và áo choàng.
- Tay trái IK bật/tắt giữa clip (F5–F14): bật đúng frame giữ, dùng match FK/IK để không giật, kiểm frame chuyển. Cách khác: để tay trái FK, key tay từng frame F7–F13, đo khoảng cách găng→cán ≤ 1–2 cm mỗi frame.
- Nhịp vung F5→F9: đầu trượng quét ~3 m trong 4F (~0,8 m/F) nên dễ nhấp nháy ở 30 fps. Câu hỏi smear F8 hợp lý. Tối thiểu mỗi frame vung là một vị trí trên cung, không trùng nhau.
- C: Idle `windy_idle/analysis.md` vẫn ghi "chốt PA A, trượng dựng chéo 18°, đuôi chạm đất", lệch dáng chéo 45° user đã chỉnh. Cập nhật để clip khác (Skill1–3) không dựng theo dáng cũ.
- C: Idle 40F đếm từ F1, Attack đếm từ F0. Theo quy ước chung, frame đếm từ 1.
- C: Hướng bay projectile do code (khoá hướng mục tiêu), anim chỉ cần đầu trượng chĩa +Z trong ±5° ở frame bắn. Điểm sinh ở `DEF_WeaponEnd_R` lệch sang phải ~0,3 m, không đáng kể ở cam game; ghi cho dev biết.
- C: Hướng mặt trăng + quả cầu đầu trượng (Idle xoay trượng 90° quanh trục) lúc bắn: ghi giữ hay xoay.
- C: Nên có sẵn một bản tối giản (lấy đà thấp, không qua đầu) phòng khi game tăng tốc đánh lên nhiều lần, cú vung lớn sẽ rối. Để user quyết.
- Thiếu: không có video ref trên máy (`work/endless_kicker/ref/` không tồn tại), không có ảnh. Chấm chỉ dựa trên chữ và số trong analysis, mục B tin theo mô tả của animator.

## Director – windy_attack analysis.md vòng 2 – mốc analysis – 2026-11-05
**Kết luận: Cần sửa** (còn 1 lỗi A, chỉ là chỉnh số, không đổi hướng)
Ý chính: Sửa tốt, 7/8 điểm vòng 1 đã xong. Đường đi trượng giờ đọc được: chĩa ra sau → quét qua bên phải đầu → chĩa thẳng mục tiêu → về chéo. Chỗ chưa ổn nhất vẫn là tay trái đón cán: chỉ xoay ngực 30–40° vẫn chưa đủ tầm, nhất là ở F7.

### Đối chiếu 8 điểm vòng 1
1 đường đi trượng: **Đã sửa**, có bảng key, nhưng F2 sai số (xem #2). · 2 tay phải F5: **Đã sửa** (vai→cổ tay ~0,25 m, trong tầm). · 3 tay trái tới cán: **Chưa đủ** (#1). · 4 chân không bước, hông hạ 4–5 cm: **Đã sửa**. · 5 tay trái Idle F0: **Đã sửa** (thả hờ, đo trên rig). · 6 khoảng hở cán–đầu ≥ 10 cm: **Đã sửa**. · 7 cột đầu: **Đã sửa**. · 8 quy ước frame + tỉ lệ 0,375: **Đã sửa**.

### Cần sửa (nặng → nhẹ)
| # | Mức | Ở đâu (frame) | Đang thấy | Nên thấy / sửa thế nào |
|---|---|---|---|---|
| 1 | A | Tay trái đón cán, F7 và F9 (lặp lại từ vòng 1, mới sửa một nửa) | Tính lại theo bảng mới: ngực xoay 35° và thân nghiêng trước thì ở F9 vai trái tới chỗ đỡ cán vẫn ~0,5 m, ở F7 ~0,65 m, đều dài hơn tay (0,46 m). F7 là lúc trượng còn chĩa lên trước 45° nên chỗ đỡ cán ở cao và xa bên phải | Đo vai trái trên rig rồi chọn: (a) tay trái đón muộn hơn, ở F8 khi trượng gần ngang; (b) tay trái nắm sát tay phải (~15 cm, không phải 30 cm); (c) trượt cán trong tay phải ~10–15 cm về phía đầu trượng như Idle từng làm. Ghi vào bảng con số đã kiểm (≤ 0,42 m để khuỷu còn gập) |
| 2 | B | Trượng, F2 | Ghi cổ tay cao 1,0 m, "trượng dựng gần đứng", đuôi cách đất 0,25 m. Ba số này không đi cùng nhau được: đuôi cách tay 1,13 m, dựng gần đứng thì đuôi xuống dưới đất ~13 cm | Chọn một: nâng cổ tay lên ~1,35 m, hoặc để trượng còn nghiêng ~45° ở F2 (đuôi ra ngoài-sau bên phải) |
| 3 | B | Đuôi trượng, F7 (và F6–F8) | Khi đầu trượng chĩa lên trước 45°, đuôi chúc xuống-sau, cao ~0,35 m, sau lưng ~0,55 m, bên phải. Chỗ này dễ cắt qua vạt sau bên phải. Bảng chỉ kiểm vạt ở F9 | Thêm kiểm "đuôi không xuyên vạt sau, áo choàng" cho cả F6–F8, không chỉ F9. Nếu xuyên, cho vạt phải bị hất ra trước khi đuôi tới |
| 4 | C | Đọc từ trên cao, F5 so với F9 | Từ trên nhìn xuống, F5 (đầu trượng ra sau, đuôi ra trước) và F9 (đầu ra trước, đuôi ra sau) đều là một vạch trước-sau qua tay phải, chỉ khác đầu có quả cầu nằm ở đâu. Cú vung lại nằm trong mặt phẳng dọc nên từ trên khó thấy quét | Cho mặt phẳng vung nghiêng ra ngoài bên phải ~20–30°, để từ trên thấy một vòng cung sang bên chứ không chỉ vạch co dãn. Để user xem ở P0 |
| 5 | C | Bảng PA, dòng A | Còn ghi "tay phải gần đuôi" | Chỗ tay phải nắm cách đuôi 1,13 m, cách đầu 1,02 m, nên đúng ra là "tay phải giữa cán, ngoài sườn phải". Sửa chữ cho khớp số |

### Giữ nguyên
- Bảng đường đi trượng theo key, đuôi nhấc trước, không cắm đất, đi ngoài chân phải.
- F5 tay cạnh tai phải, trượng ngả sau 45°: trong tầm, không chạm đầu.
- Không bước, hông hạ 4–5 cm, đổ người bằng thân. Đầu khoá mục tiêu. Khoảng hở cán–đầu ≥ 10 cm.
- Quy ước frame F0→F24, bắn F9 = 0,30 s = tỉ lệ 0,375 (frame thứ 10 nếu đếm từ 1). Dev đọc được ngay.
- Câu hỏi 4 (tay nào trước) và 5 (bản tối giản) đúng chỗ.

### Vòng sau
- Chỉ cần chốt số cho tay trái đón cán (đo vai trái thật trên rig), sửa F2. Xong là Duyệt, chuyển P0.

### Ghi chú kỹ thuật cho animator
- [đo ước] #1: chưa có vị trí vai trái thật, giả định vai ở x ±0,17, y 1,14. Ngực yaw −35° → vai trái ≈ (0,14; ; +0,10); thân nghiêng 15–20° → vai trái thêm ~+0,18 về trước, hạ ~0,06. Chỗ đỡ cán 0,3 m trước cổ tay phải dọc trượng: F9 ≈ (−0,30; 0,90; 0,55) → ~0,53 m; F7 ≈ (−0,40; 1,36; 0,46) → ~0,6–0,68 m. Chạy lại với vai thật trên rig (`DEF_Shoulder_L` hoặc tên tương ứng) trước khi chốt.
- [đo] #2: đuôi y = 1,00 − 1,13·cos(nghiêng). Muốn đuôi cao 0,25 m cần nghiêng ≈ 48° so với phương đứng.
- [đo] #3: F7, đuôi = cổ tay − 1,13·(0; 0,707; 0,707) ≈ (−0,40; 0,35; −0,55). F5, đuôi ≈ (−0,35; 0,50; +0,70): ở trước gối phải, đã hở.
- [mắt] Cổ bù ngược 30–40° để đầu nhìn thẳng khi ngực xoay: chia cho cổ và đầu, kiểm không vặn cổ khi P0.
- Không có ảnh/ref trên máy; chấm theo số trong analysis.

## Director – windy_attack analysis.md vòng 3 – mốc analysis – 2026-11-05
**Kết luận: Duyệt** (hết lỗi A; còn 2 điểm B để kiểm ở P0, 3 điểm C sửa chữ)
Ý chính: Tay trái giờ với tới cán ở F9 (vừa đủ) và có phương án lùi về bắn một tay nếu P0 không đạt. Cả đòn đã đủ số để dựng P0. Chỗ cần coi chừng nhất: đuôi trượng đi rất sát eo và mông phải lúc bắn.

### Đối chiếu vòng 2
#1 tay trái đón cán: **Đã sửa**. Vai thật đo trên rig, F9 tính lại được ~0,41 m (≤ 0,42), đón muộn F8–F9, có đường lùi PA B. · #2 F2: **Đã sửa** (nghiêng 50°, số khớp). · #3 đuôi vs vạt F6–F8: **Đã sửa**. · #4 mặt phẳng vung nghiêng ra ngoài: **Đã ghi**, để user xem ở P0. · #5 chữ PA A: **Đã sửa**.

### Cần sửa (nặng → nhẹ)
| # | Mức | Ở đâu (frame) | Đang thấy | Nên thấy / sửa thế nào |
|---|---|---|---|---|
| 1 | B | Đuôi trượng, F9–F13 | Tay phải dời vào gần giữa người, trượng chỉ quay vào ~4°. Cán sau tay đi ngang eo phải, cách tâm người ~20 cm, ngang thắt lưng chứ không phải ngang mông. Hở 4 cm là rất mỏng, hông còn nảy 2 cm ở F9–F13 | Ở P0 đo khoảng hở cán–eo–mông phải mọi frame F9–F13, không chỉ ở đuôi. Thiếu thì tăng góc quay vào lên ~6–8° (đầu trượng vẫn trong mức lệch cho phép), hoặc hạ ngực xoay bớt cho hông phải ra trước ít hơn |
| 2 | B | Tay trái, F8 | Bảng ghi tay trái "bắt đầu chạm cán" ở F8. Tính nhanh, chỗ nắm ở F8 còn cách vai ~0,45 m, quá mức 0,42 | Ở F8 cho tay trái chỉ vươn tới gần cán, chạm thật ở F9. Hoặc đo ở P0 rồi ghi lại |
| 3 | C | Chữ trong file | Mục C dòng Trượng vẫn ghi "tay phải phải đưa ra ngoài sườn phải". Mục "Điểm bắn cho dev" ghi đầu trượng lệch phải ~0,3 m, giờ chỉ còn ~0,1 m | Sửa cho khớp bảng F9 mới |
| 4 | C | Cổ + đầu, F7–F13 | Ngực xoay 40° mà đầu vẫn nhìn thẳng thì cổ phải xoay ngược ~40°. Ở chibi đầu to, chỗ này dễ thành "đầu vặn" | Chia góc cho cổ và đầu, nhìn ở P0 cạnh dáng Idle |

### Giữ nguyên
- Toàn bộ đường đi trượng theo key (F0/F2/F5/F7/F8/F9/F13/F18/F24), đuôi không cắm đất, đi ngoài chân phải.
- F5 tay cạnh tai phải, trượng ngả sau 45°. Không bước, hông hạ 4,5 cm, đổ người bằng thân. Đầu khoá mục tiêu.
- Bảng tầm với tay trái có vai thật + phương án lùi PA B: cách làm đúng, giữ cho các clip Skill.
- Quy ước frame + tỉ lệ bắn 0,375 cho dev.

### Vòng sau (P0)
- Dựng F9 trước: hai tay trên cán, trượng ngang chĩa thẳng, đuôi hở eo/mông. Nhìn ở camera trên cao rồi mới tới F5 và F7. P0 phải cho thấy ngay đây là "chĩa trượng vào mục tiêu", không phải dáng vặn người.

### Ghi chú kỹ thuật cho animator
- [đo] Tầm với F9: vai trái (0,18; 1,06; 0,32) → (−0,17; 0,88; 0,45) = 0,414 m. Tay phải: vai phải ước sau xoay + nghiêng ≈ (−0,18; 1,06; 0,02) → cổ tay (−0,17; 0,88; 0,30) ≈ 0,33 m, trong tầm.
- [đo] Đuôi F9 (−0,25; 0,85; −0,83): cán qua z ≈ 0 ở x ≈ −0,20, y ≈ 0,87 (ngang eo). Kiểm mesh eo/hông phải + áo choàng ở đoạn này.
- [đo ước] F8: cổ tay (−0,25; 1,00; 0,28), chỗ nắm 15 cm trước ≈ (−0,25; 1,0; 0,43). Tới vai trái (lấy vị trí F9) ≈ 0,45 m.
- Không ảnh/ref trên máy; Duyệt cho phần thiết kế chữ/số. P0 cần chấm bằng ảnh cam game + top + bên phải.

## Director – windy_attack blocking stepped (F0,5,7,9,13,18,24) – mốc blocking – 2026-11-06
**Kết luận: Cần sửa** (các key chính đúng hướng; còn 2 lỗi A là đuôi trượng chạm/cắm đất giữa các key, và thiếu key kiểm soát)
Ý chính: Đường trượng đúng thiết kế: chĩa lên-ra sau (F5) -> lật lên trước (F7) -> ngang chĩa thẳng (F9) -> về chéo (F18). Đuôi ở 7 key đều ≥ 0 và hở thân. Nhưng trượng lật 90° quanh tay trong 2F nên đuôi quét qua điểm thấp nhất ngay giữa các key (F2-3 và F6) và sẽ cắm đất khi spline. Sau bắn F9->F13 gần như đứng im, người và tay trái cũng quá hiền.

### Cần sửa (nặng -> nhẹ)
| # | Mức | Ở đâu (frame) | Đang thấy | Nên thấy / sửa thế nào |
|---|---|---|---|---|
| 1 | A | Đuôi trượng, F2-F3 | F0 đuôi cách đất 4 cm, F5 đuôi lên cao 43 cm ở phía trước. Nối thẳng hai key này thì giữa chừng (~F2.5) trượng gần dựng đứng, đuôi tụt xuống dưới đất ~2 cm (đuôi cắm đất) | Key F2 (đã dự định): tay ~1,0 m, trượng còn nghiêng ≥ 40-50° để đuôi cao ≥ 12 cm, đuôi ra ngoài phải (x ≤ -0,45) |
| 2 | A | Đuôi trượng, F6 | Trượng lật từ ngả sau (F5) sang ngả trước (F7) nên đi qua dựng đứng ở F6. Tay F6 ~1,17 m, trượng dài đuôi 1,13 m, đuôi chạm ~4 cm trên đất hoặc xuống dưới. Tay F5->F7 chỉ dời 24 cm trong khi đầu trượng đi 1,7 m: nhìn như xoay trượng tại chỗ chứ không phải vung cả tay | Thêm key F6: nâng tay lên ≥ 1,3 m (đuôi ≥ 17 cm) và đẩy tay ra ngoài phải thêm ~10 cm, để vòng cung nghiêng ra ngoài như thiết kế. Đầu trượng lúc dựng ~2,2 m: cách đầu/mũ ≥ 10 cm là được |
| 3 | B | Sau bắn, F9-F13 | F13 gần trùng F9: tay y hệt, đầu trượng chỉ nhích ~5 cm (~3°). Giữ 4F thì sau phát bắn nhìn đơ, không có "theo đà" | Thêm key F11 vượt đà: tay đẩy thêm ~5-6 cm ra trước (cánh tay mới duỗi ~80%, còn dư tầm), đầu trượng nảy lên ~5°, hông nảy lên, rồi lắng về F13 |
| 4 | B | Thân, F5-F9 | Ngực chỉ ngả 6° ra trước lúc bắn, xoay 12° mỗi bên, hông hạ 4,5 cm. Thiết kế cần thân đổ trước 15-20°. Cú vung trông như tay vung, thân không góp lực | Tăng ngực ngả/xoay thêm (tới ~12-15° ngả trước ở F9, ngả sau rõ hơn ở F5). Giữ đầu nhìn mục tiêu, không để cổ vặn |
| 5 | B | Tay trái, F5-F13 | Cổ tay trái đi quanh Idle: F9 chỉ lùi sau ~10 cm, ngang 12 cm. Quyết định bắn một tay cần tay trái giang cân bằng; hiện tay trái gần như bám sườn, lệ thuộc cam từ trên không đọc được cân bằng | Tay trái giang ra ngoài + sau rõ (cổ tay ~x 0,65, z -0,3, nâng ngang ngực) ở F9, ngược chiều trượng; ở F5 vươn trước; về Idle từ F13 |
| 6 | B | Đuôi trượng, F18->F24 | Đuôi F18 cao 15 cm, F0 cao 4 cm; 6F hạ 11 cm đúng lúc spline có thể vọt xuống đất | Thêm key F21 (đuôi ≥ 8 cm), kiểm đường đuôi không < 0 ở lúc settle |
| 7 | C | Hướng trượng F9 | Đầu trượng lệch +X ~5,7° (quay vào trong), vượt mốc ±5° một chút | Giảm còn ≤ 4° nếu muốn tuyệt đối chĩa mục tiêu; hoặc báo user chấp nhận |
| 8 | C | Vải | Chưa key vải/áo choàng/vạt; đuôi F7 ở sau lưng (-0,31; 0,39; -0,65) có thể quét qua vạt sau phải | Key vải sau khi chốt thân; kiểm F6-F8 đuôi xuyên vạt/áo choàng |

### Giữ nguyên
- Đường trượng 7 key đúng thiết kế, đuôi hở thân: F9 cán đi qua z=0 cách tâm người ~40 cm (không đâm eo/mông), tay-vai ~36 cm trong tầm.
- F9 trượng ngang, cao 0,95 m, chĩa +Z, đọc rõ một vạch dài ở cam từ trên.
- F18 đã sát tầm về Idle (tay lệch 5 cm), đuôi ngoài chân phải (x -0,78).
- Hông hạ 4,5 cm, không bước. Nhịp 5-4-4-11 đúng chốt.

### Vòng sau
- Thêm F2, F6, F11, F21, spline thử rồi đo lại đuôi từng frame (y ≥ 0,05). Người xem phải thấy cả người tham gia cú vung (thân ngả, tay trái giang), không chỉ cây trượng xoay.

### Ghi chú kỹ thuật cho animator
- [đo, từ số animator đưa] Đuôi = tay - 1,13·u (u = (đầu-tay)/|đầu-tay|, độ dài đầu-tay 1,015-1,02 m, khớp thiết kế 1,02): F0 (-0,80; 0,04; 0,04) · F5 (-0,20; 0,43; 0,77) · F7 (-0,31; 0,39; -0,65) · F9/F13 (-0,49; 0,95; -0,82) · F18 (-0,78; 0,15; -0,45). Cả 7 key y ≥ 0.
- [đo ước] Giữa F0 và F5, nội suy hướng trượng ở giữa u ≈ (0,26; 0,93; -0,26), tay ≈ (-0,22; 1,03; 0,15) -> đuôi y ≈ -0,02. F6: u_y ≈ 1, tay ~1,17 -> đuôi y ≈ 0,04. Cần key thật để kiểm, không dựa vào tính.
- [đo] F9 cán qua z=0 tại x ≈ -0,41, y 0,95. F7 qua z=0 tại x ≈ -0,39, y 0,95. Hở thân ≥ 15 cm.
- [đo] F9 hướng: (0,10; 0; 1,01) -> yaw 5,7°. Vai phải ước (-0,18; 1,06; 0,02) -> cổ tay F9 = 0,36 m.
- [đo] Tốc độ đầu trượng: F5->F7 0,85 m/F, F7->F9 0,45 m/F, F13->F18 0,16 m/F, F18->F24 ~0,09 m/F. Nhịp giảm dần hợp lý, nhưng F5->F7 cần F6 để không nhảy.
- [mắt chưa] Dấu cổ/đầu rx (-5, -10) chưa kiểm chiều (ngửa/cúi). Không có ảnh: chấm bằng số; cần render F2, F6, F9 cam top + trước khi sau khi thêm key.

## Director – windy_attack blocking vòng 2 (7 key, bắn một tay; F5/F7/F9 user chỉnh tay) – mốc blocking – 2026-11-06
**Kết luận: Cần sửa**
Ý chính: F0, F18, F24 ổn. Ba pose then chốt đang lệch thiết kế. F5 và F7 trượng dựng thẳng và tay duỗi quá tầm. F9 trượng chĩa sang trái chứ không chĩa trước. Sau bắn trượng về dáng Idle quá nhanh.

- F0: Idle, giữ nguyên. Đuôi trượng sát đất ~4 cm, cần giữ không cắm.
- F5: tay cách vai 0,50 (> 0,46, duỗi quá). Trượng gần dựng đứng (hướng ≈ (0,18; 0,98; 0,18)), không ngả sau 45° như thiết kế; từ trên nhìn xuống chỉ còn một chấm. Tay ra ngoài phải 0,64. Đầu/ngực gần như không đổi so Idle: lấy đà thiếu thân. Tay trái giang trước-ngoài đúng ý.
- F7: tay lùi ra sau lưng (z −0,41), cách vai 0,58 (vượt tay dài 0,46). Trượng vẫn dựng (≈ (−0,05; 0,99; −0,22)), không "lật lên trước 45°". F5→F7 tay đi lùi sau chứ không vung qua bên phải đầu; trượng chưa quét. Đo vai thật; nếu thân xoay thì ghi lại, nếu không thì tay đang giãn.
- F9: tay duỗi ra trước 0,72, cách vai 0,45 (sát giới hạn). Trượng hướng (0,82; 0,47; 0,37) lệch ~66° khỏi +Z, chĩa trái-lên; thiết kế yêu cầu ngang chĩa +Z ±5°. Đầu tiến trước 0,23 và hạ 11 cm, hông hạ 5 cm: đổ người tốt nhưng F7→F9 đầu đi 34 cm trong 2F. Tay trái giang ra trái-sau nhưng cùng phía với đầu trượng nên không thành đối trọng.
- F13: tay lùi 42 cm, đầu trượng đi ~1,1 m trong 4F: đã gần như dáng F18. Không có đoạn giữ/theo đà sau bắn. Hông 0,61 chưa theo F9.
- F18: đầu trượng lệch Idle 22 cm, tay lệch 21 cm; F13→F18 chỉ ~15 cm. Pha về 11F thực tế là đứng gần im.
- F24 = F0 ổn.

Top 3: (1) F9 xoay trượng chĩa +Z (hoặc user xác nhận chủ ý quét chéo, báo dev); (2) F5/F7 trượng ngả sau rõ + tay trong tầm 0,46, F7 tay phải đi qua trước vai bên phải; (3) F9→F13→F18 giữ dáng bắn rồi về chậm dần, không về ngay ở F13.
Không ảnh; chấm bằng số. Cần render F5, F7, F9 cam top + trước nếu muốn xác nhận.

## Director – windy_attack blocking vòng 3 (7 key, bắn một tay, FK) – mốc blocking – 2026-11-06
**Kết luận: Cần sửa nhẹ** (không còn lỗi chặn ở pose chính; còn 3 việc trước khi qua spline)
Ý chính: Lần này đúng ý: lấy đà trượng ra sau, lật lên trước, bắn ngang chĩa thẳng, theo đà rồi về. Hết lỗi vòng 2 (trượng chĩa trái, tay quá tầm, về quá nhanh). Chỗ còn xấu: F5→F7 trượng lật như xoay tại chỗ (tay dời ít), sau bắn thân và tay trái ít sống, vải chưa có.

- F0: đúng Idle. Giữ.
- F5: trượng chĩa ra sau-lên ~35° (thiết kế 45°, lệch ~11° đã biết), tay trong tầm (0,23). Tay trái đã giang trước. Chấp nhận. Chưa có ảnh góc trước để xem tay/đầu.
- F7: trượng lên-ra trước ~45°, đúng. Nhưng tay chỉ dời ~0,25 m so với F5 trong khi đầu trượng đi ~1,8 m: nhìn như xoay trượng quanh tay. F6 trượng đi qua dựng đứng, đuôi có thể xuống ~0 -> kiểm khi spline.
- F9: ngang, chĩa +Z (lệch ~3°), hông hạ 5 cm, thân ngả 17°, tay trái giang ngược phía trượng. Pose tốt nhất, đúng thiết kế. Cán đi ngang eo cách ~40 cm, hở.
- F13: đầu trượng nảy lên ~7°, hông còn thấp, đúng ý theo đà. Nhưng tay trái và tay phải y hệt F9, đứng im hoàn toàn.
- F18: đang hạ về, người gần Idle (hông 0,62), tay trái còn lệch ~20 cm, tay phải ~22 cm. Đuôi cao ~0,57, an toàn.
- F24 = F0 ổn.

Top 3: (1) thêm thử spline và đo đuôi F2–F3, F6 (y ≥ ~0,05), nếu cắm thì nâng tay F6 ≥ 1,3 m và đẩy ra ngoài phải ~10 cm (lặp lại từ vòng blocking trước); (2) F13 cho tay trái bắt đầu về/hạ nhẹ để khỏi đơ, vải key sau khi thân chốt; (3) xin ảnh góc trước + top cho F5, F7, F9 để xác nhận đầu/cổ không vặn và hở đầu/mũ ≥ 10 cm.
Không ảnh/ref video; chấm bằng số.

## Director – windy_attack breakdown/spline thử vòng 4 – mốc spline – 2026-11-06
**Kết luận: Cần sửa nhẹ** (gần được; còn 2 chỗ khựng nhỏ và tay trái/cổ tay chưa sống)
Ý chính: Lấy đà và vung đã mượt, thân có hạ hông trước tay (F3, F8). Chỗ còn khựng: ngay sau bắn (F9→F12) và đoạn về F18→F22. Không có ảnh, chấm bằng số người dùng đưa.

- Lấy đà F0–F5: nhanh rồi chậm dần vào đỉnh, đúng. Hông hạ trước, tay lên sau, tốt. Từ F4 đến F7 tay gần như đứng (8–16 cm/F) và khuỷu thẳng 168° ở F5–F6, nên đỉnh nhìn hơi cứng.
- Vung F5–F9: nổ từ F8 (tay 60, đầu trượng 88 cm/F), hông hạ trước một nhịp, đầu trượng trễ sau tay, khuỷu gập F8 rồi duỗi F9: có thân dẫn rồi tay rồi trượng. Tốt.
- Sau bắn F9–F13: đầu trượng 100 -> 24 cm/F chỉ trong 1F (phanh gấp), rồi 18 -> 22 -> 13 (nảy lên ở F12), tay 5-6-7-3 cũng nảy ở F12. Đó là cái "khực khực".
- Về F13–F24: F13–F16 gần như trôi chậm (9–14 cm/F) rồi F17 nhảy 25. F19 chậm lại 9 rồi F20–F21 lại nhanh 14, đuôi trượng hạ nhanh nhất ở F20–F21 (10 cm/F) trong lúc đầu trượng chậm dần, rồi phanh ở F22. Đó là cái giật F20.
- Tay trái: ngược chiều trượng đúng, nhưng F7 và F9 gần như cùng chỗ trong khi tay phải bắn đi 1 m; không có vọt rồi lắng. Cổ tay phải: không đo được từ số này.
- Bỏ key: nên bỏ F19 (F18, F19, F20 ba key liền trong 6F gây dao động); xem F20 còn cần không sau đó. Giữ F3, F8, F16.

Top 3: (1) F9→F12 giảm tốc dần (đầu trượng ~100 -> 45 -> 28 -> 18 -> 12), xoá nảy F12; (2) bỏ F19, dàn đuôi trượng F18–F24 giảm dần đều, không nhanh nhất ở F20; (3) tay trái vọt thêm ở F10 rồi lắng, cổ tay trễ rồi bẻ ở F9, nới khuỷu F5–F6 (~155°).
Thiếu: chưa có ảnh render, chưa có số ngực/cổ tay từng frame.

## Director – windy_attack spline thử vòng 5 (có breakdown F3/F8/F11/F16/F19) – mốc spline – 2026-11-09
**Kết luận: Cần sửa nhẹ** (vung và lấy đà ổn; còn khựng sau bắn F9-F14, thân/tay trái biên độ nhỏ, khuỷu thẳng nhiều key)
Không có ảnh, chấm bằng số animator đưa.

- Lấy đà F0-F5: nhanh rồi chậm dần, hông hạ trước tay (F3). Tốt. F4-F7 tay gần đứng (14-13-10-15 cm/F), khuỷu 155-160 gần thẳng -> đỉnh hơi cứng. F6->F7 đầu trượng 57->31 rồi F8 vọt 73: hơi do dự trước khi đập.
- Vung F5-F9: tay 15->48->58, hông hạ F8 trước F9, trượng trễ sau tay. Đúng thứ tự. Tốt.
- Sau bắn F9-F13: vẫn phanh gấp (tay 58->8, đầu trượng 116->22 trong 1F), rồi 22->18->4: phanh lần hai ở F11->F12. F12-F14 cả tay, trượng, hông, ngực đứng im 3F cùng lúc -> đơ, rồi mới trôi (lặp lại ý vòng 4).
- Hồi F13-F24: vào chậm tăng dần tốt (3,2,5,6,7). F17-F21 tay đều ~7-8 cm/F, đầu trượng F20-F22 đều ~10 rồi F23->F24 7->2 phanh hơi gắt. Đuôi hạ êm, không chạm đất (min 0,04).
- Thân: thứ tự hông -> bụng -> ngực đúng, nhưng vượt đà chỉ ~1-2 độ, ở cam trên cao không đọc được. Hông chỉ 2 cm (user dặn giữ).
- Tay trái: sống ở F5 (vươn trước) -> F9-F11 (lùi ~11 cm), nhưng giữ giang ngoài ~x 0,57 từ F7 tới F18 (11F), rồi phải về trong 6F -> sượng.

Top 3: (1) F9->F14 làm giảm tốc dần (đầu trượng ~116->55->30->15->8->5), bỏ đứng im F12-F14, cho ngực/hông bắt đầu về trước tay 1F; (2) nới khuỷu ở các frame giữa (F6, F10-F12, ~145-150) và F4-F7 tay trôi nhẹ thay vì đứng; (3) tay trái bắt đầu hạ từ F13, tăng biên độ vượt đà thân (bụng/ngực ~4-5 độ). Sau đó render F5/F7/F9/F13 cam trên + trước, rồi mới key vải.
