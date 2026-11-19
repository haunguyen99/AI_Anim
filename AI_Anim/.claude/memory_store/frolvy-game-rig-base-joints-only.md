---
name: frolvy-game-rig-base-joints-only
description: "Game rigs in Frolvy - base DEF joints only: no helper set (PRT/HLP/MUS), no twist/bendy, skin only to DEF joints"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 00fd2db5-c42c-44f1-8524-281e9fd9225a
  modified: 2026-10-31T04:50:40.607Z
---

Rigs are for games (Unity Humanoid export): build with only the base skeleton.
- Before Build/Rebuild Rig: `api.set_helper_set(False)`, `api.set_bendy_limbs(False)`, and `twistJoints = 0` on the fit joints.
- Bind skin with DEF_ joints only (skip End/Heel/FootSide/Finger4/Root; props like Weapon/Arrow only on their own rigid meshes).
- Keep at most 4 influences per vertex, drop weights < 1%, and keep each limb/finger's weights off other parts (no arm/leg weight on the torso core, no finger weight on other fingers).

**Why:** user, 2026-10-31 (Bastion): "Chỉ bind skin bằng joint DEF", then "tạo rig cho game nên sẽ không cần các joint đó, chỉ cần joint base" — the helper set I had turned on unasked (copied from Gragas) added 126 PRT/HLP/MUS joints and pulled the torso with the limbs.

Before any Rebuild Rig, zero every control (autoSnap off while switching): Rebuild bakes the current pose into the _grp/_follow offset groups (2026-10-31 Bastion: posed Pelvis got baked, rig stayed tilted with all controls at 0). Rebuild sometimes drops custom translate wires (wire_DEF_*_tx/ty/tz "add" nodes) and custom joint labels (it did once, kept them the next time) — check and redo after; never delete wire_DEF_Root_M_* (Rig Builder's own).

Thumb axes: Rig Builder leaves fit joints world-aligned, which is wrong for the thumb. Fix on the fit: per thumb joint X down the bone, Z = X x (dir to MiddleFinger1), `set_joint_orient` then zero the rotate channels (Frolvy auto-counter-rotates) and recompute child translates; after Rebuild update the translate-wire constants of DEF_ThumbFinger* and flip the sign of fng_c_DEF_ThumbFinger{1,2,3}_{L,R} so curl/Fist closes the thumb (check: tip gets closer to MiddleFinger1). Switch parents (arm->CTL_Wrist, spine->CTL_Chest, legs->CTL_IKAnkle) are reset by Rebuild too.

After a Rebuild that moved fit joints, Rebuild leaves the control pivots (CTL_*_grp) at the OLD joint spots (2026-10-31: Neck, Head, Scapula, thumbs) - compare each control's world position with its DEF joint and move the _grp (keep the curve's world shape).

**How to apply:** never turn on helper set, bendy limbs or twist joints unless the user asks. After Rebuild Rig, delete mirrored one-side props (Weapon_L etc.) and their dead wire_ nodes. Related: [[frolvy-fit-controls-after-build]], [[frolvy-rig-root-at-origin]].
