# Idle (riêng cho loại đứng chờ)

## goals
- Đứng chờ tại chỗ, loop, không root motion, chân cắm đất (trượt chân = 0).
- Hai dạng: **idle thở** (chỉ nhịp thở + chuyển động thứ cấp) và **idle có diễn xuất** (liếc, đổi trọng tâm... theo ref).
- Truyền đạt tính cách qua nhịp thở: boss nặng -> thở chậm, vai nhún rõ, đạo cụ nặng trễ.

## breath-recipe
Công thức idle thở (đã duyệt: Gaygor Idle_Front v14):
1. Loop 60F (2 s), **một** nhịp thở; F1 = đáy hơi thở (chỗ nối đứng yên).
2. Đường cong chung sine: hít vào ~26F, thở ra ~33F (thở ra dài hơn, ~45/55).
3. Tư thế đáy/đỉnh mỗi xương lấy từ ref (đáy = ref f29, đỉnh = tư thế hít đầy nhất của xương đó trong ref f5..21).
4. Overlap: hông 0, Spine1 +2, ngực +4, bả vai/cổ +6, vai phải +7, khuỷu +9, cổ tay +11, ngón +12, chùy +9 (đầu nặng thêm
   `mace_delay` D=12).
5. Lưng uốn hai chiều: Spine1 -1..+2°, ngực -2..+3.5°, cổ -0.5..+1° (gù ở đáy, ưỡn ở đỉnh); đầu bù +3..-4° (trễ 3F) để vẫn
   nhìn thẳng, gật ~3.6°, trễ sau cổ ~6F.
6. Tay tự do IK: tay nhấc 4 cm + 3 cm nền (khuỷu gập 41-54°), trễ vai 5F.
7. Vai nhún 6-9 cm (như ref); đầu nặng chùy trễ vai 5F (đỉnh) / 10F (đáy).
8. Vạt khố: con lắc + gió (trước 26.7°, sau 25.3°; chu kỳ 20F/24F; gió 7°/6°, lắc ngang 6°/5°).
Biến thể từ clip đã duyệt (Idle_Front: bỏ liếc, 60F, các chu kỳ khác nhau rõ): SKILL.md Polish rules.

## params
- **Gaygor Idle 133F** (idle có diễn xuất, theo 100% ref, polish v5, duyệt 2026-10-20): xem `work/boss_gaygor/idle/`, sai số khớp TB ~7 cm so với FBX gốc.
- **Gaygor Idle_Front 60F v14** (duyệt 2026-10-20): `legacy/blender/idle_front_build.py` -> `IDLE_FRONT` (giá trị ở `#breath-recipe`).
- **SDR Idle 1 pose**: `#sdr-one-pose`.

## feedback
| Câu gốc | Nguyên tắc |
|---|---|
| "tay bị xoắn vặn quá đà phá cấu trúc Anatomy" (Idle 133F, tay trái cầm chùy) | Không ép hướng bàn tay; khuỷu bản lề thuần → `arms_hands.md#no-overbend` |
| "cần thêm bước giới hạn góc xoay, trục xoay của các khớp theo từng model" | Ngay sau rig: `joint_limits.json`, mọi pose = 0 vi phạm → `arms_hands.md#no-overbend` |
| "theo ref tay nắm đấm, khuỷu cong ra ngoài hơn" / "khuỷu co vào thêm chút là đẹp" | → `arms_hands.md#free-arm` |
| "bắp tay phải nằm ngoài cán, khuỷu chĩa xuống trước" | Đọc tay so với đạo cụ ở góc top → `arms_hands.md#prop-hand-side-fk` |
| "chỉ nhìn phía trước, không ngó nghiêng" (GD) | Biến thể idle: bỏ đoạn liếc, khóa yaw đầu theo hướng đã duyệt. |
| "133F dài quá, làm nhịp trong 60F" | Idle game thường 2 s; dài hơn thì nhiều nhịp phải khác nhau rõ (12% trông như copy). |
| "cánh tay dùng IK... khuỷu đẩy ra sau" | Tay tự do IK, tay nhấc hơn vai khi hít vào. |
| "ở F26 tay duỗi thẳng quá" | Giữ độ gập nền cho khuỷu (>40°). |
| "đầu bị giật ở F22, F53" | Key giữa pha thở ra sát đáy -> "đập đáy"; để pha thở ra là một đường S. |
| "chùy bị giật" | Đạo cụ dài khuếch đại xoay của bả vai; giảm vẩy theo world → `props_weapons.md#long-prop-flick` |
| "vai nhấc nhanh hạ nhanh, nhịp gấp" | 1 nhịp thở chậm / 60F thay vì 2 nhịp. |
| "Spine đang tĩnh" | Uốn lưng theo nhịp thở, trễ dần lên ngực. |
| "thở ra ở cuối đang nhanh" | Loop bắt đầu ở đáy, thở ra dài hơn hít vào. |
| "tay buông thõng xuống nhanh" | Tay trễ sau vai, giãn cả pha hít vào để không thành nhấc nhanh. |
| "tự view lại và đo nhịp hít/thở có đều không" | Một đường cong chung; báo bảng số đo từng bộ phận. |
| "áp dụng Overlap... bộ phận chính và bị kéo theo" | Chuỗi trễ dẫn -> bị kéo; đầu trễ sau cổ. |
| "cột sống cứng, cho cúi và ngẩng" | Uốn lưng hai chiều, biên độ ngực ~6°. |
| "hông lên tới đây thì đứng luôn... SlowIN" | Ease sine thay smootherstep. |
| "cầm chùy sát một đầu... overlap theo vai" | Đầu nặng trễ sau vai (`mace_delay`) → `props_weapons.md#heavy-prop-lever` |
| "làm thêm anim cho các chi tiết phụ" | Vải/phụ kiện có xương phải được animate. |
| "vải dao động nhiều hơn, kiểu bay trong gió" | Biên độ lớn + gió (đợt gió, lắc ngang) → `timing_spline.md#secondary-cloth` |

