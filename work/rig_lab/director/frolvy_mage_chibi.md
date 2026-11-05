# Director log – frolvy_mage_chibi (rig Frolvy)

## Director – pháp sư chibi (Frolvy) fit skeleton v1 – mốc rig-joints – 2026-10-30
**Kết luận: Cần sửa**
Ý chính: Thân, chân, cánh tay đặt đúng giải phẫu và tỉ lệ chibi. Chỉ joint Weapon sai: sai chỗ nắm và sai trục, nên gậy sẽ xuyên lòng bàn tay.

### Lỗi (nặng → nhẹ)
| # | Mức | Khớp | Bộ phận | Lỗi | Loại | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | A | Weapon/WeaponEnd | tay phải + gậy | Weapon (-0.79,1.165,0) nằm ở đoạn ngón (sau knuckle -0.77), ngay trục giữa bàn tay. Trục +Y dọc lại xuyên qua lòng bàn tay úp (ngón cái ở z+, y-) | vị trí khớp / trục prop | Dời Weapon về khe nắm dưới lòng bàn tay, khoảng (-0.745, 1.12, 0.03). Đặt trục dọc gậy theo Z (+Z ra trước), WeaponEnd khoảng (-0.745, 1.12, 0.32). Chốt bằng cách gập Middle1/2 và Thumb thành nắm đấm, đặt gậy vào tay rồi snap Weapon theo tâm cán | [đo] knuckle -0.77, ngón cái y 1.085–1.13 z 0.06–0.126; toạ độ đề xuất là [mắt] |
| 2 | B | Weapon | gậy | Chưa chọn điểm nắm trên gậy (gậy dài 2.15, cao hơn nhân vật) | prop | Chọn điểm nắm khoảng y 0.85–1.0 trên gậy để đầu gậy cao hơn đầu nhân vật; ghi offset | [mắt] |
| 3 | B | — | áo choàng, phụ kiện vai | Không có xương cho áo choàng dài tới gối: gán cứng vào Chest sẽ xuyên đùi khi gập hông hoặc bước | thiếu xương phụ | Thêm chuỗi Cape 2–3 khớp (giữa sau + 2 bên) làm con Chest. Phụ kiện vai gán cứng vào Scapula_R/L | [mắt] |
| 4 | C | Shoulder | vai | x -0.2 nằm ở mép chỗ nối tay–thân (0.15–0.2) | vị trí khớp | Có thể dời vào -0.18 | [đo] |
| 5 | C | Wrist | cổ tay | -0.655 lệch 0.5 cm vào phía bàn tay so với chỗ thắt (-0.625..-0.65) | vị trí khớp | Dời tới -0.645 | [đo] |

### Giữ nguyên
- Cột sống z -0.015 ≈ 40% độ dày tính từ lưng. Neck 1.24 và Head 1.33 khớp chỗ thắt cổ.
- Root 0.58 / Hip 0.53, cao hơn đũng 3–5 cm. Đùi/ống chân = 0.24/0.20 ≈ 1.2. Gối z +0.015 gập sẵn ra trước. Toes ở ụ bàn chân (70%). Heel ở sàn.
- Khuỷu z -0.025 gập sẵn ra sau. Cánh tay trên/cẳng tay 0.23/0.225. Chuỗi ngón cái và ngón giữa nằm trong mesh găng.
- Tổng 64 joint = 24 fit + 40 DEF (đã bỏ Weapon_L), khớp số.

## Director – pháp sư chibi (Frolvy) xương áo choàng + 2 dải – mốc rig-joints vòng 2 – 2026-10-30
**Kết luận: Duyệt** (chỉ phần mới; còn B/C)
Ý chính: 3 chuỗi áo và 2 chuỗi dải đều nằm trên mặt vải, số đốt đủ cho game chibi. Còn lại chủ yếu là việc cần làm đúng khi skin.

