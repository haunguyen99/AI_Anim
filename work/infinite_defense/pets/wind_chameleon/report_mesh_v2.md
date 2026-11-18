# Pet 16 Wind Chameleon — chuyển rig + Idle/Attack sang mesh mới (2026-11-18)

## Kết quả
Rig, Idle (48F, lặp) và Attack (30F, bắn f13) đã chuyển sang mesh mới, key giữ nguyên 100% (so từng kênh từng frame với bản chốt: lệch 0). Chưa xuất FBX, chưa chép Unity, chưa git.

## File (thư mục `Pet_16_Wind_Chameleon/v2_mesh_moi/` trong repo tvc_source)
- `wind_chameleon_rig_v2.fv` — rig + skin mesh mới, mọi control = 0
- `wind_chameleon_idle_v2.fv` — 48F, f48 = f0 (đo mesh: giống hệt), chế độ lặp
- `wind_chameleon_attack_v2.fv` — 30F, bắn f13, f30 = Idle f0
- `shots/` — ảnh tự kiểm cạnh / trước / trên (attack_side_v2, attack_front_v2, attack_top_v2, idle_side_v2)
- Script: `work/infinite_defense/pets/wind_chameleon/v2/` (skin_v2, apply_skin_v2, shift_joints_v2, load_anim_v2, skin_check_v2, clip_metrics_v2, shot_v2, sheet_v2)

## Mesh mới
- 741 đỉnh, 1 mesh `Pet_Wind_Chameleon` gồm 4 mảnh rời: thân (562, đã liền cả đuôi, mào, chân, tấm đế), lưỡi (89), 2 mắt (45 + 45, mỗi mắt là quả cầu hở một đầu).
- Quay 180° quanh Y rồi freeze → mặt +Z, Y lên, đế chân y ≈ 0. Cao 0,77 như cũ. Thân dài -0,47…+0,49 (cũ -0,49…+0,49); con số 1,20 trong brief là do lưỡi.
- Miệng: không còn lỗ to như mesh cũ mà là ống tròn nhỏ (bán kính 3,8 cm) ở (0; 0,32; z 0,41–0,49), lưỡi thò ra từ trong ống này.
- Tấm đế dưới chân: thật ra là đế phẳng của 4 bàn chân (30 đỉnh ở y ≈ 0), không phải mảnh thừa. Đã skin vào chân/ngón, không xóa.

## Skin
- Dùng lại logic cũ (vùng + làm mịn theo cạnh mesh; đuôi theo quãng đường bề mặt từ gốc đuôi), chỉnh theo hình mới: miệng, đường cắt hàm, đế chân (mép trong đế bám chân thay vì thân).
- **Má và mắt (sửa sau khi gắn texture):** 2 quả cầu rời hai bên là MÁ phồng (texture xanh), còn MẮT là vòm trắng có con ngươi nằm trên đầu (một phần của thân). Skin: 2 quả cầu 100% Cheek_L/R; vòm mắt gán Eye_L/R theo khoảng cách (bán kính 8–11,5 cm quanh tâm vòm). Lưỡi: theo chiều dài vào 4 đốt. 39 joint DEF, tối đa 4 influence, tổng = 1. Đối chiếu trọng số cũ: 152/562 đỉnh thân đổi joint chủ đạo, hầu hết chỉ sang joint kề (đốt đuôi 4↔5, hông↔thân), 20 đỉnh quanh mắt cũ chuyển sang Head vì mắt đã tách ra.
- Xoay thử 30° từng control: không có méo thảm họa; thân/cổ/đầu 30° giãn cạnh tối đa ≈ ×2,5, đuôi Tail2 rx 30° nén một cạnh gốc đuôi xuống ×0,11 (cạnh ngắn, giống bản cũ). Biên độ clip dùng nhỏ hơn nhiều.
- Chạy cả hai clip: giãn cạnh tối đa ×1,2–1,5 (Idle ×1,34, Attack ×1,54), bản cũ lên tới ×7,2 ở miệng lúc bắn → bản mới sạch hơn rõ. Co cạnh nhỏ nhất ×0,20 ở lưỡi lúc thu (bản cũ ×0,22).

