# Windy Attack — phân tích (G1–G3, nhánh B/C: ref của GD + rig Frolvy)

Nguồn: FDD "Hero: Windy" (Vũ Việt Tiến, 14/10/2026, Prototype), mục 1 "Tấn công thường"; ref GD
`drive.horusvn.com/s/rKLLWxxCmo3k3yr` (`windy_attack_ref.mp4`, 6,2 s, 544×446, playblast Maya, xem trên trình duyệt,
đo từng frame, không tải về); rig `Windy_rig.fv` + Idle đã chốt `C:\Users\Admin\Documents\Ngoc\Hoctap\Anim\Windy_Idle.fv`
(2026-11-05).
Nhãn: [GDD] trích FDD · [ref] đo trên video · [rig] đo trên rig · [suy luận] · [?] cần hỏi.
Frame ref ghi theo 30 fps (video gốc ~20 fps, mỗi 3 frame có 1 frame lặp).

## A. FDD nói gì

| # | Câu gốc | Hệ quả cho Attack |
|---|---|---|
| 1 | [GDD] "Mage tự động chọn enemy gần nhất trong Attack Range và bắn projectile về phía mục tiêu." | Đòn lặp liên tục suốt trận → phải gọn, đọc rõ, không mỏi mắt; vào và ra **đúng Idle F0** để nối Idle → Attack → Attack → Idle không giật. |
| 2 | [GDD] "Projectile bay thẳng theo hướng mục tiêu tại thời điểm cast." / Flow: "Chọn mục tiêu → Khóa hướng → Cast → Tạo projectile" | Có **một frame bắn** rõ ràng (game sinh projectile ở frame này). Lúc bắn, đầu trượng phải chĩa **thẳng về phía trước** (hướng nhân vật quay mặt), vì code xoay cả nhân vật về mục tiêu. |
| 3 | [GDD] Animation: "Windy đưa đầu trượng về phía trước" | Đỉnh đòn = đầu trượng (đầu có quả cầu) chĩa ra trước. Điểm sinh projectile = đầu trượng (`DEF_WeaponEnd_R`). |
| 4 | [GDD] "Mage là Hero duy nhất … đứng cố định tại tâm" | Không root motion, chân không rời chỗ khi kết thúc. |
| 5 | [GDD] VFX: "Đã có" | Anim không cần chừa chỗ cho VFX tích tụ; chỉ cần frame bắn + hướng bắn rõ. |

Quyết định đã chốt trước (ghi trong bộ nhớ dự án, duyệt 2026-11-04 ở máy khác, file phân tích cũ không có ở máy này):
**Attack 24F @ 30 fps, bắn F9**, nhịp đánh trong game 0,79 s ≈ 24F, game tự co giãn tốc độ Attack theo tốc đánh.

## B. Ref của GD đo được [ref]

Video lặp **cùng một đòn 3 lần** (mỗi lần ~48F = 1,6 s, đòn 2 bắt đầu ~F48, đòn 3 ~F96), sau F150 đứng yên.
Camera **đổi góc giữa đòn**: F0–F12 nhìn chéo trước, từ F13 nhìn ngang (đầu trượng chĩa sang phải màn hình), nên
nhân vật không xoay người, chỉ máy quay đổi chỗ. Nhân vật ref là khối đơn giản đội mũ phù thủy, trượng ~ngang người.

| Pha | Frame ref | Mô tả |
|---|---|---|
| Idle | F0–F3 | Đứng thẳng, tay phải cầm trượng **dựng đứng** bên phải, tay trái thả. |
| Lấy đà | F3–F10 (7F) | Tay phải nhấc trượng lên cao rồi kéo ra sau đầu (F6 trượng trên đầu, F10 đỉnh: trượng dựng sau gáy, khuỷu phải giơ cao, tay trái giang ra cân bằng), ngực ưỡn, người hơi ngả sau. |
| Vung | F10–F15 (5F) | Trượng quét một vòng cung qua đỉnh đầu ra trước và xuống (F12 trượng nằm ngang trên đầu, F14 trượng thẳng đứng trước mặt), người đổ về trước thành thế **tấn rộng** (gối trước gập sâu, chân sau duỗi), hông hạ. |
| Bắn | F15–F16 | Trượng **nằm ngang, chĩa thẳng ra trước**, tay sau giữ đuôi trượng sát hông, tay trước đỡ giữa cán (cầm **hai tay** như cầm giáo). |
| Giữ | F16–F30 (14F) | Giữ thế tấn + trượng ngang, đầu trượng nảy nhẹ rồi lắng. |
| Về | F30–F44 (14F) | Đứng lên, kéo trượng về dựng trước người, chân thu về. |
| Idle | F44–F48 | Về dáng đứng ban đầu. |

