# Pet 14 Lucky Neko (GEK-2358) - báo cáo RIG (chưa anim, chưa xuất FBX)

File rig: `C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_14_Lucky_Neko\lucky_neko_rig.fv`
Script dựng lại: `work/infinite_defense/pets/lucky_neko/` (rig_import.py → rig_build.py → rig_skin.py → skin_check.py → save_rig.py).

## Mesh
- 3 mesh, mét, Y lên, mặt +Z, cao 0,53 m, không có xương/skin sẵn. Dùng được, không sửa.
  - `Pet_lucky_neko` (626 đỉnh): thân + tay + chân + đuôi (1 mảnh), đầu + tai + chuông cổ, kính (mảnh riêng).
  - `.001` hũ tiền (dây quai là mảnh riêng), `.002` đồng xu (28 đỉnh, phẳng).
- **Hũ tiền và đồng xu nằm rời bên cạnh nhân vật**, không ở lưng / trên tay: hũ ở x -0,41, đồng xu ở x +0,47 (cạnh bàn tay trái nhân vật). Mình giữ nguyên chỗ, chưa dời.
- Đuôi trong model chỉ là cọng thẳng ngắn (z -0,08 → -0,22), chưa có hình dấu hỏi sẵn: hình dấu hỏi sẽ do anim uốn 3 đốt.

## Rig (kiểu FK như Night Bat)
- 32 joint DEF, 32 control (CTL_*) (25 ban đầu + chuông cổ + 6 đốt tua tua hũ, thêm 2026-11-14), check_rig sạch, Root_M là hông.
- Thân: Root, Spine1, Head. Tai 2 đốt x2 (đốt gốc ở chân tai, nghiêng vào trong theo mesh, sửa 2026-11-14). Tay mỗi bên Shoulder-Elbow-Wrist. Chân mỗi bên Hip-Ankle-Toes. Đuôi Tail1-2-3 (dài hơn đủ để uốn dấu hỏi).
- Chuông cổ: `DEF_Bell_M` (con của Spine1, tâm ở gốc chuông), quả chuông skin 100% vào nó, rìa hòa vào thân.
- Tua tua hũ tiền: 2 dây, mỗi dây 3 đốt (`DEF_TasselA1..3_M`, `DEF_TasselB1..3_M`), con của Jar_M, gốc dây hòa vào hũ.
- Hũ tiền: `DEF_Jar_M` (con của Root, 100% hũ). Đồng xu: `DEF_Coin_L` (con của Wrist_L, 100% đồng xu).
- **Socket Muzzle = `DEF_Muzzle_M`**, con của DEF_Coin_L, ở tâm đồng xu (0,468 ; 0,126 ; 0,03), không có skin / control.
- Tay vẫy là tay **+X (trái của nhân vật, bên phải màn hình)**, vì đồng xu nằm bên đó. GDD ghi "tay phải": đây là phải theo góc nhìn người xem. Cần đổi bên thì báo.

## Skin
- Viết weight theo luật từng mảnh: đầu + kính + chuông 100% Head, tai theo Ear1/Ear2 hòa vào Head, tay theo chuỗi vai/khuỷu/cổ tay, chân theo Root→Hip→Ankle→Toes, đuôi theo chuỗi 3 đốt, thân Root→Spine1→Head. Tối đa 3 joint/đỉnh, chỉ DEF, đã chuẩn hóa.
- Bind khi mọi control = 0.
- Thử 29 pose xoay khớp bằng skin_check.py: đuôi, cổ tay, đồng xu, hũ sạch; đầu/tai/vai/khuỷu/chân còn 0-6 cạnh co giãn ~2 lần (nhỏ, ở nách, gốc tai, chân nhỏ, phần cổ chìm trong đầu).

