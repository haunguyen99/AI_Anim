# ===== BƯỚC 6
std('Bước 6 · Control','Control phải thấy được và bấm được',[
 blk('Để làm gì','Người làm hoạt hình kéo control mỗi ngày. Control chìm trong mesh hoặc to quá thì không ai dùng.'),
 blk('Quy tắc','Vẽ ôm sát mesh. Hai bên trái phải giống nhau (bên trái là bản lật của bên phải).'),
 blk('Windy','Gậy có <b>hai control</b>: một theo tay phải, một để gậy bay tự do (gọi là <b>target control</b>).')],
 [('img/rig/d_staffctl.svg','Windy: hai control của gậy.','sch')],fw=1.5)
std('Bước 6 · Lỗi AI hay mắc','Control ẩn, quá to, hai bên khác nhau',[
 err('Ví dụ 1 (không có hình)','"Control bị ẩn trong mesh." Có vòng ở ankle to tới 2 m.'),
 err('Ví dụ 2 (xem biểu đồ)','Control ở shoulder bên phải to 0,84 m, bên trái chỉ 0,15 m.'),
 fix('Bạn nói','<b>"Liệt kê cỡ mọi control, so trái với phải."</b>')],
 [('img/rig/d_ctl_size.svg','Control hai bên chênh nhau. Xanh dương: phải. Tím: trái.','sch')],dark=True,fw=1.4)
# ===== BƯỚC 7
std('Bước 7 · Bind skin (1/3)','Mỗi điểm trên skin nghe lời joint nào, bao nhiêu phần',[
 blk('Weight','Phần trăm nghe lời của một điểm với từng joint. Tổng luôn <b>100%</b>. Khác 100% thì điểm đó bị kéo lệch.'),
 blk('Ba luật',ul('Tối đa 4 joint mỗi điểm (để game chạy nhẹ)','Mảnh cứng (gậy, giáp) bám 100% một joint','Joint ở xa không được kéo')),
 blk('Windy','Gậy bám 100% một joint riêng nên bay tự do được.')],
 [('img/rig/d_skinrule.svg','Weight là gì, và Windy áp dụng ra sao.','sch')],fw=1.5)
std('Bước 7 · Bind skin (2/3, gate)','Đạt hay chưa đạt? Xoay từng khớp rồi nhìn',[
 blk('Bạn xem','AI xoay shoulder, elbow, hip, knee, neck, thân. Bạn nhìn bằng mắt, từ gần.'),
 blk('Đạt','Skin gập tự nhiên, không phình, không thắt, không dính sang chỗ khác.'),
 blk('Đừng chỉ tin số','Số đẹp vẫn có thể che lỗi mắt thấy.')],
 [('img/rig/nb_cell_bad.jpg','Một con vật, tư thế cánh vỗ lên, lần thử đầu: cánh phình to, dính vào đầu.','real bad'),('img/rig/nb_cell_good.jpg','Cùng tư thế, lần thử thứ 13: cánh gọn, tách khỏi đầu.','real good')],fw=1.5,mh=560,row=True)
std('Bước 7 · Lỗi AI hay mắc (3/3)','Skin dán lệch: bind pose thì ổn, cử động mới vỡ',[
 err('Ví dụ thật','"Cánh dính vào mặt" báo tới <b>4 lần</b>. Chỉnh weight mãi không hết, vì skin bị dán lúc một control đang lệch.'),
 err('Ví dụ thật','Elbow hở khi gập, bắp tay trượt ra khỏi ống giáp.'),
 fix('Bạn nói','<b>"Đưa mọi control về 0 rồi bind skin lại."</b> Báo móp thì nói rõ <b>khớp nào, xem từ góc nào</b>.')],
 [('img/rig/nb_cell_bad.jpg','Lỗi 1: cánh dính vào đầu.','real'),('img/rig/d_elbow.svg','Lỗi 2: elbow hở khi gập.','sch')],dark=True,fw=1.3,mh=260)
# ===== BƯỚC 8
std('Bước 8 · Picker','Picker giúp chọn control nhanh',[
 blk('Để làm gì','Bấm nút trên bảng thay vì mò từng control trên nhân vật.'),
 blk('Bạn xem gì','Bấm từng nút ra đúng control. Không nút nào đè nhau.'),
 err('Ví dụ thật','Đổi cỡ control mà quên đổi nút trên bảng, phải sửa hai vòng.')],
 [('img/rig/d_picker.svg','Bố cục picker. Xanh dương: phải. Tím: trái. Vàng: thân.','sch')],fw=1.5)
# ===== BƯỚC 9
std('Bước 9 · Thử rig (gate)','Thử rig như người làm hoạt hình sẽ dùng',[
 blk('Bạn xem',ul('AI thử đủ <b>2 tay và 2 chân</b>, cả IK và FK','AI báo: đổi frame rồi quay lại, bind pose không đổi','Màu texture đúng')),
 blk('AI phải báo','Cái nào <b>chưa kiểm</b> (chưa thử trong game, chưa quay video).'),
 blk('Windy','Xoay tay: gậy có đi theo không? Áo choàng có bay không?')],
 [('img/rig/d_check.svg','Kiểm đúng: đủ 8 ô.','sch')],fw=1.4)
