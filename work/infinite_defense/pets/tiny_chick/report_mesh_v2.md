# Pet 13 Tiny Chick — chuyển sang mesh mới (2026-11-18)

## Kết quả
Rig, skin, Idle, Attack đã chuyển sang mesh mới. Chưa xuất FBX, chưa chép Unity, chưa qua Director (theo brief).

## CHỐT (2026-11-18, lệnh người dùng)
File v2 đã gộp thành file gốc, không giữ bản cũ (bản cũ còn trong git của repo tvc_source). Thư mục `Projects/tvc_source/3D ANIM/EndlessKicker/Pet_13_Tiny_Chick/` giờ chỉ còn:
- `tiny_chick_rig.fv`, `tiny_chick_idle.fv` (48F), `tiny_chick_attack_new.fv` (30F, bắn F12): rig + mesh mới + skin mới + texture
- `tex/T_Pet_tiny_chick_flipped_for_frolvy.png` (texture mà 3 file .fv trỏ tới, đã kiểm mở lại vẫn hiện)
- `Pet_Tiny_Chick.fbx` (Base), `Pet_Tiny_Chick_Idle.fbx`, `Pet_Tiny_Chick_Attack.fbx` — xuất mới, ghi đè 3 FBX cũ
- `CHOT.txt`
Ảnh tự kiểm: `work/infinite_defense/pets/tiny_chick/shots_v2/`.

Kiểm FBX (so với bản cũ, cùng cấu trúc):
- Base: 16 xương DEF/phụ, 1 mesh + 1 skin + 14 cluster + BindPose, 0 AnimationStack, UnitScale 100, Root ty 0,40, xoay 0.
- Idle: 16 xương trùng Base, 0 mesh, 1,6 s = 48F, 49 key mỗi curve, F0 = F48 (sai khác 1e-6), Dummy cùng cấp, take `Idle`.
- Attack: 16 xương, 0 mesh, 1,0 s = 30F, 31 key mỗi curve, F30 = F0, Dummy, take `Attack`.
Chưa kiểm: chưa chạy Unity batchmode, chưa mở FBX trong Unity. Frame bắn F12 là key của anim, FBX không gắn event.

Bẫy Frolvy Linux (để lần sau): PNG hiện lật dọc nên dùng bản lật; `save_scene` sang file đã có trả False (chỉ ghi đè được file đang mở); `open_scene` chỉ chạy khi scene sạch (lưu tạm tên mới trước); bake DEF trước khi xuất làm scene bẩn, không lưu lại.

## File làm việc (trước khi gộp)
## Texture (thêm theo yêu cầu người dùng)
Đã gắn `T_Pet_tiny_chick.png` vào cả 3 file _v2 (vật liệu `M_Pet_Tiny_Chick`). Frolvy hiện PNG lật dọc nên dùng bản lật `T_Pet_tiny_chick_flipped_for_frolvy.png` đặt cạnh file .fv (UV giữ nguyên như FBX, không sửa). Đã kiểm trước / cạnh / sau / 3-4: mắt đen, má hồng, mỏ + chân cam, thân vàng, vỏ trứng trắng, UV không lệch hay ngược (`shots/texture_check.png`, `shots/atk_v2_textured.png`). Chú ý: file .fv trỏ tới ảnh lật này, đừng xoá.

## Mesh
Mesh mới 501 đỉnh (cũ 772 trong Frolvy), 2 mảnh như cũ (thân + vỏ, mỏ). Cùng cỡ, mặt +Z, Y lên, không cần xoay. Vị trí joint giữ như cũ, hình khối mới vẫn khớp.

## Skin
Dùng cách cũ (theo vùng: mỏ → Beak, nắp → Cap, vỏ dưới → Shell, cánh, bàn chân), chỉnh hai chỗ vì lưới mới khác:
- **Cánh**: cánh mới nhỏ hơn và nằm cao hơn; mặt nạ cũ cắt cánh theo độ cao nên kéo giãn mép trên (giãn 3,6×). Đổi sang mặt nạ theo khoảng cách ngang → giãn xuống 2,2× ở góc xoay 50° (cũ 1,6×; chỉ còn vài cạnh ở gốc cánh).
- **Bàn chân**: bàn chân mới to, ăn vào cạnh đáy vỏ; ranh giới cứng giữa vỏ dưới và chân gây giãn. Pha mềm vỏ → chân: vỏ xoay 5° giãn tối đa 1,7× (trước chỉnh 2,0×).
- Tối đa 4 joint mỗi đỉnh, chỉ DEF, bind lúc mọi control = 0.

## So Idle / Attack cũ-mới
- Dùng đúng script anim cũ (key không đổi), dựng lại trên rig mới. Idle F0 = F48 (sai khác 0). Attack F30 về đúng Idle F0, bắn F12.
- Hình dáng Attack các frame 0, 6, 8, 10, 11, 12, 15, 30 trùng bản cũ (ảnh `atk_old_side.png` / `atk_v2_side.png`).
- Đo giãn lưới theo frame: Attack mới max 5,7× ở F10 (cũ 8,0×), số cạnh giãn >1,5× trung bình 15 (cũ 18). Idle mới max 2,5×. Chỗ giãn còn lại: mép trên bàn chân khi chân co (F9–14) — đoạn chân ngắn nên tỷ lệ lớn; mắt thấy không rách.

## Chưa chắc / ghi chú
- Chưa chạy Unity, chưa xuất FBX. Ảnh viewport nhỏ nên chưa soi kỹ vành răng cưa vỏ khi nắp/vỏ xoay mạnh; Anim chỉ dùng vỏ ≤5°.
- Đầu xoay mạnh (20°/25°) vẫn có 14 cạnh giãn >1,5× ở viền nắp–đầu (cũ 51 cạnh), Anim không dùng cỡ đó.
- UV mới: độ nét texture lệch nhiều giữa các mảng (không phải việc của mình).
- Tự dựng lại Idle/Attack từ script nên không có thay đổi key; nếu cần chỉnh theo mesh mới (vd chân co ở F10) thì làm vòng sau.

## Script
`work/infinite_defense/pets/tiny_chick/rig_v2/`: `skin_v2.py` (skin), `make_anim_v2.py` (dựng Idle/Attack), `skin_check.py`, `frame_scan.py` (đo giãn), `cam.py`, `sheet.sh`, `pose_shot.sh`, `shot.py`.
Lưu ý Frolvy Linux: `save_scene` sang file đã có sẽ trả False (xoá file trước); `open_scene` chỉ chạy khi scene sạch (lưu tạm sang /tmp tên mới rồi mở).
