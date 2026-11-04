---
name: feedback-sdr-git-branch
description: "Unity repo shot-die-repeat: push anim/rig files to TungNV_Dev only, never Dev/TungNV again; stage only my files"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 18a449f5-a7e5-49ad-bd9b-fe657ea46a7a
  modified: 2026-10-26T07:35:08.273Z
---

Unity project `E:\Horus\shot-die-repeat` (remote git.horusent.com/beachwar/shot-die-repeat): push my FBX/anim files to branch **`TungNV_Dev`**, not `Dev/TungNV` (user 2026-10-26: "TungNV_Dev đẩy vào nhánh này. ko đẩy lên nhánh cũ nữa").

**Why:** TungNV_Dev is the art branch (KhaiND pushes models there); Dev/TungNV is the dev branch merged into v1. The zombie blood fix went to Dev/TungNV first (57070bac, reverted by cfe7dce8 on user request; local files keep the fixed FBX so they show as modified on Dev/TungNV — never commit them there), then to TungNV_Dev (5e69f35d).

**How to apply:** The local checkout sits on Dev/TungNV with ~44 unrelated dirty files and Unity open, so don't switch branches. Build the commit on origin/TungNV_Dev with a temp index (`GIT_INDEX_FILE=… git read-tree origin/TungNV_Dev`, `update-index --cacheinfo`, `write-tree`, `commit-tree -p origin/TungNV_Dev`, `git push origin <sha>:refs/heads/TungNV_Dev`). First check that the file's blob on TungNV_Dev is the base I edited. Stage only my files; push only when the user asks. Related: [[project-shoot-die-repeat]]

**Check before pushing a file:** the two branches can hold different versions of the same FBX (map03 MC rig: Dev/TungNV = 15/10 body+Hair+Items+crossbow3, TungNV_Dev = 16/10 merged body `MC_char_map1_Dot1` + crossbow6, no joint1-6). Compare blob hashes of the file on origin/TungNV_Dev with the base I edited; if different, redo the edit on TungNV_Dev's version instead of pushing mine. The local Unity checkout is on Dev/TungNV, so its files are Dev/TungNV's versions.

2026-10-29 (SDR03 Shoot+Reload, commit 94ded9c3): the local checkout was on **TungNV_Dev** (41 dirty files, Unity Editor closed). Anim FBX go to `Assets/_Game/Animations/Map<NN>/SDR<NN>_MC_<Clip>.fbx` like SDR06. Unity closed = no auto .meta: pushed a minimal meta (fileFormatVersion + new guid); Unity fills import settings on open. After pushing with the temp index, delete my copied untracked files and `git merge --ff-only origin/TungNV_Dev` so the user's next pull doesn't fail. No LFS: FBX stored as plain blobs.

2026-10-29 (fix + Idle, commit 5424657b): checkout on TungNV_Dev and HEAD == origin/TungNV_Dev, Unity Editor open -> plain `git commit` of only my paths + `git push origin HEAD:refs/heads/TungNV_Dev` (no temp index needed). Left the user's own Unity-edited `SDR03_MC_Reload.fbx.meta` unstaged. Verify pushed blobs with `git rev-parse origin/TungNV_Dev:<path>` == `git hash-object <export>`.
Also push the Unity-filled .meta files after checking them (useFileScale 1, no import warnings); a .meta made while the FBX was unreadable keeps legacy settings (cf8d50bc fixed SDR03 Shoot/Reload).

2026-11-03: Tùng renamed the map folders on **Dev/TungNV** (a28ec191): Map01 Jungle, Map02 Roma, Map03 Mayah, Map04 Pirate, Map05 Western, Map06 London (Animations/, 3D/Model/, Prefabs/Actors/, 2D/Gameplay/Maps/). TungNV_Dev still had MapNN that day. Scripts now resolve folders via `tools/sdr_paths.py` (`SP.anim(5, ...)` picks whichever name exists on disk; `SP.git_path` gives the new name). Before pushing, check which name the target branch tree uses (`git ls-tree origin/TungNV_Dev Assets/_Game/Animations/`).
