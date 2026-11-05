# RPG 2 — Hero (Assassin) · danh sách anim (G1) + câu hỏi (G2)
Ngày 2026-11-04. Nhãn nguồn: [GDD] trích tài liệu, [repo] có trong `D:\rpg-game1`, [file] có trong `C:\Project\RPG_2\Hero`, [suy luận], [?].

## Quyết định
- 2026-11-04, người dùng: "tôi muốn làm mới hoàn toàn. không động đến bản cũ" → câu hỏi 1 đã chốt: làm lại cả bộ song đao (A + B, thêm Sleep) trên model `Char_Main_T2` mới. Không sửa, không ghi đè file nào trong `D:\rpg-game1\Assets\_Game\Animation\Hero_RPG2\` hay controller cũ; bản mới để riêng (file làm việc ở `C:\Project\RPG_2\Hero`).
- 2026-11-04, người dùng: "Chỉ làm Idle và các anim attack" → đợt này 4 clip: `rpg2_hero_blade_idle`, `rpg2_hero_blade_attack_1`, `rpg2_hero_blade_attack_2`, `rpg2_hero_blade_deadly_strike` (đã đăng ký trong `work/clips.json`, nhân vật `RPG2_Hero`, dự án `rpg2_hero`). Move, trạng thái, Sleep, công cụ, Demon Form: ngoài phạm vi.
- 2026-11-04, người dùng: "fps là 30" → câu hỏi 2 và 3 đã chốt: cả bộ 30 FPS. Idle 30f loop (1 s). Mỗi đòn đánh 30f (1 s) theo trang Song đao: Attack 1 S10 (f1–8 kéo, f9–10 hold) · A5 (f11–15) · R15 (f16–30). Bỏ ghi chú "60 FPS" của mục 3.2 và trang Hero.

## Nguồn đã đọc
- GDD tổng quan (Google Sheet, `gdd.xlsx`, `gdd_cells.txt`): game **Assassin Quest: Hero RPG**, casual/idle RPG, iOS/Android. Tab Timeline có các dòng "Yêu cầu / Làm animation về vũ khí kiếm, cung, kiếm đôi, súng, thương, gậy phép" và "Yêu cầu về anim thu thập tài nguyên".
- Notion **[RPG 2] Thiết kế vũ khí: Song đao** (mục 3 FRAME DATA & ANIMATION, 8 clip, mỗi clip có link REF trên drive.horusvn.com).
- Notion **[RPG 2] Hero Concept & Animation** (concept Assassin, tỉ lệ 1 : 1,25 : 1,5 = 3,75 đầu, bảng màu, anim trạng thái, anim công cụ khai thác).
- [GDD] "Thể loại: RPG góc nhìn top-down · 3D" → camera game là **top-down**, đánh giá silhouette từ trên xuống. Mũ trùm là "chi tiết quan trọng nhất khi nhìn top-down".
- [GDD] Bộ phận chuyển động phụ: **2 đuôi khăn đỏ** sau lưng, vạt áo xẻ nhiều mảnh.

## Nhân vật và file
- [file] `Char_Main_T2.fbx` (sửa lúc 10:59 hôm nay) **khác** bản trong repo `Assets/3D_Art/MainCharacter2/Model/Char_Main_T2.fbx` (repo cập nhật lần cuối 2026-10-17).
- [file] `Vk_t1_Dualblades_lv1.fbx` giống hệt bản trong repo (`Weapon/Set2`). Repo còn bộ `Vk_t2_Dualblades_lv1..6` (thư mục RPG-2).
- [file] `Rig/skele.fv` = file rig Frolvy (11:24 hôm nay), chưa mở xem.
- [repo] Controller `PlayerHeroAssassinAnimatorDualBlades.controller`. Có các avatar mask `hero_sword_baseAvatar_upper_DualBlades.mask` (tách thân trên / thân dưới).

## A. Song đao — 8 clip trong GDD
| # | Clip (tên GDD) | Frame / fps [GDD] | Mô tả rút gọn [GDD] | Trong repo |
|---|---|---|---|---|
| 1 | `anim_hero_blade_idle` | 30f, loop, "Chuẩn Frame Rate: 30 FPS" | Mỗi tay một đao cầm ngang hông, lưỡi hơi hướng lên và chéo ra ngoài; hai đao rung lệch pha | `Hero_Blade/hero_blade_idle.fbx` (10-30) |
| 2 | `anim_hero_blade_move` | 30f, loop, 30 FPS | Nghiêng người về trước, giữ đao ngang hông chéo ra ngoài, bước chạy dài. **Tắt root motion**, tách thân trên / thân dưới để vừa chạy vừa đánh | `hero_blade_run.fbx` (10-30) |
| 3 | `anim_hero_Blade_attack_1` | S 10 · A 5 · R 15 = 30f, mục 3.2 "60 FPS" | Kéo đao phải ra sau (f1–8), hold 2f (f9–10), quét ngang từ phải sang trái 180° (f11–15), thu về (f16–30). Hit-stop 1f | `hero_bade_attack_1.fbx` + Atk1_Execute/End.anim |
| 4 | `anim_hero_Blade_attack_2` | 10 · 5 · 15 = 30f | Đao trái giơ cao sau vai, hold, chém chéo từ trên xuống sang phải, thu về | `hero_bade_attack_2.fbx` |
| 5 | `anim_hero_Blade_Deadly_Strike` | 10 · 5 · 15 = 30f | Hai đao bắt chéo chữ X trên đầu, hold, chém đôi xuống rồi tách mạnh hai tay sang hai bên; shake nhẹ | `hero_Blade_Deadly_Strike.fbx` |
| 6 | `anim_hero_Blade_Demon_attack_1` | 30f | Dạng quỷ: cào móng phải ngang | `Hero_Blade_Demon_form/` (hôm nay, NLeHoang) |
| 7 | `anim_hero_Blade_Demon_attack_2` | 30f | Cào móng trái chéo từ trên xuống | như trên |
| 8 | `anim_hero_Blade_Demon_Deadly_Strike` | 30f | Hai móng bắt chéo trên đầu, quật xuống rồi xé mở | như trên |

Luật chung [GDD]: "Startup + Active cố định; chỉ có Recovery scale theo chỉ số Attack Speed (0.8x đến 1.6x)". Hold 2f ở 2 frame cuối startup. Combo reset sau 3 s không có mục tiêu.
Logic đòn [GDD]: đòn 1 "Chém từ phải sang trái 180 độ", đòn 2 "Chém từ trái sang phải 180 độ".

## B. Anim trạng thái Hero (Notion Hero Concept & Animation, "Frame rate: 60 FPS")
| Clip | Frame [GDD] | Mô tả rút gọn | Bản song đao trong repo |
|---|---|---|---|
| Anim_Hero_Idle | 60f loop | Hít vào (1–20), thở ra, đầu hơi cúi (21–40), về cân bằng (41–60) | trùng với #1 ở trên? (xem câu hỏi 2) |
| Anim_Hero_Sleep | 120f (1–30 ngồi xuống, 31–100 loop thở, 101–120 giật mình bật dậy) | Ngồi thiền, đặt vũ khí xuống đất | **chưa có** (Sword có `hero_sword_sleep`) |
| Anim_Hero_Hit | 9f | Chớp trắng, ngửa người, bật nhẹ (1–5), lấy lại thăng bằng (6–9) | `hero_blade_hit.fbx` |
| Anim_Hero_Stun | 60f loop | Nghiêng đầu xoay tròn nhẹ, vòng sao trên đầu | `hero_blade_stun.fbx` |
| Anim_Hero_Dead | 72f | Khuỵu gối, buông vũ khí (1–18), ngã sấp đập mặt (19–45), giữ nằm (46–72) | `hero_blade_death.fbx` |
| Anim_Hero_Revive | 48f | Chống tay phải, co gối trái (1–15), bật đứng (16–32), về thế sẵn sàng (33–48) | `hero_blade_revive.fbx` |

## C. Anim công cụ khai thác (cùng trang, 60 FPS) — chưa thấy bản RPG2 nào trong repo
| Clip | Frame | Ghi chú [GDD] |
|---|---|---|
| Anim_Hero_Tool_Draw | 12f | Tay cầm vũ khí với ra sau lưng, vũ khí biến mất, công cụ hiện ở tay phải, hai tay cầm bên phải |
| Anim_Hero_Tool_Sheathe | 9f | Ngược lại |
| Anim_Hero_Harvest_Axe | 48f | Chém chéo phải → trái; cancel từ f25 |
| Anim_Hero_Harvest_Pickaxe | 60f | Bổ dọc từ trên đầu, rút mũi cuốc; cancel từ f31 |

## Câu hỏi (cần bạn trả lời trước khi phân tích từng clip)
1. **Làm clip nào?** Repo đã có gần đủ bộ song đao do team làm (10-30 và hôm nay). Đề xuất: [suy luận] model `Char_Main_T2` trong thư mục Hero là bản mới nên cần làm lại cả bộ song đao trên rig mới; thứ tự **Idle → Move → Attack 1 → Attack 2 → Deadly Strike**, rồi Hit/Stun/Dead/Revive, thêm **Sleep** (chưa có). Hay chỉ làm phần còn thiếu (Sleep, bộ công cụ khai thác), hay polish lại bản team đã có?
2. **Mâu thuẫn fps / độ dài Idle:** trang Song đao ghi idle 30f ở 30 FPS (1 s). Trang Hero ghi toàn bộ 60 FPS và Idle 60f (1 s). Hai trang cùng 1 s nhưng khác fps. Đề xuất: làm 60 FPS, Idle 60f (giữ 1 s), lấy mô tả cầm đao của trang Song đao.
3. **Mâu thuẫn độ dài đòn đánh:** mục 3.2 ghi "60 FPS" nhưng mỗi đòn S10+A5+R15 = 30f và cột "Thời lượng 1s". Ở 60 FPS thì 30f là 0,5 s. Đề xuất: giữ 30f ở 30 FPS (đúng 1 s) hoặc 60f ở 60 FPS (S20 · A10 · R30). Cần chốt vì nó quyết định nhịp cả bộ.
4. Đòn đánh có ghi "Loop: f30 nối mượt với f1". Đề xuất hiểu là: frame cuối trùng tư thế idle để nối combo (không phải clip loop). Đúng không?
5. **Lỗi chép trong GDD:** bảng Stun có tiêu đề "Anim_Hero_Idle", và f1–20 của Stun chép nguyên mô tả của Hit. Đề xuất: Stun f1–20 = giật lùi nhẹ khi dính choáng, f21–40 lắc đầu vòng tròn, f41–60 về thế đứng choáng (loop). Sleep: bảng trạng thái ghi "10s", phần chi tiết ghi "5s" (việc của code, chỉ ghi lại).
6. **Ref video:** mỗi clip song đao có link REF `drive.horusvn.com/s/…` (8 link). Có ref thì mình theo quy trình A (từ video ref), sát hơn tạo ảnh key pose. Bạn tải giúp các video vào `C:\Project\RPG_2\Hero\ref\` được không, hoặc cho mình biết link mở công khai được?
7. **Ảnh concept gốc** (bắt buộc khi tạo ảnh key pose): Notion có 2 ảnh (ảnh tham chiếu Assassin của game Skull Hero và ảnh concept đã chỉnh). Trang Notion chặn tải thẳng; nhờ bạn lưu 2 ảnh vào `C:\Project\RPG_2\Hero\concept\`.
8. **Rig:** `Rig/skele.fv` là rig đã duyệt để làm anim chưa? Mình dùng nó trên Frolvy (quy trình B: bạn key blocking, mình làm tiếp), hay để mình key từ đầu?
9. **Đao gắn joint nào khi xuất** (vd `Weapon_R` / `Weapon_L` hay thẳng vào bàn tay)? Kiểu cầm: [suy luận] cầm xuôi (lưỡi ra trước, "hướng lên và chéo ra ngoài") chứ không cầm ngược kiểu sát thủ. Đúng không?
10. Bộ **Demon Form** đã có trong repo từ hôm nay (model quỷ riêng `Hero_Blade_Demon_Form.fbx`). Đề xuất: không làm trong đợt này.

## Rig (kiểm 2026-11-04)
- [file] `Char_Main_T2.fbx` mới **không có xương** (chỉ 4 mesh: body, hood, scarf_1, scarf_2). `Rig/skele.fv` mở trên Frolvy cũng chỉ có 4 mesh này, 0 joint.
- [repo] Rig cũ của team (`Hero_Blade/hero_base.fbx`): tên kiểu AdvancedSkeleton `Root_M, Spine1_M, Chest_M, Neck_M, Head_M, Scapula/Shoulder/Elbow/Wrist_L|R, Hip/Knee/Ankle/Toes_L|R`, 3 ngón (Thumb 4 đốt, Middle 3 đốt, Cup), khớp gắn vũ khí `L_hand_sp` / `R_hand_sp`, chuỗi `joint*` / `joint*_L|R` cho khăn và vạt áo.
- Câu hỏi 11: rig mới có giữ đúng tên và cây xương này không (để chạy với controller và avatar mask của game)? Đề xuất: giữ đúng tên, đao gắn vào `R_hand_sp` / `L_hand_sp`.
