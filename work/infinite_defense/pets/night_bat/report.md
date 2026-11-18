# Pet 15 Night Bat (GEK-2359) - báo cáo (CHỐT 2026-11-13)

Thư mục: `C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_15_Night_Bat\`

## File chốt
- `Pet_Night_Bat.fbx` = Base: 1 mesh, 17 xương, 16 cluster skin, có BindPose, 0 clip, đúng bind pose, UnitScale 100.
- `Pet_Night_Bat_Idle.fbx` (1,6 s, 48 frame lặp) và `Pet_Night_Bat_Attack.fbx` (1,0 s, 30 frame): chỉ xương + 1 clip, 0 mesh, có Dummy cùng cấp, tên xương trùng Base. Socket bắn `DEF_Muzzle_M` (con của DEF_Jaw_M).
- `night_bat_rig.fv` (rig + skin người dùng tự chỉnh), `night_bat_idle.fv`, `night_bat_attack.fv`. `CHOT.txt` do pet_chot.py ghi (kiểm FBX đạt).
- Chưa chép vào Unity.

## Rig
- 17 joint DEF: Root_M (hông), Spine1, Head, Jaw, Muzzle (không skin), tai 2 đốt x2, cánh 4 đốt x2. 17 control FK (CTL_*). Mesh nguyên bản 996 đỉnh, xoay -90° quanh X (Y lên, mặt +Z).
- Mesh hàn liền tai-cánh nên skin không tách hẳn được màng nối; đã thử tách tai ra mesh riêng (rách mép) nên bỏ. Skin cuối do người dùng chỉnh tay trong Frolvy.

## Anim
- Idle 48F: lơ lửng 12 cm, vỗ cánh nhanh 6 nhịp/vòng (trễ pha 4 đốt), tai xoay dò lệch nhịp, đầu nhìn quanh nhẹ.
- Attack 30F, **bắn = frame 13**: gập cánh + ngửa cổ (0-8, cánh run trước sau) -> bung cánh, há miệng, thân lao tới (13) -> cánh quất ra sau rồi đu trước sau tắt dần (14-29) -> frame 30 = Idle frame 0.

## Bẫy Frolvy rút ra
- Bind skin phải ở pose 0 (control posed lúc bind = cánh dính mặt); xóa hết key channel làm channel chết; dựng lại rig để lại joint ma. Xem memory frolvy-bind-pose-and-empty-curve.
- Script dựng lại: `work/infinite_defense/pets/night_bat/` (rig_*.py, anim/, skin_check.py, finalize.sh).
