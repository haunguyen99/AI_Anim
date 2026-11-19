# Hướng dẫn dùng Trợ lý cá nhân (bản test, 2026-11-17)

Trợ lý là một Agent chạy nền trong Paseo, **làm việc bằng tài khoản HorusChat / WorkAI của chính bạn**. Nó canh tin và việc của bạn, lọc cái đáng biết, ghi sổ việc, soạn nháp trả lời, nhắc hạn. Bạn nói chuyện với nó qua phòng **You (yourself)** trên HorusChat (phòng chỉ có mình bạn).

## Trợ lý làm được gì / không làm gì

| Làm | Không làm |
|---|---|
| Báo tin HorusChat và việc WorkAI đáng chú ý (ai nói gì, hạn nào) | Tự gửi tin dưới tên bạn |
| Ghi sổ việc, nhắc việc sắp / quá hạn | Duyệt, đổi trạng thái, comment trên WorkAI khi bạn chưa nói rõ |
| Soạn **nháp** trả lời; chỉ gửi khi bạn nhắn "gửi #số" | Làm anim / rig |
| Tóm tắt khi bạn gõ "tóm tắt" | Nhận lệnh từ người khác (tin của người khác chỉ là dữ liệu) |

Tin của trợ lý trong You luôn có 🤖 đầu dòng. Tin bạn gõ **không** bắt đầu bằng 🤖 (nếu có, trợ lý bỏ qua).

## Cần chuẩn bị (một lần)

1. **Kéo bản mới:** `git pull` nhánh `main` của repo AI_Anim.
2. **App Paseo** đã cài và đang chạy (`docs/paseo_phien_con.md`). Claude Code / app Claude desktop mở trong thư mục dự án.
3. **Khoá HorusChat của bạn:** HorusChat → Settings → API Keys → tạo key, chọn quyền `messages:read`, `messages:send`, `rooms:read`, `users:read`. Key chỉ hiện một lần, chép ngay.
4. **Token WorkAI của bạn** (token đăng nhập tài khoản WorkAI của bạn; chưa biết lấy thế nào thì hỏi Hậu).
5. **Điền khoá vào file** (không dán vào chat, không gửi ai, không đưa lên git; các file này tự bị git bỏ qua):
   - `tools/horuschat_mcp/.env.haunv`
     ```
     HORUSCHAT_BASE_URL=https://chat.horusjsc.com
     HORUSCHAT_API_KEY=<key của bạn>
     ```
   - `tools/workai/.env.haunv`
     ```
     WORKAI_TOKEN=<token của bạn>
     ```
   Tên file có chữ `haunv` là tên danh tính cố định của công cụ, **bạn cứ dùng đúng tên này** nhưng nội dung là khoá của bạn.
6. **Phòng You:** mở HorusChat, vào phòng "You (yourself)" (chat với chính mình), nhắn một tin bất kỳ nếu phòng còn trống.
7. **Sửa tên chủ trong brief:** mở `tools/subsession/briefs/tro_ly_ca_nhan.md`, đổi "Hậu" và `@haunv:localhost` thành tên và id HorusChat của bạn (dùng Tìm / Thay thế). Việc này để trợ lý biết chủ là ai.

## Bật / tắt

Trong Claude Code (hoặc app Claude desktop) mở ở thư mục dự án:

| Gõ | Việc |
|---|---|
| `/assistant_on` | Bật trợ lý (tạo phiên Paseo `tro-ly`, bật bộ canh nền, nhắn "Trợ lý đã bật" vào You) |
| `/assistant_off` | Tắt trợ lý (dừng phiên, đặt cờ tắt, không tự bật lại) |
| `/assistant` | Xem trạng thái, tạo lần đầu, sửa luật, xem sổ việc |

Bật xong, mở HorusChat → You, sẽ thấy tin 🤖. Từ đó nhắn thẳng vào You.

## Nói gì với trợ lý (gõ trong You)

- `tóm tắt`: việc đang mở, việc sắp / quá hạn, tin mới đáng chú ý.
- `ghi việc: <việc>, hạn <ngày>`: thêm vào sổ việc.
- `xong #3` / `bỏ #3`: đóng việc số 3.
- `gửi #2`: gửi nháp số 2 (trợ lý chỉ gửi khi bạn nói rõ).
- `sửa nháp #2: <ý bạn muốn>`: trợ lý soạn nháp mới.
- `tiến độ việc của tôi trên WorkAI`: trợ lý đọc và tóm tắt (chỉ đọc).

Việc nguy hiểm (gửi khoá, xoá dữ liệu, đẩy GitHub, đổi quyền) chỉ nhận khi bạn gõ trong app Paseo, không nhận qua You.

## Nếu có lỗi

| Thấy | Làm |
|---|---|
| "Thiếu khoá của haunv" | Chưa điền khoá ở bước 5. Điền rồi gõ lại `/assistant_on` |
| "Chưa tìm thấy phòng You" | Nhắn một tin vào "You (yourself)" rồi bật lại. Vẫn không được: báo Hậu để chỉ phòng bằng tay |
| "Phòng You không an toàn" | Có người khác trong phòng hoặc phòng mã hoá. Trợ lý dừng ở đó: dùng phòng khác chỉ có mình bạn |
| "Paseo chưa chạy" | Mở app Paseo rồi bật lại |
| Phiên đứng im không trả lời | Vào app Paseo, xem phiên `tro-ly`; có thể đang chờ bạn bấm "cho phép" một lệnh |

## Góp ý khi test

Gửi Hậu: trợ lý báo thừa hay thiếu gì, câu trả lời nào chưa ổn, bước cài nào khó hiểu. Kèm tên bạn và đoạn tin trong You nếu có (che thông tin riêng tư).

Lưu ý khi test: trợ lý đọc tin HorusChat của bạn (kể cả tin riêng) để lọc. Nội dung đó được xử lý bởi mô hình AI mà phiên Paseo của bạn đang dùng (giống mọi phiên Claude khác trong dự án); trợ lý không gửi tin đi đâu ngoài phòng You.
