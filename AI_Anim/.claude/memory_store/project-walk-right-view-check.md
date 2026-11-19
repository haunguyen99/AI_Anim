---
name: project-walk-right-view-check
description: "Gaygor Walk blocking vs ref Phải measured 2026-10-23: no pose fix needed; db keys F1/8/15/22 are user-edited, F29 R foot ambiguous"
metadata:
  node_type: memory
  type: project
  originSessionId: 3f00d00a-7ab5-4ebe-9514-366e828876ba
  modified: 2026-10-23T07:33:28.253Z
---

Gaygor Walk blocking checked against ref Phải by silhouette IoU (page code run locally, keys from db): IoU 0.74–0.83, pelvis/feet already at optimum, residual = mesh bulk at back/hip, not pose. User confirmed "vậy đúng rồi" → no key changed.

**Why:** work/boss_gaygor/walk/block_b3/*.json is STALE for F1/F8/F15/F22 (user hand-edited them in the page after b3); F29/36/42/50 match b3. Always read the db `keys` collection (ArtifactData, doc `Gaygor_Walk-anim_v1-F<n>`), never block_b3, before measuring or editing. See [[feedback-user-edits-cascadeur]].
F29 right (swing) foot: optimizer wants +33 cm forward (IoU .62→.74) but that makes a 45 cm one-frame jump and contradicts fitFeet hint -28; left unchanged.

Spline set 2026-10-23 (db anims interp=spline, lock=true; db contacts L 15-36, R 1-15,42-56 are the user's, not POSES defaults). Open issue: R swing foot drags on floor F31-35, needs a lift key ~F33 (user: "để sau"). Pose Lab page 2026-10-23: hide-panes buttons ([ ]), 7 cameras, knee/elbow pole diamonds (placePoles/poleDrag in index.html), published as v14.

**How to apply:** run pose-lab server (launch.json), seed localStorage `poselab:Gaygor_Walk-anim_v1` from db docs, use refMask/renderMask/iouRows in the page; don't trust optimizer for feet (overlap in side views, contact lanes fix foot x). Next step for Walk: spline + floor check.
