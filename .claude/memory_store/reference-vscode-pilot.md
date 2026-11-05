---
name: reference-vscode-pilot
description: "Team can use Claude Code in VS Code (since 2026-11-05) — setup via tools/setup_vscode.ps1 + docs/vscode_pilot.md §7; endpoint LAN http://192.168.10.29:40741 or public llmpro; key only in each user's ~/.claude/settings.json"
metadata:
  node_type: memory
  type: reference
  originSessionId: 6856e308-2578-4709-9830-2d98e3bd0715
  modified: 2026-11-05T07:40:57.670Z
---

VS Code + extension anthropic.claude-code works on this repo with the same CLAUDE.md/skills/memory/.mcp.json as the desktop app (lead tested 2026-11-05: all 6 project MCP servers Connected). Missing in VS Code: Artifact, in-app browser, side sessions → those jobs stay in the desktop app. Team decision: run both in parallel.

New user / new machine (user asked 2026-11-05 to make this shared so others install too):
- `powershell -ExecutionPolicy Bypass -File tools/setup_vscode.ps1` = check only; `-Install` = winget VS Code (user scope) + extension; `-Endpoint lan|public` switches ANTHROPIC_BASE_URL in ~/.claude/settings.json (backs up first, tests LAN reachability, never writes the key).
- Key from the lead goes only into the user's own ~/.claude/settings.json (template in docs/vscode_pilot.md §7); never commit or post it.
- Then `tools/claude_memory.py restore`, open `code "E:\AI Animation"`, `/` → MCP → enable servers.
- Endpoint: LAN `http://192.168.10.29:40741` (from dev Nguyễn Đức Tùng, ~15–20% faster per call than `https://llmpro.horusjsc.com`, which goes via Cloudflare HKG). LAN only — off-site use `-Endpoint public`. Connection errors → check this first. Restart VS Code / app after switching.
- Lead's machine switched to LAN 2026-11-05, backup ~/.claude/settings.json.bak_llmpro_20261105.
- Reply style: VS Code answered "like for devs" → output style `Anim Team` (.claude/output-styles/anim-team.md, keep-coding-instructions) turned on team-wide in project .claude/settings.json (`"outputStyle": "Anim Team"`, user chose "Cả team (git)" 2026-11-05); applies to desktop sessions in this repo too. Change tone by editing that file.
- Sub-sessions in VS Code: none built in; design draft docs/vscode_subsessions_design.md (claude --bg / agents / --resume), awaiting approval. Colleague guide: docs/huong_dan_vscode_claude.md.
