---
name: reference-pose-lab
description: "Pose Lab 3D" artifact - 3D review page where reviewers rotate joints on the model per frame and send adjustments to AI
metadata:
  type: reference
---

**Active again 2026-10-22** (user: "hôm trước chúng ta có làm Trang Review 3D. phát triển tiếp trên đó"; parked
2026-10-20 before). First clip: SDR06 Reload lhand_b2, 42F, so the user can edit the hand pose in 3D. Playblast page
stays the main review; Pose Lab is for direct pose edits.

One page per animation (2026-10-22, user: map2 and map06 must not share a page; keep versions like the video review):
SDR06 Reload https://claude.ai/artifact/UKYdqvs5TXEfXJsg9GSJ3y, SDR Idle (map2) https://claude.ai/artifact/XvHD2HJ4CA74skzx8mmfdZ.
Master work/pose_lab/index.html (POSES one line per version, newest first, date + note) -> `split_pages.py` ->
pages/<key>/index.html; new version = new model json (old kept) + POSES line + split + publish with files. User asked for it 2026-10-20 as the 3D counterpart of [[reference-review-page]].
- three.js r128 viewer, joint handles + TransformControls, foot-lock IK, ghost of the original pose, timeline with
  per-frame drafts (keys, red = unsaved, yellow = saved adjust).
- Models: `work/blender/export_pose_glb.py -- <out>.json frames=a-b` (bakes the visual pose per frame; exports ONLY
  the baked action - with every action in the file the gun lay on the floor; clip starts at t=1/30 -> page offsets
  by the first key time, it was one frame late). Publish with `files` {"models/<x>.json": ...}. (artifacts cannot serve .glb, so the GLB is converted to
  glTF JSON with the buffer embedded). POSES entry needs clip, version, frames, fps, keys, glb path.
- db `adjusts`: {clip, version, frame, bones{name:{dq [w,x,y,z] Blender-world delta, deg}}, root{dp}, legs{L/R:{ankle,
  knee, ankleDq}}, local (viewer locals for preview), text, author, status}. `rounds/<clip>-<version>` same states as
  the playblast page (sent -> working -> fixed).
- SDR06: `work/shoot_die_repeat/sdr06/pose_lab_apply.py` applies adjust docs on their frame, keys CONSTANT and writes the local
  channels to work/shoot_die_repeat/sdr06/cache/lhand/manual.json; `lhand.build()` re-keys manual.json over the solve (held to the next
  key on the left arm). Round-trip at F14 matched to 0.1 mm. slingshot_0 (gun) is constraint-driven in SDR06: edits on
  it do not stick.
- Blender side: save adjust JSON to work/shoot_die_repeat/sdr/adjusts/<clip>/, `sdr_lib.apply_adjust` (FK upper body, IK legs with
  pole refinement); round-trip error 0.00 cm upper body, 0.07 cm knees.

**Gaygor Walk P0 (2026-10-23)**: page https://claude.ai/artifact/RRZZBxz7FzPHsv13Bu4Ao6 (clip Gaygor_Walk, version p0_v1, 1 frame, left hand on mace wrong). Model from `blender -b boss_walk.blend --python work/blender/export_pose_glb.py -- work/pose_lab/models/gaygor_walk_p0_v1.json frames=1-1` (reads the SAVED blend). Publish from scratchpad copy (files must be under cwd/scratchpad), capabilities db+user+comments. Next: user sends adjust docs -> apply on f1 in boss_walk.blend.

**Physics layer (2026-10-24, user approved design "làm tiếp theo đề xuất")**: thẻ Vật lý in every keys-mode page - live
springs (joint/hinge/prop/elbow swing), colliders + floor as inelastic constraints, pin lane, end ease, Bake/Hoàn tác
bake, Gaygor preset button. Settings saved in db `anims` field `phys`. Python twin tools/physics_sim.py. Spec + results:
docs/poselab_physics_p1.md. Published on Hit, Attack 50 and Walk pages (Walk 2026-10-25, live page was the d0a0cb4 build, read in full first).

**Body collision (phase 2, 2026-10-25, user approved "oki làm như đề xuất")**: thin core capsules + surface points from the skin, Idle as rest, red "xuyên" lane + list + shapes view + core radius slider; springs and props never go deeper into the body than the key. Spec + eye-checked results: docs/poselab_physics_p2.md. Published on Hit, Attack 50, Walk pages.

**Balance (phase 3, 2026-10-25, user "theo đề xuất của bạn")**: CoM (core volumes + prop 15 %), support (feet/prop within 5 cm or painted lanes), capture point, step-aware runs (lean / momentum / missed step / airborne), floor drawing, orange lane, "Đưa trọng tâm vào chân" button. Fall/death pack = separate package next. docs/poselab_physics_p3.md.

**Fall/death pack (2026-10-25, user "duyệt")**: auto-found falls judged against a rigid topple about the feet (own start tilt + speed) or free fall; graph + "Bóng đổ theo vật lý" ghost; late/early ≥ 2 F or ease-out flagged; "lún sàn" > 2 cm; lying segments = support; springs avoid the floor, 15 % bounce. Python twin matches (`--balance` on phys_check/attack_fall_bal.json). docs/poselab_physics_p4_fall.md.

**Impacts + ragdoll (p5, design approved 2026-10-25 "duyệt đề xuất", auto-step on)**: step 1 done and published (Hit, Attack 50, Walk): "+ Tác động" on any body point, 4 levels by CoM speed, tone 0.6 blend, hips = inverted pendulum, auto-step by predicted capture point, Python `--impact`. Steps 2 (ragdoll) and 3 (muscles) wait for the user to try step 1. docs/poselab_physics_p5_impact.md.
Ragdoll (p5 step 2, 2026-10-25, user "làm luôn bước 2"): published on Hit / Attack 50 / Walk. XPBD with muscles ("Sức" curve), measured joint limits (CHAR_PHYS.Gaygor.limits), held mace merged into the hand, release, sleep, clip extension (phys.rag.len). Python `--ragdoll` matches the page exactly. Step 3 (muscles with reflex poses, balance) not started.
Ragdoll with muscles (p5 step 3, 2026-10-25, user "làm bước 3 luôn đi"): 6 strength parts, balance drive (hips toward the key while the capture point is inside the feet), "cần bước" report, reflex from key poses. All 3 steps of p5 done; next real test = Gaygor Die.
Ragdoll "Về đích" (2026-10-26, user "Oki làm đi"): physics ends exactly on the last key - push search ("Tìm cú đổ"), goal drive after landing, residual blend; Die test version goal_v1 (2 keys) on the Die page with settings seeded in db. doc p5 section 17.
Live-page lesson (2026-10-26): db snapshot data is FROZEN on claude.ai - copy before mutating (ANIM.phys from applyRemote broke add/remove impact); test anything touching db on the live artifact (Browser pane can open claude.ai/artifact links; iframe errors only visible via the page status line).
