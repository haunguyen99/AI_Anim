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
  (`work/shoot_die_repeat/sdr06/spline_shoot.py`). Súng + tay LINEAR (giật gắt), cột sống/cổ/đầu/scapula Bezier có key F0 = F12, F13 = F1.

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

- **Bím tóc / dây treo trên clip one-shot ngắn (SDR03 Shoot s1 → s2, 2026-10-29, "đuôi tóc đang khá cứng chưa được tự nhiên"):**
  nội suy vài góc blocking cho từng đốt = cả bím vung như que. Làm lò xo tắt dần theo xung (frame giật): mỗi đốt trễ thêm ~0,4F,
  biên độ tăng dần xuống đuôi (sóng truyền dọc bím, bím uốn cong), lắc ngang 35% lệch pha, chút trễ ngược ở frame lấy đà; tổng góc
  đuôi đỉnh ~ bằng blocking đã duyệt; cửa sổ về 0 ở 2–3 frame cuối để frame cuối = P0 (`sdr03/shoot_spline.py` `hair_spring`).
  **→ s3 bị chê "cứng như lò xo":** chu kỳ 4,5F nảy qua lại đều đọc ra lò xo. Bím dài nặng là con lắc CHẬM (~50 cm → ~1,4 s =
  42F): trong clip ngắn nó chỉ kéo trễ một nhịp rồi trôi về, không nảy. Mô phỏng con lắc giảm chấn kích bằng chuyển động thật
  của gốc bím đo trên frame (`hair_drag`), ×3 cho đọc được, chia đốt có trễ 0,5F. Chu kỳ phải theo chiều dài thật của chi tiết.
  **→ s4, user: "Sao cứng vậy cho nó overlap manh lên chứ":** chia một góc cho các đốt + trễ cố định thì không có follow-through
  (tín hiệu gáy chỉ dài F3–F7, đốt trễ rơi vào lúc đã về). Overlap thật = CHUỖI: đốt j bám hướng đốt j−1 (lò xo nặng giảm chấn,
  `chain_sim`), góc local = hiệu hướng hai đốt; sóng chạy xuống đuôi, đuôi đi tiếp sau khi gốc dừng. Chỉnh chu kỳ đốt để đuôi
  xong nhịp trước 2–3 frame cuối (5F: tới đuôi F10–11 rồi bị ép về 0 = giật; 2,6F: đỉnh F7–8, tự về). Đuôi vung ~26 cm là vừa.
  **→ s5, user: "bạn chỉ làm có một khớp của tóc":** chuỗi lò xo hướng-đốt dồn 17° vào khớp gốc, khớp dưới bẻ ngược = cả bím
  xoay như que. Người xem đánh giá theo GÓC LOCAL từng khớp: mỗi khớp phải tự gập rõ (đỉnh 7–12°, gốc nhẹ ~3°), đỉnh lần lượt
  khớp sau trễ ~0,75F (`hair_wave`). Đo bảng gập local từng khớp mỗi frame trước khi gửi; chỉ skin vào khớp có đỉnh (khớp cuối
  của bím thường không có đỉnh mesh).
  **→ s6, user: "hãy nhớ đến bài tập anim quả bóng nảy có đuôi… các khớp bị kéo theo nhau":** đặt góc từng khớp bằng công thức
  (s2–s5) không ra cảm giác kéo. Cách đúng = **đuôi đi theo đường của đầu** (`rope_follow`): điểm j của chi tiết = dáng nghỉ
  (đầu mang) + G·(độ dời gốc lúc t − j·0,8F − độ dời gốc lúc t); xoay khớp j cho hướng đoạn HIỆN TẠI (sau khi cha đã xoay)
  khớp hướng đoạn mô phỏng (lấy độ lệch so với dáng nghỉ rồi cộng dồn qua cha = gấp đôi góc, đuôi văng 35 cm). G vừa với đoạn
  ngắn 10–14 cm là 2–3 (4–8 lệch 70–130°); làm mượt 1-2-1 một lượt theo thời gian. Verlet + lò xo về dáng nghỉ cho đoạn ngắn
  quay lung tung, bỏ.

