# Báo cáo: cập nhật 6 Pet sang model mới (Infinite Defense, 18/11/2026)

Phiên "New Pet" trên máy Linux. Số thời gian lấy từ log phiên Claude (cách tính như các báo cáo trước: AI làm = từ prompt tới tin cuối của AI; người làm = khoảng giữa hai lượt, chỉ tính khi ≤ 15′). Số đo mesh và FBX lấy từ chính file. Mọi chỗ chưa kiểm được đều ghi rõ.

## 1. Tóm tắt
- Artist cập nhật model 5 Pet (Mecha Pup, Night Bat, Pebble Turtle, Tiny Chick, Wind Chameleon) ở thư mục mesh Pet_new của Unity. Tengu Swift (Pet 18) đổi mũi mặt nạ.
- Cả 6 Pet đã chuyển rig, skin, texture sang mesh mới, giữ nguyên key Idle / Attack đã chốt, rồi xuất lại 3 FBX (Base, Idle, Attack) và chép đè vào Unity (`Assets/3D_Art/3D_Animation/Pet_NEW`).
- Làm bằng 6 phiên con chạy song song trong Paseo, mỗi phiên một Pet và một cửa sổ Frolvy riêng. Phiên chính (tôi) so model, giao việc, kiểm FBX, chép sang Unity.
- Tổng AI làm **97,0′**; từ lúc mở phiên tới lúc chép xong vào Unity là 1 g 53′ (09:18 → 11:11 ngày 18/11), chưa kể việc WorkAI.
- Người làm **94,7′**: phiên chính 44,7′ (đo từ log) + 50′ ở các phiên con (bạn khai, chỉ thao tác tay trong Frolvy và feedback). Tổng AI + người: **191,7′ (3 g 12′)**.

## 2. Thời gian
| Phần | Lượt | AI làm | Người làm | Chờ trả lời |
|---|---:|---:|---:|---:|
| Phiên chính: so model, tạo / chỉnh phiên con, kiểm FBX, chép Unity | 13 | 11,0′ | 44,7′ | 0,1′ |
| Phiên con Pet 11 Mecha Pup | 7 | 18,5′ | **20′** (bạn khai) | – |
| Phiên con Pet 12 Pebble Turtle | 4 | 12,9′ | **5′** (bạn khai) | – |
| Phiên con Pet 13 Tiny Chick | 4 | 13,6′ | **5′** (bạn khai) | – |
| Phiên con Pet 15 Night Bat | 4 | 16,7′ | **5′** (bạn khai) | – |
| Phiên con Pet 16 Wind Chameleon | 4 | 16,8′ | **5′** (bạn khai) | – |
| Phiên con Pet 18 Tengu Swift | 4 | 7,5′ | **10′** (bạn khai) | – |
| **Tổng** | | **97,0′ (1 g 37′)** | **94,7′** (44,7′ phiên chính + 50′ phiên con) | |

