# Lỗi FBX hay gặp khi vào Unity
| Thấy gì trong Unity | Nguyên nhân thường gặp | Cách sửa |
|---|---|---|
| Mesh co quắp, chân gập, tay chìa ra (nhưng xương đúng) | File thiếu BindPose, Unity gắn skin theo vị trí xương sai | Thêm BindPose và ma trận bind cho mọi xương có skin (cần xử lý riêng nếu xương có xoay sẵn) |
| Mất mesh vũ khí / prop | Prop nằm ngoài cây xương hoặc mất liên kết cha, nên bước lọc bỏ nó | Gắn lại prop làm con của xương cầm, xuất lại, đếm mesh trong Unity |
| Prop đứng sai chỗ (lọt vào thân) | Đỉnh prop lưu theo khung của xương cầm nhưng prop không gắn xương đó | Gắn lại prop dưới xương đúng; đo vị trí thế giới so với bản gốc |
| Lỗi "Cannot find root motion transform" khi Copy Avatar | File anim chỉ có một nút gốc, Base lại có mesh cùng cấp | Thêm một nút rỗng cùng cấp vào file anim |
| Nhân vật to hoặc nhỏ 100 lần | Sai đơn vị (cm và m) | Đặt UnitScaleFactor khi xuất |
| Base còn clip tĩnh | Xuất kèm khoảng thời gian | Bỏ toàn bộ animation khỏi Base |
Nguyên tắc: không đoán; đo, đếm và import thử rồi mới kết luận.
