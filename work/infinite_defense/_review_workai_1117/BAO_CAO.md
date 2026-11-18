# Báo cáo WorkAI + các phiên Pet (16–17/11/2026, máy Linux)

Phạm vi: các phiên Claude có log trên máy Linux. Gồm phiên điều phối **WorkAI** và 3 phiên con do WorkAI mở trong Paseo:
**Pet 25 Chrono Ouroboros v2**, **Pet 16 Wind Chameleon**, **Pet 25 Chrono Ouroboros** (bản gốc).

**Không có số liệu cho Pet 11–23.** Các pet này làm trên máy Windows từ 11/11 đến 14/11, nhưng log phiên của máy đó chưa chép sang máy này. Báo cáo chỉ dùng kết quả cuối của chúng (file chốt, issue Done).

Nguồn số liệu: `tools/report/session_stats.py` chạy trên log `~/.claude/projects/-home-ngocvb-Desktop-DataHDD-AI-animation/*.jsonl`.
Kết quả chạy ở `workai/` và `pet25/` (`stats.json`, `timeline.md`).

## 1. Thời gian

| Phiên | Lượt | AI gen | Người | Ghi chú |
|---|---:|---:|---:|---|
| Pet 25 Chrono Ouroboros v2 | 22 | 82.3′ | 52.7′ | 17/11 09:07 → 15:46. Có mặt 2 g 15′, bỏ 6 khoảng nghỉ (dài nhất 1 g 42′ lúc trưa) |
| WorkAI (điều phối) | 21 | 14.0′ | 21.0′ | 16/11 17:24 → 17/11 17:21 |
| Pet 16 Wind Chameleon | 7 | 6.2′ | 23.9′ | 17/11 14:22 → 15:42. Chỉ kiểm mesh, UV, texture, không làm anim |
| Pet 25 Chrono Ouroboros (gốc) | 1 | 0.2′ | 0′ | 16/11 17:16. Nhận việc rồi dừng; việc chuyển sang phiên v2 |
| **Tổng** | **51** | **102.7′** | **97.6′** | Tổng thời gian có mặt khoảng 3 g 20′ |

Pet 25 v2 theo giai đoạn:

| Giai đoạn | Lượt | AI gen | Người |
|---|---:|---:|---:|
| Rig v2 + dựng lại idle v7 / attack v2 | 1 | 6.0′ | 0′ |
| Rig v3 (22 joint) | 2 | 5.3′ | 2.2′ |
| Pose idle (v8 → v11, director, người tự sửa) | 4 | 16.6′ | 23.2′ |
| Idle (v12 → v14) | 5 | 12.2′ | 10.4′ |
| Attack (v3 → v6) | 4 | 24.8′ | 12.7′ |
| Chốt + xuất FBX + dọn thư mục | 2 | 4.3′ | 2.7′ |
| Việc khác (đẩy file sang tvc_source, git push, hỏi FBX rig) | 4 | 13.0′ | 1.4′ |

WorkAI theo giai đoạn:

| Giai đoạn | Lượt | AI gen | Người |
|---|---:|---:|---:|
| Đọc việc WorkAI, mở 2 phiên con, báo đường dẫn mesh mới | 1–4 | 2.2′ | 0′ |
| Kiểm FBX 12 pet + chép 36 FBX vào Unity `Pet_NEW` | 5–6 | 0.8′ | 0.9′ |
| Sự cố thư mục vào Thùng rác, khôi phục, nối lại WorkAI, tích Done | 7–15 | 9.2′ | 12.2′ |
| Hỏi về báo cáo, mở phiên mới từ SSD | 16–21 | 1.9′ | 8.0′ |

## 2. Số lần gen

- Pet 25 v2: 22 lượt prompt. 19 lượt có thay đổi file. Các lượt không đổi file: lượt 2 (hỏi hướng rig), lượt 9 (không tìm thấy pose người sửa) và lượt 22 (giải thích FBX rig).
- Bản `.fv` AI đã lưu: rig v3, pose v8 / v9 / v10 / v11, idle v7 / v12 / v13 / v14, attack v2 / v3 / v4 / v5 / v6.
  Khi chốt, AI chuyển các bản trung gian vào Thùng rác, nên không còn sổ phiên bản để đếm chính xác số lần ghi.
- Người ghi file 1 lần: tự sửa pose idle trong Frolvy và lưu đè lên `idle_v11_pose.fv` lúc 11:54.

## 3. Các giai đoạn chuyển biến lớn (Pet 25 v2)

