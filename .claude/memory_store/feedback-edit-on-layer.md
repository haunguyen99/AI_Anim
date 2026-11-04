---
name: feedback-edit-on-layer
description: "Frolvy edits of an existing anim always go on a new additive anim layer per round, never on Base; use frolvy_layers.py (Frolvy 0.9.36 layer bugs)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 604e1e07-64f3-4048-8621-97c0b7e7cba9
  modified: 2026-11-04T05:47:10.664Z
---

When the user asks to fix/change an anim in Frolvy, put the change on a new additive layer `fix_r<N>_<what>` (one per review round), keyed with `.claude/skills/frolvy_rig/scripts/frolvy_layers.py` (`key`/`offset` with `hold=(a,b)`), and never key the Base layer. Before export, on a copy: `bake_for_export`, then the normal export.

**Why:** user 2026-11-04 "sử dụng layer khi được yêu cầu chỉnh sửa. không sửa trực tiếp trên layer gốc như ban đầu" — keeps the approved version and lets base changes keep the fixes. Frolvy 0.9.36: set_key on additive layer double-counts and keys all channels; flatten_layers/bake_keys/export_scene double the layer (feedback #14–16).

**How to apply:** Frolvy first (Studio has no anim layers yet). Steps in knowledge/details/user_blocking.md#sửa-anim-trên-frolvy. Override layers, retime across layers, custom attrs on layers are untested. Related: [[project-workflow-b-user-blocking]], [[reference-frolvy-mcp]], [[feedback-frolvy-report]].