Tỉ lệ thời gian ref: lấy đà 7 · vung 5 · giữ 14 · về 14 (giữ + về chiếm 2/3 đòn, quá dài cho nhịp game 24F).

## C. Rig + dáng Idle F0 đo được [rig]

| Mục | Số đo | Ghi chú cho Attack |
|---|---|---|
| Cao | 1,85 m (đỉnh đầu 1,80), hông 0,63, vai 1,14 | Chibi ~3,5 đầu: đầu to che vai khi nhìn từ trên → tay vung phải ra ngoài khối đầu mới đọc được. |
| Hướng mặt | Main nhìn +Z; hông xoay sẵn 24° sang trái (Idle); chân phải trước (z +0,13), chân trái sau (z −0,15), rộng 0,37 m | Chân phải đã ở trước → thế tấn chỉ cần dồn trọng tâm lên chân phải, **không cần bước**. |
| Trượng | Dài 2,15 m, cầm cách đuôi 1,13 m / cách đầu 1,02 m; chỉ tay phải (`DEF_Weapon_R`) | Khi trượng ngang ở độ cao tay ~0,9 m, đầu trượng ra trước ~1,0 m tính từ tay, đuôi lòi ra sau ~1,1 m → đuôi trượng dễ **đâm vào eo/mông phải**. Cách xử lý ở D: tay phải trước hông phải (x −0,17), trượng quay vào trong ≤ 4–8° để cán đi ngoài eo/mông phải. |
| Trượng ở Idle F0 (user chỉnh) | Cầm **chéo ngang thân 45°**: tay phải (−0,20; 0,76; 0,23), đầu trượng lên trước-trái (0,62; 1,56; 0,57), **đuôi trượng gần chạm đất bên phải** (−0,80; 0,04; 0,03) | Khác ref (ref dựng đứng). Attack phải bắt đầu và kết thúc đúng dáng này, không đổi dáng cầm của user. Đuôi chỉ cách đất 4 cm → mọi frame lấy đà và về: đuôi cao ≥ 0 (không cắm đất). |
| Tay phải | IK (`ArmSwitch_R.fkIk = 1`), vai → cổ tay 0,46 m | Chuyển động trượng điều qua `CTL_IKWrist_R` + `CTL_Weapon_R`. Tay không với quá 0,46 m từ vai (≤ 0,42 để khuỷu còn gập). |
| Tay trái | FK (`ArmSwitch_L.fkIk = 0`), Idle F0: **thả hờ cạnh sườn trái** (cổ tay (0,37; 0,75; −0,07), khuỷu gập ~50°, cách cán trượng 0,56 m); găng chỉ ngón cái + ngón giữa | Pha về trả tay trái đúng chỗ này. Cầm hai tay cần thân xoay để vai trái tới cán (xem D). |
| Đầu + mũ | Đầu 0,53 m cao, rộng 0,50 m (1,30–1,85 m); tay phải ở cao vai chỉ ra ngoài mép đầu ~5 cm | Mọi frame vung: cán cách đầu/mũ ≥ 10 cm. |
| Vải | Áo choàng 4 đốt (đốt gốc user đã key lắc 20F), 2 vạt sau 4 đốt | Vung trượng = cú gió mạnh: vải phải bị hất ra sau lúc vung, quật về trước sau khi bắn. |
| Camera game | Từ trên chéo xuống, hero ~60–70 px trên màn 1020 px (ghi chú dự án 2026-11-04) | Chỉ hình lớn đọc được: **đường trượng** (cung vung + đường ngang chĩa mục tiêu), độ hạ người, vải. Ngón tay, mặt: không thấy. |

