---
name: push
description: Đẩy mã nguồn của dự án lên GitHub (haunguyen99/AI_Anim, nhánh main): skill, tool, quy trình, tài liệu, mã các trang Lab. Dùng khi người dùng gõ /push, nói "push", "đẩy lên GitHub", "cập nhật repo". Không đẩy dữ liệu (model, video, FBX, trang đã build).
---

# /push: đẩy mã nguồn lên GitHub

Repo GitHub `main` **chỉ chứa mã nguồn**; nhánh `master` trên máy chứa cả dữ liệu làm việc nên **không bao giờ** đẩy `master`. Việc đẩy do `tools/push_source.py` làm: nó dựng một commit từ cây `origin/main` cộng các file nguồn trong danh sách cho phép (skill `.claude/skills/**`, bộ nhớ Claude `.claude/memory_store/**` (từ 2026-11-04, để tài khoản khác `tools/claude_memory.py restore` được; chạy `claude_memory.py backup` trước khi đẩy), `tools/**`, `docs/**`, `README.md`, `MAP.md`, `requirements.txt`, `.gitignore`, `work/clips.json`, và mã các Lab: `work/pose_lab`, `work/review_page`, `work/rig_lab`, `work/mesh_lab`), dùng chỉ mục tạm nên không đụng nhánh và không commit lẫn file đang làm dở. Trả lời bằng tiếng Việt.

## Chỉ có hai nhánh: `master` (máy) và `main` (GitHub)

Nhánh `spine-live` đã bỏ (người dùng 2026-11-11, đã đưa Spine Live vào `main` rồi xoá nhánh). Spine Live (`tools/spine_live/**`, `tools/home/spine_live.py`, `spine_edit.py`, `spine_bridge.py`, `tools/spine_live_*.py`, `.claude/skills/spine2d/**`) đẩy lên `main` như mọi file khác, không có `--spine-live`. Đừng tạo lại nhánh khác trên GitHub.

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

## Gộp với GitHub trước mỗi lần đẩy + tự đẩy kiến thức (người dùng 2026-11-11)

Nhiều máy cùng đẩy lên `main`, mà `push_source.py` ghi file trên máy ĐÈ lên GitHub và coi file máy khác vừa thêm là "XOÁ". Không gộp trước thì lần đẩy sau xoá mất việc của máy kia (2026-11-11: 30 file kiến thức khác nhau, 8 file `tools/` bị coi là XOÁ: plugin Frolvy `loop_seam`, `hero_textures`, `rig_pose_tools`…). Vì vậy **luôn gộp trước khi đẩy**, cả `/push` thường (tool, tài liệu, mã Lab, `MAP.md`, `clips.json`) lẫn đẩy riêng kiến thức. Kiến thức (`.claude/skills/**`, `.claude/memory_store/**`, `tools/claude_memory.py`) là phần quý nhất của repo, không để nằm lại chỉ trên máy.

### Bước A: gộp (trước MỌI lần đẩy)
1. `.venv\Scripts\python.exe -I tools\knowledge_merge.py` xem báo cáo (không ghi gì; `--scope knowledge` hoặc `--scope code` để chỉ một nhóm). Công cụ so từng file giữa máy này, `origin/main` và **gốc chung của file đó** (tự tìm: bản mới nhất trong lịch sử `origin/main` trùng một bản trong lịch sử `master`), nên không cần dấu đồng bộ và không bị lệch khi máy khác đã đẩy từ trước. Phạm vi = đúng các file `/push` đẩy.
2. Có gì cần gộp thì thêm `--apply`:
   - bản remote = gốc chung → máy này đã có / mới hơn: giữ; bản máy này = gốc chung → lấy remote; cả hai khác gốc → gộp 3 chiều (`MEMORY.md` gộp theo dòng; `work/clips.json` gộp theo MỤC: nhân vật theo tên, clip / dự án theo id, hợp hai bên, mục cả hai sửa thì giữ bản máy này và báo); giữ kiểu xuống dòng của file;
   - file remote có mà máy này chưa từng có → thêm về; file máy này đã xoá (từng có trong `master`) → giữ xoá và báo, `/push` sẽ xoá trên GitHub: hỏi người dùng nếu không chắc;
   - chạy lại nhiều lần an toàn (không tạo xung đột mới trên chỗ đã gộp).
3. Thoát mã 2 (dấu `<<<<<<< may-nay` … `>>>>>>> remote`, file nhị phân, hoặc không có gốc chung) thì **tự đọc hai bên và sửa tay**: thường giữ cả hai phần; hai dòng sửa cùng một câu thì giữ bản remote rồi thêm phần riêng của máy này; chỗ không chắc thì hỏi người dùng. `grep -rn "<<<<<<< may-nay" .claude tools docs MAP.md work/clips.json` phải trống.
4. Có memory mới từ remote: `tools\claude_memory.py restore` (vào bộ nhớ phiên, gộp `MEMORY.md` theo dòng), rồi `backup`.
5. Commit kết quả gộp trên `master` (chỉ các file công cụ đã đụng tới, không `git add -A`), lời nhắn `merge: gộp từ GitHub main …`.
6. `push_source.py --dry-run`: không được còn XOÁ ngoài ý muốn, không file lạ. Đẩy thất bại vì người khác vừa đẩy thì chạy lại Bước A.