- **Phiên chính (44,7′):** phần lớn là lúc người chờ và xem các phiên con chạy (tối đa 11′ mỗi lần), không phải toàn bộ là gõ hay sửa tay.
- **Phiên con, phần người = bạn khai (ngày 19/11):** Pet 11: 20′; Pet 12, 13, 15, 16: 5′ mỗi Pet; Pet 18: 10′. Số này **chỉ gồm thao tác tay trong Frolvy và feedback**, tổng 50′. Đây là số bạn tự ước lượng, không đo từ log.
- **Đối chiếu với log** (chỉ tính lúc bạn nghĩ / xem trước mỗi lượt bạn tự gõ trong Paseo, tối đa 15′): Mecha Pup 16,2′ (3 lượt), Tengu Swift 3,8′ (2 lượt), 4 Pet còn lại 0′ (bạn không gõ gì). Log không thấy được thao tác tay trong Frolvy nên số khai lớn hơn; dùng số khai làm số chính.
- **Phần người ở phiên chính (44,7′)** là lúc bạn chờ và xem các phiên con chạy, chỉ đạo, ra lệnh. Số này đo từ log. Phần này và số khai ở trên là hai việc khác nhau nên tôi cộng lại (94,7′); nếu bạn vừa chờ ở phiên chính vừa sửa tay ở phiên con cùng lúc thì có thể trùng một phần.
- **Người tự gõ trong phiên con (log, 5 lượt):** Mecha Pup 3 lượt ("mở control và xương lên cho tôi check", "rig của chó chưa về dáng gốc", "texture của chó đang bị lắp lộn"), Tengu Swift 2 lượt ("check file model FBX mới ở Unity", "không sửa, cập nhật model mới đi").
- **Tổng thực theo từng Pet (AI + người khai):** Mecha Pup 38,5′; Pebble Turtle 17,9′; Tiny Chick 18,6′; Night Bat 21,7′; Wind Chameleon 21,8′; Tengu Swift 17,5′. Cộng 6 phiên con: 136,0′. Cộng cả phiên chính: AI 97,0′ + người 94,7′ = **191,7′ (3 g 12′)**.
- Việc không tính vào Pet: WorkAI (kiểm kết nối, chia lại giờ GEK-2273: AI 1,7′, người 0,8′).
- Khoảng nghỉ > 15′ không tính: 09:52 → 10:49 (57′) và 11:11 → 11:51 (39′).
- Nguồn: `s_mesh_main/`, `s_mesh_pet11/` … `s_mesh_pet18/` (`timeline.md`, `stats.json`).

## 3. Model mới khác model cũ ra sao
| Pet | Đỉnh cũ → mới | Mảnh rời | Khác biệt chính | Cần xử lý |
|---|---|---|---|---|
| 11 Mecha Pup | 1628 → 1621 | 10 → 10 | hình giống hệt, texture / material mới | xoay lại mặt +Z (file mới quay ngược 180°) |
| 12 Pebble Turtle | 871 → 703 | 3 → 6 (4 mesh gộp thành 1) | gọn hơn, mai và đầu to hơn chút, lỗi non-manifold 8 → 0 | skin lại |
| 13 Tiny Chick | 788 → 517 | 2 → 2 | gọn hơn 35%, cùng cỡ | skin lại |
| 15 Night Bat | 1004 → 547 | 1 → 3 | gọn hơn 45%, cánh hẹp hơn (0,98 → 0,93) | skin lại; 2 mảnh 80 đỉnh là **cánh**, không phải mắt |
| 16 Wind Chameleon | 1271 → 749 | 4 → 4 (2 mesh gộp thành 1) | lưỡi dài hơn (tổng dài 0,97 → 1,20), thêm tấm đế phẳng dưới chân | xoay lại mặt +Z, skin lại, kiểm lưỡi |
| 18 Tengu Swift | 906 → 912 (thân) | – | mũi mặt nạ dài thêm ~6 cm, 888 đỉnh còn lại trùng bản cũ | thay thân, giữ quạt cũ |

UV và lưới (đo từ file): không con nào có UV tràn ô 0–1 hay mặt UV bị xẹp; UV khớp texture khi đặt lên ảnh. Nửa trái và nửa phải dùng chung UV ở Night Bat, Pebble Turtle, Tiny Chick, Wind Chameleon (Mecha Pup 91%, như bản cũ). Độ nét texture đều hơn bản cũ ở Night Bat, Pebble Turtle, Wind Chameleon; **Tiny Chick lệch hơn bản cũ** (có mảng nét hơn mảng khác 4–5 lần). Ảnh so sánh: `mesh_check/<Tên>.png`.

