# Attack (riêng cho loại đánh)
Bài học dùng được cho mọi loại đã chuyển sang các file chủ đề (`arms_hands`, `props_weapons`, `torso_head`, `legs_feet`,
`timing_spline`, `review_process`, `blender_tools`, `qa_anatomy`, `cascadeur`, `export`); ở đây chỉ còn phần riêng của Attack
và con trỏ tới chỗ mới.

## status
> Gaygor Attack (68F, cửa sổ `work/boss_gaygor/blender/boss_attack_v4.blend`, bản lưu `boss_attack_v6.blend`, cổng MCP 9877).
> Blocking v9 (27 key, 2026-10-21, bản lưu `boss_attack_v9.blend`) đã lên trang review. Nạp môi trường mỗi lệnh MCP:
> `exec(open(ROOT + "/work/blender/attack_load.py", encoding="utf8").read())` (ROOT = thư mục dự án).
> Sau đó (2026-10-21) Gaygor Attack chuyển sang Cascadeur: `#cascadeur-keys` (tới casc_blocking_v4).
> 2026-10-22 user quay lại Blender: "làm tiếp Attack với blender", chọn tiếp từ `boss_attack_v9.blend` (bỏ bản Cascadeur). Lỗi v9 tự soi: `work/boss_gaygor/attack/v10rev/defects_v9.md`.
> Blocking v10 (2026-10-22, `boss_attack_v10.blend`, sửa trong `work/boss_gaygor/attack/v10/fixes.py`: mỗi `fixNN()` bắt đầu bằng `goto_v9(NN)` nên chạy lại
> được) đã lên trang review: f8 f17 f21 f28 f49 f52 f53 f58 sửa, IoU view left +0,03–0,11. Còn: f25 chỉnh nhẹ, f58 nắm tay cần xa thân
> thêm ~20 cm (xoay ngực), f17 cổ tay phải sát giới hạn, xoay cánh tay trên nhảy giữa các key (xử lý lúc spline).

## goals
- Thường không loop; có anticipation -> strike -> follow-through -> recover; impact frame phải đọc rõ từ camera game.
- Đòn "ném cả người": lấy đà dài, ra đòn rất nhanh (Gaygor: f31 -> f33, 2F), giữ impact lâu, dậy chậm.
- Thường có bước chân - đo bằng dải tiếp đất (`legs_feet.md#steps-contacts`).
- Đuôi clip = pose Idle đứng yên (`timing_spline.md#end-on-idle`).

## recipe
Đang kiểm chứng trên Gaygor:
1. Phân tích: số đo silhouette mỗi frame (đỉnh, dải tiếp đất 3 góc, độ rộng từng hàng ở góc top/bên) + ảnh 5 góc lớn từng
   pose then chốt; ghi [đo]/[mắt]; kiểm kê phụ kiện (`rig_inventory.py`). Người dùng duyệt trước khi đụng rig.
2. Scene: hiệu chỉnh camera riêng cho clip; dựng nền từ file đã duyệt (P0); prop sang không gian world; IK cho tay thứ hai,
   căn bản lề khuỷu; tự kiểm tra rig.
3. Key pose khó trước để chốt rig (f13 xoắn + 2 tay, f25 chùy sau lưng, f31 qua đầu, f33 nằm sấp), từng pose một:
   chân + hông -> prop (đo trục) -> thân/đầu (đo đỉnh đầu, xoắn bằng mắt) -> tay (`solve_grip`) -> nhìn cận -> gửi duyệt.
   (Từ 2026-10-21 mặc định blocking nhanh toàn thân rồi sửa chi tiết: `review_process.md#coarse-to-fine`.)
4. Phần còn lại: blocking stepped toàn clip -> Duyệt 2 -> spline/polish (vạt khố + mặt vòng: overlap nhẹ, đã được chọn).

## params
Chưa duyệt - mốc tạm:
- Camera Attack Gaygor: 231.3 px/m, sàn y 910, gốc x front 1056.5 / back 862.5 / `_right.mov` 953.5 / `_left.mov` 965.5,
  top (1056.5, 545.5); `_left.mov` = camera bên PHẢI nhân vật.
