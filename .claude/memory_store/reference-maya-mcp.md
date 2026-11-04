---
name: reference-maya-mcp
description: Maya 2024 MCP server `maya` in tools/maya_mcp; needs listener started inside Maya (127.0.0.1:7022)
metadata:
  type: reference
---

User asked 2026-10-27 to connect MCP with Maya 2024. Server `maya` in `.mcp.json` → tools/maya_mcp (uv). Maya side: `maya_side/maya_mcp_listener.py`, start() in GUI Maya, start(block=True) in mayapy. Tools maya_exec/eval, scene_info, ls, hierarchy, get/set attrs, set/get keys (tangent step for blocking), open/save, import/export FBX, snapshot, launch.

The user's Documents/maya/2024/scripts/userSetup.py imports a missing `maya_secure_system` (errors at startup; not ours, left untouched). Maya is a new tool next to Home Labs + Spine; see [[project-no-blender-cascadeur]].
