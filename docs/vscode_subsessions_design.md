# Phiên con cho Claude Code trong VS Code: thiết kế

Trạng thái: **lớp 1 đã làm và thử (2026-11-05)**, lớp 2 chờ quyết định. Kết quả thử và các điều phải xử lý nằm trong `.claude/skills/subsession/SKILL.md`. Người đề xuất: Claude, theo yêu cầu của lead Anim.
Liên quan: `docs/vscode_pilot.md` (thử nghiệm VS Code), `docs/huong_dan_vscode_claude.md` (hướng dẫn team).

## 1. Vấn đề

Trong app Claude desktop, một phiên chính (vd phiên trực HorusChat) giao việc cho **phiên con** ("G-DieLoop: bind skin…", "Thử nghiệm VS Code…", "Báo cáo QLDH-1260…"). Phiên con chạy song song và tự báo kết quả về. Phiên chính nhắn thêm việc được, và các phiên hiện dạng cây.

Extension Claude Code trong VS Code (2.1.318) không có phần này:
- Chỉ có nhiều tab chat độc lập, gom nhóm bằng tay (`Add Session Tab to Group`).
- Phiên không giao việc, không nhắn và không báo kết quả cho nhau.
- Không có cây cha → con.

Hệ quả: phiên điều phối (HorusChat, WorkAI) chỉ chạy được trong app desktop.

## 2. Thứ đã có sẵn trong Claude Code CLI (đã kiểm `claude --help`, bản 2.1.302)

| Lệnh | Tác dụng |
|---|---|
| `claude --bg "<việc>"` | Mở phiên chạy nền, trả về ngay một id ngắn |
| `claude agents --json [--all]` | Liệt kê các phiên (đang chạy, `--all` gồm cả phiên đã xong) dạng JSON |
| `claude logs <id>` | Xem đầu ra gần nhất của phiên nền |
| `claude attach <id>` | Mở phiên nền ra terminal để nói chuyện trực tiếp |
| `claude stop <id>` / `rm <id>` | Dừng (giữ hội thoại) / xoá phiên |
| `claude --resume <id> [--bg] -p "<tin nhắn>"` | Tiếp một phiên đã dừng hoặc đã xong lượt, kèm tin nhắn mới |
| `--session-id <uuid>`, `--fork-session` | Đặt trước id phiên; tách nhánh từ một phiên |

Trong một phiên Claude (VS Code, terminal hay app), lệnh chạy nền (`run_in_background`) **đánh thức phiên khi lệnh kết thúc**. Đây là cơ chế để phiên con báo về phiên chính.

**Kết luận:** chỉ cần một lớp mỏng nối các lệnh này lại, không phải viết bộ chạy phiên mới.

## 3. Lớp 1: plugin "phiên con" (Python + skill, không cần cài thêm)

### 3.1 File

| File | Vai trò |
|---|---|
| `tools/subsession/subsession.py` | Lệnh chính: `start`, `list`, `tree`, `log`, `send`, `stop`, `wait`, `done` |
| `tools/subsession/registry.json` (git bỏ qua) | Sổ phiên: id, tên, phiên cha, bản giao việc, thư mục làm việc, trạng thái, thời điểm, đường dẫn báo cáo |
| `work/_subsessions/<id>/brief.md` | Bản giao việc (phiên con đọc đầu tiên) |
| `work/_subsessions/<id>/report.md` | Báo cáo cuối của phiên con (2–3 câu kết quả + chi tiết) |
| `.claude/skills/phien_con/SKILL.md` | Dạy Claude khi nào giao phiên con, cách viết brief, cách nhận báo cáo |

### 3.2 Luồng

```
Phiên chính                               Phiên con (claude --bg)
-----------                               -----------------------
1. subsession.py start --name zom1-rebind
     --brief "<việc, file, xong là gì>"
   → ghi brief.md, registry
   → claude --bg "<brief + luật báo cáo>"  ──►  đọc brief.md, làm việc
   → trả id
2. subsession.py wait <id>  (chạy nền)          ...
                                                xong: ghi report.md,
                                                subsession.py done <id>
3. wait kết thúc ◄──────────────────────────────┘
   → Claude phiên chính được đánh thức,
     đọc report.md, kiểm kết quả, báo người dùng
4. (tuỳ) subsession.py send <id> "<việc thêm>"
   → claude --resume <id> --bg -p "<việc thêm>", rồi wait lại
```