- f13 v2 Blender (`work/boss_gaygor/attack/pose_f13.py`, `look_v4/grip_f13b.json`): chân trái dời (0.17, -0.15) m, xoay 15°; hông xoay trái 85°,
  không hạ; ngực xoắn phải -45° (Spine1 -18, Chest -27), cổ/đầu ngẩng 35°; chùy trục (0.18, 1, 0) giữa (0.87, 0.72, 1.02);
  tay trái đỡ dưới (s 0.15, phi 210), tay phải trên đầu tròn (s -0.6, phi 0). IoU 0.69-0.78, đỉnh đầu 1.89 m (ref 1.88).
  **Bị thay bởi f13 Cascadeur (2026-10-21):** hông ~60°, KHÔNG xoay 85° (góc back mất vạt sau) - xem `#cascadeur-keys`.

## feedback
| Câu gốc | Nguyên tắc |
|---|---|
| "Không pose nào giống ref" / "Tệ quá" (v2, 2026-10-19) | Dựng từng pose một với ảnh lớn 5 góc → `review_process.md#eye-vs-iou` |
| "hai cánh tay bị bẻ quá giới hạn và xoắn vặn hỏng anatomy" (f13 v1) | `solve_grip`, không ép hướng bàn tay → `arms_hands.md#no-overbend`. Solid Drawing |
| "Frame này chưa được... chia các bộ phận ra làm từng phần..." (f13 v1) | Dựng theo cấp → `review_process.md#coarse-to-fine`. Solid Drawing, khối lớn trước |
| "check lại Anatomy toàn thân của từng key chính đã key" (blocking v4) | `anatomy_check.py` mọi key → `qa_anatomy.md#anatomy-check` |
| 8 ghi chú chỉ khoanh tròn, không chữ (blocking v5) | → `review_process.md#circled-notes`, `props_weapons.md#prop-measure`. Solid Drawing, Staging |
| "cần phân tích cả quần áo, vải, phụ kiện... chain tóc, đuôi, tai, áo choàng" | → `blender_tools.md#rig-inventory` |
| "Sai pose" f38 (v6) | Cả đoạn giữ dáng sai → `review_process.md#circled-notes` |
| "chưa được, tự view lại bằng mắt" (v7) | → `review_process.md#self-review-sheet`, `torso_head.md#square-body` |
| "Tay tương tác với vũ khí chưa được tốt" (v8) | → `props_weapons.md#grip-big-shaft` |
| "view lại và sửa từng view một. bắt đầu với view left" (casc_blocking_v1) | → `review_process.md#per-view-pass`, `#cascadeur-keys` |

## errors
Lỗi đã gặp ở Gaygor Attack (Blender) - nội dung đã chuyển:
camera dùng lại của Idle → `blender_tools.md#review-files`; thân gập quá f13 → `torso_head.md#body-height`; xoắn ngực đọc nhầm →
`torso_head.md#twist-reading`; chùy lệch/độ cao chùy/tam giác hoá → `props_weapons.md#prop-measure`; tay trái không với tới, tay qua
đầu khuỷu khép → `arms_hands.md#reach`; IK tay phải lệch trục → `arms_hands.md#fk-arm-plane`; pose bị ghi đè, quaternion 0, scale trôi →
`blender_tools.md#live-posing`; f25 dồn trọng lượng → `legs_feet.md#weight-shift`; f13 đầu ngửa → `torso_head.md#head`; `P0_STRAIN`,
phi → `props_weapons.md#solve-grip-notes`; bẫy batch v4 → `blender_tools.md#batch-fit-traps`; bàn chân đứt, "dưới đất" →
`legs_feet.md#foot-detach`; căng da so bind, knee_dir → `qa_anatomy.md#anatomy-check`, `legs_feet.md#knee-dir`; view left =
right.mov, ảnh > 1500 px → `blender_tools.md#review-files`; áp lòng bàn tay, nắm đấm rời chùy f60 → `props_weapons.md#grip-big-shaft`.
- Danh sách lỗi tự soi v9 ghi sai BÊN ở f28/f58 ("trái" thay vì PHẢI) — analysis đã duyệt [đo] nói chân phải nhấc f25–30, tay phải buông
  f58. Trước khi sửa một lỗi tự soi, đối chiếu bên trái/phải với analysis.json. f33/f42 "chân trái co" cũng là đọc nhầm: ref co gối
  trái thật, duỗi ra thì IoU giảm → giữ v9 (2026-10-22).

## qa-checklist
Riêng mỗi pose blocking Attack (checklist chung: `qa_anatomy.md#pre-send-checklist`):
- REF | ANIM 5 góc (`eye_side.py`), IoU từng góc; ảnh chồng 2 màu (`eye_diff.py`: đỏ = ref có, xanh = anim thừa) để biết
  HƯỚNG sai; độ rộng từng hàng/cột (`extent_cmp.py`) để biết sai bao nhiêu mét; đỉnh đầu; bàn chân theo dải tiếp đất.
