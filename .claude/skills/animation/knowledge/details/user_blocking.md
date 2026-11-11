# user_blocking — Quy trình B: AI rig trên Frolvy → người dùng key blocking → Studio: pose chuyển tiếp → polish → FBX

Người dùng duyệt quy trình này ngày 2026-10-23 ("oki cập nhật vào quy trình. Khi người dùng cũng cấp blocking và AI thêm
các pose chuyển tiếp rồi sau đó polish"). Clip mẫu đã đi hết quy trình: **Gaygor Attack 50 Blocking**. Bộ script mẫu nằm
ở `work/boss_gaygor/gaygor_attack_50_blocking/`; Pose Lab https://claude.ai/artifact/8WqsypJBEfDsbXY4Bc3wdz; Review Lab
https://claude.ai/artifact/CAn8A5JiGjJXYjTNFbKKwX; FBX ở `export/` và `export/anim_only/`.

Dùng quy trình này khi người dùng hoặc team đưa một **FBX đã có blocking** của chính rig đó (vd `Bloking10/25/50.fbx`:
10%, 25%, 50% số key). Khi đó không có video ref; **file blocking là chuẩn** về pose và timing. Không dùng Blender
(user 2026-10-23: "bỏ hẳn blender"). Mọi bước chạy bằng Python cùng Pose Lab, Review Lab và ffmpeg.

## Bản 2026-10-31: người dùng key blocking trên Frolvy

Người dùng 2026-10-31: "Ở quy trình B AI sẽ Rig trên phần mềm Frolvy để cho người dùng keypose. Khi đã key xong AI sẽ Export
blocking sang Studio để làm tiếp". Họ chọn dùng auto-rig của Frolvy, file đi sang là FBX, các bước sau giữ như cũ nhưng
**làm trong Studio thay cho Pose Lab**.

**Frolvy** (https://frolvy.com, bản 0.9.24, cài ở `C:\Program Files\Frolvy`) là phần mềm rig và anim trên Windows, dùng giống
Maya. Nó có Rig Builder với mẫu người `Human05` (`templates\Human05.fvfit`, mẫu riêng lưu ở `Documents\Frolvy`), skin và Paint
Weights, IK/FK, Tool Picker, xuất FBX/glTF (mỗi frame một key) và MP4. **AI điều khiển qua MCP `frolvy`** (`Frolvy-mcp.exe`
nối tới cổng `127.0.0.1:9877` mà app mở khi chạy). Có 11 lệnh: `get_scene_info`, `get_node_info`, `execute_code` (Python với đối tượng
`fv`/`api`, 320 call, mỗi lần chạy là một bước undo), `find_api`, `get_viewport_screenshot`, `get_app_screenshot`, `list_panels`,
`show_panel`, `reset_workspace`, `undo`, `redo`. **Phải mở Frolvy trước**, nếu không lệnh báo "nothing is listening on 127.0.0.1:9877".
Tra tên call bằng `find_api` trước khi viết script, không đoán (vd `build_rig`, `create_ik_handle`, `set_ik_pole`, `constrain`).
Script mẫu của app: `C:\Program Files\Frolvy\scripts\human_rig.py`, `human03_fit.py`, `make_biped_fit.py`, `transfer_weights.py`.

| # | Bước | Ai làm | Ra gì | Cổng |
|---|---|---|---|---|
| F1 | **Rig trên Frolvy bằng auto-rig.** Nạp mesh nhân vật (FBX của team hoặc model trong Studio), mở Rig Builder, nạp `Human05`, đặt khớp (vai, khuỷu, hông, gối, cổ chân, cột sống, cổ, đầu) **trùng vị trí khớp của xương team** (đọc từ FBX team), Build Rig (xương + control + IK chân, công tắc FK/IK, pole gối/khuỷu). Bind Skin, sơn weight chỗ gập rồi Mirror. Thử gập vai, khuỷu, hông, gối bằng script và xem bằng `get_viewport_screenshot`. Lưu `work/<dự án>/<clip>/frolvy/<nv>_rig.fv` và bảng tên `bone_map.json` (xương Frolvy → xương team). | AI | rig `.fv` + `bone_map.json` | **Duyệt rig** (Director chấm trước) |
| F2 | **Người dùng key blocking trên Frolvy.** AI mở sẵn scene (fps, khoảng frame theo brief, Tool Picker) và báo control nào là gì. Người dùng tự key pose. AI không động vào scene khi người dùng đang key. | Người dùng | scene `<clip>_blocking.fv` | Người dùng báo **"key xong"** |
| F3 | **Xuất blocking sang Studio.** Qua MCP: lưu scene, đọc **thời gian các key** (key gán theo thời gian, không theo index), xuất FBX (`<clip>_blocking.fbx`, mỗi frame một key) vào `work/<dự án>/<clip>/frolvy/`. Đổi tên xương theo `bone_map.json` cho khớp rig team, nạp vào Studio thành version blocking (interp step, chỉ giữ các frame có key thật), rồi so thế giới từng xương với FBX. | AI | version `b_vN` trong Studio | **Khớp file** |
| 2… | Tiếp như bảng dưới từ bước 2 (phân tích → sửa lỗi → breakdown → trọng lượng → polish → FBX), làm trong **Studio** thay cho Pose Lab. | AI | | như dưới |

**Góp ý cho Frolvy** (người dùng 2026-10-31: "Frolvy là một ứng dụng đang phát triển. trong quá trình làm việc có vấn đề gì
bạn hãy gửi fb cho họ"): gặp lỗi hoặc thiếu sót của Frolvy thì ghi ngay vào `work/frolvy_feedback.md`, kèm cách tái hiện, ảnh,
log và cách tạm vượt qua. Soạn sẵn bản góp ý, hỏi người dùng rồi mới gửi qua menu **Help → Send Feedback…** trong Frolvy.

Chưa kiểm trên clip thật (2026-10-31), cần làm ở clip đầu tiên:
- **Xương Frolvy khác xương team.** Rig team phải đi Unity nên FBX cuối vẫn ghi đè đường cong trong FBX của team (bước 7). Vì vậy
  bước F1 đặt khớp Human05 trùng khớp team, còn F3 chuyển pose bằng góc thế giới theo `bone_map.json`. Prop và tóc không có
  trong Human05: hỏi người dùng có cần control cho prop không (thêm joint prop + parent constraint vào tay).
- **Studio chưa nạp được key từ FBX.** `Tệp → Nhập FBX` của Studio (`tools/studio/modules/fbx.js`) chỉ đọc mesh, xương và skin.
  Bộ đọc key hiện có là `make_model.py` của Pose Lab (RotationOrder từng xương). Cần thêm đường nạp key vào Studio (cầu nối
  `anim key` hoặc port qua `tools/studio/port_pose.py`) trước khi làm F3.
- Nếu team đã đưa sẵn FBX blocking thì bỏ F1–F2, vào thẳng F3 (hoặc bước 1 cũ).

## Sửa anim trên Frolvy: luôn sửa trên layer, không sửa Base (từ 2026-11-04)

Người dùng 2026-11-04: "sử dụng layer khi được yêu cầu chỉnh sửa. không sửa trực tiếp trên layer gốc như ban đầu".
Layer **Base** (index 0) giữ bản đã duyệt (blocking, spline hoặc polish). Mọi yêu cầu sửa sau đó (góp ý review, sửa clip
đã xuất) đi vào layer riêng. Nhờ vậy tắt layer là thấy lại bản cũ, và đổi Base không làm mất phần đã sửa.

Bộ hàm: `.claude/skills/frolvy_rig/scripts/frolvy_layers.py` (đọc docstring đầu file). Không key layer bằng `set_key` trần,
không dùng `flatten_layers`, `merge_layer_down` hay `bake_keys` lúc còn layer: Frolvy 0.9.36 cộng đôi layer cộng thêm
(đo 2026-11-04: Base 40 + layer 15 → màn hình 55, nhưng flatten/xuất FBX ra 70; `bake_keys` ra 30, mất cả Base).

1. **Mỗi vòng sửa = một layer mới**, chế độ additive, weight 1: `L = FL.start_fix(api, "fix_r<N>_<nội dung>")`
   (vd `fix_r1_tay_phai`). Một vòng có nhiều chỗ sửa thì chung một layer; vòng sau tạo layer mới.
2. **Key bằng `FL.key` (giá trị tổng muốn thấy) hoặc `FL.offset` (cộng thêm)**, luôn kèm `hold=(a, b)` là frame bắt đầu và
   kết thúc vùng sửa. Thiếu `hold` thì một key trên layer cộng thêm làm lệch **cả clip**. Hàm trả sai số trên màn hình (~0).
3. Lưu scene thành bản mới `<clip>_r<N>.fv` (còn layer). Báo người dùng tên layer để họ mute/solo so trước và sau.
4. Kiểm như mọi bản: giải phẫu, chân cắm, tay bám prop. Layer cộng góc xoay có thể kéo tay tuột prop (SDR06: lệch 34 cm),
   nên sửa tay cầm prop thì giải lại IK tay trong layer đó và đo độ trượt.
5. **Xuất FBX:** mở bản sao của scene, `FL.bake_for_export(api, đầu, cuối)` (đọc tổng từng frame, xoá layer, ghi lên Base,
   sai số ~0), rồi mới chạy đường xuất cũ (bake joint team → `export_scene` → `fbx_ascii_keep.py`). Scene có layer giữ lại
   làm bản gốc. Đọc lại FBX so với màn hình trước khi giao.

**Lệch nhịp hai tay cho idle loop** (Hero_Blade Idle, 2026-11-05, người dùng duyệt): `FL.lag_mirror_translate(api, L, src_tay_phải, dst_tay_trái, lag=5, gain=1.15)`.
Translate tay trái = chuyển động translate tay phải (đối xứng, tx đổi dấu) trễ `lag` frame, quanh **pose gốc của tay trái ở F0** (F0/F30 và rotate giữ nguyên).
Bài học: (a) "giữ pose gốc, không thay đổi pose gốc": không ghi thẳng giá trị tổng của tay kia lên tay này, chỉ cộng phần dao động. (b) Chỉ làm lệch **nhịp**
(trễ 3-5 frame), biên độ giữ cũ, nếu tăng thì 10-20% (x3 bị chê "quá nhiều"). (c) Chỉ translate: layer cộng không sai số; đặt cả rotate đối xứng lên layer
thì lệch 5-8° vì cộng Euler không tuyến tính ở góc lớn (rz ~60°). Cần rotate thì lặp hiệu chỉnh hoặc dời chính chuyển động của tay đó, không đổi dấu.
(d) Đổi mức lệch: `delete_layer` rồi làm lại, không chồng layer. Layer mẫu `fix_r2_tay_trai_translate_tre_5f`.

Chưa thử (làm lần đầu thì kiểm trước): layer **override** (chỉ dùng khi người dùng xin dựng lại cả một đoạn), `retime_keys`
khi đổi timing có dời key trên mọi layer không, thuộc tính tuỳ biến (switch, curl) trên layer (`list_keys` của chúng trả []).
Studio chưa có anim layer: luật này áp dụng cho Frolvy trước.

## Chép anim giữa hai cửa sổ Frolvy (Hero_Blade Attack_02 v1 → v2, 2026-11-11)

Hai cửa sổ Frolvy là hai tiến trình riêng: `copy_keys` ở cửa sổ này, `paste_keys` ở cửa sổ kia trả False; `create_connection` file kia chỉ mang
node ngoài rig (rig lồng trong reference không theo, anim cũng không). Cách chép đã chạy được (72 control, ~8100 key, giống từng frame):
1. Cửa sổ nguồn: ghi giá trị tại frame key (`get_attr`, tạm thư mục temp) ra JSON. Cửa sổ đích (`use_instance(port)`): dựng lại theo frame tăng dần
   bằng `select` + `set_key` rồi `move_key` về đúng giá trị + `set_key_interp('spline')`; kênh không có key tại frame đó thì `delete_key`.
2. `get_attr` luôn trả góc xoay trong ±180, nên chép xong phải `euler_filter` cả 72 control (không thì cổ tay quay đường dài ở F29–F31).
3. Key dựng từ frame nhỏ lên bị tính auto tangent thiếu key phía sau: **chạm lại mọi key** (`move_key` cùng giá trị, góc xoay dùng chuỗi đã unroll,
   hai lượt) cho kênh còn lệch. Chạm lại là cách duy nhất đưa key về auto sạch (`set_key_interp` không xóa tangent tay).
4. Kiểm: so mọi kênh transform + thuộc tính tại mọi frame, và vị trí thế giới các joint DEF (ngưỡng 1 mm). Đầu kiếm lộ lệch xoay cổ tay sớm nhất.
Kết quả: chỉ lệch ở 7 frame giữa key của cổ tay (F5 trái; F20, F24, F34–F40 phải), đầu kiếm tới 14 cm. Nguyên nhân: v1 có vài key tangent không
phải auto thật (chạm lại key ở v1 thì F5 khớp v2; đã hoàn tác), bản chép ra auto sạch hơn bản gốc. Muốn khớp y hệt thì ép tangent tay (`set_key_tangent`).
Lưu ý khác: `frame_range()` là playback range, người dùng đổi trong lúc làm, đừng ghi đè; file mới từ người dùng chưa có tex: `hero_textures.apply(api, force=True)`.

## Thêm in-between / breakdown vào giữa key chính trên Frolvy (Hero_Blade Attack_02 F0-18, 2026-11-11)

Lệnh một bước: `tools/frolvy_inbetween.py` (`exec(...); run(api)` trong execute_code; `run(api, dry=True)` chỉ đếm). Nguyên tắc đã dùng:
- Không đổi key chính, không đụng key từ F19; chỉ thêm key ở frame giữa (F3 5 7 8 và F10-17), giá trị = đường cong hiện có + lệch nhỏ.
- **Key hip (Root_M) trước** (người dùng 2026-11-11): mọi frame giữa đều có key hip trước, rồi spine chain, khuỷu, cổ tay. Hip dẫn trước 0.3 frame ở F3 5 7 8; frame giữa còn lại key đúng giá trị đường cong. Lần đầu tôi bỏ sót hip, người dùng nhắc.
- Tay lệch nhịp: cổ tay kéo trễ (trái 0.35, phải 0.2 frame), pole khuỷu dẫn trước 0.3 frame (gốc dẫn, ngọn kéo). Chỉ dịch thời gian nên cung đường giữ nguyên.
- Overlap thân: Spine1 → Chest → Neck kéo trễ dần so với hip (0.25 / 0.35 / 0.45 frame) ở F3 5 7 8; đoạn giữ F9-18 từng chết cứng nên thêm follow-through rx sau điểm dừng F9. Đừng dựa lag vào xoay Root ở đoạn giữ: người dùng tự sửa key Root (F4, F6, F18) và bỏ đoạn Root ry nhô, lag đó thành vô nghĩa.
- Sau khi thêm key phải chạm lại key <=18 của kênh đã sửa (auto tangent), KHÔNG chạm key sau đó (giữ tangent người dùng). Không `euler_filter` sau khi thêm key: lật rz cổ tay 180 độ ở F19/F21.
- Người dùng có thể mở lại / lưu file giữa hai lượt: chụp lại base từ scene hiện tại, đừng dùng dump cũ. Key chưa lưu mất khi Frolvy khởi động lại.

## Các bước sau khi có blocking (từ 2026-10-23)

Từ 2026-10-31 các bước này làm trong Studio. Tên lệnh Pose Lab dưới đây là của clip mẫu.

| # | Bước | Ra gì | Cổng |
|---|---|---|---|
| 1 | **Nạp FBX vào Pose Lab** (`make_model.py <in.fbx> <out.json>`): đọc đường cong kèm thời gian key, dùng mesh/skin của model Pose Lab cùng rig, local = PreRotation · Euler(**RotationOrder của từng xương**) + T. Kiểm thế giới từng xương so với FBX. | version `b50_vN` (mode keys, interp step, keys = frame key + 1) | **Khớp file** ("Khớp rồi đấy") |
| 2 | **Phân tích nhân vật + đòn** từ chính blocking và model (`measure.py`): tỉ lệ cơ thể, prop, pha, tầng key (10/25/50%), hông, thân, xoắn, đầu, chân chạm đất (đo bằng **mũi chân**), tay trên prop, cung prop, lỗi của blocking (xuyên sàn, trượt chân). Xem 20 key bằng mắt ở góc bên và góc trước. | `analysis.md` | **Duyệt phân tích** |
| 3 | **Sửa lỗi blocking**, giữ timing (`fix_v3.py`): prop xuyên sàn → xoay quanh tay cho chạm sàn 0 cm; chân trượt → dời key lúc tiếp đất về chỗ cắm. IK hai đốt giữ tay trên prop. | `b50_v(N+1)` | xem |
| 4 | **Thêm pose chuyển tiếp** (`breakdowns_v4.py`): mỗi khoảng ≥ 3 F một breakdown (khoảng dài nhất hai), có favour, lệch nhịp theo nhóm (LEAD/PULL/SETTLE), prop theo cung (blend trong không gian ngực; nằm đất thì blend theo thế giới), tay dính prop, chân cắm khóa, sàn. Kiểm `check_v4.py` + `arc_plot.py`. | `b75_v1` | xem |
| 5 | **Trọng lượng** khi user chê nhẹ (`weight_v5.py`, `shoulder_v6.py`): đo tốc độ prop/hông trước, gọi tên từng chỗ, rồi sửa breakdown. Xem `timing_spline.md#heavy-prop-weight`. | `b75_vN` | **Duyệt blocking 75%** ("Polish đi") |
| 6 | **Spline + polish, nướng từng frame** (`polish_v1.py`, các bản sửa `polish_v2/3.py`): PCHIP, ràng buộc mỗi frame, lò xo vải/phụ kiện. QA `check_polish.py <module>`. Chụp playblast từ Pose Lab (`pb_capture.js` + `save_srv.py`) → ffmpeg → Review Lab. | `polish_vN` trên Pose Lab + Review Lab | **Duyệt polish** ("oki rồi") |
| 7 | **Xuất FBX** (`export_fbx.py`): thay đường cong trong chính FBX của team (rig, skin, mesh giữ nguyên), 68 key linear, Euler theo RotationOrder, FBX 7.4; `--anim-only` cho bản không mesh. Đọc lại so từng xương. | `export/<tên>.fbx`, `export/anim_only/<tên>.fbx` | — |

Sau mỗi cổng: `git commit` kèm câu của user, tag bản duyệt (`<nv>-<clip>-<version>-approved`), cập nhật `clips.json` (note có chữ "chờ" khi đợi), MAP và file này.

## Luật rút ra (mỗi luật có ví dụ thật)
- **RotationOrder:** rig AdvancedSkeleton đặt ZYX/ZXY/XZY trên cổ, đầu, vai, tay, chân. Đọc tất cả theo XYZ làm b50_v1 sai pose. Phép kiểm "so với chính bộ đọc của mình" không bắt được lỗi này. Phải kiểm bằng một thứ độc lập với bộ đọc, vd tay trong không gian prop phải mượt qua các key. → `review_process.md#pose-lab-3d`
- **Đo tiếp đất bằng mũi chân, không bằng cổ chân.** File đã ghim mũi chân trái F35–48, cổ chân chỉ xoay quanh nó. Lần đầu khóa theo cổ chân làm gối gập thêm 32–60°.
- **Sửa prop trên sàn:** hai key cạnh nhau phải có cùng pose thế giới khi prop nằm yên. Xoay F19 và F21 khác góc làm chùy trượt rồi khựng ở F21 (user: "lỗi ở f21").
- **Cung nhấc chân chỉ dùng giữa hai lần chạm đất.** Nếu key đích đã là đỉnh bước (F28) hoặc chân đã nhấc sẵn (F50), cung thừa làm gối gập ngược: F21–23, và F52 (user: "pose 52 lại giật về"). Sửa một chỗ chân thì rà mọi breakdown có chân di chuyển.
- **Chi tự do** (tay vừa buông prop) đi theo nhịp riêng đều đặn, không theo t của thân (tay tụt 22 cm/F ở F61).
- **Chạy lại script phía trước sẽ ghi đè model đã duyệt.** Giữ một cờ dựng lại đúng bản duyệt (`B75_V3_APPROVED=1`) và so sha256 với file đang đăng.
- **Trọng lượng:** nhún lấy sức trước khi nhấc; prop ì trên sàn khi thân bật lên; thân lún thêm 1 frame sau va chạm; lê đầu prop khi nhấc khỏi đất; rơi nhanh dần vào vai, rồi vai ép, khuỵu, nảy. → `timing_spline.md#heavy-prop-weight`
- **QA polish trước khi gửi** (`check_polish.py`): góc khớp trong khoảng của key gốc ±5°, "pops", "fold_backs" (đổi chiều > 10° trong 6 F), chân cắm trượt, tay rời prop, sàn. Xem từng mục "giữa key". → `timing_spline.md#polish-bake-no-blender`
- **Khi user nói "nhầm bản":** so các frame **giữa key**, vì key của spline và blocking giống nhau. Sau đó hỏi frame cụ thể. Lỗi thật nằm ở F21, không phải nhầm version.

- **Mỗi vòng góp ý = một version mới** (Gaygor Attack 10 Blocking, 2026-10-27). Ghi key thẳng vào db của version đang mở (khi user đang
  kéo timing trên trang) đè lên thao tác của user và làm mất key; user: "ko cập nhật bản mới sao". Đọc key/timing user đã kéo từ db,
  rồi dựng lại bằng script (vd `build_b75v3.py`) và đăng `pose-version` mới, kèm `--main` / `--phases` cho bảng Timing.
- **Ghi chú có ảnh vẽ:** đọc `img.url` bằng Artifact read `path=<asset id>`, xem ảnh trước khi sửa (F42 "đầu vũ khí vẫn ở trên mặt sàn",
  F50 "chùy nghiêng ra sau do quán tính"); `cam` cho biết góc nhìn.
- **Lỗi "hai cây chùy"** là model của version cũ còn trong cảnh khi đổi version nhanh, không phải lỗi rig. Đã sửa ở Pose Lab (`openTok`).

- **AI tự xem lại** (Pose Lab, 2026-10-27): công tắc + "Số vòng" cạnh Gửi cho AI (db `settings/aiself`). Bật thì mỗi lần Gửi cho AI
  mở kế hoạch N vòng (db `selfplan`); khi trang mở version mới nhất, nó chụp các key chính + giữa pha ở 3 góc, gọi AI (`sample`),
  lưu ghi chú `kind: "ai"` (`ai.issues`, ảnh ở `imgs`) rồi gửi cho Claude. Claude: đọc ghi chú ai, **kiểm lại bằng số đo trước khi sửa**
  (AI nhìn ảnh có thể sai), ra version mới; hết vòng thì dừng chờ user duyệt. Trang chỉ chạy vòng khi user đang mở trang.
  Đăng trang phải khai báo `sample: {images: true}` cùng `db, user, comments, downloads, assets`.

## Dùng lại cho clip sau
Chép `work/boss_gaygor/gaygor_attack_50_blocking/` làm mẫu (`work/<dự án>/<id>/`). Những chỗ phải đổi trong từng script:
- `make_model.py`: `SRC_GLTF` = model Pose Lab cùng rig (mesh/skin). Rig khác thì xuất model đó trước.
- `fix_v3.py`: đường dẫn FBX nguồn, danh sách key cần sửa (`LOW_TARGET`, chân).
- `breakdowns_v4.py` / `weight_v5.py`: `PLAN` (frame, key A/B, t, offsets, lý do). Đây là phần sáng tạo, viết theo bản phân tích.
- `polish_v1.py`: `SEC` (xương phụ, độ cứng/giảm chấn), các bước ràng buộc giữ nguyên.
- `pb_capture.js`: tâm camera và khung bao, lấy số từ `pb_bounds.py <polish_vN>`.
- `export_fbx.py`: `SRC`, tên take/file, module pose nguồn (`polish_vN`).
- Đăng version: `tools/clip_registry.py pose-version | review-version`, `build`, Artifact cùng file path.

Thời gian máy chạy (Gaygor 68F, để báo trước cho user): mỗi bước dựng hoặc sửa key dưới 1 phút; QA mỗi bản khoảng 20 giây; chụp playblast 68 frame × 3 góc khoảng 3 phút (4 đợt × 17 frame); xuất FBX dưới 30 giây.

## Dùng anim thư viện (Mixamo) làm bản nền (2026-11-10)
User hỏi "tận dụng thư viện như mixamo tạo anim theo mong muốn" → thử Lumber: `Ref/Slow Run.fbx` (team đã từng dùng làm MC_Lumber_Run bằng Maya) retarget tự động bằng `tools/retarget/retarget.py`, chấm với bản team bằng `compare.py`.
- Kết quả: thân/tay/đầu/hông trùng bản team 0°/0 cm; bàn chân trùng hướng; đùi/ống chân lệch TB ~12° (max ~28°) vì team sải dài hơn (47 vs 40 cm). Mắt: gần như giống (`work/g_lumbercity/mixamo_test/look/`).
- Bài học: (1) cả hai T-pose thì KHÔNG nắn bind theo hướng xương (nắn tạo lệch cố định 4–14° ở tay/bàn tay); (2) hông dời tỉ lệ 1,0 (khớp team), không theo tỉ lệ chiều cao hông; (3) chân phải IK: cổ chân bám vị trí nguồn × tỉ lệ dài chân (Worker 0,72), **độ cao cổ chân tính từ sàn** (tính theo hông → lún 3 cm); ép tỉ lệ 0,86 → chân duỗi quá, lún 3 cm; (4) eo team Spine2_M nối `Spine` (không phải Spine1).
- Hông: tự tính theo chiều cao hông (nhân vật Mixamo khác cỡ: Standing Idle Axe hông 103 cm → 0,58); tỉ lệ 1,0 chỉ đúng với Slow Run.
- Tải Mixamo (2026-11-10, user: "Ai tự tải anim từ trên mixamo về"): khung trình duyệt của app không giữ đăng nhập Adobe → dùng Chrome của user (Claude in Chrome) đã đăng nhập; tìm bằng API trong trang (`/api/v1/products?type=Motion&query=…`, header Bearer token trong localStorage + `X-Api-Key: mixamo2`), xuất `/api/v1/animations/export` (fbx7_2019, skin false, fps 30) → chờ `/characters/<id>/monitor` → bấm link cho Chrome tải về Downloads (link có chữ ký không in ra được). Bản "Without Skin" KHÔNG có BindPose: retarget lấy T-pose từ giá trị tĩnh của xương (đã kiểm = BindPose 0°). Chrome có thể để file `.tmp` chờ "Giữ lại": file vẫn đủ (đuôi FBX đúng), chép vào `src/`.
- Chọn clip: tên Mixamo "With Axe" là thế CHIẾN ĐẤU (chân trước sau, thân chéo ~30°, tay ra trước) → không dùng dáng của thư viện cho idle game; dùng `restyle.py`: dáng = Idle1 F1 của team, chuyển động thư viện × hệ số RIÊNG TỪNG XƯƠNG theo biên độ clip team (`--k perbone`; một hệ số chung theo ngực ra ~1/5 Idle1 → Director bắt lỗi A "đứng chết"; Logger Idle cần thêm `--mul Spine2_M=0.5,Chest_M=0.6,Shoulder_R=1.6,Elbow_R=1.5,Scapula_R=1.2` để eo/ngực = Idle1 2,9°/5°, cổ tay P 18 cm; tốc độ thân TB ≥ 70% Idle1), hông theo team (Idle1 nhún 0 cm → 0), khoá chân, nối loop, video `compare_video.py`. RÌU: xương `accessory` dùng chung cho mọi prop (bút, bình xịt, can xăng, rìu AXE1 ~123 cm) → cách cầm của Idle1 là cách cầm BÚT, gắn rìu theo đó thì cán chĩa ngang ra sau (sai). Game: `LoggerController.cs` chỉ bật rìu trên tay khi đang chặt, idle bật `Axe_Back` (rìu sau lưng) → Logger Idle tay không; luôn đọc code game xem prop nào hiện ở state đó trước khi đặt tay cầm prop. Chữ tiếng Việt trên video: font `C:/Windows/Fonts/arial.ttf` (font mặc định PIL vỡ dấu).
- Thư viện chỉ là bản nền: tiếp theo đi như team đưa FBX blocking (khớp file → sửa theo GDD/gu game trên layer → polish). Kiểm giấy phép thư viện trước khi đưa vào game (Mixamo: dùng trong game được, không phát tán file gốc).

## Giãn nhịp (retime) key chính trên Frolvy (Hero_Blade Attack_02, +6 frame, 2026-11-11)
- `retime_keys` chỉ co giãn đều quanh pivot, KHÔNG dịch được (scale 1 = không làm gì) và làm tròn frame → không dùng để dời key.
- Cách dời: `copy_keys(tất cả node, a, b)` + `paste_keys(frame đích, 'replace', node)` rồi `delete_key` frame cũ trên mọi kênh. Làm từ cuối về đầu (dời đuôi +6 trước, rồi key chính từ lớn xuống nhỏ). Giữ nguyên giá trị raw (không lệch xoay), kiểm 13.8k giá trị = 0 lệch.
- Trước khi giãn: xóa in-between đã thêm (script sinh lại sau). Key chính sau giãn: 0 2 4 7 10 15 24, từ F19 dời +6.
- `tools/frolvy_inbetween.py`: `set_timing(main, stop, extra)` đặt nhịp mới rồi `run(api)`; MOVE/IB tự suy ra.
- `api.ls('*')` trả rỗng; lấy tên node từ danh sách đã lưu. `list_attrs` không gồm tx..rz (phải liệt kê kênh riêng).
- Dời key chính cũng làm key cuối (24) tính lại tangent với hàng xóm mới → đường cong đoạn sau có thể khác nhẹ bản trước (Root ry F25–29).

## Thân trên không đứng ở đoạn giữ trước lấy đà (Hero_Blade Attack_02 F9-18, 2026-11-11)
- Đoạn giữ F9→F18 mà thân trên phẳng thì nhìn "đứng": key lại F10-17 mỗi frame. Hip (Root) đi ease-in (t²) từ key F9 đến F18 → chậm đầu, nhanh dần vào pose lấy đà. Spine1 → Chest → Neck → Scapula có bump xoay nhẹ (ry/rz ~1-2°, sin(π·u^1.5)) trễ dần 1/2/3 frame, về 0 đúng ở key F18 (không đổi key chính).
- Thêm key ở F17 làm auto tangent của key F18 tính lại → đoạn F19+ lệch (tới 2.5°). Đo F19-31 trước/sau; trả lại bằng `set_key_tangent(p, 18, 0, s, broken=True)`: s=0 nếu đường cũ phẳng, còn lại tìm s tuyến tính (đo ở s=0 và s=10, giải). Đơn vị slope rất nhỏ/frame (slope 1 ≈ +0.02° ở F19).
- Shoulder CTL toàn 0 (không có chuyển động) → "vai" dùng Scapula_R/L (rz).

## Kéo dài anticipation bằng hold (Hero_Blade Attack_02, +6 frame, 2026-11-11)
- Không đụng F0-18: dời toàn bộ key từ F19 trở đi +6 (copy_keys 19..60 → paste_keys 25 'replace', xóa key cũ còn sót), rồi copy key F18 → paste F24 (key hold).
- Hold chính xác: `set_key_interp(path, 18, 'stepped')` cho mọi kênh có key F18 (tay, pole, chân giữ nguyên, không đổi tangent vào F18). Riêng hip → Spine1 → Chest → Neck → Scapula không stepped mà thêm key "thở" nhẹ (hip F20, Spine1 F21, Chest F22, Neck/Scapula F23; ~0.5-0.8°, hip ty -5 mm) rồi về đúng pose F24.
- Sau khi dời, auto tangent ở key F24 và F18 bị tính lại → đoạn vung sau bị lệch ~1-2°. Đo F25-30 trước/sau, trả lại bằng `set_key_tangent(p, 24, 0, s, True)` với s tìm tuyến tính (đo tại s=0 và s=10). Cũng làm cho vào-tangent F18 (đo theo F17) nếu F17 lệch.
- `frame_range` phải nới tới key cuối mới.

## Hip nhún trong đoạn giữ, thân hết cứng (Attack_02 F8-24, 2026-11-11)
- Thân "cứng" ở F8-14 vì hip đi ngang/phẳng, spine chain không có gì để kéo theo. Cho hip (Root ty) xuống từ F8 (đáy ~F14, -3 cm so với F8) rồi lên nhẹ tới F24; key hip trước.
- Spine1/Chest/Neck rx = giá trị cũ + G·(−Δhip trễ k frame): Spine1 G 40 trễ 1, Chest G 75 trễ 2, Neck G −35 trễ 3, nhân hệ số giảm dần (18−f)/5 để về đúng key F18 (không bị pop 2° ở F17→18).
- Key F24 đổi giá trị thì đặt in-tangent 0 và fit out-slope sao cho vận tốc đầu cú vung giữ như cũ.

## Hip hạ dần F8→F24 + overlap thân/vai/tay (Attack_02, 2026-11-11)
- File có thể bị người dùng dọn lại giữa hai lượt (key còn 0-8, 15, 24): luôn đọc key hiện có trước khi làm, không dùng số frame cũ.
- Hip ty: hạ nhanh F9–14 (smoothstep, đáy quá đà ~2 mm ở F14, bật lại ở key F15), rồi hạ chậm ease-out tới F24 (key 24 hạ thêm). Spacing mỗi frame không đều (−1 → −5.7 → +0.9 → −2 → −0.1 mm).
- Overlap: bump sin(π·u^1.3) cho từng bộ phận, trễ dần: Spine1 1f, Chest 2f, Neck 3f, Scapula 4f, tay: IKWrist_R 2f, IKWrist_L 3f, PoleArm_R 1f, PoleArm_L 2f; hai pha (F8-15 biên độ lớn, F15-24 biên độ nửa), về 0 ở các key đã có.
- Thêm key F23 làm tangent auto ở key F24 đổi → đường vung sau lệch; fit lại bằng set_key_tangent(p,24,0,s). Với kênh xoay vắt qua ±180, fit trên giá trị wrapped sai → dùng giá trị unwrapped, hoặc ghim vài key (26/28/30/32/34) bằng giá trị gốc nếu fit không khớp (IKWrist_L rz/ry).

## Blocking F8–24 (hip drop + overlap), stepped (2026-11-11)
- Chỉ key pose, không inbetween: hip trước (Root ty F11/14/18/21), rồi chuỗi trễ Spine1→Chest→Neck→Scapula, tay lệch nhịp (PoleArm/IKWrist R sớm hơn L 1f). Pose = nền nội suy giữa key chính + bump sin; set `stepped` cho key mới + F8, để key 24 spline.
- Không tin biến tail cũ (S_tail) sau khi user cấu trúc lại file: đọc key hiện tại trước.

## Overshoot sau attack + làm mượt F15–24 (Attack_02 v3, 2026-11-11)
- Mượt đoạn trước đòn: xoá key nhỏ lẻ, giữ key chính + vài breakdown; pose key chính (vd F18) phải mang cùng độ trễ với hip như các frame quanh nó, nếu không bị nhảy tại key đó. Không ép tangent vào của key đón đòn về 0 (dừng rồi bật), cũng không đặt in=out lớn (hông tăng tốc thừa): chọn in-slope để gia tốc F22–23 = 0, out-slope giữ đuôi cũ.
- Overshoot F22–35: hip lên nhanh (đỉnh ~F25) rồi xuống nhẹ + hold; thân quá đà xoay tiếp theo hướng đà vào đòn (hướng = vận tốc F20→22), mạnh ở F22–25 rồi chỉ còn ~30%, nhân kernel sin lên đỉnh t=3 rồi tắt dần (0.65e^(-(t-3)/2)+0.35e^(-(t-3)/6)); lag thân chỉ nửa lag cũ; hip trans X/Z đi tiếp ~3 cm rồi hồi. Cap: hip 3°, Spine 2.5°, Chest 4°, cổ 3°, vai 2°.
- BẪY WRAP: get_attr trả góc ±180; move_key(get_attr+offset) ghi lại giá trị đã wrap → key lệch 360° so với key kề → tay xoay một vòng giữa hai key. Với kênh xoay sát ±180 (IKWrist rz) luôn ghi lại +360 cùng vòng với key kề, rồi quét bước nhảy >180 ở mọi kênh xoay.
- Thêm key liên tiếp: đọc giá trị nền từ F-chính (không đọc curve sau khi đã thêm key kề, curve đã bị tangent kéo đi).

## Cổ tay bị xoắn trong Frolvy: cách dò và sửa (Attack_02 v3, 2026-11-11)
- `get_attr` trả góc đã TÁCH từ ma trận (bọc ±180), không phải giá trị key thật; gần gimbal (ry ≈ ±90) ra lật 180° cả ba trục. Không có hàm đọc key thô.
- Dò xoắn: `world_matrix` mỗi frame, góc giữa hai frame liền nhau = acos((trace(R0ᵀR1)−1)/2). Bình thường ≤ 5–30°/frame; 100–180°/frame = xoay một vòng giữa hai key (key khác nhánh 360° hoặc 180° tương đương euler).
- Sửa: với key lỗi, thử các biểu diễn euler tương đương ((rx,ry,rz)+k·360 và (rx+180,180−ry,rz+180)), giữ cái cho ma trận thế giới không đổi tại key đó (<1°) và GẦN NHẤT giá trị thô của key trước; ghi bằng move_key. Làm lần lượt từng key theo thời gian, rồi đo lại cả đoạn.
- Không chọn nhánh bằng "tổng góc trong cửa sổ" khi key bên cạnh chưa sửa (ra -411, -448…). Không fit tangent theo snapshot cũ (user đã thêm key khác).
- Sau khi đổi nhánh key, tangent tự tính có thể vọt (35→36 107°/frame): đặt lại tangent in=out = (giá trị key sau − key trước)/khoảng frame.
- LUẬT (user 2026-11-11): sau mỗi lượt sửa trong Frolvy, tự đo góc xoay thế giới/frame của mọi control đã đụng tới; thấy xoắn (≥ ~90°/frame) thì tự sửa luôn, không đợi user báo.