## 4. Kết quả từng Pet
| Pet | Idle | Attack (frame bắn) | So với bản chốt cũ |
|---|---|---|---|
| Mecha Pup | 48F, lặp | 24F (F9) | đỉnh lệch < 0,01 mm; control lệch tối đa 0,04° |
| Pebble Turtle | 48F, lặp | 36F (rụt đầu F10, khạc sỏi F15) | key giữ nguyên; đầu rụt không xuyên mai (xem bằng mắt) |
| Tiny Chick | 48F, lặp | 30F (F12) | key giữ nguyên |
| Night Bat | 48F, lặp | 30F (F13) | key giữ nguyên |
| Wind Chameleon | 48F, lặp | 30F (F13) | so từng kênh từng frame: lệch 0 |
| Tengu Swift | 48F, lặp | 30F (F12) | lệch 0,000 mm trên 888 đỉnh thân trùng + 141 đỉnh quạt; mũi mới cách quạt nhỏ nhất ~9 cm (Attack F12–F15) |

FBX xuất: 18 file (mỗi Pet Base + `_Idle` + `_Attack`). Kiểm cấu trúc trên file: Base có mesh, skin và BindPose, không có clip; Idle / Attack có đúng 1 clip, không mesh, số xương khớp Base; UnitScale 100. Đã so từng file với bản chép trong Unity: 18/18 khớp.

## 5. Quy trình đã làm
1. 09:18 – 09:24: so model mới với mesh cũ và rig Base đã chốt; kiểm UV và lưới, vẽ ảnh lưới cũ / mới.
2. 09:27 – 09:33: tạo phiên con. Lần đầu dùng subagent (không gõ trực tiếp được) nên đổi sang phiên Paseo; tôi cho phiên bắt đầu làm khi người dùng mới chỉ bảo tạo, người dùng dừng lại.
3. 09:40: người dùng chỉ thư mục file Frolvy của team (`tvc_source`); các phiên con bắt đầu làm thật. Mesh mới thay mesh cũ trong chính rig, joint / control / key giữ nguyên, bind skin ở pose 0.
4. 09:52: lắp texture mới; 10:49 tạo thêm phiên Pet 18.
5. 11:01 – 11:11: lệnh gộp `_v2` thành file gốc, bỏ bản cũ, xuất FBX; kiểm cấu trúc FBX; chép đè vào Unity.

## 6. Điểm mạnh
- Song song 6 Pet: 97′ AI làm gói trong khoảng 1 g 36′ đồng hồ (09:32 → 11:08).
- Key đã chốt giữ nguyên tuyệt đối (lệch 0 tới 0,04°), không phải làm lại anim.
- Có số đo thay vì chỉ nhìn: so đỉnh cũ / mới tới phần nghìn mm; tìm ra 2 con mesh mới quay ngược 180° trước khi skin.
- Chuẩn bị công cụ cho máy Linux (đổi `tools/frolvy_port.py` chạy được trên Linux), các phiên con ghi bẫy Frolvy vào `report_mesh_v2.md` cho lần sau.
- **Rig nhanh** (nhận xét của bạn).
- **Chỉnh sửa theo feedback nhanh với model lowpoly không yêu cầu quá cao** (nhận xét của bạn).
- **Cải thiện quy trình làm việc** (nhận xét của bạn): một người làm 100% thực tế mất 4–5 ngày để hoàn thành bộ Pet, còn với AI chỉ cần 3 ngày, chạy cùng lúc 12 phiên con.
- **Import FBX tốt, có thể fix bug file** (nhận xét của bạn).

