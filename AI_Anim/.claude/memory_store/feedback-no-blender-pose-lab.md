---
name: feedback-no-blender-pose-lab
description: "User 2026-10-23 \"Tôi cần bỏ hẳn blender\": Pose Lab work (Walk) must not use Blender at all, not even headless behind the scenes"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3ccc149f-3d11-4ff9-8b77-1bfb6c40469c
  modified: 2026-10-23T03:08:22.327Z
---

When the user asked to block Walk keys from ref and I started headless Blender silhouette fits, they asked "Sao vẫn
dùng blender vậy" then "Tôi cần bỏ hẳn blender".

**Why:** they want Pose Lab to be the whole tool; a hidden Blender step keeps the dependency they are trying to drop.
**How to apply:** for clips on Pose Lab do fitting, posing, checks and export in the page (three.js) — drive it via the
browser pane, push keys to the page db with ArtifactData. Existing glb/json models already exported are fine to reuse.
Related: [[project-poselab-fbx]], [[feedback-no-blender-for-cascadeur]].

2026-10-23 later: user "Ngắt kết nối với blender đi" -> blender / blender_attack added to disabledMcpjsonServers in
.claude/settings.local.json (git-ignored) and this session's two mcp-for-blender bridges stopped (other sessions' kept).
Do not re-enable them unless the user asks.
