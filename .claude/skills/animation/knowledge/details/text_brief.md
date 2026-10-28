# text_brief — Quy trình C: chỉ có yêu cầu bằng lời (không ref, không blocking)

Người dùng yêu cầu thêm nhánh này ngày 2026-10-24: "thêm một nhánh nữa là những anim chưa có ref chưa có blocking, chỉ có
yêu cầu đơn giản". Ví dụ yêu cầu: "Gaygor bị đánh trúng", "chết ngã ngửa", "gầm lên khiêu khích".
Không dùng Blender. Pose dựng bằng Python trên rig (cùng hạ tầng với nhánh B) và chỉnh trên Pose Lab. Chuyển động xem
trên Review Lab.

**Trạng thái:** chưa chạy thử trọn vẹn. Nửa sau (từ bước C5) dùng lại nhánh B, đã chạy xong trên Gaygor Attack. Những gì còn
thiếu ghi ở cuối file. Clip đầu tiên đi nhánh C sẽ viết các phần đó và cập nhật file này.

## Vì sao khác nhánh A và B
Không có gì làm chuẩn để "khớp". Mọi pose và mọi nhịp đều là **thiết kế** của AI, nên rủi ro nằm ở chỗ AI hiểu sai ý người
dùng chứ không ở chỗ đo sai. Vì vậy nhánh C có nhiều cổng duyệt sớm và rẻ (chữ, ảnh tĩnh) trước khi làm chuyển động. Bài
học SDR Attack (không ref, khoảng 17 vòng góp ý, phần lớn ở pose đứng F1 và nhịp hồi): chốt pose đầu/cuối và nhịp tổng
bằng ảnh tĩnh cùng bảng timing thật sớm → `review_process.md#no-ref-clips`.

## Các bước và cổng duyệt

| # | Bước | Ra gì | Cổng |
|---|---|---|---|
| C1 | **Intake: hỏi gộp một lần**, chỉ những gì chưa biết: nhân vật; tên clip; độ dài (số frame @ fps, hoặc để AI đề xuất); loop hay một lần; tại chỗ hay có root motion; camera trong game (góc nhìn chính); sự kiện gameplay (frame trúng đòn, lúc được huỷ đòn); prop và khớp cha của prop; pose đầu và cuối (mặc định là F1 của Idle đã duyệt của nhân vật để chuyển clip không giật). | `work/<dự án>/<id>/brief.md` | — |
| C2 | **Bản thiết kế** (thay cho phân tích ref). Gồm: đặc tính nhân vật lấy từ rig (`measure.py`: tỉ lệ, prop, xương phụ) và từ các clip đã duyệt (tính cách, tư thế đứng); ý đồ hành động theo từng pha có frame; **bảng timing** (danh sách key, đánh dấu tầng 10/25/50%: pose kể chuyện → pose chuyển chính → breakdown); từng bộ phận; chuyển động phụ; sự kiện game. Mỗi ý ghi nguồn: [yêu cầu] / [nhân vật] / [thiết kế] / [game]. Yêu cầu mơ hồ thì đưa 2–3 phương án ngắn để người dùng chọn → `review_process.md#still-options`. | `work/<dự án>/<id>/analysis.md` | **Duyệt thiết kế** |
| C3 | **Pose kể chuyện (10%)**: 3–8 pose chính dựng trên rig theo cấp thô → tinh (chân/hông → thân/đầu → prop → tay → bàn tay, `review_process.md#coarse-to-fine`). Đưa lên Pose Lab (mode keys, interp step), kèm ảnh tĩnh ở camera game và góc trên. Người dùng có thể **tự chỉnh pose ngay trên Pose Lab**. AI đọc key trong db, đối chiếu trước khi sửa, không ghi đè phần người dùng đã chỉnh. | version `k10_vN` | **Duyệt pose chính** |
| C4 | **Blocking 25–50%**: thêm anticipation, contact, extreme theo bảng timing; stepped; dùng các luật dựng pose của nhánh A (`CORE.md`: tầm với, pole, cột sống, chân không đứt…). Kiểm khớp mọi key (`check_v4.py`). | version `b50_vN` | **Duyệt blocking** (tương đương "khớp file" của nhánh B) |
| C5–C8 | **Đi tiếp đúng nhánh B từ bước 3**: sửa lỗi (sàn, trượt chân) → pose chuyển tiếp → trọng lượng → spline + polish nướng từng frame + QA + playblast Review Lab → xuất FBX (+ anim_only). | như nhánh B | **Duyệt 75%**, **duyệt polish** |