## D. Thiết kế đề xuất

**Độ dài: 24F @ 30 fps (0,8 s), bắn F9** (đã chốt). Vào và ra trùng Idle F0, không root motion, chân không trượt.

**Quy ước frame:** đếm như timeline Frolvy, **F0 → F24** (F24 = F0 = Idle F0, lặp được; xuất 24 frame F0–F23 nếu game
loop, hoặc 25 frame F0–F24 nếu game không loop – hỏi dev). Frame bắn **F9 = 0,30 s = 37,5 % độ dài đòn** (đếm từ 1 là
frame thứ 10). Game co giãn tốc độ thì dùng **tỉ lệ 0,375** để sinh projectile.

**Đường đi của trượng (vạch trượng nhìn từ trên):** chéo trước-trái (Idle) → **chĩa ra sau** (F5) → quét qua **bên phải
đầu** → **chĩa thẳng mục tiêu** (F9) → về chéo trước-trái (F24).

| Key | Cổ tay phải (x; y; z, m) | Trượng | Kiểm |
|---|---|---|---|
| F0 | (−0,20; 0,76; 0,23) | Đầu trước-trái-trên 45°, đuôi sát đất bên phải | Idle |
| F2 | ~(−0,30; 1,00; 0,15) | **Đuôi nhấc trước**: trượng vẫn nghiêng ~50° so với phương đứng, đuôi chĩa ra ngoài-xuống bên phải, cao ~0,25 m (= 1,00 − 1,13·cos 50°); đầu trượng đi lên qua trước vai phải | Đuôi ≥ 0, không quét qua chân phải (x đuôi ≤ −0,45) |
| F5 đỉnh lấy đà | ~(−0,35; 1,30; −0,10): cạnh tai phải, sau vai 0,1 m | Ngả ra sau ~45°: **đầu trượng chĩa lên-ra sau**, đuôi chúc xuống-ra trước bên hông phải (cao ~0,5 m) | Vai → cổ tay ≈ 0,26 m (trong tầm), khuỷu gập; cán cách mũ ≥ 10 cm |
| F7 giữa vung | ~(−0,40; 1,15; 0,25): trước vai phải, ra ngoài mép đầu 15 cm | Đầu trượng vừa vượt qua bên phải đầu, chĩa lên-ra trước ~45°; đuôi chúc xuống sau lưng bên phải ~(−0,40; 0,35; −0,55) | Cán cách đầu/mũ ≥ 10 cm; **F6–F8 đuôi không xuyên vạt sau phải + áo choàng** (vạt bị hất ra trước khi đuôi tới); tay trái chưa đón (quá tầm 0,65 m) |
| F8 | ~(−0,25; 1,00; 0,28) | Gần ngang, vượt ~10° (smear tuỳ chọn) | Tay trái **vươn tới gần** cán (còn ~0,45 m, chưa chạm); chạm thật ở F9 |
| F9 bắn | **(−0,17; 0,88; 0,30)**: trước hông phải, gần đường giữa | **Ngang**, cao ~0,9 m, đầu trượng chĩa +Z, quay đầu trượng vào trong 4° (tới 6–8° nếu thiếu hở); đuôi ~(−0,25; 0,85; −0,83) | Đo **cả đoạn cán** sau tay phải với eo + mông phải ở mọi frame F9–F13 (hông còn nảy 2 cm): hở ≥ 4 cm, không xuyên vạt / áo choàng; tay trái nắm (−0,17; 0,88; 0,45) |
| F13 | như F9, nảy rồi lắng | Ngang | |
| F18 | ~(−0,25; 0,90; 0,25) | Đầu trượng hạ chéo sang trái, đuôi hạ xuống bên phải (~0,3 m) | Đuôi đi ngoài chân phải (x ≤ −0,45), không cắm đất |
| F24 | = F0 | = Idle | |

