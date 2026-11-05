# Director log – rpg2_hero_blade_idle

## Director – rpg2_hero_blade_idle v1 (Frolvy, chưa lưu) – mốc blocking – 2026-11-04
**Kết luận: Cần sửa**
Chấm từ số đo animator gửi + công thức key. Không có ảnh, không có ref nên chưa xem silhouette ở góc nào; phần nhìn bằng mắt chưa duyệt được.
Ý chính: sóng thân đúng ý (hông, eo, ngực, cổ, đầu trễ dần, đầu bù). Nhưng hai tay ở toạ độ thế giới gần như cùng pha, trái yêu cầu "avoid symmetrical arm movement". Ở camera top-down thì phần động gần như chỉ có trục Y, mà trục này nhìn từ trên xuống không thấy.

### Lỗi (nặng → nhẹ)
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | A | cả vòng (đáy F3–F7, đỉnh F18–F22) | 2 cổ tay | Hai tay lên xuống gần như cùng lúc. Vì tay đặt trong không gian ngực, nhịp nhún 2,4 cm của thân át mất offset riêng của từng tay. Phải: đáy ~F5, đỉnh ~F20. Trái: đáy F7, đỉnh F22. Lệch nhau ~2F (≈7% vòng), biên độ thế giới gần bằng nhau (3,7 / 3,8 cm). Mắt sẽ đọc là hai tay đối xứng. | Overlap / tránh đối xứng | Hai tay phải lệch nhau ≥ 1/4 vòng: phải trễ ~3–4F sau ngực, trái trễ ~10–12F (hoặc gần ngược pha). Mỗi tay cho một hướng chính khác nhau: phải chủ yếu lên xuống, trái chủ yếu trước/sau hoặc ra/vào. Offset local phải đủ lớn để thắng nhịp ngực. Sửa xong đo lại đáy/đỉnh wrist_y (thế giới) từng frame. | [đo] lệch pha ~2F |
| 2 | B | cả vòng | toàn thân (camera top-down) | Gần hết chuyển động nằm ở trục Y (hông 2,4 cm, đầu 2,3 cm), nhìn top-down không thấy. Các kênh nhìn từ trên xuống thấy được thì quá nhỏ: hông tz ±0,8 cm, ngực ry ±1°, cổ tay x 0,3–0,4 cm, xoay cổ tay 1,5–3°. Lên game sẽ thấy đứng im. | Staging / đọc ở cam game | Đừng tăng nhún (user quen tay 3–4 cm; ở SDR 5,5 cm là bị chê). Tăng các kênh nằm trong mặt phẳng XZ: ngực yaw ±2–3° chia dọc chuỗi (hông, eo, ngực), hông tz ±1–1,5 cm, mũi đao vẽ cung 3–5 cm. Cần render 1 vòng ở top-down để xác nhận. | [đo] + [mắt] chưa có ảnh |
| 3 | B | chưa key | 2 đao | GDD yêu cầu "hai đao rung lệch pha". Hiện đao chỉ ăn theo cổ tay. Phase xoay cổ tay: phải rz d5, trái rx d9 → lệch ~4F (48°), chưa thấy lệch pha. Với lưỡi ~0,4 m thì xoay 3° ≈ 2 cm ở mũi đao. | Secondary / GDD | Key CTL_Weapon_R/L (hoặc xoay cổ tay) sao cho mũi hai đao lệch nhau ~1/2 vòng, mũi đao vẽ cung trong mặt phẳng ngang 3–5 cm, đao trễ thêm 2–3F sau cổ tay. Đo đường mũi đao ở top. | [đo] 4F; [mắt] chiều dài lưỡi là ước lượng |
| 4 | B | F11–F15 (phải), F15–F18 (trái) | 2 tay (IK) | Tỉ lệ duỗi tay phải lên 0,970, tay trái 0,958. Gần thẳng thì lúc spline IK dễ giật (khuỷu bật), và tay trông căng, trái ý "relaxed". | Spline IK / thả lỏng | Giới hạn đỉnh reach ≤ ~0,955, giữ quanh 0,949 của dáng gốc user đặt. Hoặc cho cổ tay lùi về thân khi ngực lên. Đo góc khuỷu từng frame ở spline, không được dao động hơn ~5°. | [đo] 0,970 |
| 5 | C | cả vòng | Root | ty và tz cùng D(t,0) nên hông đi theo một đường chéo thẳng, không có cung. | Arcs | Cho tz lệch pha ty 4–7F để hông vẽ hình bầu dục. Xem thêm: hông hạ thì ra trước hay lùi ra sau tự nhiên hơn với thế đứng này (dấu +z) ([mắt]). | [đo] cùng pha |
| 6 | C | — | quy ước | Key ghi F0 = F30, trong khi studio đếm từ F1 (F1 = F31). Head có key thừa ở F0 và F1 (bước ~0,24°). Mỗi xương key ở frame riêng nên xem stepped sẽ thấy giật lung tung. | Quy ước / quy trình | Ghi lại theo F1..F30 khi báo user. Để user xem bản nội suy (spline/linear) chứ không xem stepped. | [đo] |