## loop
- Frame cuối = frame 1; playblast phát f1..f(N-1); bắt đầu loop ở điểm đứng yên (đáy) cho chỗ nối mượt.
- Sau khi đổi giá trị key luôn chạy lại `match_seam` (SKILL.md).
- **Studio / playblast (2026-10-29, Ninja Idle, user: "loop bị giật"):** anim đúng (F41 = F1, tốc độ liền) nhưng nút Phát và `anim playblast`
  chạy F1..F41 → F41 rồi F1 cùng một pose = 1 frame khựng mỗi vòng. Đã sửa ở master Pose Lab (`% PER()`, playblast `n = PER()`) +
  `port_pose.py`. Khi user nói loop giật: đo nối trước, rồi kiểm số frame của video (`n` phải = frames − 1 với clip loop).
- **Tiếp tuyến chỗ nối (2026-11-05, RPG2 Hero Blade Idle trên Frolvy, user: "smooth frame đầu cuối để anim chuyển động mượt hơn … lưu lỗi này cho các anim loop là idle run walk"):**
  key F đầu = F cuối chưa đủ: tiếp tuyến tự động ở 2 key mút tính một phía nên tốc độ gãy ở chỗ nối (vd cổ tay tx cuối vòng 0,05 cm/F, đầu vòng 0,58 cm/F).
  Áp cho **mọi clip loop (idle, run, walk)**, xong mỗi lượt key: với mỗi kênh có >2 key, s = (v(F2) − v(F cuối−1)) / 2 (độ dốc qua chỗ nối),
  đặt cùng s (không gãy) cho cả key đầu và key cuối. Frolvy: `api.set_key_tangent(path, 0, s*fps, s*fps, False)` và tương tự ở frame cuối
  (đơn vị **mỗi giây**), kèm `set_infinity(path,'cycle','cycle')`. Kiểm: gia tốc tại chỗ nối |v1 − 2v0 + v_cuối−1| ≤ gia tốc lớn nhất giữa vòng.

## end-on-idle
- Đuôi clip non-loop cho game (SDR Attack): user muốn **các frame cuối là pose Idle đứng yên** (F20–F26 = Idle, không nhích quá đà) —
  dev blend/transition sang Idle dễ hơn và có khoảng đệm cho code ngắt clip. Key Idle tại IDLE_FROM, giữ tới hết; mọi delay
  overlap ramp về 0 trước IDLE_FROM; prop hiện lại trong tay cùng lúc. Kiểm pixel F_IDLE_FROM..F_last == Idle.


## breakdowns-procedural (2026-10-23, Gaygor Attack b75_v1, `work/boss_gaygor/gaygor_attack_50_blocking/breakdowns_v4.py`)
Breakdowns on a stepped blocking without changing its keys/timing:
- One per gap of >= 3 F (two in the longest gap); consecutive frames (F31-32-33) cannot take one.
- Per-bone slerp of the two neighbour keys with a favour weight t per gap + group offsets: LEAD (hip +.12, spine
  +.06, chest 0, arms -.04, head -.1, mace -.12, cloth -.2) when the body drives the prop; PULL when the heavy prop
  drives the body (lift, throw back); SETTLE in holds (only head/cloth lag).
- Prop blended in CHEST space -> it swings round the body (F50-55 lever arc instead of a straight chord). Exception:
  a prop lying on the floor at both keys is blended in WORLD space (in chest space it popped 14 cm up at F45).
- Hands gripping at both keys: grip blended in prop space, two-bone IK. Feet: planted at both keys -> leg IK lock;
  toe pinned -> ankle blended (pivots on the toe); moving -> lift arc 4t(1-t)*min(15, 0.25*dist) cm.
- Check (`check_v4.py`): elbow/knee angles inside the original keys' range +-5 deg, no bone taking a detour
  (A->BD + BD->B > 1.4x A->B), prop >= 0; arc plot of the prop head (`arc_plot.py`).