## 7. Điểm yếu / sai sót (nói thẳng)
- **Làm quá lệnh:** người dùng chỉ bảo "tạo nhánh con", tôi cho các phiên bắt đầu làm ngay; người dùng phải ra lệnh dừng (lượt 7). Sau đó vẫn còn file nháp (`mecha_pup/v2/`, `tiny_chick/rig_v2/`, `pebble_turtle/v2/`…).
- **Chọn sai loại phiên lần đầu:** subagent không cho người dùng gõ trực tiếp, mất một vòng (09:27 → 09:31) để đổi sang Paseo.
- **Đoán sai khi viết brief:** tôi viết 2 mảnh 80 đỉnh của Night Bat "nhiều khả năng là mắt"; thực ra là cánh. Phiên con tự sửa, nhưng brief sai có thể dẫn phiên khác sai.
- **Frolvy trên Linux còn bẫy:** script cũ trỏ đường dẫn Windows; lưu sang file đã có trả về False, mở scene chỉ chạy khi scene sạch; PNG hiện lật dọc nên phải dùng bản lật; xuất FBX bake nên cửa sổ không còn bản gốc chưa bake (phải lưu `.fv` trước).
- **Chưa kiểm tới nơi:** chưa import vào Unity (chưa biết skin có vỡ, Copy Avatar có báo lỗi không), chưa playblast MP4, chưa gọi Director; skin chỉ xem bằng ảnh viewport ở các frame chính, chưa xoay mạnh từng khớp; Night Bat chưa đo xuyên giữa cánh gập và thân; Wind Chameleon chưa dò xuyên giữa đuôi cuộn và mào ở mọi frame.
- **Chưa xử lý:** tấm đế phẳng dưới chân Wind Chameleon (chưa rõ chủ ý hay đồ thừa), độ nét UV lệch của Tiny Chick, rig Mecha Pup "về dáng gốc" mới áp cho file rig, chưa áp cho Idle / Attack (bản Idle / Attack bind cũ khớp tuyệt đối bản chốt; áp thử lệch tối đa 2,9 cm).
- **Người phải bắt lỗi:** Mecha Pup bị phát hiện hai lỗi mà phiên con không tự thấy: rig chưa về dáng gốc (10:10) và texture bị lộn do Frolvy hiển thị PNG lật dọc (10:46, phiên con sửa bằng bản texture lật). Tengu Swift phải được người nhắc lại hướng làm (10:54).
- **Số đo giờ của người trong phiên con là số bạn khai**, không phải số đo: Frolvy không ghi lại thao tác tay, log phiên chỉ thấy các lượt bạn gõ.
- **Mecha Pup tốn người nhiều nhất** (20′, hơn cả AI 18,5′): phần lớn là bạn bắt lỗi rig và texture (xem trên).
- **Feedback còn tốn nhiều thời gian** (nhận xét của bạn): nhiều khi AI vẫn tự động sửa cả những phần không được yêu cầu sửa.
- **Làm anim lệch so với GDD** (nhận xét của bạn): đã có bước phân tích GDD và posing, nhưng qua bước pose và làm anim AI vẫn làm theo hướng khác, không giống GDD đã mô tả.
- **Bind skin và đặt joint còn lẫn lộn, bị lệch ở các Pet 4 chân** (nhận xét của bạn).
- **Còn nhiều hạn chế ở kỹ năng chỉnh mesh và chạy overlap** (nhận xét của bạn).

## 8. Người vẫn phải làm
| Khi nào | Làm gì |
|---|---|
| Đầu phiên | chỉ ra Pet nào đổi, chỉ đường dẫn mesh và thư mục file Frolvy |
| Giữa chừng | quyết định cách chạy (subagent hay Paseo), ra lệnh dừng khi tôi làm quá, góp ý rig Mecha Pup |
| Cuối | ra lệnh gộp / xuất FBX / chép Unity |
| Còn lại | mở Unity xem 6 Pet; báo artist độ nét UV Tiny Chick và tấm đế Wind Chameleon; dọn file nháp; quyết định đóng 6 phiên Paseo và cửa sổ Frolvy |

Gợi ý lần sau: nói rõ "chỉ tạo, chưa làm" khi tạo phiên con; đưa luôn đường dẫn thư mục Frolvy ngay từ đầu.

## 9. Số liệu các Pet làm lần đầu (11–25, 11–17/11) để đối chiếu

**Giới hạn:** log phiên Claude của Pet 11–23 nằm ở máy Windows (11–14/11), không còn trên máy này. Với 11 Pet đó **không có số phút AI / người**, chỉ có mốc lịch từ file và giờ ước lượng ghi trên WorkAI. Chỉ có phút thật cho Pet 25 (17/11) và Pet 16 (17/11, chỉ kiểm mesh). Nguồn: `../_review_pets_11_25/BAO_CAO.md`, `BAO_CAO.md` cùng thư mục.

