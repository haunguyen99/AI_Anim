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
- 2026-11-13: default thinking set to **high** — `~/.claude/settings.json` effortLevel high (+ modelSettings claude-opus), and in `~/.paseo/config.json` each llmpro opus/sonnet model got `thinkingOptions` low…max with `high` isDefault (Paseo schema: model.thinkingOptions[{id,label,isDefault}]). Backups *.bak.20261113. Paseo installed at C:\Program Files\Paseo now. Long [1m] sessions get "loãng" → one job per session.
- 2026-11-13 (user): Paseo's llmpro API context window = **200k tokens** (not 1M). Long jobs hit auto-compact sooner → keep each Paseo job small (one job per session, self-contained brief, don't dump big files/logs into context).
- 2026-11-13: 1M context works through llmpro: model id `claude-opus[1m]` (CLI reports contextWindow 1000000, gateway accepts). Paseo config now has `claude-opus[1m]` (default) + `claude-sonnet[1m]` with thinkingOptions (high default), plain 200k models kept; backup config.json.bak.20261113b. Not yet verified with a real >200k prompt.