- Tay nào nắm đâu: zoom vùng tay ở ref (ảnh lớn), xét mặt nào của cán bàn tay nằm (camera nào thấy bàn tay).
- Nhìn cận 2 tay (`closeup`), độ giãn da vai/khuỷu/cổ tay so với P0 (`arm_strain`); khuỷu ngoài thân.
- Impact frame: đạo cụ đúng vị trí, silhouette rõ ở camera game.

## tools
`work/blender/attack_pose.py` (posing mode `from_p0`/`goto`/`key_pose`/`unkey`/`done`, `eye`, `closeup`, `body_top`, `set_weapon`,
`solve_grip`/`apply_grip`, `arm_strain`/`p0_strain`, `clean_scales`, `sweep`), `build_attack_v4.py`, `rig_attack_v4.py`,
`rig_attack_v4_fix.py`, `rig_attack_v4_armR_hinge.py`; `tools/eye_side.py`, `legacy/blender_tools/sil_compare.py`, `tools/sweep_score.py`,
`legacy/blender/sil_render.py`, `eye_views.py`, `rig_inventory.py`, `tools/eye_diff.py`, `tools/extent_cmp.py`;
playblast có ref: `attack_pose.playblast_frames` + `legacy/blender_tools/playblast_ref.py` (REF | ANIM, đánh dấu KEY / hold).
Fit/sửa: `attack_fit.py` (fit theo bóng 5 view), `anatomy_check.py` + `anatomy_fix.py`, `mace_measure.py` (tam giác hoá điểm
chùy từ pixel 2 view, cho phép toạ độ None), `mace_refix.py` (`refix` khoá chùy đo được rồi fit thân, `regrip` đặt lại điểm
nắm), `sym_fix.py` (đường hông/vai/cột sống về đích), `work/boss_gaygor/attack/v7rev/sheet.py` (bảng rà mỗi key), `work/boss_gaygor/attack/crop_cmp.py`
(REF | ANIM cắt cùng pixel, chạy bằng `.venv/Scripts/python.exe`), `hand_contact.py` (`palm_seat`, `wrap_mesh`); một dòng nạp `attack_load.py`.

## cascadeur-keys
Gaygor Attack trong Cascadeur — blocking nhanh 4 key khó (2026-10-21). Đo trên ref (frame N ref = frame N-1 Cascadeur; cm, Y lên,
nhân vật nhìn +Z, trái = +X). Chùy dài ~250 cm: s ≈ −75 (đuôi cán) … +175 (mũi vuốt) dọc trục +Y cục bộ của joint `Weapon`.
Tham số đầy đủ ở `work/cascadeur/keys/fNN.json`. Bài học Cascadeur chung: `cascadeur.md`.
- f13: hông xoay ~60° về +X (P0 15° + 45°), chúi trước 30°, gốc (−4, 68, −18); KHÔNG xoay 85° (góc back mất vạt sau) và không hạ hông
  (đai f13 còn cao hơn f1 ~2 cm). Ngực xoắn ngược lại (yaw +30 so P0), gập 12°. Chùy trục (0,32; 0,05; −0,95), đuôi cán Z≈+55, cao ~1 m.
  IoU 0,70–0,78.
- f25: chân phải nhấc ~20 cm, mũi chúc; hông dời (+26, +4, +6), bớt chúi; thân ngả sau 30°, ngực về chính diện; chùy vác chéo,
  trục (0,37; −0,53; −0,75), đầu tròn trên đầu (~205 cm). IoU 0,62–0,73.
- f31: hông + ngực quay chính diện, thân thẳng, đầu ngửa; chân phải bước tới Z +50…+98, chân trái kiễng. Chùy trục (0,04; 0,55; −0,83),
  đuôi cán (22, 200, 92). Phải dời bả vai/vai lên-trước (+30–35 Z) thì tay mới với tới đuôi cán. IoU 0,59–0,66.
- f33: nằm sấp: chùy nằm đất trục +Z, đuôi cán Z≈140, tâm cán cao ~35; hông gốc ~(−12, 60, 12) chúi 50°, ngực gập 85°; chân trái duỗi
  ra sau (chân chỉ dài 67 cm nên hông không lùi xa được). IoU 0,62–0,74.
