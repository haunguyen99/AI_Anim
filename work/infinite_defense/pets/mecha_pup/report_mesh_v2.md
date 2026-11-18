# Mecha Pup — chuyển sang MESH MỚI (2026-11-18)

## Kết quả
Xong: rig, Idle, Attack trên mesh mới. Idle/Attack giống bản chốt cũ tới <0,01 mm trên mọi đỉnh ở các frame đã đo.

File (thư mục `Pet_11_Mecha_Pup/v2_mesh_moi/` trong repo `Projects/tvc_source/3D ANIM/EndlessKicker`):
- `mecha_pup_rig_v2.fv` — rig + mesh mới đã skin
- `mecha_pup_idle_v2.fv` — Idle 48F, lặp
- `mecha_pup_attack_v2.fv` — Attack 24F (frame bắn 9)
- `shots/attack_v2_f0_f9_f15.png` — ảnh tự kiểm
File cũ không đụng. Chưa xuất FBX, chưa chép Unity.

## Đã làm gì
1. Nhập `Pet_Mecha_Pup.fbx` mới (1599 đỉnh, 1680 mặt; bản cũ 1606 đỉnh, 1689 mặt). File mới quay mặt -Z → xoay 180° quanh Y rồi freeze, ra mặt +Z, đáy y≈-0,04, đỉnh cao 1,12 m, giống hệt khung cũ.
2. Hình khối trùng bản cũ: cả 1599 đỉnh mới nằm trên một đỉnh cũ (lệch < 0,1 mm). Bản cũ có 7 đỉnh thừa không còn ở bản mới.
3. Skin: bind lại với đúng 31 joint DEF bản cũ ở bind pose (mọi control = 0, frame 0). Trọng số chép từ đỉnh cũ trùng vị trí, tổng = 1, tối đa 4 joint/đỉnh. Không phải sửa tay vì vị trí đỉnh không đổi.
4. Joint, control, cây phân cấp giữ nguyên (không dựng lại rig).
5. Anim: không dựng lại, mà chép nguyên key từ file idle/attack cũ sang rig v2 (2850 key / 19 control cho Idle, 1026 key cho Attack, đúng frame như cũ). Idle chạy lại Smooth Loop Seam (đóng vòng F0 = F48) để tangent hai đầu giống bản cũ.

## So cũ – mới
- Giá trị control từng frame (Idle F1–F48): lệch tối đa 0,04° (do tangent hai đầu tính lại). F0 của file cũ đọc sai khi dump (bẫy set_frame(0)), F0 mới = F48 đúng.
- Vị trí đỉnh sau skin, 8 frame Idle (0,6…42) và 12 frame Attack (0,3,5,7,9,11,13,15,17,19,21,24): lệch lớn nhất < 0,01 mm. Nghĩa là xoắn/co kéo, khe hở, xuyên mesh y hệt bản cũ (cả ưu lẫn nhược).
- Frame bắn Attack vẫn F9, thân Attack/Idle không đổi.

## Chưa kiểm / chưa chắc
- Chưa xem playblast đầy đủ, chỉ ảnh viewport 3 frame Attack (không thấy vỡ lưới).
- Giữ nguyên các điểm yếu skin cũ (vài cạnh chân sau co kéo, gốc tai) vì yêu cầu giữ anim đã chốt; không sửa lại.
- Texture/material mới: Frolvy không nạp được vật liệu từ FBX (danh sách vật liệu rỗng), chưa gán texture trong .fv; UV mới nằm trong mesh, texture sẽ do Unity gán. Không ảnh hưởng rig.
- Chưa chạy Director, chưa xuất FBX (chờ "chốt").
- Idle F0 vs Attack cuối: không đổi so với bản cũ (key chép nguyên).

## Bẫy Frolvy trên Linux (cho Pet sau)
- `api.open_scene` trả False khi scene hiện tại có thay đổi chưa lưu và hiện hộp thoại "Unsaved changes" (bấm tay mới tắt). Cách tránh: `save_scene` ra file tạm (/tmp/x.fv) rồi mới `open_scene` (copy .fv sang /tmp cho chắc).
- `go_to_bind_pose` báo 4 joint không về được khi scene có key; vì vậy không bind lại trong file idle/attack — bind trong file rig sạch rồi chép key sang bằng `save_anim` → `apply_anim` (replace) + dump giá trị đối chiếu.
- `api.mesh_data(tên, True)` trả vị trí đỉnh ĐÃ biến dạng (không có đối số là vị trí bind): dùng để so cũ/mới số học.
- Script dùng lại: `work/infinite_defense/pets/mecha_pup/v2/` (`anim_dump.py`, `anim_apply.py`, `pos_dump.py`, `pos_compare.py`, `swap_mesh.py` — swap_mesh chạy trên scene có key không dùng được, xem trên; `mcp_call.py` gọi tool MCP như scene_file).

## Texture (thêm 2026-11-18)
- Đã gắn `T_Pet_mecha_pup.png` (material `M_Mecha_Pup`) lên mesh trong cả 3 file `_v2`; bản copy texture nằm cạnh: `v2_mesh_moi/T_Pet_mecha_pup.png` (file .fv trỏ đường dẫn này; đổi chỗ thư mục thì gắn lại bằng `v2/tex_apply.py`).
- Tự kiểm trước + cạnh: `shots/texture_v2_truoc_canh.png` — mũ phi hành gia, tai cam, đĩa ăng-ten xanh, không thấy UV lật/lệch. Chỉ nhìn từ viewport nhỏ, chưa soi từng mảnh nhỏ (balo, chân sau, dưới bụng).
- Texture chỉ để xem, không đụng skin/anim.

