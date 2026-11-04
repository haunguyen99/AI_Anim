---
name: project-goal
description: "E:\\AI Animation project goal and chosen approach — Claude eye-keys user's 3D character from synced multi-view reference videos of that same character, in headless Blender"
metadata:
  node_type: memory
  type: project
  originSessionId: 7d2b80c9-f2b6-4906-8dd7-0a234b58ddaf
  modified: 2026-10-19T02:26:40.962Z
---

Goal: AI looks at reference and keys the user's 3D model to reproduce the motion. User communicates in Vietnamese.

Direction as of 2026-10-19 (changed same day):
- MediaPipe dropped (moved to legacy/mediapipe). User: "đi theo hướng tự key".
- Refs = synchronized multi-view videos (standard fixed views front/back/left/right), AI-generated or hand-drawn, showing the SAME character as the 3D model.
- Claude keys by eye (user's explicit choice over an optimizer): keys.json poses (aim/rot in character space x=right,y=forward,z=up) → headless Blender → overlay renders per view → Claude compares and fixes.
- User's rigs are custom; sample Assets/Boss_Gaygor uses AdvancedSkeleton naming (Root_M, Hip_L, Shoulder_L = upper arm, Scapula_L = clavicle, separate root "Weapon" bone).

**Why:** User's answers to setup questions.
**How to apply:** Reply in Vietnamese; don't reintroduce pose-estimation models unless asked; keep Claude-in-the-loop eye keying; FBX→Unity round-trip still unverified.
