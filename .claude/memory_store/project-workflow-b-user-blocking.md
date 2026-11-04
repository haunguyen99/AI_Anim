---
name: project-workflow-b-user-blocking
description: "Workflow B (updated 2026-10-31) - AI auto-rigs the character in Frolvy, user keys blocking there, AI exports FBX into Studio, then analysis/breakdowns/polish/FBX as before"
metadata:
  node_type: memory
  type: project
  originSessionId: ace47192-5f99-483f-92d3-a1afe047933f
  modified: 2026-10-31T02:49:47.576Z
---

User 2026-10-31: "Ở quy trình B AI sẽ Rig trên phần mềm Frolvy để cho người dùng keypose. Khi đã key xong AI sẽ Export bloking sang Studio để làm tiếp".
They picked Frolvy's own auto-rig (Rig Builder, Human05 template), FBX as the hand-off format, and later steps unchanged but done in Studio instead of Pose Lab.
Steps: F1 AI rigs in Frolvy (gate: rig approval) → F2 user keys → user says "key xong" → F3 AI exports FBX, renames bones via bone_map.json, loads into Studio (gate: "khớp file") → analysis → fix → breakdowns → weight → polish → FBX into the team's own file.
If the team already hands over an FBX blocking (original 2026-10-23 version, sample clip Gaygor Attack 50 Blocking), skip F1–F2.
Open as of 2026-10-31: Frolvy skeleton ≠ team skeleton (fit Human05 joints onto team joints, retarget by world rotation); Studio cannot yet import FBX keys (only mesh/skeleton/skin).

**Why:** the user wants to pose the blocking themselves in a real rigging/anim app; AI does the rig and the finishing.
**How to apply:** details in `.claude/skills/animation/knowledge/details/user_blocking.md` ("Bản 2026-10-31"); Frolvy via [[reference-frolvy-mcp]]; see [[project-studio]], [[ai-does-user-approves]].
