# MAP: bản đồ project AI Animation

Bản đồ ghi file nào nằm ở đâu và file mới nên lưu vào đâu. Đọc file này trước khi tạo script hay thư mục mới để tránh trùng. Mỗi khi tạo, đổi tên hoặc dời file, cập nhật lại MAP này, mỗi mục một dòng.

Quy trình chính được mô tả trong [docs/pipeline_v2.md](docs/pipeline_v2.md): Blender-first, gồm 7 bước và 3 cổng duyệt.

## Đang làm gì (2026-10-21)

| Clip | Trạng thái | Scene / script build | Export |
|---|---|---|---|
| Gaygor Idle (133F) | Đã duyệt bản polish v5 · trang review https://claude.ai/artifact/JK2CCuwPktgUCsD6k5fe6s | `work/blender/boss_idle.blend`, `key_idle_v2.py` | `work/idle/export/EN_M11_Boss_Gaygor_Idle.fbx` |
| Gaygor Idle_Front (60F) | Đã duyệt bản v14 | `tools/blender/idle_front_build.py` | `work/idle_front/export/EN_M11_Boss_Gaygor_Idle_Front.fbx` |
| Gaygor Attack (68F) | Blender: blocking v9 (tạm dừng). **Làm lại từ đầu trong Cascadeur** (2026-10-21): P0 đã duyệt 2026-10-21 (`gaygor_attack_p0_approved.casc`); blocking nhanh đủ 21 key (`gaygor_attack_blocking.casc`), v1 duyệt làm nền, sửa góc left tới `casc_blocking_v4` (2026-10-21), chờ duyệt; các góc còn lại chưa sửa. **2026-10-22 quay lại Blender v9** (lỗi: `work/attack/v10rev/defects_v9.md`); **blocking v10** lên trang review 2026-10-22 (sửa: `work/attack/v10/fixes.py`), chờ góp ý | `work/blender/boss_attack_v10.blend`; Cascadeur `work/cascadeur/gaygor_attack_p0.casc` | Pose Lab: https://claude.ai/artifact/RRZZBxz7FzPHsv13Bu4Ao6 (p0_v2; **anim_v1 2026-10-23 = làm anim trên trang**: key, spline, bám sàn, ref 5 góc `work/pose_lab/refs/gaygor_walk/`, Xuất FBX, nút Khớp ref (không Blender); **blocking b1: 8 key F1–F50 khớp ref; user OK tổng quan; b2 sửa chân trái (bỏ lật 18–24°, hạ gót F22/F42) đã ghi db (`work/walk/block_b2/`); b3 đặt chân lên sàn theo lưới (F22 phải lún 4 cm, F36/F42 trái lơ lửng 2 cm), `work/walk/block_b3/`**; code `work/pose_lab/fbx/`); áp chỉnh sửa Pose Lab: `work/walk/apply_adjust.py` + `work/walk/adjusts/` |
| SDR (Shoot Die Repeat) Idle + Attack | Đã export | `work/blender/sdr_*.py`, `work/sdr/` | `work/sdr/export/SDR_MC_*.fbx` (kèm `_events.json`) |
| SDR map06 (gangster + Tommy gun): Attack/Shoot + Reload | **HOÀN THÀNH 2026-10-22** (Base/Idle/Shoot/Reload FBX) · P0 v8 (ngực 54°); Shoot blocking b12 ĐÃ DUYỆT (tag sdr06-shoot-blocking-b12); Reload blocking b23 ĐÃ DUYỆT (tag sdr06-reload-blocking-b23); Reload lhand_b5 ĐÃ DUYỆT (tag sdr06-reload-lhand-b5); lhand_b6 ĐÃ DUYỆT (tag sdr06-reload-lhand-b6; Pose Lab trống F16–F22) → spline tay trái lspline_v1 ĐÃ DUYỆT (tag sdr06-reload-lspline-v1, `work/sdr06/spline_lhand.py`), đã xuất `work/sdr06/export/SDR06_MC_Reload.fbx` F1–F42 + anim_only từ bản này; Shoot polish v1 ĐÃ DUYỆT (tag sdr06-shoot-polish-v1; P0 = Reload F1 qua `p0_reload_f1.json` từ `dump_reload_p0.py`) → `work/sdr06/export/SDR06_MC_Shoot.fbx` (F1–F13) + anim_only; Idle 10F (1 pose = Shoot F1, `work/sdr06/make_idle.py`) → `SDR06_MC_Idle.fbx` + anim_only (2026-10-22) · FBX 2026-10-22: base `SDR06_MC_Base.fbx` (joint + mesh, `tools/blender/export_base.py`); súng `slingshot_0` là con của **Wrist_R** (`tools/blender/reparent_prop.py`, baked *_wristR.blend) | `work/blender/build_sdr06.py` → `sdr06_char.blend`, `work/sdr06/` | chưa có |
| Gaygor Walk (57F, loop in-place) | Bước 2: `work/walk/analysis.md` chờ duyệt (2026-10-22); lịch bước chân `work/walk/analysis/foot_schedule.json` (đo silhouette, mocap RTMPose/MediaPipe thử nhưng không dùng: `work/walk/mocap*.py`) | Analysis ĐÃ DUYỆT 2026-10-22 (giữ bất đối xứng, in-place, animate phụ kiện, 56F loop). Scene dựng: `work/blender/boss_walk.blend` (build `work/blender/build_walk.py` từ Idle, P0 f1 = Idle_Front + chân/hông khớp ref (`p0/legs_f01.json`, key trong action Walk; sửa `CTRL_hand_ik_L` về 0 vì action Idle lưu theo parent cũ), thân/tay/chùy chưa tinh chỉnh; camera Walk 305,3 px/m; render+overlay `work/walk/render_frames.py`, `overlay.py`) | chưa có |
| Queen Spider | Mới có ref, chưa bắt đầu | — | — |

