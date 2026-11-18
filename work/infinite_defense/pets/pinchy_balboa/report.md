# Pet 17 Pinchy Balboa (GEK-2361) - báo cáo

## Mesh
- FBX gốc không có xương/skin: 1 mesh, 5 mảnh rời (thân + 6 chân + 2 cuống tay, 2 găng, 2 đuôi băng đô). Đã Y-up, mặt +Z, không cần xoay. Cỡ ~1.1 x 0.62. Không cần tách thêm (các mảnh rời nhau, không hàn liền như Night Bat).
- Bản mesh gốc cất ở `...\Pet_17_Pinchy_Balboa\_orig\` (file Base mới ghi đè tên cũ).

## Rig (cổng 9885)
- 25 joint: Root_M (hông), Head_M, 2 đuôi băng đô x 2 đốt (BandA1/2, BandB1/2), mỗi tay Arm1/Arm2/Glove, 6 chân x (hông + mũi), Muzzle_M (con của DEF_Glove_R, đầu găng phải, không skin). Phải = -X, trái = +X.
- 24 joint DEF có skin, tối đa 4 influence. Găng 100% Glove (pha Arm2 ở gốc), cuống tay chia Root/Arm1/Arm2, chân chia hông/mũi theo chiều cao, đầu + băng đô pha Root->Head.
- Control FK hình tròn (CTL_*), CTL_Main ở sàn; check_rig rỗng. Đã thử xoay mạnh đầu/tay/chân/đuôi: skin không rách.

## Anim (30 fps, bay lơ lửng hover 12 cm)
- Idle: 0-48, f48 = f0, lặp liền. TƯ THẾ GỐC = THẾ THỦ QUYỀN ANH (2 găng co lại phía trước mặt, không phải T-pose). Thân nhấp 2 nhịp, lắc trọng tâm trái-phải 1 chu kỳ, găng canh thủ đung đưa trễ pha, 6 chân đổi bên (trái/phải ngược pha), đuôi băng đô trễ.
- Attack: 0-30. Lắc né 2 bên (f0-8), lấy đà găng phải ra sau + vặn thân (f11), móc ra, **ĐẤM = frame 16** (găng phải ra trước nhất, thân lao tới), hồi, f30 = pose idle f0.

## File (C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa\)
- Pet_Pinchy_Balboa.fbx (Base, bind pose), Pet_Pinchy_Balboa_Idle.fbx (48F), Pet_Pinchy_Balboa_Attack.fbx (30F)
- pinchy_idle_new.fv, pinchy_attack_new.fv (scene có anim), raw_*.fbx (thô từ Frolvy)
- Script: work/infinite_defense/pets/pinchy_balboa/ (rig_build.py, rig_skin.py, anim/idle.py, attack.py, make_clips.py, run_all.py, finalize.sh). Ảnh kiểm: shots/.

## Kiểm FBX (đọc file)
- Base: 1 mesh, 1 BindPose, 25 deformer (1 skin + 24 cluster), 0 AnimationStack, xuất ở bind (control = 0).
- Idle/Attack: 0 mesh, 0 deformer, 1 AnimationStack (take Idle 1.6s / Attack 1.0s), có Dummy cùng cấp, DEF_Muzzle_M có.
- Chưa mở thử trong Unity, chưa chép vào Unity (chờ duyệt).

## Chưa chắc
- Chưa playblast MP4, chưa gọi Director, chỉ xem contact sheet mặt trước (chưa xem cạnh/trên kỹ). Biên độ tay trong idle hơi to, có thể giảm.
- Chưa có file .fv "chỉ rig" sạch (scene hiện giữ key Base); cần thì dựng từ rig_build + rig_skin.
- "Phải" hiểu là -X khi nhìn từ sau lưng pet (mặt +Z); nếu game cần ngược lại thì đổi Muzzle sang Glove_L.
- Không commit/push.

## Cập nhật 2026-11-13 (vòng sửa)
- Rig dựng lại: joint vai Arm1/Arm2 dời ra mép thân (x=0.27/0.335) để cuống tay không kéo rách thân khi thủ; weight cuống tay mượt hơn.
- Idle: biên độ overlap tay/găng giảm khoảng một nửa. File xem: pinchy_idle_v2.fv (joint + control đang bật).
- Luật mới: chỉ xuất FBX khi người dùng nói "chốt". 3 FBX trong thư mục Pet_17 hiện CŨ/không đồng bộ (Base cũ, Idle/Attack nửa mới); sẽ xuất lại đủ bộ khi chốt. Lưu ý lúc chốt: Base cần snap_bind.py + sửa fbx_unity_bind (đang báo "bone has rotation" vì joint có xoay nhỏ).
- Vòng 3 (2026-11-13): tay vẫn tách vì đầu cuống tay (mix Arm1/Arm2) chạm găng (100% Arm2) + cuống xoay 45° quanh 1 điểm → hở. Sửa: weight cuống chuyển Arm1->Arm2 xong trước chỗ găng bắt đầu, vai có vùng bo mượt theo tay (không còn khe), thế thủ nhẹ góc hơn (35/45), biên độ lắc thân/đầu/tay giảm thêm (tay ~1/3 bản đầu). File: pinchy_idle_v3.fv.
- Vòng 4: file rig `pinchy_rig.fv` (mọi control 0, joint/control khớp mesh, đã đo 0 lệch). Lỗi trước: dựng lại rig cùng scene, đường key cũ của node đã xóa gắn lại theo tên làm nhóm control/joint lệch chỗ (~15 cm). rig_build.py giờ dựng bằng tên tạm `__t`, đổi tên sau rồi xóa key joint + key 0 control. Các .fv anim cũ (idle_v3, *_new) dựng trên rig lệch, cần dựng lại anim trên rig này.
- Vòng 5: xương tay sửa theo góp ý vẽ (4 chấm trên trục tay): Arm1 x=.226 (mép thân), Arm2 .282, Arm3 .375 (cổ găng), Glove .469 (tâm găng), Muzzle .58; 27 joint DEF. Skin chia theo vị trí dọc trục (cuống + găng cùng tỉ lệ ở chỗ chạm, bóng găng 100% Glove từ x .42). Thử thế thủ: cạnh giãn tối đa 1.29x, 0 cạnh > 1.5. Idle/attack chưa dựng lại trên rig này.
- Vòng 6 (tự kiểm bind skin): tìm ra BUG gốc ở rig_skin.py: dùng ramp(v,a,b) sai thứ tự đối số (ramp(0.40,y,0.34)...), nên mask chân/tay/đầu "hồi" lại ở y cao (vd chân kéo đỉnh vai, mask tay bật lại ở y>0.40). Sửa: ramp(y,a,b). Thêm: chân chia mềm theo z (gaussian) + phần dưới chân, vai bo mềm, đầu smoothstep y .14-.44, tay chia theo trục: Arm1->Arm2 x .235-.325, vòng cuff cứng theo Arm2, Arm2->Arm3 .345-.375, bóng găng 100% Glove từ .40. Đo trên clip idle (thế thủ 35/25/6/8): cạnh giãn tối đa 1.6x, nén 0.54x (trước: 2.5x / 0.35x). Attack (cú đấm f16) giãn 1.8x, nén 0.35x ở đầu găng. Công cụ: skin_test.py (mỗi control xoay thử), clip_stretch.py, _e*.py (soi weight cạnh xấu nhất). File rig: pinchy_rig.fv.
- Vòng 7 (2026-11-13): user tự sửa lại bind skin trong scene; lưu nguyên bản đó: pinchy_rig_skin_user.fv (không chạy lại rig_skin). Dựng anim trên đúng rig này: pinchy_idle_v4.fv (0-48, thế thủ 35/25/6/8, đo giãn 1.54x / nén 0.64x), pinchy_attack_v4.fv (0-30, đấm f16, giãn 1.93x / nén 0.62x). Chưa xuất FBX (chờ "chốt").
- Vòng 8: idle theo ảnh ref của user (cua đấm bốc: 2 găng giơ cao cạnh đầu ngang mắt, cuff thấp hơn, găng nghiêng vào mặt). GUARD=(35,25,6,4, 4,5,22,0): nâng bằng Arm3 rz 22 (không xoay Glove để khỏi nén ngón cái). pinchy_idle_v5.fv, pinchy_attack_v5.fv (attack dựng lại trên thế thủ mới, chưa chỉnh cú móc).
- Vòng 9: thế thủ theo nét vẽ user (hình chữ V: cánh tay ra ngoài hơi xuống rồi gập lên, nắm đấm hướng lên, không vòng cung ra trước mặt). GUARD=(10,5,5,0,-18,40,10,15): gập chủ yếu bằng rz, Arm1 xuống 18°, Arm2 lên 40°. pinchy_idle_v6.fv, pinchy_attack_v6.fv (attack dựng lại trên thế thủ này, cú móc chưa chỉnh).
- Vòng 10: khép tay sát người: GUARD=(25,20,10,0,-25,55,10,15) (thêm vươn trước vừa phải để găng ôm cạnh thân; khuỷu xuống 25°, cẳng tay gập lên). Tâm găng từ x .445 → .377. pinchy_idle_v7.fv, pinchy_attack_v7.fv (attack dựng lại, chưa chỉnh cú móc).
- Vòng 11: idle duyệt (v7). Attack feedback: đấm THẲNG trước mặt, người xoay nửa vòng. Root ry 45° tại f16 (+ lao tới tz .15), cánh tay phải duỗi thẳng (rz bù bỏ chữ V), găng về trước mặt: tâm găng f16 = (-0.07, ., 0.58), Muzzle (-0.02, ., 0.68) trên trục giữa. Đầu xoay ngược -22° để nhìn về trước. pinchy_attack_v8.fv. Skin: giãn max 2.2x ở vai trái/đầu quanh f18 (đầu xoay lệch thân), nén 0.3x cổ găng trái.
- Vòng 12: nhịp đấm nhanh + lực hơn: giữ đà f11-13 (vặn người -26°, tay phải kéo sau -35°), bật ra 2 frame (f13→f15, ~60 cm), **FIRE = f15**, giữ chạm f15-17, thu về nhanh f21, về idle f30. Thân hạ + cúi thêm khi đấm, lag overlap giảm để găng tới đúng frame. pinchy_attack_v9.fv. Skin: giãn max 2.3x (vai trái/đầu f18), nén 0.24x.

## CHỐT 2026-11-13
- Xuất đủ 3 FBX (anim/export_raw.py -> finalize.sh): Pet_Pinchy_Balboa.fbx (Base, 1 mesh, BindPose, 27 deformer, 0 AnimationStack, bind: Head 0,.12,0 / xoay 0), _Idle.fbx (take Idle, 49 key, f0 = f48), _Attack.fbx (take Attack, 31 key, f0 = f30 = idle f0). 27 xương DEF trùng tên giữa 3 file, UnitScale 100, 0 ghost, anim-only có Dummy cùng cấp.
- Idle = pinchy_idle_v7.fv, Attack = pinchy_attack_v9.fv. **Frame bắn f15** (giữ chạm f15-17). Socket đạn DEF_Muzzle_M (con của DEF_Glove_R).
- Bản FBX cũ cất ở _old_fbx/. Chưa chép vào Unity, chưa mở thử trong Unity, chưa push.
