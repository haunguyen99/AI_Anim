# ===== PHẦN A
raw('<p class="kick">Hướng dẫn cho người mới</p><h1 style="margin-top:auto">Nhờ AI làm rig<br>nhân vật 3D</h1><p style="max-width:1300px;color:#c9d6ea;margin-bottom:auto">Bạn không cần biết 3D. Tài liệu này chỉ: AI làm gì, bạn xem gì, khi nào gật đầu, khi nào bảo làm lại. Ví dụ xuyên suốt: nhân vật <b style="color:#F0B13B">Windy</b>.</p>',dark=True)
S[-1]=S[-1].replace('<section class="dark"','<section class="dark on" style="justify-content:center;gap:40px"')
std('Phần A · Đọc trước','Đọc xong, bạn làm được 3 việc',[
 blk('1. Giao việc cho AI','Biết cần chuẩn bị gì và nói câu đầu tiên là gì.'),
 blk('2. Duyệt từng bước','Biết nhìn vào đâu để thấy <b>đạt</b> hay <b>chưa đạt</b>.'),
 blk('3. Bắt AI sửa đúng chỗ','Biết lỗi AI hay mắc và câu để AI làm lại.')],
 [('img/windy/w_beforeafter.png','Ví dụ một lần duyệt: trái chưa đạt, phải đã sửa.','wd')],fw=1.6,mh=520)
std('Phần A · Đọc trước','Bắt đầu từ đâu? 4 việc',[
 blk('Bạn cần có','File nhân vật (.fbx) và file ảnh màu (texture).'),
 blk('Câu đầu tiên','"Rig nhân vật Windy trong Frolvy. Dừng ở bước đặt xương, chụp 3 góc gửi mình duyệt."')],
 [('img/rig/d_start.svg','Bốn việc đầu tiên.','sch')],fw=1.7)
std('Phần A · Đọc trước','Rig là gì? Lắp xương và dây vào con rối',[
 blk('Ví như con rối',ul('<b>Vỏ</b> (mesh): cái vỏ cứng, chưa cử động','<b>Xương</b>: khớp bên trong vỏ','<b>Da</b>: ôm quanh xương, xương xoay da xoay','<b>Dây điều khiển</b>: sợi dây bạn giật')),
 blk('Rig','Lắp xương, gắn da, nối dây. Xong thì chỉ cần kéo dây là nhân vật cử động.')],
 [('img/windy/w_mesh.png','Windy chưa rig: chỉ là cái vỏ.','wd'),('img/windy/w_joints_front.png','Windy có xương: mỗi chấm vàng là một khớp.','wd')],fw=1.3,mh=560,row=True)
std('Phần A · Đọc trước','Ai làm gì: bạn, AI và Frolvy',[
 blk('Quy tắc','AI làm từng bước và <b>dừng ở các cổng</b>. Bạn xem rồi bảo đi tiếp.'),
 blk('Bạn là người quyết','Bạn tự sửa trong Frolvy thì ý bạn thắng. AI không tự đổi lại.'),
 blk('AI làm sai hướng','Nói ngay: <b>"Dừng lại. Quay về bước …"</b>')],
 [('img/rig/d_roles.svg','Ba bên cùng làm việc.','sch')],fw=1.6)
quad('Phần A · Đọc trước','Bốn từ quan trọng nhất',[
 ('Xương','Khớp bên trong vỏ (chấm vàng). Nơi một bộ phận xoay.','img/windy/w_joints_front.png'),
 ('Dây điều khiển','Thứ bạn kéo. Các vòng màu quanh con vật là dây. Kéo dây thì xương xoay.','img/rig/mecha_ctl.jpg'),
 ('Da và mức bám','Da bám vào xương theo phần trăm. 50% vai + 50% khuỷu thì gập theo cả hai.','img/rig/d_skinrule.svg'),
 ('FK và IK','FK: xoay từng khớp. IK: kéo bàn tay, cả tay gập theo.','img/rig/d_ikfk.svg')])
