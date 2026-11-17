# Pet 25 Chrono Ouroboros (GEK-2369) - báo cáo rig

Phạm vi: chỉ lập file rig (chưa anim, chưa xuất FBX). Frolvy cổng 9890.

## File rig
`C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_25_Chrono_Ouroboros\chrono_ouroboros_rig.fv` (đang mở trong Frolvy 9890). check_rig sạch. Mọi control = 0, chưa có key.

## Mesh
- 1 mảnh thân liền (914 đỉnh) + 2 mảnh nhỏ (mắt, 21 đỉnh mỗi mảnh). Y lên, đầu về +Z, dài 3,05, cao 1,12 (mét). Không cần xoay/sửa.
- Không có xương/skin sẵn. Chân, bờm, vây lưng dính liền thân nên skin theo vùng.
- **Mesh KHÔNG có bánh răng thiên văn** (GDD có nói). Chưa có gì để skin cho bánh răng nên chưa có joint bánh răng. Cần model bổ sung hoặc quyết định cách làm (xem câu hỏi cuối).

## Rig (FK, 25 joint DEF, 25 control CTL_* + CTL_Main)
- Thân: `Root_M` (hông, z -0,55), `Spine1_M`, `Spine2_M`.
- Cổ + đầu: `Neck1_M`, `Neck2_M`, `Head_M`, `Jaw_M` (hàm dưới).
- **Socket đạn `DEF_Muzzle_M`**: con của Jaw, ở mũi/miệng (0, 0.66, 1.40), không skin, không có control.
- Đuôi: `Tail1_M` … `Tail5_M` (5 đốt, đuôi cong lên, vây ở đốt cuối). Chuỗi thân + cổ + đuôi dài đủ để uốn hình số 8.
- Chân (mỗi chân 3 joint): `ForeLeg1/ForeLeg2/ForeFoot` (L, R) con của Spine2; `HindLeg1/HindLeg2/HindFoot` (L, R) con của Root. Chân buông lơ lửng, trễ theo thân.
- Chiều xoay: uốn trái/phải = xoay Y; ngóc/cúi đầu, đuôi = xoay X (X âm là ngóc lên); hàm há = X dương; chân vung trước/sau = X; chân dang ngang = Z.

## Skin
Thân/cổ/đuôi tính theo khoảng cách dọc chuỗi xương (chuyển mượt), chân theo độ cao (đùi / cẳng / bàn), hàm theo vùng miệng dưới, mắt 100% Head. Tối đa 4 joint mỗi đỉnh. Bind lúc mọi control = 0.

Đã xoay thử (kiểm bằng số + nhìn ảnh):
- Uốn thân/đuôi hình chữ S ±20–30°: mượt, giãn cạnh tối đa ~1,3 lần.
- Cổ xoay 25°, ngóc đầu 30° + há hàm: sạch.
- Chân vung 35° trước/sau, dang 30°: không móp rõ.

## Chỗ yếu / chưa chắc
- Há hàm: đầu là khối đặc, không có khoang miệng; há 30° chỉ hạ phần mõm dưới, mép môi giãn ~3 lần ở mũi (đọc tạm được, chưa đẹp). Muốn há rõ có thể phải thêm hình miệng.
- Chân thấp, mỏng, dính vào thân: vung mạnh (>35°) có thể kéo bụng.
- Bờm/sừng sau đầu theo Neck2 + Head; nếu muốn bờm đung đưa riêng thì cần thêm joint.
- Chỉ kiểm tay ở vài pose, chưa chạy Director.

## Câu hỏi cho người dùng
Mesh không có bánh răng. Chọn: (a) bổ sung model bánh răng rồi thêm joint xoay riêng; (b) bỏ bánh răng trong anim, VFX làm; (c) tách vài mảnh vây/bờm làm "bánh răng" tạm (không nên).

## Script
`rig_build.py` (joint + control), `rig_skin.py` (bind + weight), `skin_check.py` (xoay thử), `posed_shot.py` (chụp pose), `save_rig.py` trong `work/infinite_defense/pets/chrono_ouroboros/`.