## heavy-prop-weight (2026-10-23, Gaygor Attack b75_v2, user: "Vũ khí đang chưa thể hiện được độ nặng")
Measure first (prop head speed per frame + hip height per key), name each spot, then fix breakdowns (keys stay):
- Lift from rest: LOAD first - body dips 4 cm and leans in while the prop barely moves (prop t 0.05), then the lift.
- Swing up from the floor: blend the prop in WORLD space with a small t (0.06 / 0.3) so it stays on the ground while
  the body rises, then accelerates into the next key (even 0.16 m/F spacing read weightless).
- After an impact the body keeps SINKING one frame (hip -3 cm) instead of rebounding at once.
- Picking it up from the floor: the head drags on the ground while the haft rises - blend normally, then turn the
  prop about the hands until its lowest point touches the floor (pinning the head to its old spot overstretched the
  arms: elbows 180 deg, because the whole prop also travels 0.3 m toward the body).
- Raising it: prop lags (t 0.25 / 0.6) and the chest leans back 4-6 deg against it.
- Back to the shoulder: balance at the top (1 deg/F), then fall faster and faster into the contact (5 -> 7 -> 12
  deg/F), body dips 3.5 cm on the catch, settle. A team key half-way down (64 deg) was moved back up (80 deg).
- Check: elbow/knee/wrist bend inside the original keys' range (`check_v4.py weight_v5`), plot `weight_plot.py`.
- Landing a heavy prop on the shoulder (b75_v3, `shoulder_v6.py`, user: "đoạn đặt lên vai lúc trở về đang bị nhẹ"):
  b75_v2 stopped dead at 49 deg then sank slowly to 41 (= placed, not dropped) and the shoulder rose after contact.
  Fix: fall accelerates INTO the contact (7 -> 12 -> 13 deg/F), contact frame turns PAST rest (36 vs 40 deg) with
  the shoulder pressed down (Scapula -8 deg), chest rolled to the prop side, hips at their lowest (-5 cm); next frame
  bounces back (42), then settles (40) while the body rises. Check the prop really touches: haft-to-Shoulder joint gap
  = the rest gap (6 cm); the first build pressed the shoulder with the haft still 22 cm above it.

## polish-bake-no-blender (2026-10-23, Gaygor Attack polish_v1, `work/boss_gaygor/gaygor_attack_50_blocking/polish_v1.py`)
- Spline: per-channel PCHIP (flat at peaks, no overshoot, zero end slopes) on sign-aligned local quaternions and
  translations through the keys; approved keys copied exactly; bake every frame.
- Constraints per frame on top of the spline: prop in chest space (world when on the floor at both segment ends),
  hand grip eased in prop space + arm IK, planted ankle / pinned toe locks + leg IK, soles >= floor, prop >= floor.
- Secondary (cloth, pendant): point-mass spring on the bone tip, near-critical (k 0.3-0.4, damping 0.38-0.48 per F),
  clamp the STATE at 15 deg, blend back to the pose over the last 6 F. First try (k .3, damping .18, clamp on the
  output only, 20 deg) swung to the limit after the impact and never settled.