| # | Lượt (giờ, gen) | Người yêu cầu / góp ý | AI thay đổi | Ảnh |
|---|---|---|---|---|
| 0 | ref | Gửi concept: rồng cuộn tròn quanh đồng hồ cát | — | `v/00_ref.png` |
| 1 | 1 (09:07, 6.0′) | WorkAI giao việc: làm tiếp Pet 25 | Dựng lại idle v7 và attack v2 trên rig v2 16 joint. Thân thẳng, uốn sóng S, **không giống concept vòng tròn** | `v/01_idle_v7_rigv2.png` |
| 2 | 2–3 (09:58–10:00, 5.3′) | "rig làm sao để thể hiện pose idle này đẹp nhất" → "rig thành v3" | Rig v3: 22 joint (Spine1–8, Tail1–7), mỗi khớp gập khoảng 18° khi cuộn đủ vòng. Pose vòng gần concept | `v/02_rigv3_vong.png` |
| 3 | 4 (11:01, 3.6′) | Pose idle theo ref | Pose v8, 1 key ở frame 0 | `v/03_pose_v8.png` |
| 4 | 5–6 (11:05–11:10, 9.0′) | "Gọi director ra check pose" → "sửa theo director" | Director kết luận **Cần sửa**: đầu quay ngược vào tâm vòng, cằm không gác lên vành, pose phẳng. Bản v10 được chấm "Duyệt kèm chỉnh nhỏ" | `v/04_pose_v10.png` |
| 5 | 7 (11:29, 4.0′) | "t thấy chưa tròn đâu" (**lỗi AI**, người phát hiện) | v11: đặt mọi khớp trên đường tròn bán kính 0,54 m, lệch tối đa 3 mm | `v/05_pose_v11.png` |
| 6 | 8–10 (11:41–11:54, 9.6′) | **Người tự sửa pose** trong Frolvy, rồi "dùng pose đó làm idle" | Idle v12, 72F, lơ lửng khoảng 5 cm, chuyển động số 8, frame 0 khớp 100% pose của người | `v/06_idle_v12.png` |
| 7 | 11–12 (13:40–13:43, 2.6′) | Không cho đồng hồ quay; đồng hồ nhấp nhô như đang bay | Idle v13, rồi v14 (bản chốt) | — |
| 8 | 13 (13:46, 3.4′) | Làm attack | Attack v3 | `v/07_attack_v3.png` |
| 9 | 14 (13:50, 4.0′) | Attack chỉ cần rồng quay 1 vòng quanh đồng hồ | Attack v4, 40F | `v/08_attack_v4.png` |
| 10 | 15 (14:03, **13.9′**) | Quay có sức sống hơn | Attack v5: dồn lực 2 đợt, thân lượn, vòng co dãn. **Người không dùng bản này** | `v/09_attack_v5.png` |
| 11 | 16 (14:19, 3.6′) | Bỏ v5, quay lại v4, làm mềm F32 → F40 | Attack v6 (bản chốt) | — |
| 12 | 17–18 (14:43–15:10, 4.3′) | "chốt", rồi giữ lại chỉ file chốt | Xuất 3 FBX (Base, Idle 72F, Attack 40F), ghi `CHOT.txt`, đưa các bản cũ vào Thùng rác | — |

## 4. Điểm mạnh của AI

- **Rig v3 trong 4.7′:** 22 joint, 22 control FK, check_rig sạch. Rig v2 giữ nguyên, không bị đụng.
- **Đo được độ tròn:** sau khi người chỉ ra, AI tìm được nguyên nhân (cộng độ cong đều cho mọi khớp) và đưa độ lệch khỏi đường tròn từ ±5 cm xuống 3 mm.
- **Loop và nối khít:** idle f72 = f0, mesh lệch 0. Attack f0 = f40 = pose của người.
- **Sửa nhỏ nhanh:** bỏ quay đồng hồ mất 1.2′, cho đồng hồ nhấp nhô mất 1.4′.
- **Director có cấu trúc:** bảng giống / khác ref, có mức độ và cách sửa. Bắt đúng lỗi đầu quay ngược.
- **WorkAI kiểm hàng loạt:** kiểm cấu trúc FBX của 12 pet trong 32 giây. Phát hiện socket đạn của Pet 12 tên `Muzzle`, khác các pet còn lại (`DEF_Muzzle_M`).
- **WorkAI tích Done 6 issue** (GEK-2358, 2366, 2367, 2369, 2370, 2273), sau đó cả nhóm Pet trên WorkAI là Done.

## 5. Điểm yếu của AI

