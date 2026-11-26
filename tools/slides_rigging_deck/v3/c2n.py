# ===== BƯỚC 1
std('Bước 1 · Nhận việc, đo model','Biết có gì và nhân vật to cỡ nào',[
 blk('Để làm gì','Biết đủ file chưa, nhân vật cao bao nhiêu, mấy mảnh, quay mặt đâu.'),
 blk('Bạn chuẩn bị','File nhân vật (.fbx) và ảnh màu (texture).'),
 blk('Windy','<b>2 mảnh</b>: thân (có đầu, áo choàng) và cây gậy. Cao 185 cm. Gậy là mảnh riêng vì chiêu cuối gậy bay tự do.'),
 blk('Bạn xem gì','Số mảnh, chiều cao, hướng mặt AI báo có khớp hình không.')],
 [('img/windy/w_mesh.png','Windy chưa rig, kèm số đo.','wd')],fw=1.05)
std('Bước 1 · Lỗi AI hay mắc','AI đoán thay vì đo',[
 err('Ví dụ thật','AI cắt cả model một lần: áo choàng lẫn vào chân, giáp lẫn vào tay.'),
 err('Ví dụ thật','AI gọi mảnh nhỏ là "mắt", thực ra là cánh. Hai file còn bị quay ngược.'),
 fix('Bạn nói','<b>"Đo bằng số, gửi bảng cho mình: số mảnh, cỡ, hướng mặt."</b>')],
 [],dark=True)
# ===== BƯỚC 2
std('Bước 2 · Kiểm lưới (cổng)','Lưới tốt thì da mới uốn đẹp',[
 blk('Để làm gì','Lưới là mạng ô trên vỏ. Ít ô hoặc lộn xộn thì chỗ gập bị góc cạnh.'),
 blk('Windy','Khoảng <b>2.950 tam giác</b>, vừa cho game điện thoại.'),
 blk('Bạn xem gì','Nhìn ảnh phóng to vai: quanh khớp có mấy vòng ô? Ít vòng thì chưa tốt.')],
 [('img/windy/w_wire.png','Windy: toàn bộ lưới.','wd'),('img/windy/w_wire_zoom.png','Phóng to vai: đếm vòng ô quanh khớp.','wd')],fw=1.2,mh=330)
std('Bước 2 · Đạt, chưa đạt, lỗi hay mắc','Lưới đạt trông thế nào',[
 err('Ví dụ thật','AI chỉ giảm bớt tam giác rồi coi như dựng lại lưới. Như vậy không sửa được hướng các ô.'),
 err('Ví dụ thật','Màu bị lật dọc khi vào Frolvy. Chỉ lật để xem, file cho game vẫn dùng ảnh gốc.'),
 fix('Bạn hỏi','<b>"Lưới đạt hay chưa? Chỗ nào chưa?"</b> Chưa đạt thì xin người vẽ model làm lại lưới.')],
 [('img/rig/d_meshokbad.svg','Lưới quanh một khớp: đạt (trái), chưa đạt (phải).','sch'),('img/rig/d_uvflip.svg','Bẫy màu bị lật.','sch')],dark=True,fw=1.2,mh=300)
# ===== BƯỚC 3
std('Bước 3 · Đặt xương (1/6)','Xương đặt ở chỗ khớp thật sự gập',[
 blk('Để làm gì','Xương là bộ khung. Đặt sai chỗ thì nhân vật gập sai chỗ.'),
 blk('Quy tắc','Đặt <b>đúng chỗ cơ thể gập</b> (khuỷu tay, đầu gối), không đặt giữa khối bắp tay hay đùi.'),
 blk('Windy','36 điểm xương: thân, chân, tay, ngón (đeo găng nên chỉ ngón giữa và ngón cái).')],
 [('img/windy/w_joints_front.png','Nhìn trước (bên phải nhân vật ở bên trái ảnh).','wd'),('img/windy/w_joints_side.png','Nhìn bên. Đường chéo dài là cây gậy.','wd'),('img/windy/w_joints_top.png','Nhìn trên (mặt nhìn xuống dưới).','wd')],fw=2.0,mh=560,row=True)
std('Bước 3 · Đặt xương (2/6)','Chân: hông, gối, cổ chân',[
 blk('Hông · cao 66,2 cm','Chỗ đùi gắn vào hông.'),
 blk('Gối · cao 36,6 cm','Giữa đùi và cẳng chân.'),
 blk('Cổ chân · cao 9,9 cm','Chỗ cẳng chân gặp bàn chân, thấp, <b>ngay trên gót</b>.')],
 [('img/windy/w_leg.png','Windy, phóng to chân. Số là độ cao so với sàn.','wd')],fw=1.9,mh=640)
std('Bước 3 · Đặt xương (3/6)','Thân và đầu',[
 blk('Gốc · cao 70,7 cm','Xương gốc ở <b>vùng hông</b>, cao hơn hai khớp hông một chút.'),
 blk('Cột sống · 87,1 → 103,7 → 123,2','Ba điểm cách nhau gần đều để thân gập mượt.'),
 blk('Đầu · 132,6 · Đỉnh đầu · 185','Đầu xoay ở gáy. Điểm cuối nằm ở <b>đỉnh đầu</b>.')],
 [('img/windy/w_spine.png','Windy: thân và đầu, số là độ cao (cm).','wd')],fw=1.9,mh=640)
