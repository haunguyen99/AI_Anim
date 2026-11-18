# Pet 22 Steam-Pug Turbo (GEK-2366) - báo cáo rig (chưa anim, chưa xuất FBX)

File rig: `C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_22_Steam_Pug_Turbo\steam_pug_turbo_rig.fv` (Frolvy cổng 9888). check_rig sạch.

## Mesh
- FBX gốc chỉ có mesh: 894 đỉnh, Y lên, mặt nhìn +Z, cao ~1,0 m, không nghiêng, không xương/skin. Dùng được, không sửa.
- 10 mảnh: 1 mảnh lớn liền (đầu + tai + thân + 4 chân + đuôi hàn chung), còn lại rời: kính thợ hàn, 3 ống hơi sau lưng, ống xả, 2 bình bên hông, ống mềm xanh, đồng hồ trước ngực.
- Không thấy bánh răng trong mesh (bánh răng đạn là VFX).

## Rig (FK, kiểu Night Bat)
- 30 joint DEF, 30 control (CTL_* + CTL_Main). Root_M là hông, không helper/twist.
- Thân/đầu: Root, Spine1, Head, Goggles (kính, xoay riêng).
- Tai 2 đốt x2 (Ear1, Ear2). Đuôi 2 đốt (Tail1, Tail2).
- 4 chân, mỗi chân 3 joint (Leg1, Leg2, Paw): FLeg_L/R, BLeg_L/R. Chân FK thả lủng lẳng theo thân (Pet bay lơ lửng, không IK/khóa đất).
- Đồ cõng: Valve (van, ống giữa), Pipe_L/R (2 ống bên), Tank_L/R (2 bình hông), Exhaust (ống xả sau lưng), Gauge (đồng hồ trước ngực, xoay trục Z để làm kim nhấp nháy).
- **Socket đạn: `DEF_Muzzle_M`** = con của Exhaust_M, ở đầu ống xả sau lưng (0, 0.44, -0.47), không skin, không có control (chạy theo Exhaust).
- Kim đồng hồ không phải mesh riêng: chỉ xoay/nhấp được cả cụm đồng hồ.

## Skin
- Bind lúc mọi control = 0. Tối đa 4 joint/đỉnh. Mảnh rời gắn 100% vào joint của nó; mảnh liền chia theo vùng (đầu theo độ cao, tai theo độ xa, chân theo độ cao + trước/sau, đuôi theo z).
- Đã xoay thử 19 pose (đầu, thân, tai, chân, gối, đuôi, đồng hồ, van, ống xả, kính): đồng hồ/van/ống xả/kính sạch.

## Chỗ còn yếu
- Cổ: quay đầu 40° vẫn kéo giãn ~2,6 lần ở đường nối đầu-thân (nhỏ hơn 2,6 nếu quay nhẹ hơn). Anim nên giữ quay đầu <= 25°.
- Tai: xoay 30° làm gốc tai co còn ~0,25 và kéo 1,4-1,6 lần; tai hàn liền với đầu. Nếu cần tai vỗ mạnh nên tách tai (extract_faces) rồi skin lại.
- Chân: gập/đá 35° giãn tối đa ~1,8 lần ở phần bụng nối chân; chấp nhận được cho chân ngắn thả lủng lẳng.
- Vị trí joint chân/tai/đuôi đặt theo số đo mesh, chưa nhìn từng góc trong viewport Frolvy (cửa sổ nhỏ). Cần bạn mở file check; chỉnh joint rồi báo để mình skin lại.
- Đuôi nhỏ, nằm sát ống xả nên khó đọc; nếu đuôi cuộn đặc trưng thì cần check kỹ.

## Script
`work/infinite_defense/pets/steam_pug_turbo/`: rig_build.py (joint + control), rig_skin.py (bind + weight), skin_check.py (xoay thử), render.py/comps.py (vẽ mesh từ số liệu để tự xem).
Chưa Director, chưa playblast, không commit, không chép vào Unity.

## Cập nhật 2026-11-13 (chiều)
- Đã xóa xương tai (còn 26 joint DEF, 26 control). Skin: người dùng tự paint lại, file `steam_pug_turbo_rig.fv` là bản của người dùng (làm gốc cho anim).
- **Idle** (`steam_pug_turbo_idle.fv`): 48 frame, lặp (f48 = f0, lệch 0). Lơ lửng 12 cm, bồng bềnh 1 nhịp/vòng, thở phì phò 4 nhịp/vòng (ngực nhấp, đầu cúi hơi cau có, quay nhìn chậm), kim đồng hồ rung nhấp nháy, van/ống xả rung nhẹ theo nhịp thở, 4 chân + đuôi + ống/bình thả trễ.
- **Attack** (`steam_pug_turbo_attack.fv`): 30 frame. Bản 2026-11-13: bỏ hết giật thân/chân/đầu, CHỈ rung lắc 3 ống nước (Valve + Pipe_L + Pipe_R): rung tăng dần 0-11, **12 = BẮN (gắn event f12)** rung mạnh, 12-20 giữ, tắt dần tới f28, f30 = đúng Idle f0.
- Chưa xuất FBX (chờ "chốt"). Chưa Director, chưa playblast. Tự kiểm bằng số + ảnh tự vẽ: mesh co giãn tối đa 2,2 lần (Idle) / 2,95 lần (Attack f13); mesh thấp nhất 4,5 cm khỏi đất khi Attack.
- Script: `anim/idle.py`, `anim/attack.py`, `anim/make_clips.py`, `anim/check.py`, `anim/sheet.py`.

