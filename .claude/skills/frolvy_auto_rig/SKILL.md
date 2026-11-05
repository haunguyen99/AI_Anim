---
name: frolvy_auto_rig
description: Cả quy trình rig một nhân vật game mới trong Frolvy từ model trần tới rig chạy được, theo đúng cách đã làm với Hero RPG2 (2026-11-04) - đo model theo từng mảnh rời, đặt joint fit từ số đo, giữ joint người dùng sửa rồi đặt lại joint con, thêm chuỗi joint cho váy / vạt áo / khăn / áo choàng, Build Rig kiểu game, dọn bản nhân đối xứng, vẽ control ôm sát mesh (snug), kiểm rig. Dùng khi người dùng nói "rig con <nhân vật>", "làm rig nhân vật mới", "rig từ đầu", "đặt lại joint các xương còn lại", "thêm joint váy / khăn", "build rig" cho một nhân vật mới trong Frolvy. Luật chi tiết (skin, switch, picker, bẫy Frolvy) ở skill frolvy_rig.
---

# Rig nhân vật mới trong Frolvy (quy trình Hero)

Trả lời bằng tiếng Việt. Frolvy điều khiển qua MCP `frolvy` (`execute_code`, `find_api`, `list_instances`). **Đọc skill `frolvy_rig` trước**: luật rig game đã chốt (chỉ joint base, Root_M = hông, skin chỉ DEF, control ôm sát), skin, switch, picker và bẫy Frolvy. Skill này là trình tự và công cụ cho một nhân vật mới.

```python
import sys; sys.path.insert(0, r"D:\Project\AI_Anim\.claude\skills\frolvy_auto_rig\scripts")
import importlib, auto_rig as A; importlib.reload(A)      # nạp luôn frolvy_rig_tools (A.R) và fit_controls (A.FC)
```

Mỗi bước dừng ở **cổng duyệt**: báo số đo bằng chữ, người dùng xem trực tiếp trong Frolvy, không chụp màn hình trừ khi được yêu cầu. Người dùng sửa joint thì ý họ thắng, kể cả khi lệch số đo. Khi đó nói một dòng nếu thấy rủi ro (Hero: Neck/Head hạ dưới vai), không tự đổi lại.

