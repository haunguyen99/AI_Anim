# Pet 18 Tengu Swift (GEK-2362) - báo cáo

Thư mục làm việc: `C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_18_Tengu_Swift\` (Frolvy cổng 9886)

## Kết quả
Rig, skin, Idle, Attack xong; đã xuất đủ 3 FBX. Mới tự kiểm bằng ảnh viewport + đo số (work/infinite_defense/pets/tengu_swift/shots/). Chưa Director, chưa playblast MP4, chưa mở Unity, chưa chép vào Unity.

## Mesh
FBX gốc: 2 object, không xương/skin. Thân (906 đỉnh, 18 mảnh rời, Y lên, mặt +Z, không cần xoay) + quạt Ba Tiêu (141 đỉnh) nằm riêng bên phải nhân vật, không nằm trong tay. Dùng được, không sửa mesh.

## Rig (FK) - 20 joint DEF
Root_M (hông), Spine1, Head, Hair1-2 (mào tóc sau), Tuft1-2 trái/phải (búi tóc hai bên sau), Arm + Hand trái/phải, Leg + Foot trái/phải (guốc theo Foot), Fan1_R + Fan2_R (con của Hand_R), **DEF_Muzzle_M** (con Fan2_R, ở mép trên quạt, không skin). 19 joint có skin, tối đa 4 joint/đỉnh, 20 control + CTL_Main, check_rig sạch.
Skin theo từng mảnh rời (đầu/tóc, tay, chân, thân), xoay thử 11 tư thế: không rách; chỗ kéo nhiều nhất là thân gập mạnh + nghiêng (bụng dưới giãn ~1,6x) và búi tóc xoay 35° (~1,7x), chấp nhận.
Chiều xoay: tay trái hạ = rz âm, tay phải hạ = rz dương; chân ra trước = rx âm.

## Idle - 49 key (0-48), lặp (f48 = f0)
Lơ lửng 12 cm, nhấp nhô 1 nhịp/vòng, thân nghiêng nhẹ; mào tóc, búi tóc, chân, guốc, quạt trễ pha theo thân (thả theo). Tay phải nâng quạt trước ngực, tay trái buông và vẩy nhẹ. Quạt nằm trong nắm tay phải ngay từ Base (đã dời mesh quạt + joint vào nắm tay, không còn offset trong anim).

## Attack - 31 key (0-30)
- 0-5: hạ thân, ngả sau, quạt kéo về sau bên phải.
- 5-14: xoay tròn 360° sang trái (Root ry 0 → 360).
- **16 = BẮN / chém quạt (gắn event ở frame 16)**: thân lệch thêm ~48° sang trái, tay phải đẩy quạt ra trước-trái (mép quạt ~49 cm trước mặt, lệch trái nhờ thân xoay).
- 19-24: giật lại, tắt dần. **30 = đúng tư thế Idle frame 0** (đã đo mép quạt trùng Idle f0).

## File
`tengu_swift_rig.fv` (rig + skin, Base), `tengu_swift_idle.fv`, `tengu_swift_attack.fv`, `raw_*.fbx`
- `Pet_Tengu_Swift.fbx` = Base (xương + 2 mesh + skin, bind pose)
- `Pet_Tengu_Swift_Idle.fbx` (1,6 s), `Pet_Tengu_Swift_Attack.fbx` (1,0 s) = chỉ xương + clip
Script: work/infinite_defense/pets/tengu_swift/ - rig_import, rig_build, rig_skin, skin_check, anim/idle.py, attack.py, make_clips.py, finalize.sh.

## Kiểm FBX
| file | mesh | xương | skin / cluster | BindPose | AnimStack | khác |
|---|---|---|---|---|---|---|
| Base | 2 | 20 | 2 / 19 | có | 0 | Muzzle có |
| Idle | 0 | 20 | 0 | không | 1 | Dummy cùng cấp |
| Attack | 0 | 20 | 0 | không | 1 | Dummy cùng cấp |
Đọc lại bằng file text; chưa chạy Unity batchmode.

## Vướng / chưa chắc
- Model **không có tà áo hay dải ruy-băng đỏ** như GDD; chỉ có 1 quạt (GDD nói 2 tay cầm quạt). Chuỗi overlap làm trên mào tóc, 2 búi tóc, chân, quạt. Nếu cần ruy-băng/quạt thứ hai thì phải có mesh.
- Quạt ngắn nên với tay ngắn, mép quạt chỉ tới ~25 cm sang trái ở frame bắn; chém đọc rõ nhất nhờ thân xoay lệch trái. Nhìn từ trên xuống đã kiểm, chưa xem video.
- Mỗi frame đều có key (không thưa) như các Pet trước.
- Chưa Director/playblast/Unity. Không commit/push.

## Sửa lần 2: quạt lệch ra ngoài tay (user 2026-11-13)
- Gốc lỗi: Base để quạt nằm cạnh nhân vật, trong anim quạt chỉ vào tay nhờ offset phụ. Giờ quạt ở trong nắm tay phải từ bind (kiểm cận cảnh: cán quạt xuyên qua nắm tay).
- Khi xoay control quạt, joint quạt trượt khỏi tay (pivot control lệch joint): thêm `hold_fix` trong anim/idle.py, mỗi frame bù tịnh tiến để cán quạt luôn dính nắm tay (cán–nắm tay lệch <5 cm ở mọi frame, ~1,5 cm lúc bắn).
- Frame bắn vẫn 16; thân xoay lệch trái thêm ~65° lúc chém.
- FILE MESH GỐC: `New_PET\Pet_18_Tengu_Swift\Pet_Tengu_Swift.fbx` đã bị Base xuất ra ghi đè (cùng tên). Mesh gốc còn ở `work/infinite_defense/pets/tengu_swift/Pet_Tengu_Swift.fbx` (rig_import đọc từ đây).
- Bẫy: nhập lại mesh vào scene đã có rig làm joint ma + Base lệch bind vài độ (fbx_add_bindpose báo lỗi). Đã mở lại Frolvy sạch rồi chạy lại toàn bộ script (rig_import, rig_build, rig_skin, build_idle, build_attack, make_clips, finalize.sh); 0 joint ma.

## CHỐT (2026-11-13) - bản cuối
- **Attack 30 frame (1,0 s), frame bắn = 12** (không còn là 16; các đoạn ở trên về nhịp cũ đã thay): 0-3 ngả sau/gồng, 3-9 xoay 360° sang trái, 12 chém quạt, 12-30 quá đà rồi hồi về mượt (Catmull-Rom, không gấp), 30 = Idle frame 0. Đã xóa 684 key thừa ngoài 0-30.
- Idle 48 frame lặp, không đổi. Quạt nằm trong nắm tay phải từ Base.
- Đã xuất lại đủ 3 FBX: Base (2 mesh, 20 xương, 1 skin + 19 cluster, BindPose, 0 AnimationStack, x100), Idle (1,6 s) và Attack (1,0 s) chỉ xương + clip, có Dummy cùng cấp, DEF_Muzzle_M có trong cả 3, 0 joint ma. Chưa chạy Unity batchmode, chưa chép vào Unity.
- File .fv: rig / idle / attack trong thư mục Pet_18. Base có sai số xoay vài phần nghìn độ được làm tròn bằng ghost_rename SNAP_DEG.