- Blocking nhanh 15 key còn lại (`work/cascadeur/keys/mk_rest.py`, base = P0 hoặc key khó gần nhất): IoU front/left 0,56–0,78.
  f49 sai nhiều nhất lúc đầu: ref đã ngồi khom dậy và **nhấc chùy ngang khỏi đất** (tâm cán ~70 cm), không còn nằm sấp. Video stepped
  `casc_blocking_v1` trên trang review (2026-10-21).
- Vòng sửa view left (v2, IoU TB 0,661 → 0,688): chân trái nằm sấp lơ lửng 26 cm (`cascadeur.md#base-chain`); chùy f8/f10/f31 cao
  35–70 cm, f52 lùi 30 cm, f58 dựng quá; f21 view left ref nhìn lưng nhưng xoay ngực −60° làm IoU tụt 0,56 → 0,44 → để người duyệt xem.
- Tay chìm trong cán, mép dưới chùy dựng đứng → `props_weapons.md#grip-big-shaft`, `#prop-measure`; suy góc hông từ vạt khố →
  `legs_feet.md#hip-height`.

## sdr-attack
SDR Attack (ném dao, thân trên, không ref) - blocking v1 (2026-10-20) → polish v5 chốt (2026-10-21). Bài học chung đã chuyển:
mô tả trước / clip không ref → `review_process.md#no-ref-clips`; dựng từ snapshot P0 → `blender_tools.md#live-posing`; FK từ rest →
`arms_hands.md#fk-arm-plane`; dao bay, bia, điểm thả → `props_weapons.md#thrown-prop`; mặt lưỡi về camera, tay ngắm song song đất →
`props_weapons.md#flat-prop-orient`, `#gun-aim`; cổ ngả sau, gối sau → `torso_head.md#head`, `legs_feet.md#knee-dir`; spacing ném/về,
tách timing, overlap resample, đuôi = Idle → `timing_spline.md`; quét cổ tay theo nét vẽ → `arms_hands.md#wrist-sweep-prop-dir`;
xuất + biến thể dao theo tay → `export.md`.
Riêng clip này:
- Đọc ở camera ingame: follow-through "vung về hông trái" chui ra sau thân ở góc right -> vung xuống trước thân; tay thả dao
  giơ cao che mặt -> duỗi tới, thả ngang cằm.
- SDR góp ý vòng v3 đều nằm ở pose Idle P0, vì Attack dùng lại P0 ở F1/F18.
- Nhịp recover (spline v1 → v2, góp ý "từ lúc phóng dao đến khi về Idle gấp quá"): 18F (recover 7F) quá gấp → 26F (0,87 s). Phần
  ném giữ nguyên, giãn phần sau: follow-through moving hold 2F, tay ngắm lại F16, tay ném về F21, lắng 5F.
- Recover 2 tay lệch pha (spline v4, góp ý "tay ném quá đà và giữ ở dưới lâu hơn, về Idle sau tay ngắm"): thêm key giữ (k13) — tay
  ngắm đã về mục tiêu, tay ném vẫn thả ở đùi; tay ném chỉ leo lên sau đó. Follow-through ném nên kết thúc thấp (cổ tay ~ngang đùi)
  và giữ 5–6F; tay ngắm luôn về trước (code aim cần nó sớm). Clip 28F (0,93 s). (User bỏ v4; polish v1 làm trên spline v3.)
- Polish v3 (tự đề xuất, user duyệt qua ảnh tĩnh): (1) silhouette — sau cú ném đừng để tay ngắm co trước bụng lâu (hai tay chồng
  lên thân = mất hình ở cỡ game), thêm key tay ngắm về mục tiêu sớm (F11); (2) lấy đà đọc từ góc camera (`torso_head.md#open-to-camera`);
  (3) điểm thả dao: nâng tay lên ngang trán lại che mắt hơn, đường tay dưới cằm mới lộ mắt.
- Polish v4 (góp ý "về quá nhanh trong 2 frame"): tay ngắm về mục tiêu dời F11 → F14 (`timing_spline.md#spacing`, `#split-timing`).
- Tay đối trọng lúc ném (polish v5, góp ý F6): tay ngắm phải **co lại** (cánh tay trên ra trước-xuống, khuỷu ~90°, nắm tay
  hướng lên) chứ không buông thẳng cả cánh tay xuống; delay overlap = 0 tới frame thả (`timing_spline.md#overlap`).
- Chốt polish v5 (2026-10-21): 26F, ném F6, dao cắm F12, Idle F20–F26; ~8 blocking + 4 spline + 5 polish vòng.
