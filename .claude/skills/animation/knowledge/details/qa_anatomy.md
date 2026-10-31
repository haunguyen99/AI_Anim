# QA & anatomy pass (mọi loại anim)

## pre-send-checklist
**Kiểm tra bắt buộc trước khi gửi** (gộp từ _common và checklist Attack):
- `tools/joint_rules.py audit` mọi key: không lỗi mới so P0 (#joint-coupling); `joint_limits.py` = 0 vi phạm; close-up từng tay/chân ở 2 góc; độ căng da vai/khuỷu/cổ tay (`arm_strain`) không vượt P0 đã
  duyệt; khiên/giáp theo xoắn cánh tay trên, không xoay độc lập; khuỷu/gối không gập ngược, không duỗi quá thẳng; khuỷu ngoài thân.
- Prop xuyên thân = 0 ở mọi key có prop (`props_weapons.md#prop-penetration`).
- Dữ liệu: scale = 1, không quaternion 0, không f-curve rỗng; pose sau khi Blender tính lại = pose đã dựng; hàm dựng chạy lại
  (`from_p0`) ra đúng pose đã key.
- Tự đo nhịp/tốc độ/trượt chân/loop: `review_process.md#self-measure`.

## anatomy-check
- "check lại Anatomy toàn thân của từng key chính đã key" (Blender Attack blocking v4): sau mỗi đợt key chạy
  `work/blender/anatomy_check.py` trên mọi key (đo hình học so P0: độ dài đùi/ống chân/cẳng tay = khớp còn liền, gập gối/khuỷu,
  hướng gối so mũi chân, xoắn/gập thân-đầu-cổ tay so P0, căng da so cả bind lẫn P0, xuyên mesh, dưới đất) rồi nhìn cận chỗ bị
  đánh dấu; sửa bằng `anatomy_fix.py`. Nguyên lý: Solid Drawing.
- Bộ đo căng da so bind vô dụng ở rig Gaygor (P0 đã giãn 3x ở hông): so cạnh với min(bind, P0). Ngưỡng phụ thuộc mesh:
  `arms_hands.md#shoulder-compression`.
- Thêm vào anatomy pass: cột sống không zigzag, nghiêng tăng dần (`torso_head.md#spine-chain`); da vai ≥ 0,30.
- SDR (sdr_lib.anatomy): da váy giữa hai đùi giãn x4-6 ở lunge là bình thường với low-poly, xem close-up thay vì tin ngưỡng.
- Cascadeur: `cascadeur.md#quick-anatomy`.

## Skin khuỷu lệch trên rig team (SDR01, 2026-10-29)
- Mesh thấp đa giác, khuỷu gập ~110°: mặt trong thắt, mặt ngoài nhô góc. Đo trước khi đổ cho pose: `sdr01/elbow_check.py` (góc gập,
  xoắn cẳng tay, hồ sơ trọng số dọc tay). Lỗi gặp: đoạn cẳng tay 0–10 cm sau khuỷu còn 18–54 % Shoulder (vùng chuyển lệch về cẳng tay).
- Sửa: chia lại Shoulder+Elbow theo smoothstep ±6 cm quanh tâm khớp (`elbow_reskin.py`), ghi chỉ 4 cluster vào bản FBX trong job
  (`apply_skin_s3.py`, giữ byte phần còn lại). Chọn dải bằng mắt (ảnh cận 3 góc): đếm tam giác lật không phân biệt được các dải.

## joint-coupling
**Giới hạn + liên động khớp** (2026-10-31, user: "khi muốn giơ tay lên đầu thì cầu vai cũng phải đi theo... AI cần phân tích và
phán đoán để tạo sự liên kết giữa các bộ phận"). Nguyên lý: Solid Drawing + Overlap (cơ thể chuyển động như một chuỗi, không khớp lẻ).
- Công cụ: `tools/joint_rules.py` + luật `tools/joint_rules/biped.json` (ghi đè theo job: `work/<dự án>/<job>/joint_rules.json`,
  luật theo `id`, `"off": true` để tắt). Mọi số đo so với **P0 đã duyệt** (ref), không so T-pose.
- Trong script dựng key: `JR.audit(rig, P, R, ref=P0)` rồi `JR.apply(rig, P, R, ref=P0, keep=...)` trước khi ghi key.
  `keep="hand"` (mặc định): bàn tay / prop giữ nguyên world, khuỷu gập lại quanh đúng trục bản lề đang có (`keep_hand`);
  `keep="dir"`: xoay vai FK, giữ hướng cánh tay, tay dời theo điểm vai; `keep="fk"`: tay quay theo bả vai.
- Soi cả clip: `python -I tools/joint_rules.py audit --rig RIG.fbx --anim ANIM.fbx --tex TEX [--fix --render F --view front --out dir]`.
- Luật v1: `scap_elev` (tay giơ → xương đòn nhún, 0° ở 30°, +6° ở 90°, +20° ở 180°), `scap_prot` (tay ra trước → bả vai ra trước tới
  +14°, vung ra sau → kéo về −14°, nhân trọng số theo độ giơ), `spine_share` (Spine1/Chest 50/50, lỗi khi một đốt < 25 % hoặc > 75 %,
  tổng ≥ 10°), `neck_share` (Neck/Head 40/60, tổng ≥ 12°), `hip_lead` (ngực ngả ≥ 35° thì hông ≥ 30 %, chỉ báo), `elbow_twist`
  (khuỷu xoắn so P0 ≤ 20°, chỉ báo), giới hạn khớp hộp gập/dạng/xoắn quanh rest (quy ước Rig bước 6; kẹp tự động: cột sống, cổ, đầu,
  bả vai). **Giới hạn tự nới tới giá trị của P0 đã duyệt** (SDR01: gối trái dạng −17°, cổ tay trái xoắn −72° ngay ở P0) → chỉ bắt lỗi
  tệ hơn P0.
- Đo trên SDR01 Shoot (đã duyệt, làm trước khi có luật): Scapula hai bên đứng yên ở mọi frame (10,4° và 5,2° so rest), tay ném ra
  trước 100–110° → thiếu bả vai ra trước +11–13° ở F5–F17; quay đầu 13–52° chỉ bằng Head (Neck 0 %) ở F4–F20. Bài thử tay qua đầu
  (Idle P0, cánh tay 85° → 167°): apply thêm xương đòn +12,6° nhún, +3,2° ra trước, điểm vai cao 3,1 cm, audit sau = 0.
- `rigpose.Rig.ik_arm` **lật khuỷu** khi giải lại một tay đang gập (SDR01 Shoot F8 tay trái: gập 111° → −121°, cổ tay xoắn 167°,
  vì hai chiều bản lề cùng sai số 0 và nó lấy chiều đầu). Giữ tay sau khi dời gốc chuỗi thì dùng `joint_rules.keep_hand`, đừng ik_arm lại.
- **Studio** (2026-10-31, user "Nối vào Studio"): `tools/studio/modules/joint_rules.js` + bản vá `jrRun` trong `pose_patches.py`.
  Kéo xong một khớp (gizmo) hoặc lệnh AI `anim rot/pos` → bả vai / Spine1-Chest / Neck-Head tự theo, cùng một bước Ctrl+Z, trước
  Auto key; đo theo phần thay đổi của lần sửa đó (so pose trước khi kéo), không cãi pose cũ. Chọn cổ tay (dời IK) = bàn tay giữ chỗ;
  xoay vai = giữ hướng cánh tay. Nút **Liên động** cạnh Khóa chân (nhớ theo máy). Luật nhân vật: `work/rig_lab/chars/<id>/joint_rules.json`
  (Home `/api/joint-rules?char=`). Cầu nối: `studio_cmd.py anim rules [on|off|status]`, `anim rules audit [keys|all|5,9]` (so F1),
  `anim rules apply [f]` (cả pose so F1, mọi luật). Thử SDR01 Shoot s1: audit khớp bản Python (lệch 1 F do Studio đếm từ F1);
  xoay vai phải 50° → bả vai nhún 6°, ra trước 4°; dời cổ tay +15 cm → nhún 4°, ra trước 2°, bàn tay đúng chỗ như khi tắt luật.
  Studio chưa kiểm giới hạn khớp (chỉ bản Python). Thử sửa trên clip thật: sao lưu `work/store/<clip>_pose_lab` trước (sửa = ghi key).
- Đường cong là điểm khởi đầu: khi user chê / duyệt một bản có số đo khác, chỉnh `curve` trong `biped.json` (mọi nhân vật) hoặc
  `joint_rules.json` của job (riêng nhân vật / phong cách), ghi ngày + câu gốc ở đây.
