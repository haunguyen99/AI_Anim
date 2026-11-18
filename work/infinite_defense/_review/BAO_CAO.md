# Báo cáo Ninja (Infinite Defense, 3D): Idle + Attack trong Studio, Skill 1 trong Frolvy

Nguồn: log 9 phiên Claude. Studio 28–30/10: `131029d3` Rig+Idle, `6eacd60e` Idle polish + mở Attack, `e7f5846c` Attack (chạy trong worktree). Frolvy 3–4/11: `8da47427`, `3f0e1f05`, `d3a5179a`, `798033c1`, `2d4078de`, `f847746a`. Thêm `work/store/ninja_*`, git log, ghi chú vẽ trong `ninja_studio/notes`, các file `.fv` / `.fbx` trong `Documents\Ngoc\Hoctap`. Số liệu tính bằng `tools/report/session_stats.py`, gộp ở `aggregate.py` (Studio) và `aggregate_frolvy.py` (Frolvy), cùng thư mục. Việc Frolvy 5/11 trở đi (Windy, Hero RPG2 …) không tính.

## 0. Tóm tắt toàn bộ Ninja
| | Studio 28–30/10 | Frolvy 3–4/11 | Cộng |
|---|---|---|---|
| Lượt prompt | 121 | 89 | **210** |
| AI gen | 12 g 17′ | 3 g 33′ | **15 g 50′** |
| Người (≤ 15′ giữa các lượt) | 4 g 39′ | 3 g 27′ | **8 g 06′** |
| Việc làm ra | Rig 48 xương, Idle 40F (11 version), Attack 30F (14 version, chốt v12) | Rig lại + picker, Idle pose lại, Skill 1 24F (blocking v5–v7, refine v1–v4), 2 FBX | |

Phần 1–7 dưới đây là Studio; phần 8 là Frolvy.

## 1. Thời gian
| | |
|---|---|
| Lượt prompt | 121 (Rig 17 · Idle 41 · Attack 41 · Skin 8 · Khác 11 · Sự cố 3) |
| AI gen | **12 g 17′** |
| Người (khoảng giữa các lượt, ≤ 15′) | 4 g 39′ |
| Chờ trả lời câu hỏi | 11′ |
| Tổng có mặt | ≈ 17 g 07′ (3 ngày: 28, 29, 30/10) |

| Giai đoạn | Lượt | AI gen | Người |
|---|---|---|---|
| Rig (khớp, skin, bind kunai) | 17 | 24′57″ | 25′00″ |
| Idle (concept, ref, F1, blocking, polish) | 41 | 4 g 16′ | 2 g 13′ |
| Skin sửa tay/chân giữa Idle | 8 | 23′10″ | 12′43″ |
| Attack (phân tích, blocking, polish v3–v14) | 41 | 6 g 03′ | 1 g 21′ |
| Việc khác (git, Studio lỗi, hỏi đáp) | 11 | 13′25″ | 27′05″ |
| Sự cố (API ECONNRESET, Home tắt) | 3 | 56′49″ | 0′38″ |

Đã hiệu chỉnh 3 lượt bị log đếm sai vì treo qua đêm / mất kết nối: S1#31 (đếm 14 g 22′ → 5′24″), S1#63 (144′ → 13′30″), S3#8 (14 g 43′ → 38′36″ gồm cả đợi script nền). S1 và S2 chạy song song 14:40–17:06 ngày 29/10 nên "người" của hai phiên chồng nhau.

