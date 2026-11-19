---
name: feedback-coarse-to-fine
description: Reviewer rule for posing: split the body into levels, main masses first (pelvis/legs, torso/head), then limbs, then hands/prop details
metadata:
  type: feedback
---
Pose one level at a time and verify each against the ref before going on: pelvis + legs -> torso/neck/head -> prop -> arms -> hands/fingers.
**Why:** f13 v1 was rejected (2026-10-20): "chia các bộ phận ra làm từng phần 1. Phần chính làm trước, sau đó đi dần đến các bộ phận con nhỏ hơn"; whole-body IoU hid a wrong head (tilted up 32°) and straight legs.
**How to apply:** per level, project that part's mesh points onto the ref (part_points + tools/part_overlay.py) and measure numbers (head extents, belt height, prop height from a side view). See [[feedback-pose-accuracy]], [[feedback-arm-anatomy]].
