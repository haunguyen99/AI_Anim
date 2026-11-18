# Pet 23 Kitsune Nine-Mist (GEK-2367) - báo cáo rig

Chỉ lập file rig (chưa anim, chưa xuất FBX). Frolvy cổng 9889.

## File
- Rig: `C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_23_Kitsune_Nine_Mist\kitsune_nine_mist_rig.fv` (check_rig sạch, mọi control = 0)
- Script dựng lại (work/infinite_defense/pets/kitsune_nine_mist/): `kit_common.py` (đo mesh, đường tâm đuôi), `rig_build.py`, `rig_skin.py`, `skin_check.py`, `shot.py`. Ảnh thử xòe đuôi: `fan_sheet.png` (khép | giữ | xòe).

## Mesh
- FBX gốc: 1 mesh, 955 đỉnh, chưa xương/skin, đã đứng đúng (Y lên, mặt +Z, cao 0,87 m) nên không xoay/freeze.
- Gồm 11 mảnh liền trong 1 mesh: thân + đầu + tai + 4 chân (liền nhau), nửa mặt nạ (rời), 9 đuôi (rời nhau, chỉ 2 đuôi trong cùng chạm nhau ở gốc). Không tách mesh, skin được sạch vì đuôi vốn rời.

## Rig (FK, 73 joint, 66 control) — cập nhật: chân 3 đốt, đuôi 5 đốt (người dùng 2026-11-13)
- Thân: DEF_Root_M (hông), DEF_Spine1_M, DEF_Head_M.
- Tai: 2 đốt mỗi bên (Ear1/Ear2 L/R).
- Chân: 4 chân, 3 đốt mỗi chân (FLeg1-3 chân trước, BLeg1-3 chân sau, L/R).
- 9 đuôi: mỗi đuôi 5 đốt skin (Tail<k>_1..5) + 1 joint socket ở đầu đuôi (không skin). Đặt theo đường tâm đo từ mesh (đuôi cuộn cũng bám theo). k=1 đuôi giữa (cuộn lên cao), 2 = cặp trong cuộn, 3 = cặp trên, 4 = cặp giữa, 5 = cặp thấp nhất; mỗi k có L/R.
- Socket Muzzle: 9 đầu đuôi. **DEF_Muzzle_M = đầu đuôi giữa**; 8 đuôi còn lại DEF_Muzzle2_L/R … DEF_Muzzle5_L/R. Cần hỏi: Unity chỉ đọc 1 socket tên DEF_Muzzle_M, hay bắn từ cả 9 đầu đuôi?
- Control: CTL_Main, 1 control mỗi joint (trừ socket), nối bằng parent constraint, tên CTL_<tên joint bỏ DEF_>. Đuôi màu tím (giữa) / xanh (L) / hồng (R).
- **CTL_TailFan**: control xòe quạt chung, dial `fan` -1..+1 (-1 khép đuôi lại, 0 = tư thế gốc, +1 xòe rộng). Lái bằng driven key lên group gốc của 8 đuôi hai bên, nên control CTL_Tail*_1 vẫn key tự do. Đuôi giữa không xoay theo fan. Đã chụp thử cả 3 giá trị, đọc đúng chiều.

## Skin
- Tối đa 4 joint/đỉnh. Đuôi: mỗi đuôi chỉ ăn chuỗi xương của chính nó, trọng số theo quãng đường dọc đuôi. Tai theo độ cao, chân theo độ cao + trái/phải + trước/sau, đầu/thân/hông theo độ cao. Mặt nạ theo đầu (phần chóp lên tai theo tai).
- Đã xoay thử (skin_check): fan khép/xòe, từng đuôi 3 trục, đuôi giữa uốn 3 đốt, tai ra/tới, đầu quay/gật/ngửa, chân trước/sau, thân. Không rách, chưa thấy móp rõ.

