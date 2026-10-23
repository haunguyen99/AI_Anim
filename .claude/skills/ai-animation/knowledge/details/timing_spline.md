# Timing, spline, overlap, chi tiết phụ, loop (mọi loại anim)
Quy tắc polish cơ bản (shift keys theo chuỗi, quaternion post-multiply, `match_seam`, jerk, biến thể clip): SKILL.md "Polish rules".

## shared-curve
- **Một nhịp chung, nhiều độ trễ.** Chuyển động chu kỳ (thở, nhún, lắc) điều khiển cả cơ thể bằng MỘT đường cong; mỗi bộ phận
  đi theo với độ trễ riêng. Nắn lại timing key từ ref thì các bộ phận đạt đỉnh lung tung (Idle_Front v8: F22..F40).

## easing
- Dùng sine (slow-in/slow-out mềm). Smootherstep có hai đầu phẳng quá lâu -> trông như dừng hẳn ("khựng"; Idle "hông lên tới đây
  thì đứng luôn... SlowIN"). Pha về (thở ra, hạ xuống) thường dài hơn pha lên.
- Key giữa pha về sát đáy -> "đập đáy" (đầu giật): để pha về là một đường S (chi tiết: SKILL.md Polish rules, Idle_Front).

## overlap
- **Overlap = trễ thời gian theo chuỗi dẫn -> bị kéo.** Thân: hông -> lưng -> ngực -> vai -> cổ -> đầu; tay: vai -> khuỷu ->
  cổ tay -> ngón; đạo cụ trễ sau phần cầm nó. Chỉ đổi thời điểm, KHÔNG đổi tư thế lấy mẫu (lấy mẫu tại độ trễ mới làm
  đầu đạt đỉnh trước ngực, tay nhấc 16 cm).
- **Overlap bằng resample trễ** (SDR Attack polish v1): curve local của bone con `fc.evaluate(f - delay)`: Chest/Neck 1F, Head 1,5F,
  tay trái 1→2F. Tay ném: delay = 0 tới frame thả dao (giữ đúng điểm thả), ramp vào ở follow-through, và chỉ 0,5/0,5/1F —
  1/1,5/2F làm khuỷu gập quá (da 0,07) ở pha về. Delay ramp về 0 ở 3 frame cuối để frame cuối = Idle tuyệt đối (kiểm pixel
  F1/F-last với bản trước).
- **Frame hiển thị, không phải key** (SDR polish v5): overlap delay của tay đối trọng cũng phải = 0 tới frame thả, nếu không key
  đúng mà frame hiển thị vẫn là pose trễ 1–2F (user nhận xét theo frame nhìn thấy, không theo key).

## lag-measure
- Đo độ trễ đúng đại lượng: phần xoay -> cực trị góc xoay trong không gian; phần tịnh tiến -> độ cao/vị trí.
  Đo độ cao của bộ phận xoay sẽ sai (ngực ưỡn làm thấp điểm đo).

## breakdowns
- SDR spline v1 (`sdr_attack.py ... spline`): breakdown = slerp giữa 2 key (`blend()`), deform Bezier auto-clamped. Prop có
  constraint: `props_weapons.md#thrown-prop`.

## all-keyed-loop
- Loop ngắn đã key mọi frame (SDR06 Shoot 12F, 4 phát): đổi CONSTANT -> Bezier không đổi gì ở 30 fps. Spline thật = dựng lại
  từ MỘT đường giật liên tục mỗi phát (lên gắt ~0,35F, về exp(-0,75t)·cos(0,6t): 1 / 0,39 / 0,08 / -0,02 = có chút quá đà rồi
  lắng), mỗi bộ phận lấy mẫu với độ trễ LẺ frame (súng 0, vai 0,4F, ngực 0,8F, đầu 1,6F), cộng các phát của vòng trước/sau
  để F13 = F1 tuyệt đối; chuẩn hoá từng bộ phận để đỉnh trên frame nguyên = blocking đã duyệt (giữ độ mạnh)
  (`work/sdr06/spline_shoot.py`). Súng + tay LINEAR (giật gắt), cột sống/cổ/đầu/scapula Bezier có key F0 = F12, F13 = F1.

## spacing
- Cú ném (SDR): tay đi ~1,1 m từ sau đầu tới điểm thả; dồn vào 1 frame (F5→F6) là "nhảy". Đặt F5 = 40% đường ném (tay qua đỉnh
  vai, cao nhất) → 55 cm + 76 cm, đọc được cung. Đo spacing bàn tay/dao từng frame (scratchpad arcs.py) trước khi gửi.
- Đường về nên tăng rồi giảm đều (5→12→21→27→23→14→7 cm/F), không dồn > 40 cm/F (SDR spline v2).
- ~70 cm duỗi tay cần ≥ 5 frame (đỉnh ≤ 16 cm/F) (SDR polish v4, "về quá nhanh trong 2 frame").

## split-timing
- Tách thời gian thân (TIMING) khỏi thời gian prop (KNIFE_FRAMES) để giãn thân mà dao vẫn thả F6 / cắm F12 (SDR spline v2).
- Tách thời gian riêng cho 1 chuỗi xương mà không đụng phần còn lại: dời key của riêng các curve Scapula/Shoulder/Elbow/Wrist_L
  (F11 → F14) sau khi key, trước overlap. Đo bước cổ tay trái từng frame (scratchpad larm.py) (SDR polish v4).

## secondary-cloth
- **Chi tiết phụ (vải, tóc, dây, đuôi):** con lắc giảm chấn, trục ở điểm đính (mép trên tấm vải, lấy từ vùng skin), mỗi chi
  tiết một chu kỳ riêng; gió = tổng vài sóng có chu kỳ chia hết độ dài loop (loop vẫn tròn). Người duyệt muốn vải "sống",
  dao động rõ (vạt khố ~25°, không phải 10°; "vải dao động nhiều hơn, kiểu bay trong gió").
- Trục xoay vạt khố ở khớp xương (giữa tấm vải) -> nửa trên/dưới ngược chiều -> trục ở mép thắt lưng (khớp xương FBX có thể
  không nằm ở điểm treo thật).
- "làm thêm anim cho các chi tiết phụ": vải/phụ kiện có xương phải được animate (kiểm kê bằng `rig_inventory.py`).

## loop
- Frame cuối = frame 1; playblast phát f1..f(N-1); bắt đầu loop ở điểm đứng yên (đáy) cho chỗ nối mượt.
- Sau khi đổi giá trị key luôn chạy lại `match_seam` (SKILL.md).

## end-on-idle
- Đuôi clip non-loop cho game (SDR Attack): user muốn **các frame cuối là pose Idle đứng yên** (F20–F26 = Idle, không nhích quá đà) —
  dev blend/transition sang Idle dễ hơn và có khoảng đệm cho code ngắt clip. Key Idle tại IDLE_FROM, giữ tới hết; mọi delay
  overlap ramp về 0 trước IDLE_FROM; prop hiện lại trong tay cùng lúc. Kiểm pixel F_IDLE_FROM..F_last == Idle.