## Idle v1 (2026-11-14, theo GDD)
- `chrono_ouroboros_idle_v1.fv`, 90 frame (3 giây, 30 fps), lặp liền mạch (f90 = f0, kiểm mesh lệch 0), chưa xuất FBX.
- Lơ lửng 12 cm, bồng bềnh nhẹ 2 nhịp/vòng. Sóng ngang (1 vòng/loop) chạy từ đầu về đuôi + sóng dọc (2 vòng/loop) => đầu vẽ hình số 8. Chân buông, trễ theo thân.
- Không làm bánh răng (mesh không có). Giãn cạnh lớn nhất cả vòng 1,5 lần (cổ/chân trước).
- Script: anim/idle.py, anim/run_idle.py.

## Idle v2 - trườn chữ S (2026-11-14)
- `chrono_ouroboros_idle_v2.fv`, 90F lặp liền (f90 = f0, mesh lệch 0). Thay v1: sóng chữ S thật chạy dọc thân từ đầu về đuôi (bước sóng 2,4 m, góc uốn ±32° ở thân, đuôi lớn hơn, đầu/cổ nhỏ hơn), sóng dọc nhẹ lệch pha, lơ lửng 12 cm. Frame 0 = pose chữ S. Giãn cạnh tối đa 1,47.
- Script: anim/idle2.py, anim/run_idle2.py.

## Idle v3 - chữ S theo chiều dọc (2026-11-14)
- `chrono_ouroboros_idle_v3.fv`: sóng S nằm trong mặt phẳng đứng (lên/xuống), ±18° ở thân, uốn ngang chỉ ±7° phụ. Nâng nền cho đáy sóng cách đất ~10 cm. Lặp liền, giãn cạnh tối đa 1,39. Script anim/idle2.py.

## Idle v4 - sóng nhỏ hơn, nhanh hơn (2026-11-14)
- `chrono_ouroboros_idle_v4.fv`: 72F (2,4 s/nhịp, v3 là 3 s), sóng S dọc ±11° (v3 ±18°), ngang ±4°, nâng nền 0,26 (đáy cách đất ~12 cm). Lặp liền (f72 = f0), giãn cạnh tối đa 1,27. Script anim/idle2.py.

## Idle v5 - sóng cao hơn, nhịp nhanh hơn (2026-11-14)
- `chrono_ouroboros_idle_v5.fv`: 54F (1,8 s/nhịp), sóng S dọc ±30°, bước sóng 1,9 m (2 đỉnh rõ), ngang ±5°, nâng nền 0,34 (đáy cách đất ~11 cm). Lặp liền (f54 = f0). Giãn cạnh tối đa 1,78 (vây đuôi, f46). Script anim/idle2.py.

## Attack v1 (2026-11-14, nền Idle v4)
- `chrono_ouroboros_attack_v1.fv`, 40F, **BẮN = frame 16** (gắn event). f0 = f40 = đúng tư thế Idle frame 0 (mesh lệch 0).
- 0-9 cuộn người (cổ rút về sau, hạ thân, đuôi cuộn) · 9-16 lao đầu tới + há hàm · 16 hàm mở ~38°, thân vươn · 16-22 giật lại, đuôi quất · 22-40 tắt dần về idle f0. Sóng trườn idle chạy 1 vòng trong attack nên nối liền idle.
- Chưa có bánh răng lóe (mesh không có). Giãn cạnh lớn nhất 3,1 lần ở môi/mõm (f18, hàm há); đầu vọt nhanh nhất ~0,28 m/frame ở f19.
- Script: anim/attack.py, anim/run_attack.py.

## Idle v6 - uốn lượn số 8 / vô cực (2026-11-14)
- `chrono_ouroboros_idle_v6.fv`: 72F lặp liền (f72 = f0). Sóng S đứng chạy dọc thân (±14°, như v4 nhưng nhỉnh hơn) + lắc ngang 2 nhịp/vòng (±15°) => mỗi điểm thân vẽ số 8 nhìn từ trước; đầu/đuôi rõ nhất. Đáy cách đất ~10 cm, giãn cạnh tối đa 1,33. Script anim/idle3.py, run_idle3.py.
- Attack v1 dựng trên Idle v4: nếu duyệt v6 thì dựng lại Attack trên idle3 (f0/f40 phải = idle v6 f0).

