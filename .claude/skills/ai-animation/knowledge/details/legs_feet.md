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
- Pole gối là con của IK bàn chân, không đặt trong world (gối bị bỏ lại khi nhấc chân); xem `arms_hands.md#pole-spec`.
- Chân sau duỗi thẳng nhìn "căng" → gối sau 20–30° (SDR v3). Với Idle 1 pose đứng lâu: gối sau gần thẳng 8° được chốt (xem
  `idle.md#sdr-one-pose`) - tấn đứng lâu ưu tiên tấn cao.

## hip-height
- Đo độ cao hông bằng **đai lưng** (trước + sau), không bằng khe đùi: vạt khố có xương riêng nên rủ khác ref (Cascadeur Gaygor).
- Từ một vị trí (vạt khố) suy ra góc xoay hông thì phải trừ vị trí gốc hông, nếu không ra 45° thay vì ~60° (Cascadeur Attack).
- Hông xoay quá nhiều làm đùi dạng ngang = dáng ếch/sumo (SDR Idle v2-v5, `idle.md#sdr-one-pose`).

## floor
- Base của key sau là ĐIỂM ĐÍCH của key trước, không phải tư thế đã giải -> sai số sàn cộng dồn; `block_pose` ghim chân
  (`keys/plant.json`) (Cascadeur).
- Kiểm nhanh: đầu ngón chân Y≈0 (`qa_anatomy.md#anatomy-check`).
- Đặt bàn chân phẳng bằng cách lăn bàn chân (roll) làm mũi chân xuyên sàn 8–9 cm (Attack v10 f49/52/53). Dùng `plant_p0(side)`
  (`work/attack/v10/fixes.py`): lấy hướng bàn chân P0, chỉ xoay yaw theo hướng thân hiện tại, cổ chân ở độ cao P0 (0,16) → gót + mũi chạm đất.
- Dời bàn chân IK đi xa mà không nghiêng nó = ống chân giãn (0,364 > 0,344) và gối lệch 83° so mũi chân (f28): bước ngắn hơn, không pitch.
