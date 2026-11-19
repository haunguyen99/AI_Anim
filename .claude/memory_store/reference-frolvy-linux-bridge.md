---
name: reference-frolvy-linux-bridge
description: "Chạy code / chụp viewport / undo trong Frolvy trên Linux: tools/frolvy_call.py <cổng> (dùng Frolvy-mcp trong AppImage đang mount); bẫy cổng, cửa sổ, open_scene"
metadata:
  node_type: memory
  type: reference
---

Trên Linux không có `Frolvy-mcp.exe` và không có MCP `frolvy` cho phiên, nhưng AppImage đang chạy có `/tmp/.mount_Frolvy*/usr/bin/Frolvy-mcp` (stdio). **`tools/frolvy_call.py <cổng> <file.py|->`** gọi nó với `DCC_MCP_PORT=<cổng>` và chạy file Python trong Frolvy (đối tượng `api`). Kết quả JSON, đọc trường `output`. Thêm `--tool get_scene_info | get_viewport_screenshot --out x.png | get_app_screenshot | list_panels | undo | show_panel --args '{"name":"Channel Box","open":false}'`.

- Cổng = `[MCP 98xx]` trong tiêu đề cửa sổ (`wmctrl -l | grep -i frolvy`). Cổng 9877 thường là cửa sổ của người dùng / phiên khác: KHÔNG đoán, đọc tiêu đề. `tools/frolvy_open.sh` mở cửa sổ mới tự lấy cổng kế tiếp; nó cũng khớp nhầm cửa sổ cùng tên file đang mở.
- Cửa sổ có thể đổi nội dung / đóng / Frolvy tự cập nhật (0.9.69 → 0.9.72 ngày 2026-11-16) giữa hai lượt: luôn `scene` kiểm trước khi sửa; chưa lưu thì mất. Người dùng thường tự lưu; hỏi trước khi lưu đè.
- `api.open_scene` trả False: muốn mở file thì mở bằng `frolvy_open.sh`, copy file vào /tmp nếu chỉ để đọc.
- Viewport nhỏ: đóng các panel (Channel Box, Graph Editor, Outliner, Attributes…) bằng `show_panel open:false`; `get_viewport_screenshot` ra ảnh ~800x400. Camera trợ giúp: `api.create_camera()` + `rename` + `set_transform`, `look_through(tên)`; xoá trước khi lưu.
- `undo` (một bước = một lần chạy execute_code có ghi). Bước chỉ-đọc không tạo bước undo.
- Một lần chạy cỡ 1000+ lệnh vẫn được (~50 s cho 13 key x 260 kênh); không thấy giới hạn 320.
- Bộ kiểm có sẵn: `work/runner_hybrid/anim/checks/` (README bên trong).
