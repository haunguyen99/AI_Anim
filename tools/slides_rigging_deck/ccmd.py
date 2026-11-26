# Câu lệnh mẫu + kết quả mong đợi, gắn theo tiêu đề trang (xem core.std)
CMDS.update({
 'Biết có gì và nhân vật to cỡ nào':('"Mở file MC_Ninja.fbx. Đo model: liệt kê từng mảnh, chiều cao, hướng mặt. Gửi mình bảng số, chỗ nào chưa chắc thì ghi rõ."','bảng: mesh body + kunai, cao 185 cm, sải tay 175,6 cm.'),
 'Topology tốt thì skin mới uốn đẹp':('"Kiểm topology Ninja: số tris, quanh shoulder, elbow, knee, neck có đủ vòng ô không. Kết luận đạt hay chưa đạt, chỗ nào chưa."','số tris, ảnh phóng to shoulder, và kết luận đạt / chưa đạt.'),
 'Joint đặt ở chỗ khớp thật sự gập':('"Đặt joint cho Ninja, chỉ bên phải và giữa, root joint ở hip. Chưa build. Chụp trước, bên, trên gửi mình duyệt."','3 ảnh joint chồng topology và bảng độ cao từng joint.'),
 'Đạt hay chưa đạt? Nhìn 3 góc rồi sửa':('"Hạ Root, Hip, Knee 3 cm. Hạ Neck, Head 7 cm. Hạ Spine 5 cm, Chest 8 cm. Scapula hạ 3 cm và ra ngoài 6 cm, shoulder ra ngoài 6 cm. Giữ nguyên chỗ mình đã sửa."','3 ảnh mới, các điểm đã chỉnh (như hình bên). Chưa đạt thì nói tiếp.'),
 'Đạt hay chưa đạt? Và lỗi AI hay mắc':('"Hạ Root, Hip, Knee 3 cm. Hạ Neck, Head 7 cm. Hạ Spine 5 cm, Chest 8 cm. Scapula hạ 3 cm và ra ngoài 6 cm, shoulder ra ngoài 6 cm. Giữ nguyên chỗ mình đã sửa."','3 ảnh mới, các điểm đã chỉnh (như hình bên). Chưa đạt thì nói tiếp.'),
 'Đuôi, khăn, áo choàng: mỗi thứ một joint chain':('"Thêm joint chain cho khăn Ninja, mỗi bên 5 joint, đầu chuỗi ở Chest. Chụp gửi mình."','ảnh joint chain chạy dọc theo khăn.'),
 'Bấm Build Rig: từ skeleton ra rig dùng được':('"Lưu file. Build Rig cho Ninja: không helper joint, root joint ở hip. Báo kết quả."','báo đã build, không có bản thừa, kèm ảnh.'),
 'Control phải thấy được và bấm được':('"Vẽ control ôm sát mesh. Kunai gắn vào joint Weapon dưới Wrist. Liệt kê cỡ mọi control, so trái với phải."','bảng cỡ control hai bên và ảnh control quanh nhân vật.'),
 'Mỗi điểm trên skin nghe lời joint nào, bao nhiêu phần':('"Đưa mọi control về 0, rồi bind skin cho Ninja. Kunai bám 100% joint Weapon. Tối đa 4 joint mỗi điểm."','báo đã bind skin, chưa duyệt. Bước sau mới xem kết quả.'),
 'Đạt hay chưa đạt? Xoay từng khớp rồi nhìn':('"Xoay shoulder, elbow, hip, knee, neck, thân ở góc thường dùng. Gửi ảnh từng khớp, camera gần."','ảnh nhân vật ở nhiều tư thế. Bạn nhìn skin có phình, thắt, dính không.'),
 'Picker giúp chọn control nhanh':('"Làm picker cho Ninja: mỗi nút chọn đúng một control, không nút nào đè nhau. Liệt kê control chưa có nút."','ảnh picker và danh sách control chưa có nút.'),
 'Thử rig như người làm hoạt hình sẽ dùng':('"Thử đủ 2 tay và 2 chân, cả IK và FK. Đổi sang frame khác rồi quay về, báo bind pose có đổi không. Liệt kê cái chưa kiểm."','bảng ✓ / ✗ cho 2 tay và 2 chân và danh sách cái chưa kiểm.'),
 'Hai loại file, chỉ xuất khi bạn nói "chốt"':('"Chốt rig Ninja. Xuất file Base, kiểm trong Unity, báo lỗi nếu có."','1 file Base và báo kết quả kiểm trong game.'),
})