## Thư mục gốc

| Đường dẫn | Nội dung |
|---|---|
| `MAP.md` | File này |
| `docs/pipeline_v2.md` | Quy trình chuẩn, bài học từ các hướng đã thử, các cổng duyệt |
| `docs/rig_lab_design.md` | Thiết kế Rig Lab (tool rigging trên web: mesh trần → xương, skin, control rig, QA, FBX), bản nháp chờ duyệt 2026-10-23 |
| `.claude/skills/ai-animation/` | Skill chính. `SKILL.md` là quy trình; `knowledge/CORE.md` (luật cho mọi clip, ≤ 6 KB) + `INDEX.md` (mục lục) đọc mỗi task; chi tiết ở `knowledge/details/<chủ đề|loại>.md`, chỉ mở khi cần (gom lại 2026-10-22). Cập nhật sau mỗi task. `SKILL.v1.md` là bản cũ |
| `.claude/launch.json` | Cấu hình preview server |
| `.mcp.json` | MCP servers (Cascadeur: phải bật Commands → MCP → Start script server mỗi lần mở): `blender` (port 9876, cửa sổ Idle), `blender_attack` (port 9877, cửa sổ Attack), `cascadeur` (HTTP 8765) |
| `requirements.txt`, `tools/setup.ps1`, `.venv/` | Môi trường Python (OpenCV + NumPy). Chạy `setup.ps1` một lần |
| `.git/`, `.gitignore` | Git local (từ 2026-10-21). Chỉ theo dõi code, md, json nhỏ. File nặng (.blend, .fbx, video, ảnh, .npy) bị bỏ qua, version bằng `_vN`. Mỗi version được duyệt/từ chối = 1 commit kèm lý do; bản duyệt có tag `<nhân vật>-<clip>-v<N>-approved` |

## Assets/ (input từ khách hoặc team, chỉ đọc)

