---
name: reference-spine-mcp
description: Spine 2D MCP server (`spine`) moved from E:\SpineAI into tools/spine_mcp; Spine projects in work/<game>/spine/<anim>
metadata:
  type: reference
---

Spine 2D (editor 4.2.43) MCP server, integrated 2026-10-26 (user: "tích hợp cả cái này vào AI_Anim: E:\SpineAI"): code `tools/spine_mcp/`, declared as `spine` in root `.mcp.json` (`uv run --directory "E:\AI Animation\tools\spine_mcp" spine-mcp`, env SPINE_EXE, SPINE_VERSION). Tools: Spine CLI export/import/pack + skeleton JSON edit (bone_*, slot_*, animation_*, keyframe_*). Workflow: export .spine → JSON, edit, import to a NEW .spine (never over the original). Project: `work/pirate_goldrush/spine/HandTut/` (`build_handtut.py`). Original `E:\SpineAI` left in place. Needs a new session to load the server. Skill `/spine2d` (.claude/skills/spine2d) holds the Spine workflow, rig/anim rules, export settings (editor-2.json, .atlas.txt, no PMA; end pause = event) and lessons; preview `tools/spine/render_spine.py`. User is also a 2D Spine animator taking orders from GD. Related: [[project-map]].
