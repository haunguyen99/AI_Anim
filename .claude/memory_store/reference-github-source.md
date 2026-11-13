---
name: reference-github-source
description: GitHub repo haunguyen99/AI_Anim (private) gets SOURCE ONLY on main, pushed from local branch `source`; local master keeps everything
metadata:
  type: reference
---

GitHub `https://github.com/haunguyen99/AI_Anim` (private, set by user 2026-10-26), branch `main` only. User: "Chỉ đẩy mã nguồn thôi — skill, tool, và quy trình tài liệu".

Push: build a commit on top of `origin/main` with a temp index (`GIT_INDEX_FILE`) containing `.claude/skills`, `tools`, `legacy`, `docs`, `MAP.md`, `README.md`, `requirements.txt`, `work/clips.json`, Lab sources (`work/pose_lab/index.html`, `work/review_page/index.html`, `work/*/split_pages.py`, `work/pose_lab/fbx/*.py|js`, `work/rig_lab/*.py`) → `git branch -f source` → `git push origin source:main` (fast-forward, never force). Compute file lists (`git ls-files ...`) BEFORE exporting GIT_INDEX_FILE (2026-10-26 slip: legacy/ was missing). Never push local `master` (has work data, tags). Tools read the project folder from `ROOT` / env `AI_ANIM_ROOT` / cwd, never hard-code E:/AI Animation. Related: [[project-map]].

**Update 2026-10-27:** pushing is now the `/push` skill (`tools/push_source.py`: allowlist, temp index, `--dry-run`, `--yes`, no force). `.claude/launch.json` and `.mcp.json` stay as on GitHub. Use it instead of the manual procedure above.

2026-11-04 (user: "Bộ nhớ Claude cũng được đẩy lên git cho tài khoản khác cũng dùng được"): `.claude/memory_store/**` nằm trong ALLOW của push_source.py, đã đẩy 07d303a. Mỗi /push: `claude_memory.py backup` rồi đẩy kèm. `.claude/mcp_store` (có khoá MCP) vẫn không đẩy. Tài khoản mới: clone/pull → `claude_memory.py restore`.

2026-11-11 (user: "bỏ nhánh spine-live, chỉ giữ main và master"): nhánh spine-live đã xoá (đưa Spine Live vào main trước, merge bằng tools/knowledge_merge.py --ref origin/spine-live). push_source.py không còn --spine-live. master và main KHÔNG chung lịch sử: không git pull/merge; lấy mã về bằng knowledge_merge.py --apply.
