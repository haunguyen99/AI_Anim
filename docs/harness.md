# Harness của repo (2026-11-20)

Khi Claude chạy bằng key API (Paseo, VS Code, terminal) thì vẫn là Claude Code: đọc/sửa file, chạy lệnh, skill, CLAUDE.md, hook, subagent đều còn. Thứ mất là các công cụ **chỉ app Claude desktop có**. Harness của repo bù lại phần đó, để phiên ở đâu cũng làm việc giống nhau.

## Gồm gì

| Phần | File | Việc |
|---|---|---|
| MCP server `harness` | `tools/harness/mcp_server.py` (khai trong `.mcp.json`) | Công cụ thay thế, không cần cài thư viện |
| Hook đầu phiên | `tools/harness/env_hook.py` (`.claude/settings.json`, SessionStart) | Ngoài app desktop: nạp bảng "thiếu X thì dùng Y"; trong app: im lặng |
| Trang Home | `/harness/` trên Home (`tools/home/server.py`), file ở `work/_harness/` | Kế hoạch các phiên + trang đã đăng, tự tải lại 5 giây |

## Thiếu gì, dùng gì thay

| Công cụ app desktop | Thay bằng |
|---|---|
| Danh sách việc + ô bước tiếp theo (`update_plan`, `wrap_up`) | `harness plan`, `harness wrap_up` (in khối tóm tắt cuối câu trả lời) |
| Artifact | `harness publish_page` → `http://127.0.0.1:8780/harness/<tên>/`; anim thì Review Lab (`studio` → `anim playblast`) |
| Trình duyệt trong app | Paseo: công cụ `browser_*` của Paseo; Studio: `harness studio` / `studio_snap` |
| Chụp màn hình, computer-use | `harness studio_snap` (viewport Studio), ảnh render đọc bằng Read |
| `start_session` (chia phiên) | `harness session` (Paseo: run / ls / logs / send / mode / stop); việc ngắn: công cụ Agent |
| visualize (sơ đồ trong chat) | Viết HTML rồi `publish_page` |
| Connector claude.ai (Gmail, Drive, Figma, Docs) | Không có với key API: làm trong app desktop |
| Skill anthropic (pdf, docx, xlsx, pptx) | Chỉ skill trong `.claude/skills/` của repo |
| SendUserFile, thông báo điện thoại | Đưa đường dẫn file / link Home trong câu trả lời |

## Kiểm nhanh

```powershell
.venv/Scripts/python.exe -I tools/harness/mcp_server.py --selftest
```

Trong phiên Claude: gọi `mcp__harness__env`. Lần đầu mở repo, Claude Code hỏi có bật MCP server của dự án không: chọn đồng ý.

## Ghi chú

- Nhận biết môi trường theo biến môi trường: app desktop đặt `CLAUDE_CODE_ENTRYPOINT=claude-desktop`; Paseo nhận theo biến có chữ `PASEO` (chưa kiểm trên máy có Paseo, nếu báo nhầm "cli" thì vẫn dùng được, chỉ tên khác).
- `.mcp.json` trỏ `.venv/Scripts/python.exe` (Windows). Máy Linux: đổi thành `.venv/bin/python`.
- Thêm công cụ: viết hàm `tool_<tên>` và thêm một dòng vào `TOOLS` trong `mcp_server.py`, cập nhật bảng trên.
