---
name: frolvy_rig
description: Rig nhân vật game trong Frolvy (app rigging giống Maya, điều khiển qua MCP frolvy) - kiểm model, đặt joint fit theo AdvancedSkeleton, Build/Rebuild Rig, skin chỉ bằng joint DEF, sửa skin theo vùng, thu gọn control, switch, picker, xuất cho Unity. Dùng skill này mỗi khi người dùng làm việc trong Frolvy với rig - "check model để đặt joint", "đặt joint", "build rig", "rebuild", "bind skin", "skin bị móp/kéo", "control bé/to quá", "tạo picker", "toggle fit", chỉnh ngón cái / cổ / đầu / giáp - kể cả khi không nhắc tên skill. Không dùng cho Rig Lab trên web (skill /rig) hay Spine 2D.
---

# Rig nhân vật game trong Frolvy

Frolvy là app rigging/anim giống Maya, mở trên máy người dùng. Mọi thao tác qua MCP `frolvy`:
`execute_code` (Python có sẵn `api`, mỗi lần gọi là một bước undo), `get_scene_info`, `find_api`, `get_viewport_screenshot`, `undo`.
Trả lời người dùng bằng tiếng Việt. Rig dùng cho **game, xuất sang Unity Humanoid**.

Công cụ dựng sẵn (chạy trong Frolvy, Python thuần vì Python của Frolvy không có numpy):

```python
import sys; sys.path.insert(0, r"D:\Project\AI_Anim\.claude\skills\frolvy_rig\scripts")
import importlib, frolvy_rig_tools as R; importlib.reload(R)
```

Đọc docstring đầu `scripts/frolvy_rig_tools.py` để biết các hàm. Plugin `tools/frolvy_plugins/fit_controls` lo việc đẩy control ra ngoài mesh.

## Luật người dùng đã chốt (rig game)

- **Chỉ joint base.** Không bật helper set (PRT/HLP/MUS), không twist, không bendy: `api.set_helper_set(False)`, `api.set_bendy_limbs(False)`, `twistJoints = 0`. Người dùng không cần các joint đó cho game.
- **Root_M là joint hông** (kiểu AdvancedSkeleton): Root nằm ở hông, nhãn `root`, không có joint Pelvis; Spine1, Hip, giáp hông nằm thẳng dưới Root. Mặc định 0.9.22+ của Frolvy (Root ở 0,0,0 + Pelvis) KHÔNG dùng cho rig game. Joint `DEF_Root_M` mang nhãn `root`.
- **Skin chỉ bằng joint DEF**, bỏ joint cuối/pivot (End, Heel, FootSide, Finger4), không cho thân ăn joint đạo cụ. Tối đa 4 joint mỗi đỉnh, bỏ weight < 1%.
- **Mảnh cứng** (giáp, mặt nạ, mắt, vòng tay, đệm gối, đạo cụ) gán 100% vào joint của nó. Giáp hông: chốt cuối của Bastion là **đi theo pelvis** (100% joint HipPad, con của Root, mép trên mảnh trên theo Root), không ăn Hip; trước đó đã thử "theo chân 50%" (50% HipPad + 50% Hip) rồi bỏ. Không constraint control giáp vào joint (sinh vòng lặp).
- **Không để joint xa ảnh hưởng.** Mỗi vùng chỉ ăn joint của nó và joint kề; tay chân không kéo thân; đầu và mặt nạ chỉ theo Head (cổ theo Neck); cổ áo/giáp thân theo thân.
- **Control vừa ôm mesh, dễ bấm**, không phải vòng khổng lồ: vòng rộng hơn mesh vài cm, IK chân là hộp ôm giày, control giáp nằm trên mặt tấm giáp. Đặt `fitScale = 6` cho control đã chỉnh tay để Fit Controls không phóng to lại.
- Chỉnh tay xong thì **lưu** (`api.save_scene(path)`); chỉ hỏi trước khi mở file khác nếu scene đang có thay đổi chưa lưu.

## Quy trình

