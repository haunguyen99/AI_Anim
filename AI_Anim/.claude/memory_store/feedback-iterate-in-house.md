---
name: feedback-iterate-in-house
description: "User wants iterative try-measure-improve and algorithm proposals; moved from in-house three.js tools to Blender via MCP (2026-10-19)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7d2b80c9-f2b6-4906-8dd7-0a234b58ddaf
  modified: 2026-10-19T06:58:30.675Z
---

User (2026-10-19) first wanted everything keyed in our own tools (three.js, no other 3D app), then rejected the results ("Chất lượng không chấp nhận được", "Kết quả chưa đạt yêu cầu") and asked to key in Blender via MCP instead. Still values "thử sai rồi rút kinh nghiệm" and algorithm proposals.

**Why:** In-house keying/silhouette fitting gave mechanical, jittery results without a real rig or graph editor; Blender lets the user watch and hand-tweak the same file.
**How to apply:** Follow docs/pipeline_v2.md (Blender-first: brief+timing → ctrl rig → stepped blocking → spline/NLA layers → QA + playblast → export), with user review gates. Report each iteration with metric + lesson. See [[reference-blender-mcp]], [[project-goal]].
