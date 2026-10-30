# maya_mcp: MCP server cho Maya 2024

Claude điều khiển Maya 2024 đang mở trên máy này: chạy Python (maya.cmds), đọc scene, đặt/đọc key, mở/lưu, nhập/xuất FBX, chụp viewport.

```
Claude ──MCP(stdio)──> tools/maya_mcp (uv) ──TCP 127.0.0.1:7022──> maya_side/maya_mcp_listener.py (trong Maya)
```

Listener chỉ nghe trên 127.0.0.1, nên máy khác không gửi lệnh vào được. Code chạy ở luồng chính của Maya, dùng chung namespace `__main__`.

## Bật listener trong Maya (mỗi lần mở Maya)

Script Editor → tab Python → chạy:

```python
import sys; sys.path.insert(0, r"E:/AI Animation/tools/maya_mcp/maya_side")
import maya_mcp_listener; maya_mcp_listener.start()
```

Có thể kéo đoạn này lên shelf thành một nút. Cách khác là gọi tool `maya_launch`, tool này mở Maya có sẵn listener.
Muốn tắt: `maya_mcp_listener.stop()`. Đổi cổng: `start(port=...)` kèm biến môi trường `MAYA_MCP_PORT` cho server.

Maya chạy nền (mayapy, không giao diện): dùng `maya_mcp_listener.start(block=True)` sau `maya.standalone.initialize()`.

## Đăng ký

`.mcp.json` ở gốc dự án có server `maya` (`uv run --directory tools/maya_mcp maya-mcp`). Mở lại phiên Claude Code để nạp server.

## Tool

| Tool | Việc |
|---|---|
| `maya_ping`, `maya_launch` | kiểm tra kết nối / mở Maya có listener |
| `maya_exec`, `maya_eval` | chạy Python tùy ý; gán `result` để trả về |
| `maya_scene_info`, `maya_ls`, `maya_hierarchy` | đọc scene |
| `maya_get_attrs`, `maya_set_attrs` | đọc/ghi thuộc tính (đọc được tại một frame) |
| `maya_set_keys`, `maya_get_keys` | key; `tangent="step"` cho blocking |
| `maya_open`, `maya_save`, `maya_import_fbx`, `maya_export_fbx` | file |
| `maya_snapshot` | playblast một frame, trả ảnh PNG (cần Maya có giao diện) |

Đã kiểm 2026-10-27 với mayapy 2024: ping, exec, key, attr, hierarchy, FBX xuất→nhập (key giữ nguyên), save. Chưa kiểm `maya_snapshot` và `maya_launch` vì hai tool này cần Maya có giao diện.