## Model mới + rig v2 (2026-11-14)
- Model mới lấy từ Unity (`Assets/Kho/Skin/mesh/Pet_new/mesh/Pet_chrono_ouroboros.fbx` + texture), chép vào `New_PET\Pet_25_Chrono_Ouroboros\Pet_Chrono_Ouroboros.fbx` (bản cũ đổi tên `_old`). Rồng thẳng, KHÔNG có chân, đầu cúi xuống, có đồng hồ cát (hourglass) mesh riêng ở giữa thân.
- `chrono_ouroboros_joints_v2.fv` (chỉ joint) và `chrono_ouroboros_rig_v2.fv` (rig + skin): 16 joint DEF (Root, Spine1-4, Neck1-2, Head, Jaw, **Muzzle** ở mũi, Tail1-5, **Hourglass** xoay quanh Y), 16 control. Đồng hồ cát skin 100% Hourglass.
- Script: v2/joints_v2.py, v2/rig_build_v2.py, v2/skin_v2.py, v2/skin_check_v2.py. Idle/Attack cũ làm trên rig cũ (có chân), cần dựng lại.

## Dựng lại trên rig v2 (2026-11-17, phiên con Paseo, Frolvy Linux cổng 9890)
- Kiểm rig v2: mở được, 16 joint DEF + 16 control, check_rig sạch. Skin ổn: xoay thân/cổ/đuôi/hàm trong biên độ idle, cạnh mesh giãn tối đa ~1,2 (cổ gập 25° ôm tốt). Đồng hồ cát là mesh riêng `hourglass`, xoay Hourglass 90° làm mesh dịch tới 0,37 m (ăn skin 100%). Mesh thân (`Pet_chrono_ouroboros`) không chứa đồng hồ cát.
- Lưu ý bind: mũi rồng nằm dưới đất ở bind pose (y = -0,17), nên Root phải nâng ~0,39 m để điểm thấp nhất cách đất ~10 cm.
- `chrono_ouroboros_idle_v7.fv`: 72F lặp liền (f72 = f0, lệch mesh 0). Hướng v6 (sóng S đứng ±14° + lắc ngang 2 nhịp/vòng ±15° = số 8), bỏ chân, thêm Hourglass xoay ngược chiều kim đồng hồ (+Y) 1 vòng/72F. Điểm thấp nhất mesh 0,109 m (đồng hồ cát 0,217), giãn cạnh tối đa 1,40 (f66, vây đuôi). Script anim/idle4.py + run_idle4.py.
- `chrono_ouroboros_attack_v2.fv`: 40F, **BẮN = frame 16** (hàm mở ~41°, thân vươn). f0 = f40 = Idle v7 f0. Cổ rút về (f9) rồi lao tới (f16), giật lại f22, tắt dần về idle. Hourglass quay nhanh dần tới f16 (đỉnh ~32°/frame), cuối về nhịp idle 5°/frame, tổng 2 vòng. Điểm thấp nhất mesh 0,095 m. Giãn cạnh tuyệt đối tối đa +0,21 m ở vây đuôi (f30), tỉ lệ cao nhất 2,4x ở cạnh hàm rất ngắn khi há (f18, +0,14 m). Script anim/attack2.py + run_attack2.py.
- Chưa duyệt, chưa CHOT.txt, chưa xuất FBX. Mới tự kiểm bằng số + vài ảnh viewport nhỏ (không có playblast, chưa chấm bằng mắt kỹ dáng đầu/hàm ở f9–f22).

## Rig v3 (2026-11-17): rig cho pose vòng tròn (concept ouroboros)
- Lý do: concept là rồng cuộn vòng quanh đồng hồ cát, model là ống thẳng dài ~3,4 m. Rig v2 (12 khớp thân/đuôi) cuộn vòng thì mỗi khớp gập 25-40 độ, mặt trong móp. Rig v3 tăng khớp để mỗi khớp gập ~18 độ.
- `chrono_ouroboros_rig_v3.fv` (rig + skin, mọi control = 0, check_rig sạch): 22 joint DEF = Root, Spine1-8 (cách ~0,18 m), Neck1-2, Head, Jaw, Muzzle, Tail1-7 (~0,17 m), Hourglass (con của Root); 22 control FK. `chrono_ouroboros_joints_v3.fv` = chỉ joint.
- Skin: mỗi điểm thân/đuôi ăn ~3 khớp theo độ dài cung (kernel), đầu/hàm giữ như v2, đồng hồ cát 100% Hourglass. Mesh thân tách riêng với `hourglass`.
- `chrono_ouroboros_ring_pose_v3.fv`: rig v3 đã đặt pose vòng (không key). Thân + đuôi cuộn về phía BỤNG (vây lưng nằm ngoài vòng), đầu ở trên-trước, mũi đuôi ở dưới-trước, khe hở nhìn ra phía trước, đồng hồ cát ở tâm vòng thẳng đứng. Công thức ở v3/ring.py (R = 0,54 m, Root rx = -121 độ, Hourglass bù xoay và dời về tâm).
- Đo skin (v3/skin_check_v3.py): pose vòng đầy giãn cạnh tối đa +0,29 m (x1,24), cạnh vây đuôi bị nén mạnh nhất (x0,17, cạnh rất ngắn ở cụm vây mũi đuôi); xoay thân/cổ/hàm trong biên độ idle như v2.
- Chưa làm: spline IK (điều khiển vòng bằng 5 điểm), chưa kiểm xuất FBX có bake đúng khi dùng spline IK. Hiện là FK 22 control, pose vòng đặt bằng script. Idle/attack trên rig v3 chưa dựng.

