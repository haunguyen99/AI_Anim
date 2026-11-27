# Đồng bộ kiến thức lên git (2026-11-10)

**Mục đích (art lead):** đổi máy hoặc đổi nền tảng thì vẫn còn thông tin cũ. Nên mọi thay đổi skill / luật / `.md` / cấu hình dùng chung phải lên GitHub ngay, không đợi cuối ngày.

## Hai nhánh
| Nhánh | Chứa | Ở đâu |
|---|---|---|
| `main` | kiến thức: `CLAUDE.md`, `MAP.md`, `SPEC.md`, `AGENTS.md`, `contexte/`, `.claude/rules|skills|settings.json|launch.json`, `.gitignore`, `.mcp.json`, `tools/sync_knowledge.py`, `tools/auto_commit.ps1`, `Docs/**/*.md`, `Docs/VFX/_Library/*.csv` | GitHub `doson2801-dos/AI_VFX` |
| `master` | nhánh làm việc ở máy: cả kiến thức lẫn tài nguyên (Assets, builder, texture…) | **chỉ ở máy**, hook `.git/hooks/pre-push` chặn mọi push chứa `refs/heads/master` |

Tài nguyên (Unity asset, Library, builder C#…) **không** lên GitHub: đổi máy thì phải chép riêng (ổ đĩa, hoặc đẩy `master` sang một remote riêng nếu art lead muốn).

## Cách hoạt động (`tools/sync_knowledge.py`)
1. Đứng ở `master`, `git add -A` + commit mọi thay đổi trong phạm vi kiến thức (chỉ các đường dẫn đó, file khác đang stage không bị kéo theo).
2. Chép từng commit mới của `master` sang `main`: dựng cây của `main`, thay phần thuộc phạm vi bằng phần của commit đó (index tạm + `commit-tree`), nên **không đổi nhánh và không đụng thư mục làm việc**. Mốc đã chép: ref `refs/vfxlib/synced-master`.
3. `git fetch`; nếu `origin/main` có commit mới (máy khác đẩy lên) thì merge vào `master` trước (xung đột thì dừng, báo trong log). Sau đó push `main`.
4. Đứng ở `main` thì commit thẳng, `pull --rebase`, push (như bản cũ).

Khi nào chạy: hook `Stop` (sau mỗi lượt Claude, `--hook` = im lặng, push chạy nền), Task Scheduler `VFX_LIb Auto Commit` 17:30 (`tools/auto_commit.ps1`, bắt cả thay đổi ngoài Claude), hoặc tay. Có khoá `tools/.sync.lock` để không chạy chồng; `index.lock` bị giữ thì bỏ qua lượt đó.

## Dựng lại trên máy mới
1. `git clone https://github.com/doson2801-dos/AI_VFX` (ra `main` với toàn bộ kiến thức, skill, script đồng bộ).
2. Chép tài nguyên (Assets…) từ máy cũ. Tạo nhánh làm việc: `git checkout -b master`.
3. Tạo hook chặn push master: `.git/hooks/pre-push` (từ chối ref chứa `refs/heads/master`).
4. Task Scheduler: tác vụ `VFX_LIb Auto Commit` 17:30 chạy `powershell -NoProfile -ExecutionPolicy Bypass -File <repo>	oolsuto_commit.ps1`.
5. Hook `Stop` đã nằm trong `.claude/settings.json` (nếu đã bật): `python -I "$CLAUDE_PROJECT_DIR/tools/sync_knowledge.py" --hook`.
6. Cần Python 3 trong PATH. Luật art lead không đổi.

## Lưu ý
- `main` vẫn còn code Assets cũ (commit trước 2026-11-04). Không cập nhật nữa, không xoá.
- Hook `Stop` trong Claude phải được art lead cho phép (cấu hình tự chạy lệnh); chưa bật thì chỉ còn lần chạy 17:30.
