# Tay, cánh tay, bàn tay (mọi loại anim)

## no-overbend
**KHÔNG bẻ khớp quá đà, phá vỡ giải phẫu** (lỗi nghiêm trọng - người duyệt đã nhắc 2 lần). Nguyên lý: Solid Drawing.
- **Lần 1 - Idle 133F, tay trái cầm chùy:** "tay bị xoắn vặn quá đà phá cấu trúc Anatomy". Nguyên nhân: đặt hướng bàn tay
  theo trục xương để khớp cán -> cẳng tay xoắn **169° ở khuỷu**. Sửa: khuỷu là bản lề thuần (chỉ gập quanh local Z, xoắn
  ±5°), xoắn chia cho vai và cổ tay (`fk_left_arm`), giới hạn khớp theo rig.
- **Lần 2 - Attack f13, hai tay trên cán:** "hai cánh tay bị bẻ quá giới hạn và xoắn vặn hỏng anatomy". Sửa: giải bài toán
  cầm (`solve_grip`): điểm cầm được trượt quanh/dọc cán, cổ tay chỉ lệch nhỏ quanh tư thế cầm tự nhiên, khuỷu ở ngoài thân,
  chấm lại trên da thật (`arm_strain`); tay gần thẳng mới với tới thì xoay/nghiêng thân (vai) chứ không bẻ tay
  (SKILL.md quy tắc 10).
- **Ngay khi rig xong** (đề xuất của người duyệt: "cần thêm bước giới hạn góc xoay, trục xoay của các khớp theo từng model"):
  khai báo trục và giới hạn góc xoay từng khớp theo model (`work/<dự án>/<job>/joint_limits.json`), mọi pose phải qua
  `joint_limits.py` = 0 vi phạm.
- **Quy tắc:** không bao giờ ép hướng/vị trí bàn tay (hay bàn chân) bằng cách bẻ chuỗi khớp - dời gốc chuỗi (vai, hông,
  thân) hoặc điểm tiếp xúc trước. Ưu tiên giải phẫu hơn khớp silhouette/ref.
- **Số góc có thể lừa:** góc "xoắn" so với rest có thể lệch ~180° (khuỷu trái gập ngược trong rest) - tin độ căng da và
  close-up hơn bảng góc (SKILL.md quy tắc 11).
- Checklist bắt buộc trước khi gửi: xem `qa_anatomy.md#pre-send-checklist`.

## twist-split
- Xoắn tay chia cho vai và cổ tay, khuỷu là bản lề thuần; khiên/giáp cẳng tay theo độ xoắn **cánh tay trên**, không xoay độc lập.
- Kiểm rig tìm xương phụ chưa key ngay từ bước phân tích (`rig_inventory.py`); tên xương có thể sai lệch (xem `blender_tools.md#rig-inventory`).

## fk-arm-plane
- Tay FK theo **mặt phẳng khuỷu** (sdr_lib.arm_plane): trục bản lề khuỷu = pháp tuyến mặt phẳng (cánh tay trên, cẳng tay),
  khuỷu gập thuần, chỉ cổ tay xoắn ≤40°. Xoay ngắn nhất (im_bone) cho roll vô nghĩa -> tìm hướng dao bằng cuộn vai tới
  -150° = xoắn vắt khăn ở vai (SDR Idle, tự phát hiện bằng close-up).
- Tay FK theo mặt phẳng khuỷu phải **bắt đầu từ rest** (thẳng, không xoắn) (SDR Attack blocking v1, 2026-10-20): P0 đã xoắn
  cẳng tay 78° quanh xương khuỷu nên trục bản lề lệch, giải từ P0 làm khuỷu gập sai trục (mọi key khuỷu 71-76°).
- IK tay phải gập lệch trục (Gaygor Attack, khuỷu xoay 77° quanh Y): chuỗi IK dựng từ tay gần thẳng -> căn roll + khóa IK theo bản lề.

