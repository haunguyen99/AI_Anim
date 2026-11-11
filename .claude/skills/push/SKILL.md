---
name: push
description: Đẩy mã nguồn của dự án lên GitHub (haunguyen99/AI_Anim, nhánh main; chỉnh sửa Spine Live vào nhánh spine-live): skill, tool, quy trình, tài liệu, mã các trang Lab. Dùng khi người dùng gõ /push, nói "push", "đẩy lên GitHub", "cập nhật repo". Không đẩy dữ liệu (model, video, FBX, trang đã build).
---

# /push: đẩy mã nguồn lên GitHub

Repo GitHub `main` **chỉ chứa mã nguồn**; nhánh `master` trên máy chứa cả dữ liệu làm việc nên **không bao giờ** đẩy `master`. Việc đẩy do `tools/push_source.py` làm: nó dựng một commit từ cây `origin/main` cộng các file nguồn trong danh sách cho phép (skill `.claude/skills/**`, bộ nhớ Claude `.claude/memory_store/**` (từ 2026-11-04, để tài khoản khác `tools/claude_memory.py restore` được; chạy `claude_memory.py backup` trước khi đẩy), `tools/**`, `docs/**`, `README.md`, `MAP.md`, `requirements.txt`, `.gitignore`, `work/clips.json`, và mã các Lab: `work/pose_lab`, `work/review_page`, `work/rig_lab`, `work/mesh_lab`), dùng chỉ mục tạm nên không đụng nhánh và không commit lẫn file đang làm dở. Trả lời bằng tiếng Việt.

## Spine Live: luôn vào nhánh `spine-live`

Người dùng 2026-10-29: "từ giờ update push thì sẽ đẩy toàn bộ chỉnh sửa của spine_live vào nhánh spine-live". Chỉnh sửa Spine Live **không** đẩy lên `main`:
- Lệnh: `.venv\Scripts\python.exe -I tools\push_source.py --spine-live --dry-run`, rồi `--spine-live --yes -m "..."`.
- File Spine Live (danh sách `SPINE_LIVE` đầu `push_source.py`): `tools/spine_live/**`, `tools/home/spine_live.py`, `tools/home/spine_edit.py`, `tools/spine_live_cmd.py`, `tools/spine_live_replay.py`, `.claude/skills/spine2d/**`. Thêm file Spine Live mới thì thêm vào `SPINE_LIVE`.
- `MAP.md` trên nhánh có dòng của phiên khác: `--spine-live` chỉ thay các dòng Spine Live (`SPINE_LIVE_MAP`), không đè cả file.
- Nhánh `spine-live` có thể mới hơn máy này (Spine làm ở máy khác, 2026-10-31: `spine_live.py`, `index.html`, `spine_live_cmd.py` trên nhánh mới hơn). Luôn `--dry-run` trước; file nào trên máy cũ hơn nhánh thì đẩy bằng `--only <file của việc này>` (không đưa `MAP.md` vào `--only`: `--spine-live` tự ghép đúng dòng). Sửa file đã có trên nhánh thì lấy bản nhánh làm gốc (`git show origin/spine-live:<file>`) rồi ghép phần mới vào.
- `tools/home/server.py` dùng chung với các tính năng khác: không đẩy theo Spine Live. Nếu Spine Live cần sửa `server.py`, kiểm `git diff origin/spine-live -- tools/home/server.py` trước, chỉ đưa phần của Spine Live lên (bản trên nhánh có thể có tính năng máy này chưa có).
- `/push` có cả việc khác lẫn Spine Live: đẩy hai lần: `--spine-live` cho Spine Live, rồi lần thường cho `main`. Lần thường (lên `main`) tự bỏ qua mọi file trong `SPINE_LIVE` (không thêm / sửa / xoá chúng trên `main`).

## Khi gõ /push [lời nhắn]

1. **Xem trước:** `.venv\Scripts\python.exe -I tools\push_source.py --dry-run`. In ra danh sách THÊM / SỬA / XOÁ và các file có thay đổi chưa commit.
2. **Kiểm trước khi đẩy**, dừng và hỏi người dùng nếu có một trong các điều sau:
   - có file XOÁ (xoá khỏi GitHub): nêu rõ danh sách và lý do, chờ đồng ý;
   - file lạ không phải mã nguồn (dữ liệu, file lớn, file có vẻ chứa khóa/mật khẩu);
   - file đang sửa dở do một phiên Claude khác (cùng thư mục): hỏi có đẩy bản hiện tại không.
   Chỉ đẩy một việc khi phiên khác đang sửa dở file khác: `--only <file / thư mục…>` (chỉ các file này, không xoá gì) và `--committed` (lấy bản đã commit, bỏ phần chưa commit), xem trước bằng `--dry-run` cùng tham số.
   Không có gì mới thì báo một dòng và dừng.
3. **Đẩy:** `.venv\Scripts\python.exe -I tools\push_source.py --yes -m "<lời nhắn ngắn nêu việc đã làm, tiếng Anh>"`. Không có lời nhắn từ người dùng thì tự viết từ các thay đổi (không viết chung chung "update").
4. **Báo kết quả:** commit, số file thêm / sửa / xoá, và việc còn chờ. Đẩy thất bại (người khác vừa đẩy) thì chạy lại để lấy bản mới; **không** dùng `--force`.