Mỗi cổng làm giống nhánh B: commit kèm câu của người dùng, tag bản duyệt, `clips.json` (note có chữ "chờ"), cập nhật MAP và file này.
Giai đoạn trong sổ: `analysis` → `p0` → `blocking` → `polish` → `export`.

## Luật thiết kế (khi không có gì để chép)
- **Đọc ở camera game:** thiết kế theo dáng nhìn (silhouette) ở góc game, không theo giải phẫu hay động tác ngoài đời → `review_process.md#no-ref-clips`.
- **Bản tối giản trước:** ít đổi tư thế thì ít lỗi xuyên và ít vòng sửa. Đề xuất bản đơn giản đọc rõ, thêm chi tiết khi người dùng muốn.
- **Tính cách nhân vật có sẵn:** lấy từ clip đã duyệt (vd Gaygor: vũ phu, nặng, tấn thấp, vai rộng gấp 2,5 hông, chùy 2,46 m). Hành động mới phải cùng "giọng" đó → `user_blocking.md` (phân tích Attack).
- **Độ nặng ngay từ thiết kế:** ghi rõ trong bảng timing chỗ nào nhún lấy sức, chỗ nào ì, chỗ nào lún sau va chạm → `timing_spline.md#heavy-prop-weight`.
- **Pose đầu và cuối = Idle F1** (trừ khi người dùng muốn khác), để chuyển clip trong game không giật → `export.md#loop-and-hold`.
- **Mọi con số đặt ra đều kiểm lại được:** độ cao đỉnh đầu, tầm với, chân chạm đất. Đo trên rig rồi mới đưa cho người dùng.

## Còn thiếu (làm ở clip đầu tiên của nhánh C)
1. ~~`pose_build.py`~~ **ĐÃ CÓ** (2026-10-24, Gaygor Hit): `work/boss_gaygor/gaygor_hit/pose_build.py`. Idle F1 đổi sang hệ xương rig chính
   xác (bind pose của file Blender xuất và file team trùng 0 cm / 0,02°). Lớp `Pose` có `hips`, `spine`, `head`, `shrug`, `foot`,
   `hand` (IK, giữ hướng cổ tay), `arm_fk` (xoay cả tay ở vai, giữ khuỷu: dùng cho tay tự do bị trễ), `fist`. Chân tự khóa, chùy theo
   tay trái. `measure()` so với Idle; `selfcheck()` kiểm chiều (pitch > 0 = ngả sau). Ảnh duyệt: `stills.js` (mỗi key một hàng:
   cam game, trên, trước) qua `save_srv.py`. Bài học: đo độ ngả thân từ hông tới **cổ** (khớp ngực không dời khi ngực xoay quanh
   nó); giữ tay tự do đứng yên bằng IK khi ngực lùi làm khuỷu duỗi thẳng 178° → dùng `arm_fk`.