### Giữ nguyên
- Dáng gốc user đặt: Root ty −0,11 / ry −10°, Spine1, Chest, Neck ry 20° (nhìn sang), chân IK đứng yên (mắt cá luôn ở 0,1).
- Chuỗi trễ dọc cột sống: hông 0, rx 1, Spine1 3, ngực 5, cổ 6, đầu 8. Đầu bù để mắt ổn định. Tay phải biên độ lớn hơn tay trái.
- Biên độ nhún 2,4 cm và tay ~3,7 cm (thế giới) đang vừa, đừng tăng thêm.

### Định hướng vòng sau
- Mục tiêu: hai tay không bao giờ cùng lên cùng xuống, mỗi tay một nhịp và một hướng; mũi đao tạo chuyển động thấy được từ trên xuống, còn thân giữ nhịp thở như hiện tại.
- Cần animator: (1) bảng wrist/mũi đao x, y, z thế giới cho cả 30 F (nội suy, không lấy stepped); (2) render top-down + 3/4 ở F1, F8, F16, F23 (≥ 512 px) hoặc playblast 1 vòng top-down; (3) góc khuỷu từng frame.
- Lưu ý: ở Lumber, user bỏ nhịp hạ hông, nhưng clip này user yêu cầu nhún hông, nên không áp luật đó.

## Director – rpg2_hero_blade_idle v2 (Frolvy, spline, chưa lưu) – mốc blocking – 2026-11-04
**Kết luận: Duyệt** (chỉ phần đã đo; chưa có ảnh nên silhouette ở top-down chưa được xem)
Ý chính: cả 4 lỗi A/B của v1 đã sửa, số đo đều đạt. Không còn lỗi mức A.

- #1 (A, v1): **Đã sửa.** Tay phải chủ yếu lên xuống, y 2,7 cm, đáy F1–3, đỉnh F18–19 (đếm từ F1). Tay trái chủ yếu trước/sau, z 2,3 cm, trước nhất F12–13. Hai tay khác trục và lệch ~10F. [đo]
- #2 (B): **Đã sửa.** Hông tz 2,4 cm và lệch pha với ty, nên hông đi hình bầu dục (sửa luôn #5 của v1). Yaw ~3° chia qua hông, eo, ngực; cổ và đầu bù lại 2°. [đo]
- #3 (B): **Đã sửa.** Hai đao ngược pha. Mũi đao phải đi ~3×3 cm, mũi đao trái đi 5,7 cm. [đo]
- #4 (B): **Đã sửa.** Độ duỗi tay tối đa 0,953 / 0,952. [đo]

### Lỗi còn lại
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | C | — | quy trình | Chưa có ảnh: chưa xem silhouette top-down, mũi đao có xuyên đùi/hông hay không, khuỷu có bật không. | Kiểm cam game | Trước khi gửi user, render một vòng top-down + 3/4, hoặc ảnh F1/F8/F16/F23 ≥ 512 px, rồi tự xem. | [mắt] chưa có |
| 2 | C | F1 | quy ước | Nhớ chuyển F0 sang F1 khi báo user (F31 = F1). | Quy ước | — | — |

### Giữ nguyên
- Dáng gốc user đặt, chuỗi trễ cột sống, cách key tay theo đích thế giới, giới hạn duỗi tay ≤ 0,95, đao ngược pha.