### 9.1 Mốc lịch và giờ ước lượng (không phải giờ làm thật)
| Pet | Issue | Bắt đầu | Chốt | Khoảng lịch | Ước lượng WorkAI lúc giao | Giờ ghi trên WorkAI sau khi chia lại 30 g |
|---|---|---|---|---|---:|---:|
| 11 Mecha Pup | GEK-2355 | 11/11 16:13 | 13/11 15:38* | ~2 ngày | 1,3 g | 1,5 g |
| 12 Pebble Turtle | GEK-2356 | 11/11 16:24 | 13/11 15:38* | ~2 ngày | 1,3 g | 1,5 g |
| 13 Tiny Chick | GEK-2357 | 12/11 08:43 | 13/11 15:38* | ~1,5 ngày | 1,3 g | 1,5 g |
| 14 Lucky Neko | GEK-2358 | 14/11 10:59 | 14/11 16:03 | 5 g 04′ | 1,5 g | 1,7 g |
| 15 Night Bat | GEK-2359 | 12/11 10:32 | 13/11 15:41 | ~1 ngày | 1,7 g | 1,9 g |
| 16 Wind Chameleon | GEK-2360 | 12/11 10:42 | 13/11 15:38* | ~1 ngày | 1,7 g | 1,9 g |
| 17 Pinchy Balboa | GEK-2361 | 13/11 10:38 | 13/11 15:29 | 4 g 51′ | 1,7 g | 1,9 g |
| 18 Tengu Swift | GEK-2362 | 13/11 10:38 | 13/11 16:50 | 6 g 12′ | 2,0 g | 2,2 g |
| 19 Kabuto Striker | GEK-2363 | 13/11 10:40 | 13/11 16:50 | 6 g 10′ | 1,7 g | 1,9 g |
| 22 Steam-Pug Turbo | GEK-2366 | 13/11 13:45 | 14/11 10:14 | qua đêm, ~4 g giờ làm | 1,7 g | 1,9 g |
| 23 Kitsune Nine-Mist | GEK-2367 | 13/11 13:45 | 14/11 15:55 | ~1 ngày | 2,5 g | 2,8 g |
| 25 Chrono Ouroboros | GEK-2369 | 14/11 (idle v1) | 17/11 14:46 | 14/11 + 17/11 | 2,3 g | 2,6 g |
| Xuất FBX 15 Pet vào Unity | GEK-2370 | | | | 2,0 g | 2,2 g |
| Sửa 6 Pet do mesh mới (báo cáo này) | GEK-2527 | 18/11 09:18 | 18/11 11:11 | 1 g 53′ | 4,0 g | 4,5 g |
| **Tổng subtask GEK-2273** | | | | | **26,7 g** | **30,0 g** |

\* Bốn Pet cùng giờ chốt 15:38 ngày 13/11 là lúc chạy công cụ chốt hàng loạt, không phải giờ xong thật. Khoảng lịch tính cả lúc chờ, chạy song song và việc khác xen vào.

### 9.2 Số phút thật đo được từ log (Pet làm lần đầu)
| Hạng mục | Lượt | AI làm | Người làm | Tổng thực |
|---|---:|---:|---:|---:|
| Pet 25 Chrono Ouroboros v2 (17/11) | 18 | 69,3′ | 51,3′ | 120,6′ (2 g 01′) |
| Pet 16 Wind Chameleon (17/11, kiểm mesh mới, không làm anim mới) | 7 | 6,2′ | 23,9′ | 30,2′ |
| Điều phối Pet qua WorkAI (tạo phiên con, kiểm FBX, chép FBX) | 6 | 3,0′ | 0,9′ | 3,9′ |
| Tổng ba hạng mục trên | 31 | 78,5′ | 76,1′ | 154,6′ |

