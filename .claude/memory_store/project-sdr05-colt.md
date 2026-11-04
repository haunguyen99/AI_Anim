---
name: project-sdr05-colt
description: SDR05 map Western cowboy + Colt Python (GSDR-1407): Base (mesh) + Idle/Shoot/Reload anim-only FBX pushed TungNV_Dev 17b6b95f, Base T-pose 1a974413 2026-11-04
metadata:
  type: project
---

SDR05 = G-DieLoop map Western, cowboy `MC_char_map5`, Colt Python (Khải's model, 1.25×) replacing the Gatling. Job `work/shoot_die_repeat/sdr05_colt/`.
- Shoot p1 (9 F, head locked forward per GD) and Idle = P0 10 F: user approved 2026-11-04.
- Reload p1 (30 F; events OnReloadStart F5, OnReloadAnimationComplete F28; loader slingshot_2 scale 1 at F12–F22, baked in the pose): user approved 2026-11-04 ("xuất FBX đi").
- `export_fbx.py --clip shoot|idle|reload` builds on the team rig file: Gatling joint1/3/5_M → slingshot_0 (Wrist_R) / slingshot_1 / slingshot_2 (Wrist_L), mesh name MC_char_map5_VK kept, holster VK01 removed. `unity_meta.py <Western dir>` writes all 3 .meta (keeps guids).
- 2026-11-04 user: "chưa bỏ mesh ở file anim" → Idle/Shoot/Reload are skeleton + anim only; mesh + Colt rig in `SDR05_MC_Base.fbx` (`--clip base`), anim metas copy the avatar from Base (like SDR06). All 8 files (FBX + meta) pushed to TungNV_Dev 17b6b95f; Base re-exported in T-pose (= bind, user) pushed 1a974413; local Unity checkout = origin. Not yet opened in Unity Editor; dev must point the controller/prefab at the new clips.

**Why:** next asks are likely a Unity check or dev questions (questions_hc.md items unsent).
**How to apply:** read `analysis.md` + `director_log.md`; see [[feedback-sdr-git-branch]], [[project-g-dieloop]].