User: Trả v2 (2026-11-04) – "làm lại, diễn phần thân trước, tay để sau. Root_M di chuyển xuống và lên, khi xuống rotate X xoay xuống theo. offset phần trên theo Root_M". Bài học: user muốn duyệt từng phần, thân trước rồi mới tới tay. v2 key cả tay, đao và yaw trong cùng một vòng nên bị trả, dù Director đã duyệt v2 theo số đo. Đề xuất phiên chính thêm vào director_standards.md.

## Director – rpg2_hero_blade_idle v3 (Frolvy, spline, chỉ thân) – mốc blocking – 2026-11-04
**Kết luận: Duyệt** (chỉ phần đã đo, chưa có ảnh). Không có lỗi mức A.
Ý chính: đúng lệnh user. Root nhún 2,4 cm, khi xuống thì rx cúi theo cùng F0 (F1 khi báo user). Phần thân trên trễ dần 0/2/4/6/8F theo Root. Đã bỏ tz và yaw, tay và đao giữ pose gốc.

### Lỗi
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | B | F1 / F15–16 | đầu | Pitch thế giới của đầu dao động ~7° (9,4° → 2,4°), gấp đôi mức gật idle đã duyệt (~3,6°, Gaygor). Lý do: phần bù ở cổ và đầu (±1 / ±1,5, trễ 6/8F) nhỏ hơn và lệch pha so với tổng pitch thân (±4,4° ở ~F2–3). Hệ quả: đầu và mũ trùm gật gù. Top-down nhìn mũ trùm rõ nhất, nên chỗ này sẽ thấy. | Overlap / ổn định đầu | Đưa dao động đầu về ~3–4°: tăng bù và kéo gần pha thân hơn, vd Neck −1,5°·D(t,4), Head −2,0°·D(t,6). Giữ phần trễ đầu ~2F để vẫn còn overlap. Ngực (dao động ~7,8°) không cần giảm. | [đo] 7° |
| 2 | C | cả vòng | 2 tay / đao | Tay IK nằm trong không gian ngực nên hai tay và hai đao đang đi cùng pha theo ngực (đối xứng). Đúng theo thứ tự user giao (tay để sau), không tính lỗi. Khi tới phần tay, lại key theo đích thế giới như cách v2 làm. | — | — | [mắt] |

### Giữ nguyên
- Root: ty và rx cùng pha. Chuỗi trễ 0/2/4/6/8. Chân đứng yên, không có kênh tĩnh bị trôi.

User (2026-11-05): làm lại file mới, giao lệnh từng bộ phận – "Hip: Lên xuống nhẹ, di chuyển trước và sau. Spine: Chuyển động ngược nhẹ với hip để giữ cân bằng. Chest: Nhấp nhô theo nhịp thở. Shoulder: Hai vai nâng hạ nhẹ."

## Director – rpg2_hero_blade_idle v4 (Frolvy, spline, F1=F31) – mốc blocking – 2026-11-05
**Kết luận: Cần sửa** (1 lỗi A). Chấm theo số đo, không có ảnh.
Ý chính: Hip, Spine và Shoulder đúng lệnh. Chest thì chưa: nhịp thở ở ngực không đọc được vì Spine và Chest triệt tiêu nhau.

### Lỗi
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | A | cả vòng (hít sâu nhất F18) | Chest | Pitch thế giới của ngực chỉ đổi 0,8° (16,1..16,9°). Lý do: Spine1 −1,2°·D(t,4) và Chest −1,2°·D(t,17) cùng biên độ, lệch nhau 13F, gần ngược pha (ngược hẳn là 15F), nên cộng lại gần bằng 0. Ngực chỉ còn nhấp nhô theo hông, không có nhịp thở riêng. Đây là một trong 4 lệnh của user mà chưa thấy. | Overlap / đọc được | Tăng Chest lên ~2,5–3°, hoặc lệch pha Chest so với Spine khoảng 6–8F thay vì 13F. Mục tiêu: pitch thế giới của ngực dao động ~1,5–2,5°, đỉnh hít F17–19. Đầu không key thì cũng sẽ dao động theo, nên đo lại; nếu đầu > ~3,5° thì thêm bù nhỏ ở cổ. | [đo] 0,8° |
| 2 | C | F17–18 | 2 vai | Hai vai cao nhất cùng lúc, chỉ lệch 2F. User chỉ yêu cầu "hai vai nâng hạ nhẹ", không yêu cầu lệch, nên chưa tính lỗi. Tay IK nằm trong không gian ngực, không theo xương bả vai: nâng vai thì khuỷu sẽ đổi góc. Đo góc khuỷu khi vai lên cao nhất. | Theo lệnh user | Đợi user duyệt. Nếu tay trông bị kéo thì kiểm khuỷu. | [đo] |

