---
name: skillreport
description: Phân tích một (hoặc nhiều) phiên làm việc AI làm anim, rồi ra báo cáo hiệu quả (BAO_CAO.md + trang báo cáo kèm video tiến độ) và slide trình chiếu. Số liệu lấy từ log phiên Claude và sổ phiên bản Spine Live, video dựng lại từ đúng bản của từng lượt. Dùng khi người dùng gõ /skillreport, hoặc xin "báo cáo phiên làm việc", "phân tích phiên", "đánh giá hiệu quả AI", "làm slide báo cáo", "gộp các báo cáo thành slide".
---

# /skillreport: báo cáo phân tích phiên làm việc + slide

Trả lời bằng tiếng Việt. Mẫu đã duyệt: 3 báo cáo cừu (Cừu cầm ô, Cừu Sakura, Cừu đi học) và slide gộp
"Hiệu quả AI làm anim Spine" (2026-11-03). Danh sách báo cáo đã làm + link ở `REPORTS.md` (thêm dòng sau mỗi lần làm).

Nguyên tắc:
- **Mọi con số lấy từ log, không ước lượng.** Nói rõ nguồn và cách tính trong báo cáo.
- Điểm yếu nói thẳng, có ví dụ cụ thể (lượt nào, sai gì, ai phát hiện). Không khen chung chung.
- Video dựng lại từ chính bản đã lưu của từng lượt, không quay lại màn hình.
- Không chụp màn hình để báo cáo (CLAUDE.md). Bước tự kiểm video (xem 1 poster) thì được.

Đầu vào cần chốt (hỏi nếu người dùng chưa nói, gộp 1 câu):
1. Dự án nào (thư mục, vd `work/test/spine/CuuSakura/`), một hay nhiều dự án.
2. Ra gì: chỉ báo cáo, chỉ slide, hay cả hai (mặc định: cả hai; nhiều dự án thì slide gộp).

## 1. Tìm phiên (1 phút)
```bash
.venv/Scripts/python.exe -I tools/report/session_stats.py find <tên thư mục hoặc tên file json>
```
- In các log phiên có từ khoá + khoảng giờ. Một dự án có thể trải nhiều phiên hoặc nằm giữa một phiên dài làm việc khác:
  chọn khung giờ `--from` / `--to` cho đúng đoạn của dự án (đọc lướt prompt đầu / cuối).
- Người dùng đã xoá phiên trong app thì log `.jsonl` thường **vẫn còn** ở `~/.claude/projects/<dự án>/` (Hộp quà 30/10 tìm lại được như vậy).
  Mất hẳn thì dựng lại từ sổ phiên bản Spine Live + mục Bài học trong skill + MAP + git log, và ghi rõ "không có log phiên".
- **Phiên fork** (nhiều phiên tách từ một phiên gốc, chạy song song): mỗi log fork chép lại các lượt trước điểm fork; chạy `stats` từng phiên với `--from` = giờ fork để không đếm trùng. "Người" của các phiên song song chồng nhau: báo cáo AI gen cộng được, "người" thì không; nêu thêm "AI gen trong khoảng thời gian trôi" (vd G-LumberCity 3 g 18′ trong 2 g 24′).
- Log `.jsonl` đã bị xoá hẳn (chỉ còn `<id>.desktop-released.json` "reason: delete"): dựng lại mốc từ `git log` (giờ commit, tag duyệt, lời người dùng trích trong commit) + `director_log.md`, chỉ báo **thời gian trôi**, ghi rõ "không có log".
- Ảnh người dùng dán (nét vẽ góp ý) nằm ở `%TEMP%/claude/<dự án>/<id phiên>/images/N.png`: dùng làm minh hoạ.

## 2. Số liệu (2 phút)
```bash
.venv/Scripts/python.exe -I tools/report/session_stats.py stats --session <id> [--session <id2>] \
   --from "YYYY-MM-DD HH:MM" --to "..." --versions <file json skeleton> --out <thư mục dự án>/_review
```
In từng lượt: giờ, AI gen, chờ trả lời, thời gian người sau lượt, prompt, câu trả lời cuối của AI, các lần ghi Spine Live
của AI trong lượt và của **người** giữa hai lượt (key pose, sửa curve, xoá key = can thiệp tay). Ghi `_review/stats.json` + `timeline.md`.

Đọc bảng rồi gán lượt vào giai đoạn, chạy lại với `--phases "1-4=Rig,5-10=Idle,11=Khác,12-16=Active,17=Xuất"` để có tổng theo giai đoạn.

