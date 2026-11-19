---
name: project-endless-kicker
description: "Endless-kicker (registered 2026-11-04) — hero Windy (wind mage + staff), Unity E:\\endless-kicker branch v1, team Maya files E:\\tvc_source\\3D ANIM\\EndlessKicker, GDD = FDD Hero Windy Google Doc"
metadata:
  node_type: memory
  type: project
  originSessionId: 181aa7b0-a060-4850-9efb-262106184560
  modified: 2026-11-04T08:58:39.417Z
---

User 2026-11-04 opened project "Endless-kicker": Unity `E:\endless-kicker` (repo git.horusent.com/beachwar/endless-kicker, branch `v1`, team working copy — never commit/push unasked), source `E:\AI Animation\Assets\Endless-kicker\` (Hero_Windy.fbx), GDD = FDD Hero Windy https://docs.google.com/document/d/1cnYhJKdC9QA9R1I_KRN8q3xsfI3FFqNlv5KRwUN8xfY (readable without login via `/export?format=txt|html`; summary + ref links in `work/endless_kicker/gdd/windy_fdd.md`).

- Game: one hero stands fixed at the centre of the defence area, auto-attacks. Windy anims in FDD: Attack (staff head forward), Skill1 Wind Cyclone (staff forward → spins), Skill2 Hunting Tornado (float up, spin staff once), Skill3 Wind Collapse (Charge: arms spread, fly up, staff floats in front; Burst: grab staff, slam down → idle).
- Game screenshot (user 2026-11-04): hero ~60–70 px tall on a ~1020 px portrait screen (~6%), centre of a stone ring, slimes from all sides → only big shapes read (staff direction, arm spread, spins, cape); fingers/breath invisible.
- Model: `body3` skinned to 53 joints + `staff` skinned 100% to `joint112` (directly under `root`, so it can fly free); AdvancedSkeleton names; Unity Generic, `Take 001`, 30 fps.
- Team ALREADY made all 5 Windy anims in Maya 2026-10-31 (`Hero_Windy/Anim/*.ma`, FBX in `Hero_Windy/Fbx/`: Idle 0–40, Attack 0–33, Skill1 0–30, Skill2 0–39, Skill3 0–52); not in Unity yet. Unity hero anims live in `Assets/_Game/Animation/Hero/<Hero>/`.
- Home: project id `endless_kicker`, character `Windy`; AI job data → `work/endless_kicker/<job>/` per [[project-work-per-project]]; progress doc `work/endless_kicker/README.md`.
- Open question: Home project `infinite_defense` (hero Ninja, tower defense) may be this same game — tvc_source/EndlessKicker has Hero_Ninja. Asked user 2026-11-04.

**Redo from scratch (user 2026-11-04 "Tôi muốn làm lại mới hoàn toàn"):** 5 new Windy anims, team Maya anims NOT used. User chose: Frolvy, AI keys everything; AI-proposed lengths (Idle 60F loop, Attack 24F fire F9, Skill1 36F launch F24, Skill2 45F summon F31, Skill3 72F one clip Charge+Burst, explode F46 = 1.5 s); Skill2 whole body spins 360° with staff. Ref videos from FDD drive links in work/endless_kicker/ref/. Analyses v2/v2.1 in work/endless_kicker/windy_*/analysis.md, director 2 rounds; APPROVED 2026-11-04 (tag endless-windy-analysis-approved; Skill1 spin in a vertical plane on the right, Skill3 staff floats in front, game speed-scales Attack; in-game attack interval 0.79 s = 24F).
- Rig Frolvy built 2026-11-04 (work/endless_kicker/rig/build_windy_rig.py): scene C:\Users\HLC_2021\Documents\Frolvy\EndlessKicker\Hero_Windy_rig.fv (Frolvy lets AI scripts write only in Documents\Frolvy + %TEMP%; copy to E:\tvc_source\3D ANIM\EndlessKicker\Hero_Windy\Frolvy). Staff: joint112 follows CTL_Staff (right hand); CTL_StaffWorld = world target + staff_bake_world for free flight (constraint-weight switches do not work in Frolvy 0.9.36). Export test 0 cm vs team FBX. Waiting rig approval.

**How to apply:** Maya is unusable here, so work in Frolvy on the team FBX like [[project-g-lumbercity]] (Generic: keep team names/hierarchy, export joints + anim only).
