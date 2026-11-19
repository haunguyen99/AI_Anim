---
name: project-runner6-pyromancer
description: Runner6 HERO_PYROMANCER - Frolvy rig_v2 (2026-11-13); anims approved IdleShop v5, Idle_Game v3, Showcase v21 (150F, 2026-11-14); files in Documents/Tungtq_TraineeSpine/Runner6/HERO_PYROMANCER
metadata:
  type: project
---
Runner6 game, hero Pyromancer (chibi wizard, cm). Source scene `Documents/Tungtq_TraineeSpine/Runner6/HERO_PYROMANCER/HERO_PYROMANCER_game.fv` (had the Ranger team skeleton + Ranger meshes as reference). Rig done 2026-11-13: `HERO_PYROMANCER/Rig/HERO_PYROMANCER_rig.fv`, `Pyromancer_Simple.fvpicker`, `Hero_Pyromancer.fvfit`; working copy `Documents/Frolvy/Runner6/`. Scripts `work/runner6/hero_pyromancer_rig/`.

User asked: drop old inbetween (Part) joints, Global on head / both shoulders / chest, twist on upper arm + forearm. Done: shoulders Global (fit flag), head = space World, twistJoints 2 on Shoulder + Elbow. **Chest Global not available in Frolvy 0.9.59** (Spine module) - waiting on the user.

**Why:** next anims for this hero start from this rig. **How to apply:** open the Rig file, not the _game file; re-skin with skin_pyro.py if the mesh changes. See [[frolvy-feedback-simple]], [[reference-frolvy-mcp]].

Anims (all on rig_v2, files copied to `HERO_PYROMANCER/`): IdleShop approved v5 (120F), Idle_Game approved v3 (floating), **Showcase approved v21 (2026-11-14, 150F, F0 = F150 = IdleShop key 0)** - retarget of Brand "Laugh" (modelviewer.lol id 63000, ref/brand_all_anims.glb) + 20 user rounds; history + lessons in `work/runner6/hero_pyromancer_showcase/analysis.md`. Not exported to FBX yet.

**FBX export 2026-11-16** (user asked for all latest versions in one folder): `Tungtq_TraineeSpine/Runner6/HERO_PYROMANCER/export/` = Hero_Pyromancer_game.fbx + Hero_Pyromancer_shop.fbx (Base, T-pose, mesh + DEF + `root`) and _IdleGame (v3), _IdleShop (v5), _Showcase (v21), _Attack (v19), _Cast (v6) anim-only with `root`, no Dummy (user: "Bỏ Dummy"). Shop mesh skinned in `Frolvy/Runner6/HERO_PYROMANCER_rig_shop.fv`. Pipeline `work/runner6/pyro_export.py` (details: knowledge export.md "Pyromancer").