| Đường dẫn | Nội dung |
|---|---|
| `Assets/Boss_Gaygor/Rig/EN_M11_Boss_Gaygor_rig.fbx` | Rig gốc Gaygor (gorilla cầm chùy) |
| `Assets/Boss_Gaygor/Texture/` | `T_Colorpalette.tga` |
| `Assets/Boss_Gaygor/Ref/Boss_Gaygor_idle/` | Ref Idle 6 góc `.mov` (front/back/left/right/top/game). Chú ý: `_left` là camera đặt bên **phải** nhân vật (xem pipeline_v2 §1) |
| `Assets/Boss_Gaygor/Ref/EN_M11_Boss_Gaygor_attack/playblasts/` | Ref Attack |
| `Assets/Boss_Gaygor/Ref/EN_M11_Boss_Gaygor_walk/playblasts/` | Ref Walk (đang phân tích → `work/walk/`) |
| `Assets/Boss_QueenSpider/Ref/` | Ref attack / crawl / idle (chưa làm) |
| `Assets/Shot-die-repeat/` | `MC_char_map2_Rig.fbx` (lính La Mã cầm gladius) và texture. Không có ref |
| `Assets/Shot-die-repeat/map06/` | `MC_char_map6_Rig.fbx`: gangster cầm Thompson (cùng skeleton với map2; xương súng `slingshot_*` là con của Chest_M). Dùng chung texture `T_Color_ShotDieRepeat.tga` |

## tools/ (công cụ dùng chung giữa các clip)

Script Python chạy bên ngoài Blender bằng `.venv`. Script nằm trong `tools/blender/` chạy bên trong Blender, qua MCP `execute_blender_code` hoặc headless với `-b`.

**Thiết lập scene và rig (bước 3)**
- `tools/blender/setup_scene.py`: dựng scene cho một job (model, fps, range, camera Ref_*)
- `tools/blender/build_ctrl_rig.py`: dựng control rig "CTRL" (IK chân/tay, follow space, prop)
- `tools/blender/arm_ik_R.py`, `add_arm_ik_R.py`: thêm IK tay phải vào CTRL
- `tools/blender/inspect_rig.py`, `rig_inventory.py`: dump hierarchy, đoán mapping, phân loại xương chính và phụ
- `tools/blender/joint_limits.py`: kiểm tra giới hạn khớp
- `tools/blender/bl_common.py`, `anim_helpers.py`, `live_render.py`: helper dùng chung bên trong Blender

**Phân tích ref (bước 2)**
- `tools/ref_timing.py`: đo chuyển động từng bộ phận trên ref
- `tools/part_strips.py`: dải thời gian của một bộ phận trên mọi góc
- `tools/ref_masks.py`: silhouette ref theo từng frame và từng góc
- `tools/tri.py`: dùng 2 góc orthographic để triangulate điểm 3D
- `tools/calib_from_anim.py`: hiệu chỉnh camera ref từ một anim đã biết

**Tạo pose và key (bước 4–5)**
- `tools/blender/solve_keys.py`, `fullbody_solve.py`: giải pose blocking từ chuyển động đo được
- `tools/blender/grip_set.py`: grip tay trái lên cán vũ khí
- `tools/blender/direct.py`: chỉnh curve thay vì key lại
- `tools/blender/idle_front_build.py`: build Idle_Front từ đầu đến cuối (curve thở chung, overlap)
- `tools/blender/head_refine.py`, `sil_refine.py`, `photo_refine.py`, `weapon_search.py`, `stage_trials.py`, `leg_trial.py`, `armR_trial.py`, `weapon_aim_trial.py`: tinh chỉnh từng phần hoặc thử nghiệm
- `tools/keyanim.py`, `tools/keyedit.py`, `tools/blender/key_pose.py`, `eye_pose.py`: luồng eye-keying cũ dựa trên keys.json

**So sánh REF|ANIM bằng mắt**
- `tools/blender/eye_views.py`: render pose hiện tại qua mọi camera Ref_*
- `tools/eye_side.py`: REF | ANIM đặt cạnh nhau, outline ANIM vẽ chồng lên REF (dùng nhiều nhất)
- `tools/eye_compare.py`, `eye_blend.py`, `eye_diff.py`, `eye_outline.py`: các kiểu overlay khác
- `tools/eye_head.py`, `eye_torso.py`, `eye_legs.py`, `eye_part_box.py`, `eye_weapon_out.py`: close-up theo bộ phận
- `tools/blender/eye_part.py`, `sil_render.py`: render riêng một bộ phận hoặc silhouette
- `tools/eye_iou.py`, `eye_legs_iou.py`, `sil_compare.py`, `sweep_score.py`, `extent_cmp.py`: số đo IoU và extent. Chỉ dùng để kiểm tra, không dùng để kết luận pose đã khớp
- `tools/blender_overlay.py`, `tools/part_overlay.py`: overlay render hoặc vertex lên frame ref
- `tools/lookgrid.py`: ghép nhiều ảnh look_<frame> thành một sheet