2. **Đọc key người dùng chỉnh trên Pose Lab về Python:** db `keys/<clip>-<version>-F<f>` lưu local three.js `[qx,qy,qz,qw,px,py,pz]`. Local của model Pose Lab chính là local FBX (cm), riêng xương `root` thêm Rx(−90) (ngược lại với `make_model.py`). Viết hàm đổi ngược và kiểm bằng phép đi một vòng (FBX → trang → FBX).
3. **FBX nguồn để xuất:** `export_fbx.py` thay đường cong trong một FBX có sẵn. Cần một FBX của rig có đường cong cho mọi xương, vd một clip đã xuất của chính nhân vật đó (Gaygor: `work/boss_gaygor/gaygor_attack_50_blocking/export/EN_M11_Boss_Gaygor_Attack.fbx`), rồi đổi số frame và tên take. Nếu nhân vật chỉ có FBX rig không có animation thì phải tạo AnimationCurveNode/Curve mới; phần này chưa làm.
- Gaygor Hit b50_v1 (2026-10-24, bước C4): pose 25–50% dựng theo thiết kế (không nội suy), giữ nguyên 6 pose đã duyệt.
  Bài học: (1) nâng prop "khỏi vai" bằng dời tay theo thế giới không đủ, vì vai cũng nhô theo ngực (F5 chùy còn ép sát
  vai hơn, 6,9 cm). Đo và đặt khoảng hở so với vai: `Pose.mace_gap(cm)` (lúc nghỉ 8,5; F5 17 → F6 14 → F8 11 → F10 8,5 →
  F12 10,4 nảy). (2) `arm_fk` với tay đang buông: pitch > 0 đưa bàn tay ra TRƯỚC, roll > 0 đưa vào TRONG; đo hướng cổ tay
  sau mỗi thao tác. (3) Ảnh duyệt blocking: một góc mỗi tấm, key theo lưới đọc trái sang phải, key mới tô màu khác
  (`stills.js` cfg.view/cols/mark).
- Gaygor Hit b75_v1 (2026-10-24, bước C5 = nhánh B bước 3–5): blocking 50% không có lỗi để sửa (chân cắm ≤ 0,3 cm, mũi
  chân −0,4/−0,5 cm như chính Idle F1 đã duyệt). Pose chuyển tiếp bằng hàm DÙNG CHUNG `pose_build.breakdown(A, B, t, offsets,
  mace_t, lift_arc="ground", hips/spine/head/gap)` thay cho `breakdowns_v4.py` (gắn với Attack): chùy blend trong không gian
  ngực rồi tay trái IK theo chùy; thêm bộ lệch nhịp `WHIP` cho cú trúng đòn (ngực dẫn, đầu/tay/chùy trễ 0,15–0,2).
  QA riêng `hit_check.py` (khoảng khớp theo key đã duyệt, đi vòng, sàn, chân, khe chùy–vai ≥ 7 cm, nhịp chùy/hông từng
  frame). Chỉ một cờ "đi vòng" ở F14 = lắc đầu có chủ ý.
- Gaygor Hit b75_v2 (2026-10-24, user: "phần bàn tay bên có khiên đang dao động hơi mạnh, không thực tế"): thiết kế cho tay
  phải văng ra sau 26 cm rồi vung ngược ra trước 25 cm "giữ thăng bằng" (17 cm/F). Tay nặng có giáp/khiên phải ĐI THEO THÂN:
  đo chuyển động riêng của tay trong không gian ngực, giữ ≤ ~10 cm, một chiều (trễ rồi lắng), không đảo chiều; nhún vai
  nhỏ và đều (6° → 0 trong 3 F làm tay giật 10 cm). Rule for designs: chi nặng/có giáp không dùng để "giữ thăng bằng".
- File Idle đã duyệt `work/boss_gaygor/idle/export/EN_M11_Boss_Gaygor_Idle.fbx` có Wrist_R scale không đều (1,026/0,935/1,012) suốt clip.
  `pose_build.idle_f1` bỏ phần scale (giữ xoay, lệch 0,5° so với trước). Phép đo góc giả định ma trận thuần xoay: ma trận có
  scale tự báo "lệch 12,5°" với chính nó, nên trực chuẩn hoá trước khi đo.
- Gaygor Hit polish_v1 (2026-10-24, bước C6): polish viết lại trên `pose_build` (`work/boss_gaygor/gaygor_hit/polish_v1.py`, QA
  `polish_check.py`), cùng công thức polish Attack đã duyệt nhưng dùng được cho mọi clip của rig: PCHIP + chùy theo ngực +
  tay trái IK + chân khóa + đế ≥ mức của Idle + lò xo phụ. Kết quả đầu tiên sạch (IK 0,002 cm, không pop, không gập
  ngược, chân trượt 0,2 cm, lò xo ≤ 12°): vì blocking 75% đã kiểm kỹ ở từng key nên polish ít lỗi hơn hẳn Attack.
  Playblast `pb_capture.js` bản riêng (khung từ bounds của Hit; nhớ đổi cả vector hướng F/R — lần đầu sed sót).