## Kiến thức: kiểm, gộp và tự đẩy lên git (người dùng 2026-11-11)

Kiến thức (`.claude/skills/animation/knowledge/**`, các skill khác trong `.claude/skills/**`, bộ nhớ `.claude/memory_store/**`, `tools/claude_memory.py`) là phần quý nhất của repo, không để nằm lại chỉ trên máy. Nhưng nhiều máy cùng đẩy lên `main`, mà `push_source.py` ghi file trên máy ĐÈ lên GitHub: máy khác đã sửa file thì lần đẩy sau xoá mất việc đó (2026-11-11: 30 file khác nhau, trong đó `frolvy_layers.py`, `REPORTS.md`, `frolvy_rig/SKILL.md`, 7 memory mới). Vì vậy **luôn gộp trước khi đẩy**.

### Bước A, trước MỌI lần đẩy kiến thức (cả `/push` thường lẫn tự đẩy)
1. `.venv\Scripts\python.exe -I tools\knowledge_merge.py` (xem báo cáo: file nào chỉ remote đổi, file nào cả hai đổi). Công cụ so 3 bản (gốc = lần đồng bộ cuối lưu ở `.git/knowledge_sync_base`, máy này, `origin/main`). Chưa có gốc thì `--base <sha>` (commit `origin/main` lần đẩy / gộp cuối).
2. Có gì cần gộp thì `... knowledge_merge.py --apply`: chỉ remote đổi → lấy remote; chỉ máy này đổi → giữ; cả hai → gộp 3 chiều (`MEMORY.md` gộp theo dòng). Giữ kiểu xuống dòng của file.
3. Thoát mã 2 (còn dấu `<<<<<<< may-nay` / `>>>>>>> remote`) thì **tự sửa tay từng chỗ** rồi mới đẩy: thường giữ cả hai phần; hai dòng sửa cùng một câu thì giữ bản remote và thêm phần riêng của máy này. Đọc nội dung hai bên, không chọn bừa; chỗ không chắc thì hỏi người dùng. `grep -rn "<<<<<<< may-nay" .claude tools/claude_memory.py` phải trống.
4. Có memory mới từ remote: `tools\claude_memory.py restore` (đưa vào bộ nhớ phiên, gộp `MEMORY.md` theo dòng), rồi `backup`.
5. Commit kết quả gộp trên `master` (`git add` đúng các file kiến thức, không `git add -A`), lời nhắn `knowledge: gộp từ GitHub main …`.
6. `--dry-run` kiểm lại: sau khi gộp, file nào chỉ do remote đổi không còn nằm trong danh sách SỬA. Còn file lạ hoặc XOÁ thì dừng hỏi.

### Bước B, đẩy
- **Mỗi `/push` thường:** có file kiến thức sửa chưa commit thì chạy `claude_memory.py backup` (nếu bộ nhớ đổi), commit riêng đúng các file đó (`knowledge: <bài học chính>`), làm Bước A, rồi đẩy `main` như bình thường.
- **Cuối mỗi việc có ghi bài học mới** (`knowledge/details/*.md`, `director_standards.md`, memory): tự đẩy riêng phần kiến thức, không chờ `/push`, không kéo theo file làm dở của việc khác:
  - Bước A, rồi `.venv\Scripts\python.exe -I tools\push_source.py --only .claude/skills .claude/memory_store tools/claude_memory.py --committed --dry-run` (chỉ bản đã commit, chỉ thêm / sửa);
  - dry-run chỉ có file kiến thức, không XOÁ, không file lạ thì `--yes -m "knowledge: <bài học>"`; ngược lại dừng và hỏi;
  - file Spine Live (`.claude/skills/spine2d/**`, `spinelive/**`) vẫn đi nhánh `spine-live`, công cụ tự bỏ qua.
- **Sau khi đẩy xong:** `.venv\Scripts\python.exe -I tools\knowledge_merge.py --mark` (ghi `origin/main` mới làm gốc cho lần sau). Quên bước này thì lần sau gộp thừa chứ không mất dữ liệu.
- Báo người dùng một dòng: đã gộp / đẩy kiến thức gì, commit nào. Đẩy thất bại (người khác vừa đẩy) thì quay lại Bước A; không `--force`.

## Quy tắc

- Không đẩy `master`, không `git push --force`, không đẩy dữ liệu (`work/*/pages`, `work/store`, models, clips, `.blend` / `.fbx` / video).
- `.claude/launch.json` và `.mcp.json` giữ nguyên bản trên GitHub (bản trên máy có cấu hình riêng). Muốn đổi hai file này, sửa trên GitHub qua một commit riêng và nói rõ với người dùng.
- Sửa danh sách cho phép / loại trừ: `ALLOW`, `DENY` đầu `tools/push_source.py`. Thêm loại file mới (vd thư mục Lab mới) thì thêm vào `ALLOW` rồi chạy `--dry-run` kiểm tra.
- Commit cục bộ trên `master` là việc khác: `/push` không commit hộ. Việc đẩy nội dung hiện tại trong thư mục làm việc, kể cả file chưa commit.
