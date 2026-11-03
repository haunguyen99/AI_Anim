# Xuất FBX (mọi loại anim)
Quy trình chuẩn: SKILL.md bước 7 (`legacy/blender/export_clip.py`). Duyệt ("oki rồi" trên version mới nhất) = xuất.

## export-clip
- Xuất SDR (2026-10-20): `legacy/blender/export_clip.py` chạy headless trên sdr_attack.blend / sdr_p0.blend → work/shoot_die_repeat/sdr/export/
  SDR_MC_Attack.fbx (26F) + SDR_MC_Idle.fbx (1 pose, 2F) + SDR_MC_Attack_events.json. Đọc lại lệch ≤ 0,02 cm. Dao bay được
  nướng vào xương slingshot_0 (con của Wrist_R).
- Exporter đặt tên take theo **tên scene** → export_clip.py giờ đặt sc.name = take trước khi xuất (trước đó take ra "Scene").
- Importer Blender lệch 1 frame (F1 → F2) là bình thường.

- **Xuất không Blender, giữ nguyên file của team** (Gaygor Attack 50 Blocking, 2026-10-23,
  `work/boss_gaygor/gaygor_attack_50_blocking/export_fbx.py`): đọc FBX nhị phân có giữ kiểu từng property, chỉ thay đường cong
  Lcl T/R/S của mọi xương (68 key linear, Euler theo đúng RotationOrder của từng xương sau khi bỏ PreRotation), đổi tên
  AnimationStack + Takes, ghi lại FBX 7.4 bằng `work/pose_lab/fbx/fbxbin.py` (thêm kiểu Y/F/C byte/S raw/mảng b, nén zlib).
  Kiểm: chạy `--roundtrip` (ghi lại file gốc không đổi → cây giống hệt), tự kiểm Euler 6 thứ tự, đọc lại FBX xuất ra
  so polish từng xương từng frame (0,00001 cm), xem bước Euler lớn nhất/frame để chắc không có lật 360°.
  `--anim-only` (user cần, 2026-10-23): bỏ Geometry/Model Mesh/Deformer/Pose/Material/Texture/Video + liên kết tới chúng,
  đếm lại Definitions (giống mẫu work/shoot_die_repeat/sdr/export/anim_only) → export/anim_only/; kiểm: 59 xương, 0 liên kết hỏng, lệch 0,00001 cm.

