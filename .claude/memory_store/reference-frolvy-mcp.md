---
name: reference-frolvy-mcp
description: "Frolvy (frolvy.com, Maya-like rig/anim app, C:\\Program Files\\Frolvy) is driven by MCP server `frolvy` = Frolvy-mcp.exe → 127.0.0.1:9877; app must be open"
metadata:
  node_type: memory
  type: reference
  originSessionId: ace47192-5f99-483f-92d3-a1afe047933f
  modified: 2026-11-11T03:46:49.036Z
---

Frolvy 0.9.54 Beta seen 2026-11-11 (was 0.9.36 on 2026-11-04, so bug notes tagged 0.9.36 in the skills may be outdated; `get_scene_info` has no file path: read the open scene + unsaved `*` from `Get-Process Frolvy` MainWindowTitle, recent files in `~/Documents/Frolvy/recent_scenes.json`; MCP OK on 9877. After an update Claude must reconnect MCP: installer kills the old Frolvy-mcp.exe), Windows rig + anim app (Rig Builder with Human05 template, skin/paint weights, IK/FK, Tool Picker, FBX/glTF export baked per frame, MP4 playblast).
MCP: `C:/Program Files/Frolvy/Frolvy-mcp.exe` (stdio) bridges to port 9877 that the running app opens; registered as `frolvy` in `.mcp.json` 2026-10-31.
Tools: get_scene_info, get_node_info, execute_code (Python, `fv`/`api` object, 320 calls, one undo step per run), find_api, get_viewport_screenshot, get_app_screenshot, list_panels, show_panel, reset_workspace, undo, redo.
API docs: https://frolvy.com/#api (SPA, read with the browser). Sample scripts: C:\Program Files\Frolvy\scripts (human_rig.py, make_biped_fit.py, transfer_weights.py).
Used by [[project-workflow-b-user-blocking]].

Parallel sessions (user 2026-11-03 "Sao không chạy song song"): one Frolvy = one open scene, so two sessions must not share a port. Env `DCC_MCP_PORT` sets the port for both Frolvy.exe and Frolvy-mcp.exe: start a second app with `$env:DCC_MCP_PORT="9879"; Start-Process "C:\Program Files\Frolvy\Frolvy.exe"` and drive it with `python tools/frolvy_port.py 9879 script.py` (stdio MCP client). Check `netstat -ano | grep 987` first: a port already LISTENING belongs to another session. The bridge cuts a call at 180 s but the code keeps running in the app.

If `/mcp` says "No MCP servers are configured" or the `frolvy` tools are missing even though Frolvy is open (port 9877 LISTENING): the cause is `.claude/settings.local.json` (git-ignored, per machine) — its `disabledMcpjsonServers` listed all project servers incl. `frolvy` (found 2026-11-11, set 2026-11-06). Fix by editing that file: remove `frolvy` from `disabledMcpjsonServers`, add it to `enabledMcpjsonServers` (user said "tự kết nối đi" = do it yourself); verify with `claude mcp get frolvy` (✔ Connected). The running session may still need `/mcp reconnect frolvy` or a new session to see the tools; meanwhile `tools/frolvy_port.py 9877 script.py` works.
