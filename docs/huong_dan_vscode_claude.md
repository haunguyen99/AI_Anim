# Hướng dẫn dùng Claude Code trong VS Code (team Animation)

Cập nhật: 2026-11-05 · Người liên hệ: Nguyễn Văn Hậu (lead Anim)

Claude Code chạy được ngay trong VS Code. Bạn vừa nói chuyện với AI, vừa xem file, ảnh, video và git ở cùng một cửa sổ. Bản này dùng chung bộ quy tắc, skill, bộ nhớ và kết nối phần mềm (Frolvy, Maya, Spine, HorusChat, ComfyUI) với app Claude desktop. Bạn có thể dùng song song với app desktop.

---

## 1. Chuẩn bị

- Máy Windows 10/11, có `git` và repo **AI Animation** (vd `E:\AI Animation`).
- **Key AI:** xin anh Hậu. Key là của riêng bạn: **không** gửi lên nhóm chat, **không** đưa vào repo hay git.
- Ngồi trong mạng công ty thì dùng đường LAN (nhanh hơn ~15–20 %). Ở ngoài thì dùng đường Internet (mục 6).

## 2. Đặt key (làm một lần)

Tạo file `C:\Users\<tên-máy-bạn>\.claude\settings.json` (tạo thư mục `.claude` nếu chưa có) với nội dung:

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "<key anh Hậu cấp>",
    "ANTHROPIC_BASE_URL": "http://192.168.10.29:40741",
    "ANTHROPIC_MODEL": "claude-opus[1m]"
  }
}
```

## 3. Cài VS Code + extension Claude Code

Mở **PowerShell** trong thư mục repo (chuột phải vào thư mục → *Open in Terminal*), chạy:

```powershell
powershell -ExecutionPolicy Bypass -File tools/setup_vscode.ps1 -Install -Endpoint lan
```

Script làm các việc sau:
- Cài **VS Code** (gói chính thức của Microsoft qua winget, cài cho tài khoản của bạn, không cần quyền admin).
- Cài extension **Claude Code** (`anthropic.claude-code`, nhà phát hành Anthropic).
- Kiểm tra key đã có chưa (không in key ra), đặt đường LAN, và sao lưu `settings.json` trước khi sửa.

Chạy không có tham số thì script chỉ kiểm tra máy, không cài gì:
`powershell -ExecutionPolicy Bypass -File tools/setup_vscode.ps1`

<details>
<summary>Cài tay (nếu không chạy được script)</summary>

```powershell
winget install --id Microsoft.VisualStudioCode -e --scope user
code --install-extension anthropic.claude-code
```
</details>

Máy mới thì nạp thêm bộ nhớ dự án cho Claude:

```powershell
.venv/Scripts/python.exe -I tools/claude_memory.py restore
```

## 4. Mở lần đầu

1. Mở repo: `code "E:\AI Animation"`, hoặc mở VS Code rồi vào *File → Open Folder*.
2. Bấm biểu tượng **Claude ✱** ở góc trên phải vùng soạn thảo hoặc thanh bên trái. Khung chat **Claude Code** hiện ra.
3. Trong ô chat, gõ `/` → chọn **MCP** → bật các server của dự án. Đúng là thấy **Connected** cho frolvy, maya, spine, horuschat, comfyui (rocketchat là chat cũ, tắt cũng được).
4. Thử: *"Đọc MAP.md, cho biết clip nào đang chờ góp ý"*.

## 5. Dùng hằng ngày

| Muốn | Làm |
|---|---|
| Nhờ AI làm việc | Gõ tiếng Việt vào ô chat, Enter |
| Gắn file / ảnh render | Gõ `@` chọn file, hoặc bấm `+`, hoặc giữ `Shift` rồi kéo ảnh vào ô chat |
| Gọi skill | Gõ `/`: `/director`, `/new_clip`, `/check_fb`, `/studio`, `/project`… |
| Hỏi về đoạn đang xem | Bôi đen trong editor, Claude tự lấy làm ngữ cảnh (hoặc `Alt+K`) |
| Đổi mức suy nghĩ | Bấm nút model `claude-opus[1m] Medium`: việc nhỏ Low/Medium, việc khó High |
| Đổi chế độ quyền | Nút `Auto` (tự làm) / `Manual` (duyệt từng bước) / `Plan` (lập kế hoạch trước) |
| Cuộc trò chuyện mới / xem lại cũ | Biểu tượng ⊕ / 🕘 ở góc trên khung chat |
| Xem ảnh, video | Bấm file trong cây thư mục bên trái |
| Xem thay đổi, commit | Biểu tượng nhánh (Source Control) ở thanh trái |
| Mở Studio / Home cạnh code | `Ctrl+Shift+P` → `Simple Browser: Show` → `http://127.0.0.1:8780/` |
| Chạy lệnh | `` Ctrl+` `` mở terminal |

**Cách Claude trả lời (output style).** Trong VS Code, Claude mặc định trả lời kiểu dành cho lập trình viên. Repo có sẵn style **Anim Team** (`.claude/output-styles/anim-team.md`): trả lời tiếng Việt, kết quả trước, lời dễ hiểu, không dán code hay log, dùng từ của nghề anim. Claude vẫn sửa file và chạy tool như cũ. Muốn bật cho máy mình, thêm dòng sau vào `.claude/settings.local.json` trong repo (tạo file nếu chưa có), rồi mở cuộc trò chuyện mới:

```json
{ "outputStyle": "Anim Team" }
```

Muốn đổi giọng (ngắn hơn, chi tiết hơn…), sửa file style đó. Trong style viết rõ người đọc là ai và muốn trả lời ra sao.

**Việc vẫn làm trong app Claude desktop:** đăng hoặc sửa trang review và Pose Lab trên claude.ai (Artifact), việc cần AI tự bấm trong trình duyệt, chia việc ra nhiều session.

## 6. Ở ngoài công ty / lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| AI báo lỗi kết nối, không trả lời | Bạn đang ở ngoài mạng công ty mà vẫn dùng đường LAN. Chạy `powershell -ExecutionPolicy Bypass -File tools/setup_vscode.ps1 -Endpoint public`, rồi **khởi động lại VS Code** |
| Về lại công ty | Chạy lại với `-Endpoint lan`, rồi khởi động lại VS Code |
| Hỏi đăng nhập khi mở Claude | Key chưa có hoặc sai trong `settings.json` (mục 2) |
| MCP không Connected | Frolvy / Maya / Spine chưa mở, hoặc thiếu `uv`. Mở phần mềm trước rồi bật lại trong `/` → MCP |
| `code` không nhận lệnh | Đóng và mở lại PowerShell sau khi cài |

Cần thêm chi tiết (số đo tốc độ, so sánh với app desktop): `docs/vscode_pilot.md`.
