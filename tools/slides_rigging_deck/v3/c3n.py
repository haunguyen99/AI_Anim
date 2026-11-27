# ===== BƯỚC 6
std('Bước 6 · Dây điều khiển','Dây phải thấy được và bấm được',[
 blk('Để làm gì','Người làm hoạt hình kéo dây mỗi ngày. Dây chìm trong vỏ hoặc to quá thì không ai dùng.'),
 blk('Quy tắc','Vẽ ôm sát vỏ. Hai bên trái phải giống nhau (bên trái là bản lật của bên phải).'),
 blk('Windy','Gậy có <b>hai dây</b>: một theo tay phải, một để gậy bay tự do (gọi là <b>dây đích</b>).')],
 [('img/rig/d_staffctl.svg','Windy: hai dây của gậy.','sch')],fw=1.5)
std('Bước 6 · Lỗi AI hay mắc','Dây ẩn, quá to, hai bên khác nhau',[
 err('Ví dụ 1 (không có hình)','"Dây bị ẩn trong vỏ." Có vòng ở cổ chân to tới 2 m.'),
 err('Ví dụ 2 (xem biểu đồ)','Dây ở vai bên phải to 0,84 m, bên trái chỉ 0,15 m.'),
 fix('Bạn nói','<b>"Liệt kê cỡ mọi dây, so trái với phải."</b>')],
 [('img/rig/d_ctl_size.svg','Dây hai bên chênh nhau. Xanh dương: phải. Tím: trái.','sch')],dark=True,fw=1.4)
# ===== BƯỚC 7
std('Bước 7 · Dán da (1/3)','Mỗi điểm trên da nghe lời xương nào, bao nhiêu phần',[
 blk('Mức bám','Phần trăm nghe lời của một điểm với từng xương. Tổng luôn <b>100%</b>. Khác 100% thì điểm đó bị kéo lệch.'),
 blk('Ba luật',ul('Tối đa 4 xương mỗi điểm (để game chạy nhẹ)','Mảnh cứng (gậy, giáp) bám 100% một xương','Xương ở xa không được kéo')),
 blk('Windy','Gậy bám 100% một xương riêng nên bay tự do được.')],
 [('img/rig/d_skinrule.svg','Mức bám là gì, và Windy áp dụng ra sao.','sch')],fw=1.5)
std('Bước 7 · Dán da (2/3, cổng)','Đạt hay chưa đạt? Xoay từng khớp rồi nhìn',[
 blk('Bạn xem','AI xoay vai, khuỷu, hông, gối, cổ, thân. Bạn nhìn bằng mắt, từ gần.'),
 blk('Đạt','Da gập tự nhiên, không phình, không thắt, không dính sang chỗ khác.'),
 blk('Đừng chỉ tin số','Số đẹp vẫn có thể che lỗi mắt thấy.')],
 [('img/rig/nb_cell_bad.jpg','Một con vật, tư thế cánh vỗ lên, lần thử đầu: cánh phình to, dính vào đầu.','real bad'),('img/rig/nb_cell_good.jpg','Cùng tư thế, lần thử thứ 13: cánh gọn, tách khỏi đầu.','real good')],fw=1.5,mh=560,row=True)
std('Bước 7 · Lỗi AI hay mắc (3/3)','Da dán lệch: tư thế gốc thì ổn, cử động mới vỡ',[
 err('Ví dụ thật','"Cánh dính vào mặt" báo tới <b>4 lần</b>. Chỉnh mức bám mãi không hết, vì da bị dán lúc một dây đang lệch.'),
 err('Ví dụ thật','Khuỷu hở khi gập, bắp tay trượt ra khỏi ống giáp.'),
 fix('Bạn nói','<b>"Đưa mọi dây về 0 rồi dán da lại."</b> Báo móp thì nói rõ <b>khớp nào, xem từ góc nào</b>.')],
 [('img/rig/nb_cell_bad.jpg','Lỗi 1: cánh dính vào đầu.','real'),('img/rig/d_elbow.svg','Lỗi 2: khuỷu hở khi gập.','sch')],dark=True,fw=1.3,mh=260)
# ===== BƯỚC 8
std('Bước 8 · Bảng nút','Bảng nút giúp chọn dây nhanh',[
 blk('Để làm gì','Bấm nút trên bảng thay vì mò từng dây trên nhân vật.'),
 blk('Bạn xem gì','Bấm từng nút ra đúng dây. Không nút nào đè nhau.'),
 err('Ví dụ thật','Đổi cỡ dây mà quên đổi nút trên bảng, phải sửa hai vòng.')],
 [('img/rig/d_picker.svg','Bố cục bảng nút. Xanh dương: phải. Tím: trái. Vàng: thân.','sch')],fw=1.5)
# ===== BƯỚC 9
std('Bước 9 · Thử rig (cổng)','Thử rig như người làm hoạt hình sẽ dùng',[
 blk('Bạn xem',ul('AI thử đủ <b>2 tay và 2 chân</b>, cả IK và FK','AI báo: đổi khung hình rồi quay lại, tư thế gốc không đổi','Màu texture đúng')),
 blk('AI phải báo','Cái nào <b>chưa kiểm</b> (chưa thử trong game, chưa quay video).'),
 blk('Windy','Xoay tay: gậy có đi theo không? Áo choàng có bay không?')],
 [('img/rig/d_check.svg','Kiểm đúng: đủ 8 ô.','sch')],fw=1.4)
