---
name: frolvy-fit-controls-after-build
description: "In Frolvy, always fit control shapes to the mesh right after every Build Rig / Rebuild Rig (now fit_controls.snug)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 83cdef65-af29-451a-8f34-f279fd5a4724
  modified: 2026-11-04T08:01:01.570Z
---

After every Build Rig (or Rebuild Rig) in Frolvy, draw the controls snug to the mesh so none is hidden inside it or blown up huge:
`import sys; sys.path.insert(0, r"D:\Project\AI_Anim\tools\frolvy_plugins\fit_controls"); import fit_controls; fit_controls.snug(api)` via mcp__frolvy__execute_code, then `fit_controls.fit(api, controls=[the ones snug skipped])` for switches/poles. Same as the Frolvy menu Plugins > Build Rig + Fit Controls (installed copy: Documents\Frolvy\plugins\fit_controls\0.1.0 — copy the repo file there after edits).

**Why:** Build Rig draws fixed-size controls that ignore the mesh (user 2026-10-30: "mỗi lần tạo control luôn bị ẩn trong mesh"). The user also dislikes oversized rings (2026-10-31 Gragas: "shape control hơi to ... phù hợp và thân thiện với người dùng hơn") and asked why an extra command was still needed after Build Rig (2026-11-04 Hero), so the snug method went into the plugin and the one-click menu.

The old `fit()` (grow/slide by an inside test) breaks on single-layer sheets (skirt, cape, scarf, hood: Hero ankle ring 2 m, scapula 2.5 m). `snug()` measures cross-sections instead and marks controls `snug=1`, `fitScale=6`, so later runs and Rebuild leave them; `force=True` redraws all.

**How to apply:** do it unasked as part of building a rig, after deleting mirrored extras; report how many controls changed and anything still awkward. Related: [[frolvy-rig-root-at-origin]].
