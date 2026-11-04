---
name: project-g-dieloop
description: "G-DieLoop = Shoot Die Repeat (SDR) — GDD Google Sheet, Unity E:\\Horus\\shot-die-repeat, team work files E:\\tvc_source\\3D ANIM\\G-ShotDieRepeat (registered 2026-11-02)"
metadata:
  node_type: memory
  type: project
  originSessionId: c10a6018-590e-43cd-9e40-5cb49cc282bc
  modified: 2026-11-02T09:04:49.069Z
---

User calls the project **G-DieLoop** (2026-11-02); it is the same project as Shoot Die Repeat / "Die Loop" GDD
([[project-shoot-die-repeat]], [[project-sdr01]], [[project-sdr-map06]]). Our data stays in `work/shoot_die_repeat/`.

- GDD: https://docs.google.com/spreadsheets/d/1ZQNHEFGnuMuG-Zv1jkJvdGothcTo01cbc1osArCU7RU/edit (local copy from
  2026-10-28 in `work/shoot_die_repeat/gdd/`; re-download when asked about new anims).
- Unity: `E:\Horus\shot-die-repeat` (push rules: [[feedback-sdr-git-branch]] — branch TungNV_Dev only).
- Team work files (Maya .ma/.mb + FBX): `E:\tvc_source\3D ANIM\G-ShotDieRepeat` — folders `MC_char_map1` (1 FBX),
  `Map01` (23 ma, 26 fbx), `map02`..`map06`.

**Why:** user opened a dedicated chat section for G-DieLoop tasks and gave these three locations as the sources.
**How to apply:** in that section, read source scenes from tvc_source (don't write there unless asked), save our work in
`work/shoot_die_repeat/<job>/`, export/push to the Unity repo per the SDR rules.

2026-11-02: rigged new zombies EN_zom1_map4_v2 + EN_zom1_map5_v2 (Main_Fix_Form) by script (`work/shoot_die_repeat/zom_v2/`, user chose "Chỉ FBX skin bằng script"), Humanoid .meta from old rigs via make_meta.py, pushed to TungNV_Dev cb6cd005 (Animations/Map04, Map05). Not yet confirmed in Unity Editor.
Then zom2 map4/map5 v2 (merged-body branch of rig_v2.py, Director round 2 Duyệt) + zom1 hat-brim fix pushed TungNV_Dev 7ce8ab89.

2026-11-03: Tùng renamed Unity map folders by name (pulled TungNV_Dev 20064b38): Map01→Jungle, Map02→Roma, Map03→Mayah, Map04→Pirate, Map05→Western, Map06→London (e.g. Assets/_Game/Animations/Western, 3D/Model/Western). Helper `tools/sdr_paths.py` maps old numbers → new names; use it for export/push paths.

2026-11-03: Khải (thread "Map London"): rig zom2 London had no texture → rebound EN_zom2_map6 rig onto textured model 3D/Model/London/EN_zom2_map6.fbx (work/shoot_die_repeat/zom2_map6_rebind/rebind.py, export/EN_zom2_map6.fbx; pushed TungNV_Dev f47ee41c, Animations/London/EN_zom2_map6.fbx, .meta unchanged; Khải tagged in G-DieLoop room). DONE (user "done task này"). zom1 map6, MC map6 and the 4 zom v2 checked OK (mesh+UV = Khải models, material → M_Colorpalette).