## Chỗ yếu / chưa chắc
- Nách khi giơ tay lên cao (vai xoay >50°) hơi giãn ×2.
- Chân rất ngắn (bàn chân sát thân), Hip xoay mạnh làm bàn chân nhỏ bị bóp nhẹ.
- Hũ / đồng xu đang rời thân: nếu để nguyên, xoay Root/Spine1 thì hũ và đồng xu quay quanh xa tâm. Cần chốt: dời hũ lên lưng và đồng xu vào bàn tay trong mesh (ở file nguồn) hay giữ rời như bản Unity.
- Chưa dùng IK (rig FK); Frolvy vẫn mở ở cổng 9891.

## Kiểm vùng ảnh hưởng (2026-11-14)
- Kiểm từng joint: vùng đỉnh, đối xứng L/R, không lẫn bên. Sửa tai: joint tai cũ nghiêng ra ngoài ngược mesh và chỉ 10 đỉnh ăn tai → đặt lại joint theo gốc/giữa tai, tách đỉnh tai theo hình tấm tai (gốc → mũi), tai xoay như một tấm.
- Dựng lại rig sạch (scene mới, không joint ma). 27 đỉnh hông/chân người dùng chỉnh tay được giữ nguyên.
- Script: skin_regions.py (vùng từng joint), plotw.py (bản đồ weight), skin_check.py.

## Pose idle (2026-11-14, theo ảnh ref Tripo + 2 ảnh người dùng gửi)
- File: `lucky_neko_idle_pose.fv` (chỉ key frame 0, chưa có chuyển động). Script: `anim/idle_pose.py` (dựng pose, giải tay/đồng xu bằng số) + `anim/idle_pose_save.py` (key + lưu).
- (Cập nhật: nhân vật quay chính diện, đồng xu scale 0.66 bằng control CTL_Coin_L, tâm 0.15/0.13/0.165.)
- Tay PHẢI nhân vật (-X) giơ vẫy cạnh má; tay TRÁI cầm đồng xu (đồng xu đứng trước hông phải, mặt hướng trước, Muzzle đi theo). Hũ tiền ở lưng (đúng ảnh nghiêng), đuôi thò ra sau dưới hũ, đầu xoay nhẹ về phía tay giơ + cúi chút, thân chồm nhẹ, hover 12 cm, chân thả.
- Bẫy Frolvy: `rotate` chỉ ăn trên curve đã có key → key 0 trước rồi mới ghi pose và key lại; đừng đổi frame khi đang giải pose trong scene đã có key.

## Idle (2026-11-14) — `lucky_neko_idle.fv`, 48 frame lặp (f0 = f48), chưa qua Director, chưa xuất FBX
- Từ pose idle người dùng chỉnh (frame 0 giữ nguyên, mọi offset = 0 ở f0/f48). Script: `anim/idle.py` (base pose ở `anim/base_pose.json`), kiểm `anim/idle_check.py`, contact sheet `anim/sheet.py`.
- Tay phải vẫy 4 nhịp/vòng (12F/nhịp): khuỷu ±16°, cổ tay ±30° trễ pha; tay trái giữ xu bồng nhẹ theo thân; thân hover bồng 2 nhịp (±1,1 cm) + đưa nhẹ 1 nhịp; cột sống/đầu/chân/đuôi/chuông/tua tua/hũ trễ pha sau thân; tai giật lệch nhịp; đuôi dấu hỏi lắc 1 nhịp, 3 đốt trễ dần.
- Kiểm: seam f0 = f48 sai số 0; bước xoay lớn nhất 17°/F (cổ tay, đúng nhịp vẫy).