### Giữ nguyên
- Hông: lên xuống 2,4 cm (F1 thấp nhất, F16 cao nhất), trước/sau 2 cm, lệch pha 3F nên đi hình bầu dục.
- Spine ngược pha với hông.
- Đầu ổn định (0,8°). Chân đứng yên. Không key tay, đao, cổ, đầu: đúng thứ tự từng phần user giao.

## Director – rpg2_hero_blade_idle v3.1 (Frolvy, spline, thân + Root tz) – mốc blocking – 2026-11-05
User yêu cầu: "làm thêm di chuyển trước và sau cho root_m".
**Kết luận: Duyệt** (chỉ phần đã đo, chưa có ảnh). Không có lỗi mức A hay B.
Ý chính: Root đi theo hình bầu dục. Xuống thấp nhất ở F1; 3F sau (F4) ra trước nhất +1 cm; lùi sau nhất ở F19, ngay sau đỉnh cao F16 (báo user theo đếm từ F1). Sát trọng lượng: nhún xuống rồi dồn tới trước, đứng lên rồi lùi về. Lỗi đầu của v3 đã sửa: dao động pitch thế giới còn 3,3° (4,1–7,4°). [đo]

Hướng hông "xuống thì ra trước": hợp với dáng cầm đao. Đây là thế sẵn sàng của sát thủ, dồn trọng lượng lên mũi chân. Lúc hông ra trước thì khung chậu cũng nghiêng trước (rx +2°), nên không thành kiểu thúc hông (thúc hông là hông ra trước mà khung chậu ngửa sau). Biên độ ±1 cm vừa phải, top-down thấy nhẹ. Nếu xem playblast thấy giống "chồm tới" thì giảm còn ±0,6 cm, không cần đảo chiều.

### Lỗi
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | C | F16–F19 | 2 chân (IK) | Hông cao nhất cộng lùi sau nhất là lúc chân duỗi nhiều nhất. Chưa có số đo độ duỗi chân, nên chưa rõ gối có bật thẳng hay giật không. | Spline IK | Đo độ duỗi chân hoặc góc gối ở F1–F31; đỉnh nên ≤ ~0,97, góc gối dao động mượt. | chưa đo |
| 2 | C | cả vòng | 2 tay / đao | Tay và đao vẫn đi cùng pha theo ngực. Đúng thứ tự user (tay để sau). | — | Làm ở vòng tay. | [mắt] |

### Giữ nguyên
- Root: ty, rx, tz như hiện tại (tz trễ 3F). Chuỗi trễ thân. Phần bù đầu mới (Neck −1,5° D4, Head −2,3° D4). Chân đứng yên.

## Director – rpg2_hero_blade_idle v4 (Frolvy, thân v3.1 + tay, chưa key đao) – mốc blocking – 2026-11-05
User yêu cầu: "Làm tay" → "Xóa, làm lại" (xoá key lạ ở tay và Scapula).
**Kết luận: Cần sửa**
Ý chính: tay đi theo thân có trễ, đúng hướng. Nhưng ở toạ độ thế giới, hai tay vẫn gần như cùng pha và cùng trục chính, lặp lại đúng lỗi A của v1.

