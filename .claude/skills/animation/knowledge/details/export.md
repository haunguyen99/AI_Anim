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
- **SDR (G-DieLoop): file anim gửi Unity luôn không mesh** (user 2026-11-04, SDR05 bị trả vì còn mesh). SDR01/03/06 trên Unity đều chỉ xương + anim. Khi rig/mesh prop đổi (vd Gatling → Colt), mesh đi riêng trong `SDR<NN>_MC_Base.fbx` đứng **T-pose = bind** (user 2026-11-04, không phải P0; xương lá không skin thì giữ local trong file vì rigpose đặt bind = tư thế gốc) (avatarSetup 1, clipAnimations []), còn .meta anim đặt avatarSetup 2, lastHumanDescriptionAvatarSource = guid Base, externalObjects {}. Kiểm sau khi xuất: 0 Geometry/Deformer/Material, 0 liên kết hỏng (`sdr05_colt/export_fbx.py`).
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
- **Mẫu mới tỉ lệ khác (zom1 Western V2, 2026-11-05, `work/shoot_die_repeat/zom1_map5_rig/`):** 3D co model (cao 188→177, sải tay 206→163) → không rebind giữ bind pose được, phải rig lại bằng `rig_v2.py`. Ngưỡng cm cố định của tay hỏng với tay ngắn (khuỷu rơi sát vai x 29,5): bàn tay / khe núm khuỷu tính theo tỉ lệ đầu ngón, CHỈ khi cách cũ không thấy bàn tay (găng QA map4 thì giữ cách cũ, lần đầu làm lệch ngón zom1 map4 26 cm). Sửa `rig_v2.py` xong luôn chạy lại 4 con v2 cũ, so `joints_*.json` (phải 0,000 cm). Kiểm thêm tay xuyên thân (`zom1_map5_rig/check.py`): tay ngắn + anim Humanoid chung → Walk4/Walk5 xuyên áo (rig cũ cũng có ở Walk5). Tên file 3D có thể sai (V2 của zom1 chứa mesh tên zom2): kiểm lưới / tên mesh trước, hỏi người dùng. Đổi tên mesh hoặc số cluster → prefab đã unpack phải gắn lại mesh + xương.
- **FBX xuất từ Frolvy vào Unity (G-LumberCity 2026-11-03):** take tên `take1` (FBX Maya team là `Take 001`) → khi chép `.meta` mẫu của team phải đổi `takeName: take1`, `firstFrame` theo LocalStart của FBX (Frolvy xuất từ F1), guid + internalID mới; team bật loop ở `.anim` tách trong editor, FBX mới chưa có `.anim`.
- **FBX anim G-LumberCity chỉ joint + anim, không mesh** (user 2026-11-03 "fbx chỉ giữ joint với anim thôi ko cần mesh"): `export_clip(..., meshes=False)` mặc định; `tools/fbx_ascii_keep.py --no-meshes` bỏ cả Geometry + Skin/Cluster, không chỉ Model mesh. Kiểm số object sau khi lọc: chỉ còn Model/NodeAttribute LimbNode + AnimationCurve(Node) + Stack/Layer.
- **FBX chỉ joint (không mesh) vào Unity Generic + avatar copy:** khi `root` là node gốc DUY NHẤT trong file, Unity gộp nó vào prefab root → lỗi "Copied Avatar Rig Configuration mis-match … Cannot find root motion transform 'root'" (G-LumberCity 2026-11-03; bản còn mesh thì không lỗi vì có 3 node gốc). Sửa: `.meta` đặt `preserveHierarchy: 1`. Kiểm bằng Editor.log (`%LOCALAPPDATA%\Unity\Editor\Editor.log`, grep "mis-match").