std('Bước 9 · Lỗi AI hay mắc','AI báo "xong" khi chưa thử hết',[
 err('Ví dụ thật','Cổ tay phải hỏng nhưng lần kiểm vẫn báo sạch, vì chỉ thử <b>tay trái</b>.'),
 err('Ví dụ thật','Rig không về dáng gốc khi đổi khung hình, có gối lệch 2 cm. Người duyệt phải tự bắt.'),
 fix('Bạn nói','<b>"Liệt kê cái chưa kiểm."</b> Và: <b>"Đổi sang khung hình khác rồi quay về, báo tư thế gốc có đổi không."</b>')],
 [],dark=True)
# ===== BƯỚC 10
std('Bước 10 · Xuất file','Hai loại file, chỉ xuất khi bạn nói "chốt"',[
 blk('Hai loại file',ul('<b>File nhân vật</b>: xương + vỏ. Xuất ở bước này','<b>File chuyển động</b>: xương + chuyển động. Có khi làm hoạt hình sau này')),
 blk('Quy tắc','Bạn nói <b>"chốt"</b> thì AI mới xuất. Còn sửa thì AI chỉ sửa.'),
 blk('Windy','Giữ nguyên tên và cây xương của team. Đã thử xuất để kiểm: khớp với file của team (chưa giao).')],
 [('img/rig/d_files.svg','Hai loại file đưa vào game.','sch')],fw=1.4)
std('Bước 10 · Lỗi AI hay mắc','File vào game bị vỡ',[
 err('Ví dụ thật','<b>Đầu và chân bay khỏi thân</b>: file thiếu thông tin tư thế gốc. Cách sửa: thêm thông tin đó.'),
 err('Ví dụ thật','File chuyển động báo lỗi gốc: thiếu một điểm phụ. Cách sửa: thêm điểm phụ.'),
 fix('Bạn nói','<b>"Kiểm file bằng game và đọc báo lỗi."</b> Đừng đoán.')],
 [('img/rig/d_bindpose.svg','Hai lỗi khi file vào game.','sch')],dark=True,fw=1.0)
# ===== PHẦN C
raw('''<p class="kick">Phần C · Dùng ngay</p><h2>Thấy gì thì nghi lỗi nào</h2>
<table style="font-size:25px"><tr><th style="width:32%">Bạn thấy</th><th style="width:30%">Thường do</th><th>Bạn nói</th></tr>
<tr class="hl"><td>Da móp khi xoay</td><td>Mức bám sai</td><td>"Móp ở khớp … khi xoay …"</td></tr>
<tr><td>Cánh, tai dính vào mặt</td><td>Dán da lúc dây lệch</td><td>"Đưa dây về 0, dán lại"</td></tr>
<tr class="hl"><td>Rig nghiêng dù dây ở 0</td><td>Dựng lại khi đang lệch</td><td>"Về 0 rồi dựng lại"</td></tr>
<tr><td>Dây ẩn, to quá, lệch hai bên</td><td>Vẽ dây không theo vỏ</td><td>"Liệt kê cỡ, so trái phải"</td></tr>
<tr class="hl"><td>Xương sai chỗ khớp</td><td>AI đặt theo giữa khối</td><td>"Chụp 3 góc gửi mình"</td></tr>
<tr><td>Vào game thấy vỡ</td><td>Thiếu thông tin trong file</td><td>"Kiểm file bằng game"</td></tr>
<tr class="hl"><td>AI báo xong mà vẫn sai</td><td>Chưa kiểm hết</td><td>"Liệt kê cái chưa kiểm"</td></tr></table>''')
std('Phần C · Dùng ngay','Câu nói để AI làm đúng',[
 '<div class="say"><b>Giao việc:</b> "Rig nhân vật Windy trong Frolvy. Dừng ở bước đặt xương, chụp 3 góc gửi mình duyệt."</div>',
 '<div class="say"><b>Đạt:</b> "Đạt. Đi tiếp bước sau."</div>',
 '<div class="say"><b>Chưa đạt:</b> "Điểm Ngực hạ xuống 4 cm. Giữ nguyên chỗ mình đã sửa."</div>',
 '<div class="say"><b>Dừng:</b> "Dừng lại. Quay về bước đặt xương, cổ chân sai chỗ."</div>',
 '<div class="say"><b>Bắt kiểm:</b> "Thử đủ 2 tay và 2 chân, đổi khung hình báo tư thế gốc có đổi không. Liệt kê cái chưa kiểm."</div>',
 '<div class="say"><b>Chốt:</b> "Chốt rig. Xuất file nhân vật, kiểm trong game."</div>'],
 [('img/windy/w_beforeafter.png','Góp ý tốt nói rõ <b>điểm nào</b>, <b>sửa bao nhiêu</b>, <b>hướng nào</b>.','wd')],fw=1.2,mh=460)
raw('''<p class="kick">Phần C · Dùng ngay</p><h2>Checklist duyệt rig</h2>
<div class="row bigl"><div class="card"><ul><li>Lưới đã kiểm</li><li>Xương đúng chỗ khớp, đã xem 3 góc</li><li>Xương gốc ở hông</li><li>Chuỗi xương đuôi, áo choàng đúng hình</li><li>Dây thấy rõ, không quá to</li><li>Hai bên trái phải giống nhau</li></ul></div>
<div class="card"><ul><li>Da bám tối đa 4 xương mỗi điểm</li><li>Đã xoay mọi khớp và nhìn bằng mắt</li><li>AI báo tư thế gốc không đổi khi đổi khung hình</li><li>Bảng nút khớp với dây</li><li>AI ghi rõ cái chưa kiểm</li><li>Chỉ xuất khi đã "chốt"</li></ul></div></div>''',dark=True)
