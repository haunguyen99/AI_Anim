# INDEX - mục lục kiến thức chi tiết
Luôn đọc `CORE.md` + file này. Chỉ mở mục `details/<file>#<mục>` khi task đụng tới (Grep `^## <mục>` trong file đó).

## Cập nhật sau mỗi task (không đợi nhắc)
- Bài học mới → thêm vào đúng mục trong `details/` (chủ đề nếu dùng cho mọi loại; file loại anim nếu riêng loại đó); ghi ngày,
  câu gốc của user, số đo; bài học mới thay bài cũ thì sửa tại chỗ và ghi "cập nhật <ngày>".
- Thêm/sửa một dòng ở `CORE.md` CHỈ khi luật áp dụng cho mọi clip; giữ CORE.md < ~6 KB. Mục mới → thêm 1 dòng vào bảng dưới.
- Gọi tên nguyên lý bị vi phạm cho mỗi feedback và thêm ví dụ vào `principles.md`.

## Trạng thái theo loại anim
| Loại | File | Trạng thái |
|---|---|---|
| Idle | `idle.md` | Gaygor Idle 133F (duyệt), Idle_Front 60F (duyệt v14), SDR Idle 1 pose (v19), Ninja Idle F1 (user chỉnh, `#ninja-guard-pose`) |
| Attack | `attack.md` | Gaygor Attack 68F (làm cũ) tạm dừng; **Gaygor Attack 50 Blocking (quy trình B) polish v3 duyệt, xuất FBX 2026-10-23**; SDR Attack chốt polish v5 (xuất) |
| Shoot / Reload | `shoot_reload.md` | SDR map06 đang làm (Reload spline v3) |
| Walk/Run, Hit, Death, Skill, Jump/khác | `other_types.md` | chưa làm - khung trống + mẫu file |

