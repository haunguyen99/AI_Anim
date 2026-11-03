# Đạo cụ, vũ khí, tay cầm prop (mọi loại anim)

## heavy-prop-lever
- **Đạo cụ nặng cầm ở một đầu = đòn bẩy tì vai.** Đầu xa đi ngược chiều vai là đúng; nhưng đầu nặng phải trễ sau vai.
  Độ cao đầu nặng do bả vai/ngực quyết định nên trễ key của đạo cụ không có tác dụng -> điều khiển trực tiếp đường đi
  của đầu nặng (`mace_delay`). (Idle: "cầm chùy sát một đầu... overlap theo vai"; Gaygor Idle_Front: chùy trễ vai 5F đỉnh / 10F đáy.)
- Biên độ x1.8 cho chùy -> đầu chùy lệch pha -> chỉ khuếch đại bả vai (Idle).

## long-prop-flick
- **Đạo cụ dài khuếch đại xoay của cha** (bả vai 1.45°/F -> đầu chùy 4.5 cm/F; Idle "chùy bị giật"). Tìm xương nguồn trước,
  giảm cú vẩy theo không gian thế giới trên key đạo cụ. Cách làm chi tiết: SKILL.md Polish rules (slerp K 0.4-0.5, đo tốc độ mũi).

## oversized-prop
- **Đạo cụ quá khổ: kiểm tầm với trước khi đặt tay** (SDR map06, 2026-10-21). Tommy gun của model dài 1,24 m (gấp ~1,45 lần súng
  thật), tay cầm trước cách cán sau 54 cm, tay trái cần 0,86 m trong khi cả tay chỉ dài 0,47 m. Cách xử lý: dò khoảng cách vai → điểm
  cầm theo vị trí súng và độ xoay thân, đổi điểm cầm (ốp nòng ngay trước trống, 35 cm), xoay súng 10° vào giữa (code aim, góc side
  không thấy), đưa xương Scapula ra trước 20° thay vì xoay thân nhiều.
- **Cập nhật sau (review Shoot b2 F8, 2026-10-21):** người duyệt vẫn xem góc top - súng phải thẳng hướng mục tiêu, nên "xoay súng
  10° vào giữa" ở trên KHÔNG còn dùng; giải tầm với bằng thân/scapula/vị trí súng (xem `#gun-aim`).

## grip-big-shaft
- Tay nắm cán to (Cascadeur Gaygor P0): điểm Wrist là cổ tay (bên hông cán, cách trục ≈ bán kính + 5 cm), không phải chỗ các ngón
  nằm trên đỉnh cán; đặt sai thì khuỷu bị đẩy lên và bàn tay lơ lửng thành "nắm đấm" cạnh cán.
- **Tay chìm trong cán** (Cascadeur Attack): cổ tay đặt cách trục cán 10–20 cm trong khi bán kính cán ~26 cm -> bàn tay nằm trong
  chùy, view left không thấy tay nào. `block_pose` giờ đẩy cổ tay ra ngoài bề mặt (`grip_radius` 30). Điểm đỡ ngoài tầm với thì dời
  về mép cán phía thân và đẩy bả vai/vai ra (`shift_points`), không kéo tay vào trong cán.
- **Áp lòng bàn tay lên prop dày** (Blender Attack v8, "Tay tương tác với vũ khí chưa được tốt"): chùy dày hơn nắm đấm nhiều (bán
  kính 0,33 m) nên ref ÁP LÒNG BÀN TAY lên mặt chùy, ngón mở ôm theo; bản cũ là nắm đấm chìm 50–90% mesh tay trong cán. Đo bằng
  BVH (đỉnh mesh tay, dấu theo pháp tuyến) - `hand_contact.py`: ngón của mesh này ở tư thế nghỉ là NẮM ĐẤM (0 = nắm, -60 = duỗi
  thẳng); bàn tay -X(L)/+X(R), lòng bàn tay = phía ngón quặp vào: +Z(L)/-Z(R). Quy trình: mở ngón -> `palm_seat` (tâm lòng bàn
  tay cách mặt 6 cm theo pháp tuyến lòng bàn tay; KHÔNG dùng "điểm gần nhất" - đó thường là cổ tay) -> `wrap_mesh` (quặp tới khi
  phần ngón xuyên tăng > 3%) -> kéo target về vai nếu cẳng tay rách. Xoay cổ tay theo trục chùy (`orient_hand`) làm tệ hơn - giữ
  hướng của `solve_grip`. Dáng vác vai (f1, P0) giữ nắm cũ vì đã khớp ref.