## 0. Tìm nhân vật
- `work/<dự án>/` (vd `work/rpg2_hero/gdd/anim_list.md`) cho biết model, file rig, phạm vi; file gốc thường ở `C:\Project\<game>\<nhân vật>\` (FBX, texture, `Rig\*.fv`).
- `list_instances`: Frolvy nào đang mở file nào. Scene đang có thay đổi chưa lưu thì hỏi trước khi mở file khác.

## 1. Đo model
- `A.survey(api)`: mỗi mesh có kích thước, đơn vị, đối xứng, **từng shell** (mảnh rời) kèm bounds, và số cạnh hở. Đặt tên vai trò cho từng shell. Hero: 0 thân + đầu + bắp tay, 1/2 bàn tay, 3 quần, 4/5 giày, 6 khăn thắt lưng, 7 váy, 8 thắt lưng, 9/10 + 14/15 giáp cẳng tay, 11/13 đệm vai, 16 vạt trước, các mảnh nhỏ là dây/khoá; mũ trùm và 2 khăn là mesh riêng.
- `A.cut(api, "body", [shell…], trục, [giá trị…], side="R")` cắt **đúng các mảnh cần**. Cắt cả model sẽ lẫn váy vào chân, giáp vào tay.
  - chân: cắt quần và giày theo y;
  - tay: cắt thân, giáp, bàn tay theo x;
  - cổ / đầu: cắt thân theo y, lấy chỗ hẹp nhất;
  - bàn chân: cắt giày theo z;
  - ngón: quét ngang bàn tay theo z. Liền một khối thì là **găng** → một chuỗi ngón + ngón cái.
- Báo mốc: cao, đơn vị (mét, Y lên, mặt +Z, phải −X), tay cầm gì (Hero: song đao, mỗi tay một), mảnh nào gắn vào joint nào, mảnh vải nào cần chuỗi joint riêng (GDD hay ghi "chuyển động phụ").

## 2. Đặt joint fit
- Chép `references/make_fit_template.py` (bảng Hero) vào `work/<dự án>/rig/make_fit.py`, thay **mọi số** bằng số đo mới, rồi chạy ngoài Frolvy:
  `.venv/Scripts/python.exe -I work/<dự án>/rig/make_fit.py "%USERPROFILE%/Documents/Frolvy/fit_skeletons/<Tên>.fvfit"`
- Rồi `api.load_fit_skeleton(path)`. Lệnh này bị từ chối khi scene đã có fit; khi đó sửa bằng `api.move`, không nạp lại.
- Luật bảng: chỉ joint giữa + phải; Root = hông (nhãn `root`), Spine1, Chest, Neck, Head (ngang cằm), HeadEnd; Scapula → Shoulder → Elbow → Wrist; ngón theo số đo (găng = `MiddleFinger1–4`); ngón cái 4 joint; Hip → Knee → Ankle → Toes → ToesEnd + Heel, FootSideInner/Outer.
- Đạo cụ:
  - Mỗi tay một đạo cụ (song đao): `Weapon` + `WeaponEnd` ở lòng bàn tay, nhãn `prop`, giữ cả hai bên.
  - Đạo cụ một tay, hoặc khăn chỉ ở một bên: đặt bên phải, xoá bản trái ở bước 5.
- Báo bảng vị trí chính, chờ duyệt.

## 3. Người dùng sửa joint → đặt lại phần còn lại
Câu thường gặp: "mình đặt lại joint thân, đặt lại các joint còn lại", "đặt lại joint từ joint chest".
- `A.fit_diff(api, path)` in joint **đã đổi** (offset cục bộ khác file đã lưu) và joint chỉ bị kéo theo.
- `A.restore_children(api, path)`: giữ nguyên joint người dùng đổi, đưa **con trực tiếp** của chúng về vị trí thế giới cũ. Joint sâu hơn tự về theo, rồi lưu fit.
- Hero, ví dụ đã gặp:
  - Hạ Root/Spine1/Chest/Neck/Head khoảng 4–13 cm → đưa lại Hip, Scapula, ScarfA1, ScarfB1, HeadEnd.
  - Dời Chest ra trước 2,9 cm → đưa lại Neck, Scapula, ScarfA1.
- Joint con bị người dùng chỉnh vài mm (ngón tay) thì cũng tính là sửa: giữ nguyên, ghi một dòng.

## 4. Chuỗi joint cho vải (váy, vạt áo, khăn, áo choàng)
- `A.panels(api, "body", shell, [y…])`: nhìn từ trên, góc 0 = trước, ±180 = sau, âm = phải. Lệnh in các khoảng có vải và các khe xẻ.
  - Hero, shell 7: vạt sau ±155..180, hai vạt hông −150..−30 / 30..150, xẻ trước và sau. Vạt trước là shell 16 riêng.
- `A.panel_line(api, "body", shell, góc_đầu, góc_cuối, [y…])` lấy đường tâm từng vạt và mép thấp nhất. Khăn là mesh riêng thì dùng `A.cut(api, "scarf_1", [0], 1, ys)`.
- Mỗi vạt có 3 joint + 1 joint cuối:
  - joint đầu ở **mép trên vạt** (cạp váy), không ở Root, để vạt gập từ cạp;
  - joint cuối ở mép dưới;
  - váy: cha là Root;
  - khăn cổ / áo choàng vai: cha là Chest;
  - khăn đeo thắt lưng: cha là Root.
- Nhãn `prop`, joint cuối `""`. Vạt giữa (trước/sau) để side `centre`; vạt hông đặt bên phải, Build nhân sang trái (giữ cả hai).
- `A.add_chains(api, rows, path)`: tạo, gắn cha, đặt vị trí, kiểm cha, lưu fit.
  - **`api.parent(n)` một đối số là GỠ cha**: hỏi cha bằng `api.joint_info()`.
- Dải vải ngắn (Hero: khăn thắt lưng shell 6, tới y 0,73) không cần chuỗi; skin theo Root/Hip. Hỏi nếu người dùng muốn nó đung đưa.

## 5. Build Rig
- `A.build(api, one_side=("ScarfA","ScarfB"), save_to=<file .fv đang mở>)` làm trọn:
  1. `zero_controls`;
  2. tắt helper / bendy, `build_rig`;
  3. `after_rebuild`: xoá bản nhân của chuỗi một bên (truyền **tiền tố**: control các đốt sau không nằm trong `_grp` đốt đầu), translate cho FK, DEF đúng fit, pivot, ngón cái vào lòng bàn tay, switch, nhãn;
  4. `snug` vẽ control ôm sát mesh; `fit` cũ chỉ lo switch / pole;
  5. kiểm và lưu.
- Kết quả phải là:
  - không twist / helper;
  - không còn bản `_L` của chuỗi một bên;
  - switch dưới `CTL_Wrist_*_follow` / `CTL_Ankle_*_follow` / `CTL_Chest_M_follow` (đi theo ở cả IK và FK);
  - switch hai bên **cùng cỡ, đối xứng** (`R.match_switches` trong `build`; Hero: switch tay phải ra 2 cm trong bàn tay, tay trái 5,6 cm trên cổ tay → người dùng phải nhắc hai lần);
  - `DEF vs fit` ở FK rỗng (IK có thể lệch vài mm ở gối);
  - `check_rig` rỗng;
  - `rig moves: True`.
- Hero: 84 DEF. Offset group có xoay ở `SkirtSide1`, `MiddleFinger1`, `Heel` là do hướng joint, không phải pose bị nướng (build mới).
- **Control trục giữa cùng cỡ, ở giữa, trừ Root** (người dùng 2026-11-04: "shape controls ở thân cho cùng kích cỡ và ở giữa", rồi "cho nằm giữa và cùng kích cỡ trừ root"): mọi control giữa — RootX (Hip), Spine1, Chest, IKMid, IKChest, Neck, Head, HipSwinger, **cả Main** — **một bán kính chung** = mặt cắt lớn nhất ở các độ cao đó + ~1,2% chiều cao. Main ở sàn quyết định cỡ (hai bàn chân: Hero 0,335 → chung 0,36, rộng 0,72; thân chỉ cần 0,31). Tâm x = 0 tại khớp (Neck / Head giữ độ cao vòng hiện có), nằm phẳng; hộp IK vuông nửa cạnh = bán kính; HipSwinger giữ hình riêng, dời về giữa, rộng bằng các vòng. **Root_M không đổi** (to hơn, 1,23 m). Đặt `snug = 1`, `fitScale = 6`. Kiểm tâm bằng **tâm khung bao**, không lấy trung bình CV (điểm đóng vòng bị đếm hai lần, lệch 3 cm).
- Báo số control đã vẽ, cỡ các vòng chính, chỗ còn bị váy che (Hero: vòng hông/gối nằm trong váy một phần). Người dùng vẫn chỉnh tay được; chạy lại `snug()` không ghi đè (chỉ `force=True` hoặc menu *Snug Controls to Mesh* mới vẽ lại).

## 6. Skin theo luật (nhân vật nhiều mảnh rời)
Hero (2026-11-04) gần như mỗi bộ phận là một shell: bind rồi **ghi lại weight mọi đỉnh theo luật từng mảnh**, thay vì dọn kết quả bind. Mẫu: `work/rpg2_hero/rig/skin_hero.py` (`S.run(api, A)`); hàm trong `auto_rig.py`: `ramp`, `chain_w` (vải: hoà tuyến tính giữa hai joint của xương gần nhất, trên joint đầu hoà vào cha), `bone_w` (tay, ngón: chủ = joint của xương gần nhất, 50% ở khớp), `write_skin` (tối đa 4, bỏ < 1%, chuẩn hoá), `save_weights` / `load_weights` (JSON, lưu trước mỗi lần sửa lớn).
1. `R.zero_controls`, `api.select([mesh]); api.bind_skin(R.influences(api))` cho từng mesh.
2. Viết bảng luật theo shell (từ `A.survey`):
   - mảnh cứng 100%: giáp cẳng tay → Elbow, đệm vai/dây bắp tay → Shoulder, băng tay → Wrist, khoá thắt lưng → Root;
   - thân: Root → Spine1 → Chest theo chiều cao;
   - tay: Shoulder hoà từ thân theo |x|, Scapula ít ở vai trên;
   - quần: Root → Hip → Knee; giày: Knee → Ankle → Toes;
   - váy theo góc (vạt sau / vạt hông, hoà ở mép) + `chain_w`;
   - mũ: Head, mép phủ vai → Chest;
   - khăn: `chain_w`.
3. Thử từng khớp ở FK bằng `R.edge_stretch` (đọc cả độ dài cạnh; cạnh < 1–2 cm cho tỉ lệ ảo). Lỗi Hero đã sửa:
   - vùng hoà hông/gối hẹp → giãn ×3,3 / ×2,6: nới Root→Hip 0,66–0,88, Hip→Knee 0,35–0,53;
   - **đường may giữa đáy quần (x = 0) bị tính hết về chân trái**: chia đôi Hip_L/Hip_R, đáy quần Root 70% (×3,8 → ×2,6);
   - cổ: đỉnh ở trục cổ chia **theo bán kính tới trục cổ**: cột cổ (r ≤ 11,5 cm) Chest → Neck → Head theo chiều cao, cằm/mặt Head, cổ áo (r ≥ 13 cm) 100% Chest (co ×0,14 → ×0,47);
   - **mesh nằm trên xương Scapula đi theo Scapula 100%** (người dùng nhắc lần 2: "hãy cho mesh nằm trên phần scapula đi theo scapula luôn"): lõi |x| 0,11 → khớp vai, y 1,22–1,37 = 100% Scapula (Shoulder lấy phần tay trước), dải chuyển ngắn: cột sống |x| 0,06–0,11, nách y 1,12–1,22, đầu 1,37–1,40; mép mũ trùm phủ vai và đầu khăn vắt vai cũng theo Scapula. Lõi dời 3,3–4,9 cm khi xoay 20° (trước 1,2), vùng khác 0, cổ áo / cổ / đầu không ăn Scapula. Nách co ×0,14 khi xoay Scapula xuống 20° là bình thường.
   - **đai cứng khi xoay Spine1** (người dùng: "skin phần đai khi xoay spine1 cứng quá"): khớp Spine1 nằm giữa đai; luật Bastion (đai Root + 15% Spine1) làm đai dời 3 mm khi thân trên dời 9 cm. Sửa: đai Root → Spine1 theo chiều cao 15% → 75% (mép dưới → mép trên), khoá trên đai cứng theo weight đai tại tâm khoá, thân nối từ mép dưới đai (Root→Spine1 0,93–1,06). Đai dời 4,1 cm, giãn ×1,57 → ×1,36. Luật Bastion chỉ đúng khi Spine1 nằm **trên** đai.
   - **Khuỷu hở khi gập** (người dùng: "xoay khuỷu tay bị hở mesh", gập 57°): bắp tay (mảnh thân) lồng vào **ống giáp cẳng tay hở** (mảnh rời, cứng 100% Elbow) từ |x| 0,515; đầu bắp tay chỉ có Elbow 35–50% nên trượt ra khỏi ống 4,1 cm. Sửa: **chỉ phần đầu nằm trong ống = 100% joint của ống**, trước miệng ống giữ như cũ (Elbow ≤ 50% trong một vòng đỉnh, 0,49–0,515). Lần đầu mình kéo dải chuyển dài 0,38–0,515 → cả bắp tay theo Elbow, người dùng: "chỉ gắn cứng phần mesh ở đầu thôi, giờ xoay lại bị móp tay". **Đo độ móp chỉ trên phần nhìn thấy** (cạnh ngoài miệng ống): dải dài 71 cạnh xấu, chỉ-đầu 12, trước khi sửa 9; đếm cả cạnh trong ống thì ra ngược lại (37 vs 43) — số đo sai chỗ. Làm mịn không đụng phần đầu. Luật chung: **mảnh rời lồng vào nhau** (tay áo trong găng, ống quần trong giày): chỉ đoạn nằm trong theo 100% joint của mảnh ngoài.
   - **Làm mịn khớp** (người dùng: "skin tay chân ổn, smooth 1 chút ở các khớp"): `A.smooth_pairs` — chỉ san phần chia giữa **hai joint của khớp** với đỉnh kề cùng mảnh, tổng của cặp và joint khác giữ nguyên; bỏ qua mảnh cứng, đường may đáy quần, và vùng cố ý giữ hẹp (mỗi cặp có hàm bỏ qua riêng: sau gối, đáy quần). Lần 1 (3 lượt, 0,5, không bỏ qua) làm sau gối co lại ×0,45 → ×0,29 → hạ 2 lượt × 0,35 + bỏ qua. Đo bằng **số cạnh co < 0,6 / giãn > 1,6** (cạnh > 1,2 cm) trên 11 động tác, không nhìn một cạnh tệ nhất: 52 → 43.
   - **Chân phải chia theo xương như tay, không theo dải chiều cao** (người dùng: "sao skin tay không bị móp khi xoay, phần chân lại bị móp? nhiều vertex ở chân bị ảnh hưởng sai joint"). Tay đúng vì luật bám vị trí khớp (|x| vai 0,24, khuỷu 0,53) và cẳng tay là giáp cứng. Chân dùng dải chiều cao tự đặt, không bám khớp: ống giày (cẳng chân) theo Ankle dù cổ chân ở y 0,10, đùi ngoài trên y 0,77 theo Root dù khớp hông ở 0,80 → 74/545 đỉnh sai joint. Sửa: `bone_w` cho quần + giày (chủ = joint của xương gần nhất, 50% ở khớp, blend 0,15), Root chỉ cho chậu **trên** khớp hông (dải hy−0,10 → hy+0,12, bớt 70% ở hông ngoài), đường may giữa (x = 0) chia đôi Hip_L/Hip_R ở mọi độ cao, đo chỗ quần tách hai ống (Hero y 0,71) — đùi trong dưới đó chỉ theo Hip. Còn 10 đỉnh "sai" là chậu trên khớp hông (đúng). Kiểm bằng cách đếm đỉnh có joint chính khác xương gần nhất. **Vị trí khớp để chia weight phải lấy ở tư thế gốc** (`api.rest_matrix`), không lấy pose hiện tại: `A._jp` đã sửa.
   - Bẹn trước khi nhấc đùi rất cao vẫn gập (×0,24) vì lưới quần chỉ có 2 hàng đỉnh cách 9 cm qua nếp bẹn; dải "rộng" trước đó giảm gập bằng cách cho đùi ăn Root (sai joint) nên đã bỏ.
   - **chân móp khi kéo IK chân** (người dùng: "phần chân bị móp khi di chuyển IKAnkle_L"; pose: IK lên 17 cm, ra trước 28 cm): đo bằng `R.pose_stretch` theo đúng pose người dùng (rest = đưa 2 control đó về 0). Hai chỗ: sau gối co ×0,38 (vùng chuyển Hip→Knee rộng 0,35–0,53 làm lõm nếp gối) và nếp bẹn trước ×0,36. Sửa: **trước / sau khác nhau** — sau gối chuyển gọn quanh khớp (0,41–0,48), trước gối giữ rộng; bẹn trước Root→Hip rộng hơn (0,55–0,95, thử 5 dải chọn dải ít co nhất), sau giữ 0,66–0,88. Kết quả: sau gối ×0,74 (gập FK 90° trước ×0,09), bẹn ×0,54. Gập gối ngược chiều (hyperextend) bỏ qua. Lưới quần thưa (cạnh 9 cm) nên không thể hết hẳn.
   - **Thử biến dạng phải bọc trong `A.keep_pose(api, fn)`**: `R.fk_rest` đưa control về 0 nên làm mất pose người dùng đang thử (Hero: 2 lần). Khi trả công tắc: **tắt autoSnap → trả fkIk → trả control → bật autoSnap**; trả autoSnap trước fkIk làm Frolvy snap control IK theo FK, mất pose IK (Hero: tay IK trái về 0). Đã sửa thứ tự trong `deform_test`, `check_rig_moves`, `keep_pose`.
   - Người dùng có thể "Save As" sang file khác giữa chừng (Hero: `skele.fv` → `skin.fv`): `save_scene` sẽ trả `False` khi ghi vào file cũ. Lưu vào đường dẫn `list_instances` báo.
   - **bả vai đi theo Scapula quá yếu** (người dùng 2026-11-04: "rotating the Scapula CTRL, the surrounding shoulder blade mesh should follow the movement more strongly"): Scapula chỉ có ở |x| > 0,17, tối đa 35% → 20/79 đỉnh, trung bình 4%. Sửa: Scapula tới 75% trên bả vai và đỉnh vai (|x| 0,07 → 0,17, y 1,12 → 1,24, tắt dần ở 1,37–1,40, mặt ngực trước bớt 45%), áp cho thân, giáp ngực và mép mũ trùm phủ vai (60% phần Chest ở |x| > 0,1); Shoulder vẫn lấy phần tay trước. Kết quả 53/79 đỉnh, TB 21%, vùng bả vai dời ×1,8, giãn ≤ ×1,3, vùng khác 0.
   - **ngón cái liền găng**: chỉ đỉnh ngón cái thật (đo vùng) theo xương ngón cái, không theo "xương gần nhất" (×4,8 → ×3,4, phần còn lại là chỗ ngón cái dính mặt găng).
4. `R.skin_report` cho mọi mesh: không cross-side, không non-DEF, ≤ 4 joint.

## 7. Picker đơn giản
Hero (2026-11-04, "tạo picker dễ nhìn dễ sử dụng"): một trang `Hero_Simple`, 57 nút, khung 420×640, xuất `C:\Project\RPG_2\Hero\Rig\Hero_Simple.fvpicker`.
- Nhìn chính diện: bên phải nhân vật nằm **bên trái** trang. Định nghĩa bên phải rồi lật x = W − x − w cho bên trái.
- Màu: phải đỏ, trái xanh dương, giữa vàng, vải / đạo cụ xanh lá, IK/FK tím, All xám. FK chữ nhật, IK tròn.
- Thân: chỉ FK (Head, Neck, Chest, Spine, Hip = RootX, Root; Main dưới đáy). Nút thân **nhỏ (64×20), cùng cỡ, xếp dọc ở giữa hai tay** (x 178–242, nằm gọn giữa hai nút Clav; Chest ngang tầm vai), Root rộng hơn chút (84×20) để phân biệt. Người dùng 2026-11-04: "kích cỡ control thân ở picker vẫn chưa thay đổi" (đổi cỡ control 3D thì đổi luôn nút picker), rồi "cho nhỏ lại và nằm ở giữa 2 tay".
- Tay: Clav, Sh, El, Wr + IK tròn to + Pole + IK/FK + Blade.
- Chân: ưu tiên IK (IK Foot tròn to, Knee = pole tròn, Toes); FK Hip/Knee/Ankle nhỏ màu nhạt ở cột ngoài; IK/FK cạnh bàn chân.
- Vải: vạt hông 3 nút cạnh hông, vạt trước + vạt sau 3 nút mỗi chuỗi ở cột giữa giữa hai chân, khăn (một bên) ở góc trên.
- Không nút ngón (curl/handPose trên switch), không IK thân, HipSwinger, công tắc thân.
- Kiểm: `select_picker_button` từng nút = đúng `picker_button_nodes`, không nút nào đè nhau, liệt kê control không có nút; nút All chứa mọi control.
- Mở bảng bằng `show_panel("Tool Picker")`.

## 8. Tiếp theo
Sửa skin theo vùng thêm, picker: theo skill `frolvy_rig` mục 4–5. Mảnh cứng gán 100%:
- mũ trùm → Head;
- giáp cẳng tay → Elbow;
- đệm vai → Shoulder (hoặc Scapula);
- vạt váy → chuỗi Skirt;
- khăn → chuỗi Scarf.

## Sau mỗi nhân vật
Ghi bài học mới vào đúng mục của skill này (bước nào, số đo, câu người dùng, ngày). Luật áp cho mọi rig thì ghi vào `frolvy_rig`. Hàm còn thiếu thì thêm vào `scripts/auto_rig.py` (Python thuần, Frolvy không có numpy).

## Lỗi của Frolvy
Gặp lỗi Frolvy: thêm một dòng vào bảng `work/frolvy_feedback.md`, viết ngắn (Lỗi / Cách thấy / Mong muốn, mỗi ý một câu). Hỏi người dùng rồi mới gửi.