raw('''<p class="kick">Phần A · Từ điển (1/2)</p><h2>Từ điển</h2>
<table style="font-size:23px"><tr><th style="width:21%">Từ</th><th>Nghĩa</th></tr><tr class="hl"><td><b>Vỏ (mesh)</b></td><td>Thân hình nhân vật, ghép từ rất nhiều mặt nhỏ</td></tr><tr class=""><td><b>Da</b></td><td>Chính cái vỏ đó, gọi là "da" khi nói chuyện bám vào xương</td></tr><tr class="hl"><td><b>Lưới</b></td><td>Cách các mặt nhỏ nối thành ô. Ô đều thì uốn đẹp</td></tr><tr class=""><td><b>Tam giác</b></td><td>Mặt nhỏ nhất của vỏ. Ít quá thì thô, nhiều quá thì nặng game</td></tr><tr class="hl"><td><b>Texture</b></td><td>Ảnh màu dán lên vỏ</td></tr><tr class=""><td><b>Xương gốc</b></td><td>Xương ở hông, mọi xương khác nối từ đây</td></tr><tr class="hl"><td><b>Chuỗi xương</b></td><td>Nhiều xương nối nhau cho phần mềm: đuôi, áo choàng</td></tr><tr class=""><td><b>Build Rig</b></td><td>Bấm một nút, Frolvy tự sinh dây điều khiển từ bộ xương</td></tr><tr class="hl"><td><b>Tư thế gốc</b></td><td>Dáng đứng chuẩn lúc mới tạo, thường dang tay chữ T</td></tr><tr class=""><td><b>Khung hình</b></td><td>Một ảnh trong chuỗi chuyển động, như một trang flipbook</td></tr></table>''')
raw('''<p class="kick">Phần A · Từ điển (2/2)</p><h2>Từ điển</h2>
<table style="font-size:23px"><tr><th style="width:21%">Từ</th><th>Nghĩa</th></tr><tr class="hl"><td><b>Về 0</b></td><td>Đưa dây điều khiển về vị trí ban đầu, như nút reset (AI làm)</td></tr><tr class=""><td><b>Dán da (bind)</b></td><td>Lần đầu gắn da vào xương, lúc nhân vật đứng tư thế gốc</td></tr><tr class="hl"><td><b>Bảng nút</b></td><td>Bảng bấm để chọn dây điều khiển cho nhanh</td></tr><tr class=""><td><b>Công tắc IK/FK</b></td><td>Nút đổi giữa hai cách kéo tay: kéo bàn tay hoặc xoay từng khớp</td></tr><tr class="hl"><td><b>Chiêu cuối</b></td><td>Đòn mạnh nhất của nhân vật trong game</td></tr><tr class=""><td><b>Cầu nối</b></td><td>Đường kết nối để AI ra lệnh cho Frolvy (nhóm kỹ thuật dựng sẵn)</td></tr><tr class="hl"><td><b>Frolvy</b></td><td>Phần mềm làm rig. AI điều khiển nó thay bạn</td></tr><tr class=""><td><b>FBX</b></td><td>File đóng gói nhân vật để đưa vào game</td></tr><tr class="hl"><td><b>Unity</b></td><td>Phần mềm làm game, nơi file FBX chạy thật</td></tr><tr class=""><td><b>Cổng duyệt</b></td><td>Chỗ AI dừng lại chờ bạn xem rồi mới đi tiếp</td></tr></table>''')
raw('''<p class="kick">Phần B · Từng bước</p><h2>10 bước (ô vàng là cổng bạn duyệt)</h2>
<div class="flow" style="margin-top:14px">
<div class="step"><span class="num">1</span><b>Nhận việc, đo</b><span>File, cỡ</span></div>
<div class="step gate"><span class="num">2·CỔNG</span><b>Kiểm lưới</b><span>Đạt hay làm lại</span></div>
<div class="step gate"><span class="num">3·CỔNG</span><b>Đặt xương</b><span>Đúng chỗ khớp</span></div>
<div class="step"><span class="num">4</span><b>Chuỗi xương</b><span>Đuôi, áo choàng</span></div>
<div class="step"><span class="num">5</span><b>Build Rig</b><span>Sinh dây</span></div>
<div class="step"><span class="num">6</span><b>Dây điều khiển</b><span>Vừa tay bấm</span></div>
<div class="step gate"><span class="num">7·CỔNG</span><b>Dán da</b><span>Da bám xương</span></div>
<div class="step"><span class="num">8</span><b>Bảng nút</b><span>Chọn dây nhanh</span></div>
<div class="step gate"><span class="num">9·CỔNG</span><b>Thử rig</b><span>Thử mọi khớp</span></div>
<div class="step"><span class="num">10</span><b>Xuất file</b><span>Vào game</span></div></div>
<div class="row" style="margin-top:24px"><div class="card"><h3>Mỗi bước</h3><p>Trang sáng: làm gì, xem gì. Trang tối: lỗi AI hay mắc.</p></div>
<div class="card"><h3>Nhãn trên hình</h3><p><b>ẢNH THẬT</b> chụp từ Frolvy · <b>WINDY</b> vẽ từ file xương thật · <b>SƠ ĐỒ</b> vẽ minh hoạ.</p></div></div>''')
