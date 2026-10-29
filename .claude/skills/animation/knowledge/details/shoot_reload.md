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
- Nỏ: `slingshot_0` con `Wrist_L` (tay trái mang nỏ), dây + tên trên `slingshot_1`: chốt z≈0, bật ra z≈+22 cm trong hệ nỏ.
- **Rig Studio làm mất xương phụ**: `rig.useFbx` chỉ giữ 25 xương thân (bỏ prop, tóc, root). Clip có prop/tóc trên rig team thì
  dựng bằng `sdr03/rigpose.py` trên khung xương FBX gốc; Pose Lab cần bộ chuyển FBX → model giữ đủ xương (chưa có, việc trước blocking).

- **Blocking Shoot b1 (2026-10-28, `sdr03/shoot_block.py`):** key = bảng (nỏ hếch/lùi, ngực cúi/xoay, đầu, tóc, dây). Nỏ = Δ·G0
  với Δ xoay quanh **điểm báng** + lùi theo nòng; hai cổ tay IK tới Δ·W0 nên bám nỏ (lệch ≤ 0,23 cm); đặt lại `slingshot_0` =
  Δ·G0 sau IK. Key có Δ = 0 (F1, F12) giữ nguyên tay P0 (IK giải lại lệch ~2 mm). Chọn chiều trục hếch một lần rồi dùng góc có
  dấu (bản đầu tự lật dấu → F7 "chúc −1°" thành hếch +1°). Xoay ngực 3° chỉ lùi vai phải ~1,8 cm: muốn vai lùi nhiều hơn phải
  dời bả vai, không tăng xoay ngực.
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

## Shoot and Reload share one P0 (2026-10-22)
- User: "Lấy F đầu tiên của Anim reload sang, vì trước đó chúng ta đã sửa lại Keypose" — when a key pose is hand-fixed in one clip (Reload F1 via Pose Lab), every clip that starts from that pose must take it over, or the in-game blend between clips pops (old Shoot P0 was 5 cm off at the gun, 9–12 cm at the left hand).
- Method (spline_shoot.py `Retarget`, data from `dump_reload_p0.py` → `work/shoot_die_repeat/sdr06/p0_reload_f1.json`): keep the recoil as a delta of the gun from the old P0 (`Gn = G0n @ G0o⁻¹ @ Gf`), scapulae as delta loc/rot on top of the new P0, arm locals = new P0, then IK both wrists to `Gn @ rel` (rel = new P0 wrist in gun space). IK must start from the new P0 arm (no twist), then scan every frame (seam, twist, slip, anatomy, gun_inside).

## Stepped prop-hand → spline (SDR06 Reload lspline_v1, 2026-10-22)
- Keys = first frame of every hold; drop the hold frames, Bezier AUTO_CLAMPED, quat_filter (`work/shoot_die_repeat/sdr06/spline_lhand.py`).
- Holds where only the prop turns in the hand (wrist + prop position unchanged, Pose Lab F17/F18/F22) are NOT path keys: otherwise the whole move lands in 1 frame (F22→F23 35 cm). Keep only the prop rotation key there.
- Hand + prop while the prop moves: arm keeps its local spline, prop rides in the hand (hand-space offset interpolated over all keys). IK of the hand onto a moving prop gave an elbow/wrist twist spike (F22 E 34°/W −25°). Prop still in the gun: IK hand onto the prop.
- End boundary 3 frames after the last key (F28 → F31), else the return to the base lands in 1 frame (17.8 cm).
