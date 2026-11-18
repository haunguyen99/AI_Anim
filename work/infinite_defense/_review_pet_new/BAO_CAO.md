# Báo cáo thời gian làm việc: Pet mới (Infinite Defense, máy Linux)

Tạo 18/11/2026 từ log phiên Claude. Mọi con số lấy từ log, không ước lượng.

## Cách tính
**Tính:**
- **AI làm:** từ lúc gửi prompt tới tin nhắn cuối của AI trong lượt.
- **Người làm:** khoảng từ lúc AI trả lời xong tới prompt kế tiếp (xem kết quả, sửa tay trong Frolvy, viết góp ý), chỉ tính khi khoảng này ≤ 15 phút.

**Không tính:**
- Khoảng giữa hai lượt dài hơn 15 phút (chờ, nghỉ, làm việc khác, qua đêm).
- Lúc chờ người trả lời câu hỏi của AI.
- Việc không phải Pet: chép file sang ổ khác, đẩy git `tvc_source`, chuyển ổ SSD, tích Done WorkAI, làm báo cáo.

## Kết quả
| Hạng mục | Lượt | AI làm | Người làm | **Tổng thực** |
|---|---:|---:|---:|---:|
| Pet 25 Chrono Ouroboros v2 (17/11) | 18 | 69.3′ | 51.3′ | **120.6′ (2 g 01′)** |
| Pet 16 Wind Chameleon (17/11) | 7 | 6.2′ | 23.9′ | **30.2′** |
| Điều phối pet qua WorkAI (tạo phiên con, kiểm FBX đã chốt, chép FBX) | 6 | 3.0′ | 0.9′ | **3.9′** |
| **Tổng Pet mới** | **31** | **78.5′** | **76.1′** | **154.6′ (2 g 35′)** |

Anim / rig / mesh thuần (không tính dòng điều phối): **150.7′ (2 g 31′)**.
Tỉ lệ: AI làm 51%, người làm 49%.

## Pet 25 theo giai đoạn
| Giai đoạn | AI làm | Người làm | Tổng thực |
|---|---:|---:|---:|
| Rig v2 + dựng lại | 6.0′ | 0′ | 6.0′ |
| Rig v3 | 5.3′ | 2.2′ | 7.6′ |
| Pose idle (theo ref, Director chấm, sửa cho tròn) | 16.6′ | 23.2′ | 39.9′ |
| Idle lơ lửng | 12.2′ | 10.4′ | 22.6′ |
| Attack (rồng quay 1 vòng) | 24.9′ | 12.7′ | 37.6′ |
| Chốt + xuất 3 FBX + dọn thư mục | 4.3′ | 2.7′ | 7.0′ |
| **Tổng** | **69.3′** | **51.3′** | **120.6′** |

Lượt tốn nhất: Attack v5 (AI 13.9′ cho một lượt "cho quay có sức sống"), và pose idle sau khi Director chấm (người 13.3′ xem và sửa tay).

## Pet 16
Không làm anim mới. Phiên chỉ kiểm mesh mới có khác mesh trong rig không, kiểm UV và texture, rồi tư vấn khi sửa rig thì có phải sửa idle / attack không. Người làm 23.9′ chủ yếu là mở Frolvy và sửa rig riêng ngoài phiên.

## Không tính (để đối chiếu)
| Phần | Thời gian | Lý do bỏ |
|---|---:|---|
| Pet 25: chép file sang `tvc_source`, đẩy git bị từ chối (hỏi mật khẩu), hỏi file FBX rig | AI 13.0′ + người 1.4′ | không phải anim |
| Phiên WorkAI: tích Done, kết nối lại, chuyển ổ SSD, so dữ liệu, chuẩn bị báo cáo | AI 11.5′ + người 20.1′ | việc khác |
| Khoảng nghỉ giữa các lượt > 15′ ở phiên Pet 25 | dài nhất 1 g 42′ (11:58 → 13:40) | nghỉ / chờ |

## Pet 11–23: không đo được phút AI / người, chỉ có mốc lưu file
Log phiên Claude của 11 pet này nằm ở máy Windows (11–14/11), máy đó không còn nên **không tách được AI làm / người làm theo phút**. Đã tìm thêm ba nguồn khác, đều không thay được log:
- **WorkAI:** ô "thời gian đã làm" để trống, chỉ có giờ ước lượng khi giao việc.
- **Log Frolvy và file lưu tự động:** chỉ còn vài file ngày 14/11, không có thông tin theo pet.
- **Giờ lưu file:** có thật (bảng dưới), nhưng là giờ lưu **bản cuối**. Khoảng giữa hai mốc gồm cả lúc chờ, nghỉ và chạy song song nhiều pet, nên không phải giờ làm thực.

