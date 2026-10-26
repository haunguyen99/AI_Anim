# Cascadeur (MCP `cascadeur`, từ Gaygor Attack P0, 2026-10-21)
Số liệu key cụ thể của Gaygor Attack trong Cascadeur: `attack.md#cascadeur-keys`.

## pipeline
- Pipeline đã chạy: FBX gốc `import_model` → `rig_mode.on.run_raw` → Quick Rig bằng template `.qrigcasc` (tên AdvancedSkeleton,
  `work/cascadeur/make_qrig_template.py`) + AutoPosing → `rig_mode.off.run`. Chùy/`Weapon` không có controller: key trực tiếp
  Position/Rotation của joint (`casc_pose.set_joint_local`).
- Ngón tay = box FK: cong bằng `casc_pose.curl_fingers` (trục = finger_dir × palm_dir, theo local của từng đốt).

## measure-vs-ref
- So ref đo được: `tools/cascadeur/casc_views.py` (camera ortho trùng pixel ref) + `casc_mask.py` + `tools/eye_side.py`;
  đọc số bằng `work/cascadeur/crop_ticks.py` / `sheet.py` (vạch cm). Chỉ render khi cửa sổ Cascadeur hiện → `tools/cascadeur/front.ps1`.
- So chi tiết có shading theo từng cấp: `review_process.md#eye-vs-iou` (`partcrop.py`, `sbs_left.py`).

## autoposing
- AutoPosing kéo theo những gì không ghim: dời bàn chân làm hông xoay 35°, đặt khuỷu sai chiều dài xương làm vai tụt 16 cm.
  Luôn gửi lại mọi điểm đã duyệt trong cùng một `set_points`; khuỷu tính bằng `two_bone_elbow` (giữ chiều dài xương, hướng gập lấy từ ref).
- AutoPosing phụ thuộc trạng thái trước (cùng tham số, kết quả khác 10-20 cm) và co kéo điểm đích khi độ dài xương không cho phép
  (dời ngực lên mà Spine1 đứng yên -> solver kéo ngực/cổ xuống 11-19 cm). Muốn lưng cao thì đổi góc gập, không tịnh tiến.

## key-before-points
- **Key trước rồi mới đặt điểm** (2026-10-21): điểm đặt vào frame không có key không giữ được, lần đánh giá sau lại nội suy từ key kề.
  Gọi `casc_pose.ensure_key(scene, F)` trong một lần run_script riêng, trước `set_points`.

## base-chain
- Base của key sau là ĐIỂM ĐÍCH của key trước, không phải tư thế đã giải -> sai số sàn cộng dồn; `block_pose` ghim chân (`keys/plant.json`).
- Chuỗi base (f31 → f33 → f37..f49) phải dựng lại theo thứ tự, và mọi chỉnh tay trên `fNN.json` phải đưa vào script sinh thông số
  (mất `shift_points` f31 khi sinh lại → tay thiếu tầm 59 cm).
- Cộng nâng/xoay lên một base vốn đã kiễng → chân lơ lửng 26 cm, AutoPosing kéo hông lên 20–47 cm.

## window-focus
- **Không lấy focus cửa sổ Cascadeur:** bản `front.ps1` cũ kích hoạt cửa sổ, một phím người dùng gõ ở chỗ khác ("F" = Add/Remove key)
  lọt vào và xoá key đang dựng (log: `Shortcut "F" triggered`). Bản mới chỉ đặt cửa sổ nổi lên trên, không lấy focus
  (`-Release` để trả lại). Cascadeur vẫn ghi ảnh khi không có focus. Khi mất pose, đọc log Cascadeur trước khi đoán.
- Cửa sổ đặt ở màn hình 2 theo lựa chọn của người dùng.

## render
- **KHÔNG gọi `RenderToFile.play_to_images_sequence` (và có lẽ cả `play_to_video_file`) từ script MCP:** Cascadeur 2026.2.3
  crash ngay sau frame đầu (2026-10-21, mất cả MCP). Playblast phải làm từ UI, hoặc chụp từng frame bằng `take_image`.
  Lưu file trước mọi thử nghiệm API mới.
- **Tỉ lệ render theo kích thước viewport:** khi cửa sổ Cascadeur đổi chỗ/cỡ (mở lại sau crash, chuyển màn hình), cùng một pose
  render ra nhỏ đi ~2,5%. Kiểm bằng cách render lại một pose đã có ảnh rồi so khung bao; chỉnh K0 qua `casc_views.calibrate_k0`
  (lưu `tools/cascadeur/k0.json`; K0 lớn hơn = camera xa hơn = ảnh nhỏ hơn).
- Đổi frame trong cùng lệnh render (`scene.set_current_frame(F)` rồi `render_view`) cho ảnh đúng frame; gửi song song 15 lệnh vẫn ổn.
- 5 lệnh `render_view` gửi song song vẫn chạy lần lượt và ra đúng 5 góc (mỗi lệnh một khung hình).
- Render clip Cascadeur chỉ trong Cascadeur (user không muốn qua Blender nữa).

## fast-blocking
- **Blocking nhanh toàn thân** (người dùng: "Làm cách này lâu quá... lên blocking nhanh toàn thân, sửa chi tiết sau"):
  `work/cascadeur/block_pose.py` + tham số `keys/fNN.json` dựng nguyên một key trong một lượt (chân → hông → thân → đầu → chùy → tay),
  render 1 lần, đọc mép silhouette theo độ cao, chỉnh 1–2 lượt. Mỗi key ~3 lượt, IoU 0,6–0,78. Chỉnh từng cấp và chờ duyệt mỗi cấp
  chỉ dùng khi người dùng yêu cầu sửa chi tiết.
- `block_pose` đẩy cổ tay ra ngoài bề mặt cán (`grip_radius` 30): `props_weapons.md#grip-big-shaft`.

## quick-anatomy
- Kiểm giải phẫu nhanh trong Cascadeur: khoảng cách cha-con so bind (≤3%), góc gối/khuỷu, đầu ngón chân Y≈0, khoảng cách trục prop tới đầu/vai.
