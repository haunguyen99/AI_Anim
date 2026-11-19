---
name: reference-frolvy-open-linux
description: "Cách mở file .fv trong Frolvy trên máy Linux Mint (AppImage) và đóng cửa sổ thừa, không cần dò lại"
metadata:
  node_type: memory
  type: reference
  originSessionId: 9d661c91-4ffc-458f-8345-da65521a8c58
  modified: 2026-11-16T04:04:18.093Z
---

Máy Linux Mint 22 (Cinnamon, X11): Frolvy là `~/Applications/Frolvy-0.9.69-x86_64.AppImage`, không có `Frolvy-mcp.exe`, và cổng 9877 không nói JSON-RPC thô, nên `tools/frolvy_port.py` (Windows) không dùng được. Đừng mất thời gian dò cổng.

**Mở file .fv (một bước):** `tools/frolvy_open.sh "<đường dẫn .fv>"`. Lệnh chạy AppImage kèm `--no-sandbox` và đường dẫn file. Nó luôn mở cửa sổ Frolvy MỚI, tự lấy cổng MCP kế tiếp (9877 bận → 9878). Tiêu đề cửa sổ có dạng `Frolvy ... - <file>.fv  [MCP <cổng>]`.

**Liệt kê / đóng cửa sổ:** `wmctrl -l | grep -i frolvy` rồi `wmctrl -i -c <id>`. Cửa sổ untitled đóng thẳng, không hỏi lưu.

**Why:** 2026-11-16 mất nhiều phút dò cổng 9877 trước khi thử chạy AppImage kèm đường dẫn; người dùng bực vì chậm và nhờ lưu lại.
**How to apply:** Người dùng đưa đường dẫn .fv → chạy thẳng script, không dò. Muốn một cửa sổ thôi thì đóng cửa sổ cũ bằng wmctrl. Cổng của file vừa mở nằm trong tiêu đề cửa sổ. `frolvy_port.py` KHÔNG dùng được trên Linux (EXE Windows, ctypes.windll). Dùng `tools/frolvy_call.py <cổng> <file.py>` (xem [[reference-frolvy-linux-bridge]]).
