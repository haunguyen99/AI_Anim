---
name: project-runner-hybrid
description: "Runner_Hybrid (CasualRunner) — Unity D:\\Project\\runner-hybrid, work files D:\\tvc_source\\3D ANIM\\CasualRunner\\Anim\\anim_hero\\Hero_Nova, GDD Lark Run 6 tab Anim & VFX; Hero NOVA 5 clips, model not rigged"
metadata:
  node_type: memory
  type: project
  originSessionId: eed79046-121f-402b-bffa-a6ee9ebbefb5
  modified: 2026-11-13T04:01:43.189Z
---

User 2026-11-13 opened project Runner_Hybrid: GitProject `D:\Project\runner-hybrid` (Unity, branch Runner666, team repo — never commit/push without asking), save work files in `D:\tvc_source\3D ANIM\CasualRunner\Anim\anim_hero\Hero_Nova`, GDD Lark https://horusrun.jp.larksuite.com/sheets/H26WsvF3ChKdVbte2w0jffv1pJg?sheet=Ba6wSS (tab Anim & VFX, public view).
- Hero NOVA (rifle): NovaIdleShop, NovaShowcase, NovaIdleGame, NovaAttack, NovaCast. GDD rule: all ingame attacks/casts build on Idle ingame (floating).
- Nova FBX (game/shop/vk) = mesh only, no joints → rig first. Sibling heroes (Ranger, Druid) use a 49-joint AdvancedSkeleton set with WeaponCtrl1_L/R, cloth1-3_M; anim FBX joints only, Generic, Take 001.
- Read Lark sheet without login: GET /space/api/v3/sheet/block?token=…&block_token=B&schema_version=9&blockIds=B (block id from client_vars snapshot.blocks), gunzip, pull UTF-8 strings.
- Details + clip table: work/runner_hybrid/README.md; Home project id `runner_hybrid`, character `Nova`.

**How to apply:** start every Nova clip from the README; rig per [[rig-in-studio-not-maya]] / [[frolvy-game-rig-base-joints-only]] after asking the user which tool.
