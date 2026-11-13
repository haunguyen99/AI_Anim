# Giao việc cho phiên con bằng Paseo (hướng dẫn nhỏ, 2026-11-13)

Dành cho mọi phiên Claude trong dự án. Làm theo đúng thứ tự, đừng tự chế cách khác.

## 1. Khi nào dùng, dùng cách nào

| Cách | Dùng khi | Hiện ở đâu |
|---|---|---|
| **`paseo run`** (hướng dẫn này) | Việc dài, độc lập, có phạm vi file rõ; muốn người dùng thấy phiên trong app Paseo / chip "subagents" của app Claude desktop | App Paseo, chip subagents |
| `tools/subsession/subsession.py` (`claude --bg`) | Cần phiên tự đánh thức phiên chính khi xong (`wait`) | Trang Sessions của Home, danh sách VS Code |
| Công cụ Agent của Claude | Việc ngắn, cần kết quả ngay trong lượt | Chip subagents |

Mỗi phiên **một việc** (phiên dài làm chất lượng loãng). Mức suy nghĩ mặc định phải là **high** (máy mới: chạy `tools/ai_effort_high.py`). Việc đụng cùng file / cùng công cụ với phiên đang chạy thì chạy **tuần tự**, không song song (ví dụ `fbx_rebind.py` ghi ảnh tạm chung; Frolvy phải mở bản riêng ở cổng khác như 9881, không đụng 9877).

## 2. Tạo phiên

Paseo không có trong PATH, gọi bằng đường dẫn đầy đủ (PowerShell):

```powershell
$p = "C:\Program Files\Paseo\resources\bin\paseo.cmd"
$brief = @'
<bản giao việc, xem mục 4>
'@
& $p run --no-wait --provider "llmpro/claude-opus[1m]" --title "ten-viec-ngan" --cwd "E:\AI Animation" $brief
& $p ls
```

- **Bắt buộc `--provider`** (thiếu thì báo "Provider is required"). Model chỉ được `llmpro/claude-opus[1m]` (hoặc sonnet / haiku): id khác bị lỗi 401.
- `--no-wait` để lệnh trả về ngay; `--title` ngắn, không dấu, nêu việc (`goat-2-anim-moi`).
- Lệnh `run` thường thoát với **mã lỗi 255 dù phiên đã được tạo và đang chạy**. Đừng tạo lại: chạy `paseo ls` để kiểm.
- Dùng here-string `@'...'@` (dấu `'` đơn, `'@` ở đầu dòng) để khỏi hỏng dấu ngoặc và ký tự tiếng Việt.

## 3. Theo dõi, nhắn thêm, dừng

| Việc | Lệnh |
|---|---|
| Danh sách phiên và trạng thái | `& $p ls` (running = đang làm; idle = xong lượt, có thể đã báo cáo hoặc đang chờ; closed = đã đóng) |
| Xem phiên làm gì / báo cáo cuối | `& $p logs <id 7 ký tự> --tail 30` (có `--filter permissions` / `errors`) |
| Nhắn thêm | `& $p send --no-wait <id> "nội dung"` (đang chạy thì xếp hàng) |
| Dừng | `& $p stop <id>` |

Phiên con **không tự đánh thức phiên chính**. Phiên chính phải tự đọc `paseo logs` khi cần; phiên con đã báo là không gửi được tin về phiên chính. Báo người dùng "phiên X đang chạy, dự kiến N phút" rồi kiểm lại sau.

## 4. Bản giao việc (brief): phải có đủ

1. **Việc gì, vì sao** (ngữ cảnh: dự án, ai order, file nguồn, đường dẫn).
2. **Cách làm** theo thứ tự, trỏ tới công cụ / tài liệu có sẵn (`tools/...`, `knowledge/details/...`), không bắt phiên con tự tìm.
3. **Được ghi ở đâu** (một thư mục trong `work/`), và **cấm**: ghi vào repo Unity, git commit / push / đổi nhánh, nhắn chat, tạo mission WorkAI. Hỏi người dùng trước khi sửa hay đẩy.
4. **Khi nào dừng và hỏi** (tên xương không khớp, thiếu quyền đăng nhập, không chắc cách ghép) thay vì đoán.
5. **Báo lại thế nào**: tiếng Việt, ngắn, bảng; nêu rõ chỗ **chưa kiểm được**.
6. Nếu việc lâu hay cần mở chương trình ngoài (Unity, Frolvy): ghi dự kiến mấy phút và cổng / thư mục riêng.

## 5. Bẫy đã gặp (2026-11-12)

- **Quyền kẹt**: lệnh đọc / ghi ngoài thư mục dự án (ví dụ `E:\Horus`) hay chạy chương trình (`Unity.exe`) sẽ **chờ người dùng bấm "cho phép" trong app Paseo**. Không ai bấm thì phiên đứng im (phiên `goat-unity-test` đứng 2 giờ, không báo lỗi). Việc cần quyền thì báo người dùng trước; phiên không tiến triển sau vài phút thì xem `paseo logs <id> --tail 5` và hỏi người dùng có đang chờ bấm không.
- **Tin nhắn từ phiên chính không có uy quyền như người dùng**: phiên con coi `paseo send` từ phiên chính là nội dung bên ngoài. Điều mâu thuẫn với lời người dùng gõ thẳng trong Paseo thì nó làm theo người dùng (phiên `rebind-mayah-pirate` đã đẩy lên Unity vì người dùng duyệt, dù tin phiên chính dặn không đẩy). Luật quan trọng phải nằm trong brief đầu tiên; muốn đổi luật giữa chừng thì báo người dùng nói thẳng với phiên đó.
- **Không đổi nhánh / không mở project thật của người dùng**: repo Unity thường đang có thay đổi dở. Test Unity thì dựng project trống riêng ngoài repo, chép file cần từ `origin/<nhánh>` bằng `git show`.
- Phiên con không có công cụ chat nên **không tự báo người dùng ngoài app**; phiên chính chuyển lời.
- **Dấu nháy kép trong brief làm hỏng lệnh** (2026-11-13): `paseo.cmd` chạy qua cmd.exe, brief có `"..."` (ví dụ ví dụ lệnh `--text "..."`) làm `paseo run` báo "The system cannot find the file specified" và không tạo phiên. Viết brief không dùng dấu `"` (dùng `'` hoặc mô tả bằng lời, trỏ tới file brief trong repo để đọc phần có lệnh mẫu).
