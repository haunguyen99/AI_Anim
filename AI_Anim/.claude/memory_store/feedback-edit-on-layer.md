---
name: feedback-edit-on-layer
description: "Frolvy RPG2 Hero edits: NO new anim layers (user 2026-11-10); edit on Base and add keys only on new frames, never touch the user's keys. Old rule (layer per round) applies only to other projects"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 604e1e07-64f3-4048-8621-97c0b7e7cba9
  modified: 2026-11-10T02:28:43.258Z
---

**Latest (user 2026-11-10, RPG2 Hero_Blade Attack_02):** "không được tạo thêm anim layer trong quá trình sửa file". Never create anim layers while editing the file. Edit on Base only, add keys on NEW frames, and never change keys the user already set (user's arm keys F4/7/11/14 were mistaken for mine once and the layer attempt was reverted: "làm hỏng key chính").

**Old rule (2026-11-04):** edits of an existing anim went on a new additive layer `fix_r<N>_<what>` via `.claude/skills/frolvy_rig/scripts/frolvy_layers.py`, never on Base. The 2026-11-10 instruction overrides this for the RPG2 Hero files; for other projects ask first.

**Why:** the user inspects and rearranges keys by hand in Frolvy; extra layers hide/duplicate keys and Frolvy 0.9.36 layers double-count (feedback #14–16).

**How to apply:** before editing, list the keys on each channel (list_keys) and treat all existing ones as the user's. If a change would need to move a user key, ask. Related: [[keep-existing-keys-when-editing]], [[project-workflow-b-user-blocking]], [[reference-frolvy-mcp]].