## Idle v8: POSE F0 theo concept (2026-11-17)
- `chrono_ouroboros_idle_v8_pose.fv` (rig v3, 1 key ở frame 0, chưa có chuyển động, range 0-72). Pose vòng ouroboros: đồng hồ cát ở tâm vòng, đầu trên-trái cúi, hàm tì lên vành đồng hồ cát, thân vòng sang phải, mũi đuôi vươn lên bên trái, vây lưng ngoài vòng. Công thức v3/ring.py (R 0,54 m, Root rx -121, Tail3-7 cuộn thêm -10 mỗi khớp, Head +4); dựng bằng v3/run_pose_v8.py. Root ty ≈ 0,35 để điểm thấp nhất cách đất 11 cm.
- Chưa làm chuyển động. Chờ người dùng duyệt pose.
- Sự cố: lúc 10:13 phiên chính chạy git (sao lưu / kéo main), thư mục pet bị dọn mất script + report; đã khôi phục từ commit sao lưu 458f3b0 (git show, không đổi nhánh/index).

## Idle v9: POSE F0 sửa theo director (2026-11-17)
- `chrono_ouroboros_idle_v9_pose.fv` (rig v3, 1 key ở frame 0). Sửa từ v8 theo director: (1) ngửa đầu -75° + cổ -10° vì đầu mesh bind đã cúi ~70°, mõm đi tiếp theo đường vòng, hướng xuống-trái; (2) vòng nhỏ lại R 0,52, xoay cả vòng PHI -150 để đầu lên ~10h30, mũi đuôi lên ~9h, đầu gần chạm đuôi; (3) xoắn nhẹ ra khỏi mặt phẳng: thân ry +4°/khớp, đuôi ry +9°/khớp => đầu ra trước (x TB +0,17 m), đuôi lùi sau (-0,21 m); (4) đồng hồ cát hạ 4 cm, dời 5 cm về phía đầu; (5) đuôi cuộn thêm Tail3-7 -10°, Tail7 thêm -10°.
- Đo: điểm thấp nhất cách đất 0,11 m; khoảng cách đỉnh gần nhất: đầu-đuôi 0,24 m, đầu-đồng hồ cát 0,14 m, đuôi-đồng hồ cát 0,056 m, thân-đồng hồ cát 0,042 m (đỉnh-đỉnh, chưa đo xuyên mặt).
- Công thức v3/ring.py (CFG), dựng v3/run_pose_v9.py.

## Idle v10: POSE F0 chỉnh nhỏ theo director lần 2 (2026-11-17)
- `chrono_ouroboros_idle_v10_pose.fv` (1 key ở frame 0). Từ v9: đồng hồ cát dời +0,08 m theo x về phía đầu và nâng 2 cm để vành trên sát cằm (director: 'Duyệt kèm chỉnh nhỏ'). Đo đỉnh-đỉnh: đầu-đồng hồ cát 0,111 m (v9: 0,137), đuôi-đồng hồ cát 0,114 m, thân-đồng hồ cát 0,069 m, đầu-đuôi 0,238 m, điểm thấp nhất 0,11 m.
- Không làm: thu vòng R 0,52 -> 0,47 (director B2). Đã thử R 0,47 ở v9: lỗ vòng chỉ còn ~0,44 m < chiều cao đồng hồ cát ~0,48 m nên đồng hồ cát cắm vào thân. Giữ R 0,52.
- Chưa đo xuyên mặt thật (chỉ đỉnh-đỉnh), chưa xem texture/mắt. Chưa làm chuyển động.

