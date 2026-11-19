---
name: reference-codex-img
description: "Codex CLI image generation via tools/codex_img.py (ChatGPT plan, no API cost) for key pose ref images in the GDD stage"
metadata:
  node_type: memory
  type: reference
  originSessionId: 01e821e4-a999-46ec-8786-cd29946496ce
  modified: 2026-10-28T05:15:38.982Z
---

- No Node/npm on the machine; the Codex desktop app bundles `codex.exe` at `%LOCALAPPDATA%\OpenAI\Codex\bin\<hash>\codex.exe` (hash folder changes on app update; tool picks newest). Logged in with ChatGPT; `image_generation` feature on.
- `tools/codex_img.py "prompt" --out x.png [--ref char.png] [-n 3]`: one `codex exec` per image, ~80–120 s each. Prompt goes via stdin because `-i` swallows following args.
- NEVER run several in parallel: concurrent ChatGPT token refresh → 401 Unauthorized on all (2026-10-28, 5/5 failed). Tool now queues via %TEMP%\codex_img.lock.
- Tested 2026-10-28: with a `--ref` image the character design (armor, props) is kept, only the pose changes.
- First run: SDR map3 crossbow (work/shoot_die_repeat/sdr03), review page https://claude.ai/artifact/QFHM3nn62XSAbQLAxhDWkH (Duyệt 1 pending 2026-10-28). Codex images drift on mechanics (string position, bolt still on rail, bow-style draw) → caption each deviation; pose/silhouette read well.
- Purpose: stage 0 planned with user 2026-10-28 (GDD → anim list → missing questions → analysis.md with [GDD]/[suy luận] sources → key pose images as blocking ref → review page). Images = intent/silhouette only, never for measuring angles ([[feedback-pose-accuracy]]).
