# Shoot / Reload súng (SDR map06: gangster + Tommy gun, ref Mafia DE từ sau lưng, game side-scroller), 2026-10-21
Bài học chung đã chuyển: súng thẳng ở top → `props_weapons.md#gun-aim`; súng quá khổ → `props_weapons.md#oversized-prop`;
xuyên thân mọi key / không đổi bằng tay căng → `props_weapons.md#prop-penetration`; cầm trống → `props_weapons.md#grip-drum`;
trống xoay theo thân → `props_weapons.md#flat-prop-orient`; mở người + đầu ra cam → `torso_head.md#open-to-camera`, `#head`;
chest_roll trục world → `torso_head.md#world-axis-roll`; sửa hông giữ thân trên → `torso_head.md#partial-fix-hip`; vai lõm/vai
xoắn → `arms_hands.md#shoulder-compression`; spline tay IK, review từ phía tay thay đạn, FK → `arms_hands.md#spline-ik-arms`,
`#prop-hand-side-fk`; action slot → `blender_tools.md#action-slot`; ngưỡng da áo khoác → `arms_hands.md#shoulder-compression`.

## crossbow-map3
SDR03 (map3, nỏ, 2026-10-28; `work/shoot_die_repeat/sdr03/`):
- **Đọc file anim có sẵn của team trước** (`Assets/_Game/Animations/<Map>/*_shoot.fbx`): nó cho cách cầm prop, vị trí dây/chốt,
  nhịp của team. P0 v1 lấy F0 của nó (báng tì vai, ngực mở 68° ra cam, nỏ ngang yaw 0). Ghi rõ là lấy từ file team.