## 2. Số lần gen
- 121 lượt, trong đó đổi dữ liệu nhìn thấy được (version mới hoặc sửa key/skin): ~75.
- Idle: 11 version Pose Lab (k10_v1–v5, b50_v1–v2, polish_v1–v4) + 4 playblast review (pb1–pb4).
- Attack: 14 version (b_v1, b_v2, polish_v3–v14; v7 loại bỏ rồi làm lại).
- Người vẽ **22 ghi chú** trong Studio (1 ngày 28/10, 5 ngày 29/10, 16 ngày 30/10), tất cả sau đó đánh dấu "đã sửa".
- Người tự sửa tay: pose F1 Idle (S1#55, "tôi vừa tự sửa lại pose cho bạn rồi, bạn học theo nhé"); lưu thành `F1_user_k10_v5.json`.

## 3. Các chuyển biến lớn
| # | Lượt | Yêu cầu / góp ý | AI làm | Ghi chú |
|---|---|---|---|---|
| 1 | S1#3–13 (28/10 15:26, ~25′) | rig Ninja + kunai tay trái, sửa khớp bàn tay | Rig 48 xương, kunai bind cứng vào `Weapon` dưới `Wrist_L`, 2 chuỗi khăn | **Lỗi AI:** #9–10 ghi đè khớp người vừa sửa, người báo "tất cả những gì đã sửa đều mất" |
| 2 | S1#18–20 (16:15, 19′) | thiết kế Idle 40F, rồi blocking | analysis.md, k10_v1, b50_v1 | duyệt nhanh |
| 3 | S1#29–43 (17:21 → 29/10 09:23, ~58′ gen) | "pose idle xấu quá" | nhờ Codex vẽ concept, 3 vòng vẽ lại ảnh front/side, ref sheet 6 ô, dựng F1 k10_v4 | **Lỗi AI:** đổi pose khi người chỉ bảo vẽ lại ảnh (#36); Codex không ra góc 90° sau 3 lần |
| 4 | S1#45–47 (09:43) | skin vai/hông vẫn lấn | clean_skin.py, leg_skin.py | người vẽ 2 ghi chú |
| 5 | S1#51–55 (10:03–10:49) | trọng tâm, chân không vững | k10_v5 sửa 3 lần theo ghi chú | **Người tự key pose F1** (10′ 10″), AI học theo |
| 6 | S1#57–63 (11:17 → 14:29) | thở 40F từ F1, khăn lắc | b50_v2 | #61–63 mất ~3 g chờ vì ECONNRESET và Home tắt |
| 7 | S2#5–7 (15:08) | skin tay méo | arm_skin.py, elbow_ring.py | lần 2 và 3 mới đúng ("Vẫn méo") |
| 8 | S2#9–10 (15:24, 14′42″ + 46′34″) | polish | polish_v2 → v4 (overlap thân, tay) | người nhận thấy "phần cánh tay chưa có anim" |
| 9 | S2#14 | "loop bị giật" | lỗi ở nút Phát chạy đủ F1–F41 (F41 = F1) | **lỗi công cụ**, không phải anim |
| 10 | S3#1–7 (29/10 17:06) | phân tích Attack, shuriken gắn tay | analysis 30F, shuriken ngoài skin con `Wrist_R` | sửa lỗi chú thích chèn giữa dòng code làm model biến mất |
| 11 | S3#9–13 (30/10 08:12–09:40) | blocking có tay xoắn, gãy khớp | b_v1 dựng lại bằng IK | **Lỗi AI:** script ghi đè song song làm 9 key thừa; mất ~1 g khôi phục |
| 12 | S3#15–19 (09:54–11:12) | thân không có đổ trước/sau, không overlap | b_v2, polish_v3, v4, v5 | 3 vòng mới ra overlap thân |
| 13 | S3#21–24 (11:13–11:54) | shuriken lơ lửng F1–F10, khăn cứng | v6, rồi v7 tự kéo tay ném | **Lỗi AI:** v7 đổi pose đã duyệt, người: "tự ý chỉnh sửa vậy", gỡ v7 |
| 14 | S3#25–36 (13:38–14:53) | khăn tung bay trái phải | v7 → v12: 6 vòng sửa khăn | khăn cứng rồi lắc vụn (6 lớp chuyển động chồng); đến lúc dùng 1 mô phỏng lò xo mới ổn |
| 15 | S3#39–43 (15:07–16:34) | Director chấm | v12 "cần sửa" (1 nặng, 6 vừa, 3 nhẹ); v13, v14 | **Người chốt bản v12 làm bản Attack cuối** (v13, v14 làm theo Director không dùng); chưa xuất FBX trong phạm vi này |

## 4. Điểm mạnh của AI
- **Dựng và sửa số lớn nhanh:** skin vai/khuỷu đo trước-sau bằng `lbs_test.py`; sửa hông/gối F1 theo số đo (hạ 8 cm, gối 40° → 80° trong 1 lượt 2′48″).
- **Tự kiểm bằng số:** `pose_check.py` (xuyên mesh, giãn da, chân chạm sàn), `verify.py` + `golden_b_v1.json` so key bằng số sau khi bị ghi đè; đọc lại 41 frame khăn khi sửa giật.
- **Bắt lỗi gốc:** loop giật do công cụ phát chứ không do key; model biến mất do chú thích chèn giữa dòng code; Ghi chú vẽ không hiện do thiếu panel.
- **Học theo người:** sau khi người tự sửa F1, AI đo chênh lệch từng bộ phận và ghi bài học `#ninja-guard-pose`; các bản sau giữ đúng pose đó.
- **Attack bám pose đã duyệt:** F1, F25, F30 trùng Idle, lệch ≤ 0,02 cm.

## 5. Điểm yếu của AI
1. **Ghi đè công sức người.** 28/10 ghi đè khớp người sửa (#9–10 mất ~2′ gen nhưng người phải kiểm lại từng khớp); 30/10 v7 đổi pose đã duyệt (người phát hiện ở S3#23). Lặp lại hai lần trong 3 ngày.
2. **Vẽ concept bằng Codex không nghe góc.** Ba vòng liên tiếp (S1#34–36, ~17′) cho "front, side 90°" mà ảnh vẫn 3/4; còn tự ý "pose lại" khi chỉ bảo vẽ lại. Người nói: "t bảo là ren lại thôi chứ có bảo pose lại đâu".
3. **Khăn mất 3 ngày.** Attack riêng khăn: v6 → v12 (chốt), 7 phiên bản, ~3 g gen. Lỗi lặp: biên độ nhỏ (5–15°, người: "cứng thế"), rồi chồng 6 lớp gây lắc vụn. Chỉ ổn khi tham khảo playblast video của người.
4. **Treo/đứt kết nối làm báo cáo sai.** 3 lượt log đếm hàng chục giờ, ~1 g 8′ thực chờ ECONNRESET/Home tắt mà không báo trước.
5. **Tay ném xoắn/gãy khớp (30/10).** 5 ghi chú "xoắn joint" trong 1 giờ: lỗi do tự tính hướng bàn tay thay vì theo cẳng tay (kinh nghiệm cũ đã ghi ở `feedback-arm-anatomy`).
6. **Director chấm v12 "cần sửa", nhưng người vẫn chốt v12**: v13, v14 sửa theo Director không được dùng.

## 6. Người vẫn phải tự làm
| Khi nào | Làm gì | Số lượng |
|---|---|---|
| 28/10 15:49 | chỉnh khớp hông, gối, bàn tay, đuôi khăn | 3 lần sửa tay |
| 29/10 10:49 | tự key lại pose F1 Idle sau 6 vòng AI không ra | 1 lần, ~10′ |
| 28–30/10 | vẽ ghi chú ✎ trực tiếp trên viewport | 22 ghi chú |
| 29/10, 30/10 | gửi video tham khảo khăn (Maya playblast) | 1 lần, mở được v13–v14 |
| 30/10 | quyết định lùi/loại bản (v7, "về bản blocking trước") | 4 lần |
Gợi ý lần sau: người chốt pose F1 trước rồi mới triển khai (tiết kiệm ~1 g 20′ của F1); đưa video ref khăn ngay từ polish đầu; đặt luật "chỉ thêm overlap, không đổi pose duyệt" (đã ghi 30/10).

## 7. Video preview
| File | Nội dung |
|---|---|
| `v/idle_pb1.mp4` | Idle polish bản đầu, 29/10 15:01 |
| `v/idle_pb2.mp4` | Idle polish sau góp ý tay, 16:25 |
| `v/idle_pb3.mp4` | polish_v4 (pb3), 16:30 |
| `v/idle_pb4.mp4` | polish_v4 sửa loop F1–F40, 16:48 |
| `v/attack_b_v2.mp4` | Attack blocking b_v2 (3 góc: phải / trước / trên) |
| `v/attack_polish_v5.mp4`, `v8`, `v12` (bản chốt), `v14` (không dùng) | Attack polish: overlap thân, khăn tung, overlap lắng, bản chốt |
| `v/skill1_blocking_v6.mp4`, `v7`, `skill1_refine.mp4` | Skill 1 Frolvy (chiếu chậm ×3, camera trên xuống); refine v1–v4 và blocking v5 không còn file |

## 8. Frolvy 3–4/11: rig lại, pose Idle, Skill 1 (kunai ném)
Số liệu: `aggregate_frolvy.py` → `stats_frolvy.json`. Lượt kết nối MCP, đổi chế độ, hỏi file nằm ở nhóm "Khác".

| Giai đoạn | Lượt | AI gen | Người |
|---|---|---|---|
| Rig (check skin, tay cầm kunai sang trái, picker) | 5 | 1 g 11′ | 8′36″ |
| Pose Idle trong Frolvy | 11 | 21′27″ | 11′25″ |
| Skill 1 blocking (phân tích GDD, 5 key pose, kunai, IK chân) | 28 | 47′15″ | 1 g 18′ |
| Skill 1 refine + xuất FBX (breakdown, khăn, đường bay) | 25 | 46′11″ | 1 g 27′ |
| Khác (kết nối MCP, đổi chế độ, hỏi file, git) | 20 | 27′31″ | 21′54″ |
| **Tổng** | **89** | **3 g 33′** | **3 g 27′** |

### Chuyển biến lớn
| # | Lượt (giờ) | Yêu cầu / góp ý | AI làm | Ghi chú |
|---|---|---|---|---|
| 1 | 8da47427#1–2 (3/11 11:05) | check bindskin `ninja_rig_v2.fv`, làm picker | chỉ sửa 1 chỗ ở háng (11′ gen), mỗi đỉnh ≤ 4 joint, chỉ DEF | |
| 2 | 8da47427#3–5, 3f0e1f05#5–6 | đưa pose Idle từ Studio vào rig Frolvy | paste pose qua MCP | làm lại ở 3f0e1f05#17–18 vì mất pose |
| 3 | 3f0e1f05#13–16 (13:39–15:10) | tay cầm kunai là tay trái; picker cũ lỗi | sửa file rig (một lượt 39′34″ gen), build lại picker (16′ gen) | **Người mất ~10′** hỏi cách đổi chế độ edit (#9–12) |
| 4 | d3a5179a#1–4 (15:47–15:59) | "key all vào f0" | báo đã key 56 control `CTL_*` ở f0 (scene `autosave2.dccscene`), người không thấy key; key lại thì **mất pose Idle** | **Lỗi AI:** "ko, làm trong frolvy cơ" / "đâu t có thấy key đâu" / "key vào thì mất pose idle nãy rồi" |
| 5 | d3a5179a#5–11 (16:00–16:11) | phân tích GDD Skill 1, pose F5 thử, triển khai các pose còn lại | bảng key pose, pose test | **Lỗi AI:** nhầm tay ném: "tay ném kunai là tay đang cầm vũ khí mà"; kunai quay tứ tung |
| 6 | d3a5179a#12–17 (16:12–17:06) | giãn lên 24F; hip, tay không cầm vũ khí chưa có nhịp; chân sang IK; "gần giống Attack Ninja đã train trong Studio" | sửa nhịp, chân IK, picker mới | người báo hip và tay phụ không có chuyển động (#13) |
| 7 | d3a5179a#18–19 | file autosave đâu; tái tạo bản mới nhất | dựng lại bản mới nhất | mất file làm việc |
| 8 | 798033c1, 2d4078de (4/11 08:32–10:05) | chốt lại 5 key pose k1–k5; Codex vẽ minh hoạ; "ngực xoay sang phải, tay cầm kunai thu về…" | dựng blocking trong Frolvy; Codex bị người bảo dừng (#4) | kết nối MCP hỏng 4 lần trong 15′ (798033c1#8–11); người chỉnh tay vài chi tiết, rồi bảo AI tự nhận xét |
| 9 | 2d4078de#5–9 | mesh bóng ánh sáng; grid giật zoom f2→f3; cố định chân; tay phải f12–15 co duỗi thừa | sửa từng cái | khoảng nghỉ 14′ sau #5 |
| 10 | f847746a#2–11 (10:15–10:58) | kunai ở tay f0–f10, bay từ f11; đường bay lung tung; body giật f12–15; khăn overlap | đường bay kunai, refine v1–v3 | **Lỗi AI:** kunai bay lung tung (#8); người: "về lại bước blocking tôi đã chốt" (#12) |
| 11 | f847746a#14–16 (11:14–13:56) | thêm pose breakdown cho mềm | thêm in-between, thấy không ổn | người bảo về lại (#15); AI revert bằng 2 undo, kiểm key ngực về [0,7,12,15,24] |
| 12 | f847746a#18–20 (14:31–14:44) | lực ném nhẹ; khăn làm kiểu vải; "chưa đủ mềm" | tăng tốc kunai 0,7 → 1,5 m/frame, overlap 2 tà khăn | người nhận 3 lần |
| 13 | f847746a#21–24 (14:58–16:39) | người lưu `refine_v4`, xuất FBX | `Ninja_Skill1.fbx` (24F loop, f24 = f0, 1,47 MB); `Ninja_Skill1_KunaiInHand.fbx` (kunai không rời tay, cho dev bắn projectile); xuất lại sau khi sửa đường bay | **Lỗi bộ xuất Frolvy:** file có 3 xương trùng tên `DEF_Weapon_L`, AI gỡ 2 bản thừa; kunai lệch phải xuất lại |

### Điểm mạnh (Frolvy)
- **Skill 1 từ GDD đến FBX trong ~1 ngày làm việc** (3/11 16:00 → 4/11 16:39): 5 key pose, 24F, refine v1–v4, hai FBX.
- **Hoàn tác an toàn:** revert breakdown bằng undo, rồi đọc lại key để chứng minh về đúng blocking đã chốt.
- **Bắt lỗi file xuất:** thấy 3 xương `DEF_Weapon_L` trùng tên, gỡ cả đường cong anim của chúng, đọc lại file không còn liên kết hỏng; so đường bay kunai trong FBX với scene, lệch < 0,1 mm.
- **Thêm bản dùng được cho dev:** `KunaiInHand` để dev tự bắn projectile, không phải đợi hỏi.

### Điểm yếu (Frolvy)
1. **Key vào sai scene / sai chỗ làm mất pose** (d3a5179a#1–4, ~6′ gen nhưng người phải nhắc 3 lần).
2. **Nhầm tay ném** (#9): đọc GDD "tay cầm kunai" mà dựng ném bằng tay kia.
3. **Phải lùi hai lần** (f847746a#12, #15): đổi pose đã chốt khi chỉ được bảo refine. Luật "không tự đổi pose đã duyệt" đã có từ 30/10 nhưng vẫn lặp lại.
4. **Kunai bay sai** hai lần (#8 và #23): sau mỗi lần sửa phải kiểm lại đường bay.
5. **Kết nối MCP hay đứt:** ~8 lượt chỉ để nối lại (798033c1#8–11, 2d4078de#1, f847746a#1, 3f0e1f05#7–12).
6. **Mất file:** autosave nằm đâu không rõ, người phải tự lưu từng phiên bản (AI không được tự lưu).

### Người vẫn phải làm (Frolvy)
| Khi nào | Làm gì |
|---|---|
| 4/11 09:33 | tự chỉnh vài chi tiết pose k2–k5 rồi bảo AI học theo |
| 4/11 14:58 | tự lưu `refine_v4` (AI không được ghi đè) |
| 3–4/11 | nhắc lại "về bản đã chốt" 2 lần |
| 3–4/11 | chọn chế độ edit, kết nối MCP |

### Video / FBX
- Video Attack / Skill 1 xem mục 7. FBX giao: `Documents\Ngoc\Hoctap\Fbx\Ninja_Skill1.fbx`, `Ninja_Skill1_KunaiInHand.fbx`.
