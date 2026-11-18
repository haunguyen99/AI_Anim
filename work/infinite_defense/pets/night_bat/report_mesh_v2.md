# Night Bat — chuyển sang mesh mới (2026-11-18)

## File (chưa xuất FBX, chưa chép Unity, chưa git)
Thư mục: `/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_15_Night_Bat/v2_mesh_moi/`
- `night_bat_rig_v2.fv` — rig + skin mới + texture mới
- `night_bat_idle_v2.fv` — Idle 48F (0–48), key cũ áp nguyên
- `night_bat_attack_v2.fv` — Attack 30F (0–30), bắn F13, F30 = Idle F0
- `shots/idle_v2.png`, `shots/attack_v2.png` — ảnh tự kiểm (front/side/top)
Script: `work/infinite_defense/pets/night_bat/v2/` (rig_build_v2.py, rig_skin_v2.py, animscan.py, save.sh, posecheck.sh).

## Mesh mới
- 547 đỉnh, 3 mảnh rời: thân (387, gồm đầu, mắt, tai) + **2 mảnh cánh (80 đỉnh/mảnh)**. Hai mảnh 80 đỉnh là CÁNH, không phải mắt (brief đoán mắt).
- Hướng đúng (mặt +Z, Y lên, đáy y≈0), không cần xoay.
- Cánh là mảnh rời, gốc cánh nằm chìm trong thân → skin sạch, không còn vùng hàn cánh–đầu–tai như mesh cũ.

## Rig
- Giữ nguyên tên + phân cấp 17 joint DEF và 17 control FK. Thân/đầu/hàm/tai giữ vị trí cũ (khớp hình khối mới).
- Chỉ dời joint cánh theo cánh mới: Wing1 (0.09,0.18,0), Wing2 (0.20,0.22,-0.01), Wing3 (0.277,0.30,-0.035), Wing4 (0.38,0.255,-0.07) (đối xứng R).
- Dựng trong scene mới (không dựng lại trong scene cũ → không joint ma).

## Skin
- Cánh: 100% theo Wing1–4 dọc trục X (nội suy mượt giữa 4 joint). Thân: Root / Spine1 / Head / Jaw / Ear1 / Ear2 theo vùng, rồi làm mềm 4 lượt ở mép tai–đầu (y 0.36–0.62). Tối đa 4 influence, tổng = 1.
- Thử chuyển trọng số cũ (người dùng chỉnh tay) sang theo đỉnh gần nhất: mép tai và cổ giãn hơn (tai gập trước ×1.7, đầu ngửa ×1.8) so với công thức mượt (×1.1–1.3, ×1.3–1.4) → bỏ, dùng công thức.
- Đo skin (xoay thử cánh/tai/đầu/hàm): giãn lớn nhất cạnh tai ×1.3, cổ ×1.4; hàm mở 30° ×2.6 ở viền miệng (như bản cũ, cùng công thức hàm).

## So Idle / Attack cũ–mới
- Key áp bằng thư viện anim (control CTL_*, thay thế, 7056 key idle / 4464 key attack = 16 control × 9 kênh); giá trị control y hệt bản chốt (F0/F13/F30 attack: Wing1_L.rz −6 / 18 / −6, Root_M.ty 0,12 / 0,20 / 0,12).
- Idle: giãn lưới lớn nhất ×1.32, nén ×0.69, mọi frame. Loop F0 = F48 (cùng key).
- Attack: giãn lớn nhất ×2.67, nén ×0.31 ở F13–16, **chỉ ở viền miệng/cằm** lúc há miệng + ngửa đầu mạnh (bản cũ cũng há miệng cùng chỗ, cùng công thức hàm). Các chỗ khác ≤ ×1.4.
- Khác bản cũ: cánh hơi hẹp hơn (0,93 so với 0,98) và joint cánh dời nhẹ nên cánh quét hơi khác cữ ở độ vài cm; không đổi key nào.

## Chưa chắc / cần người xem
1. **Chấm đỏ trên cánh**: texture mới hiện một chấm đỏ ở mép dưới ngoài mỗi cánh (giống tròng mắt trong texture), còn mắt trên mặt lại không có chấm. Nhiều khả năng UV cánh/mắt của artist bị lẫn. Tôi KHÔNG sửa mesh/UV. Cần hỏi artist.
2. Chưa kiểm xuyên giữa cánh gập và thân bằng số (chỉ xem ảnh F8/F13: không thấy xuyên rõ).
3. Chưa render playblast, chưa so từng frame cạnh bản cũ bằng ảnh (chỉ so số key + ảnh tự kiểm).
4. Viền miệng giãn ×2.6 lúc há: mắt thường thấy ổn ở F13, nhưng nên xem cận cảnh nếu muốn.

## Mẹo Frolvy (Linux, ghi lại)
- `save_scene` chỉ ghi vào file đang gắn với scene; sang file khác bị từ chối. `os.remove` bị chặn trong Frolvy.
- `open_scene` trả False khi scene bị coi là đã sửa; mở xong phải lưu + mở trong cùng một lượt chạy, hoặc khởi động lại Frolvy cổng đó.
- Chuyển key giữa file: `save_anim` (chỉ CTL_*, đúng khoảng frame) → `apply_anim(mode=replace)`; sau đó `delete_anim`.

## CHỐT 2026-11-18 (lệnh người dùng)
- Gộp: 3 file `_v2` thay `.fv` gốc cùng tên trong thư mục Pet (không giữ bản cũ). Texture chép vào `Pet_15_Night_Bat/tex/T_Pet_Night_Bat.png`, cả 3 .fv trỏ về đó; mở lại từng file: texture hiện, Idle 49 key (0–48), Attack 31 key (0–30).
- Xuất FBX bằng `v2/finalize_v2.sh` (ghost_rename → fbx_ascii_keep → pet_fbx_finalize → fbx_unity_bind → fbx_strip_anim; anim: --no-meshes → finalize → fbx_add_sibling). Ghi đè 3 FBX cũ.
- Kiểm: Base 17 xương, 1 mesh, 1 Skin + 16 Cluster, BindPose, 0 AnimationStack, UnitScale 100. Idle 17 xương, 0 mesh, take Idle 1,6 s (48F @30), Dummy. Attack 17 xương, 0 mesh, take Attack 1,0 s (30F), Dummy. Tên xương 3 file trùng nhau.
- Ảnh tự kiểm chuyển vào `shots_v2/`; đã xóa `v2_mesh_moi/` và file raw/tạm.
- Chưa kiểm bằng Unity batchmode (chỉ kiểm cấu trúc FBX bằng đọc file).
