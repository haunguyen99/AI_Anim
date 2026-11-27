# ===== BƯỚC 1
std('Bước 1 · Nhận việc và đo model','Biết mình có gì và nhân vật to cỡ nào',[
 blk('Để làm gì','Trước khi đặt xương phải biết có đủ file chưa, nhân vật cao bao nhiêu, gồm mấy mảnh rời, quay mặt về đâu.'),
 blk('Bạn chuẩn bị',ul('File model (.fbx) và texture (ảnh màu)','Tài liệu nói cần làm chuyển động gì, có đạo cụ gì')),
 blk('AI làm','Mở file, liệt kê các mảnh rời, đo chiều cao, báo hướng mặt, rồi <b>hỏi lại chỗ còn thiếu</b>.'),
 blk('Windy ở bước này','Có <b>2 mảnh</b>: thân (gồm đầu và áo choàng) và cây gậy. Cao 185 cm, sải tay 175,6 cm, mặt nhìn về phía trước, gậy ở tay phải. Ở chiêu cuối gậy bay tự do nên phải là mảnh riêng.'),
 blk('Bạn xem gì để duyệt','Số mảnh, chiều cao và hướng mặt AI báo có khớp với hình không.')],
 [('img/windy/w_mesh.png','Windy chưa rig, kèm số đo.','wd')],fw=1.05)
std('Bước 1 · Lỗi AI hay mắc','AI đoán thay vì đo, nên xương đặt sai từ đầu',[
 err('Ví dụ thật · nhân vật Hero','AI cắt cả model một lần: váy lẫn vào chân, giáp lẫn vào tay. Vì công cụ chỉ cắt mảnh lớn nhất nên phần chân và tay bị rỗng.'),
 err('Ví dụ thật · nhóm Pet','AI mô tả mảnh theo đoán: gọi mảnh nhỏ là "mắt" nhưng thực ra là cánh. Hai file mới còn bị quay ngược 180°.'),
 fix('Bạn làm gì','Bảo AI: <b>"Đo bằng số, gửi bảng cho mình trước: số mảnh, cỡ, hướng mặt."</b> Chỗ nào AI chỉ đoán thì bắt ghi rõ "chưa chắc".')],
 [],dark=True)
# ===== BƯỚC 2
std('Bước 2 · Kiểm lưới (cổng duyệt)','Lưới tốt thì da mới uốn đẹp',[
 blk('Để làm gì','Lưới là mạng ô trên vỏ nhân vật. Lưới ít ô hoặc lộn xộn thì chỗ gập sẽ góc cạnh, da kiểu gì cũng xấu.'),
 blk('AI làm',ul('Đếm số tam giác, xem lưới là ô vuông đều hay tam giác lộn xộn','Xem quanh vai, khuỷu, gối, cổ có đủ vòng lưới không','Xem nhân vật đang dang tay chữ T hay chữ A')),
 blk('Windy ở bước này','Khoảng <b>2.950 tam giác</b>, vừa với game điện thoại. Lưới thưa, kiểu low-poly.'),
 blk('Bạn xem gì để duyệt','Nhìn ảnh phóng to vai: quanh khớp có mấy vòng lưới? Ít vòng thì chỗ gập sẽ góc cạnh.')],
 [('img/windy/w_wire.png','Windy: toàn bộ lưới.','wd'),('img/windy/w_wire_zoom.png','Phóng to vai và tay: đếm vòng lưới quanh khớp.','wd')],fw=1.2,mh=330)
std('Bước 2 · Đạt hay chưa đạt, và lỗi AI hay mắc','Lưới đạt trông thế nào, và chữa sai cách',[
 err('Ví dụ thật · nhân vật MeoTom','AI giảm bớt tam giác rồi coi như đã dựng lại lưới. Giảm tam giác chỉ làm ít đi, không sửa được hướng của các ô. Lưới đúng phải có vòng ô quanh mắt, miệng, khớp.'),
 err('Ví dụ thật · nhân vật MeoTom','Texture bị lật dọc khi vào Frolvy (hình bên phải). Chỉ lật ảnh để xem, file xuất cho game vẫn dùng ảnh gốc.'),
 fix('Bạn làm gì','Hỏi AI: <b>"Lưới này đạt hay chưa đạt? Chỗ nào chưa đạt?"</b> Chưa đạt thì xin artist bản lưới dựng lại trước khi rig.')],
 [('img/rig/d_meshokbad.svg','Lưới quanh một khớp: đạt (trái) và chưa đạt (phải).','sch'),('img/rig/d_uvflip.svg','Bẫy texture lật dọc.','sch')],dark=True,fw=1.2,mh=300)