- Nắm đấm rời chùy (f60 tay phải): bật IK, đặt target tay tại điểm tam giác hoá từ 2 view, giữ hướng cổ tay FK.

## solve-grip-notes
- `solve_grip` (Blender, `attack_pose.py`): grip trượt quanh/dọc cán, khuỷu bản lề, cổ tay lệch nhỏ so với P0 grip, chấm trên da
  (`arm_strain` vs P0). Xem `arms_hands.md#no-overbend`, `#reach`.
- Quy ước phi phụ thuộc hướng cán (ref0 = "lên" chiếu vuông góc trục) - tính ref0/sa cho từng key trước khi chọn phía nắm.
- `P0_STRAIN` rỗng sau khi exec lại attack_pose.py -> strain chấm tuyệt đối (final âm); `solve_grip` nay tự gọi `p0_strain()`.
- `regrip` dựng lại từ fit đã lưu -> làm lại `leg_reach`/`knee_to_toes` sau đó.

## prop-measure
- Ghi chú khoanh chùy/tay = vị trí prop và điểm nắm sai: IoU thắng bằng chùy sai chỗ + tay sai phía; đo chùy bằng mắt từ 2 view
  ref có lưới (`mace_measure.py`, mỗi view chỉ dùng toạ độ đọc được), khoá chùy, fit lại thân (`mace_refix.refix`), rồi đặt tay
  theo ref (`regrip`: dải s/phi đọc từ ref) (Blender Attack v5).
- Độ cao chùy: đo ở view bên (left/right), không ở front (front lẫn độ sâu) - v3 hạ chùy theo front là sai, phải trả lại.
- Chùy lệch +Y 0.18 m, xa thân 0.1 m: kiểm bằng độ rộng từng hàng ref vs anim ở góc top/bên.
- f31: tam giác hoá prop từ 2 view chỉ đúng khi chọn đúng điểm tương ứng; kiểm lại bằng bề rộng cột ở view bên (`extent_cmp`) và
  `mace_points()` (đỉnh mesh) - lần đầu chùy lệch ra sau 0,2 m.
- Đọc hướng chùy bằng mắt từ ảnh nhỏ dễ sai chiều (Cascadeur f4: đọc "ngả trước" nhưng thật ra ngả sau). Đo tâm chùy theo từng độ
  cao trên mask ref rồi mới đặt; fit tự động theo đường tâm (`work/cascadeur/mace_fit.py`) KHÔNG tin được vì móng vuốt xòe kéo lệch.
- Với chùy dựng đứng, mép dưới đầu cán thấy được thấp hơn điểm s = −75 khoảng 20 cm: đặt chùy theo mép thấy được trên ref.
- Dò chùy bằng render cả người bị cánh tay (con của chùy) làm nhiễu -> dò chùy riêng bằng chiếu đỉnh mesh; bóng không phân biệt
  đầu/đuôi chùy -> ràng buộc thời gian hoặc hướng theo phân tích (blocking v4).

## prop-penetration
- **Đo prop xuyên thân ở MỌI key** (review Reload b5 F14: "mesh súng bị chìm vào mesh body"). Khi đổi P0 (súng dời vào giữa),
  các key dựng súng thừa hưởng độ lệch đó, làm súng xuyên đầu và bắp tay. `blocking.gun_inside()` đếm đỉnh prop nằm trong
  da thân/đầu (bỏ qua bàn tay và cẳng tay đang cầm). Gửi review chỉ khi đo được 0 ở các key dựng súng.
