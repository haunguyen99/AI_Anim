# ===== BƯỚC 2 đặt joint
std('Bước 2 · Đặt joint (1/6)','Joint đặt ở chỗ khớp thật sự xoay, không phải giữa khối',[
 blk('Để làm gì','Joint là xương của nhân vật. Đặt sai chỗ thì xoay lên nhân vật gập sai chỗ.'),
 blk('Quy tắc gốc','Đặt joint ở <b>điểm xoay</b> (nơi cơ thể thật sự gập), không phải ở tâm hình khối của bộ phận.'),
 blk('Windy có gì','36 joint trong file: thân, chân, tay (ngón giữa + ngón cái), cộng chuỗi áo choàng. Hình bên là nhìn trước và nhìn bên.'),
 blk('Chỉ đặt một bên','Chỉ đặt bên phải và giữa; bên trái Frolvy tự nhân đôi.')],
 [('img/windy/w_joints_front.png','Nhìn trước (bên phải nhân vật nằm bên trái ảnh).','wd'),('img/windy/w_joints_side.png','Nhìn bên (mặt hướng sang phải ảnh).','wd')],fw=1.4,mh=560,row=True)
std('Bước 2 · Đặt joint (2/6)','Chân: Hông, Gối, Cổ chân, Ngón chân',[
 blk('Hip · 66,2 cm','Khớp đùi gắn vào hông, hai bên cách đường giữa khoảng 10 cm.'),
 blk('Knee · 36,6 cm','Giữa đùi và cẳng chân, cách hông khoảng 52% đường tới cổ chân.'),
 blk('Ankle · 9,9 cm','Chỗ cẳng chân gặp bàn chân, thấp, <b>trên gót</b>.'),
 blk('Toes · 3,7 · Heel · 0,3','Ngón chân và gót; hai điểm chạm sàn.')],
 [('img/windy/w_leg.png','Windy, phóng to chân (số là độ cao so với sàn).','wd')],fw=1.9,mh=640)
std('Bước 2 · Đặt joint (3/6)','Thân và đầu: cột sống chia đều, HeadEnd ở đỉnh đầu',[
 blk('Root · 70,7 cm','Gốc của cả bộ xương, đặt ở <b>hông</b> (Unity gọi là Hips). Mọi joint khác nối từ đây.'),
 blk('Spine1 → Chest → Neck','87,1 → 103,7 → 123,2 cm. Khoảng cách 16,4 / 16,6 / 19,5 cm: chia gần đều để thân gập mượt.'),
 blk('Head · 132,6 cm','Khớp xoay đầu nằm ở gốc đầu (gáy).'),
 blk('HeadEnd · 185,0 cm','Điểm cuối, nằm ở <b>đỉnh đầu</b> (bằng đỉnh mesh).')],
 [('img/windy/w_spine.png','Windy: thân và đầu, số là độ cao (cm). Đã hạ Chest 4 cm và đưa HeadEnd về đỉnh đầu.','wd')],fw=1.9,mh=640)
std('Bước 2 · Đặt joint (4/6)','Tay: Vai bả, Vai, Khuỷu, Cổ tay, ngón tay',[
 blk('Scapula (bả vai)','Cách đường giữa 10,6 cm, nằm gần xương sống. Vai nhấc lên xuống nhờ nó.'),
 blk('Shoulder (vai)','Cách đường giữa 22,6 cm, nằm trong thân, không ở rìa chỗ cánh tay mọc ra.'),
 blk('Elbow, Wrist','Khuỷu 42,1 cm (khoảng giữa vai và cổ tay), cổ tay 62,9 cm.'),
 blk('Ngón tay','Windy đeo găng: chỉ ngón giữa và ngón cái, 3 đốt mỗi ngón.')],
 [('img/windy/w_arm.png','Windy: chuỗi tay phải (bên trái ảnh). Gậy ở tay này.','wd')],fw=1.9,mh=520)