- Every-frame QA (`check_polish.py`): joint angles inside the approved keys' range +-5, pops = speed > 12 deg/F and
  3x both neighbours (skip the smash frames), planted-foot slide, grip, floor. It found the free right hand dropping
  22 cm in one frame (a breakdown dragged the free arm with the body's t) -> give a free limb its own even t.
- Re-running an upstream script overwrites an APPROVED model: keep a flag that rebuilds it exactly and compare the
  sha256 with the published file (`B75_V3_APPROVED=1`).
- Playblast from the page without Blender: local sink `save_srv.py` (launch `pb-save`, 127.0.0.1:8124), page JS renders
  each view into a 2D canvas -> POST JPEG. Own cameras from the clip's bounds (the page presets cut a 3.4 m mace),
  fov 20. FILL the 2D canvas every frame (WebGL clear is transparent: frames piled up), capture in chunks of 17
  (one 68-frame call hit the 45 s tool limit). ffmpeg vp9 crf 34.
- polish_v2 (user: "lỗi ở f21"; first answer was "playblast nhầm bản" - the video WAS the right version: check
  in-between frames, not keys, when comparing versions). Spline exposes what stepped blocking hides:
  (1) a floor fix that turned neighbouring keys by different angles (F19 -4.7, F21 -11.2 deg) made a lying mace slide
  into F21 then stop dead - keep a resting prop's world pose identical across the hold; (2) a foot lift arc toward a
  key that is already the swing apex over-folded the knee 142 -> 87 deg in 2 F - arc only between two ground contacts.
  Scan per-frame speed of the prop and of the hip/knee around every reported frame before changing anything.
- polish_v3 (user: "pose 50 nhấc lên rồi nhưng pose 52 lại giật về trước đó"): the same lift-arc cause again (F52/F53,
  right foot stepping back from an already lifted F50): knee 128 -> 109 -> 149. RULE: a foot lift arc only between
  two ground contacts (`lift_arc="ground"`), and after any foot fix look at EVERY other breakdown with a moving foot.
  QA `check_polish.py` now lists "fold_backs": hinge turning points whose swing to both neighbouring turning points
  is > 10 deg within 6 F (catches F52; smooth one-cycle moves like the elbows F19-31 are not listed). Review each
  "giữa key" entry before sending; intended ones (impact compression, catch dip, stepping knee) stay.

## head-shake-jitter (2026-10-24, Gaygor Hit polish_v2, user: "phần đầu đang bị giật ở f13 đến f15. hãy check curves")
- A designed "shake the head clear" built as alternating 1-frame breakdowns (+6 / -3.5 / +6.5 deg yaw) = 10 deg/F direction
  flips = jitter, not a shake. A shake needs >= 3-4 F per swing and decaying amplitude: F12 0, +3, +5, +3, 0, -2, -3, -2, 0
  (<= 3 deg/F). Check the curve of the part named in a note before anything else.
- QA (`work/boss_gaygor/gaygor_hit/polish_check.py`): "jitter" = rotation direction reversing on 2+ consecutive frames with both steps
  > 3 deg (the speed-spike "pops" test cannot see it: same speed every frame); "sharp_turns" = a single fast reversal at the
  peak of a big move (snap/whip extremes, foot lift) - list them for the reviewer, usually intended.

## inertia-layer (2026-10-24, Gaygor Hit polish_v3, user: "Hai tay cùng với vũ khí đang khá cứng")
- Over-correcting a swinging arm ("tay khiên dao động mạnh" → arm locked to the chest) gives the opposite note: shoulder,
  elbow and wrist turned by the SAME angle every frame (one stiff piece) and froze relative to the chest after F14.
  Measure each joint relative to its parent, not only the hand's path.
- Fix without new keys (`work/boss_gaygor/gaygor_hit/polish_v3.py`): damped spring on the WORLD rotation toward the animated pose, per
  joint down the chain - shoulder (k .45, damping .42, <= 8 deg), elbow hinge-only (local Z part, <= 8), wrist (k .32,
  damping .38, <= 12), heavy prop about the gripping hand (k .35, damping .40, <= 8) with the arm re-IK'd onto it. Clamp the
  spring STATE, near-critical damping, blend back over the last 6 F. Result: own motion shoulder 8.5 / elbow 1-5 / wrist
  8-11 / mace +3 deg, settling, no jitter.
- A prop resting on a shoulder: never let the inertia bring it closer than the animated pose / rest gap (first try 6.0 cm
  vs 8.5) - keep the largest share of the spring that still clears it (bisection per frame).
- polish_v4 (user: "cổ tay đã mềm rồi. nhưng khuỷu tay với vai thì vẫn cứng"): the v3 springs were too stiff for the big
  joints (right elbow only +-5 deg, shoulders still after F7/F13). Big joints need SOFTER springs than the wrist, not stiffer:
  right shoulder k .28 damping .32 <= 14 deg, elbow hinge k .24 damping .30 <= 15, right scapula k .30 <= 5. For an arm whose
  hand is pinned to a prop, give the elbow its own life by a spring on its SWING about the shoulder->wrist axis (hand position
  and rotation kept): k .28 damping .32 <= 15 deg. Result: right shoulder lag up to 15 deg moving until ~F15, elbow 139-153,
  left shoulder up to 12 deg, no jitter. Always rebuild the layer from the pre-layer pose (v2), never stack springs on springs.
- polish_v5 (user on v4: "oki đấy giờ áp dụng với tay còn lại và chùy đi" - right-arm springs approved as the reference):
  for the arm whose hand holds the prop, the "wrist" softness IS the prop's spring (hand pinned to it): mace k .28 damping
  .32 <= 14 deg (= the approved right shoulder), left elbow swing k .24 damping .30 <= 15, left scapula like the right
  (re-IK the hand onto the haft after it). Spring set for this rig = these numbers (`work/boss_gaygor/gaygor_hit/polish_v5.py`; arms OK, but the mace was jerky -> see prop-path-smoothing).
- Clearance guard must use the PRE-layer pose as its floor: a lagging scapula moves the shoulder toward the prop before the
  prop's own spring runs (F2 gap 7.8 cm vs rest 8.5); clip the scapula lag per frame where it crowds the prop.

## prop-path-smoothing (2026-10-24, Gaygor Hit polish_v6, user: "Chùy đang khá là giật, nhất là đoạn cuối")
- Measure the prop's world angular speed per frame before touching anything: v5's mace went stop-go to the end (F15-F31:
  0.6 2.4 2.5 0.9 0.8 1.2 1.1 0.7 0.3 ...). Springs alone do not fix it, they add wobble on top.
- Causes: (1) 29/32 frames were keys (dense breakdowns), so the PCHIP spline smoothed nothing - motion steps like the keys;
  (2) the half-step stagger jolts the chest (2.9 cm/F then 0.6) and a prop parented in chest space copies every jolt.
- Fix: smooth the prop's WORLD path (grip point + sign-aligned quaternion) with fixed-end Laplacian smoothing (lambda .5,
  14 passes, eased in over 3 frames), keeping the hit frames (F1-F5) and the last frame (= Idle F1) exact; IK the gripping
  hand back onto it. Grip moves <= 8 cm. A heavy prop drifts through the body's small jolts instead of copying them.
