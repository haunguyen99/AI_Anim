# Báo cáo GEK-2355 — Pet 11 Mecha Pup (rig + Idle + Attack)

Thư mục làm việc: `C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_11_Mecha_Pup\`

## Kết quả
- Rig xong, skin xong, 2 clip xong, đã xuất FBX. Chưa qua Director, chưa xem lại bằng playblast (chỉ tự kiểm bằng ảnh viewport + số đo).
- File: `mecha_pup.fv` (rig sạch) · `mecha_pup_idle.fv` · `mecha_pup_attack.fv` · `Pet_Mecha_Pup_Idle.fbx` · `Pet_Mecha_Pup_Attack.fbx`.
- Script dựng lại được ở `work/infinite_defense/pets/mecha_pup/` (`rig/make_fit.py`, `rig/skin.py`, `anim/idle.py`, `anim/attack.py`).

## Mesh
- FBX gốc chỉ có mesh: không xương, không skin. 1606 đỉnh, 10 mảnh rời, cao ~1,1 m (đơn vị mét), mặt nhìn +Z.
- Dùng được, không cần sửa mesh.

## Rig
- 30 joint fit → 46 joint DEF, 49 control. Root_M là hông (luật rig game), không helper/twist.
- Joint: Root, Spine1, Chest, Neck, Head, HeadEnd; tai 2 bên (2 đốt); balo; ăng-ten (Ant1, Ant2, Dish, **Muzzle** ở mép trên đĩa); đuôi (2 đốt); chân trước (Shoulder, Elbow, Wrist, FToes); chân sau (Hip, Knee, Ankle, Toes, Heel, 2 mép bàn).
- Socket bắn đạn = joint `Muzzle_M` (con của Dish_M, đầu ăng-ten). Joint cuối nên không có DEF skin; muốn gắn event/VFX thì lấy vị trí DEF_Dish_M + offset, hoặc xuất Muzzle thành joint thật nếu team cần (xem "Chưa chắc").
- Chân trước/sau: IK (có pole), thả lủng lẳng theo thân. Cột sống: FK.
- Kiểm: DEF khớp fit, check_rig rỗng, kéo thử IK/FK chạy.

## Skin
- Viết weight theo luật từng mảnh: mũ phi hành gia (đầu + mặt) 100% Head; balo 100% Backpack; đuôi và ăng-ten theo chuỗi; tai theo chuỗi tai; thân + 4 chân: chia theo vùng (đùi sau / đùi trước / thân giữa), làm mịn 2 lượt.
- Tối đa 4 joint/đỉnh, không joint ngoài DEF. Thử xoay 22 khớp: đầu, đuôi, ăng-ten sạch; chân/thân còn vài cạnh co giãn 2–3 lần (nhỏ), một cạnh chân sau co 0,12 khi gập gối ngược.
- Tai: gốc tai co còn ~0,3 khi xoay 30°.

## Lưu ý chung (người dùng, 2026-11-11): mọi Pet là nhân vật BAY LƠ LỬNG
- Không có tiếp xúc đất: không khoá chân xuống đất, không ép/tiếp đất. Thân lơ lửng cách đất ~12 cm, chân/tay thả lủng lẳng, trễ theo thân (overlap).
- Idle + Attack đã làm lại theo hướng này (bản đầu đặt chân dính đất, đã bỏ).

## Idle — 48 frame, lặp (frame 0 = frame 48)
- Bồng bềnh lên xuống 2 nhịp/vòng (biên 3 cm quanh độ cao lơ lửng), hơi trôi tới lui; 4 chân thả lủng lẳng, đạp nhẹ, trễ pha sau thân; đuôi ngoáy 1 vòng/48 frame, ăng-ten lắc 3 vòng/48 frame, tai vỗ theo nhịp.

## Attack — 24 frame
- 0 lơ lửng · 7 lấy đà (lùi + hạ nhẹ, ăng-ten kéo ngược) · 11 chồm tới · **9 BẮN (gắn event ở frame 9)**: lao tới ~12 cm, thân ngẩng ~22°, 2 chân trước giơ cao, chân sau kéo lê phía sau, ăng-ten vụt ra trước · 16 giật lại · 19 giảm đà · 23 nhún nhẹ · 29 ổn định · 36 về đúng tư thế Idle frame 0 (nối liền Idle).
- Chớp điện / đạn là VFX, không có trong anim.

## Vướng / chưa chắc
- Bộ joint trong scene lúc nhận không đặt đúng cho Build (tạo bằng create_joint, không phải fit skeleton nên Build bị từ chối); mình nạp lại thành fit bằng `.fvfit`. Bàn chân sau trong bảng cũ chỉ ngược (mũi chân hướng ra sau) — đã sửa cho mũi hướng về +Z.
- Chưa chắc: FBX là Generic với skeleton DEF_* (tên đổi). Team Unity cần tên xương riêng thì báo. Muzzle không xuất thành xương (joint cuối bị lọc khi skin, nhưng vẫn có trong FBX nếu thuộc cây DEF_Root_M — chưa kiểm trong Unity).
- Chưa nhập FBX vào Unity/Studio để so lệch tư thế.
- Chưa chạy Director; chưa playblast. Cú chồm của Attack là bản đầu, còn thô (chân trước chưa có xoay bàn chân).

## Lỗi công cụ / bẫy trong phiên con Frolvy (cho các Pet sau)
1. `api.move` là tọa độ **cục bộ** (trong không gian cha). Đặt joint theo tọa độ thế giới mà dùng nó thì joint lệch (mình đã làm sai một lần, mất ~10 phút).
2. `set_frame(0)` khi đang ở frame 0 không tính lại: key đầu tiên ở frame 0 ra pose 0. Cách xử: `set_frame(1)` rồi `set_frame(0)`, key lại frame 0 sau khi đã có curve.
3. `api.open_scene` trả False trong phiên con (và `new_scene` không đổi scene): không mở lại file được, nên dựng clip bằng script rồi lưu/xuất cùng lúc.
4. `save_scene` sang đường dẫn file đã có (khác file đang mở) trả False: lưu tên mới rồi `mv` bên ngoài.
5. `R.match_switches` được gọi trong `auto_rig.build` nhưng không tồn tại trong `frolvy_rig_tools.py` → `A.build` chết giữa chừng; `after_rebuild` cũng chết ở bước ngón cái (pet không có ngón). Mình chạy tay từng bước còn lại.
6. Frolvy chỉ cho script ghi file ở `Documents\Frolvy` và `%TEMP%`; ghi ra ngoài phải qua API (save_scene, export_scene).
7. `delete_key` cần frame **số nguyên**.
8. Chụp viewport: thêm `tools/frolvy_shot.py <cổng> <png>` (mới). Camera `side`: `ow` ~3,2 vừa với pet, dời bằng `api.move('side', 100, 0.45, 0)`.
