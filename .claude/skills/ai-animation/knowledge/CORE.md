# CORE - luật cho MỌI clip
Đọc mỗi task cùng `INDEX.md`. `→ file#mục` = chi tiết trong `details/`, chỉ mở khi task đụng tới.

## Phân tích
- Viết mô tả từng pha/bộ phận (cả vải/tóc/phụ kiện), user duyệt trước khi dựng, kể cả không ref → review_process.md#no-ref-clips
- Kiểm kê xương phụ/mảnh mesh (`rig_inventory.py`); nhận diện theo vùng mesh, tên xương lừa → blender_tools.md#rig-inventory
- Camera hiệu chỉnh riêng từng clip; xác nhận file ref nào là trái/phải nhân vật → blender_tools.md#review-files
- Intake: hỏi prop treo vào joint nào khi xuất → export.md#reparent-prop
- Clip không ref / ref điện ảnh: thiết kế theo silhouette camera game, đề xuất bản tối giản → review_process.md#no-ref-clips

## Dựng pose (thô → tinh)
- Chốt P0 bằng ảnh tĩnh ở cam game + top + phía tay prop TRƯỚC khi block; đổi P0 sau đó = layer, không dựng lại → review_process.md#p0-lock
- Chân/hông → thân/đầu → prop → tay → bàn tay. Mặc định blocking nhanh toàn thân rồi sửa chi tiết; chờ duyệt từng cấp chỉ khi user yêu cầu (2026-10-21) → review_process.md#coarse-to-fine
- Cột sống không zigzag, mỗi đốt ≤ ~10°, nghiêng tăng dần hông→đầu → torso_head.md#spine-chain
- Sửa một phần: xoay quanh gốc chuỗi + bù ngược, đo phần còn lại không đổi → torso_head.md#partial-fix-hip
- Xoay theo trục local; đổi hướng người thì đo lại vai, đặt lại prop, giải lại tay → torso_head.md#world-axis-roll
- Xoắn thân đọc bằng camera nào thấy ngực/lưng; đo đỉnh đầu trước khi gập thân → torso_head.md#twist-reading
- Đổ người bắt đầu từ hông, không gù lưng → torso_head.md#lean-from-hip
- Game side view: mở ngực ~55°, đầu ~25° ra cam; prop vẫn ngắm mục tiêu → torso_head.md#open-to-camera
- Bàn chân không đứt khỏi ống chân; xem bộ phận thấp nhất trước khi nâng hông; bước chân đo bằng dải tiếp đất → legs_feet.md#foot-detach
- Pole gối theo hướng gối mong muốn; knee_dir sai khi kiễng; hông đo bằng đai lưng → legs_feet.md#knee-dir
- Pole KHÔNG tự do: gốc theo ngực/bàn chân, hướng khuỷu/gối ghi trong spec key, `pole_audit.py` mọi key trước khi render → arms_hands.md#pole-spec

## Tay, bàn tay, prop
- Không ép hướng bàn tay bằng bẻ khớp: khuỷu bản lề, xoắn chia vai/cổ tay, dời gốc chuỗi trước → arms_hands.md#no-overbend
- Kiểm tầm với vai→điểm cầm ≤ dài tay trước khi đặt tay; thiếu thì dời scapula/vai → arms_hands.md#reach
- Chọn hướng lòng bàn tay trước; cổ tay lệch ≤ ~25° → arms_hands.md#palm-dir
- Da vai ≥ 0,30 (vai lõm/xoắn); dò pole quanh trục vai→tay; mốc căng da = pose tự nhiên của mesh → arms_hands.md#shoulder-compression
- Giải tay bằng `hand_on_limited` (tools/blender/arm_limits.py + <clip>/joint_limits.json): góc giải phẫu đo từ vị trí khớp, xoay pole tới khi hợp lệ, cổ tay vượt thì nắn hướng bàn tay; pole theo bàn tay, gối theo bàn chân → arms_hands.md#joint-limits-in-solver
- Tay tự do khuỷu luôn gập > 40°; khuỷu thấp hơn vai 12–20 cm; cầm vật bên hông thì khuỷu ra ngoài → arms_hands.md#elbow-pole
- Tay di chuyển prop: FK giữa key; review + playblast thêm góc phía tay đó → arms_hands.md#prop-hand-side-fk
- Prop dày: áp lòng bàn tay lên mặt, cổ tay ngoài bán kính, không chìm trong cán → props_weapons.md#grip-big-shaft
- Prop xuyên thân = 0 ở mọi key, không đổi bằng tay căng (khuỷu ≥ ~50°) → props_weapons.md#prop-penetration
- Prop dẹt xoay theo thân / mặt về camera; súng thẳng mục tiêu ở góc top → props_weapons.md#flat-prop-orient
- Đo prop bằng số (2 view; độ cao ở view bên), không tin IoU hay crop nhỏ → props_weapons.md#prop-measure
- Prop nặng/dài: điều khiển đường đi đầu nặng; giảm vẩy theo world → props_weapons.md#heavy-prop-lever