Quy tắc tính (đã thống nhất, giữ nguyên để các báo cáo so được):
- AI gen = prompt → tin nhắn cuối của AI trong lượt, trừ lúc chờ người trả lời câu hỏi (AskUserQuestion).
- Người = khoảng giữa hai lượt, chỉ tính khi ≤ 15 phút; dài hơn là nghỉ (ghi khoảng nghỉ vào báo cáo).
- Thời gian làm việc thực = AI gen + người + chờ trả lời.
- Lượt không gen gì (mở trang, hỏi link) vẫn đếm là lượt prompt, ghi chú riêng.
- Việc ngoài anim xen vào (sửa công cụ Spine Live, mở lại Home) tách thành giai đoạn "Việc khác".

Đã kiểm trên Cừu đi học: 17 lượt, gen 50′, người 41′15″, chờ trả lời 7′13″, Spine Live AI 34 / người 46 (khớp báo cáo tay).

## 3. Chọn mốc + dựng video (5–10 phút)
Mốc = mỗi thay đổi lớn: rig bản đầu, rig chốt, idle bản đầu, mỗi lượt sửa idle / active có thay đổi nhìn thấy được,
bản ngay sau khi người tự key tay, bản giao. Thường 10–12 mốc. Lấy số phiên bản `#N` = lần ghi AI **cuối** của lượt
(cột "Spine Live AI ghi" trong bảng), hoặc lần ghi người cuối nếu mốc là bản người sửa.

Viết `<dự án>/_review/spec.json` (mẫu và giải thích trong đầu `tools/report/render_versions.py`), tên video `NN_<giai đoạn>_vNN`.
Cần Home chạy và một trang Spine Live mở: `preview_start` với url `http://127.0.0.1:8780/spine?json=<file json>`.
```bash
.venv/Scripts/python.exe -I tools/report/render_versions.py <dự án>/_review/spec.json
```
- Ra `_review/v/<tên>.mp4` + `<tên>.jpg` (poster). Active phát idle cuối → active → idle đầu để thấy chỗ nối; idle 3 vòng.
- Thêm `compare` (hstack các bản idle / active cạnh nhau) khi cần 1 video so trước-sau.
- Xem 1 poster để chắc hình đúng (ảnh có thanh tiêu đề + số frame).
- Dự án không có sổ Spine Live (vd rig dở như Hộp quà): đổi GIF / ảnh có sẵn ở `preview/` sang mp4:
  `ffmpeg -i x.gif -movflags +faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" x.mp4`.
- Dự án 3D (Studio / Pose Lab / Frolvy): dùng video review đã render ở từng mốc (`<clip>/review/*.mp4`, GIF → mp4), poster bằng `ffmpeg -ss 0.6 -frames:v 1`. Video 3D là khung ngang nhiều góc: slide video xếp lưới 2×2, ảnh 808×230 (mẫu `work/g_lumbercity/_review/slides/project/slides/idle1.html`).
- Upload lên artifact hay lỗi ECONNRESET khi gửi nhiều file một lần: trang báo cáo đăng trang trước rồi thêm `files` từng cặp mp4 + jpg; asset của slide ≤ 6 file / lần, file lỗi 2 lần thì bỏ, thay bằng ảnh tĩnh.

## 4. Viết BAO_CAO.md (`<dự án>/_review/BAO_CAO.md`)
Cấu trúc (mẫu đầy đủ: `work/test/spine/MascotBackToSchool/_review/BAO_CAO.md`):
1. **Thời gian**: bảng AI gen / người / chờ trả lời / tổng có mặt (+ ngày giờ các buổi); bảng AI gen theo giai đoạn.
2. **Số lần gen**: lượt prompt (bao nhiêu lượt có thay đổi), số lần AI ghi file theo giai đoạn, số lần người ghi file.
3. **Các giai đoạn chuyển biến lớn**: bảng # · Lượt (giờ, phút gen) · Yêu cầu / góp ý của người · AI thay đổi gì · Video.
   Ghi rõ lượt nào là **lỗi của AI** và lượt **người tự key / sửa**.
4. **Điểm mạnh của AI**: có số đo (phút, px, số xương, số mesh).
5. **Điểm yếu của AI**: mỗi điểm một ví dụ cụ thể; so với case trước nếu lặp lại.
6. **Người vẫn phải tự làm**: bảng Khi nào · Làm gì · Số thao tác / thời gian; kèm lý do suy ra + gợi ý lần sau.
7. **Video preview**: bảng file → nội dung.