- **Luật báo cáo** gắn vào cuối mỗi brief: "Khi xong (hoặc bị chặn, cần người dùng trả lời) thì ghi `report.md`, dòng đầu là `XONG:` / `CHẶN:` + một câu, rồi chạy `subsession.py done <id>`."
- `wait` kết thúc khi gặp một trong ba điều: có `done`, phiên nền thoát (theo `claude agents --json`), hoặc hết giờ (mặc định 2 giờ, đặt được). Hết giờ mà không có báo cáo thì `wait` in 30 dòng log cuối để phiên chính tự xem.
- **Phiên con bị chặn** (cần người dùng): ghi `CHẶN:` + câu hỏi. Phiên chính hỏi người dùng rồi `send` câu trả lời.
- **Cây phiên:** `tree` in cha → con → cháu, trạng thái (đang chạy / xong / chặn / dừng) và câu đầu của báo cáo.

### 3.3 Quy tắc an toàn

- Phiên con chạy **cùng thư mục** thì chỉ sửa file trong phạm vi brief, không commit, không đổi nhánh (giống luật phiên con trong app desktop). Việc có nhánh hoặc PR riêng thì dùng worktree (`--worktree` trong `start`, dựa trên `git worktree`).
- Hai phiên con không sửa cùng một file: `start` cảnh báo nếu brief nêu file trùng với phiên đang chạy.
- Phiên con thừa kế chế độ quyền của người dùng. Không dùng `--dangerously-skip-permissions`.
- Tối đa 4 phiên con chạy cùng lúc (đặt được), để không cạn hạn mức và máy không chậm.
- Không ghi key hay token vào brief, report hay registry.

### 3.4 Lệnh cho người dùng (gõ trong chat, Claude tự chạy)

- "Giao việc X cho phiên con" → `start` + `wait`.
- "Các phiên con đang làm gì?" → `tree`.
- "Phiên zom1 tới đâu rồi?" → `log`.
- "Bảo phiên zom1 làm thêm Y" → `send`.
- "Dừng phiên zom1" → `stop`.
- Người dùng muốn nói chuyện trực tiếp: `claude attach <id>` trong terminal VS Code.

### 3.5 Còn phải thử

1. `claude --bg` nhận câu lệnh dài (brief nhiều dòng) và chạy đúng thư mục, đúng MCP, đúng CLAUDE.md.
2. **Nhắn khi phiên con đang chạy dở:** CLI chỉ cho `--resume` khi phiên đã dừng hoặc xong lượt. Nếu không nhắn chen được thì `send` sẽ xếp hàng: lưu tin nhắn, gửi khi phiên xong lượt.
3. `wait` chạy nền có đánh thức phiên chính trong extension VS Code giống như trong CLI không.
4. Phiên con nền có hiện trong danh sách phiên của extension không (để bấm mở).

### 3.6 Ước lượng

| Bước | Thời gian |
|---|---|
| `subsession.py` + registry + luật báo cáo | ~1 giờ |
| Skill `phien_con` + thử 2 phiên con thật (vd đọc báo cáo, sửa doc) | ~1 giờ |
| Ghi `docs/huong_dan_vscode_claude.md`, `MAP.md`, đẩy GitHub | ~15 phút |

## 4. Lớp 2: extension VS Code của team (sau khi lớp 1 chạy ổn)

Cần cài **Node.js LTS** (winget `OpenJS.NodeJS.LTS`, hỏi trước) để đóng gói extension (`.vsix`), rồi cài cho team bằng `code --install-extension horus-anim.vsix` hoặc gộp vào `tools/setup_vscode.ps1`.

| Phần | Nội dung |
|---|---|
| **Cây phiên** (thanh bên) | Đọc `registry.json` + `claude agents --json`: cha → con, trạng thái, câu đầu báo cáo. Bấm: mở report, mở log, `attach` trong terminal, gửi thêm việc, dừng |
| **Thông báo** | Phiên con xong hoặc bị chặn → thông báo góc VS Code |
| **Anim** | Tab Studio / Home (`http://127.0.0.1:8780`), danh sách clip theo `work/clips.json` (giai đoạn, ghi chú), mở playblast hoặc ảnh render của clip |
| **Thay Artifact** | Trang review / Pose Lab chạy local qua Home server (`/api/store` đã có), mở trong tab VS Code. Chỉ làm khi team chốt dùng VS Code lâu dài |

Không sửa được giao diện extension Claude Code chính thức: mọi thứ là bảng riêng nằm cạnh nó.

Ước lượng: cây phiên + thông báo ~1 buổi; phần Anim ~1 buổi; thay Artifact tính riêng.

## 5. Quyết định cần duyệt

1. Làm lớp 1 trước, theo thiết kế mục 3?
2. Tên lệnh: `phien_con` (tiếng Việt) hay `subsession`?
3. Giới hạn: 4 phiên con cùng lúc, `wait` tối đa 2 giờ: có đổi không?
4. Lớp 2: có cài Node.js lên máy lead để làm extension không?