- **Bắt đầu sai hướng:** lượt 1 dựng lại idle / attack trên rig v2 thân thẳng, không giống concept vòng tròn. Mất 6′ gen, và người phải hỏi tới thì mới chuyển sang rig v3.
- **Không tự thấy lỗi hình:** đầu quay ngược do director bắt; pose chưa tròn do người bắt. Pose idle mất 4 lượt, 16.6′ gen và 23.2′ người, và cuối cùng người vẫn tự sửa pose tay.
- **Làm thừa, người bỏ:** attack v5 tốn 13.9′ gen, là lượt dài nhất phiên. Người không dùng bản này, quay lại v4.
- **Tự kiểm chưa đủ:** suốt phiên AI chỉ đo số và xem vài ảnh viewport, không có playblast lần nào. Hầu hết câu trả lời có câu "chưa playblast".
- **Ghi đè file gốc khi chốt:** Base mới ghi đè file model gốc từ Unity cùng tên (77 KB). Có bản sao ở `/tmp/p25/exp/src_model_backup.fbx`, nhưng file này nằm trong `/tmp` và sẽ mất khi máy khởi động lại.
- **Việc ngoài anim tốn thời gian:** git push tới `git.horusent.com` thất bại vì máy chưa lưu mật khẩu, mất 11.5′ gen mà không ra kết quả.

## 6. Người vẫn phải tự làm

| Khi nào | Làm gì | Thời gian |
|---|---|---|
| Lượt 2–3 | Nhận ra rig v2 không làm được pose vòng, yêu cầu rig mới | 2.2′ |
| Lượt 5 | Yêu cầu gọi director kiểm pose | 1.3′ |
| Lượt 7 | Phát hiện pose chưa tròn | 8.1′ |
| 11:44–11:54 | **Tự sửa pose idle** trong Frolvy (xoay vòng ra camera, dời về giữa, chỉnh xoắn thân và đuôi) | khoảng 10′ (6.8′ + phần ngoài khoảng tính) |
| Lượt 11–16 | Đưa góp ý chuyển động: không quay đồng hồ, nhấp nhô, quay 1 vòng, chọn v4 bỏ v5, chỉ ra đoạn F32 → F40 | 26.6′ |
| Sau chốt | Bấm Push trong GitHub Desktop, mở Unity nhập thử FBX | chưa làm |

Gợi ý lần sau:
- Đưa concept và yêu cầu "pose vòng" ngay từ lượt đầu, để AI không làm lại trên rig cũ.
- Yêu cầu playblast trước khi người xem, để bớt các lượt sửa lỗi hình.

## 7. Ảnh tiến độ

Không có video. Pet 25 làm bằng Frolvy, không có sổ phiên bản như Spine Live, và các bản `.fv` trung gian đã bị dọn khi chốt.
Ảnh dưới đây là ảnh viewport AI chụp để tự kiểm trong lúc làm, lấy từ `/tmp/p25`.

| File | Nội dung |
|---|---|
| `v/00_ref.png` | Concept người gửi |
| `v/01_idle_v7_rigv2.png` | Idle v7 trên rig v2, thân thẳng (09:11) |
| `v/02_rigv3_vong.png` | Rig v3, pose vòng đầu tiên (10:03) |
| `v/03_pose_v8.png` | Pose idle v8 (11:04) |
| `v/04_pose_v10.png` | Pose v10 sau khi sửa theo director (11:12) |
| `v/05_pose_v11.png` | Pose v11 đã tròn (11:32) |
| `v/06_idle_v12.png` | Idle v12 từ pose người sửa, frame 0 (11:57) |
| `v/07_attack_v3.png` | Attack v3, các frame chính (13:48) |
| `v/08_attack_v4.png` | Attack v4, rồng quay 1 vòng (13:53) |
| `v/09_attack_v5.png` | Attack v5, bản người bỏ (14:16) |

## Sự cố trong phiên

Lúc 16:32–16:33 ngày 17/11, thư mục `DataHDD/AI_animation` và `DataHDD/Horus/tvc_source` trên ổ HDD bị chuyển vào Thùng rác, trong lúc dự án đang được chép sang SSD. WorkAI mất 9.2′ gen và người mất 12.2′ để xử lý:
- khôi phục `tvc_source`;
- khôi phục 359 file script, báo cáo và memory của pet vào bản SSD;
- nối lại WorkAI từ `/home/ngocvb/Projects/AI_animation`.

File anim và FBX đã chốt không mất.

## Cách tính

- **AI gen:** từ lúc gửi prompt tới tin nhắn cuối của AI trong lượt.
- **Người:** khoảng giữa hai lượt, chỉ tính khi ≤ 15 phút. Khoảng dài hơn coi là nghỉ.
- **Lượt:** tin nhắn giao việc do WorkAI gửi sang phiên con (`paseo-system`) cũng được đếm là một lượt.
- **Giờ:** giờ Việt Nam.
- **Log dùng:** Pet 25 v2 `f77de0d4`, WorkAI `7fa5a05b`, Pet 16 `cb3e9e69`, Pet 25 gốc `8a059edb`.