## Timing / spline
- Một đường cong chung + trễ theo chuỗi dẫn; overlap chỉ đổi thời điểm → timing_spline.md#overlap
- Ease sine, pha về dài hơn, không key sát đáy → timing_spline.md#easing
- Spline tay IK: kiểm roll từng key, IK 2 đoạn giải tích, slerp đường ngắn → arms_hands.md#spline-ik-arms
- Đo spacing cm/F tay/prop; ~70 cm cần ≥ 5F → timing_spline.md#spacing
- User xem frame hiển thị: delay overlap = 0 ở frame then chốt → timing_spline.md#overlap
- Vải/phụ kiện: con lắc, trục ở điểm đính, biên độ rõ (~25°) → timing_spline.md#secondary-cloth
- Loop: F cuối = F1, phát f1..f(N-1), bắt đầu ở đáy; clip game non-loop kết thúc bằng Idle đứng yên → timing_spline.md#loop

## Review & ghi chú
- Mắt trước: REF|ANIM có shading mọi view, gọi tên lỗi; IoU mù trước/sau → review_process.md#eye-vs-iou
- Tự đo trước khi gửi, báo số + tác dụng phụ → review_process.md#self-measure
- Note khoanh: vẽ nét lên frame; khoanh ở hold = thêm key; note 1 frame trong hold = sửa cả đoạn → review_process.md#circled-notes
- Mỗi feedback: câu gốc + tên nguyên lý bị vi phạm → review_process.md#naming-principles
- Một hướng sửa hỏng 2 lần → 2–3 ảnh tĩnh cho user chọn hoặc mời chỉnh trong Pose Lab; giữ bản đã duyệt → review_process.md#still-options
- User muốn có trọng lượng, có hồn, luôn kèm số đo → review_process.md#reviewer-prefs

## Render / playblast / file
- Blender 4.4+: gán `action_slot`, kiểm 2 frame khác nhau → blender_tools.md#action-slot
- Posing mode, reset scale, xoá f-curve rỗng; gọi `_p0()` trước khi sửa → blender_tools.md#live-posing
- Ảnh > 1500 px bị thu nhỏ khi đọc; view left trang review = right.mov → blender_tools.md#review-files
- Cascadeur: không lấy focus, không gọi play_to_images_sequence, key trước rồi set_points → cascadeur.md#render

## QA / anatomy
- Trước khi gửi: joint_limits = 0, anatomy_check mọi key, close-up 2 góc, strain ≤ P0, prop xuyên 0, scale 1 → qa_anatomy.md#pre-send-checklist
- Ngưỡng da so min(bind, P0); low-poly xem close-up → qa_anatomy.md#anatomy-check

## Xuất
- "oki rồi" trên version mới nhất = xuất `export_clip.py`; take = tên scene; importer lệch 1F là bình thường → export.md#export-clip
- Dev đã có model → anim-only; prop ném → xuất cả 2 biến thể → export.md#anim-only