### Bước B: đẩy
- **`/push` thường:** có file kiến thức sửa chưa commit thì `claude_memory.py backup` (nếu bộ nhớ đổi) và commit riêng đúng các file đó (`knowledge: <bài học chính>`); làm Bước A; rồi đẩy như mục "Khi gõ /push".
- **Cuối mỗi việc có ghi bài học mới** (`knowledge/details/*.md`, `director_standards.md`, memory): tự đẩy riêng phần kiến thức, không chờ `/push`, không kéo theo file làm dở của việc khác:
  - Bước A với `--scope knowledge`, rồi `push_source.py --only .claude/skills .claude/memory_store tools/claude_memory.py --committed --dry-run` (chỉ bản đã commit, chỉ thêm / sửa);
  - dry-run chỉ có file kiến thức, không XOÁ, không file lạ thì `--yes -m "knowledge: <bài học>"`; ngược lại dừng và hỏi.
- Báo người dùng một dòng: đã gộp / đẩy gì, commit nào. Không `--force`.

## Nhắc và tự đẩy kiến thức theo lịch (người dùng 2026-11-11)

Hai cơ chế tự động chạy song song với việc Claude tự đẩy cuối mỗi việc có bài học (`tools/knowledge_sync.py`):
- **Nhắc (hook):** mỗi lần mở phiên / gửi tin, hook kiểm (tối đa 1 lần / 20 phút, `git fetch` 1 lần / giờ). Có kiến thức chưa đẩy, hoặc GitHub có bản kiến thức mới từ máy khác, hoặc lần tự đẩy theo lịch dừng vì cần gộp tay thì hook đưa vào ngữ cảnh một thông điệp "Kiến thức: …". **Việc của Claude:** cuối lượt trả lời đó nhắc người dùng MỘT dòng và hỏi có đẩy luôn không; đồng ý mới làm Bước A + B (Bước A trước, vì máy khác có thể đã đổi cùng file). Không tự đẩy khi người dùng chưa đồng ý ở lượt này; nhắc lại tối đa 1 lần / giờ nên không cần nhắc dồn.
- **Lịch Windows `AIAnim_KnowledgePush`** (mặc định 17:10 mỗi ngày, máy tắt thì chạy bù khi bật; cài / đổi giờ / gỡ: `powershell -ExecutionPolicy Bypass -File tools\knowledge_sync_install.ps1 [-Time 12:30] [-Remove]`): chạy `knowledge_sync.py autopush` không cần Claude: sao lưu bộ nhớ, commit file kiến thức đang sửa dở, gộp với GitHub (chỉ khi mọi file gộp SẠCH), rồi đẩy riêng các file kiến thức khác GitHub (`--only … --committed`, không xoá gì). Có xung đột / không có gốc chung / file nhị phân thì **dừng**, ghi `needs_merge` để hook nhắc ở phiên sau: khi đó Claude làm Bước A tay (sửa xung đột), rồi đẩy.
- Xem tình trạng: `.venv\Scripts\python.exe -I tools\knowledge_sync.py check`; nhật ký lần tự đẩy: `work\store\_sys\watch\knowledge_autopush.log`. Chỉ đụng kiến thức (`.claude/skills`, `.claude/memory_store`, `tools/claude_memory.py`); tool / tài liệu / Lab vẫn chờ `/push`.
- `push_source.py` đẩy `main` thành công thì ghi mốc `last_seen_remote` vào `knowledge_sync.json` (để hook không nhắc oan "GitHub có bản mới" về chính commit của mình).

## Quy tắc

- Không đẩy `master`, không `git push --force`, không đẩy dữ liệu (`work/*/pages`, `work/store`, models, clips, `.blend` / `.fbx` / video).
- `.claude/launch.json` và `.mcp.json` giữ nguyên bản trên GitHub (bản trên máy có cấu hình riêng). Muốn đổi hai file này, sửa trên GitHub qua một commit riêng và nói rõ với người dùng.
- Sửa danh sách cho phép / loại trừ: `ALLOW`, `DENY` đầu `tools/push_source.py`. Thêm loại file mới (vd thư mục Lab mới) thì thêm vào `ALLOW` rồi chạy `--dry-run` kiểm tra.
- Commit cục bộ trên `master` là việc khác: `/push` không commit hộ. Việc đẩy nội dung hiện tại trong thư mục làm việc, kể cả file chưa commit.