## Cập nhật 2026-11-13 (tối) - làm lại theo analysis.md
- **Idle viết lại** (`steam_pug_turbo_idle.fv`, 48F lặp, f48 = f0): thở 6 nhịp/vòng (hít chậm, thở ra gắt), đầu cúi cau có + chúi khi thở ra, kính tụt xuống rồi nảy lên khi thở ra, ống xả phun ra sau, van/ống/bình rung trễ, kim đồng hồ nhấp theo nhịp thở (xung ở f5-7 mỗi nhịp 8F, gắn đỏ nhấp nháy VFX ở đây).
- **Kim đồng hồ:** xoay quanh trục Z không đọc được (mesh tròn, không có kim rời), nên dùng tịnh tiến + nghiêng mặt đồng hồ. Tương tự ống xả/van: xoay quanh trục không thấy, dùng tịnh tiến hoặc xoay ngả.
- **Attack** (`steam_pug_turbo_attack.fv`): chỉ rung lắc 3 ống nước (biên độ 12° / 9°), thân đứng yên, f12 = bắn, f30 = Idle f0 (mới).
- Tự kiểm: Idle lệch f48-f0 = 0, mesh giãn tối đa 2,4 lần (f15), thấp nhất 8 cm khỏi đất.

## Cập nhật 2026-11-14 - Idle theo ý người dùng
- Idle (2026-11-14, đã quay lại bản trước khi sửa rung ống): nhịp thở êm 2 nhịp/vòng giống Pet khác, không rung cả người; chỉ cục xả tròn sau lưng rung tịnh tiến nhẹ (~1,3 cm). 3 ống đứng không rung riêng. Đỏ nhấp nháy kim đồng hồ = VFX.
- Attack dựng lại trên Idle f0 mới (vẫn chỉ rung 3 ống nước, f12 = bắn, f30 = Idle f0).
- Chân Idle chỉnh lại 2026-11-14: chân thả gần thẳng, chỉ đưa nhẹ ngược chiều thân (±2-3°, khớp sau trễ hơn khớp trước), L/R cùng nhịp, bàn chân ít nghiêng. Trước đó đưa ±4-5° + khớp gối bẻ ngược nên chân lắc như một khối.
- Attack 2026-11-14: thân chạy theo nhịp thở Idle (không đứng im), trộn về đúng Idle f0 từ f16 → f30; 3 ống vẫn rung chồng lên (gom hơi nhẹ 0-11, f12 bắn, mạnh 12-18, tắt dần tới 28).
- Attack 2026-11-14 (góp ý): đoạn xì khói (f12-~19) CẢ NGƯỜI rung theo (thân, đầu, kính, chân, đuôi, bình), tắt dần hết ở f27 rồi hồi về như Idle, f30 = Idle f0.
- Attack 2026-11-14: rung cả người giảm còn một nửa (rung nhẹ).
- Attack 2026-11-14: rung cả người giảm tiếp còn ~20% bản đầu (biên độ nhẹ).

## CHỐT 2026-11-14 - đã xuất FBX
- `Pet_Steam_Pug_Turbo.fbx` (Base: 26 xương + mesh + skin, đúng bind pose Root (0, 0.33, -0.12), xoay 0, 0 AnimationStack), `_Idle.fbx` (1,6 s, 48F lặp), `_Attack.fbx` (1,0 s, 30F, bắn ở f12). Đơn vị x100, tên 26 xương giống nhau ở 3 file, có DEF_Muzzle_M. Anim-only 0 mesh, có Dummy cùng cấp.
- pet_chot all 22: đạt; đã dọn raw_*/_tmp/bản sao mesh vào Thùng rác; CHOT.txt đã ghi. Chưa chạy Unity batchmode, chưa chép vào Unity (chờ người dùng).
- Script xuất: `anim/export_raw.py` (dựng lại clip + bake + xuất raw_*), `ghost_ears.py` + `finalize.sh` (xử lý FBX).
- Bẫy mới: xương tai đã xóa trong Frolvy VẪN được xuất vào FBX (ID cao hơn Root nên ghost_rename không bắt) → `ghost_ears.py` cắt liên kết tới cha để fbx_ascii_keep bỏ chúng.
- 2026-11-14 (sau chốt): xóa key thừa trong 2 file clip bằng `api.simplify_keys` (dung sai 0,3 mm / 0,03°): Idle 11025 → 886 key, Attack 8325 → 2574 key; mesh lệch tối đa 1 mm; FBX Idle/Attack xuất lại (vẫn mỗi frame một mẫu, lệch giá trị ≤ 0,03 so với bản trước). Script: `anim/clip_clean.py`.
