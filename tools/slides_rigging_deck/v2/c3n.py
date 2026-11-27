# ===== BƯỚC 6
std('Bước 6 · Dây điều khiển','Dây điều khiển phải thấy được và bấm được',[
 blk('Để làm gì','Đây là thứ người làm hoạt hình kéo mỗi ngày. Nằm khuất trong vỏ hoặc to quá thì không ai muốn dùng.'),
 blk('Quy tắc',ul('Vẽ ôm sát vỏ, rộng hơn vài cm','Dây ở giữa thân cùng cỡ, nằm giữa','Hai bên trái và phải giống nhau như soi gương')),
 blk('Windy ở bước này','Cây gậy có <b>hai dây</b>: một dây đi theo tay phải, một dây "đích" để gậy bay tự do ở chiêu cuối.'),
 blk('Bạn xem gì để duyệt','Thấy rõ từng dây, không dây nào chìm trong vỏ, hai bên cùng cỡ.')],
 [('img/rig/mecha_ctl.jpg','Pet Mecha Pup: dây điều khiển (các vòng màu) quanh thân.','real'),('img/rig/d_staffctl.svg','Windy: hai dây điều khiển của gậy.','sch')],fw=1.2,mh=300)
std('Bước 6 · Lỗi AI hay mắc','Dây ẩn trong vỏ, quá to, hai bên không giống nhau',[
 err('Ví dụ thật · nhân vật Hero','"Mỗi lần tạo dây đều bị ẩn trong vỏ." Có vòng ở cổ chân to tới 2 m, ở vai 2,5 m vì váy và mũ chỉ là vỏ một lớp.'),
 err('Ví dụ thật · nhân vật MeoTom','Dây ở vai bên phải to 0,84 m, bên trái chỉ 0,15 m (xem biểu đồ).'),
 fix('Bạn làm gì','Bảo AI: <b>"Liệt kê cỡ mọi dây điều khiển, so bên trái với bên phải."</b> Rồi mới duyệt.')],
 [('img/rig/d_ctl_size.svg','Dây điều khiển hai bên chênh nhau. Đỏ: bên phải, xanh: bên trái.','sch')],dark=True,fw=1.4)
# ===== BƯỚC 7
std('Bước 7 · Dán da (1/3)','Dán da: mỗi điểm nghe lời xương nào',[
 blk('Để làm gì','Mỗi điểm trên vỏ phải "nghe lời" một hoặc vài xương. Phần trăm nghe lời gọi là <b>mức bám (weight)</b>, tổng luôn bằng 100%. Tổng khác 100% thì điểm đó bị kéo lệch khỏi chỗ đúng.'),
 blk('Ba luật chính',ul('Chỉ bám vào xương DEF, tối đa 4 xương mỗi điểm','Mảnh cứng (giáp, mắt, gậy) bám 100% vào một xương','Xương ở xa không được kéo: tay chân không kéo thân')),
 blk('Windy ở bước này','Thân người, đầu, áo choàng bám vào các xương của team. <b>Gậy bám 100% vào một xương riêng</b> nên bay tự do được.')],
 [('img/rig/d_skinrule.svg','Mức bám là gì và Windy áp dụng ra sao.','sch'),('img/rig/steam_weights.jpg','Pet Steam Pug: mỗi chấm là một điểm trên da, màu là xương điều khiển điểm đó nhiều nhất.','real')],fw=1.2,mh=270)
std('Bước 7 · Dán da (2/3): cổng duyệt','Đạt hay chưa đạt? Xoay từng khớp rồi nhìn bằng mắt',[
 blk('Bạn xem gì','AI xoay từng khớp (vai, khuỷu, hông, gối, cổ, thân) ở góc người làm hoạt hình hay dùng. Bạn nhìn bằng mắt, từ camera gần.'),
 blk('Dấu hiệu đạt','Da gập tự nhiên, không phình, không thắt lại, không dính sang bộ phận khác.'),
 blk('Đừng chỉ tin số','Con số đo độ co giãn chỉ để tham khảo. Số đẹp vẫn có thể che lỗi mắt nhìn thấy.')],
 [('img/rig/nb_skin_before.jpg','Pet Night Bat lần thử đầu: cánh phình, tai bị kéo méo, màng cánh dính vào mặt.','real bad'),('img/rig/nb_skin_after.jpg','Cùng 9 tư thế, lần thử thứ 13: cánh gọn, tai và đầu tách nhau.','real good')],fw=1.5,mh=560,row=True)
