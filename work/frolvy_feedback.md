# Góp ý cho Frolvy

Lỗi / thiếu sót của Frolvy gặp khi làm việc. Gửi khi người dùng đồng ý: **Help → Send Feedback…** trong Frolvy, hoặc email hello@frolvy.com (Gmail huong99yl@gmail.com, trả lời trong luồng cũ). Bản đã gửi: `work/frolvy_feedback_send_<ngày>.txt`.

**Cách viết (người dùng 2026-11-04: "ghi feedback đơn giản hơn"):** mỗi lỗi 3 dòng ngắn — *Lỗi* (một câu), *Cách thấy* (2–3 bước), *Mong muốn* (một câu). Không kể cách mình vượt qua, không giải thích dài. Thư gửi đi cũng vậy: mỗi mục 3 dòng tiếng Anh.

| # | Lỗi | Cách thấy | Mong muốn | Gửi |
|---|---|---|---|---|
| 1 | API không đặt được khoảng frame | `frame_range()` chỉ đọc, không có lệnh đặt | Thêm `set_frame_range(start, end)` | 02/11 |
| 2 | Đổi frame làm mất giá trị chưa key | Đặt `ry` = 20 ở F0 → sang F1 → về 0 | Giữ giá trị như Maya, hoặc cảnh báo | 02/11 |
| 2b | `set_frame` bị kẹp trong khoảng phát | Khoảng 0–30, `set_frame(45)`, Set Key → key nằm ở F30 | Báo lỗi, hoặc cho key ngoài khoảng | 02/11 |
| 3 | `delete_node` không xoá được camera | `create_camera()` → `delete_node` trả False | Xoá được camera | 02/11 |
| 4 | Set Key bỏ qua thuộc tính enum (`handPose`) | Đặt `handPose` = 2, Set Key → không có key | Key cả enum | 02/11 |
| 5 | `constrain()` ràng buộc node chọn **đầu**, mô tả nói node chọn **cuối** | Chọn DEF_Wrist rồi switch, constrain → cổ tay bị khoá theo switch | Sửa cho khớp mô tả, trả về tên constraint | 04/11 |
| 6 | Build Rig vẽ control cỡ cố định | Nhân vật có váy / mũ trùm: vòng lọt trong mesh hoặc quá to | Tự chỉnh cỡ control theo mesh | 04/11 |
| 7 | Không có cờ "không nhân đối xứng" cho joint | Khăn chỉ bên phải → Build Rig vẫn tạo bản trái | Thêm cờ "no mirror" | 04/11 |
| 8 | Không có lệnh hỏi cha của node | `parent(n)` một đối số lại gỡ cha | Thêm `parent_of(n)` | 04/11 |
| 9 | Node ngón cái thừa sau Build Rig | `check_rig` báo `fng_cy_DEF_ThumbFinger*` không nối đi đâu | Không tạo node thừa | 04/11 |
| 10 | Tên thuộc tính dài trả None | `get_attr("X.translateX")` → None, `"X.tx"` mới đọc được | Nhận tên dài hoặc báo lỗi | 04/11 |
| 11 | Lưới sàn chạy theo `CTL_Main` | Dời `CTL_Main` 1,5 m → lưới phóng to, đổi khung theo rig | Lưới cố định ở gốc toạ độ | 04/11 |
| 12 | autoSnap làm mất pose IK | Bật autoSnap rồi đổi `fkIk` → control IK nhảy theo FK | Ghi chú trong tài liệu | 04/11 |
| 14 | Xoay chưa key của chuỗi cột sống FK bị về 0 | Kênh chưa có key: đặt rx/ry/rz cho Root, Spine1, Chest, Neck, rồi đặt node khác (Head, tay IK) trong cùng một script → chọn tất cả, Set Key → xoay cột sống thành 0 (dời vị trí vẫn giữ). Key đầu tiên sau khi xoá hết key cũng bị | Giữ giá trị đã đặt tới khi Set Key | 05/11 |
| 13 | Vòng Rotate ở front view (Local) trông lệch hướng | `Hero_Blade_Idle.fv`, chọn `CTL_Chest_M` (ngực xoay ngang ~25°), công cụ Rotate, Local, nhìn front | Kiểm hướng vòng xoay; ghi rõ Local vẽ theo trục control (đo world_matrix khớp ~25°) | 04/11 |
| 15 | Texture hiện lộn ngược (lật trục V) | Gán `T_Char_Main_T2.tga` / `T_Colorpalette.tga` cho Hero RPG2 → thân loang lổ, kiếm tím; lật ảnh dọc thì đúng | Đọc V như Maya/Unity | 05/11 |
| 17 | Trong layer cộng, `set_attr` / `set_key` cộng dồn phần Base | `api.layers()` có layer cộng; `set_active_layer(1)`, đặt `set_attr(rx, x)` rồi `set_key()` hai lần → giá trị đọc lại tăng thêm đúng phần Base mỗi lần (−0,31 → −1,36 → −2,40) | `get_attr` và `set_attr` cùng nghĩa (cả hai giá trị gộp hoặc cả hai của layer) | chưa |
| 16 | Thiếu lệnh Paste Connect như Maya | Muốn nối cùng material/texture hoặc liên kết thuộc tính cho nhiều node phải làm từng cái | Thêm Paste Connect | 05/11 |