## Idle v11: POSE F0 vòng TRÒN thật (2026-11-17)
- Người dùng: 'chưa tròn'. Đo v10: tâm đường thân lệch khỏi đường tròn ±5 cm (cung giữa phình 0,60, gần Root xẹp 0,52) do cộng độ cong đều và hai đoạn phẳng quanh Root.
- `chrono_ouroboros_idle_v11_pose.fv` (1 key ở frame 0). v3/ring.py viết lại thành giải hình học: mọi khớp Spine1-8, Neck, Tail1-7 nằm trên một đường tròn R 0,54 m; mỗi đoạn xương là dây cung, góc khớp = hướng dây cung - hướng bind - góc khớp cha. Root nằm giữa dây cung phẳng Spine1-Tail1. Đo lại: lệch khỏi đường tròn tối đa 3 mm (v10: ±5 cm).
- Đầu = tiếp tuyến + 12° cúi. Xoắn ra khỏi mặt phẳng chỉ dồn về hai đầu (bình phương theo vị trí): thân ry 14, đuôi ry 20 (đầu ra trước TB +0,33 m, đuôi lùi -0,09 m), để thân giữa vẫn phẳng và tròn (xoắn đều làm méo vòng, hiện góc gãy ở đỉnh). PHI -165. Đồng hồ cát dời (HG_X 0,08, DY -0,02, DZ 0,05).
- Đo đỉnh-đỉnh: đầu-đuôi 0,044 m, đầu-đồng hồ cát 0,062 m, đuôi-đồng hồ cát 0,086 m, thân-đồng hồ cát 0,070 m, điểm thấp nhất 0,11 m. Chưa đo xuyên mặt.
- Bản cũ: v3/ring_v10.py giữ lại để so.

## Idle v12 (2026-11-17): idle lơ lửng từ pose người dùng đã sửa
- Pose gốc = pose người dùng sửa tay, lưu đè `chrono_ouroboros_idle_v11_pose.fv` lúc 11:54; đã chép giữ nguyên thành `chrono_ouroboros_idle_v12_pose_user.fv`. Người dùng xoay cả vòng quanh trục đứng ~90° (Root Euler 15, -88, -180) cho mặt vòng quay ra camera trước, dời vòng về giữa (Root t = 0,09 / 0,07 / 0,57), chỉnh tay xoắn thân/cổ/đuôi.
- `chrono_ouroboros_idle_v12.fv`: 72F (2,4 s), lặp liền (f72 = f0, lệch mesh 0), key mọi frame, cycle. f0 khớp 100% pose người dùng (lệch 0). Script anim/idle6.py + run_idle6.py (đọc pose gốc thẳng từ file, mọi chuyển động là offset triệt tiêu ở f0).
- Chuyển động: lơ lửng nhô 5 cm rồi hạ về pose gốc (không bao giờ thấp hơn pose); đầu - đuôi đảo pha trước/sau 1 nhịp + đầu lên/xuống 2 nhịp => số 8; sóng độ cong trôi quanh vòng (±1,2°/khớp, nhỏ dần về đầu); đầu gật trễ pha, hàm thở, vây đuôi Tail5-7 vẫy trễ dần; đồng hồ cát xoay ngược chiều kim đồng hồ (+Y) 1 vòng/72F quanh trục đứng thế giới (chiều cao mesh không đổi qua 72 frame => trục đứng), lơ lửng nhẹ 1 cm.
- Đo cả 72F (đỉnh-đỉnh): điểm thấp nhất mesh ≥ 0,11 m (pose gốc là điểm thấp nhất); đầu-đuôi ≥ 0,033 m, đầu-đồng hồ cát ≥ 0,085 m, đuôi-đồng hồ cát ≥ 0,046 m, thân-đồng hồ cát ≥ 0,065 m; giãn cạnh tối đa +0,28 m (như pose gốc). Chưa đo xuyên mặt thật.
- Lưu ý: Euler rz của Hourglass chạy 0 -> 360 trong 72F (cùng tư thế f0), nội suy giữa f72 và f73 của vòng cycle có thể xoay một vòng nếu lấy mẫu số lẻ; lấy mẫu theo frame nguyên (Unity bake) thì đúng.
- Chưa làm: Attack v3 trên rig v3, playblast, director chấm chuyển động, FBX (chờ "chốt").