- **Tránh xuyên đừng đánh đổi bằng tay căng** (review Reload b7 F30: "đưa súng ra xa quá khiến tay bị căng"). Khi tìm vị trí
  prop, ràng buộc cả hai thứ cùng lúc: số đỉnh xuyên ≈ 0 và khuỷu ≥ ~50°. Muốn tạo khe hở thì mở khuỷu ra ngoài (pole) và xoay
  thân; khi cầm vật tròn đi ngang qua cánh tay thì đổi điểm cầm (xách mép trên), đừng đẩy prop ra xa.

## grip-drum
- **Cầm trống/băng đạn tròn: áp lòng tay vào cạnh, khuỷu ra ngoài** (review Reload b20 F11: "Chỉnh lại vị trí tay cầm vào băng
  đạn", "Để ý đẩy khuỷu tay ra"). Đỡ dưới đáy trống làm khuỷu kẹp sát sườn (lệch ra ngoài vai ~0 cm), và tay còn không với tới
  (lệch 7–19 cm). Hãy áp lòng tay vào mặt bên trống, ngay giữa, ngón ôm ra trước, đặt pole sang ngang (khuỷu ra ngoài vai ≥ ~10 cm,
  gập ~90°). Kiểm tra bằng số: khuỷu cách vai bao nhiêu theo phương ngang, và wrist_err = 0.

## flat-prop-orient
- **Prop đưa sát người phải xoay theo thân** (review Reload b21 F16: "Trống đạn bị chèn vào quần áo. hãy xoay trống đạn khi di
  chuyển"). Prop dẹt (trống, khiên) giữ hướng của súng khi mang ra hông sẽ cắm cạnh vào vạt áo. Hãy xoay cho mặt phẳng áp dọc thân
  (pháp tuyến theo trục hông trái–phải), rồi tìm vị trí (đẩy ra, lùi, góc xoay) cho số đỉnh nằm trong áo thấp nhất và di chuyển ít
  nhất. Đừng tin trục local theo ghi chú: đo pháp tuyến bằng PCA mesh. Áo khoác loe ở đùi, nên đo xuyên riêng các đỉnh của prop đó.
- Prop dẹt (dao) phải quay **mặt phẳng lưỡi** về camera ingame, không quay cạnh (SDR Attack v3). Góc lăn để lộ mặt lưỡi khác nhau
  giữa lúc cầm (P0 cần lăn 90°) và lúc bay (lăn 0) → kiểm bằng ảnh cận từng trạng thái, đừng suy từ trục rest.

## gun-aim
- **Súng ngắm phải thẳng hướng mục tiêu ở góc top** (review Shoot b2 F8: "súng cần hướng thẳng về phía trước"). Dù aim do code
  làm và góc side không thấy độ yaw, người duyệt vẫn xem góc top: đừng xoay súng để giải tầm với. Hãy giải tầm với bằng thân,
  xương scapula và vị trí súng.
- Tay ngắm phải **song song mặt đất** (SDR Attack v3: code aim lấy hướng này làm gốc).
- Đổi hướng người thì đặt lại prop theo hông mới và giải lại mọi key cầm prop (SDR map06 Shoot b3).

## thrown-prop
- Dao bay = Copy Location + Copy Rotation từ bone world, KHÔNG Copy Transforms (chép scale 1 lên rig scale 0.01 -> dao to 100 lần).
- CTRL dao: LINEAR chỉ ở đoạn bay (key F6, F9), CONSTANT ở mọi đoạn khác — nếu để LINEAR cả action, dao bay ngược từ bia về tay ở
  F16→F18 (lỗi bắt được nhờ đo bước dao theo frame). Constraint influence luôn CONSTANT (chuyển tay ↔ world là cắt cứng).
- Sau overlap phải **đặt lại điểm thả dao** theo bàn tay thật ở F6 (ngực trễ làm tay dời ~12 cm).
- Bia demo: lưỡi gladius dài ~0,45 m tính từ tâm cán; đặt mặt bia cách tâm cán ~0,41 m để chỉ mũi cắm vào (bia cũ ở 0,22 m:
  dao xuyên nửa lưỡi). Rung khi cắm: xoay quanh điểm mũi ở mặt bia +6/−4/+2/0° (F13–F16).
- Xuất cả 2 bản (dao bay demo / dao theo tay) khi có prop ném: `export.md#variants`.

## Dao bay xem trước bằng vật thể phụ Studio (SDR01 Shoot, 2026-10-29)
- `obj add <tên> --mesh <mesh dao> --bone <xương dao> --f 1` (phải đứng ở F1) → bản sao bám tay, dao gốc tự ẩn; `obj parent <tên> world <F thả>`
  rồi `obj key <tên> <F trúng> --at x,y,z --interp linear` (trục Blender, Z lên). Dao mới hiện lại: bản sao thứ hai, `--hide` F1, `--show` F cuối, interp step.
- Bia: `obj add target --box RỘNG,CAO,DÀY --at x,y,z_đáy` (hộp đặt theo đáy). Khung playblast cam game chỉ ôm nhân vật: bia ≤ 2 m, `--dist 2`.
- Đo mũi dao trước gốc xương (SDR01: dao 56 cm, mũi trước gốc 31 cm) để đặt độ cắm vào bia.
- **Dao dài chĩa ngược lúc ném dễ xuyên mũ** (SDR01 Shoot b7→b8): đặt tay ra NGOÀI đầu phía camera và nghiêng lưỡi ra ngoài; đo bằng
  `sdr01/head_clear.py` (đỉnh dao/găng trong hộp đầu và < 2 cm = chìm), yêu cầu hở ≥ 8 cm ở frame tay gần mặt.
- **Đạo cụ xuyên lòng bàn tay (bút team `accessory`, G-LumberCity Clean Output 2026-11-03):** nắm tay áp mũi/miệng thì bút (−10..+21 cm qua lòng tay) luôn chéo trước mặt ở góc front; vặn cổ tay 60–75° không cứu được mà làm cẳng tay lệch Idle1 50–76°. Cam game nhìn lưng → đưa user chọn ảnh tĩnh (A giữ / C hạ nắm tay xuống miệng / B mu cổ tay) thay vì sửa mò vòng 4. User chọn A (vặn ~38°). Tìm góc bút: lọc theo cổ tay ≤ 25° và vặn ≤ ngưỡng user rồi mới chọn khe hở (`pen_aim` trong `lumber_clean_output/build_keys.py`).
- **Sổ quạt (team `pCube1` 33×37 cm, mép trên kẹp giữa tay):** dựng tay theo hướng sổ: sổ chĩa dọc cẳng tay, mặt sổ đứng, pháp tuyến ngang ⊥ cẳng tay → quét ngang là đẩy gió (`book_arm`). Từ cam game sau lưng, cung quạt phải nằm lệch trái thân + ngang ngực, và tay phải VƯƠN XA thân (user: "tay cầm quạt cho với về trước nhiều hơn": cổ tay cách ngực 26 → 34 cm, khuỷu 96 → 65°).

## prop-rescale-keep-grip
- **Phóng to prop đã có anim mà không sửa anim** (nỏ map3 ×1,25, 2026-11-03, duyệt lượt 2): anim bake FK, prop con của một cổ tay, tay kia cầm chỗ khác → scale đều quanh một điểm làm tay kia lệch 8–11 cm. Cách đã duyệt: đo hai điểm cầm trong khung xương prop, giữ nguyên đoạn giữa hai tay (cả mặt cắt), chỉ giãn phần ngoài (z ngoài hai tay, x/y tăng dần trong 6 cm), phần to rõ (cánh, mũi) scale đều quanh gốc nối thân; dây/chi tiết nối hai phần: đỉnh bám xương động giữ, đỉnh đầu kia theo phần to. `work/shoot_die_repeat/xbow_scale/scale_props.py`.
- Mesh prop có thể được prefab khác dùng lại (mũi tên bay `Projectile Arrow` dùng mesh mũi tên trong rig, đặt lệch theo vị trí đỉnh): làm dày quanh trục để tâm không dời; nếu kéo dài thì báo dev đầu mũi tên bay đi trước thêm (Δ × scale prefab).
- "Mũi tên dày 30 %" chưa đủ: user muốn mũi tên **dài hẳn ra**, đầu nhọn nằm trọn trước mũi nỏ (+12 cm). Khi nỏ to lên, kiểm phần mũi tên nhô ra phía trước còn đọc được không.