### Lỗi
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | A (lặp lại từ v1) | cả vòng | 2 tay | Hai tay cùng trục chính (trước/sau 4,5 / 4,0 cm, lên xuống 2,6 / 2,4 cm) và cực trị chỉ lệch nhau ~1–4F. Theo z: phải F6–7 / F22, trái F10–11 / F26. Theo y: thấp F3 / F7, cao F19–21 / F17–20. Lệch ~4F = 13% vòng, mắt vẫn đọc là đối xứng. Phần chung của ngực (k 1,0 / 0,8) át chuyển động riêng của từng tay (0,4–1,2 cm). User yêu cầu "avoid symmetrical arm movement". | Overlap / tránh đối xứng | Giảm phần ngực mang theo: R k ~0,6, L k ~0,5. Đẩy L trễ thêm: dl 10–12 (cách R ≥ 7–8F). Tăng chuyển động riêng cho mỗi tay một trục chính: R lên xuống ~1,5 cm, L trước/sau ~2 cm. Mục tiêu: trên trục chính, cực trị hai tay cách nhau ≥ 7F, hoặc hai tay khác trục chính rõ. | [đo] lệch 4F |
| 2 | B | F1–F15 | tay phải | Độ duỗi kẹp phẳng 0,95 suốt nửa vòng. Trong đoạn đó góc khuỷu đứng yên (khuỷu khoá, trông cứng). Đầu/cuối đoạn kẹp có gãy vận tốc nên khuỷu dễ giật lúc spline. Lý do: pose gốc đã ở 0,949, mọi chuyển động ra xa vai đều bị kẹp. | Spline IK / thả lỏng | Không kẹp cứng. Lệch chuyển động của R về phía vai (vào trong hoặc lên), để độ duỗi tự dao động khoảng 0,93–0,95 và chạm 0,95 chỉ ở một điểm. Hoặc dùng kẹp mềm (giảm dần từ 0,94). Đo góc khuỷu R từng frame: dao động ≥ 2–3°, không có frame nào vận tốc góc đổi đột ngột. | [đo] phẳng 15F |
| 3 | B | cả vòng | 2 tay | Đường đi cổ tay khá lớn: R ~5,2 cm, L ~4,7 cm. Gần mức 5,5 cm user từng chê "giảm biên độ lên xuống của 2 tay" (SDR Ninja). Phần lớn là do ngực cúi 7,8° kéo theo. | Biên độ idle | Giảm k như lỗi #1 thì cũng xử lý luôn lỗi này. Đích: ~3–4 cm mỗi tay. | [đo] |

### Giữ nguyên
- Thân v3.1 (đã duyệt), chân đứng yên, không kênh thân nào trôi.
- Cách key tay theo đích thế giới.
- Tay trái đã duỗi/co thoải mái (0,889–0,951).
- Phase xoay cổ tay hai bên khác nhau (R rz D5, L rx D10).

### Định hướng vòng sau
- Hai tay mỗi tay một nhịp: R nhịp lên xuống theo thân, sát pha thân. L trễ hẳn, đưa trước/sau. Tay phải thả lỏng, khuỷu không đứng yên.
- Đo lại: cực trị trục chính của từng tay (frame), góc khuỷu R từng frame, tổng đường đi cổ tay.

## Director – rpg2_hero_blade_idle v4.1 (thân v3.1 + tay, chưa key đao) – mốc blocking – 2026-11-05
**Kết luận: Duyệt** (chỉ phần đã đo, chưa có ảnh). Không còn lỗi A. Lỗi A lặp lại từ v1/v4 đã sửa.
Ý chính: mỗi tay một trục chính. R lên xuống 2,9 cm (thấp F5, cao F20). L trước/sau 3,0 cm (trước F11, sau F26). Cực trị lệch 6F, khác trục, nên không còn đọc là đối xứng. Đường đi cổ tay R ~3,8 cm, L ~3,2 cm, đúng mức user quen. Tay R hết khoá khuỷu: góc dao động 11,6° mượt, duỗi tới 0,959 ở một điểm. [đo]

### Lỗi
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | B | F1 / F18 | khuỷu trái | Góc khuỷu dao động 24° (123,6° → 147,7°), gấp đôi tay R. Cổ tay chỉ đi 3,2 cm, nên phần lớn là vai (bị ngực kéo) đi mà bàn tay đứng lại: khuỷu gập-duỗi như bơm, bàn tay như bị ghim, trông không "relaxed". Ở F18 tay gần thẳng (0,962). | Overlap / thả lỏng | Tăng L k lên ~0,7 (giữ dl 11 để không mất độ lệch pha). Hoặc cộng thêm một phần chuyển động vai vào đích cổ tay. Mục tiêu: khuỷu L dao động ~12–15°, đỉnh duỗi ≤ 0,95. Đo lại để chắc cực trị trục z vẫn cách R ≥ 6F. | [đo] 24°; [mắt] chưa có ảnh |