# ===== BƯỚC 3
std('Bước 3 · Đặt xương (1/6, cổng duyệt)','Xương đặt ở chỗ khớp thật sự gập',[
 blk('Để làm gì','Xương là bộ khung của nhân vật. Đặt sai chỗ thì nhân vật gập sai chỗ.'),
 blk('Quy tắc gốc','Đặt xương <b>đúng chỗ cơ thể thật sự gập</b>, như khuỷu tay, đầu gối. Không đặt ở giữa khối bắp tay hay đùi.'),
 blk('Chỉ đặt một bên','Bạn chỉ cần đặt bên phải và giữa. Bên trái Frolvy tự làm đối xứng.'),
 blk('Windy ở bước này','Bộ xương có <b>36 điểm</b>: thân, chân, tay và các ngón (Windy đeo găng nên chỉ có ngón giữa và ngón cái), cộng chuỗi xương áo choàng.')],
 [('img/windy/w_joints_front.png','Nhìn trước (bên phải nhân vật nằm bên trái ảnh).','wd'),('img/windy/w_joints_side.png','Nhìn bên (mặt nhìn sang phải).','wd')],fw=1.4,mh=560,row=True)
std('Bước 3 · Đặt xương (2/6)','Chân: hông, gối, cổ chân, ngón chân',[
 blk('Hông (Hip) · cao 66,2 cm','Chỗ đùi gắn vào hông, cách đường giữa khoảng 10 cm.'),
 blk('Gối (Knee) · cao 36,6 cm','Nằm giữa đùi và cẳng chân.'),
 blk('Cổ chân (Ankle) · cao 9,9 cm','Chỗ cẳng chân gặp bàn chân. Nằm thấp, <b>ngay trên gót</b>.'),
 blk('Ngón chân, gót','Hai điểm chạm sàn.')],
 [('img/windy/w_leg.png','Windy, phóng to chân. Số là độ cao so với sàn.','wd')],fw=1.9,mh=640)
std('Bước 3 · Đặt xương (3/6)','Thân và đầu: cột sống chia đều, điểm cuối ở đỉnh đầu',[
 blk('Gốc (Root) · cao 70,7 cm','Xương gốc đặt ở <b>hông</b>. Mọi xương khác nối từ đây.'),
 blk('Cột sống · 87,1 → 103,7 → 123,2 cm','Ba điểm cách nhau gần đều (16 đến 20 cm) để thân gập mượt.'),
 blk('Đầu (Head) · cao 132,6 cm','Chỗ đầu xoay, nằm ở gáy.'),
 blk('Điểm cuối đầu (HeadEnd) · cao 185 cm','Nằm ở <b>đỉnh đầu</b>, bằng đỉnh của vỏ.')],
 [('img/windy/w_spine.png','Windy: thân và đầu, số là độ cao (cm).','wd')],fw=1.9,mh=640)
std('Bước 3 · Đặt xương (4/6)','Tay: bả vai, vai, khuỷu, cổ tay, ngón',[
 blk('Bả vai (Scapula)','Cách đường giữa khoảng 10,6 cm, gần xương sống. Vai nhấc lên hạ xuống nhờ nó.'),
 blk('Vai (Shoulder)','Cách đường giữa khoảng 22,6 cm, nằm <b>trong thân</b>, không ở rìa chỗ cánh tay mọc ra.'),
 blk('Khuỷu, cổ tay','Khuỷu ở khoảng giữa vai và cổ tay (42,1 cm), cổ tay ở 62,9 cm.'),
 blk('Ngón','Windy đeo găng: chỉ có ngón giữa và ngón cái, 3 đốt mỗi ngón.')],
 [('img/windy/w_arm.png','Windy: tay phải (bên trái ảnh), tay cầm gậy.','wd')],fw=1.9,mh=520)
std('Bước 3 · Đặt xương (5/6): cổng duyệt','Đạt hay chưa đạt? Nhìn 3 góc rồi sửa điểm sai',[
 blk('Bạn xem gì','Yêu cầu AI chụp <b>trước, bên, trên</b> với xương chồng lên vỏ. Hỏi: từng chấm có nằm đúng chỗ khớp xoay không?'),
 blk('Ví dụ Windy: 4 điểm cần chỉnh',ul('<b>Ngực (Chest)</b> hạ thấp xuống 4 cm','<b>Điểm cuối đầu (HeadEnd)</b> về đỉnh đầu (đang cao hơn đầu khoảng 10 cm)','<b>Bả vai</b> và <b>vai</b> dịch ra ngoài 6 cm')),
 blk('Sau khi bạn chỉnh','Bảo AI: <b>"Giữ nguyên chỗ mình đã sửa, chỉ đặt lại các xương con quanh nó."</b>')],
 [('img/windy/w_beforeafter.png','Trái: CHƯA ĐẠT (xương như trong file). Phải: ĐẠT (sau chỉnh, 4 điểm đỏ là chỗ đã sửa).','wd')],fw=1.8,mh=640)
