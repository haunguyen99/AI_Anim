# Câu lệnh mẫu + kết quả mong đợi, gắn theo tiêu đề trang (xem core.std)
CMDS.update({
 'Biết có gì và nhân vật to cỡ nào':('"Mở file Windy.fbx. Đo model: liệt kê từng mảnh, chiều cao, hướng mặt. Gửi mình bảng số, chỗ nào chưa chắc thì ghi rõ."','bảng: 2 mảnh, cao 185 cm, sải tay 175,6 cm, gậy ở tay phải.'),
 'Topology tốt thì skin mới uốn đẹp':('"Kiểm topology Windy: số tris, quanh shoulder, elbow, knee, neck có đủ vòng ô không. Kết luận đạt hay chưa đạt, chỗ nào chưa."','số tris, ảnh phóng to shoulder, và kết luận đạt / chưa đạt.'),
 'Joint đặt ở chỗ khớp thật sự gập':('"Đặt joint cho Windy, chỉ bên phải và giữa, root joint ở hip. Chưa build. Chụp trước, bên, trên gửi mình duyệt."','3 ảnh joint chồng topology và bảng độ cao từng joint.'),
 'Đạt hay chưa đạt? Nhìn 3 góc rồi sửa':('"Hạ Chest xuống 4 cm. Head End về đỉnh đầu. Scapula và shoulder ra ngoài 6 cm. Giữ nguyên chỗ mình đã sửa."','3 ảnh mới, 4 điểm đã chỉnh (như hình bên). Chưa đạt thì nói tiếp.'),
 'Đuôi, áo choàng: mỗi thứ một joint chain':('"Thêm joint chain cho áo choàng Windy, đầu chuỗi ở chỗ áo gắn vào thân. Chụp gửi mình."','ảnh joint chain chạy dọc theo áo choàng.'),
 'Bấm Build Rig: từ skeleton ra rig dùng được':('"Lưu file. Build Rig cho Windy: không helper joint, root joint ở hip. Báo kết quả."','báo đã build, không có bản thừa, kèm ảnh.'),
 'Control phải thấy được và bấm được':('"Vẽ control ôm sát mesh. Gậy có hai control: một theo tay phải, một để bay tự do. Liệt kê cỡ mọi control, so trái với phải."','bảng cỡ control hai bên và ảnh control quanh nhân vật.'),
 'Mỗi điểm trên skin nghe lời joint nào, bao nhiêu phần':('"Đưa mọi control về 0, rồi bind skin cho Windy. Gậy bám 100% vào một joint riêng. Tối đa 4 joint mỗi điểm."','báo đã bind skin, chưa duyệt. Bước sau mới xem kết quả.'),
 'Đạt hay chưa đạt? Xoay từng khớp rồi nhìn':('"Xoay shoulder, elbow, hip, knee, neck, thân ở góc thường dùng. Gửi ảnh từng khớp, camera gần."','ảnh Windy ở nhiều tư thế. Bạn nhìn skin có phình, thắt, dính không.'),
 'Picker giúp chọn control nhanh':('"Làm picker cho Windy: mỗi nút chọn đúng một control, không nút nào đè nhau. Liệt kê control chưa có nút."','ảnh picker và danh sách control chưa có nút.'),
 'Thử rig như người làm hoạt hình sẽ dùng':('"Thử đủ 2 tay và 2 chân, cả IK và FK. Đổi sang frame khác rồi quay về, báo bind pose có đổi không. Liệt kê cái chưa kiểm."','bảng ✓ / ✗ cho 2 tay và 2 chân và danh sách cái chưa kiểm.'),
 'Hai loại file, chỉ xuất khi bạn nói "chốt"':('"Chốt rig Windy. Xuất file Base, kiểm trong Unity, báo lỗi nếu có."','1 file Base và báo kết quả kiểm trong game.'),
})