## palm-dir
- **Kiểm hướng lòng bàn tay** (palm_dir) ở mọi pose cầm đạo cụ, không chỉ hướng lưỡi. SDR Idle v10: đổi sang cầm ngược để
  lưỡi chĩa ra sau mà khỏi xoắn tay -> lòng bàn tay lật ra ngoài ("mặt này là lòng bàn tay, phải hướng vào trong").
  Đúng: chọn hướng lòng bàn tay trước (cầm dao ném: lòng tay vào thái dương), sấp/ngửa cẳng tay chia đôi xương khuỷu
  (roll dọc cẳng tay) + cổ tay (155° = 78 + 78, da sạch; dồn hết vào cổ tay -> da nén x0.27), rồi hướng lưỡi tự ra từ
  cách cầm búa (lưỡi phía ngón cái); nghiêng lưỡi lên/xuống bằng lệch cổ tay về phía ngón út/cái (≤ ~25°).
  Lưỡi cầm kiểu búa luôn ⟂ bàn tay.

## wrist-sweep-prop-dir
- Prop theo nét vẽ (SDR Attack F4): khi góp ý là hướng của prop ("bẻ ra sau ít hơn" + nét chỉ hướng lưỡi dao), đừng đoán góc
  cổ tay — đổi nét vẽ thành vector đích rồi **quét góc cổ tay** trong mặt phẳng cẳng tay, chọn góc cho hướng lưỡi khớp nhất
  (lưỡi (0, 0,9, −0,42) = ra sau, chếch 25°, quét ra +25°, khớp 1°). Giữ cổ tay ≤ 25° so với cẳng tay.

## free-arm
- **Tay tự do:** dùng IK để khuỷu gập theo nhịp (tay nhấc hơn vai -> khuỷu đẩy ra sau); giữ khuỷu luôn gập (>40°), duỗi
  thẳng trông chết (Idle_Front: "cánh tay dùng IK... khuỷu đẩy ra sau", "ở F26 tay duỗi thẳng quá"). Cách làm: SKILL.md Polish rules (`arm_ik_R.py`).
