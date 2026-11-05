# Thử nghiệm VS Code + extension Claude Code cho team Animation

Ngày: 2026-11-05. Góp ý gốc: anh Nguyễn Đức Tùng (dev). Người làm thử: máy lead Anim (`E:\AI Animation`).

## 1. Kết quả ngắn

- **Chạy được.** VS Code + extension Claude Code dùng **cùng bộ máy** với ứng dụng Claude desktop: cùng `CLAUDE.md`, skills, agents (director), memory, `.mcp.json` và cùng endpoint `llmpro`. Không phải chuyển đổi dữ liệu hay viết lại skill.
- **Không làm AI nhanh hơn.** Tốc độ phụ thuộc endpoint, không phụ thuộc VS Code hay app desktop.
- **Đặt IP nội bộ được** bằng biến `ANTHROPIC_BASE_URL` (áp dụng chung cho CLI, extension và app desktop). Chỉ cần dev mở cổng LAN cho `llmpro`. Xem mục 4.
- **Đề xuất:** dùng **song song**, chưa chuyển hẳn. VS Code dùng cho việc file / git / xem ảnh / Studio. App desktop giữ cho việc cần Artifact (trang review, Pose Lab có db), trình duyệt trong app và chia session (HorusChat dispatcher, WorkAI).

## 2. Cài đặt (đã làm trên máy lead)

| Bước | Lệnh | Kết quả |
|---|---|---|
| VS Code (gói chính thức Microsoft, cài cho user, không cần admin) | `winget install --id Microsoft.VisualStudioCode -e --scope user` | 1.143.1, có lệnh `code` |
| Extension Claude Code (publisher Anthropic) | `code --install-extension anthropic.claude-code` | 2.1.318 |
| Claude Code CLI (đã có từ trước) | `winget install Anthropic.ClaudeCode` | 2.1.302 |

Mở repo: `code "E:\AI Animation"` → bấm biểu tượng Claude (thanh bên trái hoặc góc trên phải) → đăng nhập theo cách đang dùng (key `llmpro` đã có trong `~/.claude/settings.json` thì không phải nhập lại).

**Lần đầu mở repo:** Claude hỏi duyệt 6 MCP server của dự án (spine, maya, frolvy, rocketchat, horuschat, comfyui). Duyệt một lần là xong (`claude mcp list` đang báo "Pending approval" vì chưa duyệt ở CLI).

## 3. Chạy thử

| Việc | Kết quả |
|---|---|
| `claude -p` trong repo đọc `MAP.md`, trả lời về `tools/studio` | Đúng, 44,6 s với Opus (gồm nạp CLAUDE.md, memory, skills) |
| Lệnh ngắn nhất ("ok") bằng Haiku | 8,5 s cả khởi động |
| Gọi API thuần qua `llmpro` (5 token) | 1,0–1,3 s mỗi lần, lần đầu 2,5 s |
| Git (log, status, 95 file đang đổi) | Đọc bình thường; VS Code có thẳng tab Source Control để xem diff, commit |
| File ảnh, video mp4 | VS Code mở sẵn (Media Preview có trong máy, không cần extension) |
| FBX / glb 3D | VS Code không có sẵn; cần extension xem glTF (chưa cài, hỏi trước khi cài). FBX vẫn xem trong Studio / Maya |
| Studio qua cầu nối `tools/studio_cmd.py` | Không phụ thuộc giao diện Claude, chạy được từ terminal VS Code. Lúc thử Home server (cổng 8780) đang tắt nên chưa chạy được lệnh `state` |
| Trang Studio / Home trong VS Code | Lệnh `Simple Browser: Show` → `http://127.0.0.1:8780/` mở được trang local bên cạnh code, nhưng Claude **không điều khiển** được trình duyệt này (khác trình duyệt trong app desktop). Claude điều khiển trang thì dùng cầu nối hoặc Claude in Chrome |

Lead đã thử tay (2026-11-05): mở khung Claude Code (model `claude-opus[1m]`, chế độ Auto), `/` → MCP: cả 6 server dự án **Connected** (comfyui, frolvy, horuschat, maya, rocketchat, spine). Còn thử tiếp: gõ một yêu cầu anim ngắn, `@file` một ảnh playblast, xem diff Claude sửa.

## 4. Model và endpoint (ý anh Tùng về tốc độ)

Cấu hình hiện tại (chỉ đọc, không ghi key):

