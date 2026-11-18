# Pebble Turtle (Pet 12) - chuyển sang mesh mới (2026-11-18)

## Đã làm
- Mesh mới Pet_Pebble_Turtle.fbx (703 đỉnh, 6 mảnh rời: mai+đuôi 378, đầu 123, 2 chân trước 61x2, 2 chân sau 40x2) thay 4 mesh cũ trong chính file rig/idle/attack đã chốt.
- Hướng đúng sẵn: Y lên, mặt +Z, đáy chân y≈0, cao 0,67. Không xoay, không scale.
- Giữ NGUYÊN joint (18), control, cây phân cấp và toàn bộ key cũ (Idle 0-48, Attack 0-36, 9 và 13 node có key). Không đổi key nào.
- Skin: bind ở pose 0 (mọi control = 0), chỉ joint DEF, tối đa 3 influence, tổng = 1. Luật trọng số như bản cũ, áp theo từng mảnh: mai -> Root (đuôi dốc Tail1/Tail2), đầu 100% Head, chân chia Hip/Ankle/Toe theo chiều cao.
- Joint không dời: hình khối mới gần như trùng cũ (chân, đầu, đuôi cùng chỗ).

## So Idle / Attack cũ - mới (ảnh: v2_mesh_moi/shots/attack_cu_moi.png, trái = cũ, phải = mới; f0, f10, f15)
- Attack: cùng nhịp. F10 đầu rụt hết vào mai, không xuyên ra ngoài (nhìn cạnh, trước, trên); F15 đầu bật ra khạc sỏi, đầu mới to hơn một chút nên trông nặng hơn, mặt vẫn lộ rõ. F0 và cuối về đúng idle.
- Idle: lắc thân, đuôi vẫy, rụt đầu nhẹ f26-44 đều chạy đúng, đầu không lẹm vào mai (ảnh idle_v2.png). Key không đổi nên vòng lặp f48 = f0 vẫn liền.
- Khác biệt thấy được: mai/đầu hơi to hơn bản cũ (do mesh), không do anim.

## File (thư mục Pet_12_Pebble_Turtle/v2_mesh_moi/ trong repo team ~/Projects/tvc_source/3D ANIM/EndlessKicker/)
- PebbleTurtle_rig_v2.fv, PebbleTurtle_idle_v2.fv, PebbleTurtle_attack_v2.fv (lưu xong, mở lại được, key còn nguyên)
- shots/: atk_v2.png (6 frame x side/front/top), idle_v2.png (5 frame x 3 góc), attack_cu_moi.png
- Script dựng: work/infinite_defense/pets/pebble_turtle/v2/build_rig_v2.py

## Chưa kiểm / lưu ý
- Texture đã gắn (xem mục dưới). Chưa xuất FBX, chưa thử Unity (theo luật).
- Skin chỉ xem bằng mắt ở các frame mấu chốt (chân trước ở đỉnh Attack f15 và Idle, đầu rụt f10), chưa đo số / chưa gọi Director. Chưa xoay mạnh từng khớp ngoài anim.
- Mesh mới đặt tên Pet_Pebble_Turtle; file cũ ở DataHDD/.../v2_mesh_moi/PebbleTurtle_rig_v2.fv (phiên con trước, dở dang, mesh rỗng) bỏ, không dùng.
- Bẫy Frolvy: open_scene và save_scene sang đường dẫn đã có file đều bị từ chối khi scene đang sửa dở / file đã tồn tại và trả False không báo lỗi. Script phải kiểm giá trị trả về; cách chạy lại: xoá file _v2 cũ, khởi động lại cửa sổ rồi chạy.

## Texture (thêm 2026-11-18)
- Gắn T_Pet_Pebble_Turtle.png (từ Pet_new/texture) bằng material M_Pet_Pebble_Turtle lên mesh, trong cả 3 file _v2, đã lưu. Texture trong Unity, không chép đi đâu.
- UV khớp: mắt đúng hốc mắt, mặt + chân màu da, bụng xanh, mai xám có mảng xanh, không lật/ngược (trước + cạnh, Idle/Attack f0, f10, f15). Ảnh: shots/tex_rig_front_side.png, shots/tex_attack_v2.png.
- Script: work/infinite_defense/pets/pebble_turtle/v2/texture_v2.py (đặt FILE=rig_v2|idle_v2|attack_v2).
- Chỉ nhìn ở góc trước/cạnh, chưa soi mặt sau/đáy mai kỹ.

## Chốt (2026-11-18, lệnh người dùng)
- Đã gộp: 3 file _v2 thay file .fv gốc cùng tên (không còn bản cũ, không còn _v2, thư mục v2_mesh_moi/ đã xóa). Ảnh tự kiểm chuyển sang shots_v2/.
- Texture: tex/T_Pet_Pebble_Turtle.png trong thư mục Pet, đã trỏ lại trong rig/idle/attack, mở lại từng file texture còn hiện. (Trong .fv còn một dòng ghi đường dẫn texture cũ ở Unity, không dùng, vô hại.)
- FBX xuất bằng export_raw.py + finalize.sh (cùng thư mục script): Pet_Pebble_Turtle.fbx (Base), _Idle.fbx, _Attack.fbx. Base: 18 xương, 1 mesh, 1 skin, 16 cluster, BindPose, 0 AnimationStack, UnitScale 100. Idle/Attack: 18 xương (tên trùng Base) + Dummy, 0 mesh, take Idle (48F) / Attack (36F), UnitScale 100.
- Kiểm: Idle và Attack khóa đầu = khóa cuối (lặp liền / về pose F0); Attack đầu ra xa nhất f15 (khạc sỏi), rụt sâu nhất f10. Chưa thử trong Unity batchmode (không có Unity trên máy Linux này), chưa kiểm Copy Avatar.
