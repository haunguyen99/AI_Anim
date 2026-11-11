---
name: reference-paseo
description: "Paseo desktop (agent manager) runs Claude via provider llmpro → LAN endpoint; config ~/.paseo/config.json, CLI resources/bin/paseo.cmd"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1ed9c221-1d15-4c52-85cb-295054664cac
  modified: 2026-11-09T04:05:07.484Z
---

Paseo 0.15.3 (Electron app, `%LOCALAPPDATA%\Programs\Paseo`, CLI `resources\bin\paseo.cmd`) set up 2026-11-09 to run Claude through the team proxy.

- Provider `llmpro` in `~/.paseo/config.json` → `agents.providers.llmpro`: `extends: "claude"`, env `ANTHROPIC_BASE_URL=http://192.168.10.29:40741` (LAN, user's choice) + `ANTHROPIC_AUTH_TOKEN` = same LAN key as `~/.claude/settings.json`, models `claude-opus[1m]` / `claude-sonnet[1m]`.
- Built-in provider `claude` is overridden the same way (command + env + models) so picking plain "Claude" in the app also works; without it the app shows "Unavailable".
- `command` must be a string ARRAY (`["C:\\Users\\Admin\\.local\\bin\\claude.exe"]`), not `{mode, argv}` — wrong shape makes Paseo drop the provider ("Provider override matches no registered provider").
- No `claude` on PATH on this machine: `~/.local/bin/claude.exe` is a copy of the VS Code extension's native binary (2.1.318); recopy after big Claude Code updates.
- New/changed providers need `paseo.cmd restart` (or app restart); `reload` only applies overrides to existing providers. Check: `paseo.cmd provider ls` → llmpro `available`; test: `paseo.cmd run "Reply OK" --provider llmpro`.

Related: [[reference-vscode-pilot]]
