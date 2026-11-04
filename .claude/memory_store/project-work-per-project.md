---
name: project-work-per-project
description: work/ is split per project since 2026-10-28 — work/<project id>/<job>/; only shared labs + clips.json stay at work/ top
metadata:
  node_type: memory
  type: project
  originSessionId: fd0b42e4-e400-4a0c-866e-b41adcdd644a
  modified: 2026-10-28T01:41:54.625Z
---

User 2026-10-28: "trong work mỗi dự án tạo một thư mục riêng rồi lưu dữ liệu liên quan vào đó".
Layout: `work/boss_gaygor/` (all Gaygor jobs + its old .blend in `blender/`), `work/shoot_die_repeat/` (sdr, sdr06, zom1, zom2, zom2_map3, map3_props, `blender/`), `work/pirate_goldrush/spine/HandTut/`.
Shared at work/ top: `clips.json`, `pose_lab/`, `review_page/`, `rig_lab/`, `mesh_lab/`, `store/`. Project folder name = `projects[].id` in clips.json; each clip has a `dir` key; Home's "+ Animation mới" creates `work/<project>/<id>/` (commit 7fdddf5).

**Why:** user wants each game's data together.
**How to apply:** new job/clip files go to `work/<project>/<job>/` (read the clip's `dir`); scripts in a project folder reach shared labs via `../../pose_lab`, the repo root via `../../..`. See [[project-map]], [[project-home-app]].