## Attack (2026-11-14, v2) — `lucky_neko_attack.fv`, 30 frame, **BẮN = frame 10** (gắn event, socket `DEF_Muzzle_M`), f30 = idle frame 0. Chưa qua Director, chưa xuất FBX.
- v1 (tay thọc ra trước) bị trả: hành động là HẤT đồng xu đi. v2 ở trên, bản v1 là `lucky_neko_attack_prev.fv`.
- v2.1 (2026-11-14): bản v2 đầu tay trái KHÔNG animate (giải IK bị kẹt) và đồng xu lún thấp; sửa: key tay trái trực tiếp (Euler trong tầm với), đồng xu đi theo tay thật, chỉ hạ ~3 cm.
- 0-7 lấy đà: thân hạ thấp ~2 cm, ngả ra sau, tay trái hạ nhẹ kéo đồng xu về sát bụng, tay phải giơ cao ra sau cân bằng, đuôi cuộn, tai cụp.
- 7-10 hất: tay trái quét từ dưới LÊN trên (khoảng 14 cm trong 3 frame), thân vươn lên, đầu ngước theo; đồng xu rời tay ở f10, bay vút lên trước ~1,3 m và xoay 4 vòng, ẩn khi ở xa (f15); đồng xu mới hiện lại trong tay f19-27 (phồng nhẹ rồi về cỡ chuẩn) để nối idle.
- 10-17 follow-through: tay vượt đà rồi hồi, tai/đuôi/chuông/tua tua/hũ/chân trễ pha tắt dần; 17-30 về đúng idle f0 (sai số < 0,0001).
- Lưu ý khi xuất: đồng xu bay đi được key bằng translate + scale (ẩn bằng scale 0,02); nếu muốn đạn là VFX riêng thì giữ đồng xu trên tay đứng yên sau f10 (báo mình đổi). Góc xoay đồng xu nhảy tới 286°/frame ở rz (tách Euler khi xoay nhanh), cần kiểm lúc xuất FBX.
- Script: `anim/attack.py`, `anim/attack_check.py`, `anim/sheet.py`.

## CHỐT (2026-11-14) — đã xuất FBX, chưa chép vào Unity
- Thư mục `C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_14_Lucky_Neko\`: `Pet_Lucky_Neko.fbx` (Base: 32 xương, 3 mesh, skin, BindPose, 0 clip, bind pose, UnitScale 100), `Pet_Lucky_Neko_Idle.fbx` (48F, 1,6 s), `Pet_Lucky_Neko_Attack.fbx` (30F, 1,0 s, bắn f10): chỉ xương + clip, 0 mesh, có Dummy cùng cấp, tên xương trùng Base. `.fv` giữ: `lucky_neko_rig.fv`, `lucky_neko_idle.fv`, `lucky_neko_attack.fv`. `CHOT.txt` do pet_chot.py ghi (kiểm đạt).
- File mesh gốc `Pet_Lucky_Neko.fbx` của người dùng đã bị ghi đè bằng bản Base (cùng tên theo brief); bản gốc giống bản đang ở Unity.
- Quy trình: `anim/export_raw.py` (bake DEF + raw_*.fbx từng scene) → `finalize.sh` (fbx_ascii_keep → pet_fbx_finalize → fbx_unity_bind/strip hoặc fbx_add_sibling). Không có joint ma (rig dựng 1 lần trong scene sạch). Chưa thử trong Unity batchmode.
- Lưu ý khi dùng: đồng xu trên tay scale 0,65 chỉ nằm trong key anim (Base để cỡ gốc 25 cm); Attack key đồng xu bay đi bằng translate + scale (ẩn scale 0,02 rồi hiện lại).

## Sửa sau chốt (2026-11-14): đồng xu ĐỨNG YÊN Ở TAY, không bay ra
- Attack dựng lại: tay trái vẫn lấy đà thấp rồi hất lên (BẮN = f10), nhưng đồng xu đi theo bàn tay suốt clip, đứng thẳng mặt trước, không xoay, không scale, không rời tay. Viên đạn là VFX gắn ở `DEF_Muzzle_M` tại f10. Thay `lucky_neko_attack.fv` và `Pet_Lucky_Neko_Attack.fbx` (kiểm đạt, CHOT.txt giữ nguyên); Base + Idle không đổi. Các ghi chú "đồng xu bay đi / scale ẩn" ở trên không còn đúng.
