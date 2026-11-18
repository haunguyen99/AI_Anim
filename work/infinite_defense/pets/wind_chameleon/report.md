# Pet 16 Wind Chameleon (GEK-2360) - báo cáo

## Mesh
- FBX gốc không có xương/skin: 2 mảnh (thân + lưỡi). Nằm nghiêng nên xoay -90° quanh X rồi freeze (Y lên, mặt về +Z). Cao ~0,77 m, đuôi cuộn xoắn lên trên, lưỡi đã thè ra phía trước.

## Rig (cổng 9884, FK như Tiny Chick)
- 38 joint DEF: Root_M (hông) > Spine1 > Chest > Neck > Head; Crest (mào), Jaw (hàm), Cheek L/R (má, phồng bằng scale), Eye L/R, lưỡi 4 đốt (Tongue1-4) + **DEF_Muzzle_M ở đầu lưỡi** (không skin); đuôi 10 đốt (Tail1-10, cuộn xoắn); 4 chân x3 đốt (Hip, Ankle, Toes). 37 joint có skin, tối đa 4 influence.
- 38 control FK (CTL_*) điều khiển bằng parent constraint, CTL_Main ở sàn. Không dùng IK.
- Skin theo vùng + làm mịn theo cạnh mesh: má/mắt/hàm/mào theo khoảng cách, chân theo độ cao, thân theo trục sống, đuôi theo trục đuôi (gai lưng không bị kéo theo đuôi), lưỡi theo chiều dài. Đã xoay thử đuôi, má, hàm, lưỡi, chân: sạch ở biên độ clip dùng. Đuôi xoay mạnh (~100° cộng dồn) mới thấy méo.

## Anim (Base layer, 30 fps)
- **Idle: 48 frame, lặp (f0 = f48)**, đã đặt chế độ lặp. Lơ lửng 12 cm, bồng bềnh 1 nhịp/vòng; sóng đuôi chạy dọc 10 đốt (trễ pha), thở nhẹ ở ngực, đầu nhìn quanh chậm, hai mắt đảo độc lập, chân thả lủng lẳng trễ pha. Lưỡi thụt hẳn vào miệng.
- **Attack: 30 frame**. f0 lơ lửng · f4-8 ngả ra sau, má phồng dần, mắt chụm nhìn mục tiêu, chân co · f8-11 má phồng cực đại (đỉnh f10-11) · f12 má xẹp, hàm mở · **f13 = BẮN (gắn event ở frame 13)**: lưỡi vụt ra hết cỡ (dài hơn bind ~22%), thân lao tới ~8 cm, đuôi quất · f15-22 thu lưỡi về, hàm khép · f30 về đúng pose Idle f0 (nối liền Idle).
- Không có clip di chuyển (đúng GDD). Đổi màu thân là shader/VFX, không có trong anim.

## File (C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_16_Wind_Chameleon\)
- `Pet_Wind_Chameleon.fbx` = **Base**: xương + mesh + skin, bind pose (Root ty 0,20, mọi xoay 0), BindPose có, 2 mesh, 0 AnimationStack, UnitScale 100.
- `Pet_Wind_Chameleon_Idle.fbx` (0-48, 1,6 s) · `Pet_Wind_Chameleon_Attack.fbx` (0-30, 1,0 s): chỉ xương + clip, 0 mesh/deformer/material, có Null `Dummy` cùng cấp, 38 xương trùng tên Base, take tên Idle / Attack.
- Mesh gốc giữ ở `Pet_Wind_Chameleon_src.fbx`. File Frolvy: `wind_chameleon_rig.fv`, `_idle.fv`, `_attack.fv`. `raw_*.fbx` là bản thô trước khi qua công cụ.
- Script: work/infinite_defense/pets/wind_chameleon/rig/ (build_rig, skin, imp), anim/ (idle, attack, make_clips, shotsheet). Ảnh tự kiểm: shots/.
- Chưa chép vào Unity (theo brief).

## Chưa chắc / vướng
- Chưa mở FBX trong Unity (chưa chạy batchmode), chưa playblast MP4, chưa gọi Director. Tự kiểm bằng ảnh contact sheet góc cạnh + trước.
- Frolvy 0.9.59 lỗi: `set_key` ở frame mới lưu giá trị nội suy thay vì giá trị vừa đặt (mất ~30 phút dò); đã đổi script thành 2 lượt. Ghi vào knowledge `pet_chameleon_wind.md`.
- Dựng rig 3 lần trong cùng scene để lại bản "ma": FBX xuất ra có 3 bộ DEF_Root_M và check_rig báo 34 constraint mồ côi. FBX cuối đã lọc đúng bản sống (sửa `tools/fbx_ascii_keep.py`: giữ bản cuối khi trùng tên root). Mở lại .fv sẽ còn constraint mồ côi, vô hại nhưng nên dựng lại từ script nếu cần sạch.
- Muzzle ở đầu lưỡi: khi lưỡi thụt (Idle) nó nằm trong miệng; lúc bắn (f13) ra ~65-75 cm trước hông. Nếu team muốn socket cố định ở miệng, báo để thêm joint.
- Đuôi cuộn xoắn dính gai lưng trong không gian: skin đã tách, nhưng đuôi xoay mạnh vẫn có thể kéo mép xoắn nhẹ.
- Không commit/push.

## Sửa skin đuôi (2026-11-12, theo góp ý)
- Lỗi: thành trong của đoạn đuôi cong (gần gốc đuôi) bị gán nhầm cho các xương đầu xoắn vì gần về không gian, nên khi đuôi xoay thì thành đó bị kéo giãn như tấm giấy.
- Sửa: weight đuôi tính theo quãng đường đo trên bề mặt mesh từ gốc đuôi (không theo khoảng cách thẳng tới xương). Đo lại: chỉ còn 1 cạnh lệch (không thuộc đuôi), trước đó 53 cạnh. Xoay thử từng đốt đuôi 30° sạch.
- Dựng lại rig sạch trong scene Frolvy mới (hết bản "ma"), xuất lại cả 3 FBX; bản v1 để ở thư mục old_v1. File Frolvy mới: `wind_chameleon_rig_v3.fv`, `_idle_v3.fv`, `_attack_v3.fv` (file cũ không ghi đè được vì đang mở).

## Cập nhật 2026-11-12 (sau góp ý)
- Idle: hàm khép (rx -14, mesh gốc có miệng hé sẵn), lưỡi thụt sâu hơn (-0.26) nên không còn thấy đầu lưỡi. Attack: hàm há từ f8 (nhẹ), há rộng nhất f13 (khoảng +34° so với bind), khép lại đến f26; lưỡi bắn ra đúng độ dài cũ.
- Attack: chân trước và chân sau có trễ pha từng đốt, xoè ngang, vẫy tắt dần sau khi bắn; f30 = Idle f0.
- Skin: vùng hàm rộng hơn (cằm cùng chuyển động), skin đuôi theo quãng đường bề mặt, Tail2/3 không kéo hông.
- File Frolvy: wind_chameleon_rig.fv / _idle.fv / _attack.fv (bản cuối, root + control hiện). FBX 3 file đã chép vào Unity New_Pet/Pet_Wind_Chameleon (user duyệt chép 2026-11-12).