### Lỗi (nặng → nhẹ)
| # | Mức | Khớp | Bộ phận | Lỗi | Loại | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | B | CapeSide1_R/L | gốc vạt bên | Gốc (-0.255,1.13,-0.095) nằm ngoài Shoulder (x -0.18), ngay sau bắp tay và dưới miếng vai. Miếng vai gán cứng Scapula, còn gốc vạt bên lại là con Chest, nên khi nhún vai sẽ hở giữa hai phần. Đỉnh bắp tay cũng dễ ăn weight của CapeSide1. | gốc chuỗi / rò weight | Đổi cha CapeSide1_R/L sang Scapula_R/L, giữ nguyên toạ độ. Khi skin: hàng đỉnh trên cùng của vạt gán 100% cho Scapula (hoặc Chest), khoá UpperArm khỏi đỉnh áo. Thử bằng UpperArm Z 90° và giơ ra trước 60°. | [đo] Δx 7,5 cm so với vai |
| 2 | B | Kim cương ±0.39 | phụ kiện | Không gán vào End vì xương cuối không skin | gán cứng | Gán cứng 100% vào CapeSide4_R/L để kim cương lắc theo đốt cuối | [đo] |
| 3 | C | CapeMid4 | tấm lưng giữa | z -0.26 nằm trước mặt vải 1–5 cm ở y 0.5–0.55 (vải ở -0.27..-0.31). Đốt cuối ngắn: 0.22/0.22/0.16/0.10 | vị trí khớp | Dời về (0, 0.54, -0.28) để đốt đều hơn và nằm trên mặt vải | [đo] |
| 4 | C | — | giữa tấm lưng và vạt bên | Đáy áo cách 0.3–0.4 m giữa CapeMid (x 0) và CapeSide (x 0.33–0.39), đỉnh ở giữa sẽ blend 50/50. Chưa cần thêm chuỗi. | thiếu xương phụ | Chỉ thêm chuỗi CapeIn_R/L (x ±0.17, z ≈ -0.27, 4 đốt) nếu clip chạy/đá lùi thấy đùi xuyên vùng x ±0.1–0.2 | [mắt] |
| 5 | C | Ribbon4 → RibbonEnd | đuôi dải | Đốt cuối 0.39 (các đốt khác 0.30) ôm luôn mũi nhọn rời (-1.22..-1.44), nên mũi không vẫy riêng được | số đốt | Thêm khớp ở z -1.23 (đầu mũi nhọn) nếu muốn mũi nhọn vẫy riêng; không thêm thì gán cứng mũi vào Ribbon4 | [đo] |
| 6 | C | Ribbon1 | gốc dải | Gốc z -0.15 nằm trong áo 3 cm (áo ở y 1.09 ≈ -0.18) và gần CapeMid1. Đỉnh gốc dải dễ ăn weight của Cape. | rò weight | Khi skin: hàng đỉnh gốc dải gán Ribbon1/Chest và khoá Cape* | [đo] |

### Giữ nguyên
- CapeMid1–3, cả chuỗi CapeSide, End ở góc dưới (-0.395, 0.33): đều trùng mặt vải trong khoảng 1–2 cm. Đốt vạt bên đều (0.23/0.22/0.20/0.17).
- Dải: 4 đốt 0.30 m, thẳng đúng tâm x ±0.146, End trùng mũi -1.44.
- Phụ kiện vai và cổ không làm xương, gán cứng.

### Định hướng vòng sau
- Chưa kiểm trục và hướng local của các khớp mới, và đối xứng _L trong Studio (chỉ xem 2 ảnh back/top). Bước skin cần ảnh test UpperArm 90°, CapeSide1 xoay X 30°, Ribbon2 xoay Y 30°.
- Đếm lại 104 = 64 + 20 khớp mới không phải End × 2 (fit + DEF)? Xác nhận End có trong file export.

## Director – pháp sư chibi (Frolvy) skin v2 (dọn luật vùng) – mốc rig-skin – 2026-11-03
**Kết luận: Duyệt** (chỉ phần đã đo: thân, chân, đầu–cổ, vai/hông bên đang test; chấm bằng số, không xem ảnh; còn B)
Ý chính: Hai lỗi nặng của bản cũ đã hết: hạ vai làm méo đầu (5.5 cm → 0) và nhấc đùi kéo bụng (9.8 → 0.8 cm). Cross-side = 0, cổ áo 100% Chest. Gối dày hơn (0.59 → 0.79). Các ca tăng thêm vài cạnh bad (spine30, head40, hip_fwd80) chỉ là giãn nhẹ trên lưới thưa, không phải rò weight.

