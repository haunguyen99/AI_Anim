# Báo cáo thời gian Pet 11–25 (Infinite Defense / Endless Kicker, 11–17/11/2026)

**Giới hạn số liệu:** log phiên Claude của Pet 11–23 nằm ở máy Windows (11–14/11), chưa có trên máy này. Vì vậy báo cáo **không tách được AI gen và người làm theo phút** cho 11 pet đó, chỉ có mốc lịch. Riêng **Pet 25** có log của ngày 17/11 nên tách được.
Khi chép thư mục log từ máy Windows sang (`C:\Users\<tên>\.claude\projects\<dự án AI_animation>\*.jsonl`), mình làm lại bản đo theo phút như các báo cáo trước.

## Nguồn
| Mốc | Lấy từ |
|---|---|
| Giao việc | WorkAI: 12 issue tạo lúc 11/11 16:01 (GEK-2355 → 2369) |
| Bắt đầu | File làm việc sớm nhất trong `work/infinite_defense/pets/<pet>/` (script rig / skin / anim) |
| Chốt | `CHOT.txt` trong `tvc_source/3D ANIM/EndlessKicker/Pet_<số>_<tên>/` |
| Ước lượng | Giờ ước lượng ghi trên issue WorkAI |
| Pet 25 theo phút | Log phiên Claude ngày 17/11 (`session_stats.py`) |

## Bảng tổng
| Pet | Issue | Bắt đầu | Chốt | Khoảng lịch | Ước lượng WorkAI |
|---|---|---|---|---|---:|
| 11 Mecha Pup | [GEK-2355](https://workai.horusjsc.com/issues/GEK-2355) | 11/11 16:13 | 13/11 15:38* | ~2 ngày | 1,3 g |
| 12 Pebble Turtle | [GEK-2356](https://workai.horusjsc.com/issues/GEK-2356) | 11/11 16:24 | 13/11 15:38* | ~2 ngày | 1,3 g |
| 13 Tiny Chick | [GEK-2357](https://workai.horusjsc.com/issues/GEK-2357) | 12/11 08:43 | 13/11 15:38* | ~1,5 ngày | 1,3 g |
| 14 Lucky Neko | [GEK-2358](https://workai.horusjsc.com/issues/GEK-2358) | 14/11 10:59 | 14/11 16:03 | 5 g 04′ | 1,5 g |
| 15 Night Bat | [GEK-2359](https://workai.horusjsc.com/issues/GEK-2359) | 12/11 10:32 | 13/11 15:41 | ~1 ngày | 1,7 g |
| 16 Wind Chameleon | [GEK-2360](https://workai.horusjsc.com/issues/GEK-2360) | 12/11 10:42 | 13/11 15:38* | ~1 ngày (FBX vào Unity từ 12/11) | 1,7 g |
| 17 Pinchy Balboa | [GEK-2361](https://workai.horusjsc.com/issues/GEK-2361) | 13/11 10:38 | 13/11 15:29 | 4 g 51′ | 1,7 g |
| 18 Tengu Swift | [GEK-2362](https://workai.horusjsc.com/issues/GEK-2362) | 13/11 10:38 | 13/11 16:50 | 6 g 12′ | 2,0 g |
| 19 Kabuto Striker | [GEK-2363](https://workai.horusjsc.com/issues/GEK-2363) | 13/11 10:40 | 13/11 16:50 | 6 g 10′ | 1,7 g |
| 22 Steam-Pug Turbo | [GEK-2366](https://workai.horusjsc.com/issues/GEK-2366) | 13/11 13:45 | 14/11 10:14 | qua đêm, ~4 g giờ làm | 1,7 g |
| 23 Kitsune Nine-Mist | [GEK-2367](https://workai.horusjsc.com/issues/GEK-2367) | 13/11 13:45 | 14/11 15:55 | ~1 ngày | 2,5 g |
| 25 Chrono Ouroboros | [GEK-2369](https://workai.horusjsc.com/issues/GEK-2369) | 14/11 (idle v1) | 17/11 14:46 | 14/11 + 17/11 | 2,3 g |
| **12 pet** | | 11/11 | 17/11 | **5 ngày làm việc** | **20,7 g** |

\* Bốn pet có cùng giờ chốt 15:38 ngày 13/11: đây là lúc chạy công cụ chốt hàng loạt, không phải giờ xong thật của từng con.

Khoảng lịch tính cả lúc chờ người xem, các phiên chạy song song và việc khác xen vào, nên **không phải** số giờ làm thực.

## Nhận xét
- **Làm song song:** sáng 13/11 có 5 pet mở cùng lúc (17, 18, 19, rồi 22, 23 lúc 13:45), trong khi 11, 15, 16 đang được chốt. Một người theo dõi nhiều phiên AI cùng lúc.
- **Pet "một buổi":** 14, 17, 18, 19 đi từ file đầu tiên đến chốt trong một buổi làm việc (4 g 51′ → 6 g 12′ lịch), gồm rig, skin, idle, attack, xuất 3 FBX.
- **Pet tốn nhiều vòng sửa:**
  - 17 Pinchy Balboa: tay cua tách khỏi găng, 7 vòng sửa skin, có vòng người tự bind lại skin; chốt Idle v7, Attack v9.
  - 23 Kitsune Nine-Mist: rig 73 joint, attack sửa tới v4 (đuôi cụp).
  - 25 Chrono Ouroboros: đổi rig v2 → v3, pose idle 4 lượt rồi người tự sửa, chốt Idle v14, Attack v6.
- **So với ước lượng WorkAI** (20,7 g cho 12 pet): chưa so được vì thiếu số giờ thực.

## Pet 25 ngày 17/11 (có log)
| Giai đoạn | Lượt | AI gen | Người |
|---|---:|---:|---:|
| Rig v2 + dựng lại | 1 | 6.0′ | 0′ |
| Rig v3 | 2 | 5.3′ | 2.2′ |
| Pose idle | 4 | 16.6′ | 23.2′ |
| Idle | 5 | 12.2′ | 10.4′ |
| Attack | 4 | 24.8′ | 12.7′ |
| Chốt + xuất | 2 | 4.3′ | 2.7′ |
| Việc khác | 4 | 13.0′ | 1.4′ |
| **Tổng** | **22** | **82.3′** | **52.7′** |

Chưa gồm phần làm trên máy Windows ngày 14/11 (idle v1–v6, attack v1). Chi tiết ở `../_review_workai_1117/BAO_CAO.md`.

## Việc cần để báo cáo đầy đủ
1. Trên máy Windows, chép cả thư mục log của dự án AI_animation trong `C:\Users\<tên>\.claude\projects\` sang máy này.
2. Báo mình, mình chạy lại thống kê theo phút cho 11 pet còn lại và thay bảng trên.