## Sửa "rig chưa về dáng gốc" (2026-11-18, theo phản hồi người dùng)
- Nguyên nhân 1: file rig cũ có kênh control (Head rx/rz, IKWrist/IKAnkle ty/tz) mang "đường cong chết" giữ giá trị lệch; đổi frame là con chó nhảy về dáng lệch (đầu nghiêng, 4 chân nhấc ~12 cm). Đã sửa: đặt về 0 + key 0 ở F0 trên 10 kênh đó, đổi frame giữ nguyên dáng gốc.
- Nguyên nhân 2: ở dáng gốc (mọi control = 0) hai đầu gối sau lệch 2,1 cm so với lúc bind (IK kéo gối vào thẳng hàng hông-cổ chân), nên mesh ở dáng gốc lệch tối đa 2,96 cm (168 đỉnh > 0,5 cm) so với mesh gốc, và `go_to_bind_pose` báo 4 joint không về được. Đã sửa trong `mecha_pup_rig_v2.fv`: bind lại ở đúng dáng gốc (cùng 31 joint DEF, trọng số y nguyên) → mesh ở dáng gốc lệch 0,0 cm, `go_to_bind_pose` về được.
- Chưa áp cho `_idle_v2`/`_attack_v2` (vẫn bind cũ, khớp tuyệt đối bản chốt). Nếu áp: Idle đo thử lệch tối đa 2,9 cm (đỉnh quanh gối sau), trung bình 0,15 cm so với bản chốt.

## Sửa texture lắp lộn (2026-11-18)
- Frolvy hiển thị PNG bị lật dọc (giống .tga), nên texture gốc lên mesh bị lộn. Đã dùng bản lật dọc `v2_mesh_moi/T_Pet_mecha_pup_flipV.png` cho cả 3 file `_v2`: tai hồng bên trong, tai nghe xanh có điểm sáng cyan, đĩa ăng-ten sạch, bụng xanh. Ảnh kiểm: `shots/texture_v2_truoc_sau_canh_tren.png`.
- Chỉ là hiển thị trong Frolvy. FBX và Unity vẫn dùng texture gốc `T_Pet_mecha_pup.png` (UV mesh không đổi), nên trong Unity vẫn đúng như người dùng thấy.
- Texture cũ (không lật) vẫn nằm cạnh để so; mesh/UV không bị lắp nhầm FBX (nhập đúng `Pet_Mecha_Pup.fbx` mới).

## CHỐT + XUẤT FBX (2026-11-18)
- Đã gộp: `mecha_pup_rig.fv`, `mecha_pup_idle.fv`, `mecha_pup_attack.fv` trong thư mục Pet thay file cũ (bản cũ đã nằm trong git). Texture chuyển vào `tex/` (flipV + bản gốc), cả 3 .fv trỏ về `tex/`; đã xóa `v2_mesh_moi/` và mở lại từng file kiểm texture còn hiện. Ảnh tự kiểm: `work/infinite_defense/pets/mecha_pup/shots_v2/`.
- Idle/Attack trong .fv đã dựng lại trên rig bind mới (dáng gốc): key chép nguyên (giá trị control lệch 0,0 so với bản v2; Idle chạy lại Smooth Loop Seam, F0 = F48), chỉ skin vùng gối sau đổi theo bind mới (như đã báo, tối đa ~2,9 cm).
- FBX (Frolvy → `fbx_ascii_keep --root DEF_Root_M` → `pet_fbx_finalize` → `fbx_unity_bind_rot` (xương có orient, không dùng fbx_unity_bind) → `fbx_strip_anim` cho Base; `fbx_add_sibling` cho anim). Xuất từ chính 3 .fv, rig ở dáng gốc, fps 30:
  - `Pet_Mecha_Pup.fbx`: 46 xương, 1 mesh, 32 deformer (31 cluster), có BindPose, 0 AnimationStack, UV có, UnitScale 100. Kiểm: |world tính lại − TransformLink| tối đa 1,5e-6.
  - `Pet_Mecha_Pup_Idle.fbx`: 46 xương trùng tên Base, 0 mesh, có Dummy cùng cấp, take Idle, 48 frame, loop F0 = F48.
  - `Pet_Mecha_Pup_Attack.fbx`: 46 xương trùng Base, 0 mesh, Dummy, take Attack, 24 frame, key mọi frame (F9 bắn).
- Chưa kiểm: chưa nhập vào Unity batchmode (Linux, chưa thử), nên chưa soi skin/Copy Avatar trong Unity thật.
- Sự cố: Frolvy cổng 9881 tự chết giữa chừng (do đợt khởi động lại Frolvy 11:03). `frolvy_port.py`/`Frolvy-mcp` khi cổng chết sẽ TỰ chuyển sang một cửa sổ Frolvy khác (không báo lỗi rõ) — vài lệnh của mình (lưu scene ra /tmp/mp_scr_5606.fv, bước frame, chọn node, một mục thư viện `mp11_Fattack`) đã chạy nhầm vào cửa sổ Frolvy của Pet Wind Chameleon (đúng lúc nó vừa mở lại) trước khi mình phát hiện. Mình đã xóa mục thư viện; đường dẫn scene của cửa sổ đó có thể đang trỏ /tmp/mp_scr_5606.fv (bản sao scene của họ), nên người làm Wind Chameleon nên Lưu như... sang đúng đường dẫn Pet_16. Mình đã mở lại Frolvy cổng 9881 và thêm bước kiểm cổng trước mỗi lệnh.
