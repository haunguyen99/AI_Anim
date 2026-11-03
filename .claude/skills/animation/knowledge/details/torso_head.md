# Thân, cột sống, hông (phần thân trên), đầu (mọi loại anim)

## spine-chain
- **Cột sống gãy khúc** (người duyệt khoanh, Gaygor P0 Cascadeur): dời riêng điểm Chest để khớp đầu/mặt dây chuyền làm X của chuỗi
  Root→Spine1→Chest→Neck thành 3→1→15→7 (zigzag). Dời thân trên phải chia đều theo chuỗi; thêm vào anatomy pass: góc gập ngang
  (nhìn trước) và gập dọc giữa các đốt cột sống liên tiếp, không đổi dấu xen kẽ, mỗi đốt ≤ ~10°.
- Nhìn nghiêng: góc nghiêng về trước của từng đốt phải tăng dần từ hông lên đầu (P0 Gaygor: 10→9→21→43°); đốt ngực–cổ đứng thẳng
  giữa hai đốt nghiêng = lưng ưỡn ngược (người duyệt bắt lỗi). Muốn dời Chest thì dời cả vai/bả vai theo, chỉ ghim cổ tay.
- Cascadeur: muốn lưng cao thì đổi góc gập, không tịnh tiến (xem `cascadeur.md#autoposing`).