std('Bước 9 · Lỗi AI hay mắc','AI báo "xong" khi chưa thử hết',[
 err('Ví dụ thật','Wrist phải hỏng nhưng lần kiểm vẫn báo sạch, vì chỉ thử <b>tay trái</b>.'),
 err('Ví dụ thật','Rig không về dáng gốc khi đổi frame, có knee lệch 2 cm. Người duyệt phải tự bắt.'),
 fix('Bạn nói','<b>"Liệt kê cái chưa kiểm."</b> Và: <b>"Đổi sang frame khác rồi quay về, báo bind pose có đổi không."</b>')],
 [],dark=True)
# ===== BƯỚC 10
std('Bước 10 · Export FBX','Hai loại file, chỉ xuất khi bạn nói "chốt"',[
 blk('Hai loại file',ul('<b>File Base</b>: joint + mesh. Xuất ở bước này','<b>File Anim</b>: joint + chuyển động. Có khi làm hoạt hình sau này')),
 blk('Quy tắc','Bạn nói <b>"chốt"</b> thì AI mới xuất. Còn sửa thì AI chỉ sửa.'),
 blk('Windy','Giữ nguyên tên và cây joint của team. Đã thử xuất để kiểm: khớp với file của team (chưa giao).')],
 [('img/rig/d_files.svg','Hai loại file đưa vào game.','sch')],fw=1.4)
std('Bước 10 · Lỗi AI hay mắc','File vào game bị vỡ',[
 err('Ví dụ thật','<b>Đầu và chân bay khỏi thân</b>: file thiếu thông tin bind pose. Cách sửa: thêm thông tin đó.'),
 err('Ví dụ thật','File chuyển động báo lỗi gốc: thiếu một điểm phụ. Cách sửa: thêm điểm phụ.'),
 fix('Bạn nói','<b>"Kiểm file bằng game và đọc báo lỗi."</b> Đừng đoán.')],
 [('img/rig/d_bindpose.svg','Hai lỗi khi file vào game.','sch')],dark=True,fw=1.0)
# ===== PHẦN C
raw('''<p class="kick">Phần C · Dùng ngay</p><h2>Thấy gì thì nghi lỗi nào</h2>
<table style="font-size:25px"><tr><th style="width:32%">Bạn thấy</th><th style="width:30%">Thường do</th><th>Bạn nói</th></tr>
<tr class="hl"><td>Skin móp khi xoay</td><td>Weight sai</td><td>"Móp ở khớp … khi xoay …"</td></tr>
<tr><td>Cánh, tai dính vào mặt</td><td>Bind skin lúc control lệch</td><td>"Đưa control về 0, dán lại"</td></tr>
<tr class="hl"><td>Rig nghiêng dù control ở 0</td><td>Dựng lại khi đang lệch</td><td>"Về 0 rồi dựng lại"</td></tr>
<tr><td>Control ẩn, to quá, lệch hai bên</td><td>Vẽ control không theo mesh</td><td>"Liệt kê cỡ, so trái phải"</td></tr>
<tr class="hl"><td>Joint sai chỗ khớp</td><td>AI đặt theo giữa khối</td><td>"Chụp 3 góc gửi mình"</td></tr>
<tr><td>Vào game thấy vỡ</td><td>Thiếu thông tin trong file</td><td>"Kiểm file bằng game"</td></tr>
<tr class="hl"><td>AI báo xong mà vẫn sai</td><td>Chưa kiểm hết</td><td>"Liệt kê cái chưa kiểm"</td></tr></table>''')
std('Phần C · Dùng ngay','Câu nói để AI làm đúng',[
 '<div class="say"><b>Giao việc:</b> "Rig nhân vật Windy trong Frolvy. Dừng ở bước đặt joint, chụp 3 góc gửi mình duyệt."</div>',
 '<div class="say"><b>Đạt:</b> "Đạt. Đi tiếp bước sau."</div>',
 '<div class="say"><b>Chưa đạt:</b> "Điểm Chest hạ xuống 4 cm. Giữ nguyên chỗ mình đã sửa."</div>',
 '<div class="say"><b>Dừng:</b> "Dừng lại. Quay về bước đặt joint, ankle sai chỗ."</div>',
 '<div class="say"><b>Bắt kiểm:</b> "Thử đủ 2 tay và 2 chân, đổi frame báo bind pose có đổi không. Liệt kê cái chưa kiểm."</div>',
 '<div class="say"><b>Chốt:</b> "Chốt rig. Export FBX Base, kiểm trong game."</div>'],
 [('img/windy/w_beforeafter.png','Góp ý tốt nói rõ <b>điểm nào</b>, <b>sửa bao nhiêu</b>, <b>hướng nào</b>.','wd')],fw=1.2,mh=460)
raw('''<p class="kick">Phần C · Dùng ngay</p><h2>Checklist duyệt rig</h2>
<div class="row bigl"><div class="card"><ul><li>Topology đã kiểm</li><li>Joint đúng chỗ khớp, đã xem 3 góc</li><li>Root joint ở hip</li><li>Joint chain đuôi, áo choàng đúng hình</li><li>Control thấy rõ, không quá to</li><li>Hai bên trái phải giống nhau</li></ul></div>
<div class="card"><ul><li>Skin bám tối đa 4 joint mỗi điểm</li><li>Đã xoay mọi khớp và nhìn bằng mắt</li><li>AI báo bind pose không đổi khi đổi frame</li><li>Picker khớp với control</li><li>AI ghi rõ cái chưa kiểm</li><li>Chỉ xuất khi đã "chốt"</li></ul></div></div>''',dark=True)
