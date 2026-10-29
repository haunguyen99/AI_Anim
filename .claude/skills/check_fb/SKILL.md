---
name: check_fb
description: The user has left review notes on a playblast review page and types /check_fb (optionally with a clip, e.g. "/check_fb reload"). Pick up every sent review round, fix ALL its notes in ONE new version, self-check with a quick render, then post the version. Replaces the old 10-minute polling loop.
---

# /check_fb: đã có feedback trên trang review

Người dùng gõ `/check_fb` khi đã ghi xong note **và** bấm "Gửi feedback cho AI" trên trang review. Không còn polling / CronCreate (người dùng bỏ 2026-10-22). Trả lời bằng tiếng Việt.

## Studio: ghi chú vẽ (nút ✎ trong viewport, 2026-10-28)

Bộ canh in mục `"kind": "rig_gate"` (nút Duyệt / Cần sửa ở một bước Rig) → làm theo `/rig` mục 2 phần Studio: duyệt thì tự làm bước kế, cần sửa thì sửa bước đó theo note, xong `studio_cmd.py gate-done`. Mục `"kind": "note"` → các bước dưới.

Người dùng vẽ khoanh trên viewport Studio (General / Rig / Anim), bấm **Gửi cho AI** trong panel "Ghi chú vẽ". Nếu phiên chat đang chạy nền `tools/notes_watch.py` (bật mỗi khi người dùng duyệt trong Studio: chỉ canh thư mục, không tốn lượt AI), Claude được gọi dậy ngay khi có ghi chú gửi; không thì người dùng gõ `/check_fb`. Góp ý ở tab **Góp ý cho AI** của Pose (lưu ở `work/store/<anim>_pose_lab/adjusts`) bộ canh cũng nhận (mục `kind: pose_adjust`, ngay khi bấm Gửi tất cả cho AI, hoặc 45 s sau góp ý cuối nếu chưa gửi): sửa thành version mới, rồi `tools/notes_watch.py --pose-done <ns> <clip> <version> "AI: <version mới>"`. Sửa xong thì bật lại bộ canh. Làm **trước** phần Review Lab bên dưới:
1. `.venv\Scripts\python.exe -I tools\studio_cmd.py notes [nhân vật] --out <scratchpad>
otes`: ghi chú đang mở (đã gửi hoặc chưa), ảnh JPEG khung nhìn + nét, `ctx` (chế độ, bước Rig, anim + frame, khớp đang chọn, camera) và `strokes_cm` (khung trước / bên / trên: điểm đầu, cuối, tâm của mỗi nét theo cm, trục Studio). Rig: đọc thêm `work/store/<id>_rig_lab/rig/gates.json`.
2. Xem từng ảnh, đọc nét theo `strokes_cm` (vạch ngang trên một đường = vị trí khớp mong muốn, mũi tên = chỗ khớp phải tới, dấu X = bỏ vị trí cũ), nêu cách hiểu trong chat. Không rõ thì hỏi một lần, gộp.
3. Sửa trên trang Studio đang mở của người dùng qua cầu nối (`studio_cmd.py clients` để lấy `--cid`; Rig: `rig lm`, rồi tính lại skin; Anim: `anim rot/pos/key`). Tự kiểm bằng `snap` cùng góc với ghi chú.
4. `note-done <id>` cho từng ghi chú đã sửa; báo ngắn đã sửa gì, số đo trước / sau.

 mỗi anim một artifact, db collections `rounds` + `notes`)

**Danh sách trang lấy từ sổ clip** (không còn bảng viết tay): chạy `.venv\Scripts\python.exe -I tools\clip_registry.py urls` (cột Review Lab, kèm Pose Lab và Rig Lab) hoặc đọc `work/clips.json`. Trang mới được đăng ký bằng `/new_clip` (`clip_registry.py set-url`).

## Các bước

1. **Tìm lượt đã gửi.** Nếu có argument thì chỉ xem trang đó, không thì xem mọi trang. Dùng `ArtifactData` query `rounds` với `where status == "sent"`. Không có lượt nào thì báo một dòng và dừng.
2. **Nhận việc.** Cập nhật round sang `status: "working"`, `aiNote` = một câu tóm tắt việc sẽ làm.
3. **Đọc TẤT CẢ note còn mở** của version đó: query `notes` theo `clip` + `version`, `status != "done"`, kể cả note thêm sau khi bấm gửi. Dùng `out_dir` vào scratchpad để note dài/strokes không tràn context. Note có circle strokes thì làm theo [[feedback-circled-notes]] (memory).
4. **Lập kế hoạch gộp:** gom note theo key/bộ phận, và một version mới phải sửa hết. Viết danh sách ngắn trong chat: `F9 vai trái: … | F15 trống: …`. Note mâu thuẫn hoặc không rõ thì hỏi người dùng **một lần, gộp mọi câu hỏi**, không gửi version nửa vời.
5. **Sửa và tự kiểm tra bằng render nhanh** (không playblast):
   - Sửa pose / key trên Pose Lab (hoặc bằng script key rồi nạp vào Pose Lab), rồi quay playblast nhanh các frame và góc có note: nút 🎞 trong Home (chọn ít camera, cỡ nhỏ) hoặc render frame lẻ, ghép bằng `tools/quick_sheet.py` (cần file `<view>_<frame>.png`) → đọc **một** ảnh `sheet.jpg`.
   - Không đọc từng PNG lẻ. Chỉ zoom/crop khi tấm sheet không đủ để thấy lỗi.
   - Chạy anatomy_check trên các key đã sửa.
6. **Render đầy đủ một lần** khi mọi note đã ổn trên sheet: chạy lại không có `quick=`, rồi playblast → thêm version vào CLIPS trong `work/review_page/index.html` → `split_pages.py` → publish trang (Artifact, cùng file path/URL).
7. **Đóng lượt:** các note đã sửa → `status: "done"`; round → `status: "fixed"`, `aiNote` = tóm tắt các thay đổi. Git commit (theo [[feedback-git-review-log]] (memory)): `<clip> <ver>: … (review <ver cũ> F.., F..)`. Cập nhật knowledge theo SKILL animation.
8. **Báo người dùng:** link trang, danh sách note → đã sửa gì, và nhắc: xem hết clip, ghi mọi lỗi rồi mới bấm gửi + `/check_fb`.