## Gaygor Die (2026-10-25): quy trình C có ragdoll
- **C1:** hỏi gộp 4 câu (kiểu chết, nguyên nhân, chùy, độ dài). Bạn chọn: ngã ngửa, đòn từ trước, buông chùy, AI đề xuất.
- **C2:** bản thiết kế đo vật lý trước bằng ragdoll trên một clip có tư thế Idle (cuối Hit): lưng chạm đất 10–14 F sau đòn, nằm yên 40–67 F. Vì đổ thuần vật lý quá nhanh để kể chuyện, chèn thêm pha "gượng và khuỵu" key tay (F10–19) trước khi ragdoll bắt đầu ở F20.
- **C3:** pose diễn (F1, F3, F12, F20) dựng bằng `pose_build.py`. Pose chạm sàn và nằm yên lấy từ ragdoll:
  - nạp bản tạm (4 key, spline) vào Pose Lab trên máy;
  - bật ragdoll từ F20, buông chùy F23;
  - xuất `PHYS.out[f]` qua `save_srv.py`;
  - `die_k10.py --rag` đổi local trang về local FBX (root bỏ Rx(-90)).
- **Ragdoll phải chạy ở spline:** với key bậc thang, frame trước điểm bắt đầu giữ pose cũ, nên ragdoll nhận một vận tốc đầu khổng lồ.
- **Frame chạm sàn đo theo ngực, không theo điểm thấp nhất.** Khiên và chùy chạm trước lưng 2–6 F.
- **Nhìn ở cam game trước khi gửi.** F20 bản đầu (hông lùi 22 cm, thân ngửa 16°) vẫn đọc như dáng khom của Idle. Phải tăng lên hông lùi 28 cm, thân ngửa 24°, đầu ngửa 18° mới thấy "mất thăng bằng ra sau".
- **C4 blocking b50_v1 (2026-10-26):** key diễn thêm F6/F8/F17 (`die_b50.py`), phần đổ là ragdoll trên model tạm, key vật lý F28/36/46/52/55/60/72 (`rag_b50.json`).
  - **Chân đổ muộn:** gối phải giơ lên chỉ đổ xuống ở F78, quá clip 72 F. Một cú đẩy nhẹ vào gối (Tác động, light ×0,15 ở F42, hướng đổ của gối) cho nằm yên ở F63. Đẩy ở F44–46 thì vẫn còn lắc ở F72.
  - **Ma sát sàn** phải tính trên xung (giới hạn μ·lực pháp tuyến·h). Bản cũ yếu 3–5 lần, người trượt mãi.
  - **Đầu ngửa của pose đã duyệt không chép được sang lần ragdoll khác:** thân nằm nghiêng 35° về phía khiên (lưng gù và khiên đỡ), nên tư thế cổ nghỉ làm đầu nhấc lên 23 cm. Phải tìm lại góc cổ/đầu trong giới hạn khớp (mặt lệch trời tốt nhất 47°). Lăn người cho phẳng thì người bị nhấc khỏi sàn 28 cm, nên giữ tư thế vật lý.
  - **Sửa xuyên thân sau ragdoll** (tiếp xúc giữa các khối chỉ chặn vận tốc, nên lún 3–8 cm vẫn còn): xoay hông 4→8→14° rồi giữ nguyên tới hết, không trả về 0. Lúc nằm yên mà chân nhúc nhích thì sẽ thấy.
  - **Hơi thở cuối:** gập Spine1/Chest 3–4°, hai tay giữ góc world, vai phải chỉnh lại để khiên không xuyên sàn. Ngực nhấc 3 cm.