- `~/.claude/settings.json` → `env.ANTHROPIC_BASE_URL = https://llmpro.horusjsc.com`, model `claude-opus[1m]`, key ở `ANTHROPIC_AUTH_TOKEN` (file riêng của máy, không đưa vào git).
- `llmpro.horusjsc.com` phân giải ra IP Cloudflare (172.67.133.42, 104.21.13.214), header `Server: cloudflare`, `CF-RAY …-HKG`: mỗi lần gọi đi ra Cloudflare Hồng Kông rồi mới về server công ty.
- Đo: TCP ~60 ms, TLS ~120–160 ms, phản hồi trang gốc 0,3–0,5 s; lần đầu chờ DNS ~1 s.

Đặt IP nội bộ:

1. Extension **có** chỗ đặt: `ANTHROPIC_BASE_URL` trong `~/.claude/settings.json` (chung cho cả máy), hoặc `claudeCode.environmentVariables` trong cài đặt VS Code (riêng workspace). Không có ô "IP" riêng, nhưng URL nhận IP: `http://<IP-LAN>:<cổng>`.
2. Phía dev cần: cho `llmpro` nghe trên IP LAN (vd `192.168.x.x:port`) và báo IP + cổng. Nếu dùng `https` với IP thì chứng chỉ không khớp tên → dùng `http` trong LAN, hoặc tên nội bộ có chứng chỉ đúng (DNS nội bộ trỏ `llmpro.horusjsc.com` về IP LAN thì giữ nguyên URL, nhưng chứng chỉ máy chủ gốc phải hợp lệ; nếu là chứng chỉ riêng thì thêm `NODE_EXTRA_CA_CERTS`).
3. Mức lợi dự kiến: bớt chặng qua Cloudflare, khoảng 0,1–0,5 s mỗi lần gọi. Một lượt làm việc có 20–40 lần gọi công cụ thì đỡ vài giây đến hơn chục giây. Phần lớn thời gian vẫn là model sinh chữ và chặng từ `llmpro` ra Anthropic, nên **cần đo lại khi có IP**, không hứa nhanh gấp nhiều lần.
4. Việc này làm được ngay trong app desktop, không cần chuyển sang VS Code.

**Đo IP LAN (2026-11-05, anh Tùng cấp `http://192.168.10.29:40741`):** dùng được với key hiện tại, không qua Cloudflare.

| Gọi API thuần | IP LAN | `llmpro` qua Cloudflare |
|---|---|---|
| Haiku, 5 token (5 lần) | 0,86–1,10 s (TB ~0,95) | 1,01–1,34 s (TB ~1,15) |
| Opus, ~200 token (3 lần) | 2,40–2,46 s | 2,73–2,95 s |

Nhanh hơn khoảng 0,2–0,4 s mỗi lần gọi (~15–20 %). Một lượt có 30 lần gọi công cụ thì đỡ khoảng 6–12 s. Số đo lượt Claude Code đầy đủ (16–46 s) dao động quá nhiều do model, nên không dùng để so. Chỉ dùng được trong mạng công ty: ở nhà / ngoài LAN thì phải về lại `https://llmpro.horusjsc.com`. Đi `http` nên key truyền không mã hoá trong LAN.

**Đã đổi trên máy lead (2026-11-05):** `~/.claude/settings.json` → `ANTHROPIC_BASE_URL = http://192.168.10.29:40741`, bản cũ lưu ở `~/.claude/settings.json.bak_llmpro_20261105`. Đã kiểm: lệnh `claude` mới nối thẳng `192.168.10.29:40741`. Session / cửa sổ đang mở giữ URL cũ đến khi khởi động lại app. Muốn quay lại: đổi giá trị về `https://llmpro.horusjsc.com` (hoặc chép lại bản `.bak`).

## 5. Ưu và nhược so với cách đang dùng

| | VS Code + extension | App Claude desktop (đang dùng) |
|---|---|---|
| Xem ảnh, video, code, file JSON ngay cạnh chat | Tốt hơn: cây thư mục, nhiều tab, xem diff từng dòng | Có ô file, kém tiện hơn |
| Git (diff, commit, lịch sử, nhiều người chung repo) | Tốt hơn: Source Control có sẵn, thêm GitLens nếu cần | Claude tự chạy git, người dùng ít nhìn thấy |
| Cài thêm extension (glTF viewer, Live Server, Markdown…) | Có | Không |
| Chạy trang qua HTTP | Simple Browser / Live Server, nhưng Claude không điều khiển được | Trình duyệt trong app, Claude đọc và bấm được |
| Artifact (trang review, Pose Lab, slide trên claude.ai, db ghi chú) | **Không có**: phải dùng trang local qua Home server | Có |
| Chia session, session con báo lại, dispatcher HorusChat / WorkAI | **Không có** (chỉ nhiều tab chat độc lập) | Có |
| Ô tóm tắt cuối lượt, danh sách việc | Có danh sách việc, không có ô tóm tắt | Có |
| CLAUDE.md, skills, memory, MCP, cầu nối Studio | Như nhau | Như nhau |
| Tốc độ AI | Như nhau (cùng endpoint) | Như nhau |
| Người mới làm quen | Giao diện lập trình, hơi lạ với artist | Đơn giản hơn |

