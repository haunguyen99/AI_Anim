---
name: feedback-analysis-first
description: "Always write the detailed animation description (step 2, per phase + per body part) for approval before blocking, also when there is no reference"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8218d775-e470-4bab-8fca-6e6d0eb37e54
  modified: 2026-10-20T08:43:24.125Z
---

Before blocking SDR Attack I only gave a short timing table; the user asked "Bạn đã làm bước mô tả anim chi tiết chưa" (2026-10-20).
**Why:** step 2 (Analysis, approval 1) is a fixed gate of the pipeline; without a ref it is a design spec the reviewer must approve.
**How to apply:** write work/<dự án>/<job>/<clip>_analysis.md in the Gaygor analysis format (context/constraints, overview + phase table
with easing, per-part motion with frames/angles/overlap lags, prop/events, secondary parts inventory, key plan, QA), tag sources
([concept]/[đối thủ]/[quyết định]/[thiết kế] when there is no ref), get approval, then block. See [[feedback-coarse-to-fine]].
