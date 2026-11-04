---
name: director
description: Gọi agent Animation Director chấm một anim hoặc một rig ngay khi cần, ngoài các mốc tự động. Dùng khi người dùng gõ /director (vd "/director sdr01_shoot", "/director gaygor_walk blocking", "/director zom2_map3 skin"), hoặc nói "gọi director", "nhờ director check", "director xem giúp", "check lại anim này", "chấm bản này". Gom đầu vào (brief, ref, version, ảnh render, số đo), gọi subagent animation-director, báo kết quả, rồi hỏi có sửa không.
---

# /director: gọi Animation Director chấm khi cần

Agent: `.claude/agents/animation-director.md` (chỉ xem, không sửa). Các mốc tự động đã có trong skill `animation`, `/rig`, `/check_fb`; skill này để **gọi tay** bất cứ lúc nào. Trả lời bằng tiếng Việt.

## Cách gõ
`/director [clip hoặc nhân vật] [mốc] [ghi chú]`
- Clip: id trong `work/clips.json` (khớp một phần được, "walk" → `gaygor_walk`). Nhân vật (id Studio / Rig) = chấm rig.
- Mốc: `analysis` | `p0` | `blocking` | `spline` | `polish` | `pre-export` | `rig-joints` | `rig-skin` | `rig-test`. Người dùng nói "skin" = `rig-skin`, "khớp" = `rig-joints`, "thử khớp / gập" = `rig-test`.
- Không có tham số: lấy cái đang mở trong Studio (`studio_cmd.py clients` → `state` + `anim info`). Không có Studio thì hỏi một câu: chấm clip nào.
- Ghi chú (tuỳ chọn): người dùng muốn director chú ý gì ("xem tay trái F10–F15", "so với b8").

## Các bước
1. **Xác định đối tượng + mốc.** Clip: đọc `stage` + `dir` trong `clips.json`, version mới nhất (`studio_cmd.py anim versions` nếu đang mở, hoặc thư mục `block/`, `spline/`, `polish/` mới nhất trong `dir`). Không ghi mốc thì suy từ `stage` / tên version (`b*` = blocking, `s*` = spline, `p*` / `polish*` = polish, `stage: export` = pre-export). Nói một dòng: "Director chấm <clip> <ver>, mốc <mốc>".
2. **Gom đầu vào** (đường dẫn, không chép nội dung vào prompt):
   - Brief / thiết kế (`brief.md`, `analysis.md`, `*_analysis.md`), ref (video, ảnh key, concept), camera game của nhân vật.
   - Ảnh của bản cần chấm. Có sẵn sheet / playblast mới hơn version thì dùng. Không có, Studio đang mở bản đó: tự chụp vào scratchpad bằng cầu nối, **camera game trước**, rồi top và phía tay cầm prop, ≥ 512 px, các frame key (`anim frame N ";" view … ";" snap <scratchpad>/<view>_<N>.png 768x768`), ghép bằng `tools/quick_sheet.py`. Ghi lại frame + view lúc đầu và trả về như cũ khi chụp xong.
   - Rig: kết quả `.venv/Scripts/python.exe -I work/rig_lab/lbs_test.py <id>` + ảnh `--wire` cận các khớp có dòng BAD (ra scratchpad). Rig FBX của team: `rigcheck/report.md` + ảnh test nếu có. Rig Frolvy: ảnh `mcp__frolvy__get_viewport_screenshot` lưu ra scratchpad (agent không gọi được MCP).
   - Số đo QA đã có, `director_log.md` cũ của clip (hoặc `work/rig_lab/director/<id>.md`).
   Chụp + đo mất khoảng 1–2 phút, director chấm khoảng 3–4 phút: báo người dùng trước.
3. **Gọi agent:** Agent tool, `subagent_type: animation-director`, prompt gồm: clip / nhân vật, version, mốc, danh sách đường dẫn ở bước 2, scratchpad, ghi chú của người dùng, góc nào chưa có ảnh. Chạy nền và chờ thông báo, không đoán kết quả.
4. **Kiểm lỗi nặng nhất trước khi báo:** lỗi mức A mà director đo bằng số thì xác nhận nhanh nguồn gốc (script, key, số đo). Director sai thì nói rõ.
5. **Báo người dùng:** kết luận (Duyệt / Cần sửa / Chặn), bảng lỗi rút gọn (frame, bộ phận, lỗi, mức), phần nên giữ, đường dẫn nhật ký. Đang mở Studio thì nhảy tới frame lỗi nặng nhất và chọn khớp đó (`anim frame` + `anim select`) để người dùng xem ngay.
6. **Hỏi bước tiếp** (một câu): sửa các lỗi mức A thành version mới, chỉ ghi nhận, hay người dùng không đồng ý điểm nào. Người dùng không đồng ý / bỏ qua lỗi nào → ghi vào `knowledge/details/director_standards.md` (`#severity` + dòng `#calibration`), đó là cách director học.

## Quy tắc
- Không sửa anim / rig trong skill này; sửa chỉ khi người dùng đồng ý, theo skill `animation` / `/rig` / `/check_fb`, rồi gọi lại director.
- Không chụp màn hình trình duyệt để báo cáo. `snap` viewport và ảnh render là đầu vào cho director, được phép.
- Chấm nhiều clip một lần ("/director tất cả clip Lumber"): một agent cho mỗi clip, chạy song song, báo gộp một bảng.