## 6. Đề xuất

- **Không chuyển hẳn lúc này.** Phần cốt lõi của quy trình review (Artifact + db ghi chú, trình duyệt trong app, session con) chỉ có ở app desktop.
- **Dùng song song 1–2 tuần** với 1–2 người: VS Code cho việc sửa tool / script, xem playblast và ảnh, xem git; app desktop cho làm anim có trang review và việc chat / WorkAI.
- **Việc tốc độ tách riêng:** đã có IP LAN (mục 4), nhanh hơn ~15–20 % mỗi lần gọi. Máy ngồi trong mạng công ty đặt `ANTHROPIC_BASE_URL=http://192.168.10.29:40741` trong `~/.claude/settings.json`, áp dụng cho cả app desktop lẫn VS Code.
- Nếu team chốt dùng VS Code lâu dài: chuyển các trang review sang Home server local (đã có `/api/store`), để không phụ thuộc Artifact.

## 7. Hướng dẫn nhanh cho người mới

1. **Lấy repo:** `git clone` repo team, hoặc mở thư mục `E:\AI Animation` nếu dùng chung máy.
2. **Key:** nhờ lead cấp key `llmpro`. Tạo `C:\Users\<tên>\.claude\settings.json` (chỉ trên máy mình, **không commit**, không gửi lên chat chung):
   ```json
   {
     "env": {
       "ANTHROPIC_AUTH_TOKEN": "<key lead cấp>",
       "ANTHROPIC_BASE_URL": "http://192.168.10.29:40741",
       "ANTHROPIC_MODEL": "claude-opus[1m]"
     }
   }
   ```
3. **Cài bằng script** (PowerShell, trong thư mục repo):
   - Kiểm tra, không cài gì: `powershell -ExecutionPolicy Bypass -File tools/setup_vscode.ps1`
   - Cài VS Code (winget, cho user, không cần admin) + extension `anthropic.claude-code`: thêm `-Install`.
   - Đổi endpoint: `-Endpoint lan` (trong mạng công ty, nhanh hơn ~15–20 %) hoặc `-Endpoint public` (`https://llmpro.horusjsc.com`, khi ở ngoài). Script sao lưu `settings.json` trước khi sửa, kiểm nối được IP LAN rồi mới đổi, và không bao giờ ghi key.
   - Cài tay nếu cần: `winget install --id Microsoft.VisualStudioCode -e --scope user`, rồi `code --install-extension anthropic.claude-code`.
4. **Bộ nhớ dự án (máy mới):** `.venv/Scripts/python.exe -I tools/claude_memory.py restore`.
5. **Mở:** `code "E:\AI Animation"`. VS Code gợi ý cài extension Claude Code (theo `.vscode/extensions.json`). Bấm biểu tượng Claude (✱) ở thanh bên hoặc góc trên phải.
6. **Lần đầu:** gõ `/` → MCP → bật các server dự án. Phải thấy `Connected` cho frolvy, maya, spine, horuschat, comfyui; rocketchat là chat cũ, tắt cũng được.
7. **Làm việc:** gõ yêu cầu bằng tiếng Việt như trong app desktop. `@` hoặc `+` để gắn file hay ảnh (thả ảnh thì giữ `Shift`); `/` cho skill (`/director`, `/new_clip`, `/check_fb`…). Nút model (`claude-opus[1m] Medium`) đổi mức suy nghĩ. Nút `Auto` / `Manual` / `Plan` đổi chế độ quyền. Claude đọc `CLAUDE.md` và `MAP.md` tự động.
8. **Xem kết quả:** ảnh, video mở bằng cách bấm file trong cây thư mục. Thay đổi xem ở Source Control (biểu tượng nhánh). Trang Studio / Home: `Ctrl+Shift+P` → `Simple Browser: Show` → `http://127.0.0.1:8780/`.
9. Việc cần trang review, Pose Lab trên claude.ai, hay chia việc cho nhiều session: làm trong app Claude desktop.

Lỗi thường gặp: AI báo lỗi kết nối → đang ở ngoài mạng công ty mà endpoint là IP LAN, chạy `-Endpoint public`. Đổi endpoint xong phải khởi động lại VS Code / app Claude.