## Thay mesh mới vào rig team có sẵn (rebind, zom2_map6 2026-11-03, zom1_map4 2026-11-04, `work/shoot_die_repeat/zom1_map4_rebind/rebind.py`)
- **Dùng `tools/fbx_rebind.py <rig> <model> <thư mục ra> [--map CŨ=MỚI]`** (2026-11-04, ~40 s + ảnh): làm hết các luật dưới, tự thử hard/blend từng mesh trên 18 anim Share và chọn bản ít giãn/lật, kiểm theo kiểu Humanoid (góc xoay từ anim, độ dài xương của rig), ra `report.md` (bảng CŨ→MỚI, ⚠ khi tệ hơn) + `look/` (rest, anim, cận frame tệ nhất) + prefab dùng rig và số m_Bones. Nhận `git:REV:path`; file Unity trên máy khác origin thì tự lấy bản origin. Đã khớp lại zom1_map4 (trùng bản duyệt) và London (điểm tốt hơn bản duyệt). Xong thì gọi Director với report + ảnh.
- Giữ file rig, chỉ thay hình + UV + Indexes/Weights (`tools/fbx_replace_mesh.py`): xương, bind pose, anim, material trùng từng byte; kiểm lại bằng so pickle mọi object ngoài Geometry/Deformer.
- Đặt: ICP đồng dạng mới→cũ để ĐO; nếu s≈1, xoay≈0 thì dùng dời thuần (model Khải map4 lệch rig z −6,15 cm, bản model trước cũng thế), y = 0 giữ chân chạm đất.
- Skin theo tính chất mesh cũ: thân xương của rig team có ranh giới CỨNG (đỉnh 100% Chest cạnh đỉnh 100% Shoulder) → chép đúng 1 đỉnh cũ gần nhất; trộn 1/d² ở đỉnh nằm giữa sinh 73/27 → giãn vai 1,72 (Director trả). Vải (Items) thì trộn 1/d² khi xa > 0,3 cm (bỏ trộn: giãn 2,35, lật 4). Luôn cùng bên trái/phải.
- Theo khối rời: khối có bản cũ chỉ lấy từ chính mesh cũ đó (áo gile cũ 100% Chest_M; lấy từ thân thì mép vai ăn Shoulder, giãn 3–5×); khối mới hẳn mới lấy từ cả hai mesh.
- **Không thêm cluster** vào mesh trong rig mà prefab Unity đã unpack: SkinnedMeshRenderer lưu `m_Bones` = đúng số cluster (kể cả cluster rỗng) → thêm cluster lệch bindpose. Khối mới cần xương mesh đó không có (vòng cổ tay trái cần Wrist_L) → chuyển khối sang mesh có cluster đó. Điền cluster rỗng sẵn thì được.
- Kiểm: `zom_v2/stretch_scan.py` cả 2 mesh + `zom1_map4_rebind/flip_scan.py` (lật mặt) trên 18 anim Share, so CŨ|MỚI; ảnh `anim_test.py` CHẠY TUẦN TỰ (hai lần song song ghi đè ảnh tạm `_at_*.png` → ảnh "cũ" ra mesh mới).
- Tra prefab nào dùng rig: grep guid của .fbx.meta trong prefab (map4: prefab `En_Zom1_map4_Gameplay` dùng rig Zom2 và ngược lại).

## FBX Pose Lab: FileId phải khớp footer (SDR06 London Reload, 2026-11-06)
- Unity báo "Couldn't import file / File is corrupted" khi FBX do `work/pose_lab/fbx/fbxwrite.py` ghi có `FileId` = `00 01 … 0f` (giả) nhưng footer là mã Blender (`fbxbin`). Mã footer sinh từ FileId + CreationTime, hai bên phải khớp. Trước khi đẩy anim: so 16 byte FileId với một FBX Unity nhập được (Blender: `28b32aeb b624ccc2 bfc8b02a a92bfcf1`). Đã sửa trong fbxwrite.py; vá file cũ tại chỗ bằng cách thay 16 byte (không đổi độ dài).
- Cây xương / số node đúng chưa đủ để chắc file nhập được. Kiểm bằng Unity (Console) hoặc mayapy FBXImport; không có mayapy trên máy này.
- Meta bị Unity ghi lại sau lần nhập lỗi (đổi Humanoid → Generic, mất event): `git checkout` meta về bản đã đẩy trước khi commit.