**QA và playblast (bước 6)**
- `tools/blender/qa_report.py`: QA tự động cho action live (trượt chân, xuyên, khựng loop, rung)
- `tools/clip_check.py`: kiểm tra prop xuyên vào thân
- `tools/motion_compare.py`, `motion_compare2.py`: so chuyển động theo vùng giữa anim và ref
- `work/attack/v10/fixes.py`: các hàm sửa key v10 (`fixNN`, `goto_v9`, `plant_p0`, `mace_slope`); `work/attack/v10rev/trial.py`, `diff.py`, `ext.py`: render thử, so silhouette, đo độ cao/bề rộng
- `tools/playblast_ref.py`: video review REF | ANIM, các góc xếp theo hàng
- `tools/playblast_compose.py`: video review REF | render cho mọi frame
- `tools/playblast_anim.py`: playblast cho clip không có ref (lưới 2x2, loop)

**Export (bước 7)**
- `tools/blender/export_clip.py`: bake CTRL sang xương deform rồi xuất FBX cho Unity
- `tools/blender/dump_joints.py`, `retarget_world.py`: dump và retarget transform world để so sánh với anim gốc
- `tools/blender/score_pose.py`: chấm pose so với anim gốc (chỉ dùng làm đáp án, không dùng để đặt pose)

**Cascadeur (`tools/cascadeur/`)**
- `casc_views.py`: chạy **trong Cascadeur** (MCP `run_script`). Camera ortho khớp pixel với ref Attack (1920×1080, 2,313 px/cm, sàn y = 910); mỗi lần gọi chỉ render được một góc (`render_view`), gọi `restore()` ở lần cuối
- `casc_mask.py`: biến ảnh render đục của Cascadeur thành RGBA `<tag>_<view>.png` để dùng với `tools/eye_side.py`
- `casc_pose.py`: chạy **trong Cascadeur**. Đọc/đặt điểm AutoPosing (`points`, `set_points`, `move_foot`), key joint không có controller (`set_joint_local`, cho prop), `two_bone_elbow` (IK giữ chiều dài xương), `curl_fingers`
- `front.ps1`: đặt cửa sổ Cascadeur nổi lên trên **không lấy focus** (`-Release` trả lại). Cascadeur chỉ ghi ảnh render khi cửa sổ đang hiện
- `k0.json` + `casc_views.calibrate_k0`: hằng số tỉ lệ render theo layout cửa sổ hiện tại
- `casc_pose.ensure_key(scene, F)`: tạo key ở frame F trên mọi layer (phải có key thì điểm đặt mới giữ)

**Đã bỏ (giữ lại để tham khảo)**
- `tools/fit/`: fit silhouette theo từng frame (analysis-by-synthesis). Hướng này đã bỏ vì kết quả rung và "máy" (pipeline_v2 §0)
- `tools/viewer/index.html`: viewer three.js cũ dùng cho keys.json

## work/ (dữ liệu làm việc, bị gitignore)