std('Bước 2 · Đặt joint (5/6)','Cổng duyệt: bạn xem hình 3 góc và sửa điểm sai',[
 blk('Bạn xem gì','Chụp <b>trước, bên, trên</b> với joint chồng mesh. Hỏi: từng chấm có đúng chỗ khớp xoay không?'),
 blk('Ví dụ Windy: 4 điểm cần chỉnh',ul('<b>Chest</b> hạ xuống thấp hơn 4 cm','<b>HeadEnd</b> về đỉnh đầu (trong file đang cao hơn đầu 10,7 cm)','<b>Scapula</b> và <b>Shoulder</b> dịch ra ngoài 6 cm')),
 blk('Sau khi bạn chỉnh','AI giữ nguyên chỗ bạn đã sửa, chỉ đặt lại các joint con quanh nó.')],
 [('img/windy/w_beforeafter.png','Trái: joint đúng như trong file. Phải: sau chỉnh, 4 điểm đỏ là chỗ đã sửa.','wd')],fw=1.8,mh=640)
std('Bước 2 · Lỗi AI hay mắc','AI đặt theo tâm hình khối, người duyệt phải chỉnh tay',[
 err('Lỗi thật · MeoTom','Hậu chỉnh tay 18 / 33 joint hơn 2 cm (trung bình 2,5 cm, lớn nhất 8,4 cm). Cổ chân AI đặt cao 0,115, đúng là 0,065. Hướng bàn chân AI đo ra 5–9°, đúng khoảng 39°.'),
 err('Cũng gặp','Cột sống không chia đều, Neck thấp 2,9 cm; hông lệch ra ngoài 2,5 cm; gốc tai theo mép ngoài thay vì sát đỉnh đầu (lệch khoảng 5 cm).'),
 fix('Bạn làm gì','Bắt AI <b>chụp 3 góc gửi bạn trước khi build</b>. Số đo tâm mặt cắt chỉ để tham khảo, bạn nhìn bằng mắt rồi mới duyệt.')],
 [('img/rig/d_ankle.svg','MeoTom: cổ chân đặt ở chỗ thắt (0,115) thay vì chỗ chân gặp bàn chân (0,065).','sch'),('img/rig/d_foot_dir.svg','MeoTom: hướng bàn chân nhìn từ trên.','sch')],dark=True,fw=1.2,mh=290)
# ===== BƯỚC 3 chuỗi joint
std('Bước 3 · Chuỗi joint','Đuôi, tai, hàm, áo choàng, khăn: mỗi thứ một chuỗi joint',[
 blk('Để làm gì','Phần mềm mềm (đuôi, áo choàng, khăn) cần nhiều joint nối nhau thành chuỗi để uốn lượn khi nhân vật cử động.'),
 blk('AI làm',ul('Đặt chuỗi theo đường tâm của bộ phận','<b>Đầu chuỗi ở chỗ gắn vào thân</b> (cạp váy, gốc đuôi), không ở Root','Chỗ cuộn gấp thì thêm đốt, điểm cuối nằm trong mesh')),
 blk('Windy','Trong file joint có các chuỗi áo choàng. <b>Ảnh vị trí chuỗi Windy cần chụp từ Frolvy</b> (chưa vẽ được từ file); hình bên là chuỗi của Pet có cấu trúc tương tự.')],
 [('img/rig/wc_tail.jpg','Wind Chameleon: chuỗi joint bám theo đuôi cuộn.','real'),('img/rig/kitsune_rig.jpg','Kitsune Nine Mist: chuỗi joint đầu và đuôi.','real')],fw=1.2,mh=300)
std('Bước 3 · Lỗi AI hay mắc','Chuỗi joint và phần người đã chỉnh',[
 err('Lỗi thật · Hero RPG2','Người dùng hạ Root, Chest, Neck xuống 4–13 cm. Phải đặt lại Hip, Scapula, khăn, HeadEnd. Neck và Head bị hạ dưới vai: AI chỉ nên nhắc rủi ro, không tự đổi lại.'),
 err('Lỗi thật · Hero Axe','Lệnh Build với danh sách "một bên" để rỗng đã <b>xoá cả control bên trái</b>. Hoàn tác không lấy lại, phải dựng lại rig.'),
 err('Lỗi thật · MeoTom','Đuôi cuộn đặt thiếu đốt ở chỗ cuộn, Hậu thêm một đốt và hạ hai đốt cuối.'),
 fix('Bạn làm gì','Sau khi bạn sửa joint, nói: "<b>giữ nguyên chỗ mình sửa, chỉ đặt lại các joint con</b>". Lệnh có nguy cơ xoá (Build, Rebuild) thì nhắc AI lưu file trước.')],
 [('img/rig/wc_jaw.jpg','Wind Chameleon: hàm mở 4 mức. Bản lề hàm ngang miệng, JawEnd ở mút môi dưới.','real')],dark=True,fw=0.8,mh=560)