Pet 25 theo giai đoạn: rig v2 6,0′ AI; rig v3 5,3′ + 2,2′ người; pose idle 16,6′ + 23,2′; idle lơ lửng 12,2′ + 10,4′; attack 24,9′ + 12,7′; chốt + xuất 4,3′ + 2,7′. Phần Pet 25 làm trên máy Windows ngày 14/11 (idle v1–v6, attack v1) không có log nên **chưa gồm**.

### 9.3 Đối chiếu lần đầu với lần cập nhật mesh
| Pet | Lần đầu: ước lượng WorkAI (giờ) | Lần đầu: số phút đo được | Lần cập nhật mesh: AI làm | Lần cập nhật mesh: người làm (khai) |
|---|---:|---|---:|---:|
| 11 Mecha Pup | 1,3 | không đo được | 18,5′ | 20′ |
| 12 Pebble Turtle | 1,3 | không đo được | 12,9′ | 5′ |
| 13 Tiny Chick | 1,3 | không đo được | 13,6′ | 5′ |
| 15 Night Bat | 1,7 | không đo được | 16,7′ | 5′ |
| 16 Wind Chameleon | 1,7 | không đo được | 16,8′ | 5′ |
| 18 Tengu Swift | 2,0 | không đo được | 7,5′ | 10′ |
| 25 Chrono Ouroboros | 2,3 | 120,6′ (AI 69,3′ + người 51,3′) | không đổi mesh | – |
| **6 Pet cập nhật** | **9,3 g** | | **86,0′ (trung bình 14,3′ mỗi Pet)** | **50′ (trung bình 8,3′ mỗi Pet)** |

