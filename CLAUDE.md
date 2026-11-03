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

## Bộ nhớ Claude (giữ qua đổi tài khoản / máy)
- Bản sao bộ nhớ ở `.claude/memory_store/` (trong git). Nếu `MEMORY.md` trong bộ nhớ phiên đang trống hoặc thiếu, chạy `.venv/Scripts/python.exe -I tools/claude_memory.py restore` rồi đọc `.claude/memory_store/MEMORY.md`.
- Sau khi ghi / sửa memory: chạy `tools/claude_memory.py backup` để bản sao luôn mới.

## Trả lời
- Mọi câu trả lời bằng tiếng Việt.