## anim-only
- Xuất "chỉ joint + anim" (dev đã có model): `legacy/blender/export_skeleton_only.py` chạy trên file *_baked.blend
  (object_types={"ARMATURE"}, take = tên scene). SDR: work/shoot_die_repeat/sdr/export/anim_only/*.fbx, 23 xương, khớp bản có mesh 0,0006 cm.
  Mặc định hỏi/đoán: team Unity thường chỉ cần anim-only khi model đã import từ trước.

## variants
- Biến thể prop cho dev (SDR 2026-10-21, "bản dao chỉ đi theo tay"): cùng clip, prop không bao giờ rời tay
  (`sdr_attack.py ... polish inhand`: influence world-switch = 0 mọi key, bỏ bia) → SDR_MC_Attack_KnifeInHand.fbx. Kiểm trên
  FBX: khoảng cách xương dao–cổ tay không đổi (0,153 m mọi frame). Nên xuất cả 2 bản (dao bay demo / dao theo tay) khi có prop ném.

## loop-and-hold
- Clip loop (SDR06 Shoot 12F): xuất F1–F(N+1) với F(N+1) = F1 để Unity loop time khớp (SDR06_MC_Shoot.fbx F1–F13).
- Idle "chỉ là một pose" (SDR06 2026-10-22, 10F): lấy pose F1 của clip đã duyệt dùng chung P0 (Shoot = Reload F1) để chuyển clip không giật; key F1 và F10 giống hệt, CONSTANT (`work/shoot_die_repeat/sdr06/make_idle.py` chạy trên *_baked.blend), xuất bản có mesh + anim_only, đọc lại lệch 0,001 cm.
- Xuất bản stepped theo yêu cầu (SDR06 Reload lhand_b6, 2026-10-22): vẫn xuất được, nhưng đo bước nhảy cổ tay mỗi frame trước khi xuất và báo người dùng (ở đây tay trái nhảy tới 35 cm/F) — Unity sẽ chạy đúng y như vậy.

## reparent-prop
- **Hỏi lúc intake prop treo vào joint nào** (dev cần gì). SDR06 dựng cả clip với súng là con của Chest_M, tới lúc xuất user
  mới yêu cầu chuyển sang Wrist_R, nên phải bake lại cả 3 clip và kiểm lại (2026-10-22).
- Đổi cha của joint prop sau khi bake (SDR06 2026-10-22, "chuyển nó sang joint cổ tay phải": slingshot_0 Chest_M → Wrist_R):
  `legacy/blender/reparent_prop.py -- <take> <prop> <parent> <fbx> <anim_only_fbx> <out.blend>` chạy trên *_baked.blend:
  ghi world matrix prop mọi frame → edit-mode đổi parent (rest giữ) → key lại prop mọi frame; con của prop (trống) giữ local.
  Kiểm: world mọi joint lệch < 1e-6, FBX đọc lại lệch 0,0008 cm, parent trong FBX = Wrist_R.

## base
- File base "chỉ joint + mesh" (SDR06 2026-10-22): `legacy/blender/export_base.py -- <out.fbx>` trên baked blend có hierarchy cuối
  (*_wristR.blend): bỏ action, đưa pose về rest (bind), FBX bake_anim=False. Kiểm khi đọc lại: đủ xương, parent prop đúng, 0 action.

## FBX straight from Pose Lab (2026-10-23, Gaygor Walk; user: "làm hoàn toàn trên Pose Lab")
- Page button "Xuất FBX" writes an animation-only binary FBX 7.4 (Armature null + 59 limb nodes, Lcl T/R(XYZ Euler)/S curves, 30 fps, keys at frame*1539538600 ticks, no meshes) = same thing as `legacy/blender/export_skeleton_only.py`. Code: `work/pose_lab/fbx/fbxexport.js` (JS, used by the page) = `fbxbin.py` + `fbxwrite.py` (Python reference); `cmp_blender.py` imports two FBX in Blender and compares every bone per frame.
- Conversion rule (found by calibrating on 60 bones): FBX bone world = [unit-scale rotation of the glTF world | 100 x glTF world position], bone-axis correction is identity, FBX local = inverse(parent world) x world. Checked: Walk P0 and Idle_Front 60F vs Blender's own FBX -> 0.00 cm position, <= 0.1 deg (rotation error only from scale drift in the old baked Idle_Front hand bones).
- Blender cannot import ASCII FBX: write binary (array encoding 0 = uncompressed is valid; sentinel/footer as encode_bin.py).
- Artifact `downloads` capability does not allow `.fbx`: the page saves `<take>_FBX.zip` (store-only zip written in JS) -> unzip.
- Test loop without Node: tiny python http.server with a POST /save endpoint + Claude browser pane running the JS, compare the saved file in Blender.
- Keys mode (2026-10-23): the page keys/splines/foot-locks the clip itself and the FBX samples that (0.000 cm vs page) -> review_process.md#pose-lab-3d. Walk keys f8..f50 still to block.

## FBX from a team source of another length (2026-10-24, Gaygor Hit 32F from Bloking50.fbx 68F, `work/boss_gaygor/gaygor_hit/export_fbx.py`)
- Reuse `work/boss_gaygor/gaygor_attack_50_blocking/export_fbx.py` (typed reader, fbxbin writer patch, euler_from, strip_to_anim_only);
  the per-clip script only swaps the pose source and the length.
- Length: set GlobalSettings TimeSpanStop, AnimationStack LocalStop/ReferenceStop and Takes LocalTime/ReferenceTime to
  (NF-1)*DT (the source uses 67 for 68F). 5 values in all.
- The source also has non-TRS curves on every bone (Visibility, fat, fatFront, fatWidth, lockInfluenceWeights, filmboxTypeID)
  with the old 68 keys: rewrite them to the clip's key times holding their first value (assert they were constant), else the
  take runs past the clip.
- Verify: re-read with fbxanim.local(m, SECONDS) (f/30, not the frame number), compare every bone/frame to the pose, check
  key count, last key, take name and span; for a clip that ends on Idle compare the last frame to Idle F1 (here 0 cm/0 deg).
- Writing Python with a "\x00" literal through a heredoc + str.replace can drop a real NUL byte into the source (SyntaxError,
  "Binary file matches"): patch such lines with bytes([92]) + b"x00" or a script file.

## FBX from the team's anim-only file, rig with scaled bones (2026-10-29, SDR03 Shoot p1 12F, `work/shoot_die_repeat/sdr03/export_fbx.py`)
- Template = the team's own clip `Assets/_Game/Animations/Map03/MC_char_map3_shoot.fbx` (38 LimbNodes all with curves, no mesh:
  the team ships anim-only FBX for map3); same curve swap as Gaygor Hit. **Keep each bone's scale** (`slingshot_*` are 0.01):
  S = column norms of the local 3x3, rotation = pre^T (L/S) post. Forcing S = 1 (Gaygor template) would blow the crossbow up 100x.
- Pose source = rigpose local matrices (`spline/<ver>/F##.json`) = fbxanim.local of the same rig, so no axis conversion.
- Verify: fbxanim.local per bone/frame (0.00000 cm), rigpose.frame_of world (0.0000 cm), take name, 12 keys F0..F11; events JSON beside it.

## FBX tự ghi (fbxbin) phải giữ mã chân file của khuôn (2026-10-29)
- Lỗi: Unity "ImportFBX Errors: Couldn't read file …SDR03_MC_Shoot/Reload.fbx" (kéo theo "Copied Avatar Rig Configuration mis-match"),
  Maya "File is corrupted". Bộ đọc của ta vẫn đọc lại 0,00000 cm nên self-check cũ không bắt được.
- Nguyên nhân: export giữ FileId / CreationTime của file khuôn team nhưng `fbxbin` ghi mã chân file (footer, 16 byte sau sentinel
  gốc) cố định kiểu Blender; FBX SDK tính mã chân từ FileId/CreationTime, không khớp → coi là hỏng. Phiên bản 7400/7700 không phải
  nguyên nhân (đã thử cả hai). SDR06 không dính vì đi đường khác; Gaygor Attack/Hit (khuôn Bloking50.fbx) cũng dính, đã vá.
- Luật: `fbxbin.serialize(top, ver, fbxbin.foot_id_of(SRC))` (ghi đúng phiên bản khuôn, `fbxbin` đã hỗ trợ 7500+ bản ghi 64-bit).
  File đã xuất mà hỏng: vá 16 byte mã chân bằng `foot_id_of(khuôn)`, không cần xuất lại.
- **Kiểm bằng FBX SDK trước khi giao**: `mayapy` + `FBXImport` (cmds.loadPlugin("fbxmaya")) cho mọi FBX tự ghi; không tin chỉ bộ đọc
  của ta. Script kiểm đừng đặt tên `imp.py` (trùng module `imp`, mayapy crash).

## Anim cho Unity Humanoid: không dời xương người, .meta phải tạo khi FBX đọc được (SDR03, 2026-10-29)
- Rig MC map3 nhập dạng **Humanoid** (animationType 3, avatar copy từ rig). Dời vị trí (translation) mọi xương người trừ hông bị
  bỏ: Shoot p3 dời Scapula_R 7,75 cm (giật lùi) → Unity cảnh báo "'Scapula_R' has translation animation that will be discarded",
  vai đứng yên, tay lệch nỏ. Xương phụ (slingshot_*, bím tóc) dời được. Luật: giật vai/nhún vai = **xoay** Scapula (Humanoid chỉ
  cho khoảng −15…30°), không dời; trước khi xuất, đo mọi xương người trừ Root_M: translation phải = rest (`shoot_humanoid.py` có mẫu:
  dời → xoay bả vai ≤12° + `ik_min` tay giữ cổ tay world, F đầu/cuối giữ nguyên từng số để nối clip; đừng dùng `rig.ik_arm` cho việc
  này: chọn chiều bản lề khác nhau giữa các frame → tay lật 180°).
- `.meta` Unity tạo ra lúc FBX còn hỏng giữ thiết lập kiểu cũ: `useFileScale: 0`, `fileIdsGeneration: 1`, materialImportMode 1…
  → anim chạy sai dù FBX đã sửa. Sau khi sửa FBX: so `.meta` với clip chạy đúng (Idle / file team), dựng lại từ `.meta` đúng, giữ guid +
  internalID + tên clip, chỉ đổi lastFrame. Kiểm Unity bằng `%LOCALAPPDATA%\Unity\Editor\Editor.log` (dòng SDR…, cảnh báo import).

## Rig zombie từ model tĩnh mới, chỉ FBX skin bằng script (2026-11-02, zom_v2 map4/map5, `work/shoot_die_repeat/zom_v2/rig_v2.py`)
- Lấy rig team cùng loại (Animations/Map0X/En_Zom1_map*.fbx, 27 xương AdvancedSkeleton, Humanoid) làm mẫu: giữ tên + PreRotation/Lcl Rotation,
  chỉ đổi Lcl Translation (+ AnimationCurveNode d|X/Y/Z tĩnh), bind pose, cluster Transform/TransformLink; đổi tên Model/Geometry theo mesh mới;
  thêm cluster bằng nhân bản (đếm Definitions Deformer). Model mới UnitScale 100 → ×100 sang cm.
- Thân bộ xương low-poly = mảnh rời → đặt khớp ở chỗ nối mảnh (đùi/ống chân/cánh tay/cẳng tay), skin Body cứng theo mảnh; hàm dưới → Head_M.
  Bàn chân có thể nằm trong ủng QA (lấy mọi điểm thấp bên đó).
- Quần áo: 1/d^6 tới đoạn xương + mượt + đối xứng gương; áo giữa thân không theo cẳng tay/chân, vai là dốc mượt theo |x| (bậc → giãn ×16);
  mảnh nhỏ (<40 đỉnh, <20 cm) cứng theo xương trội, mảnh vắt qua đường giữa không lấy xương bên nào (khóa thắt lưng); đũng bớt Hip về Root trong ±8 cm.
- Kiểm: `zom2_map3/skin_check.py` (pose cực) + `zom_v2/anim_test.py` (ảnh anim Share) + `zom_v2/stretch_scan.py` (MINL=2, 18 anim).
- Thân liền một khối (zom2 đầu to): không có mảnh rời → khớp chân/khuỷu = cụm "núm" đỉnh dọc trục (thân xương low-poly không có đỉnh giữa,
  cắt cụm ở khe > 4 cm); Neck/Head đặt theo ĐÁY HÀM như rig cũ (Neck = hàm − 5,3, Head = hàm + 6,7), không theo đỉnh sọ (sọ to đẩy Head lên quá cao);
  skin thân theo khoảng cách 1/d^10 mượt 2 lượt, sọ + hàm cứng Head_M. Mẫu rig cũ có mesh thừa (súng VK) → bỏ, và bỏ khỏi skeleton của .meta.
- Mũ vắt qua hai bên KHÔNG phải "áo giữa thân" (lỗi 2026-11-02: luật vai thêm 0,28–0,36 vai vào vành mũ zom1, đã đẩy rồi mới phát hiện).
- `.meta`: `make_meta.py` từ meta rig cũ cùng map; Unity đang mở sẽ nhập và tự ghi lại meta (LF, thêm Scapula→Shoulder vào Humanoid) — bản đó dùng được.
- Thân liền khối (Director zom2 2026-11-02, Duyệt vòng 2): gán CỨNG khối giải phẫu trước — chậu → Root_M (núm đầu đùi |x|≥9 → Hip), cột cổ |x|≤6 →
  chuỗi Chest→Neck (4 cm sát đáy sọ dốc sang Head 0,8), Scapula chỉ |x|≥8, mảnh QA trên đáy hàm → Head; skin theo khoảng cách chỉ để hòa khớp,
  làm mượt riêng vùng khớp hông. Quét giãn cả Body lẫn QA (`MESH=_Body`). Cổ ×3,6 ở cú giật đầu chấp nhận (sọ to che).
- **FBX xuất từ Frolvy vào Unity (G-LumberCity 2026-11-03):** take tên `take1` (FBX Maya team là `Take 001`) → khi chép `.meta` mẫu của team phải đổi `takeName: take1`, `firstFrame` theo LocalStart của FBX (Frolvy xuất từ F1), guid + internalID mới; team bật loop ở `.anim` tách trong editor, FBX mới chưa có `.anim`.
- **FBX anim G-LumberCity chỉ joint + anim, không mesh** (user 2026-11-03 "fbx chỉ giữ joint với anim thôi ko cần mesh"): `export_clip(..., meshes=False)` mặc định; `tools/fbx_ascii_keep.py --no-meshes` bỏ cả Geometry + Skin/Cluster, không chỉ Model mesh. Kiểm số object sau khi lọc: chỉ còn Model/NodeAttribute LimbNode + AnimationCurve(Node) + Stack/Layer.
- **FBX chỉ joint (không mesh) vào Unity Generic + avatar copy:** khi `root` là node gốc DUY NHẤT trong file, Unity gộp nó vào prefab root → lỗi "Copied Avatar Rig Configuration mis-match … Cannot find root motion transform 'root'" (G-LumberCity 2026-11-03; bản còn mesh thì không lỗi vì có 3 node gốc). Sửa: `.meta` đặt `preserveHierarchy: 1`. Kiểm bằng Editor.log (`%LOCALAPPDATA%\Unity\Editor\Editor.log`, grep "mis-match").