- Clearance: do NOT clip back toward the old (jerky) pose per frame - the clip share changes every frame and makes new
  jolts (first try: bumps F19/F22). Instead PROJECT: push the prop about the grip, away from the shoulder, by the least
  angle that restores the floor, then light re-smooth (3 passes), repeat 5 rounds. Result: mace speed F7-F15 4.4 -> 0.35
  falling evenly, then a slow drift to the end; QA sharp turns of the mace only at F5 (the hit).
- Playblast: open the ROOT Pose Lab page (http://localhost:8771/index.html); pages/<clip>/index.html loads models by a
  relative path and renders an empty grid (first v6 capture was 32 empty frames - always look at one frame before ffmpeg).

## prop-overlap-weight (2026-10-24, Gaygor Hit polish_v7, user on v6: "chùy tôi nghĩ cần overlap nhiều hơn. để thể hiện được trọng lượng")
- A smooth path is not overlap. v6's mace decelerated so gently that a spring on it overshot only 0.4 deg. Overlap needs a
  target with the body's CLEAR STOP (here ~F13): follow the body-driven mace path (polish_v5 pose, lightly smoothed 3 passes,
  grip from the SAME source - mixing v6's grip with the body orientation put the target 15 deg into the shoulder).
- 2nd-order under-damped follower in world space, 8 sub-steps/frame: period 15 F, zeta .28 for this 3.4 m mace (period 10 /
  zeta .45 was too light). Result: lag 14 deg at the hit, overshoot 16 deg after the body stops (F14-F18), second swing 7 deg
  (F22-F26), rest on the shoulder from F28; smoothstep onto the pose over the last 8 F (F32 = Idle F1).
- Shoulder contact INSIDE the simulation as a soft pad (margin 2.5 cm, push k .08 rad/F^2 per cm, damping on the speed into
  the shoulder). Hard projection popped 25 deg in one frame; a post-pass push + re-smooth moved F2 by 11 deg and undid the
  overlap. With the pad no post push is needed (keep it only as a safety net, no re-smooth). `work/boss_gaygor/gaygor_hit/polish_v7.py`.

## poselab-physics (2026-10-24, Pose Lab vật lý giai đoạn 1, docs/poselab_physics_p1.md)
- The springs of Hit polish_v3..v7 are now a live layer on Pose Lab (thẻ Vật lý): joint / hinge / prop / elbow swing,
  presets Nhẹ/Vừa/Nặng/Rất nặng (period F, bounce = 1 - zeta, limit), Gaygor set = "Mức của nhân vật"; pinned frames
  (yellow lane), end ease, bake. Python twin `tools/physics_sim.py` (same steps; cross-check <= 0.02 deg).
- Contacts must be INELASTIC CONSTRAINTS, not soft pads: a depth-proportional pad on a mesh is chaotic (1e-6 -> 12 deg),
  hovers the prop on resting frames, and a stiff one rattles. Turn the prop out about the grip by the depth (weighted
  over all points inside, not the closest point - that switches vertex and kicks), kill the speed into the collider,
  64 sub-steps for props. Floor for props always on (min(0, key pose lowest)).
- Speed-graph flags: stop-go only WITHOUT a change of direction (a swing turning back is not stop-go); show only
  flags the physics adds (the key's own hit impulse is not its fault).

## body-collision (2026-10-25, Pose Lab vật lý giai đoạn 2, docs/poselab_physics_p2.md)
- Penetration = another segment's SURFACE points inside this segment's thin CORE (capsule, 40th pct radius of its own
  vertices). Capsule-vs-capsule or fat capsules flag contact as penetration (shield 10 cm "into" the knee, head 17 cm
  "into" the arm where the meshes only touch). Armor wraps a segment completely (shield: even the closest 5 % of the
  forearm's vertices are 17 cm out) -> take the mirror segment's radius when 30 % thicker. Scapula vertices belong to
  the torso. Depth relative to the Idle pose; hands holding the prop are not collisions.
- Eye-check every flag before trusting the tool (camera aimed at the midpoint of the two segments, with and without
  the shapes): of the approved clips, Attack F26-29 (shield through the face) and F58-60 (mace butt into the nape),
  Hit F12-13 (shield edge on the foot) are real; arm/head F45-51 and mace/collar on Walk are borderline.
- Springs avoid the body with the same inelastic contact as props, never deeper than the key pose; prune pairs whose
  bounds do not touch (reach = farthest surface point from the axis) or the cost goes 2-3x.

## balance (2026-10-25, Pose Lab vật lý giai đoạn 3, docs/poselab_physics_p3.md)
- "CoM inside the feet" alone flags every step; judge runs of frames with the capture point (CoM + v / sqrt(g/h))
  outside the support, ended by a landing (a foot or the prop that newly touches): caught = fine, missed = the new
  support does not hold the CoM, no landing for > 3 frames = "lean" (the CoM itself out) or "momentum" (only the capture
  point out). A heavy prop counts as mass (Gaygor 15 %) and, on the ground, as support. Ground = 5 cm (3 cm flagged a
  3-4 cm one-frame foot shuffle), painted contact lanes win over the height test.
- Gaygor is very stable: feet 76 cm front to back and a heavy pelvis; a 34 deg torso lean moves the CoM only ~8 cm.
  A real loss of balance needs hips back + lean back together. Hit's step back is acting, not physics.

## falls (2026-10-25, Pose Lab gói ngã/chết, docs/poselab_physics_p4_fall.md)
- A rigid body toppling about the foot edge: theta'' = g h / (h^2 + k^2) sin theta (Gaygor k = 0.3 m). Time to the
  floor depends mostly on the start tilt speed: standing still 28-43 F, knocked at 60-120 deg/s 13-20 F, collapsing
  straight down 9-12 F. So judge a fall against the clip's OWN start tilt and speed, never one fixed number.
- Pivot = the FEET support point farthest in the fall direction (a planted mace must not be the pivot); measure the
  lever and tilt in the fall plane, signed (sideways offset does not fall).
- The fall starts where the CoM starts going down without stopping (not F1, not the first "out" frame); it ends when a
  body segment (not feet, not the prop) is <= 2 cm from the floor.
- The usual fault is the "light" fall: even speed then ease-out before the impact. A real fall is fastest at the floor;
  flag last speed < 60 % of the peak, or landing >= 2 F away from the physics.
- Lying: body segments on the floor are support, so lying still is not "airborne". The floor is an obstacle for every
  spring part, never lower than the key, with a 15 % bounce (joints and props).

## impacts (2026-10-25, Pose Lab tác động bước 1, docs/poselab_physics_p5_impact.md)
- An impulse on a tree of rigid core capsules (free root): M qd = J^T j. Fully limp joints fling the hit segment
  (~10 m/s chest, hips still); blend 60 % with the joints-locked answer (same mass model, root dofs only) - both keep
  the total momentum j exactly.
- Level = what you see: the whole body's CoM speed (Gaygor ~1309 kg; a real punch ~20 N s moves it 0.015 m/s).
- Hips after a push = linear inverted pendulum, not a spring: the legs can only put the pressure point inside the feet
  (+8 cm hip strategy). A spring on the hips swallowed a 5 m/s push and never stepped. CoM speed = j/M exactly; the
  root turns about the CoM.
- Step only for what the hit ADDS over the key's own capture point (Hit steps back by itself). Pick the foot by
  predicting where the capture point will be when it lands (only the other foot pushes: it runs away as e^(w t));
  lifting the loaded foot of a wide staggered stance tipped the body over. Needed step > 2 x max (1.6 m) = a fall.
- Cap each joint's START speed so the swing peaks at its limit; capping the angle held a whipped head stuck at 30 deg.

## ragdoll-xpbd (2026-10-25, Pose Lab ragdoll, docs/poselab_physics_p5_impact.md section 12)
- XPBD: every ONE-SIDED constraint (floor, body contact, joint limit) needs its own velocity step - the separating speed
  after the push may not exceed the one before. Without it a limp body on the floor pumped itself 1.45 m up.
- Energy that GROWS with more sub-steps = something injects per sub-step (here: limit pushes turned into spin).
- Free fall from a height with no contacts isolates joints / limits: total energy must never rise.
- Bend / spread / twist limits are singular near 180 deg from rest: unwrap in time, and re-centre a joint that starts
  far from rest (team blockings can hold a 180 deg arm twist).
- Never weld a 170 kg prop to a 19 kg hand: merge it into the hand body; split on release keeping the speeds.
- A limp body on joint limits chatters for seconds: damp joints on their limit, rolling resistance on the floor, sleep
  (< 2.5 cm/F for 6 F). Gaygor then settles 0.6-1.2 s after landing.
- Mirror the page's math in Python with the same three.js formulas (quaternion multiply, applyQuaternion, Matrix3
  inverse) on plain floats: the twin matched to 0.00000 cm through contacts; changing 20 -> 19 sub-steps moved 43 cm.
- Gaygor's real radius of gyration with the mace is 0.61 m (the fall pack assumes 0.3 m).

## active-ragdoll-balance (2026-10-25, Pose Lab ragdoll step 3)
- Support for a ragdoll's balance = all sole points within 2 cm of the floor; the points pushed out of the floor in one
  sub-step (1-3) made the feet a dot and a still body read 30-40 cm "outside".
- Hold the hips toward the key only while the capture point is inside the feet (+ 8 cm hip strategy), capped by the
  feet's friction (mu g); outside, nothing holds it - that IS the fall. Report "needs a step" only if a fall follows.
- Gaygor (Idle stance) recovers from a 0.3 m/s push any side and 1 m/s sideways; 1 m/s backward needs a step (same as
  the step-1 pendulum).
- Reflex poses come from the key animation: arms at >= 60 % strength stay within 5 deg of the key while the body falls.

## ragdoll-goal
Muốn cú ngã vật lý kết thúc đúng pose người dùng đặt (2 key: Idle + nằm): dùng Ragdoll "Về đích" trên Pose Lab (`docs/poselab_physics_p5_impact.md#17`).
Mặc định **chỉ dáng**: chỉ khớp dáng, hông nằm chỗ cú đánh đưa tới; không bớt lực tác động / cú đẩy để về đúng chỗ key cuối (người dùng duyệt 2026-10-26).
- **Chỗ nằm:** cú đẩy ban đầu dò theo phần lệch đo được. Đừng chỉ dò từng bước nhỏ: cú ngã rất nhạy, dễ kẹt ở cú ngã sấp.
- **Dáng tay chân:** cơ kéo về pose cuối sau khi chạm sàn. Mục tiêu phải đi dần (≤ 4°/F), đổi ngay thì bàn chân bị quất.
- **Phần còn dư:** trộn ở 10 frame cuối, lifted khỏi sàn. Prop là xương riêng, phải nâng riêng.

## spacing-frolvy-idle-wipe (2026-11-02, G-LumberCity Idle Wipe spline)
- Đo tốc độ cổ tay mọi frame sau khi đổi sang spline. Breakdown đặt ở 57% quãng đường sau 4/12 frame → tay vọt khỏi hold (1,8 → 9,3 → 16,3 cm/F). Sửa đúng = dời FRAME breakdown theo đường ease in/out (72→74, 76→77), không chèn key phụ (key F70 thêm vào làm F70→71 vọt 20,6).
- Cú vẩy dừng phắt (15,7 → 4 cm/F): thêm key vung tiếp 1 frame sau; nếu đi thẳng tiếp thì tay duỗi thẳng (vượt tầm với) → cho đà vòng ra SAU hông (3 cm dọc + 7 cm sau): 14,6 → 8 → 3,4, khuỷu 33°.
- Breakdown nội suy dễ đẩy tay ra xa thân nhất (F92 x −44): kiểm khoảng cách cổ tay–thân + góc khuỷu ở mọi inbetween của động tác nhanh.
- **Về lại idle gốc không khựng (Idle Wipe polish v2, user 2026-11-02: "đoạn chuyển đổi giữa hành động lau mồ hôi và idle gốc ở cuối chưa được mượt. đang có một đoạn khựng"):** đừng key dáng idle TĨNH chờ tới chỗ idle gốc chạy lại (F99–F108 cùng 1 dáng → đứng chết 8 frame rồi vọt ở F112). Idle gốc lặp N frame thì các frame trước chỗ nối chính là idle gốc lùi N → key thẳng idle đang thở, và hoà động tác vào đó: tay đang có đà dùng ease-out (1−(1−t)²) để nối tốc độ, thân/tay kia smoothstep dài (~14 F). Đo "tổng chuyển động thân mỗi frame" so với mức thở idle.

## overlap-prop-flap (2026-11-03, G-LumberCity Clean Output)
- Sổ trễ (flap ngược chiều quét) phải NHỎ hơn quãng cẳng tay đi trong breakdown: flap −15…−18° ăn hết quãng → sổ đứng 5 F rồi bật (director b50 A). Dùng −4…−8°, BD ở 30–65% cung, phẩy qua đỉnh +8…+11° (20° làm cổ tay lệch 30°). Đo yaw đạo cụ nhìn từ top mọi frame: đổi ≥ ~6° mỗi BD, ≤ ~17°/F.
- Dời key cho nhịp vào sớm có thể tạo cú "đập" ở đáy nhịp trước (sổ 5 → 8 → 2 cm/F): đặt lại 2 frame trước đáy theo 45% / 80% quãng + tiếp tuyến phẳng ở đáy (`set_key_tangent(path, f, 0, 0, False)`).
- Đầu dừng gắt có thể do thân (lưng/ngực có key BD sát nhau 41/42), không phải key đầu: đo vận tốc từng control trước khi sửa.
- Loop Frolvy: key ngoài khoảng xuất F0 = F(N−1), F(N+1) = F2, F(N+2) = F3 (mở range bằng `range_fbx.py`) để tiếp tuyến hai đầu khớp.