std('Bước 3 · Lỗi AI hay mắc (6/6)','AI đặt xương theo giữa khối, người duyệt phải chỉnh tay',[
 err('Ví dụ thật · nhân vật MeoTom','Người duyệt phải chỉnh tay hơn 1/2 số xương. Ví dụ cổ chân AI đặt ở chỗ thắt nhỏ nhất của cẳng chân, trong khi đúng phải ở chỗ chân gặp bàn chân, thấp hơn khoảng 5 cm.'),
 err('Cũng gặp','Cột sống không đều, đầu gối lệch, gốc tai đặt ở rìa thay vì sát đỉnh đầu.'),
 fix('Bạn làm gì','Đừng duyệt khi chưa thấy 3 góc. Bảo AI: <b>"Chụp trước, bên, trên gửi mình trước khi build."</b> Nhìn bằng mắt rồi mới gật.')],
 [('img/rig/d_ankle.svg','Cổ chân đặt ở chỗ thắt (0,115) thay vì chỗ chân gặp bàn chân (0,065).','sch')],dark=True,fw=1.3)
# ===== BƯỚC 4
std('Bước 4 · Chuỗi xương','Đuôi, tai, hàm, áo choàng: mỗi thứ một chuỗi xương',[
 blk('Để làm gì','Những phần mềm như đuôi, áo choàng, khăn cần nhiều xương nối nhau thành chuỗi để uốn lượn khi nhân vật cử động.'),
 blk('AI làm',ul('Đặt chuỗi theo đường giữa của bộ phận','Đầu chuỗi ở <b>chỗ gắn vào thân</b> (gốc đuôi, cạp váy)','Chỗ cuộn gấp thì thêm xương')),
 blk('Windy ở bước này','File xương của Windy có các chuỗi áo choàng. <b>Ảnh Windy thật của bước này chưa có</b> (cần chụp từ Frolvy). Hình bên là chuỗi của hai Pet có cấu trúc tương tự.')],
 [('img/rig/wc_tail.jpg','Pet Wind Chameleon: chuỗi xương bám theo cái đuôi cuộn.','real'),('img/rig/kitsune_rig.jpg','Pet Kitsune: chuỗi xương ở đầu và đuôi.','real')],fw=1.2,mh=300)
std('Bước 4 · Lỗi AI hay mắc','Chuỗi xương và phần bạn đã tự sửa',[
 err('Ví dụ thật · nhân vật Hero','Bạn hạ vài xương xuống thì AI phải đặt lại các xương con quanh đó. Nếu AI tự đổi cả chỗ bạn đã sửa thì công bạn mất.'),
 err('Ví dụ thật · nhân vật Hero Axe','Một lệnh Build với danh sách "một bên" để trống đã <b>xoá hết dây điều khiển bên trái</b>. Không hoàn tác được, phải dựng lại rig.'),
 fix('Bạn làm gì','Sau khi sửa tay: <b>"Giữ nguyên chỗ mình sửa, chỉ đặt lại xương con."</b> Trước lệnh có nguy cơ xoá, nhắc AI lưu file trước.')],
 [],dark=True)
# ===== BƯỚC 5
std('Bước 5 · Build Rig','Bấm Build Rig: từ bộ xương trần ra rig dùng được',[
 blk('Để làm gì','Frolvy tự sinh xương dùng cho game (DEF), dây điều khiển và công tắc IK/FK từ bộ xương bạn đã đặt.'),
 blk('Trước khi bấm',ul('Tắt các thêm thắt game không cần (helper, bendy, twist)','Đưa mọi dây điều khiển về 0','Xương gốc đặt ở hông, không có xương Pelvis')),
 blk('Windy ở bước này','Giữ nguyên tên và cây xương của team để file chạy được trong Unity.'),
 blk('Bạn xem gì để duyệt','Xương đúng chỗ, không có bản sao thừa bên trái, công tắc IK/FK hai bên giống nhau.')],
 [('img/rig/d_build.svg','Build Rig sinh thêm gì.','sch')],fw=1.5)
std('Bước 5 · Lỗi AI hay mắc','Build và dựng lại để lại "rác"',[
 err('Ví dụ thật · nhân vật Bastion','AI tự bật thêm bộ xương phụ nên dư <b>126 xương</b>, thân bị kéo theo tay chân. Rig game chỉ cần xương cơ bản.'),
 err('Ví dụ thật · nhân vật Night Bat','Dựng lại rig nhiều lần trong cùng một cảnh: xương cũ vẫn bị xuất ra file thành "xương ma".'),
 fix('Bạn làm gì','Bảo AI <b>build một lần cho sạch</b>. Nếu phải dựng lại, nhắc đưa dây điều khiển về 0 trước và kiểm lại tâm xoay sau.')],
 [('img/rig/pinchy_rig.jpg','Pet Pinchy Balboa: rig sạch, chỉ có xương và dây cần thiết.','real')],dark=True,fw=1.2,mh=420)