| Pet | Mốc lưu file (giờ máy) | Từ file đầu tới FBX cuối | Ước lượng WorkAI | Ghi chú |
|---|---|---:|---:|---|
| 11 Mecha Pup | 12/11: idle 08:46 · attack 09:25 · FBX 10:12–10:22 | 1 g 36′ | 1,3 g | file rig bị lưu lại 17/11 nên không thấy giờ dựng rig |
| 12 Pebble Turtle | 12/11: 3 file .fv cùng 08:49 · FBX 09:56–10:05 | 1 g 16′ | 1,3 g | .fv lưu một lượt, giờ dựng không rõ |
| 13 Tiny Chick | 12/11: rig + idle 09:07 · FBX 10:12 · attack làm lại 16:56–17:03 | 7 g 56′ | 1,3 g | attack làm lại buổi chiều |
| 14 Lucky Neko | 14/11: rig 10:59 · idle 14:37 · attack 16:27 · FBX 16:35 | 5 g 36′ | 1,5 g | một buổi, có nghỉ giữa rig và idle |
| 15 Night Bat | 12/11: rig 14:39 · idle 15:44 · 13/11: attack 08:26 · FBX 15:41 | ~25 g (qua đêm) | 1,7 g | qua đêm |
| 16 Wind Chameleon | 12/11: rig + idle 14:35 · 13/11: attack 10:59 · FBX 15:38 | ~25 g (qua đêm) | 1,7 g | FBX attack lưu trong đợt chốt hàng loạt 15:38 |
| 17 Pinchy Balboa | 13/11: rig 11:59 · skin tay sửa 13:41 · idle 14:48 · attack 15:16 · FBX 15:28 | 3 g 29′ | 1,7 g | nhiều vòng sửa skin, người tự bind lại |
| 18 Tengu Swift | 13/11: rig + idle 10:55 · attack + FBX 11:36 | 41′ | 2,0 g | file lưu gần nhau, giờ dựng không rõ |
| 19 Kabuto Striker | 13/11: tất cả file 10:42–10:43 | 1′ | 1,7 g | lưu một lượt, không suy ra được |
| 22 Steam-Pug Turbo | 13/11: rig 17:04 · 14/11: FBX 10:13–10:22 | ~17 g (qua đêm) | 1,7 g | qua đêm |
| 23 Kitsune Nine-Mist | 13/11: rig 17:11 · 14/11: idle 08:39 · attack v6 11:10 · FBX 11:13 | ~18 g (qua đêm) | 2,5 g | attack sửa tới v6 |
| **11 pet** | 12/11 → 14/11 | | **18,4 g** | ước lượng, không phải số đo |

Tổng Pet mới **chưa gồm** 11 pet này. Ước lượng WorkAI 18,4 g chỉ để tham khảo, không cộng vào 154,6′.

Muốn có số đo thật cho Pet 11–23, chỉ còn một cách: bạn cho mình số giờ gần đúng mỗi pet (hoặc phiên Claude còn lưu trong tài khoản Claude, nếu xuất được), mình thêm vào cột riêng, ghi rõ "bạn khai".

## Lưu ý
- Lúc người tự sửa pose trong Frolvy chỉ được tính phần nằm giữa hai prompt (tối đa 15′). Phần sửa lâu hơn không đo được từ log.
- Báo cáo trước (`_review_thoi_gian_thuc`, tổng 200.3′) gộp cả phiên WorkAI đầy đủ và việc chép file, git. Báo cáo này bỏ các phần đó nên số nhỏ hơn.

Số liệu nguồn: `s25/`, `s16/`, `sw2/` (từng lượt, `timeline.md` + `stats.json`), `tonghop.json`.

## Video playblast (24 clip: 12 pet × Idle + Attack)
Thư mục `playblast/` (mỗi clip có `.mp4` + ảnh `.jpg`). Render từ đúng file `.fv` đã chốt trong `tvc_source/3D ANIM/EndlessKicker/Pet_<số>_<tên>/`, camera 3/4 từ trên xuống, 1280×720, 30 fps, đã ẩn control.
- Pet 25: Idle 72F, Attack 40F. Pet 11: Idle 48F, Attack 24F. Pet 12: Attack 36F. Các pet còn lại: Idle 48F, Attack 30F.
- Còn sót vài ký hiệu IK nhỏ ở chân (Pet 11 thấy rõ nhất): Frolvy không cho ẩn tay cầm IK.
- Chưa có texture: file `.fv` chỉ có mesh xám.
- Script dựng lại: `tools/pet_playblast.py` (Linux).