| Đường dẫn | Nội dung |
|---|---|
| `work/index.json` | Danh sách job (attack, idle, idle_breath, idle_look) |
| `work/blender/` | **Các file .blend chính** cùng script key và rig theo từng clip (xem bên dưới) |
| `work/idle/` | Job Idle 133F: `analysis.md`, `anim_brief.md`, camera, `p0_stages.json`, `blocking*_params.json`, video `review_*`, `export/` |
| `work/idle_front/` | Job Idle_Front 60F: `breath_v*.json`, video review v2–v14, `export/` |
| `work/idle_breath/`, `work/idle_look/` | Các job Idle cũ (30F breath, look-around) |
| `work/attack/` | Job Attack: `analysis.md` (bản hiện hành), `anatomy_v*.json`, `pose_f13/f25/f31.py`, công cụ so sánh riêng (`cmp.py`, `batch_cmp.py`, `crop_cmp.py`, `contact.py`, `rulers.py`), ghi chú `v*notes`, video `review_blocking_v*` |
| `work/sdr/` | Job Shoot Die Repeat: `attack_analysis.md`, `attack_events.json`, `p0_pose.py`, `p0_run.py`, `playblast_attack.py`, `strip.py`, các bản playblast `pb_*`, `export/` |
| `work/sdr06/` | Job SDR map06 (Shoot + Reload): `analysis.md` (Duyệt 1), `p0_shoot.py` (P0 theo mức + giải tay lên súng `hand_on`), `p0_run.py` (build P0 headless), `blocking.py` (key stepped cả 2 clip, render frame), `spline.py` (spline Reload), `spline_shoot.py` (spline Shoot: kernel giật liên tục + trễ lẻ frame, bake vòng lặp), `playblast.py` (video review), `review_<clip>_<ver>.mp4/.webm`, `pb_<clip>_<ver>/`, `ref_frames/` (tấm frame ref YouTube 1:25–1:32), `look/` (render rest + close-up súng) |
| `work/review_page/` | **Review Lab** (trang review, đổi tên 2026-10-23, tiêu đề mỗi trang dạng `<anim> Review Lab` trong `split_pages.py`): `index.html` là bản master, `split_pages.py` tách thành mỗi anim một artifact (`pages/`), `clips/` chứa webm và jpg của từng version |
| `work/pose_lab/` | Pose Lab 3D (dùng lại từ 2026-10-22): `index.html` = master (POSES, 1 dòng/phiên bản, mới nhất trên cùng), `split_pages.py` → `pages/<anim>/index.html` (1 artifact + db riêng mỗi anim: sdr06_reload, sdr_idle), `models/*.json` (glTF xuất bằng `work/blender/export_pose_glb.py frames=a-b`). Chế độ key trên trang (POSES `mode: "keys"`): key trong db `keys`, spline + bám sàn trong trang. Ảnh ref: `make_ref_sprites.py` → `refs/<anim>/<view>.jpg`. Kiểm FBX trang vs Blender: `fbx/cmp_page_track.py`. Chỉnh sửa áp về Blender bằng `work/sdr06/pose_lab_apply.py` → `cache/lhand/manual.json` |
| `work/cascadeur/` | Gaygor Attack làm lại trong Cascadeur (2026-10-21): `gaygor_attack_rig.casc` (rig FBX gốc + Quick Rig + AutoPosing), `gaygor_attack_p0_l1..l4.casc` (từng mức đã duyệt), `gaygor_attack_p0.casc` (P0 đủ 5 mức), `Gaygor_AdvancedSkeleton.qrigcasc` (tạo bằng `make_qrig_template.py`); `partcrop.py`/`sbs_left.py` (REF|ANIM có shading theo dải độ cao, sửa từng phần), `block_pose.py` + `keys/fNN.json` + `keys/plant.json` (blocking nhanh toàn thân 1 key/lượt, `keys/fNN_points.json` = điểm đã đặt, `keys/mk_rest.py` sinh thông số 15 key trung gian), `pb/blocking_v1/` (frame RGBA cho playblast_ref), `mace_fit.py` (KHÔNG tin được, chỉ để ghi lại), `gaygor_attack_f13_l1.casc` (f13 cấp 1 hông+chân); công cụ đo riêng clip: `feet_measure.py` (dải chạm đất), `crop_ticks.py` (cắt REF/ANIM có vạch cm), `sheet.py` (bảng nhiều góc); `look/` (render so ref), `shots/` |
| `work/rig_lab/` | Rig Lab M1 (2026-10-23, thiết kế `docs/rig_lab_design.md`): `extract_fbx.py` (đọc FBX không Blender → `ref_gaygor/ref_mesh.json`, `ref_skeleton.json` = rig khách làm đáp án), `propose.py` (gợi ý khớp biped từ mesh, tỉ lệ tuned trên Gaygor → `landmarks_auto.json`), `template.html` (nguồn duy nhất; các `patch_*.py` chỉ là lịch sử sửa, không chạy lại) + `build_page.py` → `pages/gaygor/index.html` (5 bước: mesh, khớp, skeleton, skin (chọn joint trong viewport, cọ tô, lưu skin db `rig/skin`), thử khớp; twist joint, undo, chọn nhiều kiểu Maya; cổng duyệt lưu db `rig/gates`, khớp lưu db `rig/landmarks`). Trang: https://claude.ai/artifact/UgRawtmJZW6biJZVbUK4Rs ; preview `rig-lab` cổng 8772 |
| `work/boss/`, `work/eye/`, `work/naenae/` | Các thử nghiệm sớm (fit, eye-keying, nae_nae). Không còn dùng |