## Idle v13 (2026-11-17): bỏ xoay đồng hồ cát
- Người dùng: "k cho đồng hồ quay nha". `chrono_ouroboros_idle_v13.fv` = v12 nhưng đồng hồ cát ĐỨNG YÊN theo vòng (không xoay, không dao động riêng), vẫn nhô lên/hạ xuống cùng cả vòng. Cờ SPIN = False trong anim/idle6.py (đặt True để bật lại xoay ngược chiều kim đồng hồ). Dựng bằng anim/run_idle7.py. v12 (có xoay) giữ lại để so.
- Lưu ý: brief GDD ghi idle có bánh răng/đồng hồ xoay ngược chiều kim đồng hồ; người dùng đã bỏ ý này cho idle.

## Idle v14 (2026-11-17): đồng hồ cát nhấp nhô như đang bay
- Người dùng: không cho đồng hồ quay, nhưng "cũng nhấp nhô như đang bay". `chrono_ouroboros_idle_v14.fv` = v13 + đồng hồ cát có nhịp lên/xuống RIÊNG (trễ pha so với vòng, thêm gợn 2 nhịp, tối đa ~4 cm so với vòng) và lắc nhẹ ±2,5° quanh trục nhìn (Z thế giới); không xoay quanh trục đứng. Lặp liền (f72 = f0), f0 = pose người dùng. Tham số HGB / HGS trong anim/idle6.py, dựng bằng anim/run_idle8.py.
- Đo 72F: khoảng cách gần nhất thân-đồng hồ cát ≥ 5,8 cm, đầu-đồng hồ cát ≥ 8,6 cm, điểm thấp nhất ≥ 10,8 cm (số đo với HGB 0,030; bản cuối HGB 0,022 nhỏ hơn).

## Attack v3 (2026-11-17): rig v3, từ pose người dùng
- `chrono_ouroboros_idle_v14.fv` đã lưu (idle lơ lửng, đồng hồ cát nhấp nhô, không quay).
- `chrono_ouroboros_attack_v3.fv`: 40F, **BẮN = frame 16** (hàm mở đỉnh 37° đúng f16, đóng lại tới f22 còn 10°, tắt hết f32). f0 = f40 = Idle v14 f0 = pose người dùng (lệch mesh 0).
- Chuyển động: 0-9 đầu/cổ rụt ngửa ra và lùi sau mặt phẳng vòng, hạ vòng 3 cm; 9-16 đầu lao ra trước (hướng camera, ry cổ/đầu +14°, ry Spine5-8 tăng dần), há miệng, vòng nảy lên 4 cm; 16-22 giật lại; 22-40 tắt dần về idle f0. Vây đuôi vẫy overshoot trễ. Chuyển động idle (trôi, số 8) chạy 1 vòng/40F ở 55% biên độ. Đồng hồ cát không quay: nảy lên 3 cm + lắc 4° khi bắn (lóe sáng là VFX).
- Hướng lao: ban đầu thử cuộn cổ thêm (đầu dí vào đồng hồ cát/đuôi, khoảng cách 6 mm) nên bỏ, đổi sang lao ra khỏi mặt phẳng vòng.
- Đo 40F (đỉnh-đỉnh): điểm thấp nhất ≥ 8,5 cm (anticipation hạ vòng); đầu-đuôi ≥ 2,5 cm, đầu-đồng hồ cát ≥ 2,5 cm (lúc lao, sát), thân-đồng hồ cát ≥ 5,8 cm; giãn cạnh tối đa +0,30 m. Chưa đo xuyên mặt thật, chưa playblast, chưa director.
- Script: anim/attack3.py + run_attack3.py (dựa anim/idle6.py).