**Chân + hông: không bước** (chọn thay vì trượt chân lên 15–20 cm, vì hero đứng cố định và chân chibi ngắn – bài học
Ninja: tấn rộng thành ngồi xổm). Hai bàn chân giữ nguyên (phải trước 0,13 m, trái sau −0,15 m). Hông chỉ hạ **4–5 cm**,
dồn lên chân phải, gối trái hơi chùng (không duỗi thẳng). Cảm giác "đổ người" lấy từ **thân nghiêng trước 15–20°** và vai.

**Tầm với tay trái (vai trái thật trên rig (0,23; 1,13; −0,02), tay 0,46 m, cần ≤ 0,42 để khuỷu còn gập):**

| Cách | Vai trái sau khi xoay/nghiêng | Chỗ nắm cán | Khoảng cách |
|---|---|---|---|
| Ngực xoay 35°, nghiêng 17°, tay phải ngoài sườn (x −0,30), nắm cách 0,3 m – bản cũ | (0,19; 1,07; 0,29) | (−0,30; 0,90; 0,55) | 0,58 m – không tới |
| Như trên, đón ở F7 | | trượng còn chĩa lên | ~0,65 m – không tới |
| **Chọn: ngực xoay 40°, nghiêng 20°, hông hạ 4,5 cm; tay phải dời vào (x −0,17); tay trái nắm sát trước tay phải 15 cm; đón F8–F9** | (0,18; 1,06; 0,32) | (−0,17; 0,88; 0,45) | **0,42 m – vừa đủ** |

Hông xoay ít (~10°). Ngực xoay 40° mà đầu nhìn thẳng → cổ + đầu xoay ngược 40°, chia đều cổ/đầu, kiểm cổ không vặn ở P0.
Tầm với đang sát giới hạn: P0 đo lại găng trái → cán ≤ 1–2 cm, khuỷu trái gập ≥ 15°. **Không đạt thì lùi về PA B (bắn
một tay, tay trái giang ra sau cân bằng)**, báo user trước.

**Mặt phẳng vung nghiêng ra ngoài bên phải ~20–30°** (không vung thẳng dọc người): nhìn từ trên, đầu trượng vẽ một
vòng cung sang phải chứ không chỉ là một vạch trước-sau ở F5 và F9. Cho user xem ở P0.

**Đầu (khối to nhất nhìn từ trên):** khoá hướng nhìn mục tiêu suốt đòn; ngửa nhẹ ~5° lúc lấy đà (F3–F5), cúi theo cú
vung ~8° (F8–F10), trễ sau ngực 1–2F; về idle cùng thân.

**Phương án tay cầm lúc bắn:**

| PA | Mô tả | Ưu | Nhược |
|---|---|---|---|
| **A (đề xuất)** | Theo ref: bắn bằng **hai tay**: tay phải nắm cán (cách đuôi 1,13 m) trước hông phải, tay trái nắm **sát trước tay phải ~15 cm**, đón muộn ở F8–F9; trượng ngang chĩa trước; tay trái buông từ F14 | Đúng ref GD, thế chắc, trượng ngang đọc rõ từ trên | Tầm với **sát giới hạn** (0,42 m, xem bảng tầm với); bật IK tay trái F8–F14; đuôi đi sát mông phải (hở ~4 cm) |
| B | Một tay: tay phải đẩy trượng ngang ra trước, tay trái giang ra sau cân bằng | Đơn giản, nhanh, dáng mở | Trượng 2,15 m chĩa ngang bằng một tay chibi trông yếu; khác ref |

**Bảng pha (A), 24F:**

