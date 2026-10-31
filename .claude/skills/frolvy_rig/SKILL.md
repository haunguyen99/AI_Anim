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
- **Mảnh cứng** (giáp, mặt nạ, mắt, vòng tay, đệm gối, đạo cụ) gán 100% vào joint của nó. Giáp hông "đi theo chân 50%" = skin 50% joint giáp + 50% Hip cùng bên (constraint lên control giáp sinh vòng lặp).
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
5. Toggle Fit (`api.toggle_fit()`) để người dùng chỉnh joint; chỉ hiển thị, không đổi rig.

### 4. Skin
1. Bind: `api.select([mesh]); api.bind_skin(R.influences(api))`; đạo cụ bind riêng vào joint của nó rồi `R.set_rigid`.
2. Làm cứng các mảnh rời theo `Mesh.shells` (giáp, mặt nạ…); gỡ weight joint giáp khỏi thân mềm.
3. `R.fix_cross_side(api, R.Mesh(api,"Body"))` - giày và mặt trong đùi rất hay ăn chân bên kia.
4. Luật vùng (chỉ gỡ, không thêm): mỗi đỉnh thuộc đoạn xương gần nhất cùng bên, chỉ ăn xương đó + cha + con kề (cho thêm joint mà đoạn xương gần không quá 6 cm); cột sống bỏ khi đỉnh cao/thấp hơn đoạn xương > 15 cm; Neck bỏ dưới 1,52 m và ngoài vai; Head chỉ ở đầu.
5. Vùng đầu–cổ: mũ + mặt nạ (kể cả tấm chắn mặt nhô ra trước, góc dưới, mép sau) 100% Head; cổ thật Neck; cổ áo 100% thân (Chest), KHÔNG một vertex cổ áo nào ăn Head hay Neck, kể cả khi mũ/mặt nạ hàn liền cổ áo (chấp nhận dải nối giãn). Kiểm: chọn các vertex có Head rồi chụp viewport; góc trong cổ áo hay lọt vào Head, lọc bằng khoảng cách ngang tới trục đầu (lớn hơn bán kính mũ thì là cổ áo), nhưng thành trong cổ áo nằm sát mũ (Bastion: |x| 0.09–0.12, cao tới đỉnh cổ áo phía sau) lọt qua bộ lọc này, nên đưa ảnh vùng Head cho người dùng chọn tiếp; sau đó `deform_test` xoay Neck/Head: không vertex nào ngoài vùng Head được dời.
6. Ngực cạnh nách: Shoulder không ăn phía trong khớp vai (về 0 ở ~30 cm từ tâm), Scapula giảm một nửa ở mặt trước ngực.
7. Kiểm: `R.skin_report(api,"Body")`, `R.deform_test(...)` (mesh_data chỉ trả vị trí gốc nên phải tự tính skin), `R.edge_stretch(...)` cho chỗ móp/rách. Chụp viewport để chắc mesh không lệch ở tư thế gốc sau khi joint dời.
8. SkinTokens (plugin AI skin) đã thử trên Bastion: model dồn 100% vào một xương phụ → không dùng được; bind bằng Frolvy rồi dọn theo luật trên.

### 5. Control, switch, picker
- Switch FK/IK **không thể đi theo joint DEF** (DEF đọc `fkIk` của chính switch → vòng lặp, cả rig đứng). Gắn: switch tay và cột sống dưới control FK cuối, switch chân dưới IK foot (chân ưu tiên IK). Phóng switch lên ~14 cm, không để lọt trong đạo cụ.
- Constraint control vào joint trong cùng cây control cũng có thể bị coi là vòng lặp → sau mỗi constraint/wire mới gọi `R.check_rig_moves(api)`; nếu rig đứng thì gỡ ngay.
- Rig Builder đã có `curl`, `spread`, `handPose` trên switch tay - không thêm control ngón tay riêng trừ khi được yêu cầu.
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

## Báo kết quả
Mở đầu bằng việc đã làm được gì. Ghi số đo cụ thể (vị trí, %, số đỉnh), những gì giữ nguyên, những gì chưa kiểm (ví dụ chưa thử pose thật), file đã lưu chưa. Ghi bài học mới vào skill này.
