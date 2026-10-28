---
name: push
description: Đẩy mã nguồn của dự án lên GitHub (haunguyen99/AI_Anim, nhánh main): skill, tool, quy trình, tài liệu, mã các trang Lab. Dùng khi người dùng gõ /push, nói "push", "đẩy lên GitHub", "cập nhật repo". Không đẩy dữ liệu (model, video, FBX, trang đã build).
---

# /push: đẩy mã nguồn lên GitHub

Repo GitHub `main` **chỉ chứa mã nguồn**; nhánh `master` trên máy chứa cả dữ liệu làm việc nên **không bao giờ** đẩy `master`. Việc đẩy do `tools/push_source.py` làm: nó dựng một commit từ cây `origin/main` cộng các file nguồn trong danh sách cho phép (skill `.claude/skills/**`, `tools/**`, `docs/**`, `README.md`, `MAP.md`, `requirements.txt`, `.gitignore`, `work/clips.json`, và mã các Lab: `work/pose_lab`, `work/review_page`, `work/rig_lab`, `work/mesh_lab`), dùng chỉ mục tạm nên không đụng nhánh và không commit lẫn file đang làm dở. Trả lời bằng tiếng Việt.

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