### Lỗi (nặng → nhẹ)
| # | Mức | Khớp | Bộ phận | Lỗi | Loại | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | B | mọi khớp _L | hai bên | Bảng test chỉ có một bên. Bản cũ là skin tự động + sửa khuỷu, nên chưa chắc hai bên đối xứng | đối xứng | Đo chênh weight giữa từng cặp đỉnh đối xứng (max \|Δw\| theo joint, cần < 2%). Chạy lại shoulder_down70, elbow120, hip_fwd80, knee110 cho _L. Lệch thì chép R→L rồi chạy lại các luật | thiếu số đo |
| 2 | B | Finger*/Thumb, handPose 2 | bàn tay phải (cầm gậy) | Đã dồn cứng 75 đỉnh về joint gần nhất mà không hammer trước (skill: hammer vài lần rồi mới dồn). Chưa test nắm tay, trong khi tay phải luôn nắm gậy | rò weight / giữ thể tích | Test handPose 2 + curl: đo cạnh bad ở đốt ngón, kiểm gậy nằm trong lòng tay (dùng `thumb_into_palm`). Có gãy ở đốt thì hammer 0.5 × 2 trong vùng ngón rồi chạy lại luật 1.5 cm | thiếu số đo |
| 3 | B | Shoulder_R, ranh \|x\| = 0.13 | vai/nách | Trong vùng thân, Shoulder bị giới hạn ≤ 0.3. Qua \|x\| > 0.13 (vùng tay) thì không còn giới hạn, nên weight có thể nhảy bậc trên đúng một cạnh dài 10–18 cm. Ba cạnh bad của shoulder_down70 có thể nằm ở đây | chuyển weight | In weight Shoulder của các đỉnh có \|x\| 0.10–0.20, y > 1.0. Nhảy > 0.3 giữa hai đỉnh kề nhau thì đổi giới hạn thành ramp tới 0.18 (khớp vai) | [đo] cần xác nhận |
| 4 | B | Hip_R X 80° | đùi + vạt áo | Max 1.73 / min 0.46 (7 cạnh). Áo chỉ có 1 chuỗi CapeMid (người dùng chọn), nên khi nhấc đùi, vạt bên đứng yên và đùi có thể xuyên qua | xuyên / giữ thể tích | Ghi 7 cạnh bad nằm ở đâu (bẹn trước hay mông sau). Đo khoảng cách đùi–vạt áo ở hip_fwd80 và hip_fwd45. Nếu xuyên ở 45° (góc hay dùng) thì đưa người dùng chọn giữa thêm chuỗi vạt bên và chịu xuyên | [đo] 1.73 |
| 5 | B | — | mesh rời | Không thấy báo cáo bước làm cứng shell (kim cương, phụ kiện vai, cổ). Đã bỏ CapeSide thì kim cương giờ gán vào đâu? Skill bắt bước này chạy cuối cùng, sau mọi lần chia theo chiều cao | gán cứng | Liệt kê shell → joint. Kiểm mỗi shell 100% một joint sau lượt dọn này (chia theo y có thể đã chẻ shell) | thiếu số đo |
| 6 | C | Ribbon1/Ribbon3, CapeMid1 | gốc dải, vạt bên | far: Ribbon3 4/4, CapeMid1 18. Gốc dải nằm sát áo (vòng trước #6). Chưa rõ đỉnh gốc dải có ăn Cape không | rò weight | Hàng đỉnh gốc dải chỉ Ribbon1/Chest. Kiểm 4 đỉnh far của Ribbon3 có phải nằm ở đoạn Ribbon2/4 không. CapeMid1 18 chấp nhận theo quyết định 1 chuỗi | [đo] |
| 7 | C | Neck/Head 40°, Spine 30° | dải cổ, bụng | head40 max 1.52 = dải nối cổ áo giãn, skill chấp nhận (không smooth cổ áo với Neck). spine30 min 0.47 = nén ở bụng, ramp 26 cm chỉ ăn khoảng 2 hàng đỉnh | giữ thể tích | Không cần sửa. Nếu clip cúi/vặn nhiều thấy gãy thì nới Spine1→Chest thành 0.80–1.08 | [đo] |
| 8 | C | Elbow 120° | khuỷu | 10 bad, min 0.29 / max 2.70. Đã chốt vòng trước, không tính là lỗi. Cũng kiểm lại thêm ở 90° (góc hay dùng) | giữ thể tích | Chỉ báo số bad ở 90° | [đo] |

### Giữ nguyên
- Vùng Head/Neck (y ≥ 1.33 hoặc y > 1.21 & |x| < 0.12), cổ áo 100% Chest: head-warp = 0.
- Hip→Knee 0.32–0.36 (chọn theo độ dày gối khi gập), Knee→Ankle 0.04–0.22, Toes theo z: ankle40 0 bad.
- Phần háng về Root, Root dưới 0.50 chuyển sang Hip: torso-move 0.8 / 0.3 cm.
- Cross-side 0; tối đa 4 ảnh hưởng; gậy 100% Weapon_R.

### Định hướng vòng sau
- Bổ sung số đo bên _L / đối xứng, test nắm tay cầm gậy, bảng shell → joint. Cả 3 sạch thì skin coi như xong, còn lại để thử bằng clip thật (`pose_stretch` với pose của người dùng).
- Xác nhận tổng weight = 1 sau khi bỏ ảnh hưởng < 1%.

## Director – pháp sư chibi (Frolvy) skin v3 (dải chuyển gối/khuỷu/cổ tay) – mốc rig-skin vòng 3 – 2026-11-03
**Kết luận: Cần sửa**
Ý chính: Nới dải chuyển đúng hướng: độ gãy khuỷu giảm 119 → 49°, gối 141 → 91°, max giãn khuỷu 2.5 → 1.5. Tuy vậy, khuỷu 90° (góc hay dùng) vẫn có cạnh bị nén còn 6% độ dài, và gối mất thể tích (0.84 → 0.66). Hai ảnh có quá nhiều overlay joint, góc chéo che mặt trong khớp, nên chưa thấy được đúng chỗ người dùng chê (nếp dồn, móp ở mặt trong).

### Lỗi (nặng → nhẹ)
| # | Mức | Khớp | Bộ phận | Lỗi | Loại | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | A | Elbow_R 90° | khuỷu, mặt trong | Vẫn 6 cạnh bad, min 0.06: một cạnh gần như bẹp hẳn. Đây đúng loại "nếp dồn một vòng" người dùng chê, ở góc hay dùng. Ảnh b_elbow2 không thấy mặt trong khuỷu | giữ thể tích | In vị trí 6 cạnh (trong/ngoài khuỷu, y). Nếu nằm ở mặt trong thì thử dải lệch về cẳng tay, ví dụ (−0.09, +0.10), hoặc thêm bù thể tích bằng một vòng đỉnh mặt trong có weight 50/50 cố định. Chấm lại min ≥ 0.3 ở 90° | [đo] min 0.06 |
| 2 | A | Knee_R 90° | gối | Độ dày 0.84 → 0.66: gối bị thắt như ống gấp, đúng chữ "móp" của người dùng. Ảnh chéo trước-phải nhìn mặt trước tròn đẹp, nhưng không thấy khoeo và cạnh bên | giữ thể tích | So hai phương án bằng ảnh, không chỉ bằng số: (−0.19,+0.12) và (−0.14,+0.09) (103° / 0.71). Mục tiêu độ dày ≥ 0.75 và độ gãy ≤ 100. Nếu không đạt cả hai thì đưa 2 ảnh để người dùng chọn | [đo] 0.66 |
| 3 | A | gối, khuỷu | ảnh kiểm | Chưa đủ ảnh để duyệt bằng mắt (luật: chấm skin bằng ảnh cận 3 góc). Người dùng chê bằng mắt nên cũng phải duyệt bằng mắt | thiếu ảnh | Render khuỷu 90/120 và gối 90/110: trước, bên, trên (thêm góc nhìn thẳng mặt trong khuỷu và khoeo). Ẩn joint/gizmo, ≥ 512 px, đặt cạnh bản v2 cùng góc | thiếu ảnh |
| 4 | A | — | các mục B của v2 | Chưa thấy báo cáo: test nắm tay cầm gậy (v2 #2), ramp Shoulder ở \|x\| 0.13 (#3), hip_fwd45 đùi–vạt áo (#4), bảng shell → joint (#5). (lặp lại từ v2) | thiếu số đo | Báo số cho cả 4 mục. Đã làm thì chỉ cần dán kết quả | thiếu số đo |
| 5 | B | Elbow 120° | khuỷu | Số cạnh bad 4 → 7, tuy max giảm (2.74 → 1.52). Chưa có min | giữ thể tích | Báo min. Nếu < 0.2 thì xử lý chung với #1 | [đo] |
| 6 | C | Wrist | cổ tay | Độ dày 0.58 không đổi: cổ tay gập 60° vẫn thắt. Chibi đeo găng thì chấp nhận được | giữ thể tích | Để đến khi có clip thật | [đo] |

### Giữ nguyên
- Khuỷu (−0.11, +0.06): độ gãy 49°, độ dày giữ 0.76. Cổ tay (−0.14, +0.09), cổ chân. Hông và vai giữ dải cũ (đã thử, các dải khác đều tệ hơn).
- Chép R→L, cross-side 0, tối đa 4 ảnh hưởng, đầu/thân không bị kéo. Phần này đóng được mục #1 của v2 (đối xứng).
- Ảnh gối: mặt trước gối tròn, không còn bậc gãy.

### Định hướng vòng sau
- Mục tiêu: khớp gập tròn và giữ thể tích ở 90°. Chấm độ gãy và độ dày cùng lúc, đừng đổi độ dày lấy độ mượt. Duyệt khi có ảnh 3 góc không overlay, và khuỷu 90 có min ≥ 0.3, gối có độ dày ≥ 0.75.
