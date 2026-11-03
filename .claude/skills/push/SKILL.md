---
name: push
description: Đẩy mã nguồn của dự án lên GitHub (haunguyen99/AI_Anim, nhánh main; chỉnh sửa Spine Live vào nhánh spine-live): skill, tool, quy trình, tài liệu, mã các trang Lab. Dùng khi người dùng gõ /push, nói "push", "đẩy lên GitHub", "cập nhật repo". Không đẩy dữ liệu (model, video, FBX, trang đã build).
---

# /push: đẩy mã nguồn lên GitHub

Repo GitHub `main` **chỉ chứa mã nguồn**; nhánh `master` trên máy chứa cả dữ liệu làm việc nên **không bao giờ** đẩy `master`. Việc đẩy do `tools/push_source.py` làm: nó dựng một commit từ cây `origin/main` cộng các file nguồn trong danh sách cho phép (skill `.claude/skills/**`, `tools/**`, `docs/**`, `README.md`, `MAP.md`, `requirements.txt`, `.gitignore`, `work/clips.json`, và mã các Lab: `work/pose_lab`, `work/review_page`, `work/rig_lab`, `work/mesh_lab`), dùng chỉ mục tạm nên không đụng nhánh và không commit lẫn file đang làm dở. Trả lời bằng tiếng Việt.

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

## Quy tắc

- Không đẩy `master`, không `git push --force`, không đẩy dữ liệu (`work/*/pages`, `work/store`, models, clips, `.blend` / `.fbx` / video).
- `.claude/launch.json` và `.mcp.json` giữ nguyên bản trên GitHub (bản trên máy có cấu hình riêng). Muốn đổi hai file này, sửa trên GitHub qua một commit riêng và nói rõ với người dùng.
- Sửa danh sách cho phép / loại trừ: `ALLOW`, `DENY` đầu `tools/push_source.py`. Thêm loại file mới (vd thư mục Lab mới) thì thêm vào `ALLOW` rồi chạy `--dry-run` kiểm tra.
- Commit cục bộ trên `master` là việc khác: `/push` không commit hộ. Việc đẩy nội dung hiện tại trong thư mục làm việc, kể cả file chưa commit.
