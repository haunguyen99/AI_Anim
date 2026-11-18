# Pet 12 Pebble Turtle (GEK-2356) - báo cáo

## Mesh
- FBX gốc không có xương/skin: 4 mảnh (mai + đuôi, đầu, 2 chân trước, 2 chân sau).
- Mesh nhập vào nằm nghiêng (Z lên, mặt về -Y). Đã xoay -90° quanh X rồi freeze: giờ Y lên, mặt hướng +Z, chân chạm y=0. Cỡ model ~0.9 đơn vị (giữ nguyên, không scale).

## Rig (cổng 9881)
- 18 joint: Root_M (hông), Tail1/2, Neck, Head, Muzzle (ổ bắn, con của Head, ở miệng), 4 chân x (Hip, Ankle, Toe). Không helper/twist.
- 17 joint DEF có skin (Muzzle không skin). Mai -> Root, đuôi dốc về Tail1/2, đầu 100% Head, chân chia Hip/Ankle/Toe theo chiều cao, tối đa 3 influence.
- Control FK hình tròn (CTL_*, có offset group) điều khiển joint bằng parent constraint; CTL_Main ở sàn. check_rig rỗng.
- Rụt đầu: kéo CTL_Head_M lùi -Z (~0.27) + gập CTL_Neck_M; đầu chui vào mai, không xuyên ra ngoài mai (đã nhìn ở góc cạnh).
- Không dùng IK: chân giữ chạm đất bằng cách bù tịnh tiến CTL_*Hip ngược với Root.

## Anim (Base layer, 30 fps)
- Idle: 49 key-frame 0-48, f48 = f0, lặp liền (Loop Seam báo "seam OK"). Thân lắc roll ±4°, nhún nhẹ, đuôi vẫy trễ pha, đầu rụt nhẹ ở f26-44 (đỉnh f30-34).
- Attack: 0-36. Rụt đầu lấy đà f0-10 (thân hạ, ngả sau), bật đầu ra f10-15, **KHẠC SỎI = frame 15** (đầu ra xa nhất, thân lao tới), hồi f15-36 về pose f0.
- Không có clip di chuyển (đúng GDD).

## File (C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_12_Pebble_Turtle\)
- PebbleTurtle_rig.fv (rig + skin, chưa anim)
- PebbleTurtle_idle.fv / .fbx (0-48)
- PebbleTurtle_attack.fv / .fbx (0-36)
- Script dựng lại: work/infinite_defense/pets/pebble_turtle/rig/ (build_rig.py, skin.py), anim/ (idle.py, attack.py). Ảnh tự kiểm: shots/.

## Chưa chắc / vướng
- FBX xuất bằng export_scene(fbx) trực tiếp, CHƯA mở thử trong Unity: cần kiểm hướng, tỉ lệ (scene đơn vị cm, mesh ~0.9) và có key dịch chuyển trên DEF_Head (rụt đầu) - Generic rig nhận được.
- Chưa playblast MP4 (chỉ ảnh contact sheet). Chưa gọi Director. Skin chưa test từng khớp bằng số đo, chỉ xem mắt: đầu/chân/đuôi ổn ở pose thử; chân trước hơi chạm mai ở đỉnh hip, cần xem thêm nếu xoay mạnh.
- Rụt đầu hơi sâu (đầu gần biến mất ở đỉnh attack), có thể giảm nếu muốn thấy mặt.
- Lỗi gặp: set_skin_weights dùng chỉ số đỉnh toàn scene (lấy từ mesh_data['vertices']), ban đầu ghi nhầm mesh, đã sửa. Lệnh command('frame_selected') không dùng được.
- Không commit/push.