## Mục lục
| Mục | Đọc khi … |
|---|---|
| **text_brief.md** | chỉ có yêu cầu bằng lời (không ref, không blocking): quy trình C, intake, bản thiết kế + bảng timing, pose 10%, phần còn thiếu (pose_build, đọc key Pose Lab, FBX nguồn) |
| **gdd_stage0.md** | có GDD (xlsx / Google Sheet) hoặc cần ảnh key pose khi không có ref: giai đoạn 0 (đọc GDD → danh sách anim → câu hỏi → phân tích có nguồn → ảnh key pose bằng Codex trên render model thật → trang duyệt), mẫu prompt, đo tỉ lệ vũ khí, lỗi Codex hay gặp |
| **user_blocking.md** | quy trình B: AI rig trên Frolvy (MCP) → user key → FBX sang Studio; hoặc team đưa FBX blocking (không ref): cổng duyệt, script mẫu, luật (RotationOrder, mũi chân, cung nhấc chân, QA fold_backs) |
| **review_process.md** `#home-app` | Home (quản lý dự án/anim), clip tạo từ Home, trạng thái hiện trên Home |
| **arms_hands.md** | |
| `#no-overbend` | tay/chân bị chê xoắn, bẻ quá; đặt tay lên prop; sau khi rig (joint_limits) |
| `#twist-split` | chia xoắn vai/cổ tay; khiên/giáp trên cẳng tay |
| `#fk-arm-plane` | dựng tay FK theo mặt phẳng khuỷu; bản lề khuỷu lệch trục, roll vô nghĩa |
| `#palm-dir` | cầm dao/prop có lưỡi; lòng bàn tay quay sai hướng |
| `#wrist-sweep-prop-dir` | góp ý về hướng prop bằng nét vẽ |
| `#free-arm` | tay không cầm gì: IK theo nhịp, nắm đấm buông bị ngửa |
| `#reach` | tay không với tới điểm cầm; tay qua đầu khuỷu khép; `solve_grip` trả None |
| `#shoulder-compression` | vai lõm, "vai bị xoắn", chọn pole; ngưỡng căng da theo mesh |
| `#elbow-pole` | "đẩy khuỷu ra", chỉnh độ cao/hướng khuỷu |
| `#pole-spec` | dựng rig IK, đặt pole khuỷu/gối; trước khi render mọi version (pole_audit) |
| `#spline-ik-arms` | spline tay đã giải IK từng key; "tay xoay loạn xạ" |
| `#prop-hand-side-fk` | tay thao tác prop ở phía xa camera; chọn FK/IK; đọc tay vs prop ở góc top |
| **qa_anatomy.md** `#joint-coupling` | dựng / sửa bất kỳ key nào; khớp dùng lẻ loi (vai đứng yên khi giơ tay, chỉ xoay đầu không xoay cổ); thêm / chỉnh luật liên động |
| **props_weapons.md** | |
| `#heavy-prop-lever` | prop nặng cầm một đầu (chùy, búa) |
| `#long-prop-flick` | đầu prop dài bị giật/vẩy |
| `#oversized-prop` | prop quá khổ so với tay (súng 1,24 m) |
| `#grip-big-shaft` | nắm cán to / áp lòng tay lên prop dày; tay chìm trong cán; nắm đấm rời prop |
| `#solve-grip-notes` | dùng `solve_grip`/`regrip` (phi, P0_STRAIN) |
| `#prop-measure` | đặt/đo vị trí, hướng, độ cao prop từ ref; note khoanh prop |
| `#prop-penetration` | prop xuyên thân/đầu/áo; tránh xuyên mà tay căng |
| `#grip-drum` | cầm trống/băng đạn tròn |
| `#flat-prop-orient` | prop dẹt (trống, khiên, dao) cắm vào áo hoặc quay cạnh về camera |
| `#gun-aim` | súng/tay ngắm; hướng aim ở góc top |
| `#thrown-prop` | prop bay/ném: constraint, curve, bia, điểm thả |
| **torso_head.md** | |
| `#spine-chain` | cột sống gãy khúc, lưng ưỡn ngược, dời Chest |
| `#partial-fix-hip` | sửa hông/một phần mà giữ nguyên thân trên |
| `#world-axis-roll` | xoay theo trục world sau khi người đổi hướng; vai bị bẻ xuống |
| `#twist-reading` | đọc độ xoắn thân từ ref |
| `#body-height` | quyết định độ gập thân theo đỉnh đầu |
| `#square-body` | thân lăn/xoắn khi ref đứng vuông (sym_fix) |
| `#open-to-camera` | game side-scroll; ngực quay về camera; lấy đà đọc từ camera |
| `#lean-from-hip` | "đổ người về trước" |
| `#head` | khoá hướng nhìn, đầu mở ra cam, đầu ngửa/chúi |
| **legs_feet.md** | |
| `#steps-contacts` | có bước chân / tấn đứng |
| `#weight-shift` | một chân nhấc, dồn trọng lượng |
| `#foot-detach` | bàn chân đứt khỏi ống chân, "dưới đất", dời hông để chân với |
| `#knee-dir` | hướng gối, pole gối, chân sau duỗi căng |
| `#hip-height` | đo độ cao/góc xoay hông |
| `#floor` | sai số sàn cộng dồn giữa các key |
| **timing_spline.md** | |
| `#shared-curve` | chuyển động chu kỳ (thở, nhún) |
| `#easing` | "khựng", "đập đáy", slow in/out |
| `#overlap` | overlap/follow-through; resample trễ; frame hiển thị khác key |
| `#lag-measure` | đo độ trễ từng bộ phận |
| `#breakdowns` | spline từ blocking: breakdown slerp |
| `#spacing` | "nhảy", "về quá nhanh", đo cm/F |
| `#split-timing` | giãn một phần/một chuỗi xương mà giữ phần khác |
| `#secondary-cloth` | vải, tóc, đuôi, vạt khố |
| `#loop` | clip loop, nối seam |
| `#end-on-idle` | đuôi clip non-loop cho game |
| **review_process.md** | |
| `#reviewer-prefs` | trước khi trả lời/gửi bản cho user |
| `#director` | trước mỗi cổng duyệt: gọi subagent animation-director, đọc director_log |
| **director_standards.md** | trước khi director chấm; sau MỖI lần user duyệt/trả (so với director, ghi calibration) |
| `#naming-principles` | ghi feedback vào knowledge |
| `#self-measure` | trước khi gửi review; sau mỗi lần sửa |
| `#eye-vs-iou` | so ref vs anim; IoU cao mà vẫn bị chê |
| `#coarse-to-fine` | bắt đầu blocking; bị chê "chia bộ phận ra làm từng phần" |
| `#per-view-pass` | được yêu cầu sửa từng view |
| `#self-review-sheet` | "tự view lại bằng mắt" |
| `#circled-notes` | note chỉ khoanh, không chữ; note trong đoạn hold |
| `#p0-lock` | trước khi block clip đầu tiên của nhân vật; định đổi P0 |
| `#still-options` | một hướng sửa thất bại; cần user chọn phương án |
| `#no-ref-clips` | clip không ref / theo concept / ref điện ảnh |
| `#approve-export` | user nói "oki rồi" |
| `#pose-lab-3d` | user muốn sửa pose trực tiếp trên trang 3D; xuất model / áp điều chỉnh 3D về Blender |
| **qa_anatomy.md** | |
| `#pre-send-checklist` | trước mỗi lần gửi review |
| `#anatomy-check` | chạy anatomy pass; đọc ngưỡng da |
| **export.md** | |
| `#reparent-prop` | intake (prop treo joint nào); đổi cha joint prop sau khi bake |
| `#export-clip` | xuất FBX, tên take, kiểm đọc lại |
| `#anim-only` | dev chỉ cần joint + anim |
| `#variants` | prop ném: bản bay / bản theo tay |
| **principles.md** | |
| A. Từng nguyên lý | gọi tên nguyên lý cho feedback; thêm ví dụ |
| B. Quy trình ↔ nguyên lý | chọn nguyên lý trọng tâm cho bước pipeline |
| C. Theo đối tượng | hông, cột sống, tay, đạo cụ, vải… nguyên lý + cách làm |
| **idle.md** | |
| `#goals` `#breath-recipe` `#params` | làm idle thở / idle mới (công thức Idle_Front v14) |
| `#feedback` `#errors` `#qa-checklist` `#tools` | sửa feedback idle; QA idle |
| `#sdr-one-pose` | idle 1 pose theo concept; tấn đứng, đổ người, xoắn eo |
| `#ninja-guard-pose` | thế thủ chibi cầm vũ khí ngắn; user tự chỉnh pose AI; khăn rời lún vào lưng |
| **attack.md** | |
| `#status` `#goals` `#recipe` `#params` | làm attack; Gaygor Attack |
| `#feedback` `#errors` | tra feedback/lỗi Attack đã gặp (con trỏ tới mục chủ đề) |
| `#qa-checklist` `#tools` | QA pose blocking Attack; script Attack |
| `#sdr-attack` | ném dao SDR: nhịp recover, 2 tay lệch pha, điểm thả |
| **shoot_reload.md** | |
| `#trigger-hand` | reload: tay cầm cò |
| `#reload-minimal` | reload/động tác từ ref điện ảnh cho game |
| **other_types.md** | |
| `#template` | bắt đầu loại anim mới |
| `#locomotion` `#hit` `#death` `#skill` `#other` | đặc trưng các loại chưa làm |
