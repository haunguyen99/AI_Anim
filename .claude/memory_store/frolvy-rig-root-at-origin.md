---
name: frolvy-rig-root-at-origin
description: "Frolvy root joint: the default (0.9.22+) puts Root at 0,0,0 with a Pelvis child, but for game rigs the user wants Root_M to BE the hip joint (AdvancedSkeleton style)"
metadata:
  node_type: memory
  type: project
  originSessionId: 00fd2db5-c42c-44f1-8524-281e9fd9225a
  modified: 2026-10-31T04:04:08.578Z
---

Since Frolvy 0.9.22, Rig Builder's Create Root makes joint "Root" at the origin (label root) and the hips go in a child "Pelvis". On 2026-10-30 the user asked for that layout on Gragas; on 2026-10-31 (Bastion, game rig) they asked the opposite: "lấy joint Root_M là joint của hip" - Root at the hips, no Pelvis, Spine1/Hip/HipPad1 directly under Root. Build then gives DEF_Root_M at the hips (Unity Hips), CTL_Main on the floor, CTL_Root_M (outer, moves the body) and CTL_RootX_M (inner, hips) both at the hips.

**Why:** game export: the hip joint is the skeleton root, as in AdvancedSkeleton.

**How to apply:** for new game rigs put Root at the hips with label root and no Pelvis joint; ask if unsure. To convert an existing fit: move Root to the Pelvis position, `api.remove_joint("Pelvis")` (it keeps the children's LOCAL translates, so reset each direct child's translate to old_world - root_world) and set Root's label back to root; save weights first and map DEF_Pelvis_M -> DEF_Root_M after Rebuild (the skin keeps pointing at the deleted joint). Frolvy installs at C:\Program Files\Frolvy. Related: [[frolvy-game-rig-base-joints-only]], [[frolvy-fit-controls-after-build]].