## Hai chỗ khác bản cũ (cần user biết)
1. **Lưỡi mesh mới nằm trước lưỡi cũ đúng 0,099 m** (z 0,316–0,735 so với 0,216–0,636; dài vẫn 0,42 m). Để Idle vẫn thụt hẳn vào miệng và Attack đúng tầm cũ mà không đụng key đã chốt, tôi **lùi cả mảnh lưỡi về sau 0,099 m** (chỉnh đỉnh lúc bind, khớp lưỡi giữ nguyên vị trí cũ). Hệ quả: tư thế bind của lưỡi ngắn hơn mesh artist 10 cm; Idle đầu lưỡi ở z 0,39 (trong miệng, đúng như cũ), Attack f13 lưỡi ra tới z 0,83 (đúng như cũ). Nếu để nguyên lưỡi artist: đầu lưỡi lúc Idle chạm môi (z 0,49) và thò ra ~2 cm (đã thử, thấy rõ), Attack vươn thêm ~9 cm (tới 0,92). Muốn theo mesh artist thì phải sửa key Idle (thụt thêm ~10 cm) và quyết tầm thè Attack: hỏi user.
2. **Joint mắt và má dời** (control dời cùng, key không đổi): Eye từ (±0,24; 0,335; 0,30) lên tâm vòm mắt (±0,19; 0,465; 0,285); Cheek từ (±0,13; 0,32; 0,34) ra tâm quả cầu má (±0,21; 0,315; 0,303).
3. **Má phồng trông to hơn bản cũ:** key scale má giữ nguyên, nhưng giờ nó phồng cả quả cầu nên đỉnh f8–f10 mỗi quả to ≈ 2 lần và che một phần dưới mắt (xem `shots/attack_tex_front_v2.png`). Nếu thấy quá tay thì giảm key scale má (cần user duyệt vì là key đã chốt).

## Chưa chắc / chưa kiểm
- Chưa mở FBX trong Unity, chưa xuất FBX (chưa "chốt"), chưa playblast MP4, chưa gọi Director. Tự kiểm bằng ảnh viewport (cạnh / trước / trên) + đo số.
- Các mảnh trong mesh mới: vòng lỗ hở 14 đỉnh ở hai bên đầu (y 0,40–0,54, x ±0,11…0,25) là miệng của hai vòm mào mắt, nằm chìm trong đầu, không thấy từ ngoài. Không xử lý.
- Chưa dò xuyên mặt giữa đuôi cuộn và mào ở mọi frame (key giữ nguyên, hai hình khối gần giống cũ; ảnh Idle/Attack không thấy xuyên).
- Quy trình dựng: mở `rig_v2` → `apply_skin_v2.py` → `load_anim_v2.py` (nạp key cũ qua thư viện anim của Frolvy, đã xóa bản tạm). Frolvy chỉ mở được scene mới khi scene hiện tại đã lưu; ghi đè file khác tên đang có sẽ trả False (xóa file trước).

## Texture (gắn thêm theo yêu cầu user)
- Vật liệu `M_Pet_WindChameleon` + `T_Pet_wind_chameleon.png` đã gắn vào mesh trong cả 3 file _v2. UV khớp texture (mắt trắng có con ngươi, miệng hồng, đuôi sọc, mào đỏ).
- Frolvy hiển thị PNG lật dọc (giống ca .tga của Hero), nên dùng bản lật `v2_mesh_moi/T_Pet_wind_chameleon_flipV.png` (copy từ texture gốc, không sửa gốc). File .fv trỏ tới bản này. Texture trong Unity vẫn là file gốc, không lật.
- Ảnh tự kiểm có texture: `shots/idle_tex_side_v2.png`, `idle_tex_front_v2.png`, `attack_tex_side_v2.png`, `attack_tex_front_v2.png`.

## Chốt + xuất FBX (2026-11-18, lệnh "chốt" của user)
- Đã gộp: `wind_chameleon_rig.fv`, `_idle.fv`, `_attack.fv` trong thư mục Pet giờ là bản mesh mới (bản cũ bỏ, còn trong git của repo tvc_source). Texture `tex/T_Pet_wind_chameleon_flipV.png`, mở lại 3 file đều thấy texture. Thư mục `v2_mesh_moi/` đã xóa; ảnh tự kiểm chuyển sang `work/infinite_defense/pets/wind_chameleon/shots_v2/`.
- 3 FBX xuất đè (qua `finalize_v2.sh`): Base (1 mesh, 1 Skin, 34 Cluster, 1 BindPose, 0 AnimationStack, UnitScale 100), Idle (take Idle, 48F, 351 curve, Dummy), Attack (take Attack, 30F, 351 curve, Dummy). Cả hai file anim: 0 mesh/deformer, 39 xương trùng tên Base. Không có nan/inf, không vật liệu/texture trong FBX (texture gắn lại trong Unity).
- Chưa kiểm bằng Unity batchmode (chưa import thử), chưa chép Unity.