## SDR anim-only theo khuôn team: chọn avatar nguồn (Pirate Reload, 2026-11-06)
- Avatar nguồn của meta = avatar mà prefab nhân vật đang dùng (`m_Avatar` trong prefab Actors/<Map>/…Gameplay.prefab), không mặc định Base.
  Jungle: Base có avatar → source Base. Pirate: Base `MC_char_map4.fbx` là animationType 0 (không avatar), prefab dùng avatar của
  `MC_char_map4_shoot.fbx` → meta copy từ meta team, `avatarSetup: 2`, `lastHumanDescriptionAvatarSource: {fileID: 9000000, guid: <guid shoot>, type: 3}`.
- Script: `sdr04/_reload/export_pirate.py` (gọi write_anim của `sdr01/_reload/export_team.py`; đừng đặt trùng tên file export_team.py
  ở thư mục khác rồi import, nó tự import chính nó).
- **Prop đổi chỗ tức thì (đạn từ nòng vào tay) trong Unity:** key mỗi frame vẫn bị Unity nội suy giữa 2 frame → prop bay ngang người
  (user thấy trong preview Pirate Reload). Chèn key giữ giá trị cũ ở 1/100 frame trước frame đổi chỗ + meta `resampleCurves: 0`
  (`export_pirate.py` step_keys). User xác nhận trong Unity hết bay (2026-11-06), kể cả xương có PreRotation.

- **Rebind GSDR-1547 (2026-11-10, `work/shoot_die_repeat/rebind_gsdr1547/`):** mesh Khải ở `3D/Model/FIX_0911/<Map>/` (tên mesh trong file vẫn là map1/map3, không khớp rig → luôn `--map`; tên rig/prefab zom1↔zom2 đặt chéo). Mesh cũ không có bản mới (đạn `bullet` Pirate MC) → `--keep bullet` (thêm vào `fbx_rebind.py`). Trước khi rebind SO đỉnh model mới với model cũ (Pirate MC, Mayah MC y hệt 0,000 cm → không cần làm; Mayah zom3 chỉ lệch ≤1,9 cm). MC có súng 2 cluster: ICP lấy theo thân, súng lệch 60 cm nếu model đặt khác pose rig.