- Mười một Pet làm lần đầu (11–23) cộng ước lượng WorkAI lúc giao là 18,4 giờ. Đó là số **ước lượng**, không phải số đo; không cộng với số phút trong báo cáo này.
- Con số duy nhất so được: Pet 25 làm mới hoàn toàn tốn AI 69,3′; cập nhật mesh một Pet trung bình 14,3′ AI + 8,3′ người (khai), tức khoảng 22,7′ mỗi Pet, bằng khoảng một phần năm tổng 120,6′ của Pet 25. Lưu ý Pet 25 có thêm pose idle và attack, còn cập nhật mesh giữ nguyên key, nên không phải cùng loại việc.
- Muốn có số đo thật cho Pet 11–23: chép thư mục log phiên của dự án AI_animation từ máy Windows (`C:\Users\<tên>\.claude\projects\`) sang máy này rồi đo lại; hoặc bạn khai số giờ gần đúng mỗi Pet, ghi riêng một cột "bạn khai".

## 10. Video playblast (24 clip của 12 Pet)

Thư mục `playblast/` (mỗi clip có `.mp4` và ảnh bìa `.jpg`), render sáng 18/11 lúc 09:20 – 09:24 từ các file `.fv` đã chốt trước đó, camera 3/4 nhìn từ trên xuống, 1280×720, 30 fps, đã ẩn control. Trang `BAO_CAO_MESH_MOI.html` cùng thư mục đã nhúng sẵn 24 video để xem trực tiếp.

**Cập nhật 19/11:** video Idle của Pet 11 Mecha Pup bị lỗi nên đã render lại từ file `.fv` mới (model mới, có texture, 48F). 23 video còn lại giữ nguyên.

**Lưu ý quan trọng:** các video còn lại quay **trước khi cập nhật mesh**, nên hình dáng là model cũ, màu xám, chưa có texture. Với 6 Pet đã cập nhật (11, 12, 13, 15, 16, 18), chuyển động trong video vẫn là chuyển động hiện tại vì key không đổi (đã so số, mục 4), nhưng hình model sẽ khác. **Chưa có playblast cho model mới.**

| Pet | Idle | Attack | Cập nhật mesh 18/11 |
|---|---|---|---|
| 11 Mecha Pup | [Idle 48F, render lại 19/11](playblast/Pet_11_Mecha_Pup_Idle.mp4) | [Attack 24F](playblast/Pet_11_Mecha_Pup_Attack.mp4) | có |
| 12 Pebble Turtle | [Idle 48F](playblast/Pet_12_Pebble_Turtle_Idle.mp4) | [Attack 36F](playblast/Pet_12_Pebble_Turtle_Attack.mp4) | có |
| 13 Tiny Chick | [Idle 48F](playblast/Pet_13_Tiny_Chick_Idle.mp4) | [Attack 30F](playblast/Pet_13_Tiny_Chick_Attack.mp4) | có |
| 14 Lucky Neko | [Idle 48F](playblast/Pet_14_Lucky_Neko_Idle.mp4) | [Attack 30F](playblast/Pet_14_Lucky_Neko_Attack.mp4) | không |
| 15 Night Bat | [Idle 48F](playblast/Pet_15_Night_Bat_Idle.mp4) | [Attack 30F](playblast/Pet_15_Night_Bat_Attack.mp4) | có |
| 16 Wind Chameleon | [Idle 48F](playblast/Pet_16_Wind_Chameleon_Idle.mp4) | [Attack 30F](playblast/Pet_16_Wind_Chameleon_Attack.mp4) | có |
| 17 Pinchy Balboa | [Idle 48F](playblast/Pet_17_Pinchy_Balboa_Idle.mp4) | [Attack 30F](playblast/Pet_17_Pinchy_Balboa_Attack.mp4) | không |
| 18 Tengu Swift | [Idle 48F](playblast/Pet_18_Tengu_Swift_Idle.mp4) | [Attack 30F](playblast/Pet_18_Tengu_Swift_Attack.mp4) | có (mũi mặt nạ) |
| 19 Kabuto Striker | [Idle 48F](playblast/Pet_19_Kabuto_Striker_Idle.mp4) | [Attack 30F](playblast/Pet_19_Kabuto_Striker_Attack.mp4) | không |
| 22 Steam-Pug Turbo | [Idle 48F](playblast/Pet_22_Steam_Pug_Turbo_Idle.mp4) | [Attack 30F](playblast/Pet_22_Steam_Pug_Turbo_Attack.mp4) | không |
| 23 Kitsune Nine-Mist | [Idle 48F](playblast/Pet_23_Kitsune_Nine_Mist_Idle.mp4) | [Attack 30F](playblast/Pet_23_Kitsune_Nine_Mist_Attack.mp4) | không |
| 25 Chrono Ouroboros | [Idle 72F](playblast/Pet_25_Chrono_Ouroboros_Idle.mp4) | [Attack 40F](playblast/Pet_25_Chrono_Ouroboros_Attack.mp4) | không |

- Còn sót vài ký hiệu IK nhỏ ở chân (Pet 11 thấy rõ nhất), vì Frolvy không cho ẩn tay cầm IK.
- Script dựng lại: `tools/pet_playblast.py` (Linux). Muốn có video cho model mới, render lại 6 Pet đã cập nhật từ các file `.fv` mới (khoảng vài phút mỗi Pet, cần mở Frolvy).

## 11. File
| File | Nội dung |
|---|---|
| `mesh_check/<Tên>.png` | lưới cũ / mới, UV đặt lên texture (5 ảnh) |
| `s_mesh_main/`, `s_mesh_pet11/` … `s_mesh_pet18/` | từng lượt của phiên chính và 6 phiên con |
| `work/infinite_defense/pets/<tên>/report_mesh_v2.md` | báo cáo chi tiết từng Pet (6 file) |
| `Pet_<ID>_<Tên>/` trong `tvc_source/3D ANIM/EndlessKicker/` | `.fv` mới, 3 FBX, `tex/`, `CHOT.txt` |
| Unity `Assets/3D_Art/3D_Animation/Pet_NEW/Pet_<Tên>/` | 18 FBX đã chép đè |
