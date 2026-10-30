# Chân, bàn chân, hông (trọng tâm), sàn (mọi loại anim)

## steps-contacts
- Thường có bước chân (root không trôi nhưng một chân bước tới rồi lùi về) - đo bằng dải tiếp đất ở từng view, đừng đoán
  "in-place" (Attack; SKILL.md quy tắc 9).
- Không giả định tấn đứng chính diện; P0 dựng từ chân lên (SKILL.md quy tắc 3).

## weight-shift
- Attack f25: thân ref dời 0,2 m về chân trụ khi chân kia nhấc (dồn trọng lượng) - chỉ lộ ra trên ảnh chồng 2 màu (front/back/top
  cùng "thừa một phía, thiếu phía kia"); IoU một mình không chỉ ra hướng sai.

## foot-detach
- Blocking v4 (Blender Attack): fit theo hình bóng làm BÀN CHÂN ĐỨT khỏi ống chân (H_Ankle là con của foot IK, Ankle copy vị trí)
  ở 9 key - IoU không thấy. Chân đang tựa: dời hông về bàn chân; chân nhấc: kéo bàn chân về tầm (hip->ankle <= 0,655 m).
- "Dưới đất" phải xem bộ phận nào thấp nhất trước khi nâng hông (f49–54 là mũi chân, nâng hông là sai).
- Dời hông để chân với (`leg_reach`) sau khi fit làm ống chân rách (f10, f44) - kiểm lại độ dài ống chân sau mỗi lần dời.
- Cascadeur: chân trái nằm sấp lơ lửng 26 cm (đã cộng nâng/xoay lên một base vốn đã kiễng) → AutoPosing kéo hông lên 20–47 cm;
  xem `cascadeur.md#base-chain`.

## knee-dir
- Hướng gối so mũi chân không áp dụng khi bàn chân chúc dốc (chân nhấc) - nhìn cận. `knee_dir` báo nhầm khi bàn chân kiễng (f26
  chúc -60°, gối gần thẳng).
- Pole gối theo hướng gối mong muốn, không theo mũi chân xoay ngoài (SDR Idle: gối sau bị đẩy về camera).
- **Gối vặn lúc nhấc chân (2026-10-26, Gaygor Walk spline_b13 F43, user: "chân trái bước lên khớp đầu gối đang xoay vặn khá nhiều").**
  Ảnh nhỏ không thấy, phải đo. Lỗi gồm hai chuyển động ngược chiều trong cùng một đoạn nhấc gót (mũi chân còn lướt sàn): gối xoay
  ra ngoài so với hông 29° → 50°, và bàn chân xoắn ngược 17° quanh ống chân (mũi chân quay ra tới 72° nhìn từ trên). Đo bằng
  `work/boss_gaygor/walk/fb_b13/knee_scan.py`. Đo `knee_yaw` (hướng gối so với hướng hông) và `foot_tw` (bàn chân so với mặt phẳng gối, quanh
  trục ống chân), không đo "gối so mũi chân" (sai khi bàn chân chúc dốc). Lúc đứng trụ `foot_tw` ~15°; khi nhấc chân không được lệch
  quá vài độ so với giá trị đó.
  Sửa (`fix_b14.py`), cổ chân giữ nguyên chỗ:
  (1) xoay đùi quanh đường hông → cổ chân, chặn mềm `knee_yaw` ~35°;
  (2) xoắn cổ chân quanh ống chân mới cho `foot_tw` đi thẳng giữa hai giá trị lúc trụ;
  (3) gập cổ chân quanh trục ngang để mũi chân về đúng độ cao cũ, vì xoắn quanh ống chân dốc làm mũi chân chìm 3–4 cm.
  Kiểm bằng `leg_check.py`: góc cổ chân phải nằm trong tầm của chân bên kia đã duyệt (trái 56° ≤ phải 76°), gia tốc không tăng.
  Chân phải ở b13 có cùng kiểu (`foot_tw` −25° khi vung so với +14° lúc trụ) nhưng chưa bị nhắc.
- Pole gối là con của IK bàn chân, không đặt trong world (gối bị bỏ lại khi nhấc chân); xem `arms_hands.md#pole-spec`.
- Chân sau duỗi thẳng nhìn "căng" → gối sau 20–30° (SDR v3). Với Idle 1 pose đứng lâu: gối sau gần thẳng 8° được chốt (xem
  `idle.md#sdr-one-pose`) - tấn đứng lâu ưu tiên tấn cao.