## Attack v4 (2026-11-17): rồng quay 1 vòng quanh đồng hồ
- Người dùng: bỏ attack v3 (đầu lao), "attack chỉ làm rồng quay 1 vòng quanh đồng hồ, đồng hồ vẫn bay lơ lửng như idle". `chrono_ouroboros_attack_v4.fv`: 40F, f0 = f40 = idle f0 = pose người dùng (mesh lệch 0).
- Cả vòng quay 360° trong mặt phẳng vòng, quanh tâm vòng (Root rx cục bộ += theta, Root tịnh tiến để tâm đứng yên), đầu đi theo hướng mõm chỉ. theta: rụt -18° ở f6, quay nhanh dần (nhanh nhất giữa clip ~19°/frame), vọt 368° ở f36, về 360° ở f40. BẮN (event) = frame 20 (lúc quay nhanh nhất), hàm mở 22° (JAW_OPEN = 0 nếu không cần). Thân/đuôi giữ chuyển động idle 55% (trôi, vây vẫy trễ).
- Đồng hồ cát đứng nguyên chỗ trong thế giới (lệch ngang 0), không quay, nhấp nhô + lắc ±2,6° như idle (1 vòng nhịp/40F). Vì gai đầu/đuôi đi xuống đáy khi quay, cả vòng + đồng hồ cát bay cao thêm tối đa 22 cm (mượt, đỉnh giữa clip) rồi hạ về f40. Điểm thấp nhất mesh ≥ 7,6 cm (f20).
- Script anim/attack4.py + run_attack4.py. v3 (đầu lao) giữ lại để so.
- Chưa playblast, chưa director, chưa FBX.

## Attack v5 (2026-11-17): rồng quay có sức sống
- Người dùng: attack v4 'quay đơ quá, không có anim'. `chrono_ouroboros_attack_v5.fv` = v4 (rồng quay 360° quanh đồng hồ, 40F, BẮN f20, hàm mở 22°, f0 = f40 = pose người dùng) + các lớp sống (anim/attack5.py, run_attack5.py), mọi lớp nhân với envelope = 0 ở f0 và f40:
  - Tốc độ quay giật theo 2 đợt (dồn lực - xả), không đều.
  - Thân luồn lượn vào/ra khỏi mặt phẳng vòng (ry = hiệu của sóng tuyệt đối cố định trong không gian, ±10°), gợn độ cong ±1°.
  - Vòng co 2% lúc dồn lực (f2-10), nở ra tới 7% lúc quay nhanh (f12-34).
  - Đầu chúi theo hướng quay (theo tốc độ), đuôi/vây trễ phía sau; đồng hồ cát nhấp nhô 60% biên độ idle, lắc ±2,6°.
  - Cả vòng + đồng hồ cát bay cao thêm tối đa 30 cm (đỉnh giữa clip) + nảy thêm 7 cm ở f20 vì gai đầu/đuôi quét qua đáy.
- Đồng hồ cát trôi vào đúng tâm vòng (ngang) khi quay, về lại chỗ cũ ở f0/f40 (hơi dịch ~11 cm theo ngang). Tâm vòng đo bằng fit đường tròn lên mesh pose người dùng (Root-local 0,013 / -0,464 / 0,044) thay cho công thức lý tưởng (lệch 5 cm).
- Bỏ lắc yaw cả vòng (HYAW = 0): Root của pose người dùng sát gimbal lock (Euler 15, -88, -180), thêm yaw làm Euler lật nhánh. Không còn nhảy Euler nào >60° giữa 2 frame.
- Đo 40F: điểm thấp nhất ≥ 9 cm; đầu-đuôi ≥ 2,3 cm (f4-8 lúc co), đầu-đồng hồ cát ≥ 10,7 cm, thân-đồng hồ cát ≥ 1,8 cm (đỉnh-đỉnh; lỗ vòng chỉ vừa đồng hồ cát, phần dẹt gần Root là chỗ sát nhất khi vòng quay tới), giãn cạnh tối đa +0,28 m. Chưa đo xuyên mặt thật, chưa playblast, chưa director.
- Nếu thấy đồng hồ cát cắt vào thân ở f16-22: thu nhỏ đồng hồ cát ~90% (cần ghi chú khi xuất FBX) hoặc tăng SQ_OUT.