std('Bước 7 · Lỗi AI hay mắc (3/3)','Dán da lệch: nhìn tư thế gốc thì ổn, cử động mới vỡ',[
 err('Ví dụ thật · Pet Night Bat','Người dùng báo "cánh dính vào mặt, tai" tới <b>4 lần</b>. Chỉnh mức bám mãi không hết, vì gốc lỗi là da bị dán lúc một dây điều khiển đang lệch.'),
 err('Ví dụ thật · nhân vật Hero','Khuỷu hở khi gập: bắp tay trượt ra khỏi ống giáp. AI kéo cả bắp tay theo khuỷu thì tay lại móp.'),
 fix('Bạn làm gì','Bảo AI: <b>"Đưa mọi dây điều khiển về 0 trước khi dán da."</b> Khi báo móp, nói rõ <b>khớp nào</b> và <b>xem từ góc nào</b>.')],
 [('img/rig/d_elbow.svg','Khuỷu hở khi gập: đầu bắp tay trượt khỏi ống giáp.','sch')],dark=True,fw=1.3)
# ===== BƯỚC 8
std('Bước 8 · Bảng nút (picker)','Bảng nút giúp chọn dây điều khiển nhanh',[
 blk('Để làm gì','Người làm hoạt hình bấm nút trên bảng thay vì mò từng dây trên nhân vật.'),
 blk('Bạn xem gì để duyệt',ul('Bấm từng nút thì đúng dây điều khiển','Không nút nào đè lên nhau','Có nút chọn tất cả')),
 err('Ví dụ thật · nhân vật Hero','Đổi cỡ dây điều khiển mà quên đổi nút trên bảng, phải sửa hai vòng.')],
 [('img/rig/d_picker.svg','Bố cục bảng nút đã duyệt. Đỏ: bên phải, xanh dương: bên trái, vàng: giữa thân.','sch')],fw=1.5)
# ===== BƯỚC 9
std('Bước 9 · Thử rig (cổng duyệt)','Thử rig như người làm hoạt hình sẽ dùng',[
 blk('Để làm gì','Phát hiện lỗi trước khi người làm hoạt hình mất công làm trên rig hỏng.'),
 blk('Bạn xem gì để duyệt',ul('Thử đủ <b>4 tay chân</b>, cả IK và FK','Đổi sang khung hình khác rồi quay lại: tư thế gốc phải đứng yên','Màu texture đúng trên nhân vật','Windy: xoay tay xem gậy có đi theo không, xem áo choàng')),
 blk('AI phải báo','Cái nào <b>chưa kiểm</b>: chưa thử trong Unity, chưa quay video xem lại, chưa kiểm có xuyên vỏ không.')],
 [('img/rig/d_check.svg','Kiểm đủ 4 tay chân, cả IK và FK. Lần kiểm cũ chỉ thử tay trái nên bỏ sót.','sch')],fw=1.4)
std('Bước 9 · Lỗi AI hay mắc','AI báo "xong" khi chưa thử hết',[
 err('Ví dụ thật · một rig tháng 11','Cây rìu bị gắn vào xương cổ tay làm cổ tay thôi chạy. Lần kiểm báo sạch vì mặc định chỉ thử <b>tay trái</b>.'),
 err('Ví dụ thật · nhóm Pet','Rig không về dáng gốc khi đổi khung hình: có gối lệch 2,1 cm. Người duyệt phải tự bắt, vì phiên làm việc con không tự thấy.'),
 fix('Bạn làm gì','Bảo AI: <b>"Liệt kê cái chưa kiểm."</b> Và tự thử một lần: đổi khung hình, xem tư thế gốc có đứng yên không.')],
 [],dark=True)
# ===== BƯỚC 10
std('Bước 10 · Xuất file cho game','Hai loại file, và chỉ xuất khi bạn nói "chốt"',[
 blk('Để làm gì','Đóng gói rig và chuyển động thành file FBX để đưa vào Unity cho game chạy.'),
 blk('Hai loại file',ul('<b>File nhân vật (Base)</b>: xương và vỏ','<b>File chuyển động (anim)</b>: chỉ xương và chuyển động, không có vỏ')),
 blk('Quy tắc','Bạn nói <b>"chốt"</b> thì AI mới xuất. Còn đang sửa hay góp ý thì AI chỉ sửa, không xuất.'),
 blk('Windy ở bước này','Windy giữ nguyên tên và cây xương của team nên file chỉ có xương và chuyển động. Đã xuất thử và khớp 0 cm với file của team.')],
 [('img/rig/d_files.svg','Hai loại file đưa vào game.','sch')],fw=1.4)
