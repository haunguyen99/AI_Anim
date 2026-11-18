# Pet 19 Kabuto Striker (GEK-2363) - báo cáo

## Mesh
- FBX gốc không có xương/skin: **một mảnh hàn liền** (539 đỉnh), đã đứng sẵn (Y lên, mặt +Z), không cần xoay.
- Hình: thân tròn + mai giáp, sừng chữ Y, 2 giáp vai, váy giáp (trước/sau/2 bên), **4 chân ngắn** bên dưới (không có 6 chân như gợi ý brief). Rig theo đúng mesh có.
- Mesh gốc giữ làm `Pet_Kabuto_Striker_src.fbx`.

## Rig (cổng 9887)
- 32 joint (19 DEF có skin + 12 joint đầu mút + Muzzle): Root_M (hông), Spine1, Chest, Neck, Head; sừng 2 đốt mỗi bên (Horn1/2); giáp vai (Sode) L/R; váy trước, sau, 2 bên; chân trước/sau L/R. Muzzle ở giữa đầu 2 sừng, con của Head, không skin.
- 20 control FK (CTL_*, vòng tròn, có group offset), CTL_Main ở sàn. check_rig rỗng.
- Skin: thân chia theo chiều cao Root→Spine→Chest→Neck→Head (vùng đầu chuyển mềm để bậc giáp không bị xé), sừng theo đường cong, váy theo hướng quanh thân, chân theo khoảng cách, làm mịn 2 lượt, tối đa 4 influence. Xoay thử từng khớp ~25° xem mắt ổn.
- Số đo: Root xoay 15° → mọi cạnh giữ nguyên (1.0). Đầu/ngực xoay mạnh (≥20°) vẫn có vài cạnh nhỏ ở mép bậc giáp giãn/co (đầu x25: tối đa 1.6x; ngực x20: có cạnh co mạnh ở sau lưng). Mắt thấy ổn ở pose attack thật.
- Script: `rig/build_rig.py`, `rig/skin.py`, `rig/skin_test.py`.

## Anim (30 fps, bay lơ lửng hover 12 cm, không tiếp đất)
- **Idle: 48 frame, lặp liền (f48 = f0)**, mọi chuyển động theo chu kỳ nguyên: nhún nhẹ, thở, sừng rung nhẹ thị uy (4 nhịp/loop), giáp vai/váy/chân thả trễ pha.
- **Attack: 30 frame**, hạ thấp + cúi đầu (sừng chĩa trước) f0-8, **húc từ dưới lên f8-12**, **FRAME BẮN = 12** (đầu/sừng hất lên cao nhất, thân lao tới), theo đà f12-22, **f30 = Idle f0**. Key mỗi frame.
- Script: `anim/idle.py`, `anim/attack.py`, `anim/make_clips.py`. Ảnh tự kiểm: `shots/att1.png` (8 frame attack nhìn ngang).

## File (C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_19_Kabuto_Striker\)
- `kabuto_striker_rig.fv`, `kabuto_striker_idle.fv`, `kabuto_striker_attack.fv`
- `Pet_Kabuto_Striker.fbx` (Base), `Pet_Kabuto_Striker_Idle.fbx`, `Pet_Kabuto_Striker_Attack.fbx`; `raw_*.fbx` là bản trung gian từ Frolvy.

## Kiểm FBX
- Base: xương + mesh + skin (19 cluster), có BindPose, 0 AnimationStack, xuất ở bind (control = 0), UnitScale 100.
- Idle (1.6 s = 48 f), Attack (1.0 s = 30 f): chỉ xương + 1 take, 0 mesh, có Dummy cùng cấp, tên xương trùng Base, có DEF_Muzzle_M.
- Chưa chép vào Unity, chưa mở thử trong Unity.

## Chưa chắc / vướng
- Mesh không có 6 chân, chỉ 4 chân ngắn: nếu cần 6 chân phải bổ sung mesh.
- Đầu = cả mái giáp (không có mặt tách riêng), nên "húc" là cả mái + sừng xoay cùng thân.
- Chưa playblast MP4, chưa gọi Director, chưa kiểm xoắn bằng góc thế giới theo frame (chỉ xem ảnh 8 frame attack và seam idle theo công thức). Idle chưa xem ảnh.
- Muzzle nằm giữa 2 đầu sừng, không phải đầu mút một sừng (đúng "sừng chữ Y").
- Không commit/push, không chép Unity.