## Chỗ còn yếu / chưa chắc
- Chân trước vung ngược chiều nhau ±30° thì chỗ hai chân dính nhau ở bụng kéo giãn ~2 lần (cạnh bé, nhìn ít lộ); hai chân cùng chiều thì sạch. Spine1 xoay 20° thì lưng sau kéo ~1,8 lần: nên giữ Spine1 dưới ~10°.
- Đuôi giữa cuộn cao 0,92 m (dài nhất): khi anim đuôi nên bẻ nhiều đốt, đốt cuối (Tail1_5) ăn cả vòng cuộn trên cùng.
- Control tròn chưa ôm sát mesh (chưa chạy fit sát), kích thước tạm. Joint chân/tai đặt theo số đo mesh, chưa nhìn kỹ bằng mắt ở cận cảnh; mặt nạ là 1 nửa mặt nên chưa rõ có bị lệch khi xoay đầu mạnh.
- Chưa Director, chưa playblast, chưa kiểm Unity. Không commit/push.

Đang đợi người dùng check rig rồi mới làm tiếp (idle/attack).

## Idle (2026-11-14) - 49 key (0-48), lặp (F48 = F0)
- File: `kitsune_nine_mist_idle.fv` (cùng thư mục với file rig). Script: `anim/idle.py`, `anim/run_idle.py`. Key mọi frame, curve đặt chế độ lặp (cycle).
- Hover 12 cm, hông nhấp nhô ±1,5 cm 1 nhịp/vòng; đầu/tai/chân trễ thân; 9 đuôi sóng chạy gốc→ngọn (mỗi đốt trễ 4F, mỗi đuôi lệch ~3F so với đuôi kề, vòng nhỏ lên-xuống + trước-sau); CTL_TailFan thở -0,05…+0,15.
- Tự kiểm: F0 = F48 đúng 0 cm; xoay tối đa 3,7°/frame (không xoắn); skin kéo tối đa 1,36 lần; đầu đuôi di chuyển 4-15 cm.
- Chưa Director, chưa playblast MP4, chưa xuất FBX (chờ "chốt").

## Attack (2026-11-14) - 31 key (0-30)
- File: `kitsune_nine_mist_attack.fv`. Script: `anim/attack.py`, `anim/run_attack.py`, kiểm: `anim/check_anim.py`. Cộng lên pose Idle F0, key mọi frame.
- 0-7 gồng: hạ hover 4 cm, ngả sau, đầu cúi, tai cụp, chân co, quạt khép (fan -0,7), ngọn đuôi cuộn ra sau/xuống. 7-12 bung (5F): thân bật lên 6 cm + tiến 6 cm, đuôi bật theo sóng (mỗi đốt trễ 1F). **12 = BẮN (gắn event)**, giữ tới 14: fan +1,0, đầu đuôi hướng ra ngoài/lên. 14-26 dư chấn: đuôi rung tắt dần, thân lún rồi nổi lại. **30 = đúng Idle F0** (đo 0 cm).
- Mắt đỏ lóe (VFX): đề xuất event bật F8, tắt F16.
- Tự kiểm: xoay tối đa 33°/frame (lúc bung F9, đúng ý snap), skin kéo tối đa +2,8 cm ở gốc tai (F14); từ trên xuống quạt bung ít (fan chỉ xòe trong mặt phẳng đứng) - chờ trả lời camera game.
- Chưa Director, chưa playblast MP4, chưa xuất FBX (chờ "chốt").

## Attack v2 (2026-11-14, theo góp ý người dùng: lấy đà đầu cúi xuống, đuôi cụp vào nhiều hơn)
- File: `kitsune_nine_mist_attack_v2.fv` (v1 giữ nguyên). Đầu cúi 24° ở F7 (v1: 8°), cúi dần từ F4; quạt khép hết (fan -1,0), ngọn đuôi cuộn vào gấp 1,7 lần v1, đốt cuối cong nhiều hơn; tai cụp sâu hơn. F12 bắn, F30 = Idle F0 giữ nguyên.
- Đo: F30 = F0 (0 cm); xoay tối đa 42,7°/frame lúc bung (F9); skin kéo tối đa +2,8 cm (gốc tai F14).

