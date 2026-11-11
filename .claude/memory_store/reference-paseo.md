---
name: reference-paseo
description: Paseo desktop (agent orchestrator) runs Claude Code CLI through the company llmpro gateway; how it is configured and the gotchas
metadata:
  node_type: memory
  type: reference
  originSessionId: ee4a0a85-6c52-4725-b009-5f30a9cc0716
  modified: 2026-11-09T03:56:15.126Z
---

Paseo 0.15.3 (app `%LOCALAPPDATA%\Programs\Paseo`, CLI `resources\bin\paseo.cmd`, daemon 127.0.0.1:6767, config `~/.paseo/config.json`) runs the `claude` CLI (winget `Anthropic.ClaudeCode`, set up 2026-11-09). The CLI reads key + endpoint from `~/.claude/settings.json` (see [[reference-vscode-pilot]]).

- The llmpro gateway only knows `claude-opus`, `claude-sonnet`, `claude-haiku`; any other model id (`claude-opus-5-5`, Paseo's default) comes back as **401 Invalid API key**. So `~/.paseo/config.json` has `agents.providers.claude.models` = those 3 (opus default) + `disallowedTools: ["WebSearch"]`; apply with `paseo reload`.
- After installing a CLI, `paseo restart` so the daemon finds it (`paseo provider ls` → claude available).
- Testing the CLI from a Claude desktop shell: first remove the inherited `ANTHROPIC_*` / `CLAUDE*` env vars (the app's own token overrides settings.json and gives a false 401).

## Cấu hình từ máy khác (2026-11-09)

Paseo 0.15.3 (Electron app, `%LOCALAPPDATA%\Programs\Paseo`, CLI `resources\bin\paseo.cmd`) set up 2026-11-09 to run Claude through the team proxy.

- Provider `llmpro` in `~/.paseo/config.json` → `agents.providers.llmpro`: `extends: "claude"`, env `ANTHROPIC_BASE_URL=http://192.168.10.29:40741` (LAN, user's choice) + `ANTHROPIC_AUTH_TOKEN` = same LAN key as `~/.claude/settings.json`, models `claude-opus[1m]` / `claude-sonnet[1m]`.
- Built-in provider `claude` is overridden the same way (command + env + models) so picking plain "Claude" in the app also works; without it the app shows "Unavailable".
- `command` must be a string ARRAY (`["C:\\Users\\Admin\\.local\\bin\\claude.exe"]`), not `{mode, argv}` — wrong shape makes Paseo drop the provider ("Provider override matches no registered provider").
- No `claude` on PATH on this machine: `~/.local/bin/claude.exe` is a copy of the VS Code extension's native binary (2.1.318); recopy after big Claude Code updates.
- New/changed providers need `paseo.cmd restart` (or app restart); `reload` only applies overrides to existing providers. Check: `paseo.cmd provider ls` → llmpro `available`; test: `paseo.cmd run "Reply OK" --provider llmpro`.

Related: [[reference-vscode-pilot]]