## errors
- Nắn key ref -> đỉnh rải F22..F40, cổ thở ra nhanh hơn hít vào -> đường cong chung.
- Đổi frame bắt đầu loop -> đầu lệch 5° (ref f29 đang chuẩn bị liếc) -> khóa yaw theo Idle f1 đã duyệt.
- Biên độ x1.8 cho chùy -> đầu chùy lệch pha -> chỉ khuếch đại bả vai.
- Uốn lưng quá tay (ngực -4..+6) -> đầu gật 18°, vai mất nhún -> giảm còn -2..+3.5.
- Trục xoay vạt khố ở khớp xương (giữa tấm vải) -> nửa trên/dưới ngược chiều -> trục ở mép thắt lưng.

## qa-checklist
- Mỗi bộ phận: đáy/đỉnh (frame), hít vào/thở ra (F), tốc độ lên/xuống; thở ra chậm hơn (tỉ lệ ~0.75-0.85).
- Chuỗi đỉnh tăng dần theo overlap (đo góc xoay cho phần xoay).
- Hướng đầu (yaw) không đổi nếu brief yêu cầu nhìn thẳng; gật ≤ ~4°.
- Khuỷu tay tự do không duỗi thẳng; tay không trôi trên cán; chân trượt 0; nối loop < 0.3 cm/F.
- Đạo cụ nặng: đầu nặng đạt đỉnh SAU vai; vải không xuyên đùi ở các frame cực trị.

## tools
`legacy/blender/idle_front_build.py` (`idle_front_build`, `idle_front_measure`, `mace_delay`, `cloth_flaps`),
`work/blender/key_idle_breath_curve.py`, `legacy/blender/arm_ik_R.py`, `direct.py` (`match_seam`), `qa_report.py`,
`playblast_anim.py` (WebM), `export_clip.py`.

## sdr-one-pose
Idle 1 pose (SDR - lính La Mã ném dao, camera ingame = góc right, không ref, theo concept 2D).
- "concept như này mà" (v1 thân mới xoay -57°, tay dao sát mũ): đặt concept cạnh render CÙNG góc camera ingame và gọi tên từng
  sai lệch trước khi chỉnh. Thân phải vuông với camera, tay dao ra ngang sau, bàn tay ngang đầu nhưng cách đầu.
- Muốn ngực quay về camera: **xoắn eo/ngực** (Spine1 -25, Chest -30), hông vẫn gần hướng mục tiêu (-35°) để chân là
  lunge dọc. Xoay hông -60..-80° làm đùi dạng ngang = dáng ếch/sumo, váy bè phẳng (v2-v5).
- Pole gối theo hướng gối mong muốn, không theo mũi chân xoay ngoài (gối sau bị đẩy về camera).
- Tham số v7: work/shoot_die_repeat/sdr/p0_pose.py (P0), kiểm tra sdr_lib.anatomy (da váy: `qa_anatomy.md#anatomy-check`).
- Hướng lòng bàn tay cầm dao (v10): `arms_hands.md#palm-dir`.
- Tấn ngắm 1 pose phải **đứng được lâu**: SDR v12 (hông hạ 13 cm, bước chân 0,72 m) bị góp ý "đẩy hông cao hơn, thu hai chân gần
  nhau để đứng thoải mái hơn" → v13 hạ hông 6 cm, bước 0,50 m, gối gập ~40°. Tấn sâu đẹp ở ảnh tĩnh nhưng nhìn mỏi khi giữ suốt
  game; tiếp tục bị góp ý "gối cong quá" → v14 hạ hông chỉ 2 cm, gối trước 22°, gối sau gần thẳng 8°. Với Idle 1 pose ưu tiên tấn
  cao, thả lỏng: gối trước ≤ 25°, chân sau gần thẳng, bước ≈ 0,5 m.
