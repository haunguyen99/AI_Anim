# Spine MCP server

Chuyển từ `E:\SpineAI` vào AI_Anim ngày 2026-10-26. Project Spine (vd HandTut của G-PirateGoldrush) nằm ở `work/spine/<game>/<anim>/`.

MCP server cho Spine 2D (editor 4.2.43). Cho phép Claude:
- gọi **Spine CLI**: export, import, xem thông tin, pack/unpack atlas, clean up animation;
- **đọc/sửa skeleton JSON**: xương, slot, animation, keyframe.

Mỗi lần sửa JSON, bản cũ được lưu vào thư mục `.spine_mcp_backups` cạnh file.

## Cách làm việc điển hình

1. `spine_export`: `.spine` → thư mục JSON
2. Sửa JSON bằng các tool `bone_*`, `slot_*`, `animation_*`, `keyframe_*`, `skeleton_set`
3. `spine_import`: JSON → **file `.spine` mới** (không import đè vào project gốc)
4. Mở project mới trong Spine để kiểm tra

## Danh sách tool

| Nhóm | Tool |
|---|---|
| Spine CLI | `spine_version`, `spine_project_info`, `spine_export`, `spine_import`, `spine_pack_atlas`, `spine_unpack_atlas`, `spine_clean_animations` |
| Đọc JSON | `skeleton_summary`, `skeleton_bone_tree`, `skeleton_get`, `slot_list`, `animation_get` |
| Sửa JSON | `skeleton_set`, `bone_add`, `bone_update`, `slot_update`, `animation_create`, `animation_rename`, `animation_delete`, `animation_scale_time`, `keyframe_set_bone`, `keyframe_set_slot`, `keyframe_remove` |

## Cấu hình

Biến môi trường:
- `SPINE_EXE`: đường dẫn `Spine.com` (mặc định `C:\Program Files\Spine\Spine.com`)
- `SPINE_VERSION`: phiên bản editor dùng khi chạy CLI (mặc định `4.2.43`)

### Claude Code (app này)
Server `spine` đã khai báo trong `.mcp.json` ở thư mục gốc dự án (file này không đẩy lên GitHub vì chứa đường dẫn trên máy). Trên máy khác, thêm một mục như dưới vào `.mcp.json` của bạn, sửa đường dẫn `uv.exe` và thư mục dự án, rồi mở lại session.

### Claude Desktop (tab Chat)
Thêm vào `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "spine": {
      "command": "C:\\Users\\HLC_2021\\.local\\bin\\uv.exe",
      "args": ["run", "--directory", "<thư mục dự án>\\tools\\spine_mcp", "spine-mcp"]
    }
  }
}
```

## Giới hạn
- Không điều khiển được cửa sổ Spine đang mở; mọi thao tác qua file và CLI.
- Đổi tên/xoá xương chưa có tool riêng (vì animation, slot, mesh tham chiếu theo tên). Dùng `skeleton_set` nếu thật cần.
- Export PNG/GIF/video: lưu file cài đặt export từ hộp thoại Export của Spine rồi truyền vào `settings_file`.