std('Bước 3 · Đặt xương (4/6)','Tay: bả vai, vai, khuỷu, cổ tay',[
 blk('Bả vai','Gần xương sống. Vai nhấc lên hạ xuống nhờ nó.'),
 blk('Vai','<b>Nằm trong thân</b>, không ở rìa chỗ cánh tay mọc ra.'),
 blk('Khuỷu, cổ tay','Khuỷu ở khoảng giữa vai và cổ tay.')],
 [('img/windy/w_arm.png','Windy: tay phải (bên trái ảnh), tay cầm gậy.','wd')],fw=1.9,mh=520)
std('Bước 3 · Đặt xương (5/6, cổng duyệt)','Đạt hay chưa đạt? Nhìn 3 góc rồi sửa',[
 blk('Bạn xem','Bảo AI chụp <b>trước, bên, trên</b>. Hỏi: mỗi chấm có đúng chỗ khớp xoay không?'),
 blk('Windy: 4 điểm cần sửa',ul('<b>Ngực</b> hạ xuống 4 cm','<b>Đỉnh đầu</b> về đúng đỉnh (đang cao hơn 10 cm)','<b>Bả vai, vai</b> ra ngoài 6 cm')),
 blk('Sau khi bạn sửa','Nói: <b>"Giữ nguyên chỗ mình sửa."</b>')],
 [('img/windy/w_beforeafter.png','Trái: chưa đạt. Phải: đạt (vòng đỏ là chỗ cũ).','wd')],fw=1.8,mh=640)
std('Bước 3 · Lỗi AI hay mắc (6/6)','AI đặt xương ở chỗ "dễ thấy", không phải chỗ gập',[
 err('Ví dụ thật','Một nhân vật cao 1 m: AI đặt xương cổ chân cao 11,5 cm. Đúng phải là 6,5 cm (chỗ cẳng chân gặp bàn chân). Lệch 5 cm nên chân gập sai chỗ. Người duyệt phải sửa tay hơn nửa số xương.'),
 fix('Bạn nói','<b>"Chụp trước, bên, trên gửi mình trước khi build."</b> Nhìn bằng mắt rồi mới gật.')],
 [('img/rig/d_ankle.svg','Cổ chân đặt cao 11,5 cm thay vì 6,5 cm.','sch')],dark=True,fw=1.3)
# ===== BƯỚC 4
std('Bước 4 · Chuỗi xương','Đuôi, áo choàng: mỗi thứ một chuỗi xương',[
 blk('Để làm gì','Phần mềm như đuôi, áo choàng cần nhiều xương nối nhau để uốn lượn.'),
 blk('Quy tắc','Đầu chuỗi ở <b>chỗ gắn vào thân</b>. Chỗ cuộn gấp thì thêm xương.'),
 blk('Windy','Áo choàng có chuỗi xương. <b>Chưa có ảnh Windy thật bước này</b>, hình bên là con vật khác có đuôi tương tự.')],
 [('img/rig/wc_tail.jpg','Một con vật: chuỗi xương bám theo đuôi cuộn.','real'),('img/rig/kitsune_rig.jpg','Một con vật khác: chuỗi xương ở đầu và đuôi.','real')],fw=1.2,mh=300)
std('Bước 4 · Lỗi AI hay mắc','Mất công bạn đã sửa',[
 err('Ví dụ thật','Bạn hạ vài xương, AI tự đổi cả chỗ bạn đã sửa. Công bạn mất.'),
 err('Ví dụ thật','Một lệnh Build nhầm đã <b>xoá hết dây điều khiển bên trái</b>. Không hoàn tác được.'),
 fix('Bạn nói','<b>"Giữ nguyên chỗ mình sửa."</b> Trước lệnh có nguy cơ xoá, nhắc AI lưu file.')],
 [],dark=True)
# ===== BƯỚC 5
std('Bước 5 · Build Rig','Bấm Build Rig: từ bộ xương ra rig dùng được',[
 blk('Để làm gì','Frolvy tự sinh dây điều khiển từ bộ xương bạn đã đặt.'),
 blk('Trước khi bấm',ul('Bỏ xương phụ (xương thêm cho hiệu ứng, game điện thoại không dùng)','Xương gốc ở hông','Dựng lại lần hai: đưa mọi dây về 0 trước')),
 blk('Bạn xem gì','Xương đúng chỗ, không có bản sao thừa, hai bên giống nhau.')],
 [('img/rig/d_build.svg','Build Rig sinh thêm gì.','sch')],fw=1.5)
std('Bước 5 · Lỗi AI hay mắc','Build để lại rác',[
 err('Ví dụ thật','AI tự bật thêm bộ xương phụ nên dư <b>126 xương</b>, thân bị kéo theo tay chân.'),
 err('Ví dụ thật','Dựng lại rig nhiều lần: xương cũ vẫn lọt vào file, thành "xương ma".'),
 fix('Bạn nói','<b>"Build một lần cho sạch."</b> Phải dựng lại thì đưa dây về 0 trước.')],
 [],dark=True)