**work/blender/: file .blend**
- `boss_idle.blend`, `boss_idle_baked.blend`, `boss_idle_front_baked.blend`: Gaygor Idle và Idle_Front
- `boss_attack_v10.blend`: Gaygor Attack, bản mới nhất (v9 = bản trước, `goto_v9` đọc từ nó). Các bản v4–v8 và `boss_attack.blend` là bản cũ
- `sdr06_char.blend` (SDR map06, build bằng `build_sdr06.py`), `sdr06_p0.blend`, `sdr06_shoot_b*.blend`, `sdr06_reload_b*.blend`, `sdr_char.blend` (nhân vật SDR), `sdr_p0*.blend`, `sdr_attack*.blend`, `sdr_*_baked.blend`

**work/blender/: script**
- Idle: `idle_blocking_setup.py`, `key_idle_blocking.py`, `key_idle_v2.py`, `key_idle_breath*.py`, `key_idle_front.py`, `p0_grid.py`, `p0_refit.py`
- Attack: `build_attack_v4.py`, `rig_attack_v4*.py`, `attack_load.py` (loader một dòng cho cửa sổ Attack), `attack_pose.py`, `attack_fit.py`, `key_attack_blocking.py`, `mace_measure.py`, `mace_refix.py`, `hand_contact.py`, `sym_fix.py`. `attack_v3_keyer.py` là bản cũ
- Anatomy: `anatomy_check.py` (chạy trên mọi key trước khi gửi), `anatomy_fix.py`; `tools/blender/pole_audit.py` (gối lệch mũi chân, khuỷu thấp hơn vai, roll bắp tay nhảy giữa key; chạy mọi key trước khi render)
- SDR: `build_sdr.py`, `sdr_lib.py`, `sdr_attack*.py` (blocking v8, spline v4, polish v2)
- Khác: `export_pose_glb.py` (GLB cho Pose Lab)

## legacy/, tests/, test_assets/

- `legacy/mediapipe/`: pipeline MediaPipe cũ (video người → mocap). Không dùng nữa
- `tests/`: `make_test_rig.py`, `render_video.py`, `render_views.py`
- `test_assets/`: rig thử, ref boss front/left, `nae_nae.webm` (xem `CREDITS.md`)

## File mới lưu ở đâu

- Công cụ dùng được cho nhiều clip → `tools/` (chạy trong Blender thì đặt ở `tools/blender/`)
- Script riêng cho một clip → `work/blender/<clip>_*.py`, hoặc `work/<job>/` nếu là script so sánh hoặc pose
- File .blend → `work/blender/`, đánh version bằng hậu tố `_v<N>`
- Phân tích, brief, ghi chú review → `work/<job>/`
- FBX bàn giao → `work/<job>/export/`
- Bài học rút ra → `.claude/skills/ai-animation/knowledge/details/<chủ đề>.md` (+ 1 dòng INDEX nếu mục mới; CORE chỉ khi luật cho mọi clip)
- Skill `/new_clip` + `tools/clip_registry.py` + `work/clips.json` (sổ clip: link Rig Lab, Pose Lab, Review Lab của từng clip và giai đoạn; `split_pages.py` của cả hai lab đọc sổ này) → nối chuỗi Rig → Pose → Review
- Skill `/rig_ai` (`.claude/skills/rig_ai/`) → gọi Rig Lab: mở trang, đọc cổng duyệt và khớp trong db, dựng nhân vật mới
- Skill `/fb` (`.claude/skills/fb/`) → nhận lượt review đã gửi, sửa gộp mọi note trong 1 version
- `tools/quick_sheet.py` → gộp render nhanh (`quick=F views=…`) thành 1 ảnh để tự kiểm