- **Đùi giật sau một đoạn chỉnh tay ngắn (2026-10-26, Gaygor Walk b16, user: "check lại rotate của đùi phải").** User xoay gối phải vào
  ở F23–F28 lúc vung chân, nhưng F22 và F29 vẫn giữ giá trị cũ. Kết quả: xoắn đùi tụt 30° trong 4F, dạng đùi có khấc chữ V (nhảy
  10–11°/F). Đo bằng `work/boss_gaygor/walk/fb_b13/thigh_scan.py`: gập, dạng, xoắn so với hông, kèm bước và gia tốc mỗi frame.
  Sửa: giữ ý của user (hướng gối) nhưng trải đều ra cả pha vung. Đặt mục tiêu xoắn = bản làm mượt (binomial 5 điểm × 3), hòa vào
  ở hai đầu cửa sổ, đạt bằng cách xoay đùi quanh trục hông → cổ chân (`fix_rthigh.py`). Cổ chân giữ nguyên chỗ, nên khấc ở phần dạng
  đùi tự hết. Sau mỗi lần user chỉnh tay một đoạn, quét ngay bước/gia tốc ở hai mép đoạn đó.

## hip-height
- **Nhịp hông so với bước chân (2026-10-26, Gaygor Walk b15, user: "anim chủ hông đang lệch nhịp so với bước chân").** Đo bằng
  `work/boss_gaygor/walk/fb_b13/hip_scan.py` (Root_M thế giới so với độ mở hai chân `ankleL.y − ankleR.y`, tương quan chéo):
  - Nhún: đáy phải trùng lúc gót chạm đất, đỉnh lúc chân vung qua chân trụ. Bản cũ trễ 3–6F.
  - Xoay hông: phải cùng pha với chân, tức bên chân đang ra trước thì hông bên đó ra trước, đỉnh ở lúc gót chạm. Bản cũ ngược pha
    (gót trái chạm mà hông phải ở trước 7,5 cm), dù số đo biên độ và độ mượt đều "đẹp". Nhìn từ trên thì thân che hông, nên phải đo.
  - Sửa (`fix_hip.py`):
    - nhún: dời chiều cao root;
    - xoay hông: đặt lại theo độ mở hai chân;
    - thân trên: giữ hướng thế giới của Spine1 (pháo, vai đã khớp ref);
    - chân: giữ hướng thế giới của đùi → IK tới cổ chân cũ → xoay đùi quanh trục hông → cổ chân cho gối chỉ hướng cũ.
  - Bẫy dấu: xoay quanh trục lên −Z thì dấu ngược với atan2(dy, dx). Lần đầu biên độ thành 68°; luôn đo lại sau khi sửa.
- Đo độ cao hông bằng **đai lưng** (trước + sau), không bằng khe đùi: vạt khố có xương riêng nên rủ khác ref (Cascadeur Gaygor).
- Từ một vị trí (vạt khố) suy ra góc xoay hông thì phải trừ vị trí gốc hông, nếu không ra 45° thay vì ~60° (Cascadeur Attack).
- Hông xoay quá nhiều làm đùi dạng ngang = dáng ếch/sumo (SDR Idle v2-v5, `idle.md#sdr-one-pose`).

## floor
- Base của key sau là ĐIỂM ĐÍCH của key trước, không phải tư thế đã giải -> sai số sàn cộng dồn; `block_pose` ghim chân
  (`keys/plant.json`) (Cascadeur).
- Kiểm nhanh: đầu ngón chân Y≈0 (`qa_anatomy.md#anatomy-check`).
- Đặt bàn chân phẳng bằng cách lăn bàn chân (roll) làm mũi chân xuyên sàn 8–9 cm (Attack v10 f49/52/53). Dùng `plant_p0(side)`
  (`work/boss_gaygor/attack/v10/fixes.py`): lấy hướng bàn chân P0, chỉ xoay yaw theo hướng thân hiện tại, cổ chân ở độ cao P0 (0,16) → gót + mũi chạm đất.
- Dời bàn chân IK đi xa mà không nghiêng nó = ống chân giãn (0,364 > 0,344) và gối lệch 83° so mũi chân (f28): bước ngắn hơn, không pitch.