## partial-fix-hip
- **Sửa một phần, giữ nguyên phần còn lại** (SDR map06 Shoot b11 F1, 2026-10-21: "Hip nghiêng về trước nhiều quá… giữ nguyên thân
  trên"): đổi độ nghiêng hông thì xoay Root quanh **gốc cột sống** (Spine1 head), không quanh khớp Root, rồi bù đúng góc đó ngược
  lại ở Spine1; tâm xoay bàn chân lấy trước khi nghiêng; đạo cụ neo vào hông thì dời theo đúng độ lệch. Kiểm bằng số: gốc cột
  sống, 2 vai, tay cầm súng, góc khuỷu, mắt cá phải trùng bản cũ (chỉ hông + gối đổi). Bù kiểu "giảm hông X°, tăng spine X°" quanh
  khớp Root vẫn làm thân trên lùi 2,4 cm và khuỷu trái duỗi 55→37° (lỗi). Đẩy khuỷu ra: `arms_hands.md#elbow-pole`.

## world-axis-roll
- **Xoay theo trục world sẽ lệch khi hướng người đổi** (SDR map06 Shoot b4: "vai đang bị bẻ xuống quá đà"). chest_roll quanh
  trục Y world vốn để hạ vai phải; sau khi cả người xoay thêm 30° thì nó lại kéo vai TRÁI thấp 2,8 cm và sụp vào trong. Mỗi lần
  đổi hướng người, đo lại chênh lệch độ cao 2 vai và xem góc 3/4. Tốt hơn là xoay theo trục local của xương.

## twist-reading
- Silhouette mù với xoắn thân khi prop và chân chiếm viền (Attack f13: 18 thử twist/bend đều 0.64-0.67): đọc xoắn bằng việc
  camera nào thấy ngực/lưng (SKILL.md quy tắc 9).
- Xoắn ngực đọc nhầm hướng (Blender Attack f13: −60° rồi 0°): đọc theo "camera nào thấy ngực/lưng", ghi lại suy luận.
- Cascadeur f21: đọc ảnh thấy view left ref nhìn lưng, nhưng xoay ngực −60° làm IoU tụt 0,56 → 0,44 → để người duyệt xem.
- Thân tự xoắn để với tay khi fit hàng loạt -> khoá twist/roll khi ref đối xứng (blocking v4).

## body-height
- Đo `body_top` trước khi quyết độ gập: Attack f13 thân gập quá (đầu thấp 25 cm) trong khi đỉnh đầu ref chỉ thấp hơn lúc đứng
  ~10 cm -> thân gần thẳng. P0 Idle có đầu cúi (1.76 m) nên phải ngẩng đầu để đạt 1.88.

## square-body
- Tự rà v7 -> v8 (Blender Attack, "chưa được, tự view lại bằng mắt"): bảng REF|ANIM 4 view mỗi key lộ lỗi KHỐI LỚN mà IoU không
  thấy: thân lăn nghiêng/xoắn ở pose ref đứng vuông (nằm sấp f33–46 hông lăn 13°, f52–58 vai xoay 40–50°). Đo đường hông/vai
  (yaw, roll) + hướng cột sống trên mặt đất, sửa bằng `sym_fix.py` (root yaw/roll + xoắn/nghiêng sống-ngực) về đích đọc từ ref
  (vuông = 0°, KHÔNG lấy P0 15°), rồi giải lại tay bị rách.

## open-to-camera
- **Game cuộn ngang: mở người về phía camera ingame** (review Shoot b3 F5: "cho body xoay hướng ra góc cam khoảng 30 độ nữa"). Ngực
  mở ~55° ra cam, prop vẫn ngắm thẳng mục tiêu. Đặt P0 cho nhân vật side view thì bắt đầu ở tư thế mở này, đừng để gần như
  nghiêng hẳn. Đổi hướng người thì đặt lại prop theo hông mới và giải lại mọi key cầm prop.
- Muốn ngực quay về camera: **xoắn eo/ngực** (SDR Idle: Spine1 -25, Chest -30), hông vẫn gần hướng mục tiêu - xem `idle.md#sdr-one-pose`.
- Lấy đà phải đọc được **từ góc camera** (SDR Attack polish v3): xoắn ngực gần như vô hình ở góc nghiêng, phải ngả thân ra sau (14°)
  + kéo khuỷu thấp ra sau.

## lean-from-hip
- Đổ người về mục tiêu phải bắt đầu từ hông, không từ cột sống (SDR Idle v15–v19, chốt v19: chậu hông 7,5°). Chi tiết và các
  bản bị bác: `idle.md#sdr-one-pose`.

## head
- **Đầu giữ hướng nhìn:** khóa yaw theo hướng đã duyệt; phần bù pitch tác động sớm để đầu vẫn trễ sau cổ.
- **Đầu cũng mở ra cam** (review Shoot b4 F12: "đầu cũng nên xoay ra khoảng 20-30 độ"): người mở ra cam thì đầu nhìn lệch ra cam
  ~25°, không khoá thẳng vào mục tiêu.
- Blender Attack f13 v2 đầu ngửa 32° và bị cánh tay phải che: neck/head `fwd` âm = ngửa. Đo hướng đầu (az/el so với P0) và mép
  đầu (min x/y điểm mesh đầu ở front + left so với ref) bằng số; sweep nhỏ chọn sai số px nhỏ nhất.
- Đầu/cổ chúi trước (SDR v3) → cổ ngả sau 8°.


## turn-chain
- Quay người nhìn/quay về phía tay (G-LumberCity Idle Wipe, user 2026-11-02: "chỉ xoay mỗi ngực nên cảm giác cơ thể bị robot"): góc quay bắt đầu từ HÔNG, chia dọc chuỗi (35° = hông 8 / eo 6 / ngực 8 / cổ 5 / đầu 8; quay 20° về tay = hông 4 / ngực 4 / cổ 4 / đầu 8). Chân IK giữ chỗ (đo trượt cổ chân ≤ 0,02 cm). Kể cả idle "giữ thân yên" của user vẫn cần hông góp vào cú quay.

## Cú nhìn phụ trong anim lặp (Ropeway Crank p4, 2026-11-03)
- Nhìn lên một vật ở cao (cáp, đỉnh máy) mà chỉ ngẩng (pitch) thì từ cam trên cao gần như không thấy: thêm quay đầu (yaw) về phía vật đó, ~25°.
- Điều khiển pitch + yaw bằng MỘT đường cong (smoothstep lên → giữ → smoothstep về), đừng lấy từ các key look_up qua Hermite: dễ ra hai nhịp (đầu khựng giữa pha).
- Thân (Spine1 + Chest, 3–5°) quay cùng chiều, dẫn trước đầu ~2 F (người dùng thích xoay bắt đầu từ thân).
- Thân chồm/ngửa trong lúc nhìn kéo pitch thế giới của đầu theo: đo pitch thế giới mỗi frame rồi bù ở cổ/đầu để giữ ổn định.
- Lúc giữ nhìn, cho trôi nhẹ (~0,4°/F) thay vì đứng chết.
