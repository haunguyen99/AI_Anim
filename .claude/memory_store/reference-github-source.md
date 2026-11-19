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

**2026-11-19 — kéo main mới về master (bài học gộp):**
- Kéo: `git fetch origin` → xem `git log HEAD..origin/main` + `git diff --stat master...origin/main` → so với `git diff --name-only` (file đang sửa dở) để biết file nào sẽ trùng. Có trùng thì **commit bản local trước**, rồi `git merge origin/main`. Không merge lên cây đang bẩn.
- Xung đột "cả file" (.gitignore, export.md…) thường chỉ do **CRLF vs LF**: so bằng `diff <(git show :2:f | tr -d '\r') <(git show :3:f | tr -d '\r')`; trống = giống nhau → `git checkout --theirs f`. Còn lại chỉ xung đột thật vài dòng thì giữ cả hai (MEMORY.md, REPORTS.md: hợp hai danh sách).
- Một file code (tro_ly.py) hai bên cùng sửa: bên local có thêm xử lý phiên Paseo `closed` → giữ, vì main không có chỗ tương đương. Kiểm cú pháp (`ast.parse`) + chạy `status` sau khi gộp.
- Sau merge `master` đã chứa main; đẩy GitHub vẫn chỉ bằng `/push` (`push_source.py --yes`) → nhánh `main`, không bao giờ push `master`. GitHub Desktop đứng ở master báo hàng chục file đổi là bình thường (dữ liệu work/), đừng commit / push từ đó.
- Đừng dùng `find` quét cả ổ (/home, DataHDD): treo phiên hơn 2 phút (2026-11-18).
