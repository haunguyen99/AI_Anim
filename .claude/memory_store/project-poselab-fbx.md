---
name: project-poselab-fbx
description: "Pose Lab is the whole Walk tool (keys, spline, foot lock, prop lock, ref fit, FBX) without Blender; Gaygor Walk blocking b1 (8 keys) in the page db 2026-10-23, waiting for the user's edits"
metadata:
  node_type: memory
  type: project
  originSessionId: 3ccc149f-3d11-4ff9-8b77-1bfb6c40469c
  modified: 2026-10-23T03:44:30.139Z
---

User (2026-10-23): whole workflow on Pose Lab, then "bỏ hẳn blender". Page https://claude.ai/artifact/RRZZBxz7FzPHsv13Bu4Ao6
version anim_v1 (57F loop): keys in db, spline/stepped, auto key, foot lock lanes, mace + left hand locked to the
shoulder, ref panel + REF|ANIM compare, "Khớp ref" fit (calibrated ref cameras), Xuất FBX.

**State 2026-10-23:** blocking b1 = keys F1, 8, 15, 22, 29, 36, 42, 50 (stepped) written to db keys via ArtifactData;
user said they will edit on the page. Known defects told to the user: left heel stays raised (F22, F42), body a bit
more open to camera than ref, F1 legs re-fitted.
**Next:** read their edits (db keys at/by), then spline/polish on the page; export FBX from the page.
**How to apply:** details in knowledge/details/review_process.md#pose-lab-3d; see [[feedback-no-blender-pose-lab]], [[reference-pose-lab]].
