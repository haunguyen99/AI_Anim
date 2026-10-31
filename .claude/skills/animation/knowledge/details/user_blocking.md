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
