---
name: feedback-update-knowledge
description: "After every animation task, proactively update the per-type knowledge base in the skill (knowledge/details/*.md; CORE.md only for every-clip rules)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7d2b80c9-f2b6-4906-8dd7-0a234b58ddaf
  modified: 2026-10-20T04:14:33.064Z
---

The user (animator lead) will coach many animation types (idle, attack, walk/run, hit, death, skill...). Since 2026-10-22 (user: "gom lại thành phần cốt lõi ngắn kèm mục lục; chi tiết chỉ đọc khi cần") knowledge is `.claude/skills/animation/knowledge/CORE.md` (≤ ~6 KB, every-clip rules) + `INDEX.md` (one line per section) + `details/<topic|type>.md`. Read CORE + INDEX before a clip, open a details section only when the task touches it. After EVERY task update the right details section without being asked (feedback quote -> principle, measured bug -> fix, approved params); add an INDEX line for a new section; touch CORE only for a rule that applies to every clip, keeping it small.

**Why:** user asked on 2026-10-20: "phân loại kiến thức theo mỗi loại anim... sau mỗi task chủ động cập nhật kiến thức nhé!"
**How to apply:** include the knowledge update as the last step of every task's plan; mention briefly what was added. Related: [[feedback-review-listening]], [[project-gaygor-idle-front]].