std('Bước 10 · Lỗi AI hay mắc','File vào game bị vỡ',[
 err('Ví dụ thật · Pet Pebble Turtle','File nhân vật vào game bị <b>đầu và chân bay khỏi thân</b> vì thiếu thông tin tư thế gốc (BindPose). Cách sửa: thêm thông tin đó vào file.'),
 err('Ví dụ thật · Pet Pebble Turtle','File chuyển động báo lỗi "Cannot find root motion transform" vì chỉ có một nút gốc. Cách sửa: thêm một nút trống (Dummy) cùng cấp.'),
 fix('Bạn làm gì','Bảo AI: <b>"Kiểm file bằng Unity và đọc log báo lỗi."</b> Có lỗi mới thì đọc log, đừng đoán.')],
 [('img/rig/d_bindpose.svg','Hai lỗi khi file vào Unity.','sch')],dark=True,fw=1.0)
# ===== PHẦN C
raw('''<p class="kick">Phần C · Dùng ngay</p><h2>Thấy gì thì nghi lỗi nào</h2>
<table style="font-size:24px"><tr><th style="width:30%">Bạn thấy</th><th style="width:30%">Thường là do</th><th>Làm gì</th></tr>
<tr class="hl"><td>Da móp khi xoay một khớp</td><td>Mức bám sai, điểm bám nhầm xương xa</td><td>Nói rõ khớp và góc xem; AI thử lại, bạn nhìn từ gần</td></tr>
<tr><td>Mặt, tai dính vào cánh hay mảnh khác</td><td>Dán da lúc dây điều khiển đang lệch, hoặc vỏ nối liền</td><td>Đưa dây về 0 rồi dán lại; hoặc tách mảnh</td></tr>
<tr class="hl"><td>Rig nghiêng dù mọi dây đều ở 0</td><td>Dựng lại rig khi đang lệch</td><td>Đưa về 0 rồi dựng lại; kiểm tâm xoay</td></tr>
<tr><td>Dây ẩn, to quá, hai bên khác nhau</td><td>Vẽ dây không theo vỏ</td><td>Bảo AI liệt kê cỡ, so trái và phải</td></tr>
<tr class="hl"><td>Xương nằm sai chỗ khớp</td><td>AI đặt theo giữa khối</td><td>Xem 3 góc, tự dời tay rồi nói AI giữ nguyên</td></tr>
<tr><td>Vào game thấy vỡ hoặc báo lỗi gốc</td><td>Thiếu thông tin tư thế gốc hoặc thiếu nút Dummy</td><td>Bảo AI xử lý file và kiểm bằng Unity</td></tr>
<tr class="hl"><td>AI báo xong mà bạn vẫn thấy sai</td><td>Chưa kiểm hết 4 tay chân, chưa đổi khung hình</td><td>Bắt AI liệt kê cái chưa kiểm</td></tr></table>''')
std('Phần C · Dùng ngay','Câu nói để AI làm đúng',[
 '<div class="say"><b>Giao việc:</b> "Rig nhân vật Windy trong Frolvy. Chỉ dùng xương cơ bản, gốc xương ở hông. Dừng ở bước đặt xương, chụp 3 góc gửi mình duyệt."</div>',
 '<div class="say"><b>Góp ý:</b> "Điểm Ngực hạ xuống 4 cm, điểm cuối đầu về đỉnh đầu. Giữ nguyên chỗ mình đã sửa, chỉ đặt lại xương con."</div>',
 '<div class="say"><b>Bắt kiểm:</b> "Thử đủ 4 tay chân, cả IK và FK, đổi khung hình xem tư thế gốc có đứng yên. Báo cái nào chưa kiểm."</div>',
 '<div class="say"><b>Dừng lại:</b> "Dừng lại. Quay về bước đặt xương, mình thấy cổ chân sai chỗ."</div>',
 '<div class="say"><b>Chốt:</b> "Chốt rig. Xuất file nhân vật và file chuyển động, kiểm trong Unity."</div>'],
 [('img/windy/w_beforeafter.png','Góp ý tốt nói rõ <b>điểm nào</b>, <b>sửa bao nhiêu</b>, <b>theo hướng nào</b>.','wd')],fw=1.2,mh=460)
