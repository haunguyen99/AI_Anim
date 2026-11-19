---
name: feedback-studio-quick-edits
description: "Simple Studio edits (delete/rename a mesh) must be fast — check object names first, no screenshot-per-click"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 98415810-dce9-4d70-8e09-d4120141ccff
  modified: 2026-10-27T11:09:30.948Z
---

User 2026-10-27 thấy chậm: "chỉ xóa mesh mà cũng lâu vậy" (mình chụp màn hình sau mỗi lần click, bấm nút thùng rác trên dòng Outliner không ăn, xóa nhầm cung `bow` thay vì nỏ `crossbow` rồi phải hoàn tác).

**Why:** những việc nhỏ trong Studio ([[project-studio]]) phải xong trong vài giây, như khi tự làm trong Maya.
User cũng xem trực tiếp trên trang (2026-10-27: "tôi hoàn toàn thấy thay đổi trên trang live nên không cần chụp hình lại báo cáo").
**How to apply:** không chụp màn hình để báo cáo; nếu cần kiểm thì kiểm bằng JS/read_page (tên object, trạng thái), báo ngắn bằng chữ; đọc tên đầy đủ của mọi object một lần (JS/read_page) và khớp đúng từ người dùng nói (nỏ = crossbow, cung = bow); gom chọn → xóa → lưu vào một batch rồi chụp màn hình đúng một lần ở cuối; nếu có thì gọi lệnh Studio trực tiếp thay vì click theo tọa độ.
