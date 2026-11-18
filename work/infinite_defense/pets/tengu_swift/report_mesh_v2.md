# Tengu Swift: chuyển sang MESH MỚI (2026-11-18)

## Kết quả
Xong: rig, Idle, Attack trên mesh mới. Idle/Attack giống bản chốt cũ tới 0,000 mm trên mọi đỉnh đã đo.

File (thư mục `Pet_18_Tengu_Swift/v2_mesh_moi/` trong repo `Projects/tvc_source/3D ANIM/EndlessKicker`):
- `tengu_swift_rig_v2.fv`: rig + mesh mới đã skin
- `tengu_swift_idle_v2.fv`: Idle 48F, lặp
- `tengu_swift_attack_v2.fv`: Attack 30F (frame bắn 12)
- `shots/attack_v2_front_f0_f6_f12.png`, `shots/attack_v2_side_f0_f12_f18.png`: ảnh tự kiểm
File cũ không đụng. Chưa xuất FBX, chưa chép Unity.

## Mesh mới khác gì cũ
Chỉ khác ở mũi mặt nạ Tengu (file Unity artist sửa 18/11 09:27): thân 906 → 912 đỉnh, mũi dài ra trước thêm ~6 cm (z 0,30 → 0,36 m), 24 đỉnh mũi mới thay 18 đỉnh cũ. 888 đỉnh còn lại trùng bản cũ tuyệt đối. Quạt không đổi (giữ quạt cũ đã nằm trong nắm tay phải + skin cũ). Hướng +Z, Y lên, không phải xoay.

## Đã làm gì
1. Mở file rig cũ, controls = 0 (bind pose), nhập `Pet_tengu_swift.fbx` mới, bỏ mảnh quạt của file mới, thay thân cũ bằng thân mới (cùng tên).
2. Skin: bind lại với đúng 17 joint DEF của thân cũ; trọng số chép từ đỉnh cũ gần nhất (888 đỉnh trùng vị trí; 24 đỉnh mũi lấy từ đỉnh gần nhất, toàn bộ 100% Head). Tối đa 4 joint/đỉnh, tổng = 1.
3. Joint, control, cây phân cấp giữ nguyên.
4. Anim: chép nguyên key 19 control từ idle/attack cũ sang rig v2 (save_anim → apply_anim replace), không dựng lại.

## So cũ – mới
- Vị trí đỉnh sau skin: Idle 9 frame (0, 6…42, 47), Attack 11 frame (0, 3…30): lệch lớn nhất 0,000 mm trên 888 đỉnh thân trùng + 141 đỉnh quạt. Nghĩa là Idle/Attack y hệt bản chốt.
- Mũi mới (24 đỉnh) chỉ theo đầu: không xuyên quạt. Khoảng cách mũi–quạt nhỏ nhất ở Attack ~9 cm (f12–f15), Idle ≥ 36 cm.
- Ảnh viewport Attack f0/f6/f12/f18: không rách lưới quanh mũi.

## Chưa kiểm / chưa chắc
- Chưa xem playblast đầy đủ, chưa Director, chưa xuất FBX (chờ "chốt"), chưa chạy Unity.
- Texture: .fv chưa gắn texture mới (ảnh tự kiểm là lưới xám); texture Unity không đổi từ 13/11 nên không ảnh hưởng.
- Ghi chú dò số mới chỉ cho thân + quạt; không đo xuyên giữa mũi và tay trái/phải.

## Bẫy Frolvy (Linux)
- `save_scene` ra file ĐÃ TỒN TẠI trả False (không lưu): xóa file đích trước. `open_scene` trả False khi scene đang sửa: lưu ra /tmp/tên-mới rồi `new_scene()` rồi mới `open_scene`.
- `tools/frolvy_shot.py` và `tengu_swift/shot.py` trong repo đang trỏ đường dẫn Windows: dùng bản copy sửa EXE (mecha_pup/v2/shot.py) và đơn vị camera là mét (ow 1.4, cy 0.45).

## Chốt + xuất FBX (2026-11-18)
- Gộp `_v2` thành file gốc (bỏ hậu tố, bản cũ nằm trong git của repo team); xóa `v2_mesh_moi/`; ảnh tự kiểm chuyển sang `shots_v2/`.
- Texture: `Pet_18_Tengu_Swift/tex/T_Pet_tengu_swift_flipV.png` (bản lật dọc để Frolvy hiện đúng), đã gắn vào rig/idle/attack, kiểm mở lại thấy "loaded". Chỉ để xem; FBX không mang texture.
- Xuất bằng `finalize_v2.sh` (Linux) từ raw của chính 3 file .fv: ghost_rename → fbx_ascii_keep → pet_fbx_finalize → fbx_unity_bind → fbx_strip_anim (Base), fbx_add_sibling (Idle/Attack).
- Kiểm so FBX chốt cũ: 20 xương trùng tên, Base 2 mesh + 21 deformer + BindPose, 0 AnimationStack, đơn vị 100; Idle 1,6 s (48F), Attack 1,0 s (30F), 0 mesh, có Dummy, take Idle/Attack. Vị trí/xoay xương Base lệch 0; Idle/Attack lệch ≤ 2e-6 so với FBX chốt cũ. Thân đổi duy nhất ở mũi (3170 → 3194 chỉ số).
- Chưa chạy Unity batchmode, chưa chép vào Unity.