- **C5 nối vật lý phys_v1 (2026-10-26):** lưu mọi frame của trang thành key: F1–19 là spline key diễn, F20–72 là ragdoll bake. Các lớp chỉnh tính theo frame bằng smoothstep, không chỉnh từng key riêng lẻ, vì chỉnh riêng thì các frame giữa lại xuyên (gối lấn khiên F37–40, chùy lấn vai F18–22).
  - **Lớp Tác động ở F3 trên key đã diễn sẵn cú giật thì bỏ.** Lực tắt chậm, vẫn lệch 2–5 cm tới F20; `pin` không chặn được lớp Tác động; nó làm lệch pose F12 đã duyệt và làm người không nằm yên kịp trước F72. Lò xo của nhân vật cũng vậy (tay phải lệch 7–19 cm). Để dành cho polish.
  - **Chùy của Gaygor là xương `Weapon` (con của root),** không phải `Prop_M`. Sửa chùy thì xoay `Weapon` quanh cổ tay trái. Dùng quy hoạch động trên từng frame (phạt độ xuyên + phạt đổi góc giữa hai frame), ra đường 1→8→0° quanh trục đứng, sạch mọi frame.
  - **Đầu quay mặt lên** trong 6 frame thì 18°/frame, trông như giật; kéo ra 12 frame còn 13°/frame.
  - Trang có chặn sàn riêng: chân lún 1,6 cm (F22) thì trang tự nhấc lên. Model và trang lệch nhau đúng chỗ đó, không phải lỗi.
- **C6 polish_v1 (2026-10-26):** `die_polish_v1.py` chạy trên các frame phys_v1 (`rag_c5.json` → `die_k10.from_page`), dùng các khối polish của Hit:
  - tay trái IK lên cán tới lúc buông (spline của trang làm tay lệch tới 2 cm);
  - khóa chân cắm. Đừng khóa frame mà spline đã bắt đầu nhấc chân (F4 bị kéo về 4,7 cm), cho F4 khóa một nửa;
  - lọc gauss nhẹ chân phải quanh cú đẩy F42;
  - lò xo vạt khố và `Prop_M` có chặn sàn: vạt sau nằm dưới lưng, chặn 98 lần.
  - Giới hạn cứng 15° làm lò xo nằm phẳng ở mức trần suốt 5 frame lúc sập; đổi sang tanh.
- **QA:** `die_polish_check.py` chạy `gaygor_hit/polish_check.py`. Mục khớp "ngoài khoảng của key" ở F32–35 (khuỷu phải duỗi 170° khi khiên đập sàn) là vật lý thật. Khoảng đó chỉ lấy từ key diễn.
- **Playblast Die:** `pb_capture.js` (góc từ trên đặt đầu, khung cố định tâm z −1,3…−1,65). Chùy nằm xa tới 3 m sau F1, nên phải thử F1, F12, F72 trước khi quay cả clip; lần đầu bị cắt ở cả ba góc.
- **polish_v2 (2026-10-26, "làm mềm tay và chùy F1–19 như Hit v4–v7"):** `die_polish_v2.py` dùng lại các lớp của Hit:
  - tay phải như Hit v4; bả vai trái và khuỷu trái như Hit v5; chùy như Hit v7, giữ đúng thông số đã duyệt;
  - chạy F1–22, lệch của mỗi lớp tắt dần bằng smoothstep F17–22 để nối êm vào ragdoll (chùy rời tay F23).
  - **Khe chùy–vai phải đo tới cả đoạn vai→khuỷu,** như bodyIssues của trang. Đo tới điểm khớp vai thì Python báo sạch mà trang vẫn báo lấn 2–3 cm (F16–17).
  - **Lớp an toàn đẩy cứng gây giật:** đẩy 23° trong một frame ở F7. Cho đệm mềm làm việc, lớp an toàn chỉ can thiệp khi lấn sâu hơn 1 cm (`V2_SAFE`).
  - **Nới cả mức khe tối thiểu (+1,5 cm) là sai:** bả vai trái mất hết độ trễ, và F21 bị đẩy 15°.