- Nỏ: `slingshot_0` con `Wrist_L` (tay trái mang nỏ), mũi tên (mesh `_bow`) trên `slingshot_1`; dây nằm trong mesh `_crossbow`:
  8 đỉnh giữa trên `slingshot_1`, hai đầu trên cánh cung (`slingshot_0`). Chốt z≈0; **dây thẳng (nghỉ) ở z≈+26,4, y +2,6 cm**
  trong hệ nỏ (đo trên mesh, b6), không phải +22 (số đọc từ file team làm giữa dây còn gập chữ V, ghi chú b5 "dây cung ở
  trạng thái nghỉ chưa được thẳng"). Đo bằng mesh: giữa dây (đỉnh `slingshot_1`) phải trùng đường nối đầu hai cánh.
- **Rig Studio làm mất xương phụ**: `rig.useFbx` chỉ giữ 25 xương thân (bỏ prop, tóc, root). Clip có prop/tóc trên rig team thì
  dựng bằng `sdr03/rigpose.py` trên khung xương FBX gốc; Pose Lab cần bộ chuyển FBX → model giữ đủ xương (chưa có, việc trước blocking).

- **Blocking Shoot b1 (2026-10-28, `sdr03/shoot_block.py`):** key = bảng (nỏ hếch/lùi, ngực cúi/xoay, đầu, tóc, dây). Nỏ = Δ·G0
  với Δ xoay quanh **điểm báng** + lùi theo nòng; hai cổ tay IK tới Δ·W0 nên bám nỏ (lệch ≤ 0,23 cm); đặt lại `slingshot_0` =
  Δ·G0 sau IK. Key có Δ = 0 (F1, F12) giữ nguyên tay P0 (IK giải lại lệch ~2 mm). Chọn chiều trục hếch một lần rồi dùng góc có
  dấu (bản đầu tự lật dấu → F7 "chúc −1°" thành hếch +1°). Xoay ngực 3° chỉ lùi vai phải ~1,8 cm: muốn vai lùi nhiều hơn phải
  dời bả vai, không tăng xoay ngực.
- **b1 bị làm lại (2026-10-29, user: "Chốt f1. hãy blocking lại các frame khác"):** biên độ theo analysis (nỏ 6°, lùi 3,5 cm,
  ngực 3,5°) ở cam game ngang trông như MỘT pose, không đọc ra lực. Blocking phải đọc được ở thumbnail cam game: b2 nỏ hếch
  12°, lùi 7 cm, ngực ngả 6° (dưới mức 12° bị chê "giật về sau hơi nhiều"), bả vai phải dời lùi theo báng, thêm key lắng F9
  (stepped F7→F12 đứng rồi bật). Số trong analysis là sàn, không phải trần: kiểm sheet key ở cam game, F2–F12 phải khác nhau
  rõ bằng mắt. Kiểm báng/đầu: khoảng đầu–nỏ mọi key ≥ khoảng ở P0 đã duyệt (b2: 2,7–3,5 cm, P0 3,2).
- **`rigpose.ik_arm` lật khớp tay 180° (b2, review F2/F7 "xoắn vặn", F4/F6 "sao lỗi này gặp nhiều thế", "lại lỗi này"):**
  nó dựng lại tay từ đầu, đoán trục khuỷu = Z local và chọn chiều xoắn theo sai số nhỏ nhất, nên chọn nghiệm lật (vai/cổ tay
  trái 180°, khuỷu phải 130° lật vào hông) dù cổ tay vẫn tới đích. Khi prop chỉ dời vài cm quanh pose đã duyệt, dùng IK ít đổi
  nhất `shoot_block.ik_min`: gập khuỷu quanh CHÍNH trục gập hiện tại (pháp tuyến vai–khuỷu–cổ tay), vai xoay `rot_between`
  góc nhỏ nhất, cổ tay lấy hướng đích. **Quét trước khi gửi:** góc xoay local của Shoulder/Elbow/Wrist mỗi key so với P0;
  > 45° ở key dời nhỏ là lật khớp (b2: 157–180°, b3: ≤ 17°). Lỗi lặp lại nhiều lần vì trước đó chỉ đo vị trí cổ tay, không đo xoay.
- **Nỏ/súng vác vai: GD muốn giật LÙI, không hếch (b3 → b4, 2026-10-29, "GD không muốn vũ khí giật lên trên quá nhiều.
  thay vào đó là đẩy về sau nhiều hơn"):** đỉnh dư chấn hếch ≤ 4°, lùi theo nòng ~10 cm, bả vai bên báng lùi gần bằng nòng
  (8 cm) để báng không lún vào vai. Mặc định cho vũ khí tì vai lần sau: lực đi dọc nòng ra sau, hếch chỉ phụ.
- **Dây nỏ phải rung sau khi bắn (b4 → b5, ghi chú F5 "Phần dây cung đang hơi tĩnh"):** dây bật ra rồi đứng im đọc ra là chết
  ngay từ blocking. Cho `slingshot_1` vượt điểm nghỉ ~5 cm ở frame bắn rồi tắt dần dấu đổi mỗi key (−4/+3/−1,5/+1/−0,4 cm dọc
  nòng, ±1,5 cm lên xuống), xong trước frame cuối. Vật thể phụ (Studio `props`) theo phiên bản: bản mới chép
  `work/store/<ns>/props/<clip>-<ver cũ>.json` sang tên mới, nếu không bản mới mất mũi tên/hình nộm.
- **Spline s1 (2026-10-29, `sdr03/shoot_spline.py`, từ b6 đã duyệt):** dựng lại từ BẢNG THÔNG SỐ key (không nội suy xoay
  từng khớp): mỗi cột = monotone cubic qua key (không vượt), mỗi bộ phận lấy mẫu trễ (ngực 0,5F, đầu 1,6F, tóc 2,2F, về 0 ở 3F
  cuối), rồi `make_key` + IK ít đổi nhất ở MỌI frame nên tay bám nỏ ≤ 0,02 cm. **Bả vai bên báng không được trễ** (bị báng
  đẩy: trễ 0,4F làm báng lún vai ở frame bắn). Quét mọi frame bằng scratchpad scan (lật khớp so P0, bước/F, trượt tay,
  đầu–nỏ, tay–thân, báng–vai) so với blocking đã duyệt.
- **Polish p1 (2026-10-29, từ s6 đã duyệt):** găng map3 là bao tay liền, chỉ `MiddleFinger1_*` có đỉnh (MF2 không), trục gập
  = local y (trục găng gập sẵn ở P0; xác định bằng cross(cổ tay→MF1, MF1→MF2) trong hệ MF1). Bóp cò 8° (12° lấn báng thêm
  0,3 cm), găng trái siết 8° khi giật; nỏ rung xoay quanh nòng (`make_key` spec[8], áp trước Δ để tay IK bám theo). Ở cam game
  găng gần như không đọc được: đừng tốn vòng chỉnh ngón trên rig găng. Tên phiên bản s/p so chuỗi sai ("p1" < "s2"): dùng
  `shoot_spline.level()`.
- **Reload b1 (2026-10-29, `sdr03/reload_block.py`):** đo tầm với trước khi dựng: vai phải → giữa dây nghỉ 66 cm, tay 47 cm (+ găng 13):
  phải có bả vai tiến (~7 cm) + ngực xoay 4°. Tay phải lấy local Scapula/Shoulder/Elbow/Wrist/găng từ frame file team (cùng khung
  xương nên khuỷu đúng hướng, không lật), rồi `ik_min` chỉnh nhỏ tới điểm nắm (dây của mình cao/xa hơn team ~4 cm). Lúc kéo: đặt
  dây theo tỉ lệ u (nghỉ → chốt), cổ tay = dây + offset tay–dây đo trên team (nắm/chốt). Kiểm ở top: dây gập chữ V theo găng.
- **Reload b2 (2026-10-29, ghi chú b1 F1/F12 "mũi tên đang ẩn / bật trở lại", F30 "dây bị kéo xuống thấp quá"):** mesh tên trên
  `slingshot_1` luôn hiện, nên trong Studio làm tên thành vật thể phụ (`props`, src = mesh tên, `hideSrc`) gắn `slingshot_0` ở chỗ
  trên rãnh của P0, key ẩn F1 → hiện ở `cocked`. Dây ở chốt cũng thấp 2,55 cm như lúc nghỉ: nâng cả ở chốt (giữa dây ngang đường
  hai đầu cánh), tên gắn thân nỏ nên không bị nâng theo.
- **Reload spline s1 (2026-10-29, `sdr03/reload_spline.py`):** tay theo đường file team = cột `tf` (frame team, số thực) nội suy
  slerp local giữa hai frame team, rồi `ik_min`; cột `g` trộn đích đường team ↔ đích bám dây. Đo spacing cổ tay cm/F: file team
  đứng yên F1–F6 nên key gần đầu phải trỏ tf = 6, không 0 (s1 đầu: F4 phí, F4→F5 nhảy 14 cm; F7→F8 18 cm/42°). Khuỷu gần duỗi
  (với 0,97) đổi 30° khi dây kéo 6 cm là hình học bình thường, không phải lật.
- **Reload polish p1 (2026-10-29):** găng bám dây bằng cách giữ VECTOR găng→giữa dây (hệ nỏ) bằng lúc nắm, dời đích cổ tay rồi
  `ik_min` lại 2 vòng (trôi 1 cm → 0). Găng phải: mở −10…−12° khi với và khi dây vào chốt, siết vượt khi về báng; găng trái siết
  ~7° khi kéo; nỏ rung quanh nòng khi dây vào chốt (±0,8° tắt dần). `studio_cmd anim version` báo "Không có phiên bản" khi
  trang chưa tải lại danh sách: `open <nhân vật> pose` rồi `anim clip`, `anim version`.
- **Mặt nhìn thẳng (2026-10-29, ghi chú Reload F1 "Cho nhân vật ngẩng đầu lên, để mặt nhìn thẳng về phía trước", rồi "Sửa cả
  Shoot"):** P0 cúi đầu 7° + cổ 3° để ngắm dọc nỏ đọc ra là cúi gằm ở cam game ngang. Mặt đo bằng trục local nhìn +Z ở rest:
  P0 cúi 7,3°, quay về cam 42°. Bỏ phần cúi gốc ở MỌI frame của cả hai clip (`reload_spline.lift_head`, `shoot_head_lift.py`),
  giữ quay về cam và các cử động tương đối; sửa cả hai clip nối nhau để F cuối Shoot = F1 Reload (lệch 0).
- **Đầu không ngửa khi giật (SDR05 Shoot b6, 2026-11-03, note "GD muốn đầu luôn hướng về phía trước không bật ngửa ra sau"):**
  GD không muốn đầu khựng ngửa (b4: đầu 3° + ngực 5° + lưng 1,5° dồn lên đầu → ngửa 8° ở đỉnh). Mặc định cho súng ngắn 2 tay:
  hướng đầu world khoá đúng P0 mọi frame, ngực/vai/tay vẫn giật; phần bù chia đôi cổ/đầu (≤3,2° mỗi khớp).
  `sdr05_colt/shoot_block.py --base b4 --head-lock`; đo `head_dev_deg` = 0 mọi key.
- **Spline súng cầm 2 tay (SDR05 Shoot s2, 2026-11-03, Director duyệt; s1 bị trả):** dựng như SDR03 (bảng thông số → monotone
  cubic, `sdr05_colt/shoot_spline.py`) nhưng: (1) **không trễ ngực trong pha giật** (F1 → đỉnh): ngực trễ 0,5F làm vai lùi thiếu,
  phần lùi dồn vào khuỷu R (+4–7° so blocking, lỗi A); trễ chỉ ở pha hồi. (2) Sàn khuỷu R = đường cong khuỷu của các key blocking,
  không kẹp ở P0 (kẹp → khuỷu về hết trong 1F); nếu thấp hơn sàn thì cho súng lùi theo thân. (3) Hếch nòng quanh hướng nòng
  P0, không quanh +Z tuyệt đối (P0 lệch ngang chút → súng lệch 0,2 cm cả pha hồi rồi giật về ở F cuối). (4) Bộ giải tay đỡ
  cho khuỷu khác P0 vài độ ở frame gần P0 → cho tay đỡ lắng dần về P0 (smoothstep 3 frame cuối) rồi chỉnh khuỷu theo bản lề
  + xoay vai để nắm tay bám súng 0 cm. Kiểm: bước súng cuối ≤ bước trước, mọi khớp ở F cuối−1 → F cuối đổi ≤ bước trước.
- **Polish súng 2 tay (SDR05 Shoot p1, 2026-11-03, Director duyệt lượt đầu):** thêm lớp trọng lượng dưới, không chạm chuỗi giật:
  hông hạ ~1,2 cm đỉnh trễ 1F sau vai (gối hấp thụ), hai chân giải lại (gối xoay quanh pháp tuyến hông–gối–cổ chân cho đúng độ
  dài, xoay hông tới cổ chân P0, khoá hướng cổ chân P0) → trượt 0; đích súng hạ theo hông. Pha vượt (tay không giải lại):
  KHÔNG giải lại cả tay để ghim súng (tay gần thẳng → vai xê vài mm làm khuỷu tụt 8°); thay vào đó xoay Shoulder_R (khuỷu
  giữ nguyên) cho độ cao súng = P0 − hông hạ, rồi chỉnh nòng bằng cổ tay. Găng liền map5: siết MiddleFinger1 quanh local y
  6° (R) / 5° trễ 1F (L): không xuyên nhưng gần như không đọc ở cam game. `shoot_spline.py --ver p1`, `shoot_block.fix_leg`.
- **Dây ở chốt cũng nâng ở Shoot p3 (2026-10-29, "sửa cả dây cung cho anim shoot" → "sửa vậy được rồi"):** mũi tên cùng xương
  `slingshot_1` với giữa dây nên trong FBX tên cao theo 2,55 cm ở F1–2 Shoot / F20–30 Reload; user chấp nhận. Studio dùng vật thể phụ.
- Bản mới đăng bằng `clip_registry.py pose-version` chưa có `work/store/<ns>/anims/<clip>-<ver>.json` nên Studio mở ở spline:
  chép file của bản trước (đổi `version`) để giữ `interp: step`, rồi `studio_cmd.py anim clip <id>` cho trang tải lại.
- Model Pose Lab cho rig team: `sdr03/poselab_model.py` (đủ xương + texture); khớp thêm của clip qua `clip_registry.py
  pose-version --names "slingshot_1=Dây nỏ,joint1_M=Bím tóc 1,…"`.

## trigger-hand
- **Reload: tay cầm cò không rời cán** (review Reload b3 F30: "giữ tay này ở đây, không bỏ ra để gạt như F36"). Kéo khóa nòng
  bằng tay kia (tay trái vươn lên nóc hộp khóa). Tay cầm cò rời cán thì đọc ra là sai tư thế cầm súng.

## reload-minimal
- **Người duyệt muốn reload gọn:** bỏ kéo khóa nòng, lắp trống xong là về luôn (54F còn 42F).
- Reload súng cho game side-scroller: người duyệt bỏ pha dựng súng cao 32–44° (lấy từ ref phim) sau 6 vòng sửa xuyên đầu/bắp
  tay/căng tay. Cái họ cần: tay phải giữ súng gần P0, chỉ nhấc 3–5 cm và ngóc 8–12° (nhịp "nhấp"), tay trái tháo/lắp băng đạn ở
  ngay dưới súng. Trước khi chép động tác ref điện ảnh, hỏi/đề xuất bản tối giản đọc được ở góc cam game; ít đổi tư thế = ít lỗi xuyên.

## gun-bone-scale
- Xương súng `slingshot_*` có scale 0,01 (FBX cm): đo "tay lệch khỏi súng" trong không gian local của súng ra số to gấp 100.
  Luôn đo ở world: `G(f) @ rel(key) - wrist(f)`. Shoot spline v1: tay lệch ≤ 1 mm cả ở subframe (con số 4 cm ban đầu là sai đơn vị).

## new-gun-fbx (SDR05 Colt, 2026-11-04)
- Đổi súng (Gatling → Colt) mà team chưa có rig mới: xuất FBX = **file rig team** (mesh + rig + anim, Unity Humanoid), không dựng FBX từ đầu.
  Dùng lại xương + cluster của súng cũ (joint1/3/5_M → `slingshot_0/1/2`: đổi tên, cha, Lcl, PoseNode, Transform/TransformLink),
  thay hình mesh súng cũ nhưng **giữ tên mesh** (prefab không mất tham chiếu), bỏ mesh thừa bằng `tools/fbx_remove_mesh.py`.
  Script mẫu: `work/shoot_die_repeat/sdr05_colt/export_fbx.py` (bước rig + bước anim như sdr03, kiểm local từng xương + đỉnh súng skin so với rig Studio = 0).
- Ma trận trong FBX (PoseNode Matrix, Cluster Transform/TransformLink) lưu **theo cột**: `M.T.reshape(-1)`. Lcl của xương trong file anim team = frame đầu, không phải bind.
- Vật thể phụ chỉ dùng ở clip khác (băng đạn tay trái của Reload) phải **ẩn ở các clip còn lại** (scale xương 0,001): render FBX góc trước thấy nó lòi khỏi găng,
  sheet side_r không thấy. Kiểm FBX bằng `rigpose.Rig(fbx)` + `fbxanim.local` render cả góc trước, không chỉ cam game.
- Đổi tên/cha xương làm đổi đường dẫn trong `transformMask` của `.meta` Unity: báo dev cập nhật mask (Upper Layer) khi thay clip.

## reload-revolver-side-cam (SDR05 Colt Reload b1→b3, 2026-11-04)
- Tay chibi ngắn: ĐO tầm với trước khi giữ chữ "tay phải duỗi suốt clip" (vai trái → ổ 65 cm > tay 54 cm). Phần thiếu lấy từ thân xoay đưa vai trái lên 15–18° + súng thu ≤ 8 cm (khuỷu R ≤ 25–35°), không kéo súng về ngực (khuỷu 80° bị Director A).
- Cuộn súng 70° = 3/4 xoắn cánh tay + 1/4 xoắn cẳng tay (≤ 20°), cổ tay giữ như P0; cuộn bằng cổ tay ra gập 110°.
- Cam nhìn ngang: mọi việc của tay trái phải nằm DƯỚI hoặc PHÍA CAM của súng. Ổ Colt mở sang trái (xa cam) → ở pha nạp cuộn súng +50° cho ổ thòng xuống dưới súng, tay trái lên từ dưới cẳng tay phải. Băng cầm ló 7 cm trước nắm tay (ở tâm nắm tay thì bị găng che).
- Ổ mở trên cần đỡ: trục quay song song nòng nhưng DƯỚI ổ (cần đẩy vỏ đồng trục ổ, quay quanh nó ổ chỉ tự xoay tại chỗ).
- Lấy đồ "sau lưng" ở cam ngang: chọn điểm túi theo hướng màn hình (−Z của cam, không phải hướng lưng của hông đang xoay 48°), tay ló ra 10 cm, thân xoay ngược 10°; thử nhiều điểm bằng ảnh side_r + back (reload_probe_back.py). Hướng lưng thật của hông = phía xa cam → tay khuất 5 F (Director A hai lượt).
- Hướng "vặn trái/phải" súng: luôn nói theo NHÂN VẬT (đỉnh súng nghiêng sang tay trái/phải của nhân vật) và ĐO dấu bằng số (đỉnh súng · trái-nhân-vật) trước khi báo; b4 ghi "vặn trái" mà thực tế đỉnh súng sang phải (đảo dấu ở hàm đo), user phát hiện. Khi user nói hướng, gửi ảnh A/B (cam game + sau lưng + trên) cho chọn.
- Spline tay đi xa (lấy đồ sau lưng → đưa lên súng, 1 s clip): dựng lại đoạn theo ĐỘ DÀI CUNG (Catmull-Rom qua điểm key) với bước/F cho trước (vd 25/25/24/18/10), không nội suy từng trục qua key (s1: vọt 38 cm/F rồi đập 5 cm/F). Đo lh_step mỗi F (≤ 30, giảm ≤ ×2,5/F), găng ↔ quần/thắt lưng ≥ 3 cm (mesh Items, không phải body), khớp tay ≤ ~45°/F; tay có lịch riêng, không dừng theo nhịp dừng của súng (sdr05_colt/reload_spline.py, reload_check.py).
- joint_rules đo gập khuỷu so rest pose của FILE TEAM (rig map5: khuỷu gập sẵn ~94°) → cờ "Elbow gập âm ngoài giới hạn" là báo nhầm khi khuỷu hình học vẫn gập dương; kiểm bằng góc hình học.

## Shoot and Reload share one P0 (2026-10-22)
- User: "Lấy F đầu tiên của Anim reload sang, vì trước đó chúng ta đã sửa lại Keypose" — when a key pose is hand-fixed in one clip (Reload F1 via Pose Lab), every clip that starts from that pose must take it over, or the in-game blend between clips pops (old Shoot P0 was 5 cm off at the gun, 9–12 cm at the left hand).
- Method (spline_shoot.py `Retarget`, data from `dump_reload_p0.py` → `work/shoot_die_repeat/sdr06/p0_reload_f1.json`): keep the recoil as a delta of the gun from the old P0 (`Gn = G0n @ G0o⁻¹ @ Gf`), scapulae as delta loc/rot on top of the new P0, arm locals = new P0, then IK both wrists to `Gn @ rel` (rel = new P0 wrist in gun space). IK must start from the new P0 arm (no twist), then scan every frame (seam, twist, slip, anatomy, gun_inside).

## Stepped prop-hand → spline (SDR06 Reload lspline_v1, 2026-10-22)
- Keys = first frame of every hold; drop the hold frames, Bezier AUTO_CLAMPED, quat_filter (`work/shoot_die_repeat/sdr06/spline_lhand.py`).
- Holds where only the prop turns in the hand (wrist + prop position unchanged, Pose Lab F17/F18/F22) are NOT path keys: otherwise the whole move lands in 1 frame (F22→F23 35 cm). Keep only the prop rotation key there.
- Hand + prop while the prop moves: arm keeps its local spline, prop rides in the hand (hand-space offset interpolated over all keys). IK of the hand onto a moving prop gave an elbow/wrist twist spike (F22 E 34°/W −25°). Prop still in the gun: IK hand onto the prop.
- End boundary 3 frames after the last key (F28 → F31), else the return to the base lands in 1 frame (17.8 cm).