### Giữ nguyên
- Thân v3.1. Trục chính và độ lệch pha của hai tay. R: k 0,6, kéo vào vai, kẹp mềm. Phase xoay cổ tay L.

### Định hướng vòng sau
- Sửa khuỷu L (B), rồi tới đao (đúng thứ tự từng phần user muốn). Trước khi gửi user, render một vòng top-down để xác nhận phần tay.

## Director – rpg2_hero_blade_idle v4.2 (L theo vai trái) – mốc blocking – 2026-11-05
**Kết luận: Cần sửa**
Ý chính: khuỷu L đã ổn (16,3°, duỗi ≤ 0,951). Nhưng ở mặt phẳng camera top-down thấy được (x/z), hai tay giờ cùng đưa trước/sau gần như cùng lúc. Tự sửa sai: ở v4.1 Director chỉ so trục chính, bỏ sót trục z của R (2,4 cm, cách L 4F). Từ v4.2 so theo trục camera.

### Lỗi
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | A | F7–F9 / F22–F25 | 2 tay (top-down) | Trục chính của R là y, mà top-down không thấy y. Nhìn từ trên xuống chỉ thấy z: R z 2,4 cm (trước F7, sau F22), L z 4,9 cm (trước F9, sau F25). Lệch 2–3F, tức hai tay cùng đưa ra trước rồi cùng lùi về; chỉ khác biên độ. Ở camera game, mắt đọc là đối xứng, trái yêu cầu "avoid symmetrical arm movement". Nguyên nhân: cả hai tay đều ăn theo ngực cúi. | Overlap / tránh đối xứng (cam game) | Theo trục z, bớt phần ngực mang theo của R: tách k theo trục, R k_z ~0,2–0,3, giữ k_y 0,6. Khi đó nhìn top-down R gần như đứng yên, chỉ có L đưa trước/sau. Hoặc cho R z ngược pha L (riêng R z ~−1 cm·D(t,9)). Mục tiêu: ở mặt phẳng x/z, cực trị hai tay cách nhau ≥ 7F, hoặc một tay biên độ < 1 cm. | [đo] lệch 2F |
| 2 | B | cả vòng | tay trái | Đường đi 5,0 cm, gần mức 5,5 cm user từng chê (SDR Ninja). | Biên độ idle | Theo vai, k ~0,7–0,75 (đường đi ~3,5–4 cm). Đo lại khuỷu: giữ được ≤ ~18° là được. | [đo] |

### Giữ nguyên
- Thân v3.1, trục y của R (2,9 cm, khuỷu 11,6°), cách cho L ăn theo vai trái (khuỷu không còn bơm), y của L ngược pha.

### Định hướng
- Từ giờ đo độ lệch pha của hai tay theo trục camera (x/z cho top-down) chứ không theo trục chính 3D. Cần một lần render top-down một vòng để xác nhận.

## Director – rpg2_hero_blade_idle v5 (tay IK + scapula + pole, brief mới "subtle, asynchronous, overlap vai/khuỷu/cổ tay, casual puzzle") – mốc blocking – 2026-11-05
**Kết luận: Duyệt** (chỉ phần đã đo, chưa có ảnh). Không có lỗi A. Lỗi A của v4.2 đã sửa: nhìn top-down, R z trước nhất F29, L z trước nhất F9, lệch 10F, và R z chỉ 0,8 cm. [đo]
Ý chính: hai tay lệch nhịp và nhẹ, đúng brief mới (span R 1,8 / L 3,7 cm, khuỷu 12,9° / 15,9°). Thứ tự overlap của L đúng, của R còn ngược ở khuỷu.