## 5. Trang báo cáo (artifact)
Load skill `artifact-design` trước, rồi dựng trang từ mẫu `templates/report_page.html` (Cừu cầm ô): header + 4 ô số liệu,
bảng thời gian theo giai đoạn (thanh AI gen / người), bảng từng lượt gen (chip mới / sửa / duyệt / giao), lưới video
(`<video src="v/..." controls loop muted playsinline>`), "Người vẫn phải làm gì", hai cột Mạnh / Yếu, "Cách tính".
Đăng bằng Artifact với `files` = `{"v/<tên>.mp4": "<dự án>/_review/v/<tên>.mp4", ...}`, icon `chart`. Tiêu đề "Báo cáo <nhân vật>".

## 6. Slide (Slides artifact)
1. `Artifact` quickstart `intent: "slides"` → tạo deck từ type Slides (`auto_open: "after_first_write"`), đọc hướng dẫn type trả về.
2. Upload mọi mp4 + jpg poster + ảnh minh hoạ: `publish` `asset: true` `file_paths` (≤ 25 file / lần). Ghi lại `/_blob/<id>` từng file.
3. Viết `project/deck.json` + từng `project/slides/<id>.html` trong scratchpad, đăng 3 slide / lần. Mẫu đã duyệt ở
   `templates/slides/` (blob id trong mẫu là của deck cũ: thay bằng id vừa upload).

Bố cục deck (một phiên ≈ 10 slide; gộp N phiên ≈ 3 + 4N + 4):
| Slide | Mẫu | Nội dung |
|---|---|---|
| Bìa | `cover.html` | nền tối, tiêu đề, 3 video bản giao bên phải |
| Tổng quan | `tongquan.html` | bảng so các phiên: ngày, thời gian thực, AI gen, lượt, lượt sửa active, người tự key, bản giao |
| Giai đoạn | `giaidoan.html` | bảng AI gen theo giai đoạn + 1 ô số nổi bật |
| Tóm tắt từng nhân vật | `umb.html` | 4 ô số liệu + 2 cột Làm tốt / Còn vướng (3 ý mỗi cột) |
| Video tiến độ | `umb1.html` (4 video), `sak3.html` (3 video) | nền tối, ≤ 4 clip / slide, mỗi clip: tiêu đề, `#bản · giờ`, 1 câu ≤ 60 ký tự |
| Mạnh / Yếu chung | `manh.html`, `yeu.html` | lưới 2×2 thẻ: số lớn + tiêu đề + 1 câu |
| Người phải làm | `nguoi.html` | bảng việc × nhân vật |
| Nhược điểm nổi bật | `gift.html` (statement nền cam), `giftlog.html` (bảng diễn biến), `giftimg.html` (5 ảnh góp ý), `giftwhy.html` (lý do + ảnh) | dùng khi có ca không hiệu quả |
| Đề xuất | `dexuat.html` | 2 cột, 3 ý mỗi cột |

Quy ước nhìn: font Be Vietnam Pro + JetBrains Mono (số); nền sáng `#F6F3EE`, nền tối `#13203A`, nhấn vàng `#F0B13B`
(chữ nhấn trên nền sáng `#8A5208`), tốt `#2E7D5B`, vướng `#C2492E`, ca không hiệu quả nền `#E5603F`; cỡ chữ 96 / 64 / 44 / 32 / 24;
số trang "n / tổng" góc phải dưới; ghi chú người nói (`<aside>`) cho số liệu phụ. Video: `<img src=poster data-video=clip>`
khung 392×420 `object-fit:contain`, nền khung = màu nền của video (`#1D3554` runtime Spine Live, `#ECEFF4` Spine CLI).
Không tự kiểm lại slide sau khi đăng (luật của type Slides) trừ khi người dùng yêu cầu.

## 7. Canva / trình chiếu
- Phiên chưa có kết nối Canva: trong trang slide dùng Share › Export › Send to (nếu có Canva), hoặc tải .pptx rồi nhập vào Canva.
  File .pptx chỉ giữ ảnh poster, không giữ video: đề nghị chép các mp4 (`_review/v/`) ra một thư mục để kéo vào Canva.
- Slide đăng ở chế độ riêng tư: nhắc người dùng chia sẻ từ menu Share trước khi gửi người khác.

## 8. Xong
- Thêm một dòng vào `REPORTS.md` (dự án, ngày, link báo cáo / slide, điều mới rút ra).
- Bài học mới về cách làm anim (không phải về báo cáo) ghi vào CASES / Bài học của skill tương ứng (`skillidle`, `skillactive`, `spine2d`).
- Báo người dùng: link + 2–3 con số chính + điểm yếu lớn nhất.
