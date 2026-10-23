---
name: fb
description: The user has left review notes on a playblast review page and types /fb (optionally with a clip, e.g. "/fb reload"). Pick up every sent review round, fix ALL its notes in ONE new version, self-check with a quick render, then post the version. Replaces the old 10-minute polling loop.
---

# /fb: đã có feedback trên trang review

Người dùng gõ `/fb` khi đã ghi xong note **và** bấm "Gửi feedback cho AI" trên trang review. Không còn polling / CronCreate (người dùng bỏ 2026-10-22). Trả lời bằng tiếng Việt.

## Trang Review Lab (tên cũ: trang review; mỗi anim một artifact, db collections `rounds` + `notes`)

**Danh sách trang lấy từ sổ clip** (không còn bảng viết tay): chạy `.venv\Scripts\python.exe -I tools\clip_registry.py urls` (cột Review Lab, kèm Pose Lab và Rig Lab) hoặc đọc `work/clips.json`. Trang mới được đăng ký bằng `/new_clip` (`clip_registry.py set-url`).

## Các bước

1. **Tìm lượt đã gửi.** Nếu có argument thì chỉ xem trang đó, không thì xem mọi trang. Dùng `ArtifactData` query `rounds` với `where status == "sent"`. Không có lượt nào thì báo một dòng và dừng.
2. **Nhận việc.** Cập nhật round sang `status: "working"`, `aiNote` = một câu tóm tắt việc sẽ làm.
3. **Đọc TẤT CẢ note còn mở** của version đó: query `notes` theo `clip` + `version`, `status != "done"`, kể cả note thêm sau khi bấm gửi. Dùng `out_dir` vào scratchpad để note dài/strokes không tràn context. Note có circle strokes thì làm theo [[feedback-circled-notes]] (memory).
4. **Lập kế hoạch gộp:** gom note theo key/bộ phận, và một version mới phải sửa hết. Viết danh sách ngắn trong chat: `F9 vai trái: … | F15 trống: …`. Note mâu thuẫn hoặc không rõ thì hỏi người dùng **một lần, gộp mọi câu hỏi**, không gửi version nửa vời.
5. **Sửa và tự kiểm tra bằng render nhanh** (không playblast):
   - SDR06: `blender -b work/blender/sdr06_char.blend --python work/sdr06/<blocking|spline>.py -- <ver> <clip> quick=<các frame note>,<frame kề> views=<góc note>`
   - Sau đó `python tools/quick_sheet.py work/sdr06/pb_<clip>_<ver>_quick` → đọc **một** ảnh `sheet.jpg`.
   - Clip khác: render đúng frame và góc cần xem ở độ phân giải thấp, rồi ghép bằng `tools/quick_sheet.py` (cần file `<view>_<frame>.png`).
   - Không đọc từng PNG lẻ. Chỉ zoom/crop khi tấm sheet không đủ để thấy lỗi.
   - Chạy anatomy_check trên các key đã sửa.
6. **Render đầy đủ một lần** khi mọi note đã ổn trên sheet: chạy lại không có `quick=`, rồi playblast → thêm version vào CLIPS trong `work/review_page/index.html` → `split_pages.py` → publish trang (Artifact, cùng file path/URL).
7. **Đóng lượt:** các note đã sửa → `status: "done"`; round → `status: "fixed"`, `aiNote` = tóm tắt các thay đổi. Git commit (theo [[feedback-git-review-log]] (memory)): `<clip> <ver>: … (review <ver cũ> F.., F..)`. Cập nhật knowledge theo SKILL ai-animation.
8. **Báo người dùng:** link trang, danh sách note → đã sửa gì, và nhắc: xem hết clip, ghi mọi lỗi rồi mới bấm gửi + `/fb`.