## Attack v6 (2026-11-17): v4 + đoạn về f32-f40 mềm hơn (bỏ v5)
- Người dùng: không dùng v5, quay về v4, chỉnh đoạn f32 -> f40 cho mềm. `chrono_ouroboros_attack_v6.fv` = v4 (rồng quay 360° quanh đồng hồ, BẮN f20, hàm 22°, đồng hồ cát lơ lửng như idle, f0 = f40 = pose người dùng) chỉ đổi cách quay về: v4 quay tới 368° ở f36 rồi giật ngược về 360° trong 4 frame (đảo chiều gấp, ~2°/frame). v6: quay ease-in-out kéo dài tới f40, giảm tốc liên tục (17°/frame ở f26 -> 6° ở f36 -> 0,6° ở f40, gia tốc đều ~ -1,5°/frame²), không đảo chiều, tới 360° với vận tốc ~0 ở f40 (nối vào idle f0 êm). Nhịp quay chậm hơn v4 cuối clip khoảng 3 frame.
- Thêm nảy nhẹ 5 cm ở f22 (gai đầu/đuôi quét qua đáy, lệch nhịp so với v4). Điểm thấp nhất mesh ≥ 9,6 cm; đầu-đuôi ≥ 3,1 cm; thân-đồng hồ cát ≥ 1,9 cm (vẫn sát như v4, ở f22-24).
- Script anim/attack6.py + run_attack6.py. v4, v5 giữ lại. Không còn nhảy Euler > 60°.

## CHỐT (2026-11-17 14:46)
- Người dùng nói "chốt". Clip chốt: Idle = `chrono_ouroboros_idle_v14.fv` (72F), Attack = `chrono_ouroboros_attack_v6.fv` (40F, bắn f20), rig `chrono_ouroboros_rig_v3.fv`, pose gốc `chrono_ouroboros_idle_v12_pose_user.fv` (= idle_v11_pose, người dùng sửa tay).
- FBX trong `New_PET\Pet_25_Chrono_Ouroboros\`: `Pet_Chrono_Ouroboros.fbx` (Base: 22 xương + 2 mesh [thân + hourglass] + skin, BindPose, 0 AnimationStack, xuất ở bind: mọi control = 0), `Pet_Chrono_Ouroboros_Idle.fbx` (2,4 s), `Pet_Chrono_Ouroboros_Attack.fbx` (1,333 s). Quy trình: export_scene -> fbx_ascii_keep --root DEF_Root_M -> pet_fbx_finalize (UnitScale 100, take Idle/Attack/Base, --meshes 2 cho Base) -> Base: fbx_unity_bind + fbx_strip_anim; anim: --no-meshes + fbx_add_sibling. Socket đạn = DEF_Muzzle_M.
- `pet_chot.py all 25` (bản chạy qua wrapper đổi đường dẫn Linux + `gio trash` thay thùng rác Windows): check ĐẠT cả 3 file, ghi CHOT.txt. Đã bỏ vào thùng rác: .fv cũ (rig/rig_v2, joints/joints_v2, idle v1-v7, v12, v13, attack v1-v5), bản sao Pet_Chrono_Ouroboros.fbx bên work, `Pet_Chrono_Ouroboros_old.fbx` (model cũ có chân), và các pose trung gian v8/v9/v10 + ring_pose_v3 (giữ idle_v11_pose = pose người dùng sửa + v12_pose_user bản sao).
- Model gốc từ Unity (77 KB) đã bị Base xuất ra ghi đè cùng tên; bản sao lưu ở /tmp/p25/exp/src_model_backup.fbx (thư mục tạm).
- Chưa làm: chép vào Unity (chờ người dùng duyệt), chưa thử nhập Unity batchmode, chưa có meta Unity (Base importAnimation 0 / avatar copy cho file anim, theo reference-pet-fbx-unity-fixes), chưa director.

## Dọn thư mục lần cuối (2026-11-17, người dùng: chỉ giữ file chốt, lưu thành idle - attack - rig)
- `New_PET\Pet_25_Chrono_Ouroboros\` chỉ còn: `chrono_ouroboros_rig.fv` (rig v3, mọi control = 0, không key, check_rig sạch), `chrono_ouroboros_idle.fv` (idle v14, 72F), `chrono_ouroboros_attack.fv` (attack v6, 40F, bắn f20), 3 FBX chốt, `T_Pet_chrono_ouroboros.png` (texture), `CHOT.txt`. Joints_v3, pose v11 / v12_pose_user và rig_v3 đã bỏ vào thùng rác (khôi phục được).
- Script dựng lại (anim/run_idle8.py, run_attack6.py...) vẫn trỏ tới tên cũ (idle_v12_pose_user.fv ...), muốn chạy lại phải đổi đường dẫn / lấy pose từ thùng rác.