## Attack v3 (2026-11-14, "đuôi cụp hẳn vào người")
- File: `kitsune_nine_mist_attack_v3.fv` (v1, v2 giữ nguyên). Lấy đà F7-8: gốc mỗi đuôi quay ra sau ~48° và hạ xuống (đuôi thấp nhất xuống nhiều nhất), đuôi giữa ngả sau ~30°, các đốt còn lại cuộn thêm: nhìn từ trước 9 đuôi khuất sau thân. Giữ F7-8 rồi bung, F12 bắn, F30 = Idle F0 (0 cm).
- Đo: xoay tối đa 42,7°/frame (F12), đầu đuôi nhanh nhất 28,5 cm/frame (F11); skin kéo tối đa +4,2 cm trên cạnh dài 13 cm giữa đốt 2-3 đuôi giữa (F9, ~30%).
- Nhìn từ bên, đuôi duỗi ngang ra sau lưng (không áp sát lưng): nếu muốn áp sát hơn thì hạ đuôi xuống dọc hông.

## Attack v4 (2026-11-14, "F5-F9 cụp đuôi lộn xộn")
- File: `kitsune_nine_mist_attack_v4.fv` (v1-v3 giữ nguyên). Nguyên nhân lộn xộn: v3 vẫn trễ pha theo từng đuôi/đốt và còn sóng idle riêng từng đuôi ở lúc gồng. Sửa: F3-F8.5 mọi đuôi/đốt cùng một nhịp (không trễ), sóng idle tắt dần 85% khi cụp; trễ từng đốt chỉ vào lại từ lúc bung (F8.5-F11). Cụp đạt đỉnh F7, giữ tới F8.5.
- Đo: F30 = F0 (0 cm); xoay tối đa 44,5°/frame (F12 lúc bung); skin kéo tối đa +5 cm trên cạnh dài (F8, đuôi cụp).

## Attack v5 (2026-11-14, "v4 vẫn lộn xộn, xấu")
- File: `kitsune_nine_mist_attack_v5.fv` (v1-v4 giữ nguyên). v3/v4 lỗi vì xoay từng đuôi ra sau/xuống thêm bằng tay: mỗi đuôi bay một hướng, chồng chéo. v5 bỏ hết phần đó; cụp = dial CTL_TailFan về -1 và khép HẲN: 9 đuôi dựng thẳng thành MỘT bó sau lưng (đủ F5-F9), rồi bung đều ra theo nhịp quạt F9-F12. Để khép hẳn, trong file Attack v5 đã đổi driven key của fan -1 từ khép 55% lên 95% (file rig + Idle chưa đổi, nếu duyệt thì áp vào rig).
- Đo: F30 = F0 (0 cm); xoay tối đa 54,9°/frame (F11 lúc bung), đầu đuôi nhanh nhất 29 cm/frame; skin kéo tối đa +2,8 cm (gốc tai F14).

## Attack v6 (2026-11-14, "đoạn cụm vào đưa xuống đây")
- File: `kitsune_nine_mist_attack_v6.fv` (v1-v5 giữ nguyên). Bó đuôi cụp (F3-F8) giờ nằm xuôi ra sau lưng, hơi chúc xuống ~10-15° so với ngang, theo hình người dùng vẽ: cả bó xoay 78° quanh gốc đuôi (công thức pitch_tails trong anim/attack.py, bù trục xoay của group fan). Đầu đuôi thấp nhất 4,6 cm (không chạm đất). Bung F8-12: bó nhấc lên + quạt xòe cùng nhịp.
- Thêm: hai đuôi trong (Tail2 L/R) dính nhau ở gốc, trọng số 6 đỉnh mối hàn đã chia đều để khỏi rách khi hai đuôi quay khác nhau (chỉ trong file Attack v6; rig/Idle chưa đổi).
- Đo: F30 = F0 (0 cm); xoay tối đa 53°/frame (F11, lúc bung); skin kéo tối đa +2,8 cm.