| F | Pha | Thân / chân | Tay phải + trượng | Tay trái | Vải |
|---|---|---|---|---|---|
| 0 | Idle F0 | Như Idle | Chéo 45° như Idle | Thả hờ cạnh sườn trái | Như Idle F0 |
| 0→5 | Lấy đà (5F, ref 7F) | Ngực ưỡn, người ngả sau ~8°, hông lùi 3 cm, trọng tâm về chân trái; đầu ngửa ~5° | Đuôi nhấc khỏi đất trước (F2), rồi tay lên cạnh tai phải, trượng ngả sau 45° | Giang ra trước-trái cân bằng | Vải hơi chùng |
| 5 | **Đỉnh lấy đà** (key) | Ưỡn nhất | Đầu trượng chĩa lên-ra sau (vạch ngược hướng mục tiêu) | Giang trước, ngang ngực | |
| 5→8 | Vung (3F, ref 5F) | Thân đổ trước, ngực xoay phải 30–40°, hông hạ dần 4–5 cm; đầu cúi theo, trễ 1–2F | Trượng quét cung qua **bên phải** đầu (cách đầu/mũ ≥ 10 cm); mỗi frame một điểm khác trên cung (đầu trượng đi ~0,8 m/frame) | Đón cán ở F7 | Vải bị hất ra sau mạnh nhất |
| 8 | Smear (tuỳ chọn) | | Trượng vượt quá ngang ~10° xuống | | |
| **9** | **BẮN** (key) | Hông thấp nhất (−4–5 cm), trọng tâm chân phải, thân nghiêng trước 15–20°, đầu nhìn thẳng mục tiêu | Trượng **ngang** cao ~0,9 m, đầu trượng chĩa thẳng +Z (lệch ≤ 5°); đuôi ngoài sườn phải | Đỡ giữa cán (≤ 1–2 cm) | |
| 9→13 | Theo đà + lắng (4F) | Hông nảy lên 2 cm rồi lắng | Đầu trượng nảy lên ~5° rồi về ngang | Giữ cán | Vải quật về trước (trễ 2–3F mỗi đốt) |
| 13 | Bắt đầu về (key) | | | Buông cán từ F14 | |
| 13→24 | Về (11F, ref 14F) | Đứng lên, ngực xoay về, trọng tâm về giữa | Đầu trượng hạ chéo sang trái, đuôi hạ xuống bên phải ngoài chân (không cắm đất) về đúng dáng 45°; ease-in dài | Về đúng chỗ thả hờ cạnh sườn | Lắng về pha Idle F0 |
| 24 | = Idle F0 | | | | |

Nhịp: 5F lấy đà · 4F vung (có frame bắn) · 4F lắng · 11F về. So ref: co lấy đà 7→5, vung 5→4, bỏ phần giữ dài (14→4) vì
game bắn liên tục; về 14→11.

**Đọc từ camera trên cao [suy luận]:** cung vung phải đi **qua bên phải đầu** (không ngay trên đỉnh đầu) để không bị cái
đầu to che; trượng lúc bắn nằm ngang hẳn (nhìn từ trên là một vạch dài chĩa về mục tiêu).

**Điểm bắn cho dev:** F9 (tỉ lệ 0,375), vị trí `DEF_WeaponEnd_R` (đầu trượng, lệch phải tâm người ~0,1 m, trước người ~1,3 m, cao ~0,9 m), hướng +Z
của nhân vật. Hướng bay do code quyết định; anim chỉ bảo đảm đầu trượng chĩa thẳng trước ở F9.

**Rig khi dựng:** tay trái bật IK ở F5–F14 (match FK→IK ở frame giữ, kiểm frame chuyển không giật), hoặc giữ FK và key
từng frame F7–F13, đo găng → cán ≤ 1–2 cm. Mặt trăng + quả cầu đầu trượng giữ hướng xoay như Idle (không xoay trượng
quanh trục) trừ khi user muốn khác.

## E. Cần hỏi [?]

1. PA A (hai tay như ref) hay B (một tay)?
2. Có cần frame smear F8 (trượng vượt ngang rồi bật về) không, hay giữ sạch?
3. Bắn liên tục: game có phát Attack nối Attack không (đòn sau bắt đầu ngay F24 của đòn trước)? Nếu có, F0/F24 phải trùng Idle F0 tuyệt đối (đang thiết kế như vậy). Xuất 24 hay 25 frame?
4. Ref lúc bắn: mình đọc là tay sau ở hông, tay trước đỡ giữa cán, nhưng góc ngang khó phân biệt tay nào trước. Windy chân phải trước + tay phải sau, tay trái trước là thế vặn chéo (đã tính bằng xoay ngực 30–40°). Có muốn đổi: tay phải trước, tay trái giữ đuôi không?
5. Nếu game tăng tốc đánh nhiều (đòn < 0,5 s), có cần bản tối giản (lấy đà thấp, không vung qua đầu) không?