- Tay tự do: nắm đấm, khuỷu hướng ra ngoài, gập vừa phải - đẹp hơn khớp ref máy móc (Idle: "theo ref tay nắm đấm, khuỷu cong
  ra ngoài hơn" / "khuỷu co vào thêm chút là đẹp").
- **Tay buông nắm đấm** (Gaygor P0 Cascadeur, người duyệt khoanh "bàn tay đang bị ngửa ra quá"): khi cẳng tay chĩa chéo ra trước
  mà giữ hướng bàn tay của bind (lòng bàn tay quay vào đùi) thì nắm đấm trông ngửa. Đúng: cẳng tay úp (lòng bàn tay quay về
  sau-trong, ngón cái vào trong), cổ tay gập nhẹ 15–25° về phía lòng bàn tay cho nắm đấm chĩa xuống. Kiểm bằng pháp tuyến lòng
  bàn tay của mesh (index-pinky × hướng ngón) chứ không bằng mắt.
- Tay đối trọng lúc ném (SDR polish v5): xem `attack.md#sdr-attack` (co lại, khuỷu ~90°).

## reach
- Luôn kiểm tra vai -> điểm nắm <= dài tay (Gaygor Attack: tay trái không với tới; cổ tay copy IK che việc này, cẳng tay "giãn" 22%).
  Kiểm cổ tay đứt bằng độ dài cẳng tay.
- Tay gần thẳng mới với tới = dời vai (xoay/nghiêng ngực, đầu bù), không bẻ tay. Với SDR map06: đưa xương Scapula ra trước 20°
  thay vì xoay thân nhiều (xem `props_weapons.md#oversized-prop`). Cascadeur f31: dời bả vai/vai lên-trước (+30–35 Z) thì tay mới
  với tới đuôi cán.
- Tay đưa qua đầu mà khuỷu khép vào trong: vai thấp -> nhún Scapula (~20°) thì khuỷu mở ra như ref (Gaygor Attack f31).
- `solve_grip` trả None khi mọi điểm nắm ngoài tầm: tính trước khoảng cách vai -> điểm nắm (trục + 0,34 bán kính) cho từng s,
  mở dải s về phía vai. Tay với không tới phía ngoài chùy khi vai bên đó lùi sau: chọn phi lệch về phía vai (f8 L phi 140).

## shoulder-compression
- **Vai gấp lõm = da vai bị nén < ~0,3** (SDR map06, user xem trong Blender: vai trái lõm ở mặt trước khi tay với ra trước để
  nắm ốp nòng). Hướng khuỷu (pole) và hướng bàn tay quyết định độ nén ở vai, trong khi góc khuỷu gần như không đổi. Hãy dò pole +
  hướng tay + điểm cầm với mục tiêu "nén vai tối thiểu cao nhất", rồi xem close-up shading xám đặc, đúng góc người duyệt nhìn.
- **Vai xoắn = nếp gấp da vai, đo được** (review Reload b22 F9/F15/F25: "Vai bị xoắn"). Rig không có xương twist cho bắp tay,
  nên hướng pole quyết định độ roll của xương Shoulder. Khi tay gần duỗi, pole tùy ý có thể làm roll lệch P0 tới ±150°. Đừng lấy
  pole cố định: hãy xoay pole quanh trục vai→tay (±90°) và chấm điểm từng nghiệm: tỉ lệ cạnh da vai nhỏ nhất (anatomy 'skin
  shoulder', phải ≥ 0,30; nếp gấp người duyệt khoanh là 0,14–0,20) là ưu tiên số 1, rồi mới đến khuỷu ra ngoài (đo theo trục
  ngang của góc front, vì người duyệt vẽ trên góc đó). Tay ôm vật trước ngực mà khuỷu ra ngang > 5 cm thì vai gập: báo đánh đổi
  cho người duyệt, đừng cố cả hai.
- **Ngưỡng căng da phụ thuộc mesh:** áo khoác low-poly có chỉ số căng ~1,9 ở cổ và cột sống ngay khi tay rời T-pose (tay buông
  tự nhiên đo được 2,2). Lấy mốc là pose tự nhiên của chính mesh đó, không dùng cứng ngưỡng 1,6.

## elbow-pole
- Đẩy khuỷu "ra một chút" = đổi pole theo trục ngang của đạo cụ, mỗi 0,5 ≈ 3 cm; theo dõi độ nén da vai (SDR map06 Shoot b11).
- Khi dò hướng khuỷu, ràng buộc cả độ thấp so với vai (khuỷu thấp hơn vai 12–20 cm), không chỉ độ ra ngoài và da vai (SDR06
  Reload, 2026-10-21; xem `#prop-hand-side-fk`).
- Cầm trống tròn: khuỷu ra ngoài vai ≥ ~10 cm (xem `props_weapons.md#grip-drum`). Ghi chú: ba con số này không mâu thuẫn -
  khuỷu ra ngoài khi cầm vật bên hông/dưới súng, nhưng ôm vật trước ngực thì ưu tiên da vai (`#shoulder-compression`).

## spline-ik-arms
- **Spline tay đã giải IK theo từng key: kiểm độ xoay dọc trục trước khi nội suy** (SDR06 Reload spline v1, 2026-10-21, góp ý
  "tay thay đạn bị xoay loạn xạ"). Bản stepped trông ổn vẫn có thể giấu key có bắp tay xoay 270° quanh trục mình, hoặc bản lề
  khuỷu lấy theo độ xoắn của frame trước. Khi spline, tay sẽ vặn giữa các key. Cách làm: (1) đo độ xoay bắp tay của từng key so
  với lời giải chuẩn (reset khuỷu về tư thế gốc rồi mới giải `arm_plane`); (2) frame trung gian dùng IK hai đoạn giải tích (vị
  trí cổ tay theo vật đang cầm, hướng khuỷu nội suy), không dùng CCD hay dò góc riêng từng frame; (3) độ xoắn cẳng tay tính ở
  key (chia đôi với cổ tay), nội suy theo đường ngắn giữa key, đừng cộng dồn kiểu unwrap theo frame (F cuối sẽ lệch F đầu);
  (4) slerp quaternion phải ép đường ngắn (dot < 0 thì đảo dấu). Đo Δ góc vai/khuỷu/cổ tay theo từng frame, rồi render camera
  cận phía tay đó (góc game và top bị thân/mũ che).

## prop-hand-side-fk
- **Review tay thao tác prop ở góc tay đó đang làm việc, không chỉ góc game** (SDR06 Reload, 2026-10-21). Góc right (ingame)
  che hết tay trái thay trống; từ góc left mới thấy khuỷu vung lên ngang vai rồi tụt xuống rồi ra sau. Đó là hệ quả của các góp
  ý "đẩy khuỷu ra" khi chỉ xem từ góc right. Playblast clip có tay xa camera phải thêm góc phía tay đó (cỡ lớn).
- Tay đang di chuyển prop: diễn **FK** giữa các key, prop đi theo bàn tay (người duyệt muốn thử FK); chỉ giữ IK ở đoạn tay bám
  vật cố định (ốp lót tay). Prop xuyên áo thì dang cả cánh tay theo nhịp sin, biên độ tối thiểu đủ để thoát.
- Đọc vị trí tay so với đạo cụ ở góc top (góc nghiêng giấu chiều sâu): Idle "bắp tay phải nằm ngoài cán, khuỷu chĩa xuống trước"
  (SKILL.md quy tắc 6).

## joint-limits-in-solver
User 2026-10-22: "tạo giới hạn cho các joint để tránh các lỗi bẻ pose quá đà sai Anatomy. AI cũng tránh phải thử quá nhiều lần".
- `legacy/blender/arm_limits.py`: `arm_angles(side)` đo elbow_flex, elevation, humeral_rot, pronation, wrist_flex, wrist_dev TỪ VỊ TRÍ KHỚP + lòng bàn tay (zero giải phẫu, giống nhau mọi rig). Đừng đo bằng Euler local: rig SDR có trục xương Wrist = -X local, tail của Wrist KHÔNG chỉ về ngón tay.
- Dấu đã kiểm trên rest: gập về lòng bàn tay +, lệch về ngón út +, sấp (pronation, ngón cái xuống) +; T-pose lòng úp = 0.
- `hand_on_limited`: mỗi lần thử reset Shoulder/Elbow/Wrist về cùng basis (arm_plane cần khuỷu không xoắn; quên reset → cổ tay lệch 33 cm). Xoay pole quanh trục vai→điểm cầm theo danh sách `swivels`; cổ tay vượt giới hạn thì nắn hướng bàn tay vào vùng cho phép (lòng tay vẫn đặt đúng điểm cầm). Chọn: vi phạm ít nhất → hướng tay đổi ít nhất (`hand_clamped`) → gần pole yêu cầu.
- `limit_fail` còn lại (thường elbow_flex = với không tới) → sửa spec key (đưa vật lại gần), không ép tay.
- Giới hạn SDR: work/shoot_die_repeat/sdr06/joint_limits.json; nới để P0 đã duyệt qua được (L pronation -111, wrist_dev +44.5).
- Phát hiện đầu tiên: key cầm trống Reload b1 gập cổ tay 120–178° (hướng tay trong arm_target không hợp với cẳng tay) — đây là lỗi "tay chưa tốt" F23; `hand_clamped` lớn (~90°) = hướng tay của mode đó sai, nên sửa mode chứ không chỉ kẹp.
- Khuỷu chìm vào thân (user 2026-10-22 "Khuỷu tay đang bị chìm vào trong cơ thể", b2q2): solver xoay pole –120° để tránh nhăn vai → khuỷu ép sát sườn, lùi ra sau; nhìn trước thì bắp tay khuất, cẳng tay như mọc ra từ áo. Thử nghiệm "điểm trong mesh" (tia ra/vào) KHÔNG bắt được vì mesh low-poly hở (áo 1 lớp). Đo đúng = `elbow_gap`: khe ngang giữa da khuỷu và da thân/áo cùng độ cao + độ sâu; P0 = 7+ cm, chìm = âm. Đưa vào cost (10/cm dưới GAP_MIN 6 cm) cùng `elbow_covered` và nhăn vai. Luôn render cả góc TRÊN để kiểm khuỷu với thân.

## pole-spec
**Pole không bao giờ là biến tự do** (user 2026-10-22: "ở dự án SDR việc để pole vector của IK tự do tốn rất nhiều lần thử hãy
rút kinh nghiệm từ đó"). Nguyên lý: Solid Drawing (khối tay/chân đúng hướng) + Arcs (roll liên tục giữa key).
- Chuyện ở SDR map06: hướng khuỷu là đầu ra của solver, mỗi vòng review thêm đúng 1 ràng buộc → khoảng 9 vòng chỉ để sửa khuỷu/vai:
  khuỷu ra ngoài (Shoot b10, b11; Reload b15, b16), ôm trống (b21), vai xoắn = roll bắp tay (b22→b23), khuỷu chìm vào thân
  (lhand_b2q2→q4), tay xoay loạn xạ khi spline (spline v1). Mỗi ràng buộc mới lại đẩy pole sang chỗ phá ràng buộc cũ.
- Cách làm từ nay:
  1. **Gốc của pole đi theo khối nó thuộc về:** pole khuỷu là con của ngực (hoặc bàn tay khi tay cầm prop), pole gối là con của
     IK bàn chân (gối theo mũi chân). Pole đặt trong world sẽ bị bỏ lại khi người xoay hoặc nhấc chân. Gaygor Attack v9 có pole gối
     trong world: gối phải lệch mũi chân 99–176° ở f25–f28.
  2. **Hướng khuỷu/gối là một phần spec của key**, đọc từ ref như hông hay prop (khuỷu: ra ngoài / xuống / ra sau bao nhiêu cm so
     với vai; gối: theo mũi chân hoặc lệch có chủ đích), không để solver tự chọn.
  3. **Kiểm mọi ràng buộc CÙNG LÚC, cho mọi key, trước khi render**: `legacy/blender/pole_audit.py` (gối lệch mũi chân ≤ 30°,
     khuỷu thấp hơn vai 12–20 cm với tay tự do hoặc tay cầm vật bên hông, roll bắp tay giữa hai key liền nhau ≤ 60°) cộng thêm
     `elbow_gap` ≥ 6 cm, da vai ≥ 0,30 (`#shoulder-compression`, `#joint-limits-in-solver`). Có xung đột thì báo đánh đổi cho
     người duyệt, đừng để mỗi vòng review sửa một thứ.
  4. Solver chỉ dò pole quanh hướng trong spec (±30°), không quét ±180°.
- Gaygor Attack v9 (audit 2026-10-22): gối phải f13–f21 41–46°, f25/f26/f28 99/107/176°, f31 36°; gối trái f32 50°; roll tay trái
  nhảy 82–152° ở f8, f13, f21, f25, f31, f64 → sửa trong v10 cùng các lỗi pose (`work/boss_gaygor/attack/v10rev/defects_v9.md`).

## thick-bar-grip
Người dùng 2026-11-03 (G-LumberCity Ropeway Crank s2, tay quay dày 9,3 cm): "kiểm tra lại bàn tay, đang bị nắm và nhiều quá".
- Lỗi: s2 nắm kín (curl 0,85), cổ tay đặt 7 cm sau tâm thanh dọc cẳng tay → thanh xuyên qua khớp ngón (Middle1 cách trục 3,4 cm < bán kính 4,65), bàn tay chĩa dọc thanh. Ảnh toàn thân không thấy; chỉ cận cảnh (render_pose `--focus Wrist_R:14`) mới thấy.
- Đo trước khi nắm: bán kính prop chỗ cầm, chiều dài bàn tay (MC_Worker: cổ tay → khớp ngón 12,4 cm, đốt ngón 5,8 cm, ngón đã cong 59° ở curl 0). Prop dày hơn tầm ôm của ngón → không nắm kín: lòng bàn tay áp thanh, ngón gần mở vắt qua (curl ~0,1).
- Bộ giải `work/g_lumbercity/lumber_ropeway_crank/grip_wrap.py`: hàng khớp ngón song song trục thanh; tâm thanh ở điểm HOOK trong hệ cổ tay (MC_Worker R: (10, −1, −7,2), L: lật cả 3 trục); xoay bàn tay quanh trục thanh (psi) để cổ tay gập ít nhất (14–27°), psi frame trước làm hạt giống frame sau (liền mạch); xoắn chia nửa khuỷu nửa cổ tay; pole khuỷu bớt bè (x × 0,3).
- Rig mirror: hệ trục khớp tay trái có thể là âm của tay phải (MC_Worker: hướng bàn tay −x, trỏ −y, lòng +z) — đo từng bên, đừng chép HOOK.

- **Tay gần thẳng: ik_arm chọn nhầm chiều gập** (SDR05 Colt P0, 2026-11-03). Với reach ≥ 0,98, `rigpose.ik_arm` có thể chọn nghiệm khuỷu duỗi quá (−12° so bind),
  mũi khuỷu chĩa lên, rồi cổ tay/cẳng tay xoắn 110–150° để giữ prop đúng hướng. Luôn đo khuỷu bằng `joint_rules.decompose` so BIND
  (gập > 0, xoắn ≈ 0) và cổ tay so bind. Cách đúng (`sdr05_colt/p0_build.py`): khuỷu = bản lề gập N° so bind (`set_elbow`), cổ tay thẳng,
  xoay CẢ cánh tay quanh trục vai→cổ tay cho prop ngửa đúng (`twist_arm`), rồi xoay quanh vai để nhắm. Đo "bàn tay so cẳng tay" bằng xương
  ngón là sai khi rest ngón đang nắm.
- **Ngắm súng 2 tay (Weaver)**: user tự chỉnh P0 (2026-11-03 "chỉnh lại khuỷu tay với bả vai"): tay súng duỗi thì **mũi khuỷu chĩa xuống**
  (xoay trong ở vai), cẳng tay sấp ~40° bù. Tay đỡ: khuỷu chĩa xuống–ra ngoài ~35°, cổ tay gập 25° ôm dưới, 2 nắm tay ≤ 6 cm, phải ló
  ra dưới tay súng ở cam game (Director v5: khuỷu đỡ ngang vai thì cam game đọc thành cầm 1 tay).
## ref-arm-retarget-anat
(2026-10-29, Mob Era Ride_Throw, user F3–F8: "lỗi khớp vai, cẳng tay, bàn tay, bị gập quá mức, đối nghịch rotate của nhau")
- Key ref cùng rig vẫn có thể hỏng giải phẫu: ref vặn vai 60–118° rồi vặn ngược cổ tay 69° để bù, khuỷu lệch trục bản lề 15–20°.
  IK "rot_of" (xoay nhỏ nhất) trên khuỷu còn làm tệ hơn (F8 khuỷu bẻ 104°, lệch trục 38°). Nguyên lý: arcs + giải phẫu (khuỷu là bản lề).
- Cách sửa được dùng: khuỷu chỉ gập quanh trục bản lề của pose main (đo: cross(cánh tay trên, cẳng tay)); vai = khung 2 vectơ
  (hướng cánh tay trên + trục bản lề thế giới của mặt phẳng vai-khuỷu-cổ tay); đường khuỷu (pole) làm mượt vòng 1-2-1 để vai không bật vặn;
  cổ tay không vặn, chỉ gập theo pha; giới hạn bả vai thì dời điểm tay theo độ dời của khớp vai (không ép tay với quá).
- Bả vai khi tay qua đầu: giới hạn chặt (30°) dồn hết vào khớp vai → đỉnh vai nén (0,08); 50° cân bằng (nén 0,19, giãn sườn 2,71 < ref 3,02).
- Đo: arm_probe (swing/twist mỗi khớp so với main, khuỷu off-axis) + da so main theo frame; script `work/mob_era/ride_throw/build_ride_throw.py` (ANAT).
- Duyệt "ổn rồi" ở v5 (2026-10-29). Các vòng: v3 tự thêm xoắn/đổ/nhấp thân bị user bỏ ("back toàn bộ nhịp xoay nhấp") → v5 lấy **đúng delta
  thân + chân của ref** (lưng ngả xuống đỉnh 7,7° ở F12, trễ ~5F sau cú ném; chân hất ngược rồi đưa tới) - khi có ref, nhịp thân học từ ref,
  không tự thiết kế. Key user sửa trong Studio đọc từ `work/store/<clip>_pose_lab/keys/` (`ride_throw/studio_keys.py`: so với glTF đã xuất,
  > 0,5° mới là chỉnh thật, 0,1° là làm tròn); tay nắm cố định (đai thú) = IK + khoá hướng bàn tay thế giới như F1 sau khi thân đổi.

## chibi-retarget-skin
(2026-10-29, Mob Era Ride_Cheer từ Mixamo "Cheering While Sitting")
- Retarget lên chibi: tay (46 cm) không giơ qua đầu (r ≈ 42 cm) được - chọn điểm cổ tay gần ý ref nhất ngoài khối đầu + chừa nắm đấm ~10 cm,
  khuỷu né đầu ≥ 6 cm (xoay pole quanh trục vai→cổ tay); đầu/cổ chỉ lấy 50/60% xoay ref (100% → đầu to đổ ~50°, che nắm đấm).
- Kết clip về main: KHÔNG dùng lớp bù retarget hiện dần ở cuối nếu tư thế ref cuối khác main (user: "không cần phải từ frame 70 rồi lại đẩy
  khuỷu tay lên trên") - nội suy local từ tư thế ref về main trong ~10F rồi giữ main.
- Nách lồi lõm do weight nhảy gắt (đỉnh dưới nách 97% Chest cạnh đỉnh 79% Shoulder): làm mượt Laplacian chỉ giữa Chest/Scapula/Shoulder,
  vùng 17 cm quanh khớp vai bind, 8 lượt (`work/mob_era/ride_cheer/armpit.py`), đo "lồi lõm" = đổi Laplacian đỉnh so với main; ghi weight
  vào FBX bằng `outputs.set_weights` (cluster Indexes/Weights), đọc lại kiểm tổng = 1.
- IK bản lề luôn có 2 nghiệm khuỷu cho cùng độ gập: chọn nghiệm GẦN FRAME TRƯỚC (không chọn theo phía cố định) - nếu không, khuỷu nhảy
  ~130°/F, vai vặn ngược, cổ tay bù ~160° → user thấy "xoắn mesh quá đà" (Ride_Cheer F10–F16, 2026-10-29). Kiểm mọi bản: tốc độ xoay
  vai/khuỷu/cổ tay °/F, > ~40°/F là lật nghiệm, không phải anim. Sửa giữ hướng cánh tay trên + bả vai: chỉ giải lại góc khuỷu + vặn vai + cổ tay.
- Tay giơ cổ vũ qua vai (Ride_Cheer v9, user: "hướng khuỷu tay phải giơ sang bên phải chứ không phải ra đằng sau mới đúng anatomy",
  "tay đang bị vươn quá mức"): pole khuỷu ra NGOÀI (cùng phía tay), hơi thấp, không ra sau; vai→cổ tay ≤ ~88% tầm tay (khuỷu gập 45–65°
  ở đỉnh), đừng duỗi gần hết tầm. Muốn thấy nắm đấm từ cam game sau-trên: đẩy cổ tay ra ngoài viền đầu (chibi ≥ ~11 cm) chứ không duỗi tay.