raw('''<p class="kick">Phần C · Dùng ngay</p><h2>Checklist duyệt rig (12 mục)</h2>
<div class="row bigl"><div class="card"><ul><li>Lưới đã kiểm, dựng lại nếu cần</li><li>Xương đặt đúng chỗ khớp, đã xem 3 góc</li><li>Xương gốc ở hông, không bộ xương phụ</li><li>Chuỗi xương đuôi, áo choàng đúng hình</li><li>Dây điều khiển thấy rõ, không quá to</li><li>Hai bên trái phải giống nhau</li></ul></div>
<div class="card"><ul><li>Da chỉ bám xương DEF, tối đa 4 xương mỗi điểm</li><li>Xương gốc không có da bám</li><li>Đã xoay vai, khuỷu, hông, gối, cổ, thân và nhìn bằng mắt</li><li>Đổi khung hình, tư thế gốc đứng yên</li><li>Bảng nút khớp với dây điều khiển</li><li>AI ghi rõ cái chưa kiểm</li></ul></div></div>
<p class="note">Gửi kèm checklist này với mỗi bản rig để người duyệt biết đã kiểm tới đâu.</p>''',dark=True)
# ===== PHỤ LỤC
raw('''<p class="kick">Phụ lục · Lỗi thật từ các dự án trước</p><h2>Những lỗi AI từng mắc, để bạn nhận ra sớm</h2>
<table style="font-size:21px"><tr><th style="width:18%">Nhân vật</th><th style="width:44%">Chuyện đã xảy ra</th><th>Bài học</th></tr>
<tr class="hl"><td>Hero</td><td>Dây điều khiển bị ẩn trong vỏ, có dây to 2 m. Switch hai bên khác cỡ nên bị nhắc hai lần.</td><td>So cỡ dây trái và phải</td></tr>
<tr><td>Hero</td><td>Bả vai không theo xương bả vai; đai lưng cứng khi xoay thân; chân móp khi kéo IK.</td><td>Thử từng khớp bằng mắt</td></tr>
<tr class="hl"><td>Nova</td><td>Xoay vai thì ống tay thắt lại như cái nêm vì mép dưới còn bám thân.</td><td>Vùng tay chỉ bám xương tay</td></tr>
<tr><td>London</td><td>Xương gốc bị dán da: 277 trên 1199 điểm. Xương gốc dời thì cả thân méo.</td><td>Xương gốc không được dán da</td></tr>
<tr class="hl"><td>Bastion</td><td>Dựng lại rig khi đang lệch pose: rig nghiêng dù mọi dây về 0; mất một số dây tuỳ chỉnh.</td><td>Về 0 trước khi dựng lại</td></tr>
<tr><td>MeoTom</td><td>Xương đặt theo giữa khối: cổ chân cao hơn 5 cm, hướng bàn chân lệch, đuôi cuộn thiếu xương.</td><td>Đặt ở chỗ gập, xem 3 góc</td></tr>
<tr class="hl"><td>Pet (nhóm)</td><td>Thay mesh mới: rig không về dáng gốc, texture lật; AI báo xong khi chưa kiểm hết.</td><td>Bắt AI nêu cái chưa kiểm</td></tr></table>''')
raw('''<p class="kick">Phụ lục · Bẫy của Frolvy</p><h2>Lỗi của phần mềm, không phải của AI</h2>
<div class="row"><div class="card err"><span class="lab">Xoá nhầm vỏ</span><p>Xoá khi đang chọn điểm hoặc mặt có thể xoá nhầm vỏ khác, và Ctrl+Z không lấy lại. Luôn quay về chế độ chọn cả vật trước khi xoá.</p></div>
<div class="card err"><span class="lab">Hoàn tác lùi quá</span><p>Hoàn tác nhiều lần có thể lùi cả việc bạn đã làm tay. Sửa tiếp về phía trước, kiểm lại sau khi hoàn tác.</p></div>
<div class="card err"><span class="lab">Lệnh chạy nhầm cửa sổ</span><p>Khi cửa sổ Frolvy bị đóng, lệnh có thể nhảy sang cửa sổ Frolvy khác mà không báo. Kiểm lại cảnh sau mỗi lần mở lại.</p></div></div>
<div class="row"><div class="card err"><span class="lab">Lưu và mở file</span><p>Lưu đè lên file đã có thì không được; mở file khi cảnh đang sửa dở thì lệnh nhập sau đó chồng vào cảnh rig.</p></div>
<div class="card err"><span class="lab">Xoá xương</span><p>Xoá một xương làm cả cây xương con nhảy lên. Dán da còn trỏ vào xương đã xoá: lưu mức bám trước khi dựng lại.</p></div>
<div class="card"><h3>Gặp lỗi của Frolvy</h3><p>Ghi một dòng: lỗi gì, thấy ở đâu, muốn thế nào. Hỏi bạn rồi mới gửi cho đội làm phần mềm.</p></div></div>''')