### 1. Kiểm model (trước khi đặt joint)
`R.check_model(api)` rồi `R.sections(api, "Body", 1, [...])` / `sections(api,"Body",0,[...])` để lấy đường tâm chân, thân, tay; cắt qua cạnh mesh chính xác hơn lấy đỉnh trên model ít poly. Báo: cao, đơn vị (mét, Y lên, mặt nhìn +Z, phải là −X), đối xứng, từng mảnh rời và joint nó sẽ gắn vào, tay nào cầm đạo cụ, các mốc xương.

### 2. Đặt joint fit
- Đặt **mới từ số đo của chính model** khi người dùng yêu cầu ("đặt lại từ đầu theo cách bạn vừa check"), không bê bảng cũ.
- Viết bảng (tên AdvancedSkeleton, nhãn: root, spine, chest, neck, head, clavicle, shoulder, elbow, wrist, finger, thumb, thigh, knee, ankle, toe, heel, foot_inner, foot_outer, prop; "" = joint cuối), chỉ bên giữa + phải; xuất `.fvfit` vào `Documents\Frolvy\fit_skeletons\` và `api.load_fit_skeleton(path)`. Mẫu script: `references/fit_table_example.md`.
- Ngón tay: quét ngang bàn tay (khe giữa các ngón) để lấy tâm từng ngón; tay nằm trong đạo cụ thì đặt đối xứng theo tay kia.
- Cổ/đầu: lấy tâm của **mũ/đầu** (lát cắt cao, không lẫn giáp thân), Head ngang cằm, HeadEnd ở đỉnh.
- Ngón cái: trục X dọc xương, Z = X × (hướng về gốc ngón giữa), `set_joint_orient` rồi đưa kênh xoay về 0 (Frolvy tự bù kênh xoay) và tính lại translate con. Thử: xoay +30° quanh Z, đầu ngón phải lại gần gốc ngón giữa.
- `api.save_fit_skeleton(path)` sau mỗi lần chỉnh.

**Khi người dùng tự chỉnh joint rồi bảo "chỉnh các xương còn lại":** so với file fit đã lưu (translate cục bộ) để tìm joint họ đổi, **giữ nguyên** joint đó, rồi đưa các joint con trực tiếp về vị trí thế giới cũ (các joint sâu hơn tự về). Joint bị kéo theo phải về đúng mesh (bàn tay, súng, giày…), không để thò ra ngoài.

### 3. Build / Rebuild
1. `R.zero_controls(api)` **trước mọi lần build**: Rebuild nướng pose hiện tại vào group offset, rig sẽ nghiêng dù control về 0. Nếu báo có group offset bị xoay → pose đã bị nướng: hoàn tác về trước Rebuild hoặc làm lại.
2. `api.set_helper_set(False); api.set_bendy_limbs(False); api.build_rig()` hoặc `api.rebuild_rig()` (Rebuild giữ skin + hình control).
3. `R.after_rebuild(api, one_side=("Weapon","Arrow"), prop_side="_R")` - làm lại mọi thứ Rebuild bỏ/để sai: xóa đạo cụ bị mirror sang bên kia (và node `wire_` chết, **không bao giờ xóa `wire_DEF_Root_M_*`**), nối translate cho control FK, đặt joint DEF đúng fit, dời pivot control về joint, sửa dấu gập ngón cái, gắn lại switch, đặt lại nhãn. Kiểm in ra: `DEF vs fit: []`, `check_rig: []`, `rig moves: True`.
4. Chạy Fit Controls (plugin) cho control mới, rồi thu gọn tay những control quá to.
5. Kiểm lại sau Rebuild (Bastion từng sót cả ba): switch còn đúng cha (`R.parent(api, "CTL_ArmSwitch_L_grp")` = `CTL_Wrist_L`…, sai thì `R.reparent_switches(api)`), đạo cụ bị lật sang bên kia đã thật sự bị xóa (`DEF_Weapon_L` không còn), vòng control ngón cái nằm trên ngón cái.
6. Toggle Fit (`api.toggle_fit()`) để người dùng chỉnh joint; chỉ hiển thị, không đổi rig.

### 4. Skin
**Quy trình chuẩn** (Bastion 2026-10-31, người dùng đã duyệt từng vùng):
1. Bind: `api.select([mesh]); api.bind_skin(R.influences(api))`; đạo cụ bind riêng vào joint của nó rồi `R.set_rigid`.
2. Đo các mốc chiều cao của model mới (joint, mép đai trên/dưới, gối, cổ giày, mũi giày), chép `R.BASTION_SKIN` thành cfg mới, sửa số và bảng `rigid` (chỉ số shell → joint; xem `Mesh.shells`).
3. `R.skin_pass(api, "Body", cfg, head_neck_keep=<chỉ số đỉnh mũ+mặt nạ+cổ thật>, profile=True)`. Hàm này làm theo thứ tự:
   - chia lại thân (Root/Spine1/Chest) và chân (Hip/Knee/Ankle/Toes) theo chiều cao;
   - áp luật đai dưới, nách, không Head/Neck ngoài đầu–cổ, không ăn bên kia;
   - làm cứng shell **cuối cùng**.
4. Sửa đầu–cổ, bàn tay, vai theo các mục dưới.
5. Mỗi lần **smooth/hammer** xong: `R.skin_pass(..., profile=False)` để giữ phần smooth nhưng áp lại luật cứng (đai dưới, nách, cổ áo, bên kia, shell). Hàm chạy lại nhiều lần không đổi gì thêm.
6. Thử bằng **tư thế thật của người dùng**: `R.pose_stretch(api, m, vùng, rest, pose)` (so với tư thế gốc); `edge_stretch` chỉ dùng khi scene chưa có pose. Cạnh rất ngắn (< 1 cm) cho tỉ lệ giãn ảo, nhìn khoảng cách thật.
7. Lưu weight ra JSON trong scratchpad trước mỗi lần sửa lớn để trả lại khi người dùng không ưng.

**Luật từng vùng** (lý do, để áp cho model khác):
- Luật chung (chỉ gỡ, không thêm): mỗi đỉnh thuộc đoạn xương gần nhất cùng bên, chỉ ăn xương đó + cha + con kề; tay chân không kéo thân, thân không kéo tay chân.
- Bàn tay: đỉnh ăn joint xa hơn joint gần nhất > 1,5 cm (không phải cha/con) là sai → hammer vài lần, phần còn lại gỡ hẳn về joint gần nhất.
- Vùng đầu–cổ: mũ + mặt nạ (kể cả tấm chắn mặt nhô ra trước, góc dưới, mép sau) 100% Head; cổ thật Neck; cổ áo 100% thân (Chest), KHÔNG một vertex cổ áo nào ăn Head hay Neck, kể cả khi mũ/mặt nạ hàn liền cổ áo (chấp nhận dải nối giãn). Kiểm: chọn các vertex có Head rồi chụp viewport; góc trong cổ áo hay lọt vào Head, lọc bằng khoảng cách ngang tới trục đầu (lớn hơn bán kính mũ thì là cổ áo), nhưng thành trong cổ áo nằm sát mũ (Bastion: |x| 0.09–0.12, cao tới đỉnh cổ áo phía sau) lọt qua bộ lọc này, nên đưa ảnh vùng Head cho người dùng chọn tiếp; sau đó `deform_test` xoay Neck/Head: không vertex nào ngoài vùng Head được dời. Đừng hammer/smooth cổ áo với Neck để bớt giãn dải nối: Bastion thử rồi, ngửa cổ mạnh là mảng ngực quanh cổ bị kéo theo, người dùng bắt bỏ. Lưới cổ thật nằm sau mặt nạ (Bastion 34 + 12 đỉnh mặt sau ống cổ) theo Neck, không phải Head.
- Thân (Root/Spine1/Chest, `skin_torso` + `skin_lower_belt`): giữ phần weight tay/chân/giáp, chia lại phần cột sống theo chiều cao, chuyển mượt giữa các joint (Bastion: Đai dưới gần như Root (< 1,115 m; chốt: Spine1 15% ở mép trên giảm về 0 ở 1,0 m cho đỡ cứng khi cúi; người dùng hai lần: Spine1 làm đai dưới "ăn vào trong"), Root→Spine1 dồn trong đai trên 1,115–1,20; smooth thân xong phải áp lại luật này; Spine1 1,14–1,26; Spine1→Chest 1,26–1,40; Chest trên đó). Bind mặc định để Root 40% ở bụng và Root 89% sát Chest ở sườn → xé ×25 khi xoay thân; sau khi chia lại còn ×1,9.
- Chân (`skin_legs`): chia lại phần Hip/Knee/Ankle/Toes theo chiều cao (giữ Root ở háng, giáp hông): Hip trên gối +5 cm, Hip→Knee trong ±4 cm quanh gối, Knee cả ống chân, Knee→Ankle 3–9 cm trên cổ chân, Ankle dưới đó, Toes chỉ ở mũi giày trước khớp ngón. **Bỏ qua các mảnh rời (shell) khi chia theo chiều cao**: giáp gối (Bastion shell 11–16) phải cứng 100% Knee, giáp hông theo HipPad/Root; chia theo chiều cao làm giáp gối bị bẻ móp khi gập gối. Mọi lần chia lại/smooth xong: chạy lại bước làm cứng shell. Bind để Hip xuống tới ống chân, Knee xuống bàn chân, Ankle/Toes lên bắp chân → nhấc chân móp gối, xoay bàn chân móp bắp chân. Thử bằng tư thế thật của người dùng (đo so với rest, không dùng `edge_stretch` khi đang có pose vì nó lấy pose hiện tại làm gốc).
- Ngực cạnh nách (`skin_armpit`): Shoulder không ăn tấm ngực phía trong khớp vai (trần 0→50% từ 29→36 cm tính từ tâm), Scapula mặt trước ngực trần 35%, về 0 về phía xương ức. Smooth vai không có luật này đã làm giáp ngực móp khi hạ tay (Bastion: ×3,1 → ×1,1 sau khi áp).
- Vai: smooth nhẹ (hammer 0.5 × 3) vùng Scapula/Shoulder/Chest, bỏ giáp vai, chép weight bên trái sang bên phải theo cặp đỉnh đối xứng để hai vai giống nhau, rồi áp luật nách.
- Giáp hông: theo pelvis (HipPad, con của Root), hàng mép trên mảnh trên theo Root như bản lề; mảnh dưới theo joint của nó. Giáp gối cứng theo Knee.
- Kiểm: `R.skin_report(api,"Body")` (ở tư thế gốc: khi rig đang có pose nó báo "far" giả), `R.deform_test(...)`, `R.pose_stretch(...)`. Chụp viewport ở tư thế người dùng để chắc.
- **Háng: KHÔNG trộn weight chân bên kia để chữa giãn** (Windy 2026-11-04, người dùng: "Check skin hai bên đùi, đang ảnh hưởng lẫn nhau"): chia đối xứng dải ±6 cm làm mặt trong đùi này đi theo đùi kia. Đúng: đỉnh lệch khỏi đường giữa chỉ ăn chân cùng bên; đường giữa + mặt trong đùi sát háng chuyển một phần weight chân sang `Root_M` (khung chậu), giảm dần theo khoảng cách. Kiểm: nhấc/xoay một chân, đùi kia dời ≈ 0.
- **Soát weight ở MỌI mức > 0, không chỉ ≥ 5 %** (Windy 2026-11-04, người dùng: "Joint ở chân đang ảnh hưởng đến skin bàn tay"): lần đầu lọc ≥ 5 % sót 8 đỉnh ngón cái ăn 1,3–4,4 % joint mũi chân, nhấc chân kéo ngón cái 3,9 cm. Kiểm bằng chuyển động thật: nhấc/xoay từng chi, đo đỉnh của vùng KHÁC dời bao nhiêu (`api.mesh_data(obj, True)` cho vị trí đã biến dạng), phải 0. Skin của team (joint tên team, không phải DEF) thì `skin_report`/`deform_test` không dùng được: tự quét theo cây `root` (`work/endless_kicker/rig/skin_check.md`).
- SkinTokens (plugin AI skin) đã thử trên Bastion: model dồn 100% vào một xương phụ → không dùng được; bind bằng Frolvy rồi dọn theo luật trên.

### 5. Control, switch, picker
- Switch FK/IK **không thể đi theo joint DEF** (DEF đọc `fkIk` của chính switch → vòng lặp, cả rig đứng). Gắn: switch tay và cột sống dưới control FK cuối, switch chân dưới IK foot (chân ưu tiên IK). Phóng switch lên ~14 cm, không để lọt trong đạo cụ.
- Constraint control vào joint trong cùng cây control cũng có thể bị coi là vòng lặp → sau mỗi constraint/wire mới gọi `R.check_rig_moves(api)`; nếu rig đứng thì gỡ ngay.
- Ngón cái khi curl/handPose phải **xoay vào lòng bàn tay** (ngang qua lòng, về phía ngón út), không gập xuống hay lật lên mu: Rig Builder chỉ quay trục Y của ngón cái → dùng `R.thumb_into_palm(api)` (quay trục Z, thêm chút Y ngược; `after_rebuild` đã gọi). Kiểm: nắm tay (handPose 2) thì đầu ngón cái nằm dưới đốt giữa ngón trỏ/giữa. Sau Rebuild còn kiểm **vòng control ngón cái**: Rebuild giữ hình control theo trục cũ, Bastion bị lệch 9–10 cm về phía cổ tay và to gấp đôi → đặt lại vòng vuông góc xương, tâm ở ~45% đốt, bán kính ôm đốt (Bastion 5/4/3,3 cm), rồi `fitScale` = 6 để Fit Controls không đổi.
- Rig Builder đã có `curl`, `spread`, `handPose` trên switch tay - không thêm control ngón tay riêng trừ khi được yêu cầu.
- Picker: `add_picker_button(pk, label, x, y, w, h, nodes)` lấy **x, y là TÂM nút** (file `.fvpicker` lưu `"centre"`), không phải góc; truyền góc thì nút lệch nửa cỡ, nút to lệch nhiều (G-LumberCity 2026-11-02). Mẫu đầy đủ: `work/g_lumbercity/rig/make_picker.py`.
- Picker: `api.create_picker` + `add_picker_button` theo hình chiếu chính diện (phải đỏ, trái xanh, giữa vàng, giáp/đạo cụ xanh lá, switch tím; FK chữ nhật, IK tròn); chân ưu tiên IK (IK Foot/Knee to, FK nhỏ màu nhạt ở cột ngoài); hai bảng bàn tay + nút All. Xóa nút cũng phải sửa nút All (chứa mọi control). `api.export_picker(pk, <thư mục Rig>/<nv>.fvpicker)`.

## Bẫy của Frolvy (đã gặp)

- **Undo lẫn thao tác của người dùng.** Hoàn tác nhiều bước có thể lùi quá cả việc người dùng làm. Ưu tiên sửa tiến (xóa/nối lại bằng tay); sau undo luôn kiểm lại trạng thái trước khi làm tiếp. Người dùng bấm Ctrl+Z cũng có thể khôi phục thứ vừa xóa → kiểm lại khi họ báo "vẫn còn".
- **Biến Python dùng chung giữa các lần `execute_code`** (globals giữ lại): đừng tái dùng tên như `region`, `base` cho kiểu khác.
- `remove_joint` giữ translate cục bộ của con (cả cây nhảy lên) và xóa nhãn joint cha → đặt lại translate con theo vị trí cũ và đặt lại nhãn.
- `set_joint_orient` tự bù kênh xoay để trục thế giới không đổi → phải đưa xoay về 0.
- `autoSnap` chép pose của bên kia (IK↔FK) sang control khi chuyển switch → tắt autoSnap khi chuyển trong lúc thử/bind, và đưa control về 0 trước khi bật lại (đã từng làm `CTL_IKAnkle_L` lệch 7 mm, `CTL_PoleLeg_L` lệch 5,6 cm).
- Tính lại translate gốc của DEF (`sync_rest`) phải làm ở **FK, mọi control = 0**; tính lúc chân đang IK thì khung xương cha bị IK xoay → hằng số sai (hai gối lệch 7–8 mm ở FK). Kiểm bằng `R.def_vs_fit_both(api)`: cả `current` và `fk` phải rỗng, so cả hai bên L và R.
- **KHÔNG BAO GIỜ `delete_selection()` khi đang ở component mode (face/vertex).** Chỉ số mặt/đỉnh là chung cả scene, nên lệnh xóa nhầm mặt của mesh khác (2026-10-31: Body mất nửa dưới, VK còn 5 mặt), trả `True` và mesh đang chọn không đổi; Ctrl+Z không lấy lại. Frolvy không có lệnh xóa/tạo mặt: tạo mesh mới bằng cách ghi FBX ASCII rồi `api.import_file` (OBJ không nhận). Trước mọi `delete_selection` luôn `set_component_mode("object")` và kiểm `api.selection()`. Khôi phục: nạp lại FBX model gốc, bind, chép weight theo vị trí từ mesh còn lại + bản lưu weight (khóa = id đỉnh toàn cục theo thứ tự VK, Body, VK_Bullet).
- Skin vẫn trỏ tới joint đã xóa sau Rebuild (ví dụ `DEF_Pelvis_M`) → lưu weight trước, map sang joint mới.
- App Claude chạy trong MSIX: file mình tạo trong `AppData\Local` có thể bị chuyển vào `Packages\Claude_…\LocalCache`, Frolvy không thấy → ghi/chép file đó bằng Python bên trong Frolvy.
- Unity Humanoid bỏ translate của xương tay/chân/cột sống (chỉ giữ hông); translate trên đạo cụ (mũi tên trượt) thì vẫn xuất được.
- **Ràng buộc đọc một node đã bị ràng buộc / joint DEF làm node đó đứng cứng** (2026-11-02): group rìu constrain vào `DEF_Wrist_R` → cổ tay DEF phải thôi chạy; constrain vào joint team `Wrist_R` (đã constrain vào DEF) → `Wrist_R` thôi theo. `check_rig()` vẫn `[]`, `check_rig_moves` mặc định chỉ thử tay TRÁI → luôn thử cả 4 tay chân. Cách làm: đặt group control làm con trực tiếp của joint DEF.
- **Xuất FBX luôn ghi cả scene** (rig, DEF, fit, group); xoá node trước khi xuất không có tác dụng (node con thành "ma", vẫn bị ghi). `delete_node` trả False, node constraint không chọn được. Lọc sau khi xuất bằng `tools/fbx_ascii_keep.py` (FBX Frolvy là ASCII).
- Model đo bằng **cm** (FBX của team): Rig Builder vẽ control cỡ mét → chìm trong mesh; nhân bán kính fit ×100.
- **Fit Controls hỏng trên mesh low-poly hở** (đế giày, cổ áo hở → phép đếm chẵn/lẻ sai): nó phóng vòng tới ×6, chạy lần hai còn nhân dồn. Người dùng 2026-11-02 chê "chưa gọn". Cách làm gọn: đo mặt cắt mesh (cắt cạnh, chỉ lấy đỉnh có skin trội thuộc khớp đó — `vertex_weights` dùng id đỉnh TOÀN CỤC `R.Mesh(...).G`, mesh khác đứng trước thì chỉ số lệch) rồi đặt bán kính = mặt cắt + 2–3 cm (ngón +0,8); vòng chìm trong quần/giày/thân thì dời hình vòng dọc xương tới chỗ chi lộ ra (đùi dưới mép quần, trên giày, mũi giày, bắp tay, trán); IK chân = hộp ôm giày; scapula = đĩa nhỏ trên vai, ngoài vùng đầu; vòng FK phải vuông góc với xương. Chỉ đổi điểm curve, không đổi pivot. Lưu hình bằng `curve_points` ra JSON để dựng lại (mẫu `work/g_lumbercity/rig/ctl_shapes.json`).

- **Frolvy 0.9.36 chỉ cho script AI ghi vào `Documents\Frolvy` và `%TEMP%`** (2026-11-04, Windy): `os.makedirs`/`open(...,"w")`/`save_scene` ra `E:\tvc_source` bị chặn. Làm việc trong `Documents\Frolvy\<dự án>\`, chép sang thư mục team bằng lệnh ngoài Frolvy.
- **Driven key và node toán (reverse/clamp → `set_node_output`) KHÔNG lái được trọng số constraint** (`parentConstraintN.w0/w1`) dù `driven_keys()` liệt kê và tài liệu nói được (2026-11-04): constraint vẫn trộn theo giá trị gốc. Chỉ `set_attr(...w1, 0)` trực tiếp là có tác dụng (không key được). → Không làm công tắc không gian bằng trọng số: prop theo MỘT control trong tay + control đích world, nướng theo đích khi cần bay tự do (`work/endless_kicker/rig/build_windy_rig.py` `staff_bake_world`).
- **`api.constraints()` trả MỌI constraint của scene**, không theo vùng chọn; `rename` constraint trả False. Tìm constraint của mình bằng tập trước/sau khi tạo. (Đã từng nhận nhầm `spineWaist_M` của Rig Builder và gắn driven key vào nó.)
- **Sau `open_scene` (vd cuối `export_clip`) undo trống và `new_scene()`/`open_scene()` trả False nếu scene bị coi là có thay đổi**; lệnh `import_file` ngay sau đó sẽ nhập CHỒNG vào scene rig. Luôn `assert api.new_scene()`; muốn bỏ thay đổi thì `save_scene(<temp>\junk.fv)` rồi `open_scene(file sạch)`.
- Tay "găng" (chỉ ngón giữa + ngón cái, Windy): fit Middle1–3 + Thumb1–3, Rig Builder dựng được; `fix_thumb_curl` đã sửa để lấy đốt cuối có thật (ThumbFinger3).
- Tự render mesh đã biến dạng khi viewport Frolvy quá nhỏ: `api.mesh_data(mesh, True)` → JSON trong temp → `work/endless_kicker/rig/render_posed.py`.

## Unity Generic: rig Frolvy lái skeleton của team

Khi Unity nhập FBX dạng **Generic** (`animationType: 2` trong `.meta`), clip chỉ chạy trên đúng skeleton cũ (tên, cây joint kể cả joint phụ `*Part1_*`, `root`, đạo cụ, hướng trục). Đừng xuất joint DEF đổi tên. Làm như G-LumberCity (`work/g_lumbercity/rig/build_worker_rig.py`):
1. Nhập FBX model có mesh + skin của team; skeleton team giữ nguyên làm skeleton xuất, mesh giữ skin team.
2. Fit đặt đúng vị trí joint team (chỉ thêm joint cuối / pivot chân), Build Rig, `after_rebuild`.
3. Mỗi joint team `constrain('parent', True)` vào DEF tương ứng; joint phụ theo DEF cha; `root` theo `CTL_Main`; đạo cụ theo control riêng (group là con joint DEF cổ tay).
4. Kiểm: mọi joint team giữ offset với DEF khi kéo IK/FK cả hai bên (`follow_test`).
5. Xuất: lưu scene anim → (scene có anim layer: `frolvy_layers.bake_for_export` trên bản sao trước) → bake joint team → `export_scene` → mở lại scene → `fbx_ascii_keep.py` chỉ giữ cây `root` + mesh. Nhập lại để so tư thế (phải lệch 0).

## Sửa anim: luôn trên anim layer (người dùng 2026-11-04)
Sửa anim đã có (góp ý, clip đã xuất) thì không key lên Base: mỗi vòng sửa một layer additive `fix_r<N>_<nội dung>` bằng `scripts/frolvy_layers.py` (`start_fix`, `key`/`offset` kèm `hold`, `bake_for_export` trước khi xuất). Lý do và các bước: `.claude/skills/animation/knowledge/details/user_blocking.md#sửa-anim-trên-frolvy`. Lỗi layer của Frolvy 0.9.36: `set_key` trên layer cộng thêm lưu tổng (cộng đôi) và key mọi kênh của node; `flatten_layers` / `bake_keys` / `export_scene` cộng đôi layer cộng thêm (feedback #14–#16).

## Báo kết quả
Mở đầu bằng việc đã làm được gì. Ghi số đo cụ thể (vị trí, %, số đỉnh), những gì giữ nguyên, những gì chưa kiểm (ví dụ chưa thử pose thật), file đã lưu chưa. Ghi bài học mới vào skill này.
