---
name: feedback-quick-render
description: "Self-check fixes with a quick render (only the noted frames/views, 25 %, one contact sheet); full playblast only for the version posted for review"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5777a8b4-d319-4595-b272-c4de7037baa5
  modified: 2026-10-22T01:12:43.199Z
---

User approved 2026-10-22 ("làm gộp note và render nhanh"). SDR06: add `quick=F,F views=a,b` to blocking.py / spline.py → `pb_<clip>_<ver>_quick/`, then `tools/quick_sheet.py <dir>` → read ONE `sheet.jpg`. In spline.py quick mode also re-solves only those frames (the per-frame hand solve, not the render, is what takes >15 min).

**Why:** reading hundreds of PNGs per session filled the context (2–3 compactions/session) and every small fix ran the full build+render+playblast+publish chain.
**How to apply:** iterate on quick sheets; run the full render + playblast + page publish once, when every note looks fixed. Related: [[feedback-review-listening]].
