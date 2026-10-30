# Quy trình làm việc & review (mọi loại anim)
Trang review, chu kỳ lắng nghe, round hand-off: SKILL.md "Team review page".

## reviewer-prefs
Sở thích của người duyệt (animator lead):
- Góp ý bằng ngôn ngữ nguyên lý (overlap, slow-in, follow-through) - áp dụng đúng nguyên lý, không chỉ chỉnh chỗ được khoanh.
- Thích chuyển động có trọng lượng và có "hồn": vật nặng trễ, vải bay, nhịp thở chậm.
- Muốn AI tự xem lại và đo ("bạn hãy tự view lại và đo...") - luôn kèm số đo trong câu trả lời.

## director
- **Animation Director (subagent `animation-director`, thêm 2026-10-30, user: tạo agent "định hướng và feedback anim trong quá
  trình sản xuất")**: gọi trước mỗi cổng duyệt và trong `/check_fb` trước khi render đầy đủ. Ngữ cảnh riêng, chỉ thấy kết quả
  (ảnh, số đo, brief) nên ít thiên vị bài của animator. Kết luận Duyệt / Cần sửa / Chặn; lỗi mức A phải sửa trước khi gửi;
  tối đa 2 vòng director rồi gửi người dùng. Lỗi director nhắc lại mà người dùng cũng bắt → ghi vào mục `#feedback` của loại anim.
- Nhật ký từng clip: `work/<dự án>/<clip>/director_log.md` (director tự thêm mỗi lần chấm).
- Các điểm gọi director (2026-10-30): mọi cổng duyệt anim, `/check_fb` (note Review Lab và ghi chú vẽ Studio, bước 3b), mỗi bước Rig
  2–5 trong `/rig` (mốc rig-joints / rig-skin / rig-test, log `work/rig_lab/director/<id>.md`). Ghi chú nhỏ đã đo rõ được bỏ qua, phải ghi lý do.

## naming-principles
- Mỗi feedback: gọi tên nguyên lý bị vi phạm (xem `principles.md`) và thêm ví dụ thật vào nguyên lý đó; đổi trạng thái
  [chưa] -> [đã thử] -> [đã kiểm chứng] khi được duyệt.
- Mỗi ghi chú feedback -> 1 dòng ở mục "Feedback" của file loại anim (câu gốc + nguyên tắc) và, nếu có đo đạc, 1 dòng ở mục "Lỗi".
- Ghi ngắn, có số đo; bỏ những gì đã sai/lỗi thời thay vì để chồng chéo.

## self-measure
- **Tự đo trước khi gửi review**, không đợi người duyệt chỉ ra: chuỗi đỉnh từng bộ phận, tỉ lệ thời lượng/tốc độ hai pha,
  tốc độ tối đa, trượt chân, tay trôi trên cán, giới hạn khớp, nối loop.
- **Mỗi lần sửa soát tác dụng phụ:** làm chậm pha này có thể làm nhanh pha khác; báo tốc độ tối đa trước/sau.

## eye-vs-iou
- "Không pose nào giống ref" / "Tệ quá" (Gaygor Attack v2, 2026-10-19): ước lượng hướng bằng mắt từ crop nhỏ sai 20-40°; dựng từng
  pose một với ảnh lớn 5 góc; không kết luận khớp từ overlay.
- **IoU silhouette không thấy thứ tự trước/sau và chi tiết** (người duyệt: "góc left so với ref chưa đúng", "sửa từng chi tiết từng
  phần", khi IoU view left đã 0,69): so ảnh CÓ SHADING REF | ANIM theo từng cấp (chân/hông → thân/đầu → prop → tay → bàn tay) bằng
  `work/cascadeur/partcrop.py` (cắt theo dải độ cao, thước cm) và `sbs_left.py`; tìm ra nắm đấm thiếu, đầu ngóc, chùy sau thân thay
  vì trước, chân lún/hở đất. Sửa đúng chi tiết có thể làm IoU giảm nhẹ - vẫn đúng hơn.
- Ảnh chồng 2 màu (`eye_diff.py`) cho biết HƯỚNG sai, `extent_cmp.py` cho biết sai bao nhiêu mét (xem `attack.md#qa-checklist`).
- Điểm phạt "chùy dưới đất" trong sil_score có thể kéo IoU xuống 0,29 dù bóng vẫn 0,66 - xem `detail` trước khi hoảng.
- P0 bị chê ở 2 góc nghiêng dù đầu/chân khớp: phải so **mép trước/sau silhouette theo từng độ cao** ở mọi góc (bảng Y → Z), không
  chỉ đo vài điểm. Lỗi tìm ra: đuôi chùy thấp 17 cm, khuỷu trái không đủ lùi, nắm đấm phải bị rút về (nhầm với gối), đầu thấp 6 cm.
- Ref nhiều vật tròn chồng nhau (nắm đấm, đầu gối): xác nhận bằng góc thứ 2/3 trước khi dùng số đo (đã nhầm gối phải thành nắm đấm).
- Góc nhìn cạnh dễ bị cánh tay P0 che khi chưa dựng tay.

## coarse-to-fine
- f13 v1 (Blender Attack, "Frame này chưa được... chia các bộ phận ra làm từng phần, phần chính làm trước, sau đó đi dần đến các
  bộ phận con", khoanh đầu + chân): dựng theo cấp, mỗi cấp đo xong mới sang cấp sau: (1) hông + chân (`legs13`: hạ hông, pole gối
  theo khung hông) → (2) thân/cổ/đầu (`torso13`: hướng + độ cao đầu đo bằng số) → (3) chùy (`mace13`) → (4) hai tay `solve_grip`
  → bàn tay nhìn cận. Đo cấp bằng `part_points` + `part_overlay` (điểm mesh của bộ phận chiếu lên ref), không bằng IoU cả người.
- **Cập nhật 2026-10-21 (Cascadeur):** người dùng: "Làm cách này lâu quá... lên blocking nhanh toàn thân, sửa chi tiết sau". Mặc
  định blocking = dựng nguyên một key trong một lượt (vẫn theo thứ tự chân → hông → thân → đầu → prop → tay), render 1 lần, chỉnh
  1–2 lượt (`cascadeur.md#fast-blocking`). Dựng từng cấp và **chờ duyệt mỗi cấp** chỉ khi người dùng yêu cầu sửa chi tiết.

## per-view-pass
- **Vòng sửa theo từng view** (casc_blocking_v1: "view lại và sửa từng view một. bắt đầu với view left"): đo đường viền trên/dưới
  theo từng cột Z (mỗi 20–25 cm) ở view đó, ref so với anim, rồi sửa đúng vùng lệch; IoU view left TB 0,661 → 0,688 (v2). Lỗi
  cụ thể: `attack.md#cascadeur-keys`.

## self-review-sheet
- "chưa được, tự view lại bằng mắt" (Blender Attack v7): bảng REF|ANIM 4 view mỗi key (`work/boss_gaygor/attack/v7rev/sheet.py`, crop theo
  người) lộ lỗi KHỐI LỚN mà IoU không thấy (`torso_head.md#square-body`).

## circled-notes
- 8 ghi chú chỉ khoanh tròn, không chữ (Blender Attack blocking v5: f8 f10 f13 f26 f30 f44 f53 f60): vẽ nét ghi chú lên frame webm
  (hộp bao từng nét) để biết khoanh gì. Khoanh vào frame HOLD = ref đã đổi pose -> thêm key ở đó. Khoanh chùy/tay = vị trí prop
  và điểm nắm sai -> `props_weapons.md#prop-measure`.
- Ghi chú 1 frame trong đoạn giữ dáng (f38 "Sai pose", v6) = cả đoạn sai: so ref của cả đoạn (f33–46 cùng dáng) và sửa mọi key
  trong đó, không chỉ frame bị khoanh.

## still-options
- **Bài học SDR Idle v16–v18 (bị bác, user: "quá tệ, quay lại bản v4")**: khi một hướng sửa thất bại 2 lần, dừng lại đưa 2–3
  phương án ảnh tĩnh cạnh nhau cho user chọn trước khi dựng cả clip; luôn giữ được bản đã duyệt để quay lại (tham số pose ghi
  trong p0_pose.py + so khớp pixel khi khôi phục). User chọn "50% của A" sau khi xem ảnh tĩnh v4 | A | B: đưa phương án ảnh tĩnh
  + cho user chọn tỉ lệ nhanh hơn nhiều so với sửa mò cả clip (chi tiết `idle.md#sdr-one-pose`).
- SDR polish v3 (tự đề xuất, user duyệt qua ảnh tĩnh): luôn thử bằng ảnh tĩnh trước/sau rồi mới dựng clip.
- **Một bộ phận hỏng ≥ 2 vòng thì mời người duyệt tự chỉnh trong Pose Lab 3D** (`#pose-lab-3d`). SDR06 tay trái Reload: sửa bằng
  solver mất khoảng 20 bản (b4→b23, lhand_b2), còn người duyệt tự chỉnh trong Pose Lab thì 4 vòng là được duyệt (lhand_b3→b6). Họ chỉ
  ra đúng pose họ muốn nhanh hơn mọi lời mô tả (2026-10-22).

## no-ref-clips
- Clip không ref: viết bản mô tả trước (work/shoot_die_repeat/sdr/attack_analysis.md, nguồn [concept]/[đối thủ]/[quyết định]/[thiết kế]) -> duyệt
  -> blocking cả clip.
- Đọc ở camera ingame, thiết kế theo silhouette của camera game, không theo giải phẫu/hành động thật (SDR Attack: follow-through
  chui ra sau thân ở góc right -> vung xuống trước thân).
- "concept như này mà" (SDR Idle v1): đặt concept cạnh render CÙNG góc camera ingame và gọi tên từng sai lệch trước khi chỉnh.
- SDR Attack chốt ở polish v5 (2026-10-21) sau ~8 blocking + 4 spline + 5 polish vòng; phần lớn góp ý nằm ở pose Idle/tấn đứng
  (F1) và nhịp recover — với clip không ref, chốt pose Idle + nhịp tổng bằng ảnh tĩnh và timing chart sớm sẽ đỡ nhiều vòng.
- Ref điện ảnh cho game (SDR map06 Reload): trước khi chép động tác ref điện ảnh, hỏi/đề xuất bản tối giản đọc được ở góc cam
  game; ít đổi tư thế = ít lỗi xuyên (chi tiết `shoot_reload.md#reload-minimal`).

## approve-export
- **Duyệt ("oki rồi" trên version mới nhất) = xuất** bằng `export_clip.py` (`export.md`).

## pose-lab-3d
- **Playblast Walk từ Pose Lab trên máy (2026-10-26):** `work/boss_gaygor/walk/pb_capture.js`, chép vào `work/pose_lab/fbx/out/` rồi nạp bằng
  thẻ script. Các bước: mở `/index.html` (trang riêng `pages/<clip>/` không tải được model trên máy); `openPose(Walk anim_v1)`; nạp key + đặt
  `ANIM`/`CT` giống doc `anims` trong db (vật lý, điểm tiếp đất); `__pbw(frames, true, name)` gửi ảnh tới `save_srv.py` (launch
  `pb-save`, cổng 8125; cổng 8124 có thể đang bị server cũ giữ).
  Bẫy: vật trợ giúp (đường root nét đứt, dấu khóa chân) được dựng lại sau mỗi `goto()`, nên phải ẩn lại sau mỗi frame. Model là
  `Group` tên "Scene"; lưới là `GridHelper` (bản three này không có cờ `isGridHelper`). Chụp thử 1 frame trước để kiểm khung.
- **Encode khung JPEG từ trang thành WebM (2026-10-26, user báo "Không tải được video WebM" trên b14):** JPEG đi vào là dải màu
  full (yuvj420p), ffmpeg ghi `color_range=pc` / `bt470bg`. Chrome phát được nhưng tua thì báo `PIPELINE_ERROR_DECODE`. Luôn ép
  dải chuẩn: `-vf "scale=out_range=tv:out_color_matrix=bt709,format=yuv420p" -colorspace bt709 -color_primaries bt709
  -color_trc bt709 -color_range tv`, rồi `ffprobe` phải thấy `color_range=tv`. Thử trong trình duyệt bằng blob + tua từng frame
  trước khi đăng.
Pose Lab 3D (source work/pose_lab/) = the reviewer edits the pose in 3D per frame; dùng lại 2026-10-22 cho SDR06
Reload lhand_b2.
- ONE page (artifact + own db) PER ANIMATION, like the playblast review pages (user: map2 and map06 must not share a
  page). Master index.html holds every POSES line (one per version, newest first, with date + note);
  `python work/pose_lab/split_pages.py` writes pages/<key>/index.html. SDR06 Reload:
  https://claude.ai/artifact/UKYdqvs5TXEfXJsg9GSJ3y, SDR Idle (map2): https://claude.ai/artifact/XvHD2HJ4CA74skzx8mmfdZ.
- Translate (W): hip, ankles (leg IK), wrists (arm IK: shoulder+elbow bend, hand keeps its world orientation; saved as
  rotations) and the gun slingshot_0 (world move/turn; "Tay phải bám súng" keeps the right grip by arm IK). The gun is
  saved whenever its world pose changed (also when it only rode the chest), with bones.slingshot_0.dp. SDR06 Blender:
  pose_lab_apply.py writes it as CTRL_knife keys on that frame only (WYSIWYG, gun + body are baked per frame) in a
  per-version CTRL action copy (<ver>_C), manual.json "CTRL:CTRL_knife"; lhand.build re-keys it. Assign the new CTRL
  action BEFORE frame_set, or the next update re-evaluates it and wipes the gun move (test: off 8.37 cm -> 0.00).
- Edit on F1 of a clip where F1 = P0 (end returns to it): lhand.build applies it as a LAYER (p0_layer: base + w *
  (new - base@F1), w = smoothstep 1 at F1 -> 0 at the first hand key, 0 through the last, back to 1 at P0_BACK=34).
  Layering local rotations alone pulls the hands off the gun (b3 first try: right grip slid 3 cm, left hand 34 cm off).
  Then p0_grips: the F1 grip (wrist in gun space) is held on EVERY frame - right hand always, left hand outside its own
  keys where the base has it on the gun - by two-bone arm IK (ik_arm), keyed per frame. Check: grip slip vs F1 = 0.
- Joint display (user 2026-10-22 "điểm khớp chồng lên nhau rối mắt"): stick figure (small dot + stick to the parent
  joint), 50 % opacity by default, fading with camera distance (near clearest), 100 % near the mouse or when selected,
  constant screen size (dot 3.5 px, stick 0.8 px radius; user found 0.011 m dots too big). Never hide the other joints on select. Picking is in screen space (nearest dot within 14 px,
  nearer camera wins). Marquee drag on empty space, Shift = add/remove; gizmo on the last picked joint, in rotate mode
  the others turn by the same world rotation; Copy key / Reset work on the whole selection.
- Page titles are the user's (SDRmap6 Reload / SDRmap2 Idle Pose Lab): kept in split_pages.py.
- Pasted keys (user copies one key's arm pose onto another in Pose Lab): the drum (slingshot_1) is not in the copy, so lhand.build copies the source key's drum channels when the arm channels match (F21=F16, 2026-10-22). Otherwise the hand slides off the drum.
- New version: export models/<clip>_<version>.json (keep old models), add a POSES line on top, split, publish that
  page with `files` {"models/<new>.json": ...} (files left out stay). Left column = version list with round status.
- **Animate on the page (POSES `mode: "keys"`, 2026-10-23, user: "build nó thành 1 công cụ hoàn chỉnh"; first: Gaygor
  Walk anim_v1)**. Keys live in db `keys` (doc `<clip>-<version>-F<f>` = {clip, version, frame, pose{bone: [qx,qy,qz,qw,
  px,py,pz] three.js LOCAL}, at, by}), settings in `anims/<clip>-<version>` {interp spline|step, lock, contacts{L,R:
  "15-45,50"}}. No db keys yet -> seeded from the glb at POSES `keys` (or `seedFrom` version); the first save writes all.
  - Stepped (Bậc thang) holds the WHOLE key pose: foot lock and prop blend are off in step mode (user: "Phần chân đang
    chưa để Step by Step" - the lock slid the planted feet between stepped keys).
  - In-betweens: per channel cubic Hermite, Blender-like auto-clamped tangents (flat at a peak) + Fritsch-Carlson limit
    (no overshoot); quaternions sign-aligned, normalised. Stepped toggle for blocking. `loop: true` = last frame == F1
    (key on the last frame is stored on F1, curves wrap).
  - "Bám sàn": contact lanes (blue L / purple R under the timeline, paint by drag, "Dò chạm đất" = feet within 3 cm of
    the lowest at two neighbour keys) -> ankle on straight lines through its spline position at the span ends + every
    key inside, two-bone IK. Test: planted ankle 0.00 cm drift (0.09 cm without lock); keyed frames unchanged.
  - Auto key (default on): an ended edit (gizmo drag, Channel Box, paste, reset joint) keys the whole pose on that frame;
    S = key, Delete = remove (undo restores keys), Shift/middle-drag a diamond = move key.
  - FBX export samples the evaluated keys: Walk test 57F re-imported in Blender = page positions 0.000 cm
    (`work/pose_lab/fbx/cmp_page_track.py`).
  - Ref panel: sprite sheet per view (`.venv/Scripts/python.exe work/pose_lab/make_ref_sprites.py <frames> <masks> <out>`,
    crop = union silhouette +10 %, 360 px cells), POSES `ref.cams` maps page camera -> ref view. Gaygor: page Right
    camera = ref "left" view (refs.json naming), Front = front, Top = top; G toggles, click = size.
  - Camera presets scale with the highest joint (camFit = top/1.75 m); Gaygor ~1.26.
  - **Import a hand-made FBX into Pose Lab, no Blender** (2026-10-23, Gaygor Attack 50% blocking): `work/boss_gaygor/gaygor_attack_50_blocking/make_model.py <in.fbx> <out.json>`
    reads curves with key times (`fbxanim.py`; KeyAttrFlags 2 = constant = stepped). **Apply each bone's RotationOrder**
    (enum 0 XYZ,1 XZY,2 YZX,3 YXZ,4 ZXY,5 ZYX; "XYZ" = X first = Rz@Ry@Rx; Pre/PostRotation always XYZ): AdvancedSkeleton
    sets ZYX/ZXY/XZY on 20 bones (neck, head, arms, legs); b50_v1 ignored it and the user rejected it ("nhiều pose lỗi,
    sai so với file blocking"). A world-match check against my own reader cannot catch this; check with something
    independent of the reader: hand-in-prop space over the keys (Wrist_L vs Weapon: 77 cm median jumps with XYZ, smooth
    slide along the haft with the file orders). Takes mesh/skin/nodes from the
    Gaygor Walk P0 model (same 59 bones, same parents, cm under Armature 0.01 + Rx90), local = PreRotation * Lcl
    Rotation + Lcl Translation, root bone gets Rx(-90); samples every frame at t = f/30 (1-based). Check: bone worlds
    vs FBX 0.003 mm. POSES: `mode: "keys", interp: "step", keys: [key frames + 1]` -> page seeds the db keys from it.
    Publish with files models/<x>.json + fbxexport.js (the page 404s on Xuất FBX without it).
  - **Fixing an imported blocking without the page** (b50_v3, `work/boss_gaygor/gaygor_attack_50_blocking/fix_v3.py`): edit FBX-space
    locals per key, `make_model.write(models, local_fn, nf, out)`. Prop under the floor -> turn the prop about the
    hands' midpoint (bisection on the lowest mesh point), then two-bone IK (hinge = Elbow/Knee local Z in this rig)
    so each wrist keeps its prop-space transform. Measure contacts on the TOES, not the ankle: the file already pinned
    the left toe F35-48 (ankle pivoting about it) and the right foot was still only on F31-32; an ankle lock "fix"
    bent the knee 32-60 deg. Check units in prop space: glTF world includes Armature 0.01, so prop-space offsets are
    already cm (a x100 made 0.09 cm read as 9 cm). `verify.py old new` = skinned lowest point, grip drift, ankle move.
  - `clip_registry.py build` runs the split scripts with `-X utf8` (`-I` ignores PYTHONIOENCODING; cp1252 crashed on
    Vietnamese prints).
  - Publishing ~4 MB of images in one call failed (ECONNRESET): publish one image per call.
- **Fit to ref on the page, no Blender (2026-10-23, user: "Tôi cần bỏ hẳn blender")** — button "Khớp ref" (keys mode):
  - Cameras: POSES `ref.cal` per view {dir, up, u0, v0} in ref pixels, 305.3 px/m, ortho; `calibrateRef()` (console)
    finds u0 (+ v0 / up for top) by IoU of P0 vs ref F1. Gaygor Walk: front u0 1088, back 833, left (camera at -X,
    looks +X) 1071.5, right 851, top up -Z u0 1087.5 v0 647, side v0 = floor 934.5; IoU 0.78-0.84. Checks: front+back
    and left+right u0 sum to ~1920. Sprite `crop` per view comes from make_ref_sprites.py (refs.json).
  - Stages: legs (hip move/turn, feet IK, knee twist, heel roll about the toe tip) on the low region of 4 side views,
    then body (spine/chest/head bends, mace offset, right hand) on the high region + top. Line search per parameter.
  - IoU alone lifted the WRONG foot and put the planted foot in front (feet overlap in side views). Fixes, keep all:
    each foot's lowest row in front/back vs ref; floor band 0-6 cm IoU in the side views (heel/toe contact);
    POSES `fitFeet` toe targets per key (world cm). Gaygor Walk measured: toe joint = front edge of that foot's floor
    band + 2 cm; planted feet slide back 2.1 cm/F (L 58 at F15 -> -15 at F50, R 58 at F42 -> -28 at F29).
    Measure in WORLD cm (u - u0) — a 9 cm offset slip (column 960 vs u0) put every foot too far forward.
  - Coupled moves need a joint parameter: dropping a lifted heel = ankle down + foot pitch together (heel roll),
    one-at-a-time search never finds it. Regularise hip x/y (.3/m), hip yaw, foot yaw, foot side (1.5/m) and the
    right hand: unconstrained, F29 twisted the whole body to the camera (hip +20 cm, foot 28 deg).
  - Prop lock (POSES `follow` {prop: Weapon, to: Scapula_L, hand: L}): Weapon is a child of `root`, so the page keeps
    it on the shoulder and the left hand on its grip, in edits and on every spline frame (relations blended between keys).
  - "So cạnh nhau" in the ref panel = model through the calibrated ref camera next to the ref (grey, like the playblast).
  - Browser pane hidden -> timers throttle: fits run 25 s/key instead of 3 s; poll a window.JOB object, short calls.
  - Gaygor Walk block_b1 (8 keys F1..F50, stepped) written to db keys via ArtifactData batch (work/boss_gaygor/walk/block_b1/).
    Known: left foot keeps P0's raised heel on some keys (F22, F42), body ~10-20 deg more open to the camera than the ref
    (from the approved P0); F1 legs were re-fitted (right foot 10 cm back to the ref).
  - block_b2 (user: "chân trái ... đang lỗi"): every key's LEFT foot was rolled 18-24 deg about its long axis (sole
    tilted out), inherited from the P0 Ankle_L edit and carried by the relative fits. Measure foot roll against the
    OTHER foot mirrored: this rig is a clean mirror, L_world = mirror_YZ(R_world) * C, C = 180 deg about X (same for
    hip/knee/toes, 0.1 deg). Fix = turn about the ankle->toe-tip axis until roll 0 (ankle and tip do not move).
    Also F22 heel down to ankle 20 cm, F42 heel set by the floor band of the near-side view (ref "right" = character's
    left side: use the view where that foot is NEAR the camera). Free 3D grid searches on the foot (pitch + tip move)
    gave nonsense (F50 toes 51 cm up) - constrain to one measured quantity at a time.
  - block_b3 (user screenshots, no words: right foot sunk at F22): check feet with the MESH, not joints - lowest skinned
    vertex of each foot (main weight on Ankle/Toes/ToesEnd, boneTransform). Found R -4 cm at F22, planted L +2 cm at
    F36/F42, R -1 cm on 4 keys. Button "Chân lên sàn": planted foot (lanes) lowest vertex = 0, lifted foot >= 0, by leg
    IK straight up. Spline also clamps every frame to >= 0 (hip/knee spline arcs dipped the swinging R foot 14 cm at F33).
- Export: `blender -b <blend> --python work/blender/export_pose_glb.py -- work/pose_lab/models/<x>.json frames=1-N`.
  Only the baked action may go out (`export_animation_mode=ACTIVE_ACTIONS`, other actions removed): with all actions
  in the file every channel had 2 samples and the gun lay on the floor.
- Blender's glTF clip starts at t = F1/fps, not 0: the page offsets by the first key time. Check after every export:
  `toBl(wp(B[n]))` on the page == Blender world head at the same frame (F14 matched to 0.1 mm).
- Back to Blender: adjust docs → `work/shoot_die_repeat/sdr06/pose_lab_apply.py` (apply_adjust on its frame, CONSTANT key, local
  channels into cache/lhand/manual.json); `lhand.build()` re-keys manual.json over the solve. Bones driven by
  constraints (SDR06 gun slingshot_0) cannot be edited this way.
- Controls (user 2026-10-22, "làm giống maya", "làm thêm channelbox"): Q select / W move / E rotate / R = scale (locked,
  message only); Alt+LMB/MMB/RMB tumble/track/dolly, wheel zooms; F frame selected, A frame all; up/down pickwalk;
  `, .` prev/next key. Selecting a joint hides the other markers ("làm rối mắt"). Channel Box: Rotate XYZ = degrees on
  the joint's local axes relative to the original pose of the frame; Translate XYZ (hip, feet) = cm Blender axes;
  drag the channel name = virtual slider, type + Enter.
- Copy key (user 2026-10-22 "Thêm tính năng copykey"): Ctrl+C = local pose of the selected joint (Ctrl+Shift+C + its
  child joints, nothing selected = every joint), Ctrl+V = paste on this frame, Ctrl+Shift+V = paste up to the frame
  before the next key (hold). "Lưu điều chỉnh" saves every frame with edits, one adjust doc per frame. Saved, not yet
  applied adjusts show on the model (ghost = original), so a later edit is a delta on top - same order Blender applies
  them (frame, createdAt).
- Saving needs the claude.ai artifact (db). On the local preview (localhost:8771) the button is "Tải file điều chỉnh"
  and downloads the same adjust docs as .json (user 2026-10-22 edited on localhost and could not save). Put such
  files in work/shoot_die_repeat/sdr06/pose_lab_adjusts/ and run pose_lab_apply.py on them. Always send the user the claude.ai link,
  never the localhost tab, for edits that must be kept.
- Twisted inbetweens on IK-held frames (SDR06 Reload lhand_b4 → b5, 2026-10-22, user: "áp dụng Euler Filter cho vai và cánh tay"): when a hand is pinned by IK on a prop while the base arm swings toward another pose, start the IK from the held pose's arm (F1), not the base arm — otherwise the bend plane is the swinging one (elbow twist −70°, wrist bent 120–170°). Then run `quat_filter` (sign continuity = Euler Filter for quaternion bones). Check with per-frame local twist/swing about the bone Y axis (scratchpad inspect_twist.py idea): elbow twist should stay near its rest value, per-frame change ≤ ~10°.
- Pose Lab edits on non-key frames (lhand_b5 round: drum on F17/F18/F22) become new holds; lhand.build now applies manual.json in frame order so an earlier hold never overwrites a later edit. Pose Lab "local.q" is three.js order [x, y, z, w]; "bones.dq" is [w, x, y, z] — compare accordingly in checks.

## p0-lock
**Chốt P0 ở góc camera game trước khi blocking clip nào** (rút ra 2026-10-22 từ lịch sử git SDR map06). P0 đổi 6 lần SAU khi
đã block Shoot/Reload: v3 súng thẳng ở góc top, v4 người xoay 30° ra cam, v5 vai cân + đầu 25° ra cam, v6 mở người như demo,
b7 vai trái lõm, v8 ngực 80→54°. Mỗi lần đổi P0 phải dựng lại cả 2 clip (Shoot b3→b9, Reload b5→b14). Đó là 6 vòng chỉ để
sửa staging. Nguyên lý: Staging.
- Duyệt P0 bằng 1 ảnh tĩnh ở camera ingame + góc top + góc phía tay cầm prop, kiểm cùng lúc: hướng ngực/đầu so với camera
  (`torso_head.md#open-to-camera`), prop ngắm thẳng ở góc top, vai cân, không vai lõm (`arms_hands.md#shoulder-compression`),
  hướng khuỷu/gối (`arms_hands.md#pole-spec`). Có demo hoặc ảnh mẫu của team thì so với nó ngay từ đầu.
- Chưa có chữ "duyệt P0" thì chưa block. Sau đó vẫn phải đổi P0 thì đổi bằng layer (P0 cộng thêm delta, xem `#pose-lab-3d`),
  đừng dựng lại từng key.

## home-app
**Home là cửa vào (2026-10-23, user: "người dùng sẽ bắt đầu làm việc từ đây").** Home chạy trên máy (`tools/home/start.bat`
hoặc preview `home`, http://127.0.0.1:8780), một người dùng, dữ liệu nằm trên máy đó; không phải artifact.
- Dự án = game (SDR gồm map2 + map06). Khóa `projects` trong `work/clips.json` gom nhân vật theo dự án; clip thuộc dự án qua nhân vật.
- Home đọc bản mới nhất + ảnh từ CLIPS (`work/review_page/index.html`) và POSES (`work/pose_lab/index.html`), hoạt động từ git log.
  Muốn Home hiện đúng thì giữ sổ đúng: đổi giai đoạn bằng `clip_registry.py stage`, ghi `note` có chữ "chờ" khi đợi góp ý
  (Home đoán trạng thái: export = xong, "tạm dừng" = tạm dừng, "chờ" = chờ góp ý; user có thể chọn tay trong "Sửa trạng thái" → khóa `status`).
- Trạng thái: working / waiting / done / **paused** ("Tạm dừng", thêm 2026-10-26 cho clip bị thay thế hoặc gác lại, vd Attack cũ → Attack 50;
  không vào "Tiếp tục làm"). Server đọc cổng từ `HOME_PORT`, rồi `PORT` (preview tự đổi cổng khi 8780 đang có Home của user chạy).
- Đổi tên (2026-10-26): anim → nút "Sửa / đổi tên", ghi khóa `title` của clip (chỉ tên hiện trên Home; id, thư mục, trang Lab
  giữ nguyên, để trống = tên gốc `review.name`); dự án → nút "Sửa dự án" (tên + mô tả, id/URL `#/p/<id>` giữ nguyên).
  Tên nhân vật chưa đổi được trên Home (dùng ở sổ, Rig Lab, file).
- "+ Animation mới" trên Home đã đăng ký clip (giống `clip_registry.py new`) và viết `work/<dự án>/<id>/brief.md`; khi user gõ
  `/new_clip <id>` thì đọc brief đó, đừng hỏi lại những gì đã có, rồi làm tiếp từ bước 3 (rig) hoặc 5 (phân tích).

## Playblast Studio ghi chậm khi tab chạy nền (2026-10-29, SDR01 Shoot pb1)
`anim playblast` trên tab Studio đang ẩn ghi theo thời gian thực (~1 s mỗi frame anim): 30 frame ra video 30,5 s / 915 frame.
Kiểm sau mỗi playblast: `ffprobe -count_frames` phải = số frame anim. Server Home (`_retime_playblast` trong `tools/home/server.py`)
tự lấy frame giữa mỗi đoạn khi video có > 1,5× số frame (cần khởi động lại server để có hiệu lực).
