---
name: reference-linux-machine
description: Linux machine (tungtq, 2026-11-18): Python env ~/.venvs/ai_anim replaces .venv/Scripts/python.exe; no pip/uv/Spine CLI; in-app browser lost WebGL when the Claude app auto-disabled GPU (fixed 2026-11-18)
metadata:
  node_type: memory
  type: reference
  originSessionId: 05056dac-2837-4c5f-bba8-2f28a41463bf
  modified: 2026-11-18T05:02:41.573Z
---

Project path on this Linux machine: `/media/tungtq/New Volume/Claude2Danim/AI_Anim` (memory slug `-media-tungtq-New-Volume-Claude2Danim-AI-Anim`; restore with `python3 -I tools/claude_memory.py restore`).

- `.venv/Scripts/python.exe` in CLAUDE.md / skills is the Windows venv. Here use `~/.venvs/ai_anim/bin/python -I` (made 2026-11-18 from Blender's bundled Python `~/Applications/blender-5.3.0-linux-x64/5.3/python/bin/python3.13 -m venv`, because system python3 has no pip / ensurepip; installed requirements.txt + psd-tools + scipy). Plain `python3 -I` works for stdlib-only tools (claude_memory.py, spine_live/ensure_server.py, spine_live_recent.py).
- No `uv` → MCP `spine` fails to start; no Spine editor / CLI → cannot import JSON to `.spine` or export here (user does it in Spine, or on the Windows machine).
- No WebGL in the built-in browser was caused by the Claude app itself: 2026-11-16 14:51 its GPU process was killed 20× in <0.1 s (with the network process, SIGTERM = likely logout/shutdown, not a GPU fault) -> app auto-wrote `isHardwareAccelerationDisabled` + `isHardwareAccelerationAutoDisabled: true` in `~/.config/Claude/claude_desktop_config.json` (GPU process ran `--use-gl=disabled`; machine GPU NVIDIA RTX 3050, driver 595.99 OK). User OK'd 2026-11-18: set both false (backup `claude_desktop_config.json.bak_gpu_20261118`), restart app -> FIXED, verified 2026-11-18: WebGL on (ANGLE, RTX 3050), Spine Live draws Char4. If it comes back, re-check the two keys. Check: JS `document.createElement("canvas").getContext("webgl")` in the pane, or `ps` gpu-process args.
- (before the fix) Built-in browser (Claude desktop on Linux) reports no WebGL → Spine Live page loads but the player cannot draw ("browser does not support WebGL"). Self-check rigs with `tools/spine/render_spine.py` instead; opening Spine Live in Chrome needs the user's OK ([[spine-live-in-claude-only]]).
- Spine Live server must be started with the venv python (`~/.venvs/ai_anim/bin/python -I tools/spine_live/ensure_server.py`; it relaunches with sys.executable): started with system python3 it runs but snap / mesh / weight / thumbnails fail (HTTP 500, no numpy in server.log). Fixed 2026-11-18 by killing the python3 server and relaunching.
- Frolvy here: see [[reference-frolvy-mcp]] (Linux section).
