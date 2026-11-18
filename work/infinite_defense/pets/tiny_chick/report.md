# Báo cáo GEK-2357 — Pet 13 Tiny Chick (rig + Idle + Attack)

Thư mục làm việc: `C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_13_Tiny_Chick\`

## Kết quả
Rig, skin, Idle, Attack xong và đã xuất FBX. Chưa qua Director, chưa playblast MP4, chưa mở FBX trong Unity. Mới tự kiểm bằng ảnh viewport (ảnh ở `work/infinite_defense/pets/tiny_chick/shots/`).

## Mesh
- FBX gốc chỉ có mesh, không xương, không skin. 772 đỉnh, 2 mảnh: thân (gồm vỏ trứng trên + vỏ dưới + cánh + chân dính liền) và mỏ.
- Mesh nằm nghiêng (Z lên, mặt về -Y). Đã xoay -90° quanh X rồi freeze: giờ Y lên, mặt +Z, cao ~0,95, chân chạm y=0.

## Rig (FK, như Pebble Turtle)
- 16 joint: Root_M (hông), Spine1, Head, Cap (nắp vỏ trên, bản lề ở sau), Shell (vỏ dưới, xương riêng để va lách cách), Beak, **DEF_Muzzle_M** (đầu mỏ, con của Beak, không skin), cánh 2 đốt x2, chân (Ankle, Toes) x2.
- 14 joint DEF có skin; 15 control (CTL_*), check_rig rỗng.
- Skin viết theo vùng: mỏ 100% Beak; nắp trên theo độ cao → Cap; vỏ dưới → Shell; cánh theo độ xa trục; bàn chân Ankle/Toes; thân Root/Spine1/Head theo độ cao. Tối đa 4 joint mỗi đỉnh. Thử xoay các khớp thấy sạch; vỏ dưới xoay quá ~10° thì hở khe với bụng (anim chỉ dùng ≤5°).

## Idle — 48 frame, lặp (frame 0 = frame 48)
Thân hover 12 cm, bồng bềnh 1 nhịp/vòng; lắc mông 2 nhịp/vòng (xoay quanh trục đứng ±8°, thêm nghiêng nhẹ), đầu giữ nhìn thẳng. Vỏ dưới trễ và lắc rộng hơn thân, nắp trên gõ gấp đôi nhịp → lách cách. Cánh, chân thả lủng lẳng, trễ pha sau thân. Có đặt chế độ lặp trên curve.

## Attack — 30 frame
0 lơ lửng · 5–8 lấy đà (hạ thân, ngả sau, cánh khép) · 10 vút lên (cánh vỗ, chân co) · **12 BẮN (gắn event ở frame 12)**: thân vút lên cao ~20 cm, lao tới ~22 cm, chúi người ~40° mổ, mỏ chĩa trước · 15 giật lại · 19–24 giảm đà · **30 về đúng tư thế Idle frame 0**. Key mỗi frame (nội suy mượt).

## File
- `tiny_chick_rig.fv` (rig + skin, chưa anim) · `tiny_chick_idle.fv` · `tiny_chick_attack.fv`
- **Base** `Pet_Tiny_Chick.fbx` = xương + mesh + skin, đứng bind pose (1 mesh, 15 deformer).
- **Anim-only** `Pet_Tiny_Chick_Idle.fbx` (0–48, 1,6 s) · `Pet_Tiny_Chick_Attack.fbx` (0–30, 1,0 s): chỉ xương + clip, 0 Geometry / Deformer / Material; bộ tên xương DEF_* trùng Base. UnitScale 100, take tên Idle / Attack.
- Script: `work/infinite_defense/pets/tiny_chick/rig/` (import_mesh, build_rig, skin), `anim/` (idle, attack, make_clips). `finalize.py` (UnitScale + kiểm mesh; `tools/pet_fbx_finalize.py` đang lỗi cú pháp dòng 22 do phiên khác sửa dở nên dùng bản này). Công cụ phụ mới: `tools/_pt_frames.py` (ảnh nhiều frame một tấm).

## Sửa FBX cho Unity (2026-11-12, theo lỗi Pebble Turtle)
- Base: thêm BindPose + sửa TransformLink (`fbx_unity_bind.py`), bỏ clip tĩnh (`fbx_strip_anim.py`). File anim: thêm nút Null cùng cấp (`fbx_add_sibling.py`).
- Phát hiện thêm: lần xuất Base đầu bị lệch (Root ty 0,54, xoay 3,7° — dính pose frame 0 của anim, do key bake còn trên joint DEF). Đã xoá key, xuất lại: Root ty 0,40, mọi xoay 0.
- Chưa chạy Unity batchmode để kiểm.

## Vướng / chưa chắc
- Frolvy cổng 9882 "đã mở sẵn" bị tắt giữa chừng (mất bản đầu) — mình mở lại Frolvy mới trên 9882 và dựng lại từ script.
- Vỏ trứng nằm chung một mảnh mesh với thân, nên nắp trên tách bằng độ cao (ramp 0,58–0,68), vỏ dưới tách theo độ cao <0,38. Vành răng cưa có thể kéo giãn nhẹ khi nắp/vỏ xoay mạnh.
- Cộng dồn góc chúi của Root+Spine+Head+Beak ở frame bắn ~40°; nếu muốn mổ mạnh hơn thì tăng.
- Idle f0 có vận tốc xoay khác 0 còn Attack nối vào đứng yên: chỗ nối Attack→Idle có thể giật nhẹ, chưa xem trong game.
- FBX là Generic, tên xương DEF_*; DEF_Muzzle_M nằm trong cây DEF_Beak_M nhưng chưa kiểm trong Unity. Không có key chạm đất (đúng luật bay lơ lửng).
- Không commit/push.