### Lỗi
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | B | F20–F24 | khuỷu phải | Thứ tự R: vai F17 → cổ tay y F20 → xoay F23 → khuỷu x F24. Khuỷu đi sau cả bàn tay, nên đọc như bàn tay kéo khuỷu. Brief yêu cầu overlap vai → khuỷu → cổ tay. Nhìn top-down thấy khá rõ vì khuỷu dịch ngang. | Overlap / follow-through | PoleArm_R D(t,20) → D(t,18–19), cho khuỷu nằm giữa vai F17 và cổ tay F20. Hoặc giữ khuỷu, dời cổ tay y sang ~F21–22 và xoay sang ~F25. | [đo] |
| 2 | C | F6–F9 | cổ tay trái | Xoay cổ tay F6–9 gần như cùng lúc với vị trí cổ tay F9. Xoay nên là thứ trễ nhất. | Overlap | rx D(t,6) → ~D(t,11), ry D(t,9) → ~D(t,13). | [đo] |
| 3 | C | cả vòng | tay phải | Span 1,8 cm, bằng một nửa L. Trong một vòng thấy L động, R gần như đứng. Brief muốn nhẹ thì chấp nhận được. Nhưng ở SDR Ninja, tay ~3 cm từng bị chê "chưa thấy có anim". | Biên độ | Nếu user nói tay phải "đứng" thì nâng R lên ~2,5 cm (y riêng −0,8 cm). | [đo] |

Về chuỗi overlap của L: cổ tay z ở F9 do vai thân kéo (thân cúi ~F2–5, trễ 4). Phần scapula riêng F27 → khuỷu F30 → xoay F6–9 → cổ tay F9 đi đúng thứ tự theo vòng loop. Hai nguồn lệch nhau ~8F nhưng không ngược chiều nhau, nên không tính lỗi.

### Giữ nguyên
- Thân v3.1. R ít đi trước/sau, L đi trước/sau chính (lệch 10F). Khuỷu ≤ 16°, duỗi ≤ 0,956. Biên độ "subtle" phù hợp game casual.

User (2026-11-05): xoá key làm lại – "Hip: Lên xuống mạnh, di chuyển trước và sau. Spine: Chuyển động ngược mạnh với hip để giữ cân bằng. Chest: Nhấp nhô theo nhịp thở. Shoulder: Hai vai nâng hạ nhẹ. Arms: Hai tay chuyển động lệch nhịp, không đối xứng, lên xuống nhiều, offset theo thân. Head: Chuyển động nhẹ, có độ trễ với chest." Bản trước user chê "phần đầu rotate nhiều quá" (9,8°), duyệt ở ~4,9°.

## Director – rpg2_hero_blade_idle v5 (Frolvy, spline, F1=F31) – mốc blocking – 2026-11-05
**Kết luận: Duyệt** (không có lỗi A; chấm theo số đo, chưa có ảnh)
Đủ 6 lệnh của user: hông nhún 4 cm (mạnh) và trước/sau 2,4 cm; spine ngả ngược 5,7°; ngực thở 5,9° (lỗi A của v4 đã sửa); vai nâng hạ; hai tay lệch ~8–9F (L thấp F2/cao F17, R thấp F10/cao F26), biên độ khác nhau (5,2 / 6,2 cm); đầu 3,6°, trễ ngực 3F (ngực ngả sau nhất F7, đầu F10). Biên độ đầu dưới mức 4,9° user đã duyệt.

### Lỗi
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | C | F9–F15 | tay phải IK | Đoạn này bị kẹp duỗi (reach 0,95), dễ làm khuỷu khựng hoặc đổi hướng gập. Đường y của cổ tay vẫn mượt (77,0 / 76,4 / 77,0). | Spline IK | Đo góc khuỷu R từng frame ở F8–F16: không bậc > ~2°/F, hướng gối khuỷu không lật. | [đo] |
| 2 | C | cả vòng | đao trái | Mũi đao L thấp hơn cổ tay 5–8 cm, tức lưỡi chúi xuống, khác GDD ("lưỡi hơi hướng lên"). Pose đao là của user đặt, chưa key, nên không tính lỗi. | Theo user | Hỏi user một lần khi tới phần đao. | [đo] |

### Giữ nguyên
- Toàn bộ công thức v5. Đầu ≤ ~4–5°. Chân đứng yên.