- Tư thế ngắm/ném phải **đổ về phía mục tiêu**: SDR v15 thân hơi ngả sau (đầu nằm sau thắt lưng ở góc right) → user gửi ref "toàn
  cơ thể đổ về trước". v16: hông dồn trước 5 cm, Spine1 +11°, Chest +9° (tổng ~20°), cổ/đầu bù ngược để mặt vẫn nhìn ngang. Kiểm
  nhanh: ở góc nhìn ngang, **mặt phải nằm trước khóa thắt lưng**. Khi thân đổ trước, đường tay ném ngang mặt (F6) bị hạ thấp hơn để
  không che mắt.
- **Đổ người phải bắt đầu từ hông**, không phải từ cột sống: v16 nghiêng Spine1/Chest +20° → user: "gù lưng, không mạnh mẽ".
  v17 nghiêng chậu hông 16° + lưng thẳng → "chổng mông, ngực vẫn đổ nhiều". v18: chậu hông 9°, Spine −2°, Chest −5° (ngực ưỡn), tổng
  thân đổ ~2–5° ra trước, gối 34°/32°. Dù layer Attack không key hông, pose mặc định của hông vẫn được chỉnh.
- **v16–v18 đều bị bác** (user: "quá tệ, quay lại bản v4"): gù, chổng mông, pha trộn — cả 3 đều xấu hơn tư thế đứng thẳng v15.
  Bài học quy trình (dừng sau 2 lần thất bại, đưa ảnh tĩnh): `review_process.md#still-options`.
- **SDR chốt (v19 / Attack blocking_v7, thay v18):** chỉ chỉnh hông từ v4 — chậu hông xoay đổ trước 7,5°, đẩy trước 3 cm, hạ 1,2 cm
  (giữ chân sau không duỗi quá khớp), thân trên đổ theo. User chọn "50% của A" sau khi xem ảnh tĩnh v4 | A (15°, 6 cm) | B (thân
  giữ nguyên).

## ninja-guard-pose
Ninja Idle F1 (chibi, kunai cầm ngược tay trái), user tự chỉnh pose AI dựng rồi bảo "bạn học theo nhé" (2026-10-29).
Pose chuẩn: `work/infinite_defense/ninja_idle/keys/F1_user_k10_v5.json` (giá trị khớp), script `pose_k10v3.py` (P = pose user).
Những gì user sửa so với bản AI (đo bằng mesh đã pose, cm):
- **Tấn so le trước–sau, không trung bình tấn:** chân sau lùi thêm 12 cm (so le ~30, rộng ~40), chậu hạ 2. Trước đó user đã chê
  tấn rộng sâu: "nâng trọng tâm lên, khép chân lại". Chibi chân ngắn: tấn rộng trông như ngồi xổm.
- **Hông xoay ~12° về phía tay cầm vũ khí** (vai trái dẫn). AI từng bỏ xoay hông vì gối chụm; user vẫn xoay, gối theo IK vẫn ổn.
- **Đổ người dồn ở lưng dưới** (Spine1 13°), ngực ít; **đầu bù ngược ~15°** để vẫn nhìn thẳng → đầu chúi ra trước 5 cm, dáng rình.
- **Tay vũ khí:** nắm tay ở giữa bụng (đường giữa thân), khuỷu khép sát; lưỡi kunai chĩa **xuống** và hơi ra ngoài, không chĩa ra trước.
- **Tay tự do:** kéo hẳn ra sau hông (lùi 28 cm so với bản AI). Concept/ghi chú trước đó đã nói "tay chưa đánh ra sau".
- **Khăn:** rủ ra sau ~45° ở gốc, không bay ngang sang một bên.
Quy trình: user đã tự sửa pose thì **không chạy lại script dựng pose đè lên version đó**; đọc khớp (`anim read`), lưu json, rút bài học.
Tự kiểm pose trên mesh đã skin: `pose_check.py` (xuyên kunai/tay/khăn, giãn da, sàn); khăn rời quay quanh gốc dễ lún vào lưng —
gốc khăn gập trong mặt phẳng dải khăn, dời gốc ra sau khi thân đổ / tay kéo sau.