## Base + anim-only (mọi dự án, user 2026-11-12)
- Luôn xuất 2 loại: **Base** = xương + mesh (T-pose/bind); **file anim** = chỉ xương + clip, không Geometry / Deformer / Material / Texture. Mục đích: lắp anim vào Unity không lỗi.
- Pet Infinite Defense: `Pet_<Tên>.fbx` (Base) + `Pet_<Tên>_Idle.fbx`, `Pet_<Tên>_Attack.fbx` (anim-only). Tên xương trong file anim phải trùng Base.
- Kiểm trước khi đẩy Unity: file anim 0 mesh, 0 liên kết hỏng, số xương = Base; Base có mesh + skin. Chạy `tools/pet_fbx_finalize.py` cho UnitScale 100 (xem pet_quadruped_mecha_pup.md).
- **Đích Unity của Pet Infinite Defense (user 2026-11-12):** `C:\Users\Admin\Documents\Horus\endless-kicker\Assets\_Game\Animation\New_Pet\Pet_<Tên>\` (Base + _Idle + _Attack, theo kiểu mỗi nhân vật một thư mục như Hero/Normal). File làm việc ở `C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_<ID>_<Tên>\`. Chỉ chép sau khi kiểm; không commit repo Unity khi chưa được bảo.
- **Quy ước tên (user 2026-11-12):** nối bằng gạch dưới `_`, không dùng `@` (đã đổi tên 3 Pet đầu).
- **Base Pet skin vỡ trong Unity (Pebble Turtle 2026-11-12):** FBX ASCII của Frolvy không có BindPose và Unity (2022.3) lấy `Transform` của Cluster làm bindpose, bỏ qua `TransformLink` → mesh skin lệch đúng bằng vị trí xương (đầu/chân bay khỏi thân). Sửa sau `fbx_ascii_keep`: `tools/fbx_unity_bind.py in out` (thêm BindPose + đặt Transform = nghịch đảo TransformLink, xương không xoay). Đo bằng Unity batchmode (Unity 2022.3.62f2 có trên máy): project tạm + script Editor in `SkinnedMeshRenderer.BakeMesh().bounds` so với `sharedMesh.bounds` (phải bằng nhau ở bind), bindposes, xương. Base không để clip `take` tĩnh (`tools/fbx_strip_anim.py`); file anim đặt tên take = Idle/Attack. Copy-avatar từ Base chạy sạch trong thử batchmode.
- **File anim-only Pet: "Cannot find root motion transform 'DEF_Root_M'" (Copy From Other Avatar, 2026-11-12):** Unity coi nút gốc DUY NHẤT của file là gốc file, còn Base có mesh cùng cấp với xương → khác cấu trúc. Sửa: `tools/fbx_add_sibling.py in out` thêm một nút Null cùng cấp vào file anim (Base giữ nguyên). Đã kiểm bằng Unity batchmode (log "Import Messages" in ra log; clip chạy, 0 path thiếu). Chạy sau `fbx_ascii_keep --no-meshes`.
- **Khi nào xuất (user 2026-11-13):** nhánh con/Pet chỉ xuất FBX khi user bảo "chốt". Các vòng sửa và feedback chỉ sửa + lưu .fv trong Frolvy, không xuất, không chép Unity.
- **Chốt Pet (user 2026-11-13):** nói "chốt <Pet>" thì tự: `tools/pet_chot.py clean <ID>` (giữ .fv mới nhất của mỗi clip, xóa bản cũ + raw_* + _tmp) → xuất FBX chốt (Base + _Idle + _Attack) bằng quy trình xuất của Pet đó → `pet_chot.py check <ID>` (Base có mesh/deformer/BindPose, 0 AnimationStack; file anim 0 mesh, có Dummy) → `mark <ID>` ghi CHOT.txt để WorkAI tích Done.
- **Sau chốt, thư mục Pet thống nhất (user 2026-11-13):** chỉ còn đúng 3 FBX chốt (Base, _Idle, _Attack) + .fv mới nhất mỗi clip trong `New_PET\Pet_NN_*`; xóa mọi FBX khác (raw_*, _src, _orig, _old_fbx) và bản sao mesh / fbx_backup trong `work/infinite_defense/pets/<tên>/`. `tools/pet_chot.py clean <ID>` làm hết; chạy cho mọi Pet đã chốt.
- **Hero Nova Base vỡ trong Unity (2026-11-18):** triệu chứng = mesh co quắp (chân gập, tay chìa ra) ở tab Model. Nguyên nhân = lỗi bind như Pebble Turtle nhưng xương Nova CÓ joint orient (24/29 cluster TransformLink có xoay) nên `fbx_unity_bind.py` từ chối → dùng `tools/fbx_unity_bind_rot.py` (sai số 2.5e-5). Base xuất từ Frolvy còn clip `take1` tĩnh → `fbx_strip_anim.py` trước. Chạy: strip_anim → unity_bind_rot. Chưa kiểm bằng Unity batchmode (máy Linux không có Unity).
- **Nova vũ khí `vk_Hero_NOVA1` mất trong Unity (2026-11-18):** không phải sai vị trí mà là mất cha. Đỉnh súng lưu theo khung của xương `DEF_Weapon_R` (nhóm Null `vk_Hero_NOVA1` đáng lẽ nằm dưới Weapon_R), nhưng `export_scene` của tôi ghi Null ở gốc (`C: OO,<Null>,0`) → `fbx_ascii_keep --root DEF_Root_M` bỏ Null, mesh mồ côi → Unity không nhập mesh súng (sub-asset chỉ còn Hero_NOVA_game1). Sửa: trước ascii_keep đổi `C: "OO",<Null>,0` thành cha = id `DEF_Weapon_R` (súng theo tay, đúng vị trí Frolvy, sai số 4e-5 kiểm bằng world(Weapon_R)×đỉnh vs `api.mesh_data`). Chuỗi Nova Base: raw → gắn Null vk dưới DEF_Weapon_R → ascii_keep --root DEF_Root_M → strip_anim → unity_bind_rot. Kiểm sau khi xuất: mọi Model mesh phải có kết nối cha; trong Unity đếm sub-asset mesh = số mesh. `tools/fbx_fix_mesh_frame.py` (bake khung vào đỉnh) chỉ dùng khi mesh thật sự không có cha; ở Nova KHÔNG dùng.
