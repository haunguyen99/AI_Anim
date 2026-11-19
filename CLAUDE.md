# Quy tắc chung cho mọi phiên Claude trong dự án AI Animation

Đọc `MAP.md` trước khi tạo file mới. Luật làm anim nằm ở `.claude/skills/animation/knowledge/CORE.md`.

## Điều khiển Studio: dùng cầu nối trước
- Việc trong Studio (ẩn/hiện mesh, chọn, xoay/dời joint, về bind pose, focus mesh / rig / pose, bật lớp scene (nhân vật) / anim, chạy lệnh bất kỳ: `cmds` liệt kê): `.venv/Scripts/python.exe -I tools/studio_cmd.py …` (xem đầu file). Lệnh tới trang Studio đang mở ở bất kỳ trình duyệt nào (Chrome của người dùng hoặc trình duyệt trong app), ~4 ms mỗi lệnh; gom nhiều lệnh bằng `";"` trong một lần chạy. Kiểm bằng `studio_cmd.py state`. Góp ý vẽ của người dùng (nút ✎ trong viewport, mọi chế độ): `studio_cmd.py notes [nhân vật] --out <scratchpad>` in ghi chú đang mở + ghi ảnh khung nhìn kèm nét vẽ, xem ảnh trước khi sửa; sửa xong `note-done <id>`. Rig (`rig lms|lm|sel|step`), anim (`anim frame|read|rot|pos|key|unkey|versions|version`), `view`, `undo`, `snap` (ảnh viewport để tự kiểm) cũng qua cầu nối (W2). Workspace chỉ là bố cục: không cần đổi workspace để chạy lệnh Rig / Pose.
- Chỉ dùng công cụ trình duyệt của Claude khi cầu nối chưa có lệnh cần (thì thêm lệnh vào `tools/studio/modules/bridge.js`), hoặc để test giao diện. Cầu nối chỉ có lệnh có tên, không chạy mã tuỳ ý.

## Trình duyệt (Studio, Home, các Lab, trang review)
- **Chỉ chụp màn hình khi người dùng yêu cầu** (người dùng, 2026-10-27). Người dùng xem trực tiếp trên trang nên thấy ngay mọi thay đổi.
- Kiểm tra kết quả bằng `javascript_tool`, `read_page` hoặc `find` (tên object, ẩn/hiện, đang chọn gì, lỗi console), rồi báo ngắn bằng chữ.
- Bấm theo `ref` (từ `find` / `read_page`) hoặc gọi lệnh trên trang bằng JS, không đọc tọa độ từ ảnh chụp.
- Việc nhỏ (xóa, ẩn, đổi tên): đọc đủ tên object trước, làm trong một lượt, không chờ từng bước.
- Không thuộc quy tắc này: các bản render / playblast trong quy trình anim (quick render, so REF|ANIM, kiểm giải phẫu). Đó là bước tự kiểm tra pose, không phải chụp màn hình để báo cáo.

## Làm việc nhanh (người dùng, 2026-11-11: "tối ưu cách làm việc để đạt tốc độ nhanh nhất")
- Việc đã giao rõ thì làm luôn: một lượt xem (đếm cái sẽ đụng tới), rồi một lượt làm + kiểm; không dò từng bước nhỏ. Lệnh độc lập gọi chung một lượt, lệnh phụ thuộc nối bằng `;` trong một lần Bash. Người dùng đã ra lệnh thì không hỏi lại.
- Frolvy: mở đầu bằng `.venv/Scripts/python.exe -I tools/frolvy_port.py scene` (file đang mở, `*` = chưa lưu, layer, key). Người dùng có thể mở lại Frolvy giữa hai lượt, scene có thể đã khác (đừng giả định). Việc hay gặp có lệnh một bước: `keys <tên>`, `clear <tên>` (xóa key + về pose mặc định), `reset <tên>` (xem đầu `tools/frolvy_port.py`). Có công cụ `frolvy` trực tiếp thì gọi `anim_ops` qua `execute_code`. Không đụng cổng của phiên khác (9878…).
- Việc nào làm lần thứ hai thì làm thành lệnh một bước. Không đọc lại tài liệu / memory đã đọc trong phiên; ghi kiến thức một lần ở cuối việc. Báo trước bước nào lâu.

## Chạy ngoài app Claude desktop (Paseo, VS Code, terminal)
- Không có công cụ riêng của app (danh sách việc, wrap_up, Artifact, trình duyệt trong app, start_session…). Dùng MCP `harness` của repo thay: `plan` / `wrap_up` (hiện ở Home `/harness/`), `publish_page` thay Artifact, `studio` / `studio_snap`, `session` (phiên con Paseo). Hook đầu phiên tự nạp bảng thay thế. Chi tiết: `docs/harness.md`.

## Bộ nhớ Claude (giữ qua đổi tài khoản / máy)
- Bản sao bộ nhớ ở `.claude/memory_store/` (trong git). Nếu `MEMORY.md` trong bộ nhớ phiên đang trống hoặc thiếu, chạy `.venv/Scripts/python.exe -I tools/claude_memory.py restore` rồi đọc `.claude/memory_store/MEMORY.md`.
- Sau khi ghi / sửa memory: chạy `tools/claude_memory.py backup` để bản sao luôn mới.

## VS Code + Claude Code (máy mới / người mới)
- Team dùng được Claude trong VS Code (extension `anthropic.claude-code`), song song với app Claude desktop. Cài và cấu hình theo `docs/vscode_pilot.md` mục 7: `tools/setup_vscode.ps1 -Install` cài VS Code + extension; `-Endpoint lan` (IP LAN `http://192.168.10.29:40741`, trong công ty) hoặc `-Endpoint public` (`https://llmpro.horusjsc.com`, ở ngoài).
- Mức suy nghĩ mặc định = **high** cho Claude Code và Paseo (`tools/ai_effort_high.py`, `setup_vscode.ps1` tự chạy); "medium" làm việc khó hời hợt. Mỗi việc lớn một phiên mới.
- Key `llmpro` chỉ để trong `~/.claude/settings.json` của từng máy: không ghi vào repo, không in ra chat. Khi người dùng nhờ cài, chạy script, hỏi trước khi cài, và nhắc khởi động lại VS Code / app sau khi đổi endpoint.
- Việc cần Artifact (trang review, Pose Lab trên claude.ai), trình duyệt trong app hay chia session: làm trong app Claude desktop.

## Trả lời
- Mọi câu trả lời bằng tiếng Việt.
