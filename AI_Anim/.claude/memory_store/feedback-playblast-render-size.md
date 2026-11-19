---
name: feedback-playblast-render-size
description: "Pose Lab playblast frames got cropped (spline_b10, 2026-10-23); always reset renderer size per cell and look at a frame before encoding"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3f00d00a-7ab5-4ebe-9514-366e828876ba
  modified: 2026-10-23T09:21:30.109Z
---

When rendering review playblast frames from the Pose Lab page (composite 1800x600 via renderer.domElement), the page's ResizeObserver can reset the WebGL buffer to the viewer size between my `setSize(600,600)` and the render; `drawImage(canvas, 0,0,600,600,...)` then copies only the top-left crop -> cropped, off-centre views (user: "Lỗi video review").

**Why:** spline_b10 shipped with this bug; b6-b8 happened to be fine.

**How to apply:** in the per-cell function call `renderer.setPixelRatio(1); renderer.setSize(600,600,false); camera.aspect=1; camera.updateProjectionMatrix()` before every render and copy with `renderer.domElement.width/height`; read one mid-clip frame image (e.g. F17) before running ffmpeg, then republish with the same file name. See [[reference-review-page]] and [[project-walk-right-view-check]].
