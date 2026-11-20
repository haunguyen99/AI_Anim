---
name: skin-check-full-rom-wireframe
description: "When checking a skin, sweep every joint through its full range of angles and inspect with the mesh wireframe on; good skin = edges stretch evenly"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 54cd37d1-1c51-427b-abd6-dc2deffeb774
  modified: 2026-10-27T16:06:36.173Z
---

When verifying or tuning skin weights, rotate each joint through its full range on every axis (both directions, many angles, not one sample per axis) — a single test angle misses most problems. Always check deformation with the mesh wireframe visible: a good skin makes the wire edges stretch/compress evenly across the bend, not concentrated in one row of edges.

**Why:** the user (2026-10-27, Boss_Gragas rig) said one angle per axis did not reveal all errors, and judges skin quality by how evenly the wireframe edges spread.

**How to apply:** in `work/rig_lab/lbs_test.py`-style checks, sweep angles per joint (e.g. 15° steps over the anatomical range) and measure edge-stretch evenness, not only a >25 % threshold; renders for self-review should draw the wireframe (ideally colored by stretch). Related: [[screenshots-on-request]] does not apply to these self-check renders.
