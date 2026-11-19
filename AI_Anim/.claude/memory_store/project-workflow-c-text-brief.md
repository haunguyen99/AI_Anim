---
name: project-workflow-c-text-brief
description: Workflow C added 2026-10-24 - clips with no ref and no blocking, only a short text request; design + timing chart first, 10% poses in Pose Lab, then workflow B
metadata:
  type: project
---

User 2026-10-24: "thêm một nhánh nữa là những anim chưa có ref chưa có blocking, chỉ có yêu cầu đơn giản".
C1 merged intake → C2 design doc + timing chart (gate) → C3 storytelling poses 10% on Pose Lab, user may edit there (gate)
→ C4 blocking 25-50% (gate) → continue [[project-workflow-b-user-blocking]] from step 3. Spec: `.claude/skills/animation/knowledge/details/text_brief.md`.
First full run 2026-10-24: Gaygor Hit 32F (work/boss_gaygor/gaygor_hit) - design B → k10 → b50 → b75_v2 → polish_v1..v7 (v7 approved "oki rồi đấy", tag gaygor-hit-polish-v7-approved) → FBX via work/boss_gaygor/gaygor_hit/export_fbx.py (any length from the 68F team source). Polish rounds were all secondary motion: head jitter, stiff arms, jerky mace, then mace overlap/weight (timing_spline.md: inertia-layer, prop-path-smoothing, prop-overlap-weight).

**Why:** many game clips (hit, death, taunt) arrive as a one-line request; SDR Attack (no ref) took ~17 review rounds mostly on F1 stance + recovery timing.
**How to apply:** route in `/new_clip` when the brief has no ref file; lock start/end pose and the timing chart with stills before any motion.