# ===== BƯỚC 4 Build Rig
std('Bước 4 · Build Rig','Bấm Build Rig: từ bộ xương trần ra rig dùng được',[
 blk('Để làm gì','Frolvy tự sinh joint DEF, control và công tắc IK/FK từ bộ joint bạn đã đặt.'),
 blk('Trước khi build',ul('Tắt helper, bendy, twist (game không cần)','Mọi control về 0','Root đặt ở hông, không có Pelvis')),
 blk('Bạn xem gì để duyệt','Joint đúng chỗ, không có bản trái thừa, công tắc IK/FK hai bên giống nhau. Windy: giữ nguyên tên và cây xương của team để Unity chạy.')],
 [('img/rig/d_build.svg','Build Rig sinh thêm gì.','sch')],fw=1.5)
std('Bước 4 · Lỗi AI hay mắc','Build và Rebuild để lại rác',[
 err('Lỗi thật · Bastion','AI tự bật "helper set": thêm <b>126 joint thừa</b>, thân bị kéo theo tay chân.'),
 err('Lỗi thật · Bastion','Rebuild khi Pelvis đang lệch: pose bị nướng vào rig, rig nghiêng dù mọi control = 0. Sau Rebuild còn mất dây tuỳ chỉnh, pivot control nằm ở chỗ joint cũ.'),
 err('Lỗi thật · Night Bat','Dựng lại rig trong cùng scene: joint và constraint cũ vẫn bị xuất ra thành <b>joint ma</b> trong FBX.'),
 fix('Bạn làm gì','Build <b>một lần cho sạch</b>. Rebuild thì bảo AI đưa control về 0 trước và kiểm lại pivot sau.')],
 [('img/rig/pinchy_rig.jpg','Pinchy Balboa: rig sạch sau khi sửa, chỉ có joint và control cần thiết.','real')],dark=True,fw=1.2,mh=420)
# ===== BƯỚC 5 Control
std('Bước 5 · Control','Control phải thấy được, bấm được, hai bên giống nhau',[
 blk('Để làm gì','Control là thứ animator kéo hằng ngày. Ẩn trong mesh hay to quá thì không ai muốn dùng.'),
 blk('Quy tắc',ul('Vẽ ôm sát mesh, rộng hơn vài cm','Control trục giữa cùng cỡ, nằm giữa','Hai bên trái và phải soi gương nhau')),
 blk('Windy: gậy có hai control','Một control theo tay phải; một control "đích" để gậy bay tự do ở Skill 3.')],
 [('img/rig/mecha_ctl.jpg','Mecha Pup: control (các vòng màu) quanh thân.','real'),('img/rig/d_staffctl.svg','Windy: hai control của gậy.','sch')],fw=1.2,mh=300)
std('Bước 5 · Lỗi AI hay mắc','Control ẩn, to quá, lệch hai bên',[
 err('Lỗi thật · Hero RPG2','"Mỗi lần tạo control luôn bị ẩn trong mesh". Vòng cổ chân 2 m, vai 2,5 m vì váy, mũ là lưới một lớp. Switch tay phải ra 2 cm trong bàn tay, tay trái 5,6 cm trên cổ tay.'),
 err('Lỗi thật · Hero Axe','Vòng ôm cả rìu: cổ tay 1,46 m, Root 1,85 m.'),
 err('Lỗi thật · MeoTom','Shoulder phải 0,84 m, trái 0,15 m; HipSwinger lệch 33 cm khỏi hông.'),
 fix('Bạn làm gì','Bảo AI: <b>"liệt kê cỡ mọi control, so trái với phải"</b> rồi mới duyệt.')],
 [('img/rig/d_ctl_size.svg','MeoTom sau Build: control hai bên chênh nhau.','sch')],dark=True,fw=1.4)
