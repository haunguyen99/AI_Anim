---
name: feedback-git-review-log
description: Commit after every review verdict with the reason; tag approved versions; mine diffs (rejected→approved) for knowledge/ lessons
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4f795391-752e-4d94-ade3-b0e754a8101d
  modified: 2026-10-21T01:25:41.436Z
---

Project is a local git repo since 2026-10-21 (no remote). Only code/md/small json tracked; .blend/.fbx/video/images/npy ignored (versioned by `_vN`).

Convention: each time the user approves or rejects a version, commit the scripts/params/notes for it with a message "<clip> v<N>: approved|rejected — <reason from user, quoted>" and what was changed from the previous version. Approved versions get tag `<char>-<clip>-v<N>-approved` (existing: gaygor-idle-v5-approved, gaygor-idle-front-v14-approved).

**Why:** user agreed git is for (1) rollback of scripts/knowledge, (2) a feedback log Claude can re-read, (3) deriving lessons from real diffs between rejected and approved versions.
**How to apply:** when writing lessons into knowledge/ ([[feedback-update-knowledge]]), base them on `git diff` between rejected and approved commits. Never push; no remote unless the user asks. See [[project-map]].
